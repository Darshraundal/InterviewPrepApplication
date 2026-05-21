# PaymentReminderService — Complete Interview Preparation Guide

> **Project Type:** .NET 8.0 Background Worker Service  
> **Purpose:** Automatically fetches pending payment reminder emails from a database, builds threaded HTML email bodies, and sends them via SMTP on a configurable interval.  
> **Stack:** .NET 8, Generic Host, Dapper, SQL Server, ADO.NET, Custom Crypter DLL  
> **Note:** This is a **backend-only** service. There is **no Angular frontend**, no MVC/Web API, no JWT/Auth, and no Entity Framework in this project.

---

## 1. PROJECT ARCHITECTURE SUMMARY

### Complete Architecture Flow

```
appsettings.json
      │
      ▼
Program.cs  ──── Host.CreateDefaultBuilder()
      │                ├── Config.Initialize()        (static config holder)
      │                ├── AddHostedService<Worker>()
      │                ├── AddSingleton<PaymentReminderService>()
      │                ├── AddSingleton<IConfigEmailSMTPDataService>()
      │                └── AddSingleton<IPaymentReminderEmailDataService>()
      │
      ▼
Worker.cs (BackgroundService)
      │   ExecuteAsync() — loops every N minutes via Task.Delay
      │
      ▼
PaymentReminderService.cs (Core Logic)
      │   ExecuteTask()
      │     ├── GetReminderEmailTransaction() ── PaymentReminderEmailDataService (Dapper)
      │     │         └── SQL Server SP: CS_GetPaymentReminderEmail
      │     │
      │     ├── Groups emails by AssignmentID
      │     ├── Builds threaded HTML body (StringBuilder)
      │     │
      │     └── SendAndUpdateEmailStatus()
      │           ├── GetSmtpData() ─── ConfigEmailSMTPDataService (ADO.NET)
      │           │         └── SQL Server SP: CS_GetConfigEmailSMTPOnFilter
      │           ├── Decrypts SMTP password (Crypter.dll)
      │           ├── Decrypts email addresses and placeholders
      │           ├── SmtpClient.Send()
      │           └── UpdateReminderEmailTransaction() (Dapper)
      │                     └── SQL Server SP: CS_UpdatePaymentReminderEmail
      │
      ▼
   File-based Logs  (Logs/yyyy-MM-dd.log)
```

### Key Flows

**Scheduling Flow:**  
`Program.cs` builds the Generic Host → registers `Worker` as a hosted service → `Worker.ExecuteAsync()` validates interval config → runs `PaymentReminderService.ExecuteTask()` → waits via `Task.Delay` → repeats.

**Email Send Flow:**  
Fetch pending emails (Status=0) → group by AssignmentID → order by stage/trigger time → build threaded HTML body using `StringBuilder` → decrypt placeholders → get SMTP config → send via `SmtpClient` → update status to sent.

**Database Interaction Flow:**  
All DB operations go through Stored Procedures. `PaymentReminderEmailDataService` uses Dapper for async execution. `ConfigEmailSMTPDataService` uses raw ADO.NET + `DataTable` + `TableUtilities` reflection mapper.

---

## 2. .NET / .NET CORE — CONCEPTS & INTERVIEW Q&A

---

### BACKGROUND SERVICE / HOSTED SERVICE

**QUESTION:**  
What is `BackgroundService` in .NET and how is it used in your project?

**ANSWER:**  
`BackgroundService` is an abstract base class in .NET that implements `IHostedService`. It provides a single abstract method `ExecuteAsync(CancellationToken)` which runs continuously as a background task. It is designed for long-running operations that need to run alongside the main application lifecycle.

**PROJECT EXAMPLE:**
- **File:** `Worker.cs`
- **Class:** `Worker : BackgroundService`
- **Method:** `ExecuteAsync(CancellationToken stoppingToken)`
- **Explanation:** `Worker` extends `BackgroundService`. Inside `ExecuteAsync`, there is a `while (!stoppingToken.IsCancellationRequested)` loop. Every iteration it calls `await _paymentreminderService.ExecuteTask()`, then waits `await Task.Delay(TimeSpan.FromMinutes(_intervalMinutes), stoppingToken)` before the next run. The interval is read from `Config.IntervalMinutes` which maps to `appsettings.json > Settings:IntervalMinutes`.

**Benefits in my project:**  
The service runs as a Windows Service / Linux daemon without a UI thread. The `CancellationToken` ensures clean shutdown when the OS stops the service.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `IHostedService` and `BackgroundService`?
2. How does the Generic Host manage the lifetime of a hosted service?
3. What happens if `ExecuteAsync` throws an unhandled exception?

**IMPORTANT FOR INTERVIEW:**  
- `BackgroundService` is the base; `IHostedService` is the interface (with `StartAsync`/`StopAsync`).
- If `ExecuteAsync` throws, the host catches it and logs — the service stops, but the process may continue. In our `Worker.cs`, we catch exceptions and call `stoppingToken.ThrowIfCancellationRequested()` to propagate graceful shutdown.
- `Microsoft.Extensions.Hosting.WindowsServices` NuGet package enables running as a Windows Service.

---

### DEPENDENCY INJECTION (DI)

**QUESTION:**  
How is Dependency Injection implemented in your project?

**ANSWER:**  
DI is the pattern where objects receive their dependencies from an external container rather than creating them. In .NET Core/8, the built-in DI container is configured in `Program.cs` via `builder.ConfigureServices()`. Dependencies are injected via constructor injection.

**PROJECT EXAMPLE:**
- **File:** `Program.cs`
- **Registration:**
  ```csharp
  services.AddHostedService<Worker>();
  services.AddSingleton<PaymentReminderService>();
  services.AddSingleton<IConfigEmailSMTPDataService, ConfigEmailSMTPDataService>();
  services.AddSingleton<IPaymentReminderEmailDataService, PaymentReminderEmailDataService>();
  ```
- **Injection in `Worker.cs`:**
  ```csharp
  public Worker(IConfiguration configuration, ILogger<Worker> logger, PaymentReminderService paymentreminderService)
  ```
- **Injection in `PaymentReminderService.cs`:**
  ```csharp
  public PaymentReminderService(IPaymentReminderEmailDataService ..., IConfigEmailSMTPDataService ...)
  ```

