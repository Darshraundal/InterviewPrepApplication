# CSInvoice Project — Interview Preparation Guide
> Generated: 2026-05-18 | Target: 3–5 Years Experienced Developer

---

## PROJECT ARCHITECTURE SUMMARY

### What Is This Project?
CSInvoice is a **.NET Core 6.0 Background Worker Service** — not a Web API, not an MVC app. It is a headless, scheduled service that runs every 2 minutes, queries SQL Server for pending invoices, generates PDFs by calling an external PDF engine, and sends emails to clients.

### Complete Architecture Flow

```
appsettings.json
      ↓
  Program.cs  (loads config, registers Worker as IHostedService)
      ↓
   Worker.cs  (BackgroundService — polls every Config.IntervalMinutes)
      ↓ (parallel tasks)
 ┌────────────────────────────────────────────────────────────────┐
 │  GenerateDocumentsService.cs  (orchestration layer)            │
 │   ├─ GenerateNormalInvoices()                                  │
 │   ├─ GenerateCPInvoices()                                      │
 │   └─ GenerateMonthlyInvoicesforOrganizations()                 │
 └────────────────────────────────────────────────────────────────┘
      ↓
   DAL/*.cs  (DAO classes → SQL Server stored procedures)
      ↓
 Crypter.Operations.TableDataDecrypt()  (decrypt sensitive columns)
      ↓
 Import.TranslateDBInvoice()  (DTO → Invoice domain object)
      ↓
 DocumentGenerateFactory.CreateDocumentObj()  (Factory + Unity IoC)
      ↓
 PDFDocumentsGenerationUtility.cs  (IDocumentGenerate implementation)
      ↓
 PdfEngineService.GeneratePDF()  →  HTTP POST  →  printengine.enago.com
      ↓
 Email sent + NLog file logging
```

### Key Technology Choices
| Concern | Technology |
|---------|-----------|
| Framework | .NET Core 6.0 Worker Service |
| Database Access | SqlClient + Stored Procedures (DAO pattern) |
| PDF Generation | External HTTP service (printengine.enago.com) |
| Dependency Injection | Unity Container (partial), manual instantiation |
| Logging | NLog 5.0 |
| Serialization | Newtonsoft.Json |
| Encryption | Custom Crypter project reference |
| Timezone | TimeZoneConverter NuGet + Windows-Linux-TimeZone.json |
| IoC | Unity.Container 5.11.10 |

---

---

# .NET / .NET CORE QUESTIONS

---

QUESTION:
What is a Worker Service in .NET Core, and why did you choose it for this project?

ANSWER:
A Worker Service is a long-running background process hosted by the .NET Generic Host. It is ideal for scheduled tasks, queue consumers, and service daemons that don't need HTTP endpoints. Unlike a Web API, it has no controllers or routing — it just runs continuously.

PROJECT EXAMPLE:
- File: Worker.cs
- Class: Worker : BackgroundService
- Method: ExecuteAsync(CancellationToken stoppingToken)
- The Worker polls every `Config.IntervalMinutes` (default: 2 minutes) and spawns three parallel tasks: `GenerateNormalInvoices()`, `GenerateCPInvoices()`, and `GenerateMonthlyInvoicesforOrganizations()`. This makes it a lightweight alternative to Windows Task Scheduler or a separate timer-based console app — it self-manages its lifecycle through the Generic Host.

FOLLOW-UP QUESTIONS:
1. How is the Worker registered with the Generic Host?
2. What happens if ExecuteAsync throws an unhandled exception?
3. How would you add graceful shutdown handling in Worker?

IMPORTANT FOR INTERVIEW:
In Program.cs, the Worker is registered via `services.AddHostedService<Worker>()`. If ExecuteAsync throws and is unhandled, the host shuts down — so wrapping the polling loop in try/catch is critical. `IHostApplicationLifetime` is injected into the Worker constructor to support graceful stop.

---

QUESTION:
How is the application configured, and how do you access configuration values at runtime?

ANSWER:
Configuration is loaded from `appsettings.json` using the .NET Generic Host's built-in `IConfiguration` and then mapped into a static class for convenient global access.

PROJECT EXAMPLE:
- File: Program.cs, Config.cs, appsettings.json
- Class: Config (static)
- Method: Program.cs reads `IConfiguration` and sets static properties on Config
- Properties include: `Config.ConnectionString`, `Config.IntervalMinutes`, `Config.RunAutomaticaly`, and 8 boolean flags like `Config.GenerateNormalInvoices`, `Config.GenerateCPInvoices`, etc. Each DAO class then accesses `Config.ConnectionString` directly: `public static string connectionString = Config.ConnectionString;`

FOLLOW-UP QUESTIONS:
1. What is the difference between IConfiguration and IOptions<T>?
2. How would you reload configuration without restarting the service?
3. Why use a static Config class instead of injecting IOptions<T>?

IMPORTANT FOR INTERVIEW:
The project uses a static Config class instead of `IOptions<T>` — simpler but not testable via DI. In enterprise projects, `IOptions<T>` with `Configure<T>()` is preferred because it supports validation, named options, and injected-lifetime configuration. For `appsettings.Development.json`, .NET automatically merges it with `appsettings.json` in Development environment.

---

QUESTION:
What is Dependency Injection, and how is it used in this project?

ANSWER:
Dependency Injection (DI) is a pattern where an object's dependencies are provided externally rather than created inside the class. .NET Core's Generic Host has a built-in DI container. This project uses both the built-in host DI and Unity Container for specific parts.

PROJECT EXAMPLE:
- File: Worker.cs, Interface/DocumentGenerateFactory.cs
- Class: Worker constructor → `Worker(ILogger<Worker> logger, IHostApplicationLifetime lifetime)` — both are injected by the Generic Host's DI container
- File: DocumentGenerateFactory.cs — uses Unity Container for interface-to-implementation mapping: `container.RegisterType<IDocumentGenerate, PDFDocumentsGenerationUtility>(DocType)` → `container.Resolve<IDocumentGenerate>(DocType)`
- Other classes like `AssignmentsDAO` and `GenerateDocumentsService` are instantiated manually with `new`, not through DI

FOLLOW-UP QUESTIONS:
1. What are the three service lifetimes in .NET Core DI?
2. What is the difference between AddSingleton, AddScoped, and AddTransient?
3. Why does this project use Unity Container alongside the built-in DI?

