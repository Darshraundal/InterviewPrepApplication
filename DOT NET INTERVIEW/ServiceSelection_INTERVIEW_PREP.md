# CMR-ServiceSelection — Complete Technical Interview Preparation Guide

> Project: Service Selection Page Revamp
> Stack: Angular 12 (Angular Elements / Web Component) + ASP.NET Core 6.0 + SQL Server
> Author: Darshan Raundal
> Level: 3–5 Years Experience

---

## PROJECT ARCHITECTURE SUMMARY

### What This Project Does
A multi-brand service selection portal component that allows users (customers of Enago/Ulatus/Voxtab/Publication Support) to view their assignment history and be routed to the correct service. It was originally a monolithic page and was revamped into a reusable Angular Web Component + .NET 6 REST API.

### Complete Architecture Flow

```
Browser / Host Portal
       │
       ▼
<service-selection> Web Component (Angular Element)
   [service-selection-element.js + service-selection-styles.css]
       │
       ├── Reads DOM attributes (ClientUserName, WebsiteID, ICCode, etc.)
       │
       ├── TokenApiService
       │     └── POST → https://securitytoken.enago.com/SecurityToken/tokengenerator
       │           └── Stores JWT in sessionStorage
       │
       └── AssignmentDataService
             └── GET → /serviceselection/v1/AssignmentData/GetAssignmentDataforServiceSelection
                   └── Header: Authorization: Bearer {JWT}
                         │
                         ▼
                   ASP.NET Core 6.0 API (ServiceSelectionApi)
                         │
                         ├── JWT Middleware validates token
                         ├── AssignmentDataController
                         │     ├── IAssignmentDataContract.GetAssignmentData()
                         │     │     └── Dapper → SP: MP_GetASNdataForServiceSelectionApi
                         │     └── ISubdomainRedirectEnabler.GetBrandUrlbyBrandIds()
                         │           └── Dapper → SP: MP_SP_GetConfigServiceBrandwiseData
                         │
                         └── Returns JSON: { asndata[], brandUrl[] }
                               │
                               ▼
                   Frontend sorts cards, renders with i18n text
                   User clicks "Order Now" → Opens brand URL in new tab
```

### Authentication Flow
1. Angular calls external SecurityToken API with base64-encoded credentials
2. Receives JWT (HS256 signed)
3. Stores in sessionStorage with expiry timestamp
4. `TokenInterceptor` attaches `Authorization: Bearer {token}` to every outgoing HTTP call
5. ASP.NET Core JWT middleware validates token signature and expiry
6. If valid → controller executes; if expired → 401 returned, frontend re-fetches token

### Frontend Rendering Flow
1. Component initializes → reads DOM attributes
2. Sets language via RxTranslation (based on `Languageid`)
3. Fetches JWT → fetches assignment data
4. Sorts brands: primary by `ASNBrandCount` (desc), secondary by `ASNCreatedOn` (desc)
5. Formats dates using moment.js + CultureCode
6. Renders brand cards (Enago, Ulatus, Voxtab, Publication Support)

---

# .NET / ASP.NET CORE SECTION

---

## MVC Architecture

---

**QUESTION:**
Does your project follow MVC architecture? How is it structured?

**ANSWER:**
This project follows a **Web API architecture** which is the API-only variant of MVC — no Views layer. The pattern is:
- **Model** → Classes in the `Models/` folder (`AssignmentDataModel.cs`, `SubdomianRedirectModel.cs`)
- **Controller** → `AssignmentDataController.cs` handles HTTP routing
- **No View** → Frontend (Angular) acts as the View layer, completely decoupled

**PROJECT EXAMPLE:**
- File: `Controllers/AssignmentDataController.cs`
- Class: `AssignmentDataController`
- Method: `GetAssignmentDataforServiceSelection()`
- The controller receives the request, delegates to repository, and returns JSON response — it contains zero business logic itself.

```csharp
[Route("serviceselection/v{version:apiVersion}/[controller]")]
[ApiController]
[Authorize]
public class AssignmentDataController : ControllerBase
{
    private readonly IAssignmentDataContract _assignmentData;
    private readonly ISubdomainRedirectEnabler _subdomainRedirect;

    public AssignmentDataController(IAssignmentDataContract assignmentData,
                                    ISubdomainRedirectEnabler subdomainRedirect)
    { ... }
}
```

**FOLLOW-UP QUESTIONS:**
1. What is the difference between MVC and Web API in .NET?
2. Why did you choose Web API over a full MVC project?
3. What is `ControllerBase` vs `Controller`?

**IMPORTANT FOR INTERVIEW:**
`ControllerBase` is used in APIs (no View support). `Controller` inherits from `ControllerBase` and adds View-related methods like `View()`, `Json()`. In API-only projects, always use `ControllerBase`.

---

## Dependency Injection

---

**QUESTION:**
How is Dependency Injection implemented in your project?

**ANSWER:**
DI is implemented using ASP.NET Core's built-in IoC container registered in `Startup.cs`. Interfaces are registered against their concrete implementations so that controllers and other classes never instantiate dependencies directly.

**PROJECT EXAMPLE:**
- File: `Startup.cs`
- Registration:
```csharp
services.AddTransient<IAssignmentDataContract, AssignmentDataRepository>();
services.AddTransient<ISubdomainRedirectEnabler, SubdomainRedirectRepository>();
```
- File: `Controllers/AssignmentDataController.cs`
- Constructor injection:
```csharp
public AssignmentDataController(IAssignmentDataContract assignmentData,
                                ISubdomainRedirectEnabler subdomainRedirect)
{
    _assignmentData = assignmentData;
    _subdomainRedirect = subdomainRedirect;
}
```

The controller does not know it is using `AssignmentDataRepository` — it only knows the `IAssignmentDataContract` interface. This is the core of DI.

**FOLLOW-UP QUESTIONS:**
1. What are the three service lifetimes in ASP.NET Core?
2. Why is `AddTransient` used here instead of `AddSingleton`?
3. What happens if you inject a Transient service into a Singleton?

**IMPORTANT FOR INTERVIEW:**
- `AddTransient` → new instance every time injected (used here because DB connections should not be shared)
- `AddScoped` → one instance per HTTP request
- `AddSingleton` → one instance for entire app lifetime
- Never inject Scoped/Transient services into a Singleton — causes "captive dependency" bug

---

## Service Lifetimes

---

**QUESTION:**
Which service lifetime is used in your project and why?

**ANSWER:**
`AddTransient` is used for both `AssignmentDataRepository` and `SubdomainRedirectRepository`. This is the correct choice because:
- Each HTTP request should get a fresh repository instance
- Database connections (via Dapper) are opened and closed per operation
- No shared mutable state between requests

**PROJECT EXAMPLE:**
- File: `Startup.cs`
```csharp
services.AddTransient<IAssignmentDataContract, AssignmentDataRepository>();
services.AddTransient<ISubdomainRedirectEnabler, SubdomainRedirectRepository>();
```

**FOLLOW-UP QUESTIONS:**
1. When would you use `AddScoped` for a repository?
2. What is a memory leak risk with `AddSingleton`?
3. Can two classes share a Transient instance in the same request?

**IMPORTANT FOR INTERVIEW:**
If using Entity Framework's `DbContext`, the correct lifetime is `AddScoped` (one context per request). Since this project uses Dapper with raw SqlConnection, `AddTransient` is fine because connections are manually opened/closed per query.

---

## JWT Authentication & Authorization

---

**QUESTION:**
How is JWT authentication implemented in your project?

**ANSWER:**
The project uses JWT Bearer authentication with HS256 (HMAC SHA256) algorithm.

**Configuration** (`Startup.cs`):
```csharp
services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(Configuration["JWT:JWTAuthenticationKey"])),
            ValidateIssuer = false,
            ValidateAudience = false
        };
    });
```

**Secret key** (`appsettings.json`):
```json
"JWT": { "JWTAuthenticationKey": "95ba7edefb308827e28625d41bcc215c17cfee75e0605c1865d6240a8612c693" }
```

**Controller** (`AssignmentDataController.cs`):
```csharp
[Authorize]
public class AssignmentDataController : ControllerBase { ... }
```

The token is generated externally by `https://securitytoken.enago.com/SecurityToken/tokengenerator` and validated here.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Authentication and Authorization?
2. Why is `ValidateIssuer = false` risky in production?
3. What is the structure of a JWT token?