**Benefits in my project:**  
Loose coupling — `Worker` doesn't know about `ConfigEmailSMTPDataService` directly. Interfaces allow easy unit testing by swapping real implementations with mocks.

**FOLLOW-UP QUESTIONS:**
1. What are the three service lifetimes in .NET DI?
2. Why are all services registered as Singleton in this project?
3. What problem does DI solve over using `new` keyword?

**IMPORTANT FOR INTERVIEW:**  
Interface injection (e.g., `IPaymentReminderEmailDataService`) is the recommended approach. The concrete class (`PaymentReminderEmailDataService`) is hidden from the consumer.

---

### SERVICE LIFETIMES

**QUESTION:**  
Explain service lifetimes in .NET. What lifetime is used in your project and why?

**ANSWER:**  
.NET DI supports three lifetimes:
- **Singleton** — one instance for the entire application lifetime
- **Scoped** — one instance per HTTP request (or per scope)
- **Transient** — new instance every time it is requested

**PROJECT EXAMPLE:**
- **File:** `Program.cs`
- All services (`PaymentReminderService`, `ConfigEmailSMTPDataService`, `PaymentReminderEmailDataService`) are registered as **Singleton**.
- **Why Singleton here?** Because this is a background worker (no HTTP request context), there are no scope boundaries. Creating new DB connections per method call is handled inside each method with `using var con = new SqlConnection(...)`, so thread safety is maintained. Singleton avoids repeated object instantiation overhead.

**Benefits in my project:**  
Singletons reduce GC pressure since objects are reused. Connection pooling handles actual DB connections.

**FOLLOW-UP QUESTIONS:**
1. What is "captive dependency" — when a Singleton depends on a Scoped service?
2. When would you choose Transient over Singleton?
3. Is it safe to use Singleton with `SqlConnection`?