IMPORTANT FOR INTERVIEW:
Service lifetimes: **Singleton** (one instance for app lifetime), **Scoped** (one per request/scope), **Transient** (new instance every time). The project uses Unity for the Factory pattern to resolve `IDocumentGenerate` by string key (document type) — something the built-in DI container doesn't support natively without named registrations. In newer .NET, `Keyed Services` (from .NET 8) would eliminate this Unity dependency.

---

QUESTION:
What is the Singleton design pattern, and where is it used in this project?

ANSWER:
The Singleton pattern ensures only one instance of a class exists throughout the application lifetime. It is used when shared state or expensive initialization should happen only once.

PROJECT EXAMPLE:
- File: Manager/Import.cs
  - Class: Import
  - Pattern: `private static Import _instance; public static Import Instance { get { if (_instance == null) _instance = new Import(); return _instance; } }`
  - Method: `TranslateDBInvoices(List<InvoiceSendingDetailDTO>)` — translates DTOs to domain Invoice objects; also fetches template labels from DB
- File: Manager/DocumentsGenerationUtility.cs
  - Class: DocumentsGenerationUtility
  - Pattern: Same singleton via `ObjInstance` property, holds `DocumentType` string

FOLLOW-UP QUESTIONS:
1. Is this singleton thread-safe? How would you make it thread-safe?
2. What is the difference between Singleton design pattern and Singleton service lifetime in .NET DI?
3. What are the downsides of singletons?

IMPORTANT FOR INTERVIEW:
The current `Import.Instance` is NOT thread-safe — if two threads call it simultaneously when `_instance` is null, two instances could be created. Thread-safe solutions: double-checked locking with `lock`, `Lazy<T>`, or static initialization. In .NET DI, `AddSingleton<T>()` is thread-safe by design. Singletons make unit testing harder because they hold global state.

---

QUESTION:
What is the Factory design pattern, and how is it implemented in this project?

ANSWER:
The Factory pattern provides a centralized way to create objects without exposing the creation logic to the caller. It returns instances of an interface, hiding the concrete implementation.

PROJECT EXAMPLE:
- File: Interface/DocumentGenerateFactory.cs
- Class: DocumentGenerateFactory
- Method: `CreateDocumentObj(string DocType, bool _IsPdf)` → returns `IDocumentGenerate`
- Implementation: Registers `PDFDocumentsGenerationUtility` with Unity Container under the `DocType` key, then resolves it: `container.RegisterType<IDocumentGenerate, PDFDocumentsGenerationUtility>(DocType)` → `ObjSelector = container.Resolve<IDocumentGenerate>(DocType)`
- Called from: GenerateDocumentsService.cs when processing each invoice type

FOLLOW-UP QUESTIONS:
1. What is the difference between Factory Method and Abstract Factory patterns?
2. Why use Unity Container inside the Factory instead of just `new PDFDocumentsGenerationUtility()`?
3. How would you add a Word document generator alongside the PDF generator?

IMPORTANT FOR INTERVIEW:
Using Unity inside the Factory allows future extensibility — you can register a `WordDocumentsGenerationUtility` for a different `DocType` string without changing the calling code. This is the Open/Closed principle in practice.

---

QUESTION:
What is the Strategy design pattern, and where does this project demonstrate it?

ANSWER:
Strategy defines a family of algorithms (or behaviors), encapsulates each one, and makes them interchangeable. The caller works through a common interface without knowing which concrete implementation it uses.

PROJECT EXAMPLE:
- File: Interface/IDocumentGenerate.cs
- Interface: IDocumentGenerate
- Methods: `ProcessInvoice()`, `ProcessMonthlyInvoice()`, `ProcessCPInvoice()`, `ProcessCancellation()`, `ProcessOrgMonthly()`, `ProcessMonthlyInvoicesDeliveryMailsAndCOE()`
- Concrete implementation: PDFDocumentsGenerationUtility.cs implements all these methods differently for each invoice type
- Caller: GenerateDocumentsService calls the appropriate method through the interface without knowing it's PDFDocumentsGenerationUtility

FOLLOW-UP QUESTIONS:
1. How would you add a new invoice type without modifying GenerateDocumentsService?
2. What SOLID principle does this demonstrate?
3. What is the difference between Strategy and Template Method pattern?

IMPORTANT FOR INTERVIEW:
This demonstrates the Open/Closed Principle — new invoice processing strategies can be added by implementing IDocumentGenerate without modifying existing code. Strategy vs Template Method: Strategy composes behavior via interface (runtime swappable), Template Method uses inheritance to define a skeleton algorithm.

---

QUESTION:
How does this project access the database, and what pattern does it follow?

ANSWER:
The project uses the DAO (Data Access Object) pattern with ADO.NET SqlClient and stored procedures — not Entity Framework. Each DAO class encapsulates all database operations for a specific domain entity.

PROJECT EXAMPLE:
- Files: DAL/AssignmentsDAO.cs, DAL/AssignmentFilesDAO.cs, DAL/AdminMastersDAO.cs, DAL/ClientsDAO.cs, DAL/PaymentMastersDAO.cs, DAL/MessageDAO.cs
- Pattern: Each DAO has `public static string connectionString = Config.ConnectionString;`
- Implementation:
  ```csharp
  SqlCommand cmd = new SqlCommand("CS_GetASNDetailsAfterInvoiceCheck", conn);
  cmd.CommandType = CommandType.StoredProcedure;
  cmd.CommandTimeout = GlobalEnum.TimeoutTime; // 600 seconds
  cmd.Parameters.AddWithValue("@AssignmentID", dto.AssignmentID);
  SqlDataAdapter da = new SqlDataAdapter(cmd);
  da.Fill(ds);
  ```
- Key DAO: AssignmentsDAO.GetAssignmentInvoiceSendingDetails() fetches invoice data; PaymentMastersDAO.GetASN_AdjustmentDetails() fetches adjustment details

FOLLOW-UP QUESTIONS:
1. What is the difference between DAO and Repository pattern?
2. Why use stored procedures instead of inline SQL or ORM?
3. What is the risk of CommandTimeout = 600 seconds?

IMPORTANT FOR INTERVIEW:
DAO and Repository are similar — both abstract data access. Repository is more focused on domain objects and collection-like semantics; DAO is a simpler, infrastructure-level pattern. Stored procedures provide security (no SQL injection), performance (execution plan caching), and encapsulation of DB logic. 600-second timeout was set because invoice generation queries can be long-running aggregation queries over large datasets.

---

QUESTION:
How does this project handle data mapping between database results and domain objects?

ANSWER:
It uses a custom generic translator utility that maps `DataRow` columns to DTO properties using Reflection, instead of an ORM like Entity Framework or Dapper.

