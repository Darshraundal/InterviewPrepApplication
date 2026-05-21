# Interview Preparation Guide — Offline Invoice Project
> Generated: 2026-05-18 | Stack: .NET 6 Web API + .NET 6 Worker Service + Class Library (CSCrypter)
> **Note:** This project has NO Angular frontend. All Angular questions are marked as "Not Implemented."

---

## 1. PROJECT ARCHITECTURE SUMMARY

### Components
| Component | Type | Purpose |
|---|---|---|
| `OfflineInvoice-API` | ASP.NET Core Web API (.NET 6) | Receives offline invoice data from external clients, updates DB via stored procedures |
| `OfflineInvoice-service` | .NET Worker Service (.NET 6) | Background service that polls DB and pushes ASN/invoice data to external Odoo API |
| `CSCrypter` | .NET Class Library (.NET 6) | AES encryption/decryption + XML address parsing, referenced by the service |

### Full Request Lifecycle (API Side)
```
External Client
  → HTTP POST with JWT Bearer token in Authorization header
  → ASP.NET Core Middleware Pipeline (HTTPS Redirect → Routing → Authentication → CORS → Authorization)
  → OfflineInvoiceASNDataController (Route: offlineInvoice/v{version}/OfflineInvoiceASNData)
  → IOfflineInvoiceASNData interface (DI resolved to IOfflineInvoiceASNDataRepository)
  → Dapper + SqlConnection → Stored Procedure (CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing or CS_UpdateIsPushToOfflineInvoicingbacktoCS)
  → SQL Server (CIPLPROD)
  → Returns int result → Controller maps to HTTP 200 or 400
```

### Worker Service Lifecycle
```
Program.cs → Host.CreateDefaultBuilder → Worker (BackgroundService)
  → ExecuteAsync runs every 60 minutes (IntervalMinutes from Config)
  → ScheduleService() → OfflineInvoiceASNdatapush_service.offlineInvoiceASNdataPush()
  → AsnInvoiceDataDAO.GetASNInvoiceData() → SP: CS_GetASNDataForOfflineInvoicing
  → Decrypt PII fields using Crypter.Operations.DecryptAES()
  → For each ASN: POST to Odoo (ClientDataAPIUrl + ASNInvoiceDataAPIUrl) via RestSharp
  → AsnInvoiceDataDAO.UpdateOffileInvoiceAsnDataPush() → SP: CS_UpdateASNDataForOfflineInvoices
```

### Authentication Flow
```
Worker Service:
  Startup → GetCookiesForAuthorization() → POST to InvoiceSessionAPIUrl (Odoo)
  → Receives Token → stored in Environment Variable "AuthToken"
  → Token reused in Authorization header for all subsequent API calls
  → Session expiry detected by error.code == 100 → re-authenticates automatically

OfflineInvoice-API:
  JWT Bearer Token (HS256) → Validated against JWTAuthenticationKey from appsettings
  → [Authorize] attribute on controller enforces authentication
```

### Database Interaction Flow
```
Both projects → Dapper (micro-ORM) → SqlConnection/IDbConnection
  → Stored Procedures called with DynamicParameters
  → Table-Valued Parameters (TVPs) used to pass lists:
      - dbo.UpdateOfflineInvoiceASNListTableType (API)
      - dbo.OfflineInvoiceASNListTableType (Service)
  → QuerySingle<int> for scalar results
  → QueryMultiple for multiple result sets (ASN + Client data)
  → No Entity Framework used
```

---

## 2. .NET / .NET CORE — QUESTIONS & ANSWERS

---

QUESTION:
What is the middleware pipeline in your project and how is it configured?

ANSWER:
The middleware pipeline is a sequence of components in ASP.NET Core that process HTTP requests in order. Each middleware can short-circuit the pipeline or pass the request to the next component. Order matters critically.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Startup.cs`
- Class: `Startup`
- Method: `Configure(IApplicationBuilder app, IWebHostEnvironment env)`
- Implementation:
```
1. UseDeveloperExceptionPage() — catches unhandled exceptions, shows detail
2. UseSwagger() + UseSwaggerUI() — serves OpenAPI docs at /swagger
3. UseHttpsRedirection() — redirects HTTP to HTTPS
4. UseRouting() — matches request to endpoint
5. UseAuthentication() — validates JWT token
6. UseCors() — adds CORS headers (from AllowedClientUrls config)
7. UseAuthorization() — enforces [Authorize] attribute
8. UseEndpoints() — maps controllers and /health endpoint
```
Order is critical: `UseAuthentication()` must come before `UseAuthorization()`.

FOLLOW-UP QUESTIONS:
1. Why must UseAuthentication come before UseAuthorization?
2. What happens if you call UseRouting after UseAuthorization?
3. What is short-circuiting in middleware and where would it happen here?

IMPORTANT FOR INTERVIEW:
CORS is configured twice in this project — once in `ConfigureServices` with `AddPolicy` and once in `Configure` with `UseCors`. The second call using `WithOrigins` but also calling `AllowAnyOrigin()` is contradictory and effectively allows all origins regardless. Mention this as a gap: ideally, use a named policy consistently.

---

QUESTION:
How is Dependency Injection (DI) implemented in your project?

ANSWER:
DI is the design pattern where objects receive their dependencies from an external source rather than creating them. ASP.NET Core has a built-in IoC container.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Startup.cs` (line 84)
- Class: `Startup.ConfigureServices`
- Implementation:
```csharp
services.AddTransient<IOfflineInvoiceASNData, IOfflineInvoiceASNDataRepository>();
```
The controller `OfflineInvoiceASNDataController` declares `IOfflineInvoiceASNData` in its constructor — the framework injects `IOfflineInvoiceASNDataRepository` at runtime.

- File: `OfflineInvoice-service/Program.cs` (line 40)
```csharp
services.AddSingleton<IAPIOperation, ApiOperation>();
```
`ApiOperation` is injected into `Worker` via `IAPIOperation`, which is then passed to `OfflineInvoiceASNdatapush_service`.

FOLLOW-UP QUESTIONS:
1. What is the difference between AddTransient, AddScoped, and AddSingleton?
2. Why is IAPIOperation registered as Singleton rather than Transient here?
3. What happens if you inject a Scoped service into a Singleton?

IMPORTANT FOR INTERVIEW:
- **Transient**: New instance every time it's requested. Used for `IOfflineInvoiceASNData` (stateless repository).
- **Scoped**: One instance per HTTP request. Common for DbContext in EF Core.
- **Singleton**: One instance for app lifetime. Used for `IAPIOperation` (stateless HTTP client wrapper).
- Captive dependency problem: injecting a Transient or Scoped into a Singleton is dangerous — the short-lived service gets captured for the app's lifetime.

---

QUESTION:
What are the service lifetimes used in your project and why?

ANSWER:
- `AddTransient<IOfflineInvoiceASNData, IOfflineInvoiceASNDataRepository>` — creates a new repository instance per injection. Safe because the repository holds no state; connection string is read in constructor.
- `AddSingleton<IAPIOperation, ApiOperation>` — one instance of `ApiOperation` for the entire service lifetime. Safe because `ApiOperation` is stateless (no fields mutated between calls, except token refresh which uses Environment variables).

PROJECT EXAMPLE:
- File: `Startup.cs` line 84 — Transient registration
- File: `OfflineInvoice-service/Program.cs` line 40 — Singleton registration