**IMPORTANT FOR INTERVIEW:**  
`SqlConnection` itself is NOT stored as a field — it is created fresh inside each method with `using` (so it's disposed immediately). Only the service class instance is Singleton. SQL Server connection pooling handles the physical connections efficiently.

---

### ASYNC / AWAIT

**QUESTION:**  
How is async/await used in your project?

**ANSWER:**  
`async/await` allows asynchronous non-blocking execution. It frees the calling thread while waiting for I/O operations (DB calls, network calls) to complete.

**PROJECT EXAMPLE:**
- **File:** `Worker.cs` — `protected override async Task ExecuteAsync(...)`
- **File:** `PaymentReminderService.cs` — `public async Task ExecuteTask()`, `private async Task SendAndUpdateEmailStatus(...)`
- **File:** `PaymentReminderEmailDataService.cs` — `await con.OpenAsync()`, `await con.QueryAsync<>()`, `await con.ExecuteAsync()`
- **File:** `Worker.cs` — `await Task.Delay(delay, stoppingToken)` — non-blocking sleep between intervals

**Benefits in my project:**  
The Worker thread is not blocked while waiting for SQL queries. Dapper's `QueryAsync` / `ExecuteAsync` use async SQL under the hood. The service can handle cancellation cleanly during the delay.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `Task.Delay` and `Thread.Sleep`?
2. What happens if you call an async method without `await`?
3. What is `ConfigureAwait(false)` and should it be used in a Worker Service?

**IMPORTANT FOR INTERVIEW:**  
- `Task.Delay` is non-blocking (thread returns to pool); `Thread.Sleep` blocks the thread.
- In a Worker Service (no SynchronizationContext), `ConfigureAwait(false)` is less critical than in ASP.NET, but is still good practice in library code.
- `await` unwraps the `Task<T>` result — so `await con.QueryAsync<PaymentReminderEmailTransaction>(...)` gives a `IEnumerable<PaymentReminderEmailTransaction>`.

---

### INTERFACES vs ABSTRACT CLASSES

**QUESTION:**  
When do you use an interface vs an abstract class? How does your project use both?

**ANSWER:**  
- **Interface** — pure contract, no implementation, supports multiple "inheritance"
- **Abstract class** — partial implementation, single inheritance, can have constructors and state

**PROJECT EXAMPLE:**
- **Interfaces:** `IPaymentReminderEmailDataService` (`interface/IPaymentReminderEmailDataService.cs`) and `IConfigEmailSMTPDataService` — define contracts for data access with no implementation.
- **Abstract class:** `BackgroundService` (from .NET SDK) — `Worker` extends it, inheriting the `StartAsync`/`StopAsync` implementation while overriding only `ExecuteAsync`.

**Benefits in my project:**  
Interfaces enable DI to swap implementations (e.g., replace SQL with a mock in tests). `BackgroundService` gives `Worker` the hosted service lifecycle for free.

**FOLLOW-UP QUESTIONS:**
1. Can an interface have a default implementation in C# 8+?
2. Why does .NET use `BackgroundService` (abstract class) instead of just `IHostedService` (interface)?
3. Can a class implement multiple interfaces?

**IMPORTANT FOR INTERVIEW:**  
Use interface when you need a contract without any shared behavior. Use abstract class when multiple subclasses share some implementation but need to override specific parts.

---

### EXCEPTION HANDLING

**QUESTION:**  
How is exception handling implemented in your project?

**ANSWER:**  
Exception handling is implemented using try-catch blocks at multiple levels with specific catch for `SqlException` and graceful degradation (return empty list/null rather than crashing the service).

**PROJECT EXAMPLE:**
- **File:** `Worker.cs` — `ExecuteAsync` has outer try-catch for startup errors and inner try-catch inside the while loop for runtime errors. On error, calls `stoppingToken.ThrowIfCancellationRequested()`.
- **File:** `PaymentReminderEmailDataService.cs` — `GetReminderEmailTransaction` catches `SqlException`, logs via `WriteLog`, returns `new List<>()`.
- **File:** `PaymentReminderService.cs` — `ExecuteTask` catches `Exception`, logs error, does NOT rethrow (prevents crashing the service loop).
- **File:** `PaymentReminderService.cs` — `SendEmail` catches `Exception`, logs error, returns `false` (boolean to indicate failure).

**Benefits in my project:**  
Graceful degradation — a failed DB call or email send does not crash the entire Worker. The service continues running on the next scheduled interval.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `throw` and `throw ex`?
2. When should you rethrow an exception vs swallow it?
3. What is a global exception handler in .NET?

**IMPORTANT FOR INTERVIEW:**  
Note the commented-out `throw` lines in the DAO classes. This is a deliberate design choice: keep the service running even on partial failures, but log all errors. In an enterprise setting, you might add alerting when error thresholds are exceeded.

---

### CONFIGURATION MANAGEMENT

**QUESTION:**  
How is configuration managed in your project?

**ANSWER:**  
Configuration uses `appsettings.json` loaded via the Generic Host, then copied into a static `Config` class for easy access throughout the application.

**PROJECT EXAMPLE:**
- **File:** `appsettings.json` — stores `ConnectionStrings`, `Settings` (interval, log path, testing mode), and `CsSpName` (stored procedure names).
- **File:** `Program.cs` — `builder.ConfigureAppConfiguration()` loads `appsettings.json` + environment variables + command-line args.
- **File:** `Config.cs` — `Config.Initialize(configuration)` called in `ConfigureServices`. Static properties: `Config.DBConnectionString`, `Config.IntervalMinutes`, `Config.IsTestingPhase`, `Config.GetPaymentReminderEmail`, etc.

**Benefits in my project:**  
Centralized config in one class. Stored procedure names are configurable (can change SP name without code change). Testing mode can be toggled via config without code deployment.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `appsettings.json` and `appsettings.Development.json`?
2. What are environment variables used for in configuration?
3. What is `IOptions<T>` and how does it differ from a static Config class?

**IMPORTANT FOR INTERVIEW:**  
The static `Config` class is simple but has a downside: it cannot be mocked in unit tests. The enterprise alternative is `IOptions<T>` pattern — register a strongly-typed POCO class and inject it. Also note that `appsettings.Development.json` overrides the base file when `DOTNET_ENVIRONMENT=Development`.

---

### PROGRAM.CS / GENERIC HOST

**QUESTION:**  
Explain the role of `Program.cs` and the Generic Host in your project.

**ANSWER:**  
`Program.cs` is the entry point. The Generic Host (`IHost`) is .NET's infrastructure for running long-lived applications (services, daemons). It manages DI, configuration, logging, and the application lifetime.

**PROJECT EXAMPLE:**
- **File:** `Program.cs`
- `Host.CreateDefaultBuilder(args)` — sets up defaults: appsettings.json, environment variables, default logging.
- `builder.ConfigureAppConfiguration(...)` — explicitly adds `appsettings.json`, environment variables, command-line.
- `builder.ConfigureServices(...)` — registers all services into the DI container.
- `Config.Initialize(configuration)` — initializes static config before services are built.
- `await app.RunAsync()` — starts the host and runs until shutdown signal.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `WebApplication.CreateBuilder` and `Host.CreateDefaultBuilder`?
2. How does the Generic Host manage graceful shutdown?
3. What is the role of `IHostApplicationLifetime`?

**IMPORTANT FOR INTERVIEW:**  
`Host.CreateDefaultBuilder` is for non-web services (Worker Services). `WebApplication.CreateBuilder` includes Kestrel and HTTP middleware. This project uses Worker SDK (`Microsoft.NET.Sdk.Worker`) — not Web SDK.

---

### DEPENDENCY INJECTION — DAO PATTERN

**QUESTION:**  
Does your project implement the Repository pattern? Explain the data access approach used.

**ANSWER:**  
This project implements the **DAO (Data Access Object) pattern**, which is similar to the Repository pattern but simpler. Each DAO class encapsulates database access for a specific entity.

**PROJECT EXAMPLE:**
- **Files:** `DAO/PaymentReminderEmailDataService.cs`, `DAO/ConfigEmailSMTPDataService.cs`
- **Interfaces:** `interface/IPaymentReminderEmailDataService.cs`, `interface/IConfigEmailSMTPDataService.cs`
- `PaymentReminderEmailDataService` handles: `GetReminderEmailTransaction()` and `UpdateReminderEmailTransaction()` for the email transaction table.
- `ConfigEmailSMTPDataService` handles: `GetSmtpData()` for the SMTP configuration table.
- Both are injected via their interfaces into `PaymentReminderService`.

**This project currently does not implement the Repository pattern fully, but ideally it should be implemented using:**  
A generic `IRepository<T>` interface with methods like `GetAll()`, `GetById()`, `Update()`, `Add()`, combined with a Unit of Work pattern for transaction management.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between DAO and Repository patterns?
2. What is the Unit of Work pattern and when would you add it here?
3. Why are stored procedure names stored in config rather than hardcoded?

---

### DAPPER ORM

**QUESTION:**  
What ORM does your project use and why?

**ANSWER:**  
This project uses **Dapper**, a micro-ORM that extends `IDbConnection` with helper methods. It maps SQL results to C# objects without the overhead of a full ORM like Entity Framework.

**PROJECT EXAMPLE:**
- **File:** `DAO/PaymentReminderEmailDataService.cs`
- `await con.QueryAsync<PaymentReminderEmailTransaction>(Config.GetPaymentReminderEmail, commandType: CommandType.StoredProcedure)` — fetches records and maps to `PaymentReminderEmailTransaction`.
- `await con.ExecuteAsync(Config.UpdatePaymentReminderEmail, parameters, commandType: CommandType.StoredProcedure)` — executes SP with anonymous parameters.

**Benefits in my project:**  
- Faster than EF for read-heavy operations (no change tracking overhead).
- Direct SP call with automatic mapping to POCO.
- Async support out of the box.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Dapper and Entity Framework?
2. How does Dapper handle SQL injection prevention?
3. What is `IQueryable` vs `IEnumerable` and which does Dapper return?

**IMPORTANT FOR INTERVIEW:**  
Dapper returns `IEnumerable<T>` — the query executes on the database, and results are streamed back. EF's `IQueryable<T>` can compose queries (add `.Where()` etc.) before hitting the DB. Since all queries in this project go through SPs, `IQueryable` composition is not needed — `IEnumerable` is the correct choice.

---

### LINQ

**QUESTION:**  
How is LINQ used in your project?

**ANSWER:**  
LINQ (Language Integrated Query) is used extensively in `PaymentReminderService.cs` to filter, group, and sort the in-memory email transaction list returned from the database.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs`, method `ExecuteTask()`
- `emailTransactions.Where(x => x.Status == 0).Select(x => x.AssignmentID).Distinct()` — gets unique AssignmentIDs for pending emails.
- `emailTransactions.Where(e => e.AssignmentID == AssignmentID).OrderByDescending(e => e.PaymentReminderStageID).ThenByDescending(e => e.EmailTriggerTime).ToList()` — sorts emails for an assignment.
- `emailsForAssignments.First()` — gets the most recent/highest-priority email.
- `emailsForAssignments.Skip(1)` — skips the primary to get history emails.
- `previousEmails.Where(e => e.Status == 1)` — only append previously sent emails to thread.

**FOLLOW-UP QUESTIONS:**
1. What is deferred execution in LINQ?
2. What is the difference between `First()` and `FirstOrDefault()`?
3. When should you use LINQ vs raw SQL?

**IMPORTANT FOR INTERVIEW:**  
LINQ here operates on in-memory collections (`List<T>`), so all filtering/sorting happens in .NET — not in SQL. This is fine for the data volume here but would be inefficient if the SP returned thousands of records. Deferred execution applies to `IQueryable`, not `IEnumerable` — LINQ on a `List<T>` is immediate.

---

### STRINGBUILDER

**QUESTION:**  
Why is `StringBuilder` used in your project instead of string concatenation?

**ANSWER:**  
`StringBuilder` is a mutable character buffer. Unlike `string` (immutable in C#), it does not create a new string object on every concatenation, making it efficient for building strings in loops.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs`, method `ExecuteTask()`
- `var finalMessageText = new StringBuilder(finalEmail.MessageText)` — initialized with the primary email body.
- In the `foreach` loop over `previousEmails`, `finalMessageText.Append(GetHtmlFormattedBody(email))` — each previous email's HTML is appended.
- After the loop, `finalMessageText.ToString()` is not needed explicitly as it's passed as a string to `SendAndUpdateEmailStatus`.

**Benefits in my project:**  
An email thread may have 5–10 previous messages. Without `StringBuilder`, each `+=` would allocate a new string. With `StringBuilder`, all appends happen in-place.

**FOLLOW-UP QUESTIONS:**
1. When would you NOT use `StringBuilder`?
2. What is the difference between `StringBuilder` and `string.Concat()`?
3. What is `string.Format` vs interpolation performance?

**IMPORTANT FOR INTERVIEW:**  
For 2–3 fixed concatenations, string interpolation (`$"..."`) is cleaner and the compiler optimizes it. Use `StringBuilder` when concatenating in loops or building large strings dynamically.

---

### GENERIC CLASSES / METHODS

**QUESTION:**  
How are generics used in your project?

**ANSWER:**  
Generics allow writing type-safe, reusable code that works with any data type.

**PROJECT EXAMPLE:**
- **File:** `Utilities/TableUtilities.cs`
- `public static List<T> ConvertDataTable<T>(DataTable dt)` — a generic method that converts any `DataTable` to a `List<T>`.
- `public static T GetItem<T>(DataRow dr)` — uses `Activator.CreateInstance<T>()` to create instances of any type T, then uses Reflection (`PropertyInfo`) to map column values.
- Used in `ConfigEmailSMTPDataService.cs`: `TableUtilities.ConvertDataTable<ConfigEmailSMTP>(dt)`.
- Dapper itself uses generics: `con.QueryAsync<PaymentReminderEmailTransaction>(...)`.

**FOLLOW-UP QUESTIONS:**
1. What is a generic constraint (`where T : class`)?
2. What is `Activator.CreateInstance<T>()` and when would you use it?
3. What is the difference between `List<T>` and `ArrayList`?

**IMPORTANT FOR INTERVIEW:**  
`Activator.CreateInstance<T>()` uses reflection to create objects at runtime — it requires a public parameterless constructor. This is the pattern used in `TableUtilities.GetItem<T>`. Performance is slower than direct construction, but acceptable for this use case.

---

### REFLECTION

**QUESTION:**  
How is reflection used in your project?

**ANSWER:**  
Reflection allows inspecting and manipulating types, properties, and methods at runtime without knowing them at compile time.

**PROJECT EXAMPLE:**
- **File:** `Utilities/TableUtilities.cs`, method `GetItem<T>`
- `Type temp = typeof(T)` — gets the type metadata.
- `temp.GetProperties()` — retrieves all public properties of type T.
- `pro.Name == column.ColumnName` — matches DB column name to C# property name.
- `pro.SetValue(obj, dr[column.ColumnName], null)` — sets the property value at runtime.

**Benefits in my project:**  
`ConfigEmailSMTPDataService` returns raw `DataTable` from `SqlDataAdapter`. `TableUtilities.ConvertDataTable<ConfigEmailSMTP>` converts it to a typed object without writing manual mapping code.

**FOLLOW-UP QUESTIONS:**
1. What are the performance implications of reflection?
2. How does Dapper avoid reflection overhead?
3. What is `AutoMapper` and how does it compare to this reflection-based mapper?

**IMPORTANT FOR INTERVIEW:**  
Dapper uses cached `IL emit`-based mappers (faster than raw reflection). `TableUtilities` uses raw reflection (slower). This project currently does not implement AutoMapper. The enterprise improvement would be: use Dapper for `ConfigEmailSMTP` too, eliminating the need for `TableUtilities` entirely.

---

### STATIC CLASS / STATIC METHODS

**QUESTION:**  
How are static classes and methods used in your project?

**ANSWER:**  
Static classes/members belong to the type itself, not an instance. They are shared across all instances and the entire application.

**PROJECT EXAMPLE:**
- **File:** `Config.cs` — `public static class Config` — holds all configuration values as static properties. `Config.DBConnectionString`, `Config.IntervalMinutes`, etc.
- **File:** `PaymentReminderService.cs` — `public static void WriteLog(string typeOfMsg, string source, string strValue)` — shared across all classes (called from DAO and Worker without an instance).
- **File:** `PaymentReminderService.cs` — `private static string GetHtmlFormattedBody(...)` and `GetHtmlFormattedBodyLang(...)` — pure functions, no state needed.
- **File:** `Utilities/TableUtilities.cs` — `public static List<T> ConvertDataTable<T>` — utility method with no state.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `static`, `readonly`, and `const`?
2. What are the drawbacks of static classes?
3. Can a static class implement an interface?

**IMPORTANT FOR INTERVIEW:**  
`const` — compile-time constant, value baked into IL. `readonly` — runtime constant, set once in constructor. `static readonly` — runtime constant, shared. `Config` uses `static` properties with `private set` — effectively write-once after `Initialize()`.

---

### EXTENSION METHODS

**QUESTION:**  
Are extension methods used in your project?

**ANSWER:**  
Yes. Extension methods add methods to existing types without modifying them.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs` (bottom of file)
- `public static class StringExtensions` with `public static string ReplaceNewlines(this string input)`.
- Used as: `finalEmail.MessageText.ReplaceNewlines()` — replaces `\r\n`, `\r`, `\n` with `<br />` for HTML rendering.
- Called throughout `ExecuteTask()` before appending email bodies.

**FOLLOW-UP QUESTIONS:**
1. What are the rules for defining an extension method?
2. Can extension methods override existing methods?
3. When should you use extension methods vs helper classes?

---

### OOP CONCEPTS

**QUESTION:**  
Explain OOP concepts demonstrated in your project.

**ANSWER:**

**Encapsulation:**
- `Config.cs` — properties have `private set` — external code can read but not modify config values after initialization.
- DAO classes encapsulate all database access — consumers don't know if it's Dapper or ADO.NET.

**Abstraction:**
- `IPaymentReminderEmailDataService` and `IConfigEmailSMTPDataService` — interfaces expose only what consumers need.
- `BackgroundService` abstracts the host lifecycle from `Worker`.

**Inheritance:**
- `Worker : BackgroundService` — inherits hosted service lifecycle (StartAsync, StopAsync) and only overrides `ExecuteAsync`.

**Polymorphism:**
- Interface-based polymorphism — `PaymentReminderService` depends on `IPaymentReminderEmailDataService`. Could swap in a mock or different implementation.

---

### SOLID PRINCIPLES

**QUESTION:**  
How are SOLID principles applied in your project?

**ANSWER:**

**S — Single Responsibility Principle:**
- `Worker.cs` — only schedules task execution.
- `PaymentReminderService.cs` — only handles email business logic.
- `PaymentReminderEmailDataService.cs` — only handles email transaction DB access.
- `ConfigEmailSMTPDataService.cs` — only handles SMTP config DB access.
- `Config.cs` — only holds configuration.
- `TableUtilities.cs` — only does DataTable-to-object conversion.

**O — Open/Closed Principle:**  
Partially present — can add new DAO implementations without modifying consumers (thanks to interfaces).

**L — Liskov Substitution:**  
`Worker` can be used wherever `BackgroundService` is expected.

**I — Interface Segregation:**  
`IPaymentReminderEmailDataService` has only 2 relevant methods. `IConfigEmailSMTPDataService` has 1. Neither is bloated.

**D — Dependency Inversion:**  
`PaymentReminderService` depends on interfaces (`IPaymentReminderEmailDataService`, `IConfigEmailSMTPDataService`), not concrete classes. The DI container wires up the concrete classes.

**FOLLOW-UP QUESTIONS:**
1. Give an example of where the project violates OCP.
2. What is the difference between DIP (dependency inversion principle) and DI (dependency injection)?
3. How would you refactor `Config` to better support SOLID?

---

### TASK vs THREAD

**QUESTION:**  
What is the difference between `Task` and `Thread`? Which does your project use?

**ANSWER:**  
- **Thread** — OS-level thread, expensive to create, 1MB stack per thread.
- **Task** — a unit of work that runs on the ThreadPool, lightweight, can represent async I/O that uses no thread.

**PROJECT EXAMPLE:**
- This project uses **only Tasks** — no `Thread` is created directly.
- `ExecuteAsync` returns `Task` — runs on a ThreadPool thread managed by the Generic Host.
- `await Task.Delay(...)` — releases the thread during wait, no thread blocked.
- `await con.QueryAsync(...)` — async I/O, no thread blocked during SQL wait.

**FOLLOW-UP QUESTIONS:**
1. What is `Task.Run` used for?
2. What is the ThreadPool and how does it work?
3. When would you use `Thread` over `Task`?

**IMPORTANT FOR INTERVIEW:**  
`Task.Run` is for CPU-bound work (offload to ThreadPool). `async/await` with I/O methods is for I/O-bound work (no thread consumed during I/O). This project is I/O-bound (DB + SMTP), so `async/await` is the correct choice.

---

### LOGGING

**QUESTION:**  
How is logging implemented in your project?

**ANSWER:**  
This project uses a **custom file-based logger** — `WriteLog()` in `PaymentReminderService.cs` — which writes timestamped entries to daily log files.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs`, method `WriteLog(string typeOfMsg, string source, string strValue)`
- Log path from config: `Config.LogFolderPath` → `/dotnet-service/paymentreminderservice/Logs`.
- File name: `yyyy-MM-dd.log` — one file per day.
- Format: `yyyy/MM/dd HH:mm:ss.ffff|{typeOfMsg}||{strValue}||{source}`.
- Uses `StreamWriter` with `append: true`.
- Also uses `ILogger<Worker>` (injected by Generic Host) in `Worker.cs` for structured logging.

**This project does not implement structured/centralized logging fully, but ideally it should be implemented using:**  
Serilog or NLog with sinks (file, Seq, Elasticsearch, Azure Monitor). `ILogger<T>` is already injected in `Worker` — replacing `WriteLog` with `ILogger<T>` throughout would be the standard improvement.

**FOLLOW-UP QUESTIONS:**
1. What is structured logging vs flat-text logging?
2. What is `ILogger<T>` and how does it differ from `Console.WriteLine`?
3. What are log levels (Trace, Debug, Information, Warning, Error, Critical)?

---

### PATTERN MATCHING / SWITCH EXPRESSION

**QUESTION:**  
Is pattern matching used in your project?

**ANSWER:**  
Yes, the C# 8+ switch expression is used for multi-language name mapping.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs`, method `DecryptName(string encryptedName)`
- After decrypting, a switch expression maps language-specific customer labels:
  ```csharp
  return decryptedName switch {
      "お客様" => "お客様",
      "親愛的客戶" => "親愛的客戶",
      "尊敬的客户" => "尊敬的客户",
      "고객명" => "고객명",
      "Klient" => "Klient",
      "Cliente" => "Cliente",
      "client" => "Client",
      _ => decryptedName
  };
  ```
- Default case (`_`) returns the decrypted name as-is.

---

### DISPOSABLE PATTERN (using)

**QUESTION:**  
How is the `IDisposable` / `using` pattern used in your project?

**ANSWER:**  
`using` statements ensure that unmanaged resources (DB connections, SMTP connections, file writers) are disposed promptly after use, even if an exception occurs.

**PROJECT EXAMPLE:**
- `using var con = new SqlConnection(...)` — connection closed and disposed after block.
- `using (var mail = new MailMessage {...})` — mail message disposed.
- `using (var smtp = new SmtpClient(...))` — SMTP connection closed.
- `using (var sw = new StreamWriter(...))` — file handle closed.
- `using (var adapter = new SqlDataAdapter(...))` — adapter disposed.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `using` statement and `using` declaration?
2. What does `Dispose()` do?
3. What is the difference between managed and unmanaged resources?

---

### REGEX

**QUESTION:**  
How is Regex used in your project?

**ANSWER:**  
Regular expressions are used to find and replace encrypted placeholder tokens in email body text.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderService.cs`, method `DecryptionAndReplaceLogic(string emailText)`
- Pattern: `"{{{{(.*?)}}}}"`  — matches text wrapped in `{{` and `}}` (double curly braces, 4 braces in string literal = 2 actual).
- `Regex.Matches(emailText, pattern)` — finds all encrypted placeholders.
- For each match, decrypts the captured group via `DecryptName()` and replaces in the email text.

**Benefits in my project:**  
Email bodies stored in DB have encrypted customer names (e.g., `{{encryptedName}}`). Before sending, these are decrypted and replaced with actual names.

---

### WHAT IS NOT IN THIS PROJECT

| Concept | Status | Notes |
|---|---|---|
| MVC Architecture | Not present | Worker Service, not Web App |
| ASP.NET Middleware Pipeline | Not present | No HTTP pipeline |
| JWT / OAuth | Not present | Service-to-service, no user auth |
| Entity Framework | Not present | Uses Dapper + ADO.NET |
| API Versioning | Not present | No Web API controllers |
| CORS | Not present | No HTTP server |
| AutoMapper | Not present | Manual mapping + TableUtilities |
| Repository Pattern | Not present | DAO pattern used instead |
| Angular | Not present | Backend-only service |
| Session/Cookies | Not present | Not a web app |
| Delegates/Events | Not present | No pub-sub needed |

---

## 3. DATABASE / SQL CONCEPTS

---

### STORED PROCEDURES

**QUESTION:**  
How are stored procedures used in your project?

**ANSWER:**  
All database operations go through stored procedures. The application does not use inline SQL. SP names are stored in `appsettings.json` to allow name changes without code deployment.

**PROJECT EXAMPLE:**
- **`CS_GetPaymentReminderEmail`** — called in `PaymentReminderEmailDataService.GetReminderEmailTransaction()`. Returns all email transactions with Status = 0 (unsent). No parameters needed.
- **`CS_UpdatePaymentReminderEmail`** — called in `PaymentReminderEmailDataService.UpdateReminderEmailTransaction()`. Takes `@EmailTransactionID`, updates Status = 1 and SentOn.
- **`CS_GetConfigEmailSMTPOnFilter`** — called in `ConfigEmailSMTPDataService.GetSmtpData()`. Takes `@SMTPId`, `@SearchString`, `@IsDeleted`, `@Emailsituationcode`, `@Websiteid`, `@EmailTransactionID`. Returns SMTP configuration.

**Benefits in my project:**  
- Business logic for determining which emails to send lives in the SP — the .NET code just processes results.
- SQL injection prevention — parameterized SP calls.
- DB team can optimize SPs independently of the .NET service.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between a stored procedure and a function in SQL?
2. How does Dapper call a stored procedure with parameters?
3. What is `CommandType.StoredProcedure` and why is it needed?

**IMPORTANT FOR INTERVIEW:**  
`CommandType.StoredProcedure` tells ADO.NET/Dapper to execute the command as a SP call (`EXEC SP_Name @param`) rather than as a raw SQL string. Without it, the command would fail or execute as a T-SQL statement.

---

### PARAMETERIZED QUERIES / SQL INJECTION PREVENTION

**QUESTION:**  
How does your project prevent SQL injection?

**ANSWER:**  
The project prevents SQL injection by using:
1. **Stored procedures** for all DB calls — no dynamic SQL built from user input.
2. **Dapper's parameterized queries** — anonymous parameter objects passed to `ExecuteAsync`.
3. **ADO.NET's `cmd.Parameters.AddWithValue()`** — parameterized SP parameters.

**PROJECT EXAMPLE:**
- **File:** `PaymentReminderEmailDataService.cs` — `var parameters = new { EmailTransactionID = ... }; await con.ExecuteAsync(Config.UpdatePaymentReminderEmail, parameters, commandType: CommandType.StoredProcedure)` — Dapper maps the anonymous object properties to SP parameters automatically.
- **File:** `ConfigEmailSMTPDataService.cs` — `cmd.Parameters.AddWithValue("@SMTPId", configEmailSMTPDTO.SMTPId)` — parameterized ADO.NET.

---

### ADO.NET vs DAPPER

**QUESTION:**  
Why does your project use two different data access approaches — Dapper and raw ADO.NET?

**ANSWER:**  
- `PaymentReminderEmailDataService` uses **Dapper** — clean async API, automatic object mapping, concise code.
- `ConfigEmailSMTPDataService` uses **raw ADO.NET** (`SqlCommand`, `SqlDataAdapter`, `DataTable`) — likely legacy code or written before Dapper was added.

**This is a missing best practice** — `ConfigEmailSMTPDataService` should be refactored to use Dapper like `PaymentReminderEmailDataService`, which would eliminate the need for `TableUtilities.ConvertDataTable<T>` entirely.

---

## 4. PROJECT ARCHITECTURE SUMMARY (DETAILED)

### Layers in this Project

| Layer | Class | Responsibility |
|---|---|---|
| Host / Entry | `Program.cs` | DI registration, host configuration |
| Config | `Config.cs` | Static config holder |
| Scheduler | `Worker.cs` | Interval-based execution trigger |
| Business Logic | `PaymentReminderService.cs` | Email processing, SMTP sending |
| Data Access | `PaymentReminderEmailDataService.cs` | Email transaction CRUD |
| Data Access | `ConfigEmailSMTPDataService.cs` | SMTP config retrieval |
| Models | `PaymentReminderEmailTransaction.cs`, `ConfigEmailSMTP.cs` | DTOs |
| Utilities | `TableUtilities.cs` | DataTable → object mapper |
| External | `Crypter.dll` | Encryption/decryption |

---

## 5. TOP 30 MOST IMPORTANT INTERVIEW QUESTIONS (Project-Specific)

1. What is a Background Service in .NET 8 and how is it different from a regular console app?
2. How does `Worker.cs` know when to stop running?
3. Why are all services registered as Singleton and not Scoped?
4. What is the role of `CancellationToken` in `ExecuteAsync`?
5. How does the project handle failures — what happens if the DB is down during a run?
6. Why does `PaymentReminderService.ExecuteTask()` group emails by `AssignmentID`?
7. Why is `StringBuilder` used to build email bodies instead of string concatenation?
8. How does the email threading logic work — what is `emailsForAssignments.Skip(1)`?
9. What is the purpose of `Config.IsTestingPhase` and how does it affect email sending?
10. How are SMTP passwords secured in this project?
11. What is `Crypter.dll` and what operations does it perform?
12. Why are stored procedure names in `appsettings.json` and not hardcoded?
13. How does Dapper map SQL results to `PaymentReminderEmailTransaction`?
14. What is the difference between `con.QueryAsync<T>` and `con.ExecuteAsync` in Dapper?
15. What is `TableUtilities.ConvertDataTable<T>` and why does it use reflection?
16. How does `DecryptionAndReplaceLogic` work — what does `{{{{(.*?)}}}}` match?
17. What is `ReplaceNewlines()` extension method and why is it needed?
18. What is the difference between the two logging mechanisms (`WriteLog` vs `ILogger<Worker>`)?
19. How does the `appsettings.Development.json` override `appsettings.json`?
20. Why does `ConfigEmailSMTPDataService` use `SqlDataAdapter` instead of Dapper?
21. What is `CommandType.StoredProcedure` and why is it set explicitly?
22. How would you unit test `PaymentReminderService.ExecuteTask()`?
23. What SOLID principles are demonstrated in this project?
24. What happens if `SendEmail` returns `false` — does the status get updated?
25. Why does `GetSmtpData` decrypt `Password_Alternate` but not `Password`?
26. What is the `using` pattern and where is it used in this project?
27. How is multi-language support handled — what languages are supported?
28. Why does `Worker.cs` validate `IntervalMinutes` before starting the loop?
29. How would you add retry logic to the email send operation?
30. What changes would you make to move from file-based logging to structured logging?

---

## 6. MISSING BEST PRACTICES / ENTERPRISE IMPROVEMENTS

### High Priority

1. **Replace static `Config` class with `IOptions<T>`** — enables testability, hot-reload, typed validation.
2. **Unify data access** — refactor `ConfigEmailSMTPDataService` to use Dapper (remove ADO.NET + TableUtilities).
3. **Structured logging** — replace `WriteLog()` with Serilog + file/Seq sinks. Use `ILogger<T>` injection everywhere.
4. **Retry logic** — add Polly for transient DB failures and SMTP failures with exponential backoff.
5. **Unit tests** — current architecture supports mocking via interfaces. Add xUnit + Moq tests for `ExecuteTask`.

### Medium Priority

6. **Health checks** — add `AddHealthChecks()` to monitor DB connectivity.
7. **`IOptions<T>` pattern** — for `ConfigEmailSMTP` settings instead of reading from DB on every email.
8. **Secrets management** — move `DBConnectionString` to Azure Key Vault / environment variable instead of appsettings.json.
9. **Email queue** — move to a message queue (RabbitMQ/Azure Service Bus) instead of polling DB.
10. **Distributed locking** — if multiple instances run, prevent duplicate sends (Redis lock or DB flag).

### Low Priority

11. **Replace `AddWithValue`** with typed parameters to avoid SQL type inference issues.
12. **Cancellation propagation** — pass `CancellationToken` from `ExecuteAsync` down to all DB calls.
13. **AlertManager / dead-letter queue** — alert when email send fails more than N times.
14. **Metrics** — Prometheus / Application Insights for email send rate, failure rate.

---

## 7. REAL-TIME SCENARIO QUESTIONS

**Scenario 1:**  
The payment reminder service runs every 60 minutes, but an email was supposed to be sent at 10:00 AM and was not sent. The DB shows Status = 0 still. How would you debug this?

*Answer clues: Check `Logs/yyyy-MM-dd.log`, check if Worker started, check if `GetReminderEmailTransaction` returned records, check SMTP connectivity, check `IsTestingPhase` setting.*

---

**Scenario 2:**  
A customer complains they received the same reminder email 3 times. What could cause this?

*Answer clues: Race condition if multiple instances are running, `UpdateReminderEmailTransaction` failed silently (returned 0), Status update SP failed, DB transaction not atomic.*

---

**Scenario 3:**  
The SMTP password was rotated in the database but emails are still failing. What would you check?

*Answer clues: `Crypter.Operations.Decrypt` — password in DB is encrypted, must re-encrypt new password using same Crypter DLL before storing. Check if `Password_Alternate` was updated.*

---

**Scenario 4:**  
You need to add support for a new language (e.g., Arabic). What code changes are needed?

*Answer clues: Add entry in `DecryptName()` switch expression. Check if `MessageTextLanguage` field in DB already stores Arabic content. Update SP or DB if new language fields needed.*

---

**Scenario 5:**  
The service is deployed as a Windows Service. After a server reboot, emails are not being sent for 2 hours. Why?

*Answer clues: Service startup type not set to Automatic. Or the interval is 60 minutes and previous run state is lost on restart — on restart it waits a full interval before first run. Fix: run immediately on start, then delay.*

---

**Scenario 6:**  
You're asked to handle 10,000 pending emails in one run. The current code loops through each AssignmentID sequentially. How would you optimize?

*Answer clues: `Parallel.ForEachAsync`, `Task.WhenAll`, throttle with `SemaphoreSlim`, batch DB updates, connection pool limits.*

---

## 8. HR + MANAGER ROUND QUESTIONS

**Q: Explain what this project does in simple terms.**  
"This is an automated email notification service. It runs every hour in the background, checks the database for any payment reminders that haven't been sent yet, and emails them to the respective customers. It also attaches the history of previous reminder emails in the thread, so the customer can see all previous communications."

**Q: What was the business need for this service?**  
"Manually sending payment reminder emails is error-prone and time-consuming. This service automates the process, ensuring reminders go out at the right time without any manual intervention."

**Q: What challenges did you face?**  
"The main challenges were: handling multi-language email bodies (Japanese, Chinese, Korean, etc.), decrypting sensitive customer information stored encrypted in the database, and ensuring that if an email fails to send, the service doesn't crash and retries in the next cycle."

**Q: How did you ensure emails are not sent twice?**  
"After a successful send, we update the `Status` field in the database from 0 to 1. On the next run, the stored procedure only returns records with Status = 0, so already-sent emails are excluded."

**Q: How do you test this service before production deployment?**  
"There's an `IsTestingPhase` flag in the config. When set to `true`, all emails are redirected to a test email address (`rushikesh.patil@crimsoni.com`) regardless of the actual recipient. This prevents real customers from receiving test emails."

---

## 9. QUICK REVISION NOTES

### Core Architecture
- **.NET 8 Worker Service** — `Microsoft.NET.Sdk.Worker`, not Web SDK
- **Entry point:** `Program.cs` → `Host.CreateDefaultBuilder` → `ConfigureServices` → `RunAsync`
- **Scheduler:** `Worker : BackgroundService` → `ExecuteAsync` → loop with `Task.Delay`
- **Business logic:** `PaymentReminderService.ExecuteTask()`
- **Data access:** `PaymentReminderEmailDataService` (Dapper) + `ConfigEmailSMTPDataService` (ADO.NET)

### DI & Lifetimes
- All services: **Singleton** (no scoped — no HTTP requests)
- Injection via constructors, interfaces as abstractions
- `Config.Initialize()` called before DI build — static config holder

### Data Flow
1. `GetReminderEmailTransaction()` → SP `CS_GetPaymentReminderEmail` → `List<PaymentReminderEmailTransaction>`
2. Group by `AssignmentID` → sort by `PaymentReminderStageID` desc → `First()` = current, `Skip(1)` = history
3. Build `StringBuilder` body — append `GetHtmlFormattedBodyLang()` for each previous sent email
4. `GetSmtpData()` → SP `CS_GetConfigEmailSMTPOnFilter` → decrypt password → `SmtpClient.Send()`
5. `UpdateReminderEmailTransaction()` → SP `CS_UpdatePaymentReminderEmail` → Status = 1

### Key Classes
| Class | Inherits/Implements | Key Method |
|---|---|---|
| Worker | BackgroundService | ExecuteAsync() |
| PaymentReminderService | — | ExecuteTask(), SendEmail(), WriteLog() |
| PaymentReminderEmailDataService | IPaymentReminderEmailDataService | GetReminderEmailTransaction(), UpdateReminderEmailTransaction() |
| ConfigEmailSMTPDataService | IConfigEmailSMTPDataService | GetSmtpData() |
| Config | static class | Initialize() |
| TableUtilities | static class | ConvertDataTable<T>() |

### Key NuGet Packages
- **Dapper 2.1.66** — micro ORM
- **Microsoft.Extensions.Hosting** — Generic Host
- **Microsoft.Extensions.Hosting.WindowsServices** — Windows Service support
- **System.Data.SqlClient + Microsoft.Data.SqlClient** — SQL Server drivers

### Security
- SMTP passwords encrypted in DB, decrypted by `Crypter.Operations.Decrypt()`
- Email addresses decrypted by `Crypter.Operations.CrypterEmailCommaSeperator()`
- Customer names in email body encrypted as `{{token}}`, decrypted in `DecryptionAndReplaceLogic()`
- `IsTestingPhase = true` redirects all emails to test address

---

## 10. TOP 10 STRONGEST CONCEPTS DEMONSTRATED

1. **Background Service / Hosted Service** — Textbook implementation of `BackgroundService` with `CancellationToken` and configurable interval.
2. **Dependency Injection** — Clean interface-based DI with proper Singleton registration in Generic Host.
3. **Async/Await** — Consistent use throughout Worker, business logic, and data access layers.
4. **DAO Pattern** — Clear separation of data access from business logic with interface abstraction.
5. **Dapper Micro-ORM** — Efficient async SP execution with automatic mapping.
6. **Stored Procedure Usage** — All DB operations via SPs, no inline SQL, proper parameterization.
7. **StringBuilder for String Building** — Efficient email body construction in a loop.
8. **Configuration Management** — Environment-aware config via appsettings.json hierarchy.
9. **Exception Handling / Graceful Degradation** — Errors logged and suppressed to keep service running.
10. **LINQ on In-Memory Collections** — Practical use of `Where`, `Select`, `Distinct`, `OrderByDescending`, `Skip`, `First`.

---

## 11. TOP 10 CONCEPTS MISSING OR WEAK

1. **IOptions<T>** — Static `Config` class not testable; should use typed options pattern.
2. **Entity Framework / Code-First** — No EF; relies on SPs and Dapper. Acceptable but limits ORM features.
3. **Structured / Centralized Logging** — File-based custom logging; no Serilog, NLog, or Application Insights.
4. **Retry / Resilience Policies** — No Polly; transient SMTP/DB failures not retried.
5. **Unit Testing** — No test project; code is testable via interfaces but untested.
6. **Repository Pattern / Unit of Work** — DAO pattern used; no generic repository or transaction management.
7. **AutoMapper** — Manual mapping via reflection `TableUtilities`; AutoMapper would be cleaner.
8. **Health Checks** — No `AddHealthChecks()` for DB or SMTP connectivity monitoring.
9. **Secrets Management** — DB connection string and credentials in `appsettings.json`; should use Key Vault or environment secrets.
10. **Concurrent/Parallel Processing** — Emails processed sequentially per `AssignmentID`; no parallel processing for high volume.