PROJECT EXAMPLE:
- File: Utility/TranslatorUtility.cs
- Method: `TranslateObject<T>(T helper, DataRow row)` — iterates DataRow columns and sets matching properties on T using `typeof(T).GetProperty(columnName)?.SetValue(helper, value)`
- Method: `TranslateArray<T>(DataRowCollection rows)` — calls TranslateObject for each row and returns a List<T>
- Used by: DAO classes to convert DataTable results into DTO lists
- Also: Manager/Import.cs → `TranslateDBInvoice(InvoiceSendingDetailDTO dto)` maps the DTO to the heavier `Invoice` domain object

FOLLOW-UP QUESTIONS:
1. What are the performance implications of using Reflection for mapping?
2. How does this compare to AutoMapper or Dapper?
3. What happens if a column name in the DataRow doesn't match the property name in the DTO?

IMPORTANT FOR INTERVIEW:
Reflection-based mapping is flexible but slower than compiled expression trees (AutoMapper) or direct mapping (Dapper). For high-throughput scenarios, AutoMapper with compiled maps or Dapper would be better. The current approach works fine for this service since it processes invoices in batches (not thousands per second). If column name ≠ property name, the property simply isn't set — silent failure, no exception.

---

QUESTION:
How does the project handle encryption and sensitive data?

ANSWER:
The project uses a custom `Crypter` library (referenced as a project dependency) to decrypt sensitive columns after retrieving them from the database. Sensitive fields are never stored or transmitted in plain text.

PROJECT EXAMPLE:
- File: CSInvoice.csproj — `<ProjectReference Include="..\Utility\Crypter\Crypter.csproj" />`
- Called in: DAO classes after filling DataTable → `Crypter.Operations.TableDataDecrypt(dataTable, encryptedColumns)`
- Encrypted columns (defined in Model/Parameters.cs):
  - Personal: `UserName`, `PayerName`, `FirstName`, `LastName`, `ChannelPartnerName`
  - Address: `WorkAddress`, `HomeAddress`, `BillingAddress`, `AccountAddress`
- WCF credentials stored in: Common/clsGlobalCommon.cs → `g_WCF_UserName = "CrimsonWCF"`, `g_WCF_Password = "Cr1ms0nWCF@0123"` (hardcoded — security concern)

FOLLOW-UP QUESTIONS:
1. Why are encrypted columns decrypted in the application layer instead of the database?
2. What is the risk of hardcoding WCF credentials in clsGlobalCommon.cs?
3. How would you improve secret management in this project?

IMPORTANT FOR INTERVIEW:
Hardcoded credentials in clsGlobalCommon.cs is a security vulnerability. Best practice: store secrets in environment variables, Azure Key Vault, or .NET User Secrets. Application-layer decryption (vs DB-layer) gives more control over when and where decryption happens, but requires the encryption key to be available to the app — key management becomes critical.

---

QUESTION:
How does the project implement logging, and what logging framework is used?

ANSWER:
The project uses NLog 5.0 for structured, file-based logging with daily rolling log files.

PROJECT EXAMPLE:
- File: nlog.config (at project root)
- Configuration:
  - Log file path: `${basedir}/Logs/${date:format=yyyy-MM-dd}.log`
  - Format: `${date}|${level:uppercase=true}|${mdlc:item=SessionKey}|${message} ${exception}|${logger}|${all-event-properties}`
  - Archive: Daily rollover, max 5 files, 5MB each
  - UDP Viewer: sends to 127.0.0.1:7071 for real-time monitoring
- Usage in every class:
  ```csharp
  private static NLog.Logger _logger = NLog.LogManager.GetCurrentClassLogger();
  _logger.Info("Processing invoice for AssignmentID: " + id);
  _logger.Error(ex, "Failed to generate PDF");
  ```

FOLLOW-UP QUESTIONS:
1. What is the difference between NLog, Serilog, and Microsoft.Extensions.Logging?
2. What does `GetCurrentClassLogger()` do?
3. How would you add structured logging with correlation IDs?

IMPORTANT FOR INTERVIEW:
`GetCurrentClassLogger()` automatically uses the calling class's full name as the logger name — useful for filtering logs by class. For structured logging, NLog supports properties: `_logger.Info("Processing {AssignmentID}", id)` with structured layout renderers. Microsoft.Extensions.Logging is the abstraction layer — NLog, Serilog can be plugged in as providers. The UDP viewer target allows real-time log monitoring with NLog Viewer tools.

---

QUESTION:
How does the project call the external PDF generation service?

ANSWER:
It uses `HttpClient` to make an HTTP POST request with JSON payload to an external PDF engine service and parses the JSON response.

PROJECT EXAMPLE:
- File: ExternalServices/PdfEngineService.cs
- Class: PdfEngineService
- Method: `GeneratePDF(PDFEngineServiceRequest request)` → `PDFEngineServiceResponse`
- Implementation:
  - Constructor takes `serviceURL` (read from `Config.PDFServiceURL` = "https://printengine.enago.com/process.php")
  - Serializes request to JSON via Newtonsoft.Json
  - `HttpClient.PostAsync()` with `StringContent` and `application/json` media type
  - Timeout: 100,000,000 ms (very large — potential issue)
  - Checks `result.status == "SUCCESS"` to determine success
- Request classes: `CPInvoiceRequest` and `CPSpecialRequest` extend `PDFEngineServiceRequest` with 50+ invoice-specific properties

FOLLOW-UP QUESTIONS:
1. What is wrong with creating a new HttpClient in a constructor?
2. What is HttpClientFactory and why should you use it?
3. How would you add retry logic for failed PDF generation calls?

IMPORTANT FOR INTERVIEW:
Creating `new HttpClient()` in each call or per-class instance causes socket exhaustion under load — each instance doesn't reuse TCP connections. The correct approach is `IHttpClientFactory` (registered in DI) which manages a pool of `HttpMessageHandler` instances. For retry/resilience, `Polly` (via `AddPolicyHandler`) would add exponential backoff. The 100-second timeout on an external service call with no retry policy is a reliability gap.

---

QUESTION:
How does the project handle async/await and parallel execution?

ANSWER:
The Worker uses `Task.Run` and `await Task.WhenAll` to run invoice generation tasks in parallel, and individual methods use async/await for non-blocking I/O.