FOLLOW-UP QUESTIONS:
1. If IOfflineInvoiceASNDataRepository held a SqlConnection as a field, what lifetime would be appropriate?
2. Can you register a service with AddHostedService? What lifetime does it use?

---

QUESTION:
How is JWT Authentication implemented in your project?

ANSWER:
JWT (JSON Web Token) is a compact, self-contained token format. The API validates tokens using a symmetric key (HS256).

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Startup.cs` (lines 67–83)
- Class: `Startup.ConfigureServices`
- Implementation:
```csharp
var key = Configuration["JWT:JWTAuthenticationKey"];
services.AddAuthentication(x => {
    x.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    x.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
}).AddJwtBearer(x => {
    x.RequireHttpsMetadata = false;
    x.SaveToken = true;
    x.TokenValidationParameters = new TokenValidationParameters {
        ValidateIssuerSigningKey = true,
        ValidateIssuer = false,
        ValidateAudience = false,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.ASCII.GetBytes(key))
    };
});
```
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Controllers/OfflineInvoiceASNController.cs` (line 11)
- `[Authorize]` attribute on the controller class enforces token validation on all endpoints.

Key from `appsettings.json`: `JWT:JWTAuthenticationKey` (a 64-char hex string).

FOLLOW-UP QUESTIONS:
1. What does ValidateIssuer = false mean and what risk does it introduce?
2. How would you implement token refresh in this project?
3. What is the difference between Authentication and Authorization?

IMPORTANT FOR INTERVIEW:
`ValidateIssuer = false` and `ValidateAudience = false` means any token signed with the correct key is accepted regardless of its origin. In production, both should be true for stricter security. Also `RequireHttpsMetadata = false` allows HTTP, which should be true in production.

---

QUESTION:
How is API Versioning implemented in your project?

ANSWER:
API versioning allows multiple versions of the same API to coexist. This project uses URL segment versioning.

PROJECT EXAMPLE:
- File: `Startup.cs` (lines 86–97)
- Implementation:
```csharp
var defaultVersion = Configuration["ApiVersion:DefaultVersion"]; // "1.0"
services.AddApiVersioning(x => {
    x.DefaultApiVersion = new ApiVersion(majorVersion, minorVersion);
    x.AssumeDefaultVersionWhenUnspecified = true;
    x.ReportApiVersions = true;
});
```
- File: `OfflineInvoiceASNController.cs` (line 13)
```csharp
[Route("offlineInvoice/v{version:apiVersion}/[controller]")]
```
URL: `POST /offlineInvoice/v1/OfflineInvoiceASNData/PostASNDataForOfflineInvoice`

The default version (`1.0`) is read dynamically from `appsettings.json:ApiVersion:DefaultVersion`.

FOLLOW-UP QUESTIONS:
1. What are the three approaches to API versioning in ASP.NET Core?
2. What does ReportApiVersions = true do?
3. How would you deprecate version 1.0 and introduce version 2.0?

IMPORTANT FOR INTERVIEW:
Three approaches: URL segment (`v{version:apiVersion}`), query string (`?api-version=1.0`), HTTP header (`api-version: 1.0`). URL segment is the most visible and cache-friendly. Header versioning keeps clean URLs but is harder to test in a browser.

---

QUESTION:
How is logging implemented in your project?

ANSWER:
This project uses dual logging — both **Serilog** (structured logging with Elasticsearch sink) and **NLog** (file-based logging).

PROJECT EXAMPLE:
**Serilog (API):**
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Program.cs`
- Class: `Program.ConfigureLogging()`
- Sinks: Debug, Console, Elasticsearch
- Configuration:
```csharp
Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .WriteTo.Debug()
    .WriteTo.Console()
    .WriteTo.Elasticsearch(ConfigureElasticSink(...))
    .ReadFrom.Configuration(configuration)
    .CreateLogger();
```
- Elasticsearch index pattern: `OfflineInvoice-log-{yyyy.MM.dd}`
- `.UseSerilog()` wires Serilog into the host pipeline.

**NLog (both API and Service):**
- File: `OfflineInvoiceASNController.cs` (line 16)
```csharp
private static NLog.Logger _logger = NLog.LogManager.GetCurrentClassLogger();
```
- Used for `Info`, `Warn`, `Error` logs in controllers and repositories.

FOLLOW-UP QUESTIONS:
1. Why use both Serilog and NLog?
2. What is structured logging and why is it better than string interpolation logs?
3. How would you add a minimum log level override for a specific namespace?

IMPORTANT FOR INTERVIEW:
Using both frameworks simultaneously adds complexity — ideally one should be chosen. Serilog with Elasticsearch provides centralized, searchable logs (ELK stack), while NLog provides file-based local logs via `nlog.config`. The structured log enrichments (`FromLogContext`, `WithMachineName`) add useful metadata for production debugging.

---

QUESTION:
What is the Repository Pattern and how is it used in your project?

ANSWER:
The Repository Pattern abstracts the data access layer, hiding SQL/ORM details behind an interface. Controllers depend on the interface, not the concrete implementation.

PROJECT EXAMPLE:
- Interface: `OfflineInvoice-API/OfflineInvoicingAPI/Contracts/IOfflineInvoiceASNData.cs`
```csharp
public interface IOfflineInvoiceASNData {
    int UpdateInvoiceASNdata(OfflineInvoiceASNdata offlineInvoiceASNdata);
    int PushOfflinedatabacktoCS(List<AssignmentDataModel> assignments);
}
```
- Implementation: `OfflineInvoice-API/OfflineInvoicingAPI/Repository/AsnRepository.cs`
  - Class: `IOfflineInvoiceASNDataRepository : IOfflineInvoiceASNData`
  - Opens `SqlConnection`, builds `DataTable`, calls stored procedures via Dapper.
- Controller: `OfflineInvoiceASNDataController` receives `IOfflineInvoiceASNData` in constructor — it never knows about `SqlConnection` or Dapper.

Same pattern in the service: `IAPIOperation` interface / `ApiOperation` concrete class.

FOLLOW-UP QUESTIONS:
1. Why name the concrete class `IOfflineInvoiceASNDataRepository` — it starts with I like an interface. What naming convention would you suggest?
2. How would you unit test the controller using a mock `IOfflineInvoiceASNData`?
3. What is the difference between Repository and DAO (Data Access Object)?

IMPORTANT FOR INTERVIEW:
The naming issue is worth mentioning: `IOfflineInvoiceASNDataRepository` starts with "I" but is a concrete class. Best practice is to name it `OfflineInvoiceASNDataRepository`. This could confuse other developers. The DI registration `services.AddTransient<IOfflineInvoiceASNData, IOfflineInvoiceASNDataRepository>` is correct despite the naming.

---

QUESTION:
How does your project handle CORS?

ANSWER:
CORS (Cross-Origin Resource Sharing) allows the API to accept requests from different origins (domains). This is configured in `Startup.cs`.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Startup.cs`
- ConfigureServices (line 27):
```csharp
services.AddCors(o => o.AddPolicy("_myAllowSpecificOrigins", builder => {
    builder.AllowAnyMethod().AllowAnyHeader().AllowAnyOrigin();
}));
```
- Configure (line 122):
```csharp
app.UseCors(builder => builder.WithOrigins(Configuration["AllowedClientUrls"].ToString())
    .AllowAnyHeader().AllowAnyMethod().AllowAnyOrigin().Build());
```
The `AllowedClientUrls` config key is an empty string in the current `appsettings.json`.