**IMPORTANT FOR INTERVIEW:**
JWT has 3 parts: `Header.Payload.Signature`
- Header: algorithm type (HS256)
- Payload: claims (userId, expiry, roles)
- Signature: HMAC(header + payload + secret)

Setting `ValidateIssuer = false` and `ValidateAudience = false` is a security shortcut acceptable for internal microservices but not ideal for public APIs. A best practice is to always validate issuer and audience.

---

## API Versioning

---

**QUESTION:**
How is API versioning implemented in your project?

**ANSWER:**
API versioning is implemented using the `Microsoft.AspNetCore.Mvc.Versioning` NuGet package. Version is passed in the route URL.

**Configuration** (`Startup.cs`):
```csharp
services.AddApiVersioning(config => {
    config.DefaultApiVersion = new ApiVersion(1, 0);
    config.AssumeDefaultVersionWhenUnspecified = true;
});
```

**Controller Route**:
```csharp
[Route("serviceselection/v{version:apiVersion}/AssignmentData")]
```

So the endpoint is: `/serviceselection/v1/AssignmentData/GetAssignmentDataforServiceSelection`

If a v2 is needed in future, a new controller with `[ApiVersion("2.0")]` can be added without breaking existing v1 consumers.

**FOLLOW-UP QUESTIONS:**
1. What are the three ways to pass API version (URL, header, query string)?
2. How do you deprecate an old API version?
3. What happens if a client calls without a version number?