PROJECT EXAMPLE:
- File: Worker.cs → ExecuteAsync()
- Implementation:
  ```csharp
  var task1 = Task.Run(() => GenerateNormalInvoices());
  var task2 = Task.Run(() => GenerateCPInvoices());
  var task3 = Task.Run(() => GenerateMonthlyInvoicesforOrganizations());
  await Task.WhenAll(task1, task2, task3);
  ```
- Polling loop: `await Task.Delay(TimeSpan.FromMinutes(Config.IntervalMinutes), stoppingToken)`
- The `stoppingToken` (CancellationToken) is passed to allow graceful shutdown

FOLLOW-UP QUESTIONS:
1. What is the difference between Task.Run and async/await?
2. What happens if one of the tasks in Task.WhenAll throws an exception?
3. What is CancellationToken and why is it important here?

IMPORTANT FOR INTERVIEW:
`Task.WhenAll` throws an `AggregateException` if any task fails — inner exceptions can be inspected. If one task fails, the others still run to completion. `CancellationToken` in `Task.Delay` ensures the service responds promptly to shutdown signals (Ctrl+C, Windows service stop) instead of waiting the full 2-minute interval. `Task.Run` offloads work to the thread pool; for true async I/O (like async SQL calls), `await cmd.ExecuteReaderAsync()` would be preferred over `Task.Run(() => syncMethod())`.

---

QUESTION:
How does this project handle cross-platform timezone differences?

ANSWER:
It uses a JSON mapping file and the `TimeZoneConverter` NuGet package to convert Windows timezone names to IANA (Linux) timezone names at runtime.

PROJECT EXAMPLE:
- File: Windows-Linux-TimeZone.json — a dictionary of Windows → IANA timezone name mappings
- File: Code/ConfigManager.cs
- Method: `GetFormattedInvoiceTimeNow(DateTime dt)` and `GetFormattedInvoiceDate(...)`
- Implementation:
  ```csharp
  if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
  {
      // Use IANA timezone from mapping file
  }
  else
  {
      TimeZoneInfo.ConvertTimeBySystemTimeZoneId(dt, "India Standard Time");
  }
  ```
- Default timezone: "India Standard Time" defined in `Common/clsGlobalCommon.cs → destinationTimeZone`

FOLLOW-UP QUESTIONS:
1. Why do Windows and Linux use different timezone format names?
2. What does TimeZoneConverter NuGet package do?
3. How would you handle clients in different timezones for invoice dates?

IMPORTANT FOR INTERVIEW:
Windows uses "India Standard Time", Linux uses "Asia/Kolkata" — different registries. `TimeZoneConverter` (by Matt Johnson-Peck) abstracts this difference transparently. In .NET 6+, `TimeZoneInfo.FindSystemTimeZoneById()` accepts both formats on any platform when `TimeZoneConverter` is registered. For multi-timezone invoice dates, `TimeZoneInfo.ConvertTime()` with per-client timezone strings (stored in DB per client) would be the correct approach.

---

QUESTION:
What is the DTO pattern and how is it used in this project?

ANSWER:
DTO (Data Transfer Object) is a simple object used to carry data between layers. It avoids exposing domain objects or database entities directly.

PROJECT EXAMPLE:
- File: Model/InvoiceSendingDetailDTO.cs
- Class: InvoiceSendingDetailDTO — 100+ properties covering financial data, client info, invoice metadata, and template paths
- Attributes: `[DataContract(Namespace="http://www.enago.net/CrimsonWCF/2010/01/01")]`, `[Serializable]`, `[DataMember]` on each property
- Other DTOs: AssignmentFilesDTO, AssignmentAdjustmentDetailDTO, AdminChannelPartnerMasterDTO, MessageDTO, etc.
- Flow: SQL Server returns DataTable → TranslatorUtility maps to DTO → Import maps DTO to Invoice domain object → PDFDocumentsGenerationUtility uses Invoice

FOLLOW-UP QUESTIONS:
1. Why are DTOs marked with [DataContract] and [DataMember] attributes?
2. What is the difference between a DTO and a domain model?
3. Why is InvoiceSendingDetailDTO so large (100+ properties)?

IMPORTANT FOR INTERVIEW:
`[DataContract]` and `[DataMember]` are WCF serialization attributes — this project historically shared DTOs with a WCF service (hence the namespace `http://www.enago.net/CrimsonWCF/2010/01/01`). In modern projects, these would be replaced with simpler POCOs and JSON serialization attributes. Large DTOs indicate an "anemic domain model" smell — splitting into smaller focused DTOs (SRP) would improve maintainability.

---

QUESTION:
How are SOLID principles applied in this project?

ANSWER:
The project demonstrates several SOLID principles, though not all are fully implemented.

PROJECT EXAMPLE:

**S — Single Responsibility Principle:**
- Each DAO class handles one entity: `AssignmentsDAO` only handles assignments, `PaymentMastersDAO` only handles payment masters
- `ConfigManager.cs` only handles date/timezone formatting
- `MailUtility.cs` only handles mail-specific string operations

**O — Open/Closed Principle:**
- `IDocumentGenerate` interface allows new invoice generators to be added without modifying `GenerateDocumentsService` — just implement the interface and register in factory

**L — Liskov Substitution Principle:**
- `PDFDocumentsGenerationUtility` fully implements all `IDocumentGenerate` methods — can be substituted wherever `IDocumentGenerate` is expected

**I — Interface Segregation Principle:**
- Partially implemented — `IDocumentGenerate` has many methods; a client needing only `ProcessCPInvoice()` is forced to implement all others

**D — Dependency Inversion Principle:**
- `GenerateDocumentsService` depends on `IDocumentGenerate` (abstraction), not `PDFDocumentsGenerationUtility` (concrete) — done via Factory

FOLLOW-UP QUESTIONS:
1. Where is ISP violated in this project?
2. How would you refactor the Singleton pattern in Import.cs to follow DIP?
3. Give an example of how OCP saved effort in this project.

IMPORTANT FOR INTERVIEW:
ISP violation: IDocumentGenerate has 7 methods. A CP invoice processor only needs `ProcessCPInvoice()` and `ProcessCPInvoice_Special()` but must implement all 7. Fix: split into `INormalInvoiceProcessor`, `ICPInvoiceProcessor`, `IMonthlyInvoiceProcessor`. DIP violation: DAO classes and GenerateDocumentsService use `new` for instantiation instead of injected interfaces — makes unit testing impossible without mocking frameworks.

---

QUESTION:
How does exception handling work in this project?

ANSWER:
The project uses try/catch blocks in DAO classes with custom exception propagation, and logs all exceptions via NLog before rethrowing or swallowing.