FOLLOW-UP QUESTIONS:
1. What is the security risk of AllowAnyOrigin with AllowCredentials?
2. In the current code, AllowAnyOrigin() overrides WithOrigins() — what actually happens?
3. How would you restrict CORS to specific domains?

IMPORTANT FOR INTERVIEW:
`AllowAnyOrigin()` and `AllowCredentials()` cannot be combined — ASP.NET Core throws an exception. The current code calls both `WithOrigins()` and `AllowAnyOrigin()`, making `WithOrigins` redundant. For production, restrict to specific origins: `builder.WithOrigins("https://app.example.com").AllowAnyHeader().AllowAnyMethod()`.

---

QUESTION:
How does your project use Dapper as an ORM?

ANSWER:
Dapper is a micro-ORM — it extends `IDbConnection` with extension methods for mapping SQL results to objects. It is faster than Entity Framework because it doesn't manage entity tracking.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Repository/AsnRepository.cs`
- **Scalar result with stored procedure:**
```csharp
result = con.QuerySingle<int>(
    SqlConstants.CS_UpadateInvoiceEmailSentOn_OfflineInvoice,
    param,
    commandType: CommandType.StoredProcedure
);
```
- **Table-Valued Parameters (TVP):**
```csharp
DataTable assignmentTable = new DataTable();
assignmentTable.Columns.Add("AssignmentID", typeof(int));
...
param.Add("@Assignments", assignmentTable.AsTableValuedParameter("dbo.UpdateOfflineInvoiceASNListTableType"));
```
- **Multiple result sets:**
```csharp
var lst_getAsnInvoiceData = con.QueryMultiple(SPName.CS_GetASNDataForOfflineInvoicing, parameters, commandType: CommandType.StoredProcedure);
var listasndetails = lst_getAsnInvoiceData.Read<ASNInvoiceDataModel>().ToList();
var listclientdetails = lst_getAsnInvoiceData.Read<ClientDataModel>().ToList();
```
(File: `OfflineInvoice-service/Repositories/OfflineInvoiceAsnDataRepository.cs`)

FOLLOW-UP QUESTIONS:
1. What is the difference between QuerySingle and QuerySingleOrDefault?
2. When would you use Execute vs Query in Dapper?
3. How does Dapper map column names to property names when they differ?

IMPORTANT FOR INTERVIEW:
Dapper maps by convention: column name must match property name (case-insensitive). For mismatches, you can use column aliases in SQL or configure a custom type map. TVPs require a `DataTable` whose column names match the SQL UDT exactly. `AsTableValuedParameter` is a Dapper extension that wraps the `DataTable` with the SQL type name.

---

QUESTION:
How does your project handle Stored Procedures?