**IMPORTANT FOR INTERVIEW:**
URL versioning is the most visible and cacheable approach. Header versioning is cleaner (doesn't pollute URLs) but harder to test in browsers. Query string (`?api-version=1.0`) is the simplest but looks ugly.

---

## Repository Pattern

---

**QUESTION:**
How is the Repository Pattern implemented in your project?

**ANSWER:**
The project uses a classic Repository Pattern with interface-based abstraction:
- **Interface** (Contract) defines the method signatures
- **Repository** (Concrete class) implements the actual database logic
- **Controller** depends only on the interface, not the concrete class

**PROJECT EXAMPLE:**
- File: `Contracts/IAssignmentDataContract.cs`
```csharp
public interface IAssignmentDataContract {
    Task<List<AssignmentData>> GetAssignmentData(ClientRequest request);
}
```
- File: `Repositories/AssignmentDataRepository.cs`
```csharp
public class AssignmentDataRepository : IAssignmentDataContract {
    public async Task<List<AssignmentData>> GetAssignmentData(ClientRequest request) {
        // Dapper DB call here
    }
}
```
- File: `Controllers/AssignmentDataController.cs` — uses only `IAssignmentDataContract`, never `AssignmentDataRepository` directly.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Repository Pattern and a plain service class?
2. How does this pattern help in unit testing?
3. What is the Unit of Work pattern and does your project use it?

**IMPORTANT FOR INTERVIEW:**
The Repository Pattern's biggest benefit is testability — you can mock `IAssignmentDataContract` in unit tests without hitting a real database. This project does not implement Unit of Work because there's only one write operation path, but in enterprise apps with multiple repositories, Unit of Work coordinates transactions across them.

---

## SOLID Principles

---

**QUESTION:**
Which SOLID principles are applied in your project?

**ANSWER:**

**S — Single Responsibility Principle:**
- `AssignmentDataController` → only handles HTTP routing
- `AssignmentDataRepository` → only talks to DB
- `SubdomainRedirectRepository` → only resolves brand URLs
- `TokenApiService` (Frontend) → only manages JWT lifecycle
Each class has exactly one reason to change.

**O — Open/Closed Principle:**
- `IAssignmentDataContract` and `ISubdomainRedirectEnabler` interfaces allow new implementations without modifying existing code. Add a new database strategy? Implement the interface, register it — existing controller unchanged.

**D — Dependency Inversion Principle:**
- `AssignmentDataController` depends on abstractions (`IAssignmentDataContract`) not concrete classes (`AssignmentDataRepository`).

**L — Liskov Substitution Principle:**
- `AssignmentDataRepository` can be substituted anywhere `IAssignmentDataContract` is expected.

**I — Interface Segregation:**
- Partially applied. `IAssignmentDataContract` only has assignment-related methods. `ISubdomainRedirectEnabler` handles URL resolution separately. They are not merged into one large interface.

**FOLLOW-UP QUESTIONS:**
1. Give a real example where Open/Closed Principle saved you from regression?
2. What violation does injecting `AssignmentDataRepository` directly into the controller cause?
3. How would you add a caching layer without changing the controller?

**IMPORTANT FOR INTERVIEW:**
The answer to Q3 is the Decorator Pattern — create a `CachedAssignmentDataRepository` that wraps `AssignmentDataRepository`, checks cache first, then falls back to DB. Register it as the implementation of `IAssignmentDataContract`. Controller never changes.

---

## OOP Concepts

---

**QUESTION:**
Which OOP concepts are used in this project?

**ANSWER:**

**Encapsulation:**
`AssignmentData` model uses `init`-only properties — data is set at object creation and cannot be mutated externally.
```csharp
public class AssignmentData {
    public int BrandId { get; init; }
    public int ASNCount { get; init; }
    public string LastestASN { get; init; }
}
```

**Abstraction:**
`IAssignmentDataContract` and `ISubdomainRedirectEnabler` interfaces hide all SQL and business logic from the controller.

**Polymorphism (Interface Polymorphism):**
The controller accepts `IAssignmentDataContract` — any class implementing this interface can be swapped in at runtime via DI.

**Inheritance:**
`AssignmentDataController : ControllerBase` — inherits HTTP handling capabilities from the base class.

**Enum (Type Safety as OOP feature):**
```csharp
public enum enumServiceWorkFlowType {
    enago = 1, ulatus = 2, voxtab = 3, PS = 4
}
```
Eliminates magic numbers in brand logic.

**FOLLOW-UP QUESTIONS:**
1. Why use `init` instead of `set` in the model?
2. What is the difference between interface and abstract class here?
3. Why is polymorphism important in the Repository Pattern?

**IMPORTANT FOR INTERVIEW:**
`init` (C# 9+) creates immutable-after-construction objects. This is important for DTOs/models where you don't want data to be accidentally changed after deserialization. It's thread-safe by nature.

---

## Interface vs Abstract Class

---

**QUESTION:**
Did you use interfaces or abstract classes? Why?

**ANSWER:**
This project uses **interfaces** (`IAssignmentDataContract`, `ISubdomainRedirectEnabler`), not abstract classes. The reason is:

- **Interfaces** are used when you want to define a contract without imposing any implementation. Multiple classes can implement the same interface regardless of inheritance hierarchy.
- **Abstract classes** are used when you want to share common implementation code across related classes.

Since `AssignmentDataRepository` and `SubdomainRedirectRepository` have no shared base behavior, interfaces are the right choice. They also support DI registration cleanly.

**FOLLOW-UP QUESTIONS:**
1. When would you choose abstract class over interface in a .NET project?
2. Can a C# class implement multiple interfaces? Multiple abstract classes?
3. From C# 8.0, what new feature was added to interfaces?

**IMPORTANT FOR INTERVIEW:**
C# 8.0 added **default interface methods** — interfaces can now have implementation. This is useful for adding methods to interfaces without breaking existing implementors. However, most enterprise code still keeps interfaces as pure contracts.

---

## Dapper (Data Access) — No Entity Framework

---

**QUESTION:**
Why did you use Dapper instead of Entity Framework? How is it implemented?

**ANSWER:**
Dapper is a **micro-ORM** — it maps SQL results to C# objects without the overhead of EF's change tracking, lazy loading, and migration system. This project uses stored procedures in SQL Server, so Dapper is the ideal choice.

**Implementation** (`AssignmentDataRepository.cs`):
```csharp
using (SqlConnection conn = new SqlConnection(_connectionString)) {
    var result = await conn.QueryAsync<AssignmentData>(
        "MP_GetASNdataForServiceSelectionApi",
        new { UserName = request.ClientUserName, WebsiteID = request.WebsiteID },
        commandType: CommandType.StoredProcedure
    );
    return result.ToList();
}
```

**Why Dapper over EF here:**
1. Stored procedures already exist — EF doesn't benefit you much over existing SPs
2. Dapper is ~10x faster than EF for read-heavy workloads
3. No migration complexity needed — DB schema managed separately
4. Full SQL control for complex queries

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Dapper and Entity Framework Core?
2. What does `IEnumerable` vs `IQueryable` mean in the context of Dapper?
3. How do you handle transactions in Dapper?

**IMPORTANT FOR INTERVIEW:**
With Dapper you get `IEnumerable` — all filtering happens in-memory after data is fetched. With EF you get `IQueryable` — LINQ expressions are translated to SQL and filtering happens in the database. For this project with SPs, `IEnumerable` is fine since SPs handle filtering.

---

## IQueryable vs IEnumerable

---

**QUESTION:**
Does your project use IQueryable or IEnumerable?

**ANSWER:**
Since this project uses **Dapper**, all data access returns `IEnumerable<T>` (or `List<T>`). There is no `IQueryable` usage.

- `IEnumerable<T>` → data is fetched from DB, LINQ filters run **in memory**
- `IQueryable<T>` → filters are translated to SQL and run **in the database** (EF Core feature)

In `AssignmentDataRepository.cs`, `conn.QueryAsync<AssignmentData>()` returns `IEnumerable<AssignmentData>`. This is fine here because the stored procedure already handles all filtering at the database level.

**FOLLOW-UP QUESTIONS:**
1. When does using IEnumerable over IQueryable cause a performance problem?
2. How would you add IQueryable if you switched to EF Core?
3. What is deferred execution in LINQ?

**IMPORTANT FOR INTERVIEW:**
IQueryable deferred execution means the SQL isn't sent until you call `.ToList()`, `.FirstOrDefault()`, etc. Multiple `.Where()` calls on `IQueryable` chain into one SQL statement. With `IEnumerable`, every `.Where()` filters an already-loaded collection in memory.

---

## CORS Configuration

---

**QUESTION:**
How is CORS configured in your project?

**ANSWER:**
CORS is configured in `Startup.cs` with a permissive policy — allowing any origin, method, and header. This is because the Angular Web Component is embedded in multiple different portals (different domains).

```csharp
services.AddCors(options => {
    options.AddPolicy("CorsPolicy", builder =>
        builder.AllowAnyMethod()
               .AllowAnyHeader()
               .AllowAnyOrigin());
});

app.UseCors("CorsPolicy");
```

**Why `AllowAnyOrigin`:** The component is deployed on Enago.com, Ulatus.com, Voxtab.com portals — all different domains. Restricting by origin would break all consumers.

**FOLLOW-UP QUESTIONS:**
1. What security risk does `AllowAnyOrigin` introduce?
2. Can you use `AllowAnyOrigin` with `AllowCredentials`?
3. What are the CORS preflight requests (OPTIONS)?

**IMPORTANT FOR INTERVIEW:**
`AllowAnyOrigin` + `AllowCredentials()` is explicitly forbidden by the CORS spec and .NET will throw an exception. If you need credentials with CORS, you must specify exact origins. For this project, since JWT is used (not cookies), `AllowAnyOrigin` is acceptable but ideally should be restricted to known portal domains.

---

## Routing

---

**QUESTION:**
How is routing configured in your project?

**ANSWER:**
Attribute routing is used with API versioning embedded in the route template.

```csharp
[Route("serviceselection/v{version:apiVersion}/[controller]")]
[ApiController]
public class AssignmentDataController : ControllerBase
{
    [HttpGet("GetAssignmentDataforServiceSelection")]
    public async Task<IActionResult> GetAssignmentDataforServiceSelection(
        [FromQuery] string ClientUserName,
        [FromQuery] int WebsiteID, ...)
    { ... }
}
```

Full URL: `GET /serviceselection/v1/AssignmentData/GetAssignmentDataforServiceSelection?ClientUserName=...`

**FOLLOW-UP QUESTIONS:**
1. What is the difference between attribute routing and conventional routing?
2. What does `[FromQuery]` vs `[FromBody]` vs `[FromRoute]` mean?
3. How does `[ApiController]` attribute affect routing?

**IMPORTANT FOR INTERVIEW:**
`[ApiController]` automatically enables:
1. Attribute routing requirement
2. Automatic 400 response for invalid ModelState
3. Binding source inference (`[FromBody]` for complex types, `[FromQuery]` for primitives)
4. Problem details responses

---

## Configuration Management

---

**QUESTION:**
How do you manage configuration across multiple environments?

**ANSWER:**
The project uses ASP.NET Core's built-in configuration system with environment-specific `appsettings` files.

**Files present:**
- `appsettings.json` — base config
- `appsettings.Development.json`
- `appsettings.prod.json`
- `appsettings.preprod.json`
- `appsettings.stage1.json`, `appsettings.stage2.json`
- `appsettings.uat1.json`, `appsettings.uat3.json`, `appsettings.uat5.json`, `appsettings.uat6.json`, `appsettings.uat11.json`

**Loading in `Program.cs`:**
```csharp
// ASP.NET Core automatically loads appsettings.{ASPNETCORE_ENVIRONMENT}.json
// over the base appsettings.json
```

**Accessing config:**
```csharp
Configuration["JWT:JWTAuthenticationKey"]
Configuration["Settings:ConnectionString"]
```

**FOLLOW-UP QUESTIONS:**
1. What is the configuration override order in ASP.NET Core?
2. How do you protect secrets in production (avoid hardcoding in appsettings)?
3. What is the Options pattern?

**IMPORTANT FOR INTERVIEW:**
Configuration override priority (lowest to highest):
1. `appsettings.json`
2. `appsettings.{Environment}.json`
3. Environment variables
4. Command-line arguments

Hardcoding secrets in `appsettings.json` (as done in this project) is a security risk. Production best practice is Azure Key Vault, AWS Secrets Manager, or environment variables injected at runtime.

---

## Logging with Serilog & Elasticsearch

---

**QUESTION:**
How is logging implemented in your project?

**ANSWER:**
The project uses **Serilog** as the structured logging framework, with **Elasticsearch** as the log sink for centralized log aggregation.

**Configuration in `Program.cs`:**
```csharp
Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri(elasticUri)) {
        IndexFormat = "serviceselection-log-{0:yyyy.MM.dd}",
        TemplateName = "serviceselection-log",
        ModifyConnectionSettings = x =>
            x.BasicAuthentication(username, password)
    })
    .CreateLogger();
```

**Why Serilog + Elasticsearch:**
- Serilog supports structured logging (key-value pairs, not just strings)
- Elasticsearch + Kibana enables searching, dashboards, alerting across distributed services
- Index per day (`serviceselection-log-2024.01.15`) enables efficient time-range queries
- NLog is also configured (`nlog.config`) as an additional logger

**FOLLOW-UP QUESTIONS:**
1. What is the difference between structured logging and text logging?
2. What log levels does Serilog support?
3. How would you add correlation IDs to trace requests across microservices?

**IMPORTANT FOR INTERVIEW:**
Structured logging means logging objects, not strings: `Log.Information("Fetched {Count} assignments for {User}", count, username)`. This allows querying Elasticsearch for "show all logs where User=john" instead of text searching. This is a fundamental difference from `Console.WriteLine("Fetched " + count + " assignments")`.

---

## Startup.cs / Program.cs

---

**QUESTION:**
Explain the role of Program.cs and Startup.cs in your project.

**ANSWER:**

**Program.cs** (entry point):
- Configures Serilog before host builds
- Builds the web host using `CreateHostBuilder`
- Wraps in try/catch to log startup failures

**Startup.cs** (configuration):
- `ConfigureServices()` → registers all DI services (repositories, auth, CORS, Swagger, API versioning, health checks)
- `Configure()` → builds the HTTP middleware pipeline

**Middleware pipeline order** (`Configure()`):
```csharp
app.UseRouting();
app.UseCors("CorsPolicy");
app.UseAuthentication();   // Must come before Authorization
app.UseAuthorization();
app.UseEndpoints(endpoints => {
    endpoints.MapControllers();
    endpoints.MapHealthChecks("/health");
});
```

**FOLLOW-UP QUESTIONS:**
1. Why must `UseAuthentication()` come before `UseAuthorization()`?
2. What happens if you call `UseRouting()` after `UseAuthorization()`?
3. In .NET 6, is Startup.cs still required?

**IMPORTANT FOR INTERVIEW:**
In .NET 6 minimal hosting model, `Startup.cs` is merged into `Program.cs`. This project still uses the traditional Startup class which is perfectly valid. `UseAuthentication()` must come before `UseAuthorization()` because auth middleware sets the `ClaimsPrincipal` (identity) that authorization middleware reads.

---

## DTOs (Data Transfer Objects)

---

**QUESTION:**
How are DTOs used in your project?

**ANSWER:**
The project uses separate model classes as DTOs to transfer data between layers.

**File: `Models/AssignmentDataModel.cs`:**
```csharp
// Request DTO
public class ClientRequest {
    public string ClientUserName { get; init; }
    public int WebsiteID { get; init; }
    public string ICCode { get; init; }
    public string EmailAddress { get; set; }
    public string MembershipID { get; set; }
}

// Response DTO
public class ClientResponse {
    public List<AssignmentData> asndata { get; set; }
    public List<BrandUrl> brandUrl { get; set; }
}

// Data DTO
public class AssignmentData {
    public int BrandId { get; init; }
    public int ASNCount { get; init; }
    public string LastestASN { get; init; }
    public string AttributeValue { get; init; }
    public string ASNBrandIds { get; set; }
}
```

**Note on AutoMapper:** This project does NOT use AutoMapper. Since Dapper directly maps to `AssignmentData` objects and the models are simple, manual mapping is sufficient. AutoMapper would add unnecessary complexity here.

**FOLLOW-UP QUESTIONS:**
1. Why use DTOs instead of returning entity/domain objects directly?
2. What is the difference between DTO and ViewModel?
3. When should you use AutoMapper?

**IMPORTANT FOR INTERVIEW:**
DTOs prevent over-posting attacks (user sending extra fields) and over-fetching (returning sensitive DB columns to clients). They decouple the API contract from the database schema — you can change the DB without breaking the API consumers.

---

## async/await

---

**QUESTION:**
How is async/await used in your project?

**ANSWER:**
The project uses async/await throughout the data access layer to avoid blocking threads during database I/O.

**Controller:**
```csharp
[HttpGet("GetAssignmentDataforServiceSelection")]
public async Task<IActionResult> GetAssignmentDataforServiceSelection(...)
{
    var asndata = await _assignmentData.GetAssignmentData(request);
    var brandUrls = await _subdomainRedirect.GetBrandUrlbyBrandIds(...);
    return Ok(new List<ClientResponse> { new ClientResponse { asndata = ..., brandUrl = ... } });
}
```

**Repository:**
```csharp
public async Task<List<AssignmentData>> GetAssignmentData(ClientRequest request)
{
    using (SqlConnection conn = new SqlConnection(_connectionString))
    {
        var result = await conn.QueryAsync<AssignmentData>(...);
        return result.ToList();
    }
}
```

**Why async:** SQL queries are I/O-bound operations. Using async frees the thread to serve other requests while waiting for DB response, improving throughput under load.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Task and Thread?
2. What happens if you call `.Result` on a Task instead of `await`?
3. What is `ConfigureAwait(false)` and should you use it here?

**IMPORTANT FOR INTERVIEW:**
Calling `.Result` or `.Wait()` on a Task in ASP.NET Core can cause **deadlocks** — the async context is blocked waiting for a task that's waiting for the context. Always use `await`. `ConfigureAwait(false)` is a library-level optimization that avoids capturing the synchronization context — use it in library code, not in ASP.NET controller code.

---

## Exception Handling

---

**QUESTION:**
How is exception handling done in your project?

**ANSWER:**
This project does NOT implement global exception handling middleware. Exception handling is done locally within try/catch blocks in repositories where DB connections are made.

**What ideally should be implemented:**
A global exception handling middleware or `UseExceptionHandler` that:
1. Catches all unhandled exceptions
2. Logs them via Serilog
3. Returns a consistent error response (ProblemDetails format)

```csharp
// MISSING in this project — recommended implementation:
app.UseExceptionHandler(appError => {
    appError.Run(async context => {
        context.Response.StatusCode = 500;
        context.Response.ContentType = "application/json";
        var error = context.Features.Get<IExceptionHandlerFeature>();
        Log.Error(error?.Error, "Unhandled exception");
        await context.Response.WriteAsync(JsonSerializer.Serialize(new {
            StatusCode = 500,
            Message = "Internal Server Error"
        }));
    });
});
```

**FOLLOW-UP QUESTIONS:**
1. What is the difference between try/catch in controller vs global exception middleware?
2. What is ProblemDetails in ASP.NET Core?
3. How would you handle different exception types differently (e.g., ValidationException vs DatabaseException)?

**IMPORTANT FOR INTERVIEW:**
Global exception handling ensures consistent error responses and centralized logging. Without it, unhandled exceptions may expose stack traces to clients (security risk) or be swallowed silently (debugging nightmare).

---

## Health Checks

---

**QUESTION:**
Does your project implement health checks?

**ANSWER:**
Yes. A basic health check endpoint is configured.

**`Startup.cs`:**
```csharp
services.AddHealthChecks();

app.UseEndpoints(endpoints => {
    endpoints.MapControllers();
    endpoints.MapHealthChecks("/health");
});
```

Calling `GET /health` returns `200 OK` with `"Healthy"` if the service is running. This is used by load balancers, container orchestrators (Kubernetes), and monitoring tools to verify the service is alive.

**FOLLOW-UP QUESTIONS:**
1. How would you add a database health check?
2. What is the difference between liveness and readiness probes in Kubernetes?
3. How do you add custom health check logic?

**IMPORTANT FOR INTERVIEW:**
A proper health check should also verify DB connectivity: `services.AddHealthChecks().AddSqlServer(connectionString)`. This project only checks app-level health (process alive), not dependency health (DB reachable).

---

## Swagger / OpenAPI

---

**QUESTION:**
How is Swagger configured in your project?

**ANSWER:**
Swagger is configured using `Swashbuckle.AspNetCore` with JWT security support.

**`Startup.cs`:**
```csharp
services.AddSwaggerGen(c => {
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "ServiceSelectionApi", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme {
        Description = "JWT Authorization header using the Bearer scheme",
        Type = SecuritySchemeType.Http,
        Scheme = "bearer"
    });
    c.AddSecurityRequirement(new OpenApiSecurityRequirement { ... });
});

app.UseSwagger();
app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "ServiceSelectionApi v1"));
```

This allows testing JWT-protected endpoints directly from Swagger UI by pasting the Bearer token.

**FOLLOW-UP QUESTIONS:**
1. Should Swagger be enabled in production?
2. How do you version Swagger documentation?
3. What is the difference between Swagger and OpenAPI?

**IMPORTANT FOR INTERVIEW:**
OpenAPI is the specification standard. Swagger is the toolset (Swashbuckle implements OpenAPI). Swagger UI should be disabled in production to avoid exposing API documentation to attackers. Typically done with `if (env.IsDevelopment()) { app.UseSwaggerUI(...); }`.

---

## Docker / Containerization

---

**QUESTION:**
Is your project containerized? How?

**ANSWER:**
Yes. The project has a `Dockerfile` for containerization.

**Backend `Dockerfile` approach:**
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 14004

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "ServiceSelectionApi.dll"]
```

**Run commands:**
```bash
docker build -t dockimg-editprofile-v1 .
docker run -d -p 14004:14004 --name cont-editprofile-v1 dockimg-editprofile-v1
```

**FOLLOW-UP QUESTIONS:**
1. What is a multi-stage Docker build and why is it used here?
2. What is the difference between `EXPOSE` and `-p` in Docker?
3. How do you pass environment variables to a Docker container?

**IMPORTANT FOR INTERVIEW:**
Multi-stage builds keep the final image small — the SDK image (~700MB) is only used for building. The final image uses the runtime-only image (~200MB). Environment variables are passed via `-e ASPNETCORE_ENVIRONMENT=Production` or `--env-file .env` at `docker run` time.

---

---

# ANGULAR SECTION

---

## Angular Architecture — Angular Elements (Web Component)

---

**QUESTION:**
What is the Angular architecture used in this project? What is an Angular Element?

**ANSWER:**
This project uses **Angular Elements** — a feature that packages an Angular component as a standard **Web Component** (Custom HTML Element). Instead of running as a full Angular SPA, it compiles to a self-contained JavaScript bundle that can be dropped into any webpage.

**`app.module.ts`:**
```typescript
import { createCustomElement } from '@angular/elements';

@NgModule({
  declarations: [AppComponent, ServiceSelectionComponent, ...],
  imports: [BrowserModule, HttpClientModule, ...],
  bootstrap: []   // No bootstrap component — using entryComponents
})
export class AppModule {
  constructor(private injector: Injector) {
    const el = createCustomElement(ServiceSelectionComponent, { injector });
    customElements.define('service-selection', el);  // Registers as <service-selection>
  }
  ngDoBootstrap() {}
}
```

**Output:**
Single file `service-selection-element.js` — host page only needs:
```html
<script src="service-selection-element.js"></script>
<service-selection ClientUserName="..." WebsiteID="1"></service-selection>
```

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Angular SPA and Angular Element?
2. How does `createCustomElement` work internally?
3. How do you pass data into and out of an Angular Element?

**IMPORTANT FOR INTERVIEW:**
Angular Elements solve the problem of embedding Angular in non-Angular pages (React portals, plain HTML, WordPress, etc.). Input attributes map to Angular `@Input()`. Output events map to custom DOM events. The entire Angular runtime is bundled in — this is why the JS file is ~1MB.

---

## Components

---

**QUESTION:**
Explain the component architecture of your project.

**ANSWER:**
Three components are present:

**1. ServiceSelectionComponent** (`service-selection.component.ts`):
- The **root Web Component** registered as `<service-selection>`
- Reads native element attributes from the DOM using `ElementRef`
- Passes data to the dialog component via `@Input()` bindings
- Thin layer — no business logic

**2. ServiceSelectionDialogComponent** (`service-selection-dialog.component.ts`):
- The **main business component**
- Receives inputs from parent
- Calls `getasndata()` to fetch and sort assignment data
- Handles date formatting, language, card rendering
- Contains `btnContinuclick()` for navigation

**3. LoaderComponent** (`loader.component.ts`):
- Simple UI component showing a loading spinner
- Controlled by `LoaderService` (shown/hidden via BehaviorSubject)

**FOLLOW-UP QUESTIONS:**
1. What lifecycle hook is used for initialization in your components?
2. How does the parent component pass data to the dialog component?
3. What is `ElementRef` and when should you avoid it?

**IMPORTANT FOR INTERVIEW:**
`ElementRef` gives direct access to the native DOM element — used here to read custom HTML attributes. Overuse of `ElementRef` breaks Angular's abstraction (testability, SSR). It's acceptable here because reading host element attributes is a valid Angular Elements use case.

---

## Angular Modules

---

**QUESTION:**
How are Angular modules structured in your project?

**ANSWER:**
The project has a **single module** architecture — `AppModule` — which is appropriate for a Web Component that gets bundled into a single JS file. There is no lazy loading since routing is not used.

**`app.module.ts` imports:**
- `BrowserModule` — for browser DOM support
- `HttpClientModule` — for HTTP calls
- `BrowserAnimationsModule` — for Angular Material animations
- `MatDialogModule` — for Angular Material dialog
- `RxTranslationModule` — for i18n
- `LoggerModule` — for ngx-logger

All components are declared in this single module. There are no feature modules or shared modules since the scope of the application is small and focused.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `BrowserModule` and `CommonModule`?
2. Why can't you import `BrowserModule` twice?
3. When would you create a SharedModule?

**IMPORTANT FOR INTERVIEW:**
`BrowserModule` should only be imported in the root `AppModule`. Feature/shared modules should import `CommonModule` (which is a subset of `BrowserModule`). Importing `BrowserModule` in multiple places throws a runtime error.

---

## Angular Services & Dependency Injection

---

**QUESTION:**
How are services and DI implemented in the Angular part of your project?

**ANSWER:**
Angular services use `@Injectable({ providedIn: 'root' })` for singleton registration at application level.

**Services present:**
- `AssignmentDataService` → Calls backend API, returns `Observable<AssignmentResponseData[]>`
- `TokenApiService` → Fetches JWT, manages sessionStorage, checks expiry
- `LoaderService` → Controls loader visibility via `BehaviorSubject<boolean>`
- `LoggerService` → Wraps NGXLogger for structured client-side logging

**Example (`assignment-data-service.service.ts`):**
```typescript
@Injectable({ providedIn: 'root' })
export class AssignmentDataService {
  constructor(private http: HttpClient) {}

  GetAssignmentdata(params: ...): Observable<AssignmentResponseData[]> {
    return this.http.get<AssignmentResponseData[]>(url, { params });
  }
}
```

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `providedIn: 'root'` and declaring in `providers[]` array?
2. How is LoaderService shared between components without @Input/@Output?
3. What is a BehaviorSubject and why is it used in LoaderService?

**IMPORTANT FOR INTERVIEW:**
`providedIn: 'root'` is tree-shakable — if the service is never injected, it's removed from the bundle. Declaring in `providers[]` always includes it. `BehaviorSubject` is used in `LoaderService` because it emits the **current value** immediately to new subscribers — perfect for UI state that components need to read when they initialize.

---

## HTTP Interceptors

---

**QUESTION:**
How is the HTTP Interceptor implemented in your project?

**ANSWER:**
`TokenInterceptor` (`helpers/token.interceptor.ts`) automatically attaches the JWT Bearer token to every outgoing HTTP request.

**Implementation:**
```typescript
@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  constructor(private tokenService: TokenApiService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip token injection for the token generation call itself
    if (request.url.includes('tokengenerator')) {
      return next.handle(request);
    }

    const token = sessionStorage.getItem('jwtToken');
    if (token) {
      request = request.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
    }
    return next.handle(request);
  }
}
```

**Registered in `app.module.ts`:**
```typescript
providers: [
  { provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true }
]
```

**FOLLOW-UP QUESTIONS:**
1. What does `multi: true` mean in the HTTP_INTERCEPTORS provider?
2. Why is `request.clone()` used instead of modifying the request directly?
3. How would you add a response interceptor for global 401 handling?

**IMPORTANT FOR INTERVIEW:**
`HttpRequest` objects are **immutable** in Angular. You must use `.clone()` to create a modified copy. `multi: true` tells Angular this is one of potentially many interceptors (not the only one) — without it, only the last interceptor would be registered.

---

## RxJS & Observables

---

**QUESTION:**
How is RxJS used in your project?

**ANSWER:**

**1. HTTP calls return Observables:**
```typescript
GetAssignmentdata(...): Observable<AssignmentResponseData[]> {
  return this.http.get<AssignmentResponseData[]>(url, { params });
}
```

**2. Subscribing in component:**
```typescript
this.assignmentService.GetAssignmentdata(...).subscribe({
  next: (data) => { this.asndata = data; },
  error: (err) => { console.error(err); }
});
```

**3. BehaviorSubject for loader state:**
```typescript
// LoaderService
private isLoading = new BehaviorSubject<boolean>(false);
loading$ = this.isLoading.asObservable();