PROJECT EXAMPLE:
- File: DAL/*.cs — all DAO methods wrap SQL operations in try/catch
- File: Exceptions/ — custom exception classes defined here
- Pattern:
  ```csharp
  try {
      // SQL operation
  } catch (Exception ex) {
      _logger.Error(ex, "Error in GetAssignmentInvoiceSendingDetails: " + ex.StackTrace);
      throw; // or custom exception
  }
  ```
- File: Worker.cs — wraps the parallel task execution in try/catch to prevent the service from crashing on a single invoice failure

FOLLOW-UP QUESTIONS:
1. What is the difference between `throw` and `throw ex`?
2. What is a global exception handler in .NET Core?
3. How would you implement a dead-letter queue for failed invoice generations?

IMPORTANT FOR INTERVIEW:
`throw` (rethrow) preserves the original stack trace; `throw ex` resets the stack trace to the current line — always prefer `throw`. In Web APIs, middleware-based global exception handling (`UseExceptionHandler`) is standard. For this worker service, wrapping each invoice in try/catch and logging failures (rather than crashing) is correct — one bad invoice shouldn't stop all others.

---

QUESTION:
How does the project use enums and constants?

ANSWER:
All enums and constants are centralized in `GlobalEnum.cs`, providing a single source of truth for magic values used across the project.

PROJECT EXAMPLE:
- File: Enum/GlobalEnum.cs
- `const int TimeoutTime = 600` — SQL command timeout used by all DAO classes
- `enum enumServiceWorkFlowType` — identifies business unit (Enago=1, Ulatus=2, Voxtab=3, etc.)
- `enum FolderID` — 40+ file storage folder identifiers (InquiryEditingFile=1, AssignmentInvoices=8, ChannelPartnerInvoices=26, etc.)
- `enum TaskRelatedCategory` — invoice/assignment type categorization
- `enum enumSinglebrandGeo` — single-brand geography codes (Taiwan=2, China=4, Korea=11, etc.)

FOLLOW-UP QUESTIONS:
1. What is the difference between const, readonly, and static readonly?
2. When would you use an enum vs a lookup table in the database?
3. What are [Flags] enums and when are they useful?

IMPORTANT FOR INTERVIEW:
`const` = compile-time constant, baked into calling assembly — changing it requires recompiling all dependents. `readonly` = runtime constant, set in constructor. `static readonly` = runtime constant, set at class initialization — safer for values that might change between builds. For FolderID with 40+ values, a database lookup table would be more maintainable — no recompile needed to add new folder types.

---

QUESTION:
How does the project use the Generic Host and what does Program.cs set up?

ANSWER:
Program.cs uses `IHostBuilder` to set up the Generic Host, which manages the application's lifetime, configuration, logging, and DI container. The Worker is registered as a hosted service.

PROJECT EXAMPLE:
- File: Program.cs
- Implementation:
  ```csharp
  IHost host = Host.CreateDefaultBuilder(args)
      .ConfigureServices((hostContext, services) => {
          services.AddHostedService<Worker>();
      })
      .Build();
  
  // Load config into static Config class
  IConfiguration configuration = host.Services.GetRequiredService<IConfiguration>();
  Config.ConnectionString = configuration["Settings:ConnectionString"];
  Config.IntervalMinutes = int.Parse(configuration["ConfigurationManager:IntervalMinutes"]);
  // ... other Config properties
  
  host.Run();
  ```
- `Host.CreateDefaultBuilder()` automatically sets up: appsettings.json loading, environment variable overrides, NLog integration, and the default DI container

FOLLOW-UP QUESTIONS:
1. What does Host.CreateDefaultBuilder() configure automatically?
2. What is the difference between Generic Host and Web Host?
3. How would you run this as a Windows Service or Linux systemd service?

IMPORTANT FOR INTERVIEW:
`CreateDefaultBuilder` wires up: JSON config files, environment variables, command-line args, console logging, and the host lifetime. Generic Host (non-web) vs WebHost: Generic Host has no HTTP pipeline — lighter weight, no Kestrel. To run as Windows Service: add `UseWindowsService()`. For Linux systemd: add `UseSystemd()`. Both are single NuGet package additions.

---

QUESTION:
How does the project use Reflection, and what are the implications?

ANSWER:
Reflection is used in `TranslatorUtility` to dynamically map database column names to DTO property names at runtime without code generation or ORM.

PROJECT EXAMPLE:
- File: Utility/TranslatorUtility.cs
- Method: `TranslateObject<T>(T helper, DataRow row)`
- Implementation:
  ```csharp
  foreach (DataColumn col in row.Table.Columns) {
      PropertyInfo prop = typeof(T).GetProperty(col.ColumnName);
      if (prop != null && row[col] != DBNull.Value)
          prop.SetValue(helper, Convert.ChangeType(row[col], prop.PropertyType));
  }
  ```
- Used by all DAO classes to avoid writing manual mapping for 100+ property DTOs

FOLLOW-UP QUESTIONS:
1. What is the performance cost of Reflection?
2. How does AutoMapper avoid Reflection overhead?
3. When is Reflection appropriate vs inappropriate?

IMPORTANT FOR INTERVIEW:
Reflection is 10-50x slower than direct property access because it bypasses compile-time optimization. AutoMapper uses compiled expression trees (generated once, cached) for near-native speed. For this project, reflection is acceptable since invoice generation doesn't require microsecond throughput. Source generators (in .NET 6+) are another option — generate mapping code at compile time with zero runtime overhead.

---

QUESTION:
How does the project handle stored procedures, and what are the SQL patterns used?

ANSWER:
All database operations use SQL Server stored procedures via ADO.NET SqlCommand. The project never uses inline SQL or ORM queries.

PROJECT EXAMPLE:
- File: All DAL/*.cs files
- Stored procedures called: `CS_GetASNDetailsAfterInvoiceCheck`, `GetASN_AdjustmentDetails`, `CS_AssignmentsGetDetailsByAssignmentID`, `CS_Messages_Save`, `CS_GetAdminChannelPartnerMaster`, `GetAssigmentFiles`
- Pattern:
  ```csharp
  using SqlConnection conn = new SqlConnection(connectionString);
  SqlCommand cmd = new SqlCommand("CS_GetASNDetailsAfterInvoiceCheck", conn);
  cmd.CommandType = CommandType.StoredProcedure;
  cmd.CommandTimeout = GlobalEnum.TimeoutTime; // 600s
  cmd.Parameters.AddWithValue("@InvoiceTypeID", invoiceTypeId);
  SqlDataAdapter da = new SqlDataAdapter(cmd);
  DataSet ds = new DataSet();
  da.Fill(ds);
  ```

FOLLOW-UP QUESTIONS:
1. What are the advantages of stored procedures over inline SQL?
2. What is AddWithValue vs Add with explicit SqlDbType?
3. Why is CommandTimeout set to 600 seconds?

IMPORTANT FOR INTERVIEW:
`AddWithValue` can cause type inference issues — e.g., passing a string for a `nvarchar` column works, but for `datetime` or `decimal`, SQL Server might infer wrong types. `Add("@Param", SqlDbType.Int).Value = value` is more explicit and avoids implicit conversion overhead. Stored procedures have pre-compiled execution plans — faster repeated calls. 600-second timeout is set for long-running invoice aggregation queries.

---

QUESTION:
How does the project demonstrate the interface vs abstract class decision?

ANSWER:
The project uses interfaces (`IDocumentGenerate`) for contractual behavior that multiple implementations could satisfy. There are no abstract base classes, which means shared behavior isn't reused — a potential improvement.

PROJECT EXAMPLE:
- File: Interface/IDocumentGenerate.cs
- Interface: IDocumentGenerate with 7 method signatures + 3 properties
- File: PDFDocumentsGenerationUtility.cs — only implementation
- No abstract base class exists, so common logic (logging, error handling) is duplicated across invoice processing methods

FOLLOW-UP QUESTIONS:
1. When would you use an abstract class instead of an interface?
2. Can a class implement multiple interfaces in C#?
3. What is the benefit of interface default implementations (C# 8+)?

IMPORTANT FOR INTERVIEW:
Interface: defines a contract (what), no implementation. Abstract class: can provide partial implementation (what + some how), single inheritance only. Use interface when unrelated classes need to satisfy a contract. Use abstract class when sharing base implementation. In this project, an abstract class `BaseDocumentGenerator` with shared logging/error handling would eliminate duplication across invoice types. C# 8+ interface default implementations allow adding methods to interfaces without breaking existing implementations.

---

---

# DATABASE / SQL QUESTIONS

---

QUESTION:
How does this project use SQL Server stored procedures, and what query patterns are involved?

ANSWER:
Every database call in this project uses stored procedures. They encapsulate business logic at the DB layer — fetching invoiceable assignments, adjustment details, channel partner data, etc.

PROJECT EXAMPLE:
- Key SPs: `CS_GetASNDetailsAfterInvoiceCheck` (main invoice query), `GetASN_AdjustmentDetails`, `CS_AssignmentsGetDetailsByAssignmentID`, `CS_GetAdminChannelPartnerMaster`
- SP calls are in: AssignmentsDAO, PaymentMastersDAO, AssignmentFilesDAO, AdminMastersDAO
- All use: `CommandType.StoredProcedure`, `SqlDataAdapter.Fill()`, 600s timeout
- Encrypted columns are listed in `Parameters.cs` and decrypted after the DataTable is filled

FOLLOW-UP QUESTIONS:
1. How would you optimize a slow stored procedure in this context?
2. What indexing strategy makes sense for an invoice query filtering by AssignmentID and InvoiceTypeID?
3. How would you implement pagination for large invoice result sets?

IMPORTANT FOR INTERVIEW:
For invoice queries, a composite index on `(AssignmentID, InvoiceTypeID, InvoiceStatus)` with `INCLUDE` clauses for frequently returned columns would eliminate key lookups. Pagination: use `OFFSET n ROWS FETCH NEXT m ROWS ONLY` (SQL Server 2012+) — requires an `ORDER BY` clause. For the 600s timeout, query analysis with `SET STATISTICS IO ON` and execution plan review would identify missing indexes or table scans.

---

QUESTION:
What SQL performance concerns exist in a project like this?

ANSWER:
Long-running invoice queries (600s timeout), potential N+1 problems if fetching per-assignment, and unindexed lookups on large assignment tables are the main concerns.

PROJECT EXAMPLE:
- CommandTimeout = 600 seconds suggests existing queries are slow
- `CS_GetASNDetailsAfterInvoiceCheck` likely joins multiple tables (Assignments, Clients, Payments, Invoices)
- Decryption of 100+ column DataTable rows in application layer adds CPU overhead
- No caching layer — every 2-minute cycle hits the DB fresh

FOLLOW-UP QUESTIONS:
1. What is an index seek vs index scan?
2. What are CTEs and how would they help in invoice queries?
3. What is a covering index?

IMPORTANT FOR INTERVIEW:
Index seek: directly finds rows matching condition (fast). Index scan: reads entire index (slow for large tables). CTE (Common Table Expression) improves readability of multi-step aggregation — e.g., calculating invoice totals then joining to client data. Covering index: index includes all columns needed by the query in the `INCLUDE` clause, eliminating table lookups. For the invoice service, adding a non-clustered index on `InvoiceStatus`, `AssignmentID` with covering columns would significantly reduce query time.

---

QUESTION:
How would you implement pagination in the stored procedures used by this project?

ANSWER:
This project currently does not implement pagination — it fetches all pending invoices in one query. Enterprise-grade pagination uses `OFFSET/FETCH` in SQL Server.

PROJECT EXAMPLE:
- Current: `CS_GetASNDetailsAfterInvoiceCheck` returns all eligible assignments at once
- Missing implementation — for high-volume invoice scenarios, this could return thousands of rows
- Ideal implementation:
  ```sql
  SELECT * FROM Assignments
  WHERE InvoiceStatus = 'Pending'
  ORDER BY AssignmentID
  OFFSET @PageNumber * @PageSize ROWS
  FETCH NEXT @PageSize ROWS ONLY;
  ```

FOLLOW-UP QUESTIONS:
1. What is keyset pagination vs offset pagination?
2. How do you count total records alongside a paginated query efficiently?
3. What is the problem with OFFSET pagination on large datasets?

IMPORTANT FOR INTERVIEW:
Offset pagination performance degrades on large tables because SQL Server must skip N rows (reads and discards them). Keyset pagination ("seek method") — using `WHERE id > lastSeenId` — is O(1) regardless of page depth, but requires a stable sort key. For count with pagination, use `COUNT(*) OVER()` window function in the same query to avoid a second DB roundtrip.

---

---

# PROJECT ARCHITECTURE SUMMARY

## End-to-End Request Lifecycle
1. **Host starts** → Program.cs loads appsettings.json → initializes static Config → registers Worker
2. **Worker.ExecuteAsync()** runs in loop → waits `Config.IntervalMinutes` → spawns 3 parallel tasks
3. **GenerateDocumentsService** (per task type) → calls DAO → executes stored procedure → gets DataTable
4. **TranslatorUtility** maps DataTable rows → DTO objects → decrypts sensitive columns via Crypter
5. **Import.TranslateDBInvoice()** maps DTO → Invoice domain object (fetches template labels from DB)
6. **DocumentGenerateFactory.CreateDocumentObj()** → Unity Container resolves → PDFDocumentsGenerationUtility
7. **PDFDocumentsGenerationUtility.Process*()** → builds CPInvoiceRequest/PDFEngineServiceRequest
8. **PdfEngineService.GeneratePDF()** → HTTP POST to printengine.enago.com → returns PDF binary/URL
9. **Email sent** with PDF attachment → **NLog** logs success or failure
10. **Loop repeats** after 2 minutes

## Authentication Flow
- None (background service, no user-facing endpoints)
- DB connection authenticated via SQL Server credentials in connection string
- External PDF service authenticated via property_id in request payload
- WCF credentials hardcoded in clsGlobalCommon.cs (improvement needed)

---

# TOP 30 PROJECT-SPECIFIC INTERVIEW QUESTIONS

1. What type of .NET application is CSInvoice, and why is it not a Web API?
2. Explain the Worker.cs class and BackgroundService lifecycle.
3. How does Program.cs wire up the service and load configuration?
4. Walk me through the execution flow from Worker polling to PDF generation.
5. What is the Factory pattern in DocumentGenerateFactory? Why use Unity Container there?
6. What does IDocumentGenerate interface contain, and which class implements it?
7. How does the Singleton pattern work in Import.cs? Is it thread-safe?
8. How does TranslatorUtility map database results to DTOs without EF or Dapper?
9. Why does the project use Reflection in TranslatorUtility? What are the trade-offs?
10. How does the project decrypt sensitive data, and which columns are encrypted?
11. What is the role of PDFDocumentsGenerationUtility.cs (the 366KB file)?
12. How does PdfEngineService.GeneratePDF() communicate with the external service?
13. What stored procedures does AssignmentsDAO call, and what data do they return?
14. Why is CommandTimeout set to 600 seconds in all DAO classes?
15. How does ConfigManager.cs handle cross-platform timezone differences?
16. What are the 8 boolean flags in Config.cs, and how do they control service behavior?
17. How does Task.WhenAll work in Worker.cs for parallel invoice generation?
18. What happens if one of the parallel tasks fails in Worker.cs?
19. How does NLog rolling file logging work in this project?
20. What are the service workflow types in enumServiceWorkFlowType, and what do they represent?
21. How does the project handle Channel Partner invoices differently from Normal invoices?
22. What is the purpose of Parameters.cs in the Model folder?
23. How does Windows-Linux-TimeZone.json support cross-platform deployment?
24. What security vulnerabilities exist in this project?
25. How would you refactor the DAO pattern to make it testable?
26. How does the monthly invoice generation differ from normal invoice generation timing?
27. What is the InvoiceSendingDetailDTO, and why does it have 100+ properties?
28. How does Import.TranslateDBInvoice() differ from TranslatorUtility.TranslateObject()?
29. How would you add a new invoice type (e.g., CreditNote) to this service?
30. How would you containerize this Worker Service for Docker/Kubernetes deployment?

---

# MISSING BEST PRACTICES

### High Priority
1. **HttpClientFactory** — PdfEngineService creates `new HttpClient()` directly → socket exhaustion risk. Should use `IHttpClientFactory` with `AddHttpClient<PdfEngineService>()`.
2. **Secret Management** — WCF credentials and DB connection string hardcoded/in plain text. Should use Azure Key Vault, environment variables, or .NET User Secrets.
3. **Async DAO** — All DAO methods are synchronous (blocking thread pool threads). Should use `await cmd.ExecuteReaderAsync()`, `await da.FillAsync()`.
4. **Thread-safe Singletons** — `Import.Instance` and `DocumentsGenerationUtility.ObjInstance` are not thread-safe. Use `Lazy<T>` or `lock`.
5. **Unit Testing** — No unit tests exist. DAO classes use `new` and static Config — untestable without refactoring to interfaces and DI.

### Medium Priority
6. **IOptions<T>** — Static Config class prevents per-environment configuration changes without recompile. Should inject `IOptions<AppSettings>`.
7. **Polly Retry** — No retry logic for failed PDF generation HTTP calls. Add Polly policy with exponential backoff.
8. **ISP Violation** — IDocumentGenerate has 7 methods. Split into focused interfaces per invoice type.
9. **Large Class** — PDFDocumentsGenerationUtility.cs is 366KB — violates SRP. Should be split into per-invoice-type generators.
10. **Pagination** — Stored procedures return all invoices at once. Should add batch/pagination support for high-volume scenarios.

### Lower Priority
11. **Structured Logging** — NLog format uses string concatenation. Should use structured logging: `_logger.Info("Invoice {AssignmentID} generated", id)`.
12. **Health Checks** — No health check endpoint. Add `IHealthCheck` implementation for monitoring.
13. **Metrics** — No performance metrics. Add OpenTelemetry or Application Insights for throughput/latency tracking.
14. **Configuration Validation** — No startup validation of config values. Add `IValidateOptions<T>` or startup checks.
15. **Dead Letter Queue** — Failed invoices are only logged. Should save to a retry queue or dead-letter table in DB.

---

# REAL-TIME SCENARIO QUESTIONS

SCENARIO 1:
The PDF engine service at printengine.enago.com is down. What happens in the current project, and how would you improve it?

ANSWER:
Currently: PdfEngineService.GeneratePDF() throws an exception → logged by NLog → that invoice is skipped → other invoices continue. No retry, no alerting.
Improvement: Add Polly retry with exponential backoff (3 retries, 2s/4s/8s delays). After all retries fail, insert a "failed" record to a DB retry table. Add an alert notification (email/Slack) when failure rate exceeds threshold. Implement circuit breaker to stop hammering a clearly-down service.

---

SCENARIO 2:
The service is running but some invoices are not being generated. How would you debug this?

ANSWER:
1. Check NLog log files in `/Logs/{date}.log` for errors
2. Verify Config boolean flags — `Config.GenerateNormalInvoices`, etc. might be `false` in appsettings
3. Check if the stored procedure `CS_GetASNDetailsAfterInvoiceCheck` returns any rows for pending invoices
4. Verify `Config.RunAutomaticaly = true`
5. Check that `Config.GenerateMonthlyInvoicesDeliveryMailsAndCOE` flag matches the expected invoice type
6. Look for decryption failures in Crypter for specific assignments
7. Check external PDF service response — `result.status` might not be "SUCCESS"

---

SCENARIO 3:
You need to add support for generating invoices in Word format alongside PDF. How would you extend this project?

ANSWER:
1. Create `WordDocumentsGenerationUtility.cs` implementing `IDocumentGenerate`
2. In DocumentGenerateFactory.CreateDocumentObj(), register: `container.RegisterType<IDocumentGenerate, WordDocumentsGenerationUtility>("WORD")`
3. Add a new Config flag: `Config.GenerateWordInvoices`
4. In GenerateDocumentsService, call factory with `"WORD"` instead of `"PDF"` when the flag is set
5. No changes needed to Worker.cs, IDocumentGenerate interface, or DAO classes
This demonstrates the Open/Closed Principle — extension without modification.

---

SCENARIO 4:
The service is consuming too much memory after running for several hours. How would you investigate?

ANSWER:
Likely causes in this project:
1. `Import.Instance` is a singleton holding cached template labels in memory — check its size
2. `PDFDocumentsGenerationUtility` (366KB class) may hold large invoice lists in-memory between processing cycles
3. `new SqlConnection` objects not properly disposed — use `using` statements consistently
4. DataTable/DataSet objects not cleared after processing
5. NLog buffered targets not flushing

Investigation: Use dotnet-dump / Visual Studio diagnostic tools to take a memory snapshot. Look for growth in DataTable, Invoice[], and List<> collections. Add `GC.Collect()` calls at end of each Worker cycle (last resort). Better: ensure `IDisposable` resources use `using` blocks.

---

# HR + MANAGER ROUND QUESTIONS

Q: Can you walk me through the CSInvoice project?
A: CSInvoice is a .NET Core 6 Worker Service that automates invoice generation for an academic editing company (Enago/Ulatus). Every 2 minutes, it queries SQL Server for assignments that need invoices, retrieves client and payment data, decrypts sensitive fields, builds invoice data objects, and sends them to an external PDF engine service to generate PDF invoices. It handles multiple invoice types — normal assignment invoices, channel partner invoices, monthly organization invoices, advance payment invoices, and cancellations. The generated PDFs are emailed to clients.

Q: What was the most challenging part of working on this project?
A: (Your personal answer — suggested angle) Handling the complexity of multiple invoice types with different calculation rules (adjustments, debit/credit, channel partner commissions, monthly aggregation) while keeping the code maintainable. The InvoiceSendingDetailDTO with 100+ properties reflects the real-world complexity of billing across multiple currencies, locales, and tax regimes.

Q: How does this project scale?
A: Currently it's a single-process service. To scale: containerize with Docker, deploy multiple instances with DB-level locking on invoice rows being processed (to prevent duplicate generation), use Azure Service Bus or RabbitMQ for invoice job queuing, and move PDF generation to async background jobs. The current 2-minute polling could be replaced with event-driven triggers from the main application.

---

# QUICK REVISION NOTES

- Project type: .NET Core 6 Worker Service (BackgroundService, no HTTP endpoints)
- Entry: Program.cs → Host.CreateDefaultBuilder → Config (static) → Worker registered as IHostedService
- Main execution: Worker.ExecuteAsync() → Task.WhenAll(3 parallel tasks) → every 2 minutes
- Invoice flow: DAO → DataTable → TranslatorUtility (Reflection) → DTO → Import (Singleton) → Invoice → Factory → PDFDocumentsGenerationUtility → PdfEngineService (HTTP) → PDF
- Key patterns: Singleton (Import, DocumentsGenerationUtility), Factory (DocumentGenerateFactory + Unity), Strategy (IDocumentGenerate), DAO (8 classes), Translator (Reflection)
- DB: SQL Server, all SPs, SqlDataAdapter, CommandTimeout=600s, Crypter for encrypted columns
- Config: appsettings.json → static Config class → 8 boolean flags control which invoice types run
- Logging: NLog, daily rolling files, UDP viewer, `GetCurrentClassLogger()`
- External: HTTP POST to printengine.enago.com with JSON, Newtonsoft.Json
- No Angular/frontend, No JWT/OAuth, No Entity Framework, No AutoMapper
- Security gaps: hardcoded WCF credentials, no retry policy, non-async DAO, non-thread-safe singletons

---

# TOP 10 STRONGEST CONCEPTS IN THIS PROJECT

1. **Worker Service / Generic Host** — Clean BackgroundService implementation with CancellationToken and graceful shutdown
2. **Factory Pattern + Unity IoC** — DocumentGenerateFactory with interface-based resolution
3. **DAO Pattern** — Well-organized, consistent 8-class DAO layer using stored procedures
4. **Strategy Pattern** — IDocumentGenerate with multiple invoice processing strategies
5. **Singleton Pattern** — Import.Instance and DocumentsGenerationUtility.ObjInstance
6. **Parallel Task Execution** — Task.WhenAll for concurrent invoice type processing
7. **Stored Procedure Usage** — All DB calls via SPs with 600s timeout and proper parameter binding
8. **Cross-Platform Timezone Handling** — Windows/Linux timezone mapping with dedicated JSON config
9. **NLog Structured Logging** — Daily rolling files, archive policy, UDP viewer target
10. **Custom Translator (Reflection)** — Generic DataRow-to-DTO mapper without ORM dependency

---

# TOP 10 MISSING OR WEAK CONCEPTS

1. **HttpClientFactory** — Direct HttpClient instantiation risks socket exhaustion
2. **Async/Await in DAO** — Synchronous SqlClient calls block thread pool threads unnecessarily
3. **Thread-Safe Singletons** — Import.Instance and ObjInstance lack double-checked locking or Lazy<T>
4. **Secret Management** — WCF credentials hardcoded; connection string in plain text appsettings.json
5. **Unit Testing / Testability** — No tests; DAO/service coupling makes mocking impossible
6. **Retry / Resilience Policy (Polly)** — No retry on failed HTTP calls to PDF service
7. **ISP (Interface Segregation)** — IDocumentGenerate has 7 methods; should be split by invoice type
8. **Pagination on DB Queries** — All invoices fetched at once; no batch processing
9. **IOptions<T> Configuration** — Static Config class instead of injectable, validatable options
10. **Health Checks & Metrics** — No observability endpoint; no throughput/latency instrumentation

---