ANSWER:
The project uses SQL Server stored procedures exclusively for all database operations. No inline SQL is used.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/SqlConstant.cs`
```csharp
public const string CS_UpadateInvoiceEmailSentOn_OfflineInvoice = "CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing";
public const string SP_UpdateIsPushToOfflineInvoicingbacktoCS = "CS_UpdateIsPushToOfflineInvoicingbacktoCS";
```
- File: `OfflineInvoice-service/Common/common.cs`
```csharp
public const string CS_GetASNDataForOfflineInvoicing = "CS_GetASNDataForOfflineInvoicing";
public static string CS_UpdatePushASNDataOfflineInvoicing = "CS_UpdateASNDataForOfflineInvoices";
```
Stored procedures receive TVPs for bulk operations, return int codes (1 = success, 2 = not found).

FOLLOW-UP QUESTIONS:
1. What are the advantages of stored procedures over inline SQL?
2. How do Table-Valued Parameters work in SQL Server?
3. How does Dapper pass TVPs to stored procedures?

IMPORTANT FOR INTERVIEW:
Stored procedures provide: security (permissions at SP level), performance (cached execution plans), encapsulation (DB logic separate from app logic). TVPs allow passing a list/table as a single parameter, avoiding multiple round-trips or dynamic SQL with IN clauses.

---

QUESTION:
How is async/await used in your project?

ANSWER:
`async/await` enables non-blocking I/O, allowing the thread to be released while waiting for I/O operations (DB, HTTP).

PROJECT EXAMPLE:
- File: `OfflineInvoice-service/Worker.cs`
- Method: `ExecuteAsync(CancellationToken stoppingToken)`
```csharp
protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    while (!stoppingToken.IsCancellationRequested)
    {
        ScheduleService();
        await Task.Delay(
            Convert.ToInt32(TimeSpan.FromMinutes(Convert.ToInt16(Config.IntervalMinutes)).TotalMilliseconds),
            stoppingToken
        );
    }
}
```
`await Task.Delay(...)` is non-blocking — the thread is released to the thread pool during the wait.

FOLLOW-UP QUESTIONS:
1. What is the difference between Task.Delay and Thread.Sleep?
2. Why is `ScheduleService()` synchronous rather than async?
3. What happens if you throw an exception inside ExecuteAsync?

IMPORTANT FOR INTERVIEW:
`Task.Delay` is async and releases the thread. `Thread.Sleep` blocks the thread. In a Worker Service, `ExecuteAsync` should be async throughout. The current `ScheduleService()` is synchronous, which means the thread is blocked during all DB and HTTP operations. Making it async with `await` for DB calls and HTTP calls would be the ideal implementation. RestSharp supports `ExecuteAsync` which was not used here.

---

QUESTION:
How is exception handling implemented in your project?

ANSWER:
The project uses try-catch blocks at multiple layers — controller, repository, and service classes.

PROJECT EXAMPLE:
- **Controller level** (`OfflineInvoiceASNController.cs`):
```csharp
catch (Exception ex)
{
    _logger.Error(ex, "PostASNDataForOfflineInvoice error");
    return StatusCode(400, "Request Body is not correct");
}
```
- **Repository level** (`AsnRepository.cs`):
```csharp
catch (SqlException ex)
{
    _logger.Error(ex, $"UpdateInvoiceASNdata SQL error. MembershipID={...}, SP={...}");
}
catch (Exception ex)
{
    _logger.Error(ex, $"UpdateInvoiceASNdata error. MembershipID={...}");
}
```
SQL exceptions are caught separately from general exceptions for better diagnostics. Returns `0` on error (not re-thrown).

FOLLOW-UP QUESTIONS:
1. Why catch SqlException separately from Exception?
2. What is the issue with catching exceptions in the repository and returning 0 silently?
3. How would you implement a global exception handler in ASP.NET Core?

IMPORTANT FOR INTERVIEW:
The current approach swallows exceptions in the repository (returns 0) rather than re-throwing. The controller catches this 0 as a generic DB error (returns 400) without knowing the root cause. Best practice: re-throw from the repository and use middleware-level exception handling (`UseExceptionHandler`) or a global filter to return consistent error responses. This project currently does not implement global exception middleware.

---

QUESTION:
How is configuration management done in this project?

ANSWER:
Configuration is read from `appsettings.json` using ASP.NET Core's `IConfiguration` and mapped into static `Config` classes.

PROJECT EXAMPLE:
- **API** (`OfflineInvoice-API/OfflineInvoicingAPI/Config.cs`):
```csharp
public static class Config {
    public static void Initialize(IConfiguration configuration) {
        JWTAuthenticationKey = Configuration["JWT:JWTAuthenticationKey"];
        AllowedClientUrls = Configuration["AllowedClientUrls"];
        ConnectionString = Configuration["Settings:ConnectionString"];
    }
}
```
- **Service** (`OfflineInvoice-service/Config.cs`):
```csharp
Config.Initialize(configuration); // called in Program.Main()
// Reads: ConnectionString, IntervalMinutes, ServerLocation, API URLs
```
- Environment variables also used:
```csharp
Environment.SetEnvironmentVariable("ConnectionString", Configuration["Settings:ConnectionString"]);
// Retrieved later: Environment.GetEnvironmentVariable("ConnectionString")
Environment.SetEnvironmentVariable("AuthToken", authdata.Token);
```

FOLLOW-UP QUESTIONS:
1. Why use both static Config class and Environment.SetEnvironmentVariable?
2. What is the risk of storing connection strings in appsettings.json?
3. How would you use the Options pattern instead?

IMPORTANT FOR INTERVIEW:
Using static classes for configuration is an anti-pattern in DI-first .NET Core — it makes testing hard. The Options pattern (`IOptions<T>`) is preferred. Also, storing credentials (DB connection strings, JWT keys, API passwords) in `appsettings.json` is a security risk in source control — use Azure Key Vault, environment variables, or .NET User Secrets (`dotnet user-secrets`) for local development.

---

QUESTION:
How is the BackgroundService pattern used in your project?

ANSWER:
`BackgroundService` is an abstract base class in .NET that implements `IHostedService`. You override `ExecuteAsync` to run long-running tasks.

PROJECT EXAMPLE:
- File: `OfflineInvoice-service/Worker.cs`
- Class: `Worker : BackgroundService`
```csharp
protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    while (!stoppingToken.IsCancellationRequested)
    {
        ScheduleService(); // does DB reads + external API calls
        await Task.Delay(TimeSpan.FromMinutes(IntervalMinutes).TotalMilliseconds, stoppingToken);
    }
}
```
Registered in `Program.cs`:
```csharp
services.AddHostedService<Worker>();
```
The service runs every 60 minutes (from `Settings:IntervalMinutes` in appsettings.json).

FOLLOW-UP QUESTIONS:
1. What is the difference between IHostedService and BackgroundService?
2. How does CancellationToken.IsCancellationRequested work during app shutdown?
3. What happens if ExecuteAsync throws an unhandled exception?

IMPORTANT FOR INTERVIEW:
`BackgroundService` provides a default `StartAsync` and `StopAsync` that manage the `CancellationTokenSource`. If `ExecuteAsync` throws, the host catches it and logs it, but the service stops. For resilience, wrap the inner loop body in try-catch (which this project does via `ScheduleService()`).

---

QUESTION:
How does the project handle AES Encryption and Decryption?

ANSWER:
The `CSCrypter` project (class library) provides AES-256 encryption and decryption for PII fields stored encrypted in the database.

PROJECT EXAMPLE:
- File: `CSCrypter/Crypter.cs`
- Class: `Crypter.Operations` (static)
- Key: Hardcoded `"Cr1m$0n&eCuR3k3y!5@4#3$2%1^0&9*8"` (padded to 32 bytes for AES-256)
- IV: Zero-filled 16-byte array (fixed IV)
```csharp
public static string DecryptAES(string encryptedText) {
    byte[] iv = new byte[16]; // fixed zero IV
    byte[] keyBytes = Encoding.UTF8.GetBytes(AESEncryptionKey.PadRight(32));
    using (Aes aes = Aes.Create()) {
        aes.Key = keyBytes; aes.IV = iv;
        ICryptoTransform decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
        // MemoryStream + CryptoStream → Base64 decode + decrypt
    }
}
```
Used in `AsnInvoiceDataDAO.GetASNInvoiceData()`:
```csharp
asninvoice.PayerName = string.Join(" ", encryptedSegments.Select(s => Crypter.Operations.DecryptAES(s)));
asninvoice.OrgMonthlyEmailTo = Crypter.Operations.DecryptAES(asninvoice.OrgMonthlyEmailTo);
client.FirstName = propertiesToDecrypt[0]; // after DecryptAES
```
Also handles XML address format: `CrypterXmlAddressEncryptDecryptSplitter` parses XML, decrypts each field.

FOLLOW-UP QUESTIONS:
1. What is the security risk of a fixed (zero) IV in AES-CBC?
2. Why is the key hardcoded and what is the better approach?
3. What is the difference between AES-CBC and AES-GCM?

IMPORTANT FOR INTERVIEW:
Fixed IV (all zeros) is a known security weakness — same plaintext always produces same ciphertext, defeating the purpose of the IV. AES should use a random IV per encryption, stored alongside the ciphertext. The hardcoded key in source code is also a security risk — keys should be in a key vault or environment variable, not in version control.

---

QUESTION:
How does the project use RestSharp for HTTP communication?

ANSWER:
The Worker Service uses RestSharp (v111.2.0) to call external Odoo APIs for pushing ASN invoice and client data.

PROJECT EXAMPLE:
- File: `OfflineInvoice-service/APIOperation/APIOperation.cs`
- Class: `ApiOperation`
```csharp
var options = new RestClientOptions() { Timeout = TimeSpan.FromMilliseconds(120000) };
RestClient restClient = new RestClient(options);
RestRequest request = new RestRequest(sendUrl, Method.Post);
request.AddHeader("Content-Type", "application/json");
request.AddHeader("Authorization", authToken);
request.AddParameter("application/json", body, ParameterType.RequestBody);
RestResponse response = restClient.Execute(request);
```
- Session expiry handling:
```csharp
if (data.error != null && data.error.code == 100) {
    authToken = AuthorizationData(); // re-authenticate
    PostASNInvoiceRequest(asnjson, sendUrl, authToken); // recursive retry
}
```

FOLLOW-UP QUESTIONS:
1. What is the risk of recursive retry without a depth limit?
2. How would you implement IHttpClientFactory instead of RestSharp here?
3. What is connection pooling and why should you reuse HttpClient instances?

IMPORTANT FOR INTERVIEW:
The recursive retry on session expiry (error code 100) has no base case limit — it could recurse infinitely if re-authentication also fails. Add a retry counter. Also, creating `new RestClient()` per call bypasses connection pooling. Best practice: use `IHttpClientFactory` (registered as a singleton) which manages `HttpClient` instances with proper connection pool reuse, preventing socket exhaustion.

---

QUESTION:
How does the project implement the Interface vs Abstract Class design choice?

ANSWER:
The project exclusively uses interfaces for abstraction, with no abstract classes.

PROJECT EXAMPLE:
- `IOfflineInvoiceASNData` (API Contracts) — defines `UpdateInvoiceASNdata` and `PushOfflinedatabacktoCS`
- `IAPIOperation` (Service Contracts) — defines `GetCookiesForAuthorization`, `PostASNInvoiceRequest`, `PostClientDataRequest`

Both interfaces are injected via constructor DI and resolved to concrete implementations at runtime.

FOLLOW-UP QUESTIONS:
1. When would you choose an abstract class over an interface?
2. Can you implement multiple interfaces in C#?
3. What is the default interface method feature introduced in C# 8?

IMPORTANT FOR INTERVIEW:
Interface vs Abstract Class: Use interfaces when you need to define a contract that multiple unrelated classes can implement (as done here). Use abstract classes when you have common implementation to share across related classes. In .NET, a class can implement multiple interfaces but only inherit from one abstract class. C# 8+ allows default implementations in interfaces.

---

QUESTION:
How does this project demonstrate SOLID principles?

ANSWER:
- **S (Single Responsibility):** `ApiOperation` handles only HTTP communication; `AsnInvoiceDataDAO` handles only DB access; `OfflineInvoiceASNdatapush_service` handles orchestration.
- **O (Open/Closed):** `IAPIOperation` and `IOfflineInvoiceASNData` allow new implementations without modifying existing code.
- **L (Liskov Substitution):** `IOfflineInvoiceASNDataRepository` satisfies `IOfflineInvoiceASNData` contract fully.
- **I (Interface Segregation):** `IAPIOperation` has only 3 focused methods; `IOfflineInvoiceASNData` has only 2.
- **D (Dependency Inversion):** Controllers depend on `IOfflineInvoiceASNData` (abstraction), not `IOfflineInvoiceASNDataRepository` (concrete).

FOLLOW-UP QUESTIONS:
1. Where does this project violate SOLID? (Hint: Worker directly instantiates OfflineInvoiceASNdatapush_service)
2. How would you refactor Worker.cs to better follow DI?
3. What is the violation in Program.cs calling AuthorizationData() after Build().Run()?

IMPORTANT FOR INTERVIEW:
`Worker.cs` (line 20): `_prg = new OfflineInvoiceASNdatapush_service(_iAPIOperation)` — direct instantiation instead of injection violates DIP. `OfflineInvoiceASNdatapush_service` should be registered in DI and injected. Also, `Program.AuthorizationData()` after `Build().Run()` is dead code — `Run()` blocks until shutdown, so the line never executes.

---

QUESTION:
How does the Generic DataTable Extension Method work in your project?

ANSWER:
A generic extension method converts `List<T>` to `DataTable` using reflection, used to prepare TVPs for stored procedures.

PROJECT EXAMPLE:
- File: `OfflineInvoice-service/Helper/DataTableHelper.cs`
- Class: `DataTableHelper` (static)
```csharp
public static DataTable ToDataTable<T>(this List<T> iList)
{
    DataTable dataTable = new DataTable();
    PropertyDescriptorCollection props = TypeDescriptor.GetProperties(typeof(T));
    // Add columns based on T's properties
    foreach (T item in iList) {
        // Add row with values
    }
    return dataTable;
}
```
Usage in `AsnInvoiceDataDAO`:
```csharp
AssignmentList = pushedAssignmentList.ToDataTable(); // List<PushedAssignmentList> → DataTable
param.Add("@PushedAssignments", AssignmentList.AsTableValuedParameter(SPName.AssignmentListTableType));
```

FOLLOW-UP QUESTIONS:
1. What is the difference between reflection and TypeDescriptor?
2. Why does the code handle Nullable<> types separately?
3. What happens if T has properties that don't match the TVP column names?

IMPORTANT FOR INTERVIEW:
`TypeDescriptor.GetProperties` is slightly slower than direct property access but useful for dynamic column building. The Nullable unwrapping (`Nullable.GetUnderlyingType`) is necessary because `DataTable` doesn't support nullable column types natively — you use the underlying type and allow `DBNull.Value` for nulls.

---

QUESTION:
How is Health Check implemented in this project?

ANSWER:
A basic health check endpoint is registered and available at `/health`.

PROJECT EXAMPLE:
- File: `Startup.cs`
- ConfigureServices: `services.AddHealthChecks()`
- Configure: `endpoints.MapHealthChecks("/health")`

The health check returns `200 Healthy` when the API is running. No custom health checks (e.g., DB connectivity check) are implemented.

FOLLOW-UP QUESTIONS:
1. How would you add a database health check?
2. What is the difference between liveness and readiness probes in Kubernetes?
3. What response format does the default health check return?

IMPORTANT FOR INTERVIEW:
The project implements only the default runtime health check. For production, add: `services.AddHealthChecks().AddSqlServer(connectionString)` to check DB connectivity. The `/health` endpoint returns `{"status": "Healthy"}` or `{"status": "Unhealthy"}`. In Kubernetes, liveness = "is the app running?" (restart if not), readiness = "can it serve traffic?" (remove from LB if not).

---

QUESTION:
How does the project demonstrate the use of LINQ?

ANSWER:
LINQ is used in multiple places for collection operations.

PROJECT EXAMPLE:
- `FirstOrDefault` for lookup: `asn.clientDataModels.FirstOrDefault(x => x.Username == asnInvoiceData.UserName && x.MembershipId == asnInvoiceData.MembershipId)` (`OfflineInvoiceASNdatapush_service.cs` line 51)
- `Select` with lambda: `separator.Select(name => DecryptAES(name))` (`Crypter.cs` line 138)
- `ToList()`: converting Dapper query results to `List<T>`
- `Count()` on list: `pushedAssignmentlist.Count()`
- `Contains()` for whitelist check: `whitelistFields.Contains(fieldName.ToLower())`
- `string.Join` + LINQ Select for bulk decrypt: `string.Join(" ", encryptedSegments.Select(s => Crypter.Operations.DecryptAES(s)))`

FOLLOW-UP QUESTIONS:
1. What is the difference between IQueryable and IEnumerable?
2. What is deferred execution in LINQ?
3. When would you use LINQ to SQL vs Dapper?

IMPORTANT FOR INTERVIEW:
`IQueryable` builds an expression tree and translates to SQL — used with EF Core. `IEnumerable` runs in-memory — used after Dapper results are already fetched. The project uses only `IEnumerable`-based LINQ because Dapper returns fully materialized lists. This is correct since SQL execution happens inside the stored procedures.

---

QUESTION:
How does the project handle Models / DTOs?

ANSWER:
The project uses plain C# classes as data models (DTOs), with no AutoMapper.

PROJECT EXAMPLE:
- File: `OfflineInvoice-API/OfflineInvoicingAPI/Models/AssignmentDataModel.cs`
```csharp
public class OfflineInvoiceASNdata {
    public List<OfflineInvoiceASNdatalist> offlineInvoiceASNdatalist { get; set; }
    public string? MembershipID { get; set; }
    public int status { get; set; }
    public DateTime InvoiceEmailSentOn { get; set; }
    public decimal? InvoiceAmount { get; set; }
}
```
- `ASNInvoiceJSON` and `GetClientDetailsJSON` wrap models for Odoo JSON-RPC format using Newtonsoft.Json `[JsonProperty]` attributes.

FOLLOW-UP QUESTIONS:
1. What is AutoMapper and when would you use it here?
2. What is the difference between a Model and a DTO?
3. Should models have validation attributes? Where would they be applied?

IMPORTANT FOR INTERVIEW:
This project currently does not use AutoMapper. The models serve as both DB-mapped classes and API request/response classes, which violates separation of concerns. Ideally: separate DB models from API DTOs, use AutoMapper to map between them. For input validation, add `[Required]`, `[Range]`, `[MaxLength]` attributes and check `ModelState.IsValid` in the controller.

---

QUESTION:
How does the Startup.cs (or Program.cs) differ between the API and the Worker Service?

ANSWER:
The API uses the classic Startup class separation; the Worker Service uses the newer minimal host builder approach.

PROJECT EXAMPLE:
- **API** (`OfflineInvoicingAPI/Program.cs`):
  - Uses `CreateHostBuilder` + `UseStartup<Startup>()` — classic pattern
  - Configures Serilog, Elasticsearch sink, URL binding
  - `Startup.cs` handles `ConfigureServices` and `Configure` separately

- **Service** (`OfflineInvoice-service/Program.cs`):
  - Uses `Host.CreateDefaultBuilder` without Startup class
  - Registers `Worker` as `AddHostedService`
  - Registers `ApiOperation` as `AddSingleton<IAPIOperation, ApiOperation>`
  - Uses `Microsoft.NET.Sdk.Worker` (not Web SDK)

FOLLOW-UP QUESTIONS:
1. What changed in .NET 6 minimal hosting model vs classic Startup?
2. What is the difference between Microsoft.NET.Sdk and Microsoft.NET.Sdk.Web and Microsoft.NET.Sdk.Worker?
3. Why doesn't the Worker Service need UseRouting or UseAuthentication?

---

QUESTION:
How does the project use Environment Variables?

ANSWER:
Environment variables are used as a runtime store for sensitive/shared values (connection string and auth token).

PROJECT EXAMPLE:
- API (`Startup.cs` line 65):
```csharp
Environment.SetEnvironmentVariable("ConnectionString", Configuration["Settings:ConnectionString"]);
```
- Service (read back):
```csharp
connectionString = Environment.GetEnvironmentVariable("ConnectionString");
```
- Auth token lifecycle:
```csharp
Environment.SetEnvironmentVariable("AuthToken", authdata.Token); // after auth
authToken = Environment.GetEnvironmentVariable("AuthToken"); // on use
```

FOLLOW-UP QUESTIONS:
1. What is the scope of Environment.SetEnvironmentVariable in .NET? (Process-level)
2. Why is using Environment variables for auth tokens risky?
3. What is the preferred alternative for secrets in production?

IMPORTANT FOR INTERVIEW:
`Environment.SetEnvironmentVariable` sets process-level variables, visible only within the same process. This is fine for the auth token within the Worker Service. However, the token is stored in plaintext in a process environment variable, which is less secure than using `IMemoryCache` or a proper token store. For production secrets, use Azure Key Vault, AWS Secrets Manager, or Docker secrets.

---

QUESTION:
How does the project handle Static vs Const vs Readonly?

ANSWER:
The project uses all three in different contexts.

PROJECT EXAMPLE:
- **const** (compile-time constant, implicitly static):
  ```csharp
  // SqlConstant.cs
  public const string CS_UpadateInvoiceEmailSentOn_OfflineInvoice = "CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing";
  // Crypter.cs
  private static string AESEncryptionKey = "Cr1m$0n&eCuR3k3y!5@4#3$2%1^0&9*8";
  ```
- **static** (shared across instances):
  ```csharp
  private static NLog.Logger _logger = NLog.LogManager.GetCurrentClassLogger(); // all repositories
  private static readonly JsonSerializerOptions LogJsonOptions = new() {...}; // Controller
  ```
- **readonly** (set once, at declaration or constructor):
  ```csharp
  private static readonly JsonSerializerOptions LogJsonOptions = new() { ... }; // Controller.cs line 17
  ```

FOLLOW-UP QUESTIONS:
1. Why is AESEncryptionKey `static` and not `const`?
2. What is the difference between `static readonly` and `const`?
3. Can a `const` field hold a reference type?

IMPORTANT FOR INTERVIEW:
`const` is evaluated at compile time, inlined into the calling assembly — changing it requires recompiling all referencing assemblies. `static readonly` is evaluated at runtime (once) — safe for reference types or values computed at startup. `AESEncryptionKey` uses `static` (not const) which is slightly odd since it never changes — it could be `const` as it is a string literal, but `static readonly` would also be appropriate. `readonly` alone (without static) means instance-level once-set (constructor-only).

---

## 3. DATABASE / SQL — QUESTIONS & ANSWERS

---

QUESTION:
How are Stored Procedures called in this project?

ANSWER:
All DB operations use stored procedures via Dapper with `CommandType.StoredProcedure`. No inline SQL is used.

PROJECT EXAMPLE:
Stored procedures used:
| Name | Purpose | Project |
|---|---|---|
| `CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing` | Update invoice sent date + status | API |
| `CS_UpdateIsPushToOfflineInvoicingbacktoCS` | Revert assignment to CS | API |
| `CS_GetASNDataForOfflineInvoicing` | Fetch pending ASN + client data | Service |
| `CS_UpdateASNDataForOfflineInvoices` | Mark ASN as pushed | Service |

FOLLOW-UP QUESTIONS:
1. How do you pass a list to a stored procedure without TVP?
2. What is the benefit of stored procedures over raw SQL in terms of security?
3. How do you debug a stored procedure call in production?

---

QUESTION:
How does the project use Table-Valued Parameters (TVPs)?

ANSWER:
TVPs allow passing a table (list of rows) as a single stored procedure parameter, avoiding looping and multiple round trips.

PROJECT EXAMPLE:
- File: `AsnRepository.cs`
```csharp
DataTable assignmentTable = new DataTable();
assignmentTable.Columns.Add("AssignmentID", typeof(int));
assignmentTable.Columns.Add("Asnnumber", typeof(string));
assignmentTable.Columns.Add("InvoiceNumber", typeof(string));
assignmentTable.Columns.Add("InvoiceAmount", typeof(decimal));
assignmentTable.Columns.Add("IsMonthly", typeof(bool));
foreach (var assignment in offlineInvoiceASNdata.offlineInvoiceASNdatalist)
    assignmentTable.Rows.Add(assignment.AssignmentID, assignment.Asnnumber, ...);