show() { this.isLoading.next(true); }
hide() { this.isLoading.next(false); }
```

**4. TokenApiService** uses Observables for the token HTTP call and the component chains token fetch → data fetch sequentially.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Observable and Promise?
2. What is the difference between Subject, BehaviorSubject, and ReplaySubject?
3. What RxJS operators would you use to retry a failed API call?

**IMPORTANT FOR INTERVIEW:**
- Observable is lazy (doesn't execute until subscribed). Promise is eager (executes immediately).
- BehaviorSubject requires an initial value and always emits the latest value to new subscribers.
- For retry: `retryWhen()` or `retry(3)` operator. For chaining dependent calls: `switchMap()`.

---

## Lifecycle Hooks

---

**QUESTION:**
Which Angular lifecycle hooks are used in your project?

**ANSWER:**

**`ngOnInit()`** is the primary hook used in `ServiceSelectionDialogComponent`:
- Sets language using RxTranslation
- Calls `getasndata()` to initiate the data fetch flow
- Runs after Angular has initialized all input bindings

**`ServiceSelectionComponent`** uses the constructor or `ngOnInit` to read DOM attributes via `ElementRef` and pass them to child.

**What's NOT used:** `ngOnChanges`, `ngAfterViewInit`, `ngOnDestroy`. Since the component is a Web Component with no dynamic input changes and the component lifecycle is tied to the page lifecycle, `ngOnDestroy` is particularly important to add to unsubscribe Observables and prevent memory leaks.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `constructor` and `ngOnInit`?
2. Why should you unsubscribe from Observables in `ngOnDestroy`?
3. When would you use `ngAfterViewInit`?

**IMPORTANT FOR INTERVIEW:**
Constructor should only inject dependencies. `ngOnInit` is where initialization logic lives because `@Input()` values are set by Angular before `ngOnInit` runs but not before the constructor. This project is missing `ngOnDestroy` — if the user navigates away and the component is destroyed while an HTTP call is in flight, it could cause memory leaks.

---

## Multilingual Support (i18n / RxTranslation)

---

**QUESTION:**
How is multi-language support implemented in your Angular project?

**ANSWER:**
The project uses `@rxweb/translate` (RxTranslation) for runtime language switching based on the `Languageid` attribute.

**Language constants** (`constants/languages.ts`):
```typescript
export const LANGUAGES = [
  { id: 1, code: 'en' },
  { id: 2, code: 'jp' },
  { id: 3, code: 'cn' },
  // ... 20+ languages
];
```

**Translation files** (`assets/i18n/{lang}/messages.json`):
```json
{
  "ServiceSelectionDialogComponent": {
    "headingtext": "Please select the desired service",
    "BrandheadingEnago": "Editing Service",
    "OrderNow": "Order now"
  }
}
```

**Component:**
```typescript
@translate()
export class ServiceSelectionDialogComponent {
  @prop() headingtext: string;
  @prop() BrandheadingEnago: string;
}
```

The `@translate()` decorator automatically binds translated strings to component properties based on the active language.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between `@angular/localize` and `@rxweb/translate`?
2. How do you switch language at runtime without page reload?
3. How are translation files loaded asynchronously?

**IMPORTANT FOR INTERVIEW:**
Angular's built-in `@angular/localize` requires a separate build per language (build-time i18n). `@rxweb/translate` loads JSON files at runtime enabling language switching without rebuild. For this project, runtime switching is essential because the `Languageid` attribute can differ per user session.

---

## Environment Configuration (Angular)

---

**QUESTION:**
How are multiple environments handled in your Angular project?

**ANSWER:**
Angular's built-in environment file system is used with custom build configurations.

**Environment files:**
- `src/environments/environment.ts` (dev)
- `src/environments/environment.prod.ts`
- `src/environments/environment.uat5.ts`
- `src/environments/environment.uat6.ts`
- `src/environments/environment.preprod.ts`
- etc.

**Each file contains:**
```typescript
export const environment = {
  production: true,
  apis: [
    {
      api: Apis.ServiceselectionAPi,
      url: 'https://mypagerevampapi.enago.com/serviceselection/v1/...',
      key: 'MVAM4AqgmM1vZ6qRqcuJv6vECdNaqaYt3g7kk8V6'
    },
    {
      api: Apis.jwtTokenApi,
      url: 'https://securitytoken.enago.com/SecurityToken/tokengenerator',
      key: '...'
    }
  ]
};
```

**Build commands (`package.json`):**
```json
"build:elements": "...-c production",
"build:elements-uat6": "...-c uat6",
"build:elements-prprod": "...-c preprod"
```

**FOLLOW-UP QUESTIONS:**
1. How does Angular replace environment files at build time?
2. What is the `fileReplacements` config in `angular.json`?
3. Why should API keys not be in frontend environment files?

**IMPORTANT FOR INTERVIEW:**
`angular.json` `fileReplacements` swaps `environment.ts` with `environment.{env}.ts` at build time. Important security note: all Angular environment files are bundled into the JS output and are visible to anyone who downloads the file. API keys in frontend code are a security risk — ideally move to backend proxy calls.

---

## AOT Compilation

---

**QUESTION:**
Does your project use AOT or JIT compilation?

**ANSWER:**
The project uses **AOT (Ahead-of-Time) compilation** for all production builds. This is configured in `angular.json`:

```json
"configurations": {
  "production": {
    "aot": true,
    "buildOptimizer": true,
    "optimization": true
  }
}
```

**Why AOT for Web Components:**
1. Smaller bundle — templates compiled to JavaScript, no Angular compiler needed at runtime
2. Faster rendering — compiled templates execute immediately
3. Earlier error detection — template errors caught at build time, not browser runtime
4. This is critical for a Web Component since the JS file must be self-contained and fast

**FOLLOW-UP QUESTIONS:**
1. What is the difference between AOT and JIT?
2. What errors does AOT catch that JIT misses?
3. What is Ivy and how does it relate to AOT?

**IMPORTANT FOR INTERVIEW:**
JIT compiles templates in the browser at runtime — useful for development (faster rebuilds). AOT compiles templates to TypeScript/JS during build — mandatory for production. Angular Ivy (Angular 9+) is the new AOT compilation engine that produces smaller, faster output. This project uses Angular 12 which uses Ivy by default.

---

## Change Detection

---

**QUESTION:**
How does change detection work in this project?

**ANSWER:**
This project uses Angular's **default change detection** strategy (`ChangeDetectionStrategy.Default`). Angular checks the entire component tree after every event, timer, HTTP response, or async operation.

Since the component is a Web Component:
- It mounts once, loads data once
- No complex state mutations after initial load
- Default change detection is acceptable

**What could be improved:**
Using `ChangeDetectionStrategy.OnPush` in `ServiceSelectionDialogComponent` would be more performant — it only re-renders when `@Input()` references change or when an `Observable` emits. Since data only loads once, `OnPush` + `async` pipe would be ideal.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between Default and OnPush change detection?
2. What triggers change detection in Default strategy?
3. How does the `async` pipe benefit OnPush components?

**IMPORTANT FOR INTERVIEW:**
Zone.js is what makes Angular's default change detection work — it patches all async APIs (setTimeout, XMLHttpRequest, Promises) and notifies Angular when something happens. `OnPush` components only check when explicitly marked dirty, making them Zone.js independent and much more performant in large component trees.

---

---

# DATABASE / SQL SECTION

---

## Stored Procedures

---

**QUESTION:**
How are stored procedures used in your project?

**ANSWER:**
All database operations use stored procedures — no inline SQL. Dapper calls them with parameters.

**Stored Procedures used:**
1. `MP_GetASNdataForServiceSelectionApi`
   - Parameters: `@UserName`, `@WebsiteID`
   - Returns: Assignment data with brand counts, creation dates, brand IDs

2. `MP_SP_GetConfigServiceBrandwiseData`
   - Parameters: `@WebsiteId`
   - Returns: Brand-wise service configuration, URLs

**Dapper call:**
```csharp
var result = await conn.QueryAsync<AssignmentData>(
    "MP_GetASNdataForServiceSelectionApi",
    new { UserName = request.ClientUserName, WebsiteID = request.WebsiteID },
    commandType: CommandType.StoredProcedure
);
```

**Benefits:**
1. SQL logic centralized in DB — one change fixes all consumers
2. Better performance — execution plans are cached by SQL Server
3. Security — parameterized, prevents SQL injection
4. Access control — app user only has EXECUTE permission, not direct table access

**FOLLOW-UP QUESTIONS:**
1. What is the difference between a stored procedure and a function in SQL?
2. How does SQL Server cache execution plans for stored procedures?
3. How do you debug a stored procedure called from .NET code?

**IMPORTANT FOR INTERVIEW:**
Functions cannot have side effects (no INSERT/UPDATE/DELETE), can be used in SELECT statements, and are always synchronous. Stored procedures can do anything and return multiple result sets. Execution plan caching means the first call compiles the plan, subsequent calls reuse it — faster after first execution.

---

## SQL JOINs

---

**QUESTION:**
What JOIN types are likely used in the stored procedures of your project?

**ANSWER:**
The stored procedures in this project (`MP_GetASNdataForServiceSelectionApi`, `MP_SP_GetConfigServiceBrandwiseData`) are accessed via Dapper and return data involving multiple entities. Based on the data model returned:

- `INNER JOIN` — To join assignment data with brand configuration tables (only matching records)
- `LEFT JOIN` — To fetch brand data even when a user has no assignments (AttributeValue vs ASNBrandIds logic suggests LEFT JOIN on assignment history)

**The controller logic confirms LEFT JOIN usage:**
```csharp
// If ASNCount == 0 → user has no assignments → uses AttributeValue (default brands from config)
// If ASNCount > 0 → user has assignments → uses ASNBrandIds (actual brand history)
```
This two-path logic suggests the SP does a LEFT JOIN between user-assignment table and brand config table, returning NULLs for users with no history.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?
2. When would a CROSS JOIN be useful?
3. What is a self-join and when would you use it?

**IMPORTANT FOR INTERVIEW:**
LEFT JOIN returns all rows from the left table + matching rows from right (NULL if no match). This is essential here — you want ALL users in the result, even those with no assignments. INNER JOIN would exclude users with no assignment history.

---

## Query Optimization & Indexing

---

**QUESTION:**
What query optimization strategies are relevant to this project?

**ANSWER:**
Based on the stored procedures and data accessed:

**Likely required indexes:**
- Index on user/username column in assignment table — `MP_GetASNdataForServiceSelectionApi` filters by `@UserName`
- Index on `WebsiteID` in config table — `MP_SP_GetConfigServiceBrandwiseData` filters by `@WebsiteId`
- Composite index on `(UserName, WebsiteID)` for the main SP — covers both filter columns

**Why indexing matters here:**
- This is a high-traffic API (every portal page load calls it)
- Response time directly affects user experience
- Without indexes, SQL Server does full table scans

**Execution plan caching:**
Stored procedures have execution plans cached by SQL Server — first call slightly slower (plan compilation), subsequent calls use cached plan.

**FOLLOW-UP QUESTIONS:**
1. What is the difference between clustered and non-clustered index?
2. What is index fragmentation and how do you fix it?
3. What is the SQL Server execution plan and how do you read it?

**IMPORTANT FOR INTERVIEW:**
Clustered index defines physical row order in the table (one per table, usually primary key). Non-clustered index is a separate structure pointing to rows (multiple allowed). For read-heavy APIs like this, a covering index (includes all queried columns) eliminates the need for key lookups — the entire query resolves from the index alone.

---

## Transactions

---

**QUESTION:**
Are transactions used in your project? Should they be?

**ANSWER:**
This project is **read-only** — `AssignmentDataController` only does SELECT operations. No INSERT/UPDATE/DELETE in the visible code paths. Therefore, explicit transactions are not required.

**If write operations were added**, Dapper transactions would be used:
```csharp
using (var conn = new SqlConnection(_connectionString))
{
    conn.Open();
    using (var transaction = conn.BeginTransaction())
    {
        try
        {
            await conn.ExecuteAsync("SP_Name", params, transaction);
            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
}
```

**FOLLOW-UP QUESTIONS:**
1. What are the ACID properties of a transaction?
2. What are SQL Server isolation levels?
3. What is a deadlock and how do you prevent it?

**IMPORTANT FOR INTERVIEW:**
ACID: Atomicity (all or nothing), Consistency (valid state before and after), Isolation (concurrent transactions don't interfere), Durability (committed changes persist). Default SQL Server isolation is READ COMMITTED — readers don't block writers, writers block readers.

---

## Pagination

---

**QUESTION:**
Is pagination implemented in your project?

**ANSWER:**
This project does NOT implement pagination. The stored procedure `MP_GetASNdataForServiceSelectionApi` returns all assignment records for a user. Since the dataset is small (a single user's assignment history across 4 brands), pagination is not needed.

**If pagination were needed**, SQL Server `OFFSET-FETCH` would be used:
```sql
SELECT * FROM AssignmentData
WHERE UserName = @UserName
ORDER BY ASNCreatedOn DESC
OFFSET (@PageNumber - 1) * @PageSize ROWS
FETCH NEXT @PageSize ROWS ONLY
```

**FOLLOW-UP QUESTIONS:**
1. What is the difference between OFFSET-FETCH and ROW_NUMBER() for pagination?
2. What is keyset pagination and when is it better than offset pagination?
3. How do you return total record count alongside paged results efficiently?

**IMPORTANT FOR INTERVIEW:**
OFFSET pagination has a performance problem at large offsets — it still reads and discards N rows. Keyset pagination (cursor-based, using `WHERE id > lastSeenId`) is more efficient for large datasets but requires a unique sortable key.

---

---

## MOST IMPORTANT INTERVIEW QUESTIONS (Top 30 — Project-Specific)

1. **Explain the complete architecture of your Service Selection project — frontend to database.**
2. **Why did you use Angular Elements instead of a regular Angular application?**
3. **How does the JWT token flow work — from Angular to the backend API?**
4. **Explain the Repository Pattern implementation in your .NET project.**
5. **Why was Dapper chosen over Entity Framework Core?**
6. **How does the `TokenInterceptor` work and why is `request.clone()` needed?**
7. **How do you handle multiple environments (UAT1, UAT5, UAT6, Stage, Prod) in both Angular and .NET?**
8. **Explain how multi-language support works using `@rxweb/translate`.**
9. **What is the purpose of `IAssignmentDataContract` — why not use `AssignmentDataRepository` directly?**
10. **How is API versioning implemented? What happens if a client doesn't pass a version?**
11. **What SOLID principles did you implement? Give one concrete example from the code.**
12. **What is the difference between `init` and `set` in C# property accessors? Where did you use `init`?**
13. **Explain the complete Serilog + Elasticsearch logging setup.**
14. **How does CORS work and why is `AllowAnyOrigin` used here?**
15. **What is `AddTransient` vs `AddScoped` vs `AddSingleton`? Which did you use and why?**
16. **Explain the Angular Web Component lifecycle — how are attributes read from the DOM?**
17. **What is `BehaviorSubject` and how is it used in `LoaderService`?**
18. **What is AOT compilation and why is it important for your Web Component build?**
19. **How does Dapper map stored procedure results to C# objects?**
20. **Explain the brand selection logic — how does ASNCount = 0 vs ASNCount > 0 affect the flow?**
21. **What is the health check endpoint for and how is it configured?**
22. **How does the `concatenate.js` build script package the Angular Element?**
23. **What are the security vulnerabilities in this project and how would you fix them?**
24. **How would you add caching to this API without changing the controller?**
25. **What happens if the JWT token expires mid-session? How does the Angular code handle it?**
26. **Why does the controller return `List<ClientResponse>` instead of just `ClientResponse`?**
27. **How would you add unit tests to the `AssignmentDataRepository`?**
28. **What is the `enumServiceWorkFlowType` enum used for in the business logic?**
29. **Explain the date formatting logic in the frontend — why is `moment.js` used?**
30. **If this service needed to handle 10x traffic, what would you change in the architecture?**

---

## MISSING BEST PRACTICES (Enterprise Improvement Areas)

### Security
- **JWT secret hardcoded in `appsettings.json`** → Move to Azure Key Vault / AWS Secrets Manager / environment variables
- **`ValidateIssuer = false`, `ValidateAudience = false`** → Always validate issuer and audience in production
- **API keys in Angular environment files** → Frontend bundles are public; keys visible to anyone
- **`AllowAnyOrigin` in CORS** → Restrict to known domains (enago.com, ulatus.com, etc.)
- **Token in sessionStorage** → Vulnerable to XSS; consider HttpOnly cookies for web contexts

### Error Handling
- **No global exception handling middleware** → Add `UseExceptionHandler` or `IMiddleware`-based error handler
- **No input validation** → Add FluentValidation or DataAnnotations on `ClientRequest`
- **No circuit breaker** → Add Polly for the external SecurityToken API call

### Performance
- **No caching layer** → Assignment data per user changes infrequently; add Redis/IMemoryCache
- **No rate limiting** → Public-facing API should throttle requests
- **No response compression** → Add `app.UseResponseCompression()` for smaller payloads
- **Angular bundle ~1MB** → Consider splitting, lazy loading assets, or differential loading

### Testing
- **Spec files exist but are empty** → Unit tests for components, services, and repositories are missing
- **No integration tests** → Backend should have Postman/xUnit integration test suite
- **No mock for IAssignmentDataContract** → DI is set up correctly, tests would be straightforward to add

### Architecture
- **No Unit of Work pattern** → Acceptable for now but needed if multi-repository transactions are added
- **No AutoMapper** → Manual mapping is fine here but AutoMapper reduces boilerplate in larger projects
- **No request/response logging middleware** → Log every API call with duration for performance monitoring
- **No correlation ID** → Add `X-Correlation-ID` header tracing for distributed debugging

### Angular
- **Missing `ngOnDestroy` + unsubscribe** → HTTP subscriptions should be cleaned up
- **No `ChangeDetectionStrategy.OnPush`** → Would improve rendering performance
- **No error boundary** → What does the user see if the API fails? No error state UI visible

---

## REAL-TIME SCENARIO-BASED QUESTIONS

**Scenario 1:**
> "The service selection component loads correctly in your local UAT environment but shows a blank screen in production. How do you debug this?"

Answer approach: Check browser console for JS errors → Check network tab for API call (is it 401 → token expired? 403 → wrong token? CORS error?) → Check if `appsettings.prod.json` has correct connection string → Check Elasticsearch logs (Kibana) for server-side errors → Check if `service-selection-element.js` path is correct in the production portal

---

**Scenario 2:**
> "A user reports that the wrong service cards are being shown. They've used Enago 5 times but Ulatus card appears first. How do you investigate?"

Answer approach: Check `getasndata()` sorting logic — primary sort is by `ASNBrandCount` (desc), secondary by `ASNCreatedOn`. Check if the stored proc `MP_GetASNdataForServiceSelectionApi` is returning correct `ASNBrandCount` for this user. Check `WebsiteID` parameter — wrong WebsiteID would pull wrong brand history. Check if `ASNCount == 0` branch is wrongly triggered (using `AttributeValue` instead of `ASNBrandIds`).

---

**Scenario 3:**
> "The API is responding slowly — average 3 seconds. How would you diagnose and fix it?"

Answer approach: Add request timing middleware → Check Serilog logs for slow queries → Run the stored procedure `MP_GetASNdataForServiceSelectionApi` directly in SSMS with EXPLAIN → Look for missing indexes on `@UserName`, `@WebsiteID` → Add IMemoryCache for brand URL data (rarely changes) → Check if `SubdomainRedirectRepository` is making an additional external HTTP call

---

**Scenario 4:**
> "You need to support a new brand — 'Tranka' — with ID 5. What files/code needs to change?"

Answer: 
1. Backend: Add `tranka = 5` to `enumServiceWorkFlowType` enum
2. DB: Add brand config in `MP_SP_GetConfigServiceBrandwiseData` result set
3. Frontend: Add case in `getBrandHeading(5)`, `getBrandDescription(5)`, `getBrandClass(5)`
4. i18n: Add `BrandheadingTranka` and `BrandDescriptionTranka` keys to all 20+ language JSON files
5. Add SVG icon to `assets/images/`

---

**Scenario 5:**
> "A security audit found that JWT tokens are being stored in sessionStorage, which is vulnerable to XSS. How would you fix it?"

Answer: Move to HttpOnly cookies — the Angular frontend cannot access HttpOnly cookies via JavaScript (XSS-safe). The TokenApiService would no longer store in sessionStorage. Backend sets `Set-Cookie: token=...; HttpOnly; Secure; SameSite=Strict`. The TokenInterceptor would be removed (cookies are automatically sent by the browser). This requires CORS to allow credentials (`withCredentials: true` in Angular HttpClient) and the backend must specify exact origins.

---

## HR + MANAGER ROUND QUESTIONS

**Q: Tell me about this project in 2 minutes.**

> "I worked on revamping the service selection page for Enago's customer portal. The original page was tightly coupled to a single portal. My task was to convert it into a reusable Angular Web Component — essentially a self-contained custom HTML element that any portal can embed without knowing it's Angular. On the backend, I built a clean .NET 6 REST API using the Repository Pattern, Dapper for data access, and JWT authentication. The API aggregates assignment history data from SQL Server stored procedures and resolves brand-specific URLs, returning which service brands the user has used and in what order. The component supports 20+ languages and deploys to 6 different environments from UAT to production."

---

**Q: What was the most challenging part of this project?**

> "The most challenging part was the Angular Elements packaging. Unlike a normal SPA, a Web Component bundles the entire Angular runtime into a single file. Getting the asset paths, translation file loading, and attribute-to-input binding to work correctly when embedded in third-party pages required significant troubleshooting — especially the custom `concatenate.js` build script that merges the runtime, polyfills, and application chunks into one deployable file."

---

**Q: What would you do differently if you built this again?**

> "I would add proper global exception handling middleware, Redis caching for brand URL data that rarely changes, and replace sessionStorage JWT storage with HttpOnly cookies for better security. I'd also add unit tests from day one — the DI setup is perfect for mocking but no tests were written. And I'd restrict CORS to known domains instead of allowing any origin."

---

**Q: How did you ensure the component works across all brand portals?**

> "The Web Component reads all configuration from DOM attributes — no hardcoded portal-specific logic inside the component. By passing `WebsiteID` and `ICCode` as attributes, the backend resolves the correct brand URLs for that portal. The component itself is portal-agnostic."

---

## QUICK REVISION NOTES (30-minute pre-interview review)

```
BACKEND QUICK FACTS:
─────────────────────────────────────
Framework       : ASP.NET Core 6.0
ORM             : Dapper (NOT Entity Framework)
Database        : SQL Server — CIPLPROD catalog
Auth            : JWT Bearer, HS256, no issuer/audience validation
DI Lifetime     : AddTransient for both repositories
Pattern         : Repository Pattern + Interface-based DI
Logging         : Serilog → Elasticsearch (index: serviceselection-log-yyyy.MM.dd)
CORS            : AllowAnyOrigin, AllowAnyMethod, AllowAnyHeader
API Versioning  : URL-based (/v1/), default v1.0
Health Check    : GET /health
Swagger         : Enabled with JWT Bearer auth
Stored Procs    : MP_GetASNdataForServiceSelectionApi
                  MP_SP_GetConfigServiceBrandwiseData
Models          : init-only properties (immutable DTOs)
Docker          : Multi-stage Dockerfile, port 14004

ANGULAR QUICK FACTS:
─────────────────────────────────────
Framework       : Angular 12.1.3
Build Type      : Angular Element (Web Component)
Output          : service-selection-element.js (~1MB)
                  service-selection-styles.css (~427KB)
Components      : ServiceSelectionComponent (root)
                  ServiceSelectionDialogComponent (main)
                  LoaderComponent
Services        : AssignmentDataService, TokenApiService, LoaderService, LoggerService
Interceptor     : TokenInterceptor (adds JWT Bearer header)
i18n            : @rxweb/translate — 20+ languages, runtime switching
Compilation     : AOT (production)
Change Detection: Default (should be OnPush)
State           : No NgRx — simple BehaviorSubject in LoaderService
Environments    : 8+ env files (dev, uat1/5/6/11, stage1/2, preprod, prod)
Build Scripts   : npm run build:elements-{env}

BUSINESS LOGIC QUICK FACTS:
─────────────────────────────────────
Brands          : Enago(1), Ulatus(2), Voxtab(3), PublicationSupport(4)
Sort Logic      : Primary: ASNBrandCount DESC, Secondary: ASNCreatedOn DESC
Token Flow      : Angular → SecurityToken API → JWT → sessionStorage → TokenInterceptor → API Header
Data Flow       : DOM attrs → token → API call → SP → brand URLs → sorted cards → user clicks → new tab
Language Load   : Languageid attribute → LANGUAGES array lookup → RxTranslation
No assignments  : AttributeValue field used (default brand list)
Has assignments : ASNBrandIds field used (historical brand list)
```

---

## TOP 10 STRONGEST CONCEPTS IN THIS PROJECT

1. **Angular Elements (Web Component)** — Advanced Angular feature; packaged as reusable custom HTML element
2. **Repository Pattern with Interface-based DI** — Clean, testable, SOLID-compliant architecture
3. **JWT Authentication** — Proper Bearer token flow with external token service and interceptor
4. **HTTP Interceptor** — Elegant cross-cutting concern for token injection
5. **Multi-environment Configuration** — 8+ environments for both Angular and .NET managed cleanly
6. **Multi-language i18n** — Runtime language switching with 20+ locales via RxTranslation
7. **Dapper with Stored Procedures** — Performant, secure, SQL-controlled data access
8. **Serilog + Elasticsearch Logging** — Production-grade structured log aggregation
9. **Immutable DTOs (init properties)** — Thread-safe, encapsulated model design in C#
10. **API Versioning** — URL-based versioning for future-proof API evolution

---

## TOP 10 MISSING / WEAK CONCEPTS IN THIS PROJECT

1. **Global Exception Handling** — No middleware; unhandled exceptions may expose stack traces
2. **Unit Tests** — Spec files exist but no test implementations; 0% test coverage
3. **Input Validation** — No FluentValidation or DataAnnotations on `ClientRequest`
4. **Caching Layer** — No Redis/IMemoryCache; brand URL data re-fetched every request
5. **HttpOnly Cookie for JWT** — sessionStorage is XSS-vulnerable; HttpOnly cookies are safer
6. **CORS Origin Restriction** — `AllowAnyOrigin` is overly permissive; should list known domains
7. **`ngOnDestroy` / Observable Cleanup** — Angular components don't unsubscribe; memory leak risk
8. **Global API Error Handling (Angular)** — No response interceptor for 401/500 handling
9. **`ChangeDetectionStrategy.OnPush`** — Default change detection is inefficient for read-once data
10. **Secret Management** — JWT key and DB credentials hardcoded in config files; should use vault/env vars

---

*Document generated for interview preparation. All examples reference actual files, classes, and methods from the CMR-ServiceSelection project.*