param.Add("@Assignments", assignmentTable.AsTableValuedParameter("dbo.UpdateOfflineInvoiceASNListTableType"));
```
The SQL UDT (`UpdateOfflineInvoiceASNListTableType`) must exist in the database with matching column definitions.

FOLLOW-UP QUESTIONS:
1. How do you define a User-Defined Table Type in SQL Server?
2. What happens if the DataTable column order doesn't match the TVP column order?
3. Can you use TVPs with non-stored-procedure queries?

---

QUESTION:
How does QueryMultiple work in this project?

ANSWER:
`QueryMultiple` executes a stored procedure that returns multiple result sets in a single DB round trip.

PROJECT EXAMPLE:
- File: `OfflineInvoiceAsnDataRepository.cs`
```csharp
var lst_getAsnInvoiceData = con.QueryMultiple(
    SPName.CS_GetASNDataForOfflineInvoicing, parameters, commandType: CommandType.StoredProcedure
);
var listasndetails = lst_getAsnInvoiceData.Read<ASNInvoiceDataModel>().ToList(); // first result set
var listclientdetails = lst_getAsnInvoiceData.Read<ClientDataModel>().ToList();  // second result set
```
The SP `CS_GetASNDataForOfflineInvoicing` does two SELECT statements, returning ASN data and client data together.

FOLLOW-UP QUESTIONS:
1. Why use QueryMultiple instead of two separate queries?
2. What happens if you call Read() more times than the SP returns result sets?
3. How does the SP produce two result sets?

---

QUESTION:
How does the project handle NULL values in SQL parameters?

ANSWER:
NULL values are handled explicitly when building TVP rows using helper methods and `DBNull.Value`.

PROJECT EXAMPLE:
- File: `AsnRepository.cs`
```csharp
private static object ToIsMonthlyBit(string? isMonthlyClient) {
    if (string.IsNullOrWhiteSpace(isMonthlyClient)) return DBNull.Value;
    return isMonthlyClient.Trim().Equals("yes", StringComparison.OrdinalIgnoreCase);
}
private static object ToTvpInvoiceNumber(string? invoiceNumber) {
    if (string.IsNullOrWhiteSpace(invoiceNumber)) return DBNull.Value;
    return invoiceNumber.Trim();
}
```
Usage:
```csharp
assignmentTable.Rows.Add(assignment.AssignmentID, assignment.Asnnumber ?? (object)DBNull.Value, ToTvpInvoiceNumber(assignment.InvoiceNumber), ...);
```

FOLLOW-UP QUESTIONS:
1. What is the difference between `null` in C# and `DBNull.Value` in ADO.NET?
2. Why does the `??` operator use `(object)DBNull.Value` instead of just `DBNull.Value`?
3. What SQL type does `IsMonthly` map to when stored as bool in a DataTable?

---

## 4. ANGULAR — NOT IMPLEMENTED

This project has no Angular frontend. For Angular interview questions, mention:
- "This project is a backend-only solution — the API is consumed by an external Odoo frontend and other microservices."
- If Angular is mentioned, you can discuss it theoretically, but be transparent that your hands-on experience with Angular is from other projects.

This project currently does not implement the following Angular concepts:
- Components, Modules, Routing, Lazy Loading
- Reactive/Template-driven Forms
- RxJS / Observables
- HTTP Interceptors, Guards
- State Management, Change Detection, JIT vs AOT

Ideal implementation would use Angular with `HttpClient` + interceptors for JWT token attachment, route guards for auth protection, reactive forms for invoice data entry, and lazy-loaded feature modules.

---

## 5. TOP 30 INTERVIEW QUESTIONS MOST RELEVANT TO THIS PROJECT

1. Walk me through the architecture of your Offline Invoice project — how do the three components interact?
2. How does the Worker Service authenticate with the external Odoo API and how does it handle session expiry?
3. Why did you choose Dapper over Entity Framework for this project?
4. Explain how Table-Valued Parameters work and why you used them here.
5. What is the role of the `CSCrypter` library and why is AES decryption done in the application layer instead of the DB layer?
6. How is JWT configured in the API — what parameters are validated and which are skipped?
7. Why does your project use both NLog and Serilog? What does each provide?
8. Explain the middleware pipeline order in your API and why the order matters.
9. What is the difference between AddTransient and AddSingleton, and which did you use where and why?
10. How does `ExecuteAsync` in `Worker.cs` prevent blocking the thread while waiting between runs?
11. The `Program.AuthorizationData()` call in `OfflineInvoice-service/Program.cs` after `Build().Run()` — does it ever execute? Why?
12. `Worker.cs` calls `new OfflineInvoiceASNdatapush_service(...)` directly. What is wrong with this and how would you fix it?
13. The CORS configuration calls both `WithOrigins(...)` and `AllowAnyOrigin()`. What does this actually do?
14. Why is the fixed zero IV in AES encryption a security risk?
15. How does `QueryMultiple` work and what performance benefit does it provide over two separate queries?
16. Why is the connection string stored in both `appsettings.json` and `Environment` variables?
17. How would you add input validation to the `PostASNDataForOfflineInvoice` endpoint?
18. The recursive retry on session expiry (error code 100) in `ApiOperation.cs` — what risk does it introduce?
19. How does `ToDataTable<T>()` use generics and reflection to convert a list to a DataTable?
20. The concrete class `IOfflineInvoiceASNDataRepository` starts with "I" like an interface. How would you rename it and why?
21. How does API versioning work in this project and how would you add a v2 endpoint?
22. What stored procedures does the API call and what does each return?
23. How does the `DataTableHelper.ToDataTable` handle nullable types and why is that necessary?
24. How would you implement a retry policy (e.g., Polly) in the RestSharp calls?
25. How are encryption keys managed in this project and what is the recommended improvement?
26. What is `AsTableValuedParameter` and how does Dapper pass it to SQL Server?
27. How would you make `ScheduleService()` fully async?
28. How does the `OfflineInvoiceASNdatapush_service` determine which API URL to call — ASN vs Client?
29. What health checks exist and how would you add a database connectivity check?
30. How would you containerize this Worker Service using Docker?

---

## 6. MISSING BEST PRACTICES

### Security
- **Secrets in config:** JWT key, DB connection string, AES encryption key, and Odoo credentials are all in `appsettings.json`. Use Azure Key Vault or environment variables.
- **Fixed IV in AES:** Use a random IV per encryption (store with ciphertext). Current approach is deterministic and weakens encryption.
- **JWT validation:** `ValidateIssuer = false` and `ValidateAudience = false` should be enabled in production.
- **CORS misconfiguration:** `AllowAnyOrigin()` overrides `WithOrigins()`. Restrict to specific origins.

### Architecture
- **Global exception middleware:** No `UseExceptionHandler` or global exception filter. Errors are caught per-method with inconsistent handling.
- **No AutoMapper:** Models serve as both DB entities and API DTOs — violates separation of concerns.
- **No input validation:** `OfflineInvoiceASNdata` has no `[Required]`, `[Range]`, or `ModelState.IsValid` checks beyond null checks.
- **Direct instantiation in Worker:** `new OfflineInvoiceASNdatapush_service(...)` should be DI-injected.
- **Dead code:** `Program.AuthorizationData()` after `Build().Run()` never executes.
- **Naming:** `IOfflineInvoiceASNDataRepository` (concrete class) should be `OfflineInvoiceASNDataRepository`.

### Async
- **Synchronous HTTP calls:** `restClient.Execute()` should be `await restClient.ExecuteAsync()`.
- **Synchronous DB access:** Dapper's `QuerySingle` should be `await QuerySingleAsync`.
- **`ScheduleService()` is sync** inside an `async` method — blocks thread.

### Observability
- **Dual logging frameworks:** NLog + Serilog adds complexity. Pick one.
- **No distributed tracing:** No correlation ID (request ID) propagation between API → DB logs.
- **No metrics:** No Prometheus/Application Insights metrics.

### Testing
- **No unit tests** in any project. No test project in the solution.
- **Static Config class** makes unit testing hard (can't mock configuration).

### Resilience
- **No Polly retry policy** for RestSharp HTTP calls.
- **Recursive retry** on session expiry (no depth limit — potential stack overflow).
- **No circuit breaker** for external API calls.

---

## 7. REAL-TIME SCENARIO QUESTIONS

SCENARIO 1:
The Worker Service runs fine for a week, then suddenly stops processing ASNs. The logs show "Session Expired" for every request. What would you investigate?

→ The `AuthToken` environment variable stores the Odoo session token. If the token expires and re-authentication fails (e.g., password change, network issue), `GetCookiesForAuthorization()` returns an empty `AuthorizationData`. The recursive retry in `PostASNInvoiceRequest` will keep retrying without bound. Check: (1) Odoo credentials in config, (2) `InvoiceSessionAPIUrl` reachability, (3) whether the infinite recursion triggered a stack overflow.

SCENARIO 2:
The API starts returning 400 for all requests even with valid data. Investigation reveals `result = 0` from the DB call. What could cause this?

→ The stored procedure `CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing` returned 0 (not 1 or 2). Could be: (1) DB connection issue (exception caught, returns 0), (2) SP logic returned 0 for unhandled case, (3) TVP data mismatch (column count/type). Check NLog for SqlException messages before the 0 result. The repository swallows exceptions and returns 0 — this makes root cause analysis hard.

SCENARIO 3:
A new field `PRNNumber` was added to `ASNInvoiceDataModel`. How would you ensure it is passed to the Odoo API correctly?

→ Check `ASNInvoiceJSON` wrapper — it has `[JsonProperty("params")]` wrapping `ASNInvoiceDataModel`. Since `PRNNumber` is a public property with default Newtonsoft serialization, it will be included automatically. Verify the property name matches what Odoo expects (may need `[JsonProperty("prn_number")]`). For DB, verify `CS_GetASNDataForOfflineInvoicing` SP now returns this column and it maps to `PRNNumber` property. (This was added in commit `45b1703` — `CW-18655`.)

SCENARIO 4:
You need to add a new endpoint to the API that allows querying invoice status. How would you add it without breaking the v1 contract?

→ Add a new method to `IOfflineInvoiceASNData` interface (and its implementation). Add a new `[HttpGet]` action in `OfflineInvoiceASNDataController`. Since the route already includes `v{version:apiVersion}`, clients on v1 can call the new endpoint via `v1/`. If breaking changes are needed, register v2 in `AddApiVersioning` and add `[ApiVersion("2.0")]` to a new controller or action.

SCENARIO 5:
The DBA reports that `CS_GetASNDataForOfflineInvoicing` is causing table scans and slow performance during peak hours. How would you approach this?

→ (1) Check execution plan for missing indexes on `IsPushedToOfflineInvoicing` or `MembershipId` columns. (2) The SP fetches unbounded rows — add pagination or TOP N with status filter. (3) Check if the Worker runs hourly during peak hours — consider an off-peak schedule. (4) Verify statistics are updated. (5) Consider read replicas or caching if the dataset is large and doesn't change frequently between intervals.

---

## 8. HR + MANAGER ROUND QUESTIONS

Q: Tell me about your Offline Invoice project.
A: "I built a system to automate pushing invoice data from our internal database to an external Odoo invoicing platform. It has three components: a .NET 6 Web API that receives invoice submission confirmations from internal systems, a .NET 6 Worker Service that runs every 60 minutes to fetch pending invoices from the DB and push them to Odoo via REST APIs, and a shared class library (CSCrypter) that handles AES decryption of PII fields stored encrypted in the database. The system handles authentication with Odoo, session management, and bulk data transfer using TVPs for efficient DB operations."

Q: What was the biggest technical challenge in this project?
A: "Handling PII data securely — client names, email addresses, and addresses are stored AES-encrypted in the database. We had to decrypt them before sending to Odoo, handling edge cases like space-delimited names (each word encrypted separately) and XML-formatted addresses. Another challenge was session management with Odoo — tokens expire, so we implemented automatic re-authentication on expiry detection."

Q: If you were to rebuild this project, what would you do differently?
A: "I would: (1) Move secrets to a vault instead of config files, (2) Use the Options pattern instead of a static Config class, (3) Make the Worker fully async with `await` for DB and HTTP calls, (4) Add Polly for retry/circuit breaker on external API calls, (5) Add unit tests with mock interfaces, (6) Fix the AES IV to be random per encryption, (7) Use a single logging framework instead of both NLog and Serilog."

Q: How do you ensure the system is reliable?
A: "The Worker Service has try-catch at both the orchestration level and per-ASN level — so a failure for one ASN doesn't stop others. NLog logs all errors with context. The API returns specific status codes (400 for bad data vs internal error). Health check endpoint at `/health` allows monitoring. The service re-authenticates automatically on session expiry."

---

## 9. QUICK REVISION NOTES

### Architecture
- 3 components: API (port 5010) + Worker Service (runs every 60min) + CSCrypter (class library)
- Database: SQL Server `CIPLPROD` via `IDbConnection` + Dapper + Stored Procedures

### API Key Facts
- Route pattern: `offlineInvoice/v{version:apiVersion}/[controller]`
- Auth: JWT Bearer (HS256), key from appsettings `JWT:JWTAuthenticationKey`
- DI: `IOfflineInvoiceASNData` → `IOfflineInvoiceASNDataRepository` (Transient)
- Logging: NLog (file) + Serilog (Elasticsearch index: `OfflineInvoice-log-{date}`)
- Versioning: Default `1.0`, from `ApiVersion:DefaultVersion` config

### Service Key Facts
- BackgroundService → runs `ExecuteAsync` in loop with `Task.Delay`
- DI: `IAPIOperation` → `ApiOperation` (Singleton)
- HTTP client: RestSharp v111 with 120-second timeout
- Session: Odoo token stored in `Environment.SetEnvironmentVariable("AuthToken")`
- SP `CS_GetASNDataForOfflineInvoicing` returns 2 result sets → `QueryMultiple`

### Crypter Key Facts
- AES-256 (key padded to 32 bytes), zero IV (security gap)
- Handles: single fields, space-delimited names, XML address format
- `CrypterXmlAddressEncryptDecryptSplitter` → parses `/ClientAddress/MailingAddress`, City, Zip, State

### Stored Procedures
- API: `CS_UpadateInvoiceEmailSentOnFor_OfflineInvoicing`, `CS_UpdateIsPushToOfflineInvoicingbacktoCS`
- Service: `CS_GetASNDataForOfflineInvoicing`, `CS_UpdateASNDataForOfflineInvoices`
- TVP types: `dbo.UpdateOfflineInvoiceASNListTableType` (API), `dbo.OfflineInvoiceASNListTableType` (Service)

### Known Gaps to Mention Proactively
- No unit tests
- Secrets in config files
- Sync HTTP/DB calls (not awaited)
- Fixed IV in AES
- Recursive retry without depth limit
- Dead code in Program.cs (after Build().Run())
- Naming: `IOfflineInvoiceASNDataRepository` should not start with I

---

## 10. TOP 10 STRONGEST CONCEPTS DEMONSTRATED

1. **Repository Pattern with DI** — Clean separation via `IOfflineInvoiceASNData` / `IAPIOperation` interfaces resolved via DI container
2. **JWT Authentication** — Correctly configured middleware with `[Authorize]` attribute enforcement
3. **API Versioning** — URL segment versioning with dynamic default version from config
4. **Dapper with TVPs** — Efficient bulk SQL operations using Table-Valued Parameters and stored procedures
5. **BackgroundService / Worker Service** — Proper implementation of a long-running scheduled background task
6. **AES Encryption/Decryption** — Custom crypto library with multi-format support (single field, space-split, XML)
7. **Serilog + Elasticsearch Integration** — Structured centralized logging with machine name enrichment
8. **QueryMultiple** — Efficient fetching of multiple result sets in a single DB round trip
9. **Generic Extension Method (`ToDataTable<T>`)** — Reflection-based List-to-DataTable conversion for TVPs
10. **Configuration Management** — Multi-environment `appsettings.json` with `IConfiguration` and environment variable bridge

---

## 11. TOP 10 WEAK OR MISSING CONCEPTS

1. **No Unit Tests** — No test project, no Mocking (Moq), no test coverage
2. **Secrets Management** — Credentials, JWT keys, AES keys all in source-controlled config files
3. **Async/Await Throughout** — HTTP and DB calls are synchronous; `ScheduleService` blocks the thread
4. **AES IV Security** — Fixed zero IV is a cryptographic weakness; should use random IV per encryption
5. **Global Exception Handling** — No middleware-level error handler; exceptions handled inconsistently
6. **No Angular Frontend** — Project is backend-only; no frontend experience demonstrated here
7. **Polly / Resilience** — No retry policy, circuit breaker, or timeout policy for external API calls
8. **AutoMapper / DTO Separation** — No mapping library; models double as DB and API DTOs
9. **Input Validation** — No data annotations (`[Required]`, `[Range]`) or FluentValidation
10. **No Entity Framework** — Database First or Code First EF concepts are not present; all DB is raw ADO.NET + Dapper

---
*End of Interview Preparation Guide*
