# Interview Preparation — Payment Wallet Verification Project

> Generated from: `Payment-Walletverification_revamp`
> Stack: .NET Core 8.0 (ASP.NET Web API) + Angular 16 + SQL Server
> Target: 3–5 years experienced developer interviews

---

# PROJECT ARCHITECTURE SUMMARY

## Complete Architecture Flow

```
User Browser (Angular 16)
    │
    ├─ OIDC Authentication (angular-auth-oidc-client)
    │       └─ Redirects to internal OIDC server → returns id_token + access_token
    │
    ├─ HTTP Interceptor (TokenInterceptor)
    │       └─ Attaches JWT Bearer token to every API request
    │
    ├─ REST API calls → ASP.NET Core 8.0 Web API
    │       ├─ JWT Auth Middleware validates token
    │       ├─ Controller routes request
    │       ├─ Repository pattern handles data access
    │       └─ SqlClient executes Stored Procedures on SQL Server
    │
    └─ SQL Server (IPLPROD_UAT9)
            └─ All CRUD via Stored Procedures (CS_Wallet_*, PM_GetWallet*)
```

## Frontend to Backend Request Lifecycle

1. Component calls a `Service` method (e.g., `PaymentVerificationService.getListOfPaymentVar()`)
2. `HttpClient` creates an outgoing HTTP request
3. `TokenInterceptor` intercepts → checks `sessionStorage` for a valid JWT → fetches new one from `TokenApiService` if expired
4. `Authorization: Bearer <token>` header is attached
5. Request hits `WalletVerificationController` at `/api/wallet/*`
6. ASP.NET middleware validates JWT → request reaches the Controller action
7. Controller calls `IWalletVerificationRepository` method
8. Repository opens `SqlConnection`, executes stored procedure, maps `SqlDataReader` to model
9. Response flows back → JSON serialized → Angular deserializes → Component updates UI

## Authentication Flow

1. User visits `/VerifyWalletDeposits`
2. `AuthorizationGuard.canActivate()` checks `oidcSecurityService.isAuthenticated$`
3. Not authenticated → navigates to `/autologin`
4. `AutoLoginComponent` clears stale OIDC storage → calls `oidcSecurityService.authorize()`
5. Browser redirected to OIDC server (`http://192.168.0.17:347` for dev)
6. User logs in → OIDC server redirects back with tokens in URL hash (`#id_token=...`)
7. `AppComponent` detects hash → calls `oidcSecurityService.checkAuth()`
8. User data from `userData$` deserialized into `UserInfo` model via `json2typescript`
9. `UserInfoService` (BehaviorSubject) broadcasts user info to all components
10. User redirected to `/VerifyWalletDeposits`, data loads

## API Communication Flow

- **GET** `GetPMWalletVerificationData` → list of PM wallet statements (for matching)
- **POST** `WalletGetVerification` → pending/verified deposits per client
- **POST** `WalletUpdateVerifiedDetails` → mark a deposit as verified
- **POST** `WalletDeposit/Client/{id}` → insert initial transaction
- **GET** `GetDecrementalBalance/Client/{id}` → current wallet balance

## Database Interaction Flow

- Repository creates `SqlConnection` using connection string from `IConfiguration`
- `SqlCommand` with `CommandType.StoredProcedure`
- Input params via `SqlParameter` objects (prevents SQL injection)
- Output params capture stored procedure return values
- `SqlDataReader` iterates rows → mapped to C# model objects
- Connection closed in `finally` block

---

# .NET / .NET CORE CONCEPTS

---

QUESTION:
What is the MVC pattern and how does your project use it?

ANSWER:
MVC (Model-View-Controller) separates concerns into three layers: Model (data), View (presentation), Controller (request handling). In Web API projects, there is no View layer — the controller returns JSON, which the Angular frontend renders.

PROJECT EXAMPLE:
- File: `Controllers/WalletVerificationController.cs`
- Class: `WalletVerificationController : ControllerBase`
- Method: `WalletGetVerification([FromBody] VerificationDetailsResponse obj)`
- The Controller receives HTTP requests, delegates to `IWalletVerificationRepository`, and returns `Ok(result)` with JSON
- Models: `VerificationDetailsResponse`, `WalletCallResponse`, `PMWalletVerificationData` in `Models/`
- No View layer — Angular serves as the presentation tier

FOLLOW-UP QUESTIONS:
1. Why does a Web API controller inherit from `ControllerBase` instead of `Controller`?
2. What is `[ApiController]` attribute and what does it do automatically?
3. How does model binding work with `[FromBody]` vs `[FromQuery]`?

IMPORTANT FOR INTERVIEW:
`ControllerBase` has no view support (no `View()` method). `[ApiController]` enables automatic model validation, automatic 400 responses for invalid models, and binding source inference.

---

QUESTION:
How does the middleware pipeline work in your project?

ANSWER:
Middleware is a chain of components that process HTTP requests and responses. Each middleware can short-circuit the pipeline or pass the request to the next component.

PROJECT EXAMPLE:
- File: `Program.cs`
- Pipeline order (critical — order matters):
  ```csharp
  app.UseSerilogRequestLogging();
  app.UseCors("AllowAll");
  app.UseAuthentication();   // Must come before UseAuthorization
  app.UseAuthorization();
  app.MapControllers();
  app.MapHealthChecks("/health");
  ```
- CORS middleware allows cross-origin requests from Angular frontend
- Authentication middleware validates JWT Bearer tokens
- Authorization middleware enforces `[Authorize]` attributes on controllers
- Serilog middleware logs every HTTP request/response

FOLLOW-UP QUESTIONS:
1. What happens if you put `UseAuthorization` before `UseAuthentication`?
2. How would you write a custom middleware in this project?
3. What is short-circuit middleware and when would you use it?

IMPORTANT FOR INTERVIEW:
Order is everything. `UseAuthentication` must precede `UseAuthorization`. CORS must be early in the pipeline. If authentication middleware is missing but `[Authorize]` is on the controller, requests will receive 401 without any meaningful error.

---

QUESTION:
How is Dependency Injection configured in your project?

ANSWER:
DI is the built-in IoC container in ASP.NET Core. Services are registered in `Program.cs` and injected via constructors.

PROJECT EXAMPLE:
- File: `Program.cs`
  ```csharp
  builder.Services.AddScoped<IWalletVerificationRepository, WalletVerificationRepository>();
  builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)...
  builder.Services.AddSerilog();
  builder.Services.AddControllers();
  builder.Services.AddHealthChecks();
  ```
- File: `Controllers/WalletVerificationController.cs`
  ```csharp
  public WalletVerificationController(
      IWalletVerificationRepository walletVerificationRepository,
      ILogger<WalletVerificationController> logger,
      IConfiguration configuration)
  ```
- The controller never instantiates the repository — ASP.NET creates and injects it

FOLLOW-UP QUESTIONS:
1. What is the difference between AddScoped, AddSingleton, and AddTransient?
2. Why is `IWalletVerificationRepository` registered as Scoped rather than Singleton?
3. How would you inject `IConfiguration` into a static utility class?

IMPORTANT FOR INTERVIEW:
Scoped = one instance per HTTP request (correct for repository that holds a DB connection). Singleton = one for the app lifetime (dangerous with DbContext). Transient = new instance every time it's requested (fine for lightweight stateless services).

---

QUESTION:
What are service lifetimes and which did you use in this project?

ANSWER:
- **Transient**: New instance every injection. Good for stateless, lightweight services.
- **Scoped**: One instance per HTTP request. Good for repositories, DbContext.
- **Singleton**: One instance for application lifetime. Good for config, caches.

PROJECT EXAMPLE:
- `IWalletVerificationRepository` → **Scoped** (one per request, holds SQL connection scope)
- `ILogger<T>` → **Singleton** (built-in, thread-safe)
- `IConfiguration` → **Singleton** (reads from appsettings, immutable)
- `TokenInterceptor` in Angular → effectively **Singleton** (provided in AppModule root)

FOLLOW-UP QUESTIONS:
1. What is "captive dependency" and how does it cause bugs?
2. Can you inject a Scoped service into a Singleton? What happens?
3. How do you verify service lifetimes at runtime?

IMPORTANT FOR INTERVIEW:
Captive dependency = Singleton captures a Scoped service → the Scoped instance lives forever, defeating the purpose. ASP.NET Core throws an exception by default when this happens in development mode (`ValidateScopes`).

---

QUESTION:
How is JWT Authentication implemented in your project?

ANSWER:
JWT (JSON Web Token) is a stateless authentication mechanism. The server validates a signed token on every request without needing session storage.

PROJECT EXAMPLE:
- File: `Program.cs`
  ```csharp
  builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
      .AddJwtBearer(options => {
          options.TokenValidationParameters = new TokenValidationParameters {
              ValidateIssuerSigningKey = true,
              IssuerSigningKey = new SymmetricSecurityKey(
                  Encoding.ASCII.GetBytes(builder.Configuration["Jwt:Key"])),
              ValidateIssuer = false,
              ValidateAudience = false
          };
      });
  ```
- File: `appsettings.json` — Key: `95ba7edefb308827e28625d41bcc215c17cfee75e0605c1865d6240a8612c693`
- File: `Controllers/WalletVerificationController.cs` — `[Authorize]` attribute on the entire controller
- Angular: `TokenInterceptor` adds `Authorization: Bearer <token>` header
- Token fetched from `/SecurityToken/tokengenerator` endpoint by `TokenApiService`

FOLLOW-UP QUESTIONS:
1. Why does this project set `ValidateIssuer = false`? What are the security implications?
2. What is the difference between authentication and authorization?
3. How do you handle JWT token expiry in this project?

IMPORTANT FOR INTERVIEW:
`ValidateIssuer = false` and `ValidateAudience = false` means any valid signature passes — useful in internal microservice environments but risky if the token endpoint is exposed externally. The Angular `TokenInterceptor` handles token refresh by checking `expires_in` from sessionStorage before each request.

---

QUESTION:
How does routing work in your Web API project?

ANSWER:
ASP.NET Core uses attribute routing in Web API controllers. Routes are defined at controller and action level using `[Route]` and HTTP method attributes.

PROJECT EXAMPLE:
- File: `Controllers/WalletVerificationController.cs`
  ```csharp
  [Route("api/wallet")]
  [ApiController]
  [Authorize]
  public class WalletVerificationController : ControllerBase
  {
      [HttpPost("WalletGetVerification")]
      [HttpPost("WalletUpdateVerifiedDetails")]
      [HttpPost("GetWalletpassbook")]
      [HttpGet("GetDecrementalBalance/Client/{clientid}")]
      [HttpPost("WalletDeposit/Client/{Clientid}")]
      [HttpGet("GetPMWalletVerificationData")]
  }
  ```
- Route parameter: `{clientid}` in `GetDecrementalBalance` bound via `[FromRoute]`

FOLLOW-UP QUESTIONS:
1. What is the difference between `[Route]` and `[HttpGet]`/`[HttpPost]`?
2. How does route constraint work (e.g., `{id:int}`)?
3. How would you add API versioning to these routes?

IMPORTANT FOR INTERVIEW:
In this project, API versioning is NOT implemented. Ideally routes should be versioned as `api/v1/wallet/...` using `Microsoft.AspNetCore.Mvc.Versioning` NuGet package. This is a common interview follow-up.

---

QUESTION:
Does your project use Entity Framework? How is database access handled?

ANSWER:
This project does NOT use Entity Framework. It uses raw ADO.NET (`Microsoft.Data.SqlClient`) with stored procedures for all database operations.

PROJECT EXAMPLE:
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  using var connection = new SqlConnection(_connectionString);
  using var command = new SqlCommand("CS_Wallet_GetPaymentVerificationDetails", connection);
  command.CommandType = CommandType.StoredProcedure;
  command.Parameters.AddWithValue("@ClientId", obj.ClientId);
  await connection.OpenAsync();
  using var reader = await command.ExecuteReaderAsync();
  while (await reader.ReadAsync()) {
      // Manual mapping to model
  }
  ```
- Stored procedures used: `CS_Wallet_GetPaymentVerificationDetails`, `CS_Wallet_UpdateVerifiedDetails`, `CS_Wallet_Client_Passbook`, `CS_Wallet_GetDecrementalBalance`, `CS_Wallet_InsertInitialTransaction`, `PM_GetWalletVerificationList`

FOLLOW-UP QUESTIONS:
1. What are the advantages of stored procedures over EF LINQ queries?
2. How does `AddWithValue` differ from `Add` with explicit `SqlDbType`? Which is safer?
3. How would you migrate this to Entity Framework if required?

IMPORTANT FOR INTERVIEW:
`AddWithValue` can cause implicit type conversion issues (e.g., `nvarchar` vs `varchar` causes index scans). Best practice is `command.Parameters.Add("@Param", SqlDbType.NVarChar).Value = value`. The stored procedure approach gives DBAs control over query plans and execution.

---

QUESTION:
How is async/await used in your project?

ANSWER:
All repository methods are asynchronous using `async Task<T>` to prevent thread blocking during I/O operations (database calls).

PROJECT EXAMPLE:
- File: `Contracts/IWalletVerificationRepository.cs`
  ```csharp
  Task<List<VerificationDetailsResponse>> GetWalletPaymentVerificationDetailsAsync(VerificationDetailsResponse obj);
  Task<WalletCallResponse> WalletUpdateVerifiedDetailsAsync(VerificationDetailsResponse obj);
  ```
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  public async Task<List<VerificationDetailsResponse>> GetWalletPaymentVerificationDetailsAsync(...)
  {
      await connection.OpenAsync();
      using var reader = await command.ExecuteReaderAsync();
  }
  ```
- File: `Controllers/WalletVerificationController.cs`
  ```csharp
  public async Task<IActionResult> WalletGetVerification([FromBody] VerificationDetailsResponse obj)
  {
      var result = await _walletVerificationRepository.GetWalletPaymentVerificationDetailsAsync(obj);
      return Ok(result);
  }
  ```

FOLLOW-UP QUESTIONS:
1. What is the difference between `Task`, `Task<T>`, and `ValueTask<T>`?
2. What is `ConfigureAwait(false)` and when should you use it in a Web API?
3. What happens if you call an async method without awaiting it?

IMPORTANT FOR INTERVIEW:
`ConfigureAwait(false)` prevents deadlocks in non-ASP.NET contexts (e.g., WinForms, WPF). In ASP.NET Core Web API, there is no SynchronizationContext, so it's technically unnecessary but still a good practice for library code. Never use `.Result` or `.Wait()` in async code — it causes deadlocks.

---

QUESTION:
How is the Repository pattern implemented in your project?

ANSWER:
The Repository pattern abstracts data access behind an interface, decoupling the controller from the specific database implementation.

PROJECT EXAMPLE:
- Interface: `Contracts/IWalletVerificationRepository.cs`
  ```csharp
  public interface IWalletVerificationRepository {
      Task<List<VerificationDetailsResponse>> GetWalletPaymentVerificationDetailsAsync(...);
      Task<WalletCallResponse> WalletUpdateVerifiedDetailsAsync(...);
      // 4 more methods
  }
  ```
- Implementation: `Repository/WalletVerificationRepository.cs`
  - Implements `IWalletVerificationRepository`
  - Contains all ADO.NET / SQL logic
- Registration: `Program.cs` → `builder.Services.AddScoped<IWalletVerificationRepository, WalletVerificationRepository>()`
- Controller depends only on `IWalletVerificationRepository` — not the concrete class

FOLLOW-UP QUESTIONS:
1. What is the Unit of Work pattern and does this project use it?
2. How does the Repository pattern help with unit testing?
3. What would change if you switched from SQL Server to PostgreSQL?

IMPORTANT FOR INTERVIEW:
This project does NOT implement Unit of Work — each repository method manages its own connection/transaction. Unit of Work would wrap multiple repository operations in a single transaction. Since all data access goes through stored procedures, switching databases would require rewriting the repository but not the controller.

---

QUESTION:
How is exception handling done in your project?

ANSWER:
Exception handling is done at the repository level using try-catch blocks with Serilog logging. Controllers receive either a result or rethrown exception.

PROJECT EXAMPLE:
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  try {
      await connection.OpenAsync();
      // ... execute command
  }
  catch (SqlException sqlEx) {
      _logger.LogError(sqlEx, "SQL error in GetWalletPaymentVerificationDetailsAsync: {Message}", sqlEx.Message);
      throw;
  }
  catch (Exception ex) {
      _logger.LogError(ex, "Unexpected error in GetWalletPaymentVerificationDetailsAsync: {Message}", ex.Message);
      throw;
  }
  ```
- Global exception handling: This project currently does NOT implement a global exception filter or middleware (like `UseExceptionHandler`). Ideally it should use a global exception handling middleware to return consistent error responses.

FOLLOW-UP QUESTIONS:
1. What is the difference between a global exception filter and exception-handling middleware?
2. How would you implement a `ProblemDetails` response for all unhandled exceptions?
3. What is the `finally` block used for in repository code?

IMPORTANT FOR INTERVIEW:
Best practice: add `app.UseExceptionHandler()` or a custom middleware that catches all unhandled exceptions and returns a `ProblemDetails` (RFC 7807) JSON response. Currently, unhandled exceptions in this project would return a 500 with the stack trace in development mode — dangerous in production.

---

QUESTION:
How is CORS configured in your project?

ANSWER:
CORS (Cross-Origin Resource Sharing) allows the Angular frontend (different origin) to call the .NET API.

PROJECT EXAMPLE:
- File: `Program.cs`
  ```csharp
  builder.Services.AddCors(options => {
      options.AddPolicy("AllowAll", policy => {
          policy.AllowAnyOrigin()
                .AllowAnyMethod()
                .AllowAnyHeader();
      });
  });
  app.UseCors("AllowAll");
  ```
- The Angular app runs on a different domain/port from the API, so CORS is required
- `AllowAnyOrigin` is used — permissive, acceptable for internal tooling

FOLLOW-UP QUESTIONS:
1. What is a preflight request and when does the browser send one?
2. Why can't you use `AllowAnyOrigin` with `AllowCredentials()`?
3. How would you restrict CORS to only allow the production Angular domain?

IMPORTANT FOR INTERVIEW:
`AllowAnyOrigin` + `AllowCredentials()` is forbidden by the CORS spec. For production, restrict to specific origins: `policy.WithOrigins("https://cspayments.enago.com")`. A preflight `OPTIONS` request is sent for non-simple requests (POST with JSON body, custom headers).

---

QUESTION:
How is logging implemented in your project?

ANSWER:
The project uses Serilog, a structured logging library, configured to write to files and read settings from `serilog.json`.

PROJECT EXAMPLE:
- File: `Program.cs`
  ```csharp
  builder.Host.UseSerilog((context, config) =>
      config.ReadFrom.Configuration(context.Configuration));
  ```
- File: `WalletVerificationAPI.csproj` — NuGet: `Serilog.AspNetCore (v10.0.0)`
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  private readonly ILogger<WalletVerificationRepository> _logger;
  _logger.LogError(ex, "SQL error: {Message}", ex.Message);
  _logger.LogInformation("Successfully retrieved {Count} records", result.Count);
  ```
- Logs are stored in `Logs/` directory
- Middleware: `app.UseSerilogRequestLogging()` logs every HTTP request automatically

FOLLOW-UP QUESTIONS:
1. What is the difference between Serilog and the built-in `ILogger`?
2. What are Serilog sinks and which ones would you add for production?
3. What is structured logging and why is it better than string concatenation?

IMPORTANT FOR INTERVIEW:
Structured logging means `_logger.LogError("Error for client {ClientId}", clientId)` stores `ClientId` as a searchable property, not just a string. In production, add sinks like Seq, Elasticsearch, or Azure Application Insights. `{Message}` in Serilog is a named placeholder, not string interpolation.

---

QUESTION:
How is Configuration Management done in your project?

ANSWER:
Configuration is managed via `appsettings.json` and `appsettings.{Environment}.json`, accessed through `IConfiguration` injected via DI.

PROJECT EXAMPLE:
- File: `appsettings.json`
  ```json
  {
    "ConnectionStrings": { "DefaultConnection": "Server=IPLPROD_UAT9;..." },
    "Jwt": { "Key": "95ba7edefb308827e28625d41bcc215c17cfee75e0605c1865d6240a8612c693" },
    "PassbookURL": "https://uat9web.enago.com",
    "APIKey": "MVAM4AqgmM1vZ6qRqcuJv6vECdNaqaYt3g7kk8V6"
  }
  ```
- File: `Program.cs`
  ```csharp
  var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
      ?? Environment.GetEnvironmentVariable("DB_CONNECTION_STRING");
  ```
- Repository gets `IConfiguration` injected and reads `_configuration["PassbookURL"]`

FOLLOW-UP QUESTIONS:
1. What is the Options pattern (`IOptions<T>`) and why is it better than `IConfiguration`?
2. How do you override configuration values in production without changing `appsettings.json`?
3. How should secrets like JWT keys be stored in production?

IMPORTANT FOR INTERVIEW:
JWT keys and connection strings should NEVER be in `appsettings.json` in production. Use environment variables, Azure Key Vault, AWS Secrets Manager, or ASP.NET Core's Secret Manager for local development. The Options pattern with `IOptions<JwtSettings>` is strongly typed and testable.

---

QUESTION:
How are DTOs used in your project?

ANSWER:
DTOs (Data Transfer Objects) are used to shape data flowing between the API and client, decoupling the database schema from the API contract.

PROJECT EXAMPLE:
- File: `Models/VerificationDetailsResponse.cs` — serves as both input DTO and output model:
  ```csharp
  public class VerificationDetailsResponse {
      public int? ClientId { get; set; }
      public decimal? Debit { get; set; }
      public string? EmailAddress { get; set; }
      public decimal? VerifiedAmt { get; set; }
      // ... 20+ properties
  }
  ```
- File: `Models/WalletCallResponse.cs` — pure output DTO:
  ```csharp
  public class WalletCallResponse {
      public int Status { get; set; }
      public string? Message { get; set; }
      public int ClientId { get; set; }
      public string? MembershipID { get; set; }
  }
  ```
- File: `Models/WalletTransactionInitializationDTO.cs` — input-only DTO
- AutoMapper: This project currently does NOT use AutoMapper. Mapping is done manually inside the repository's `SqlDataReader` loop.

FOLLOW-UP QUESTIONS:
1. What is the difference between a DTO and a ViewModel?
2. Why should you avoid returning domain/entity objects directly from the API?
3. How would AutoMapper improve the repository mapping code here?

IMPORTANT FOR INTERVIEW:
Using domain entities as API responses leaks database schema details and causes over-posting vulnerabilities. AutoMapper would eliminate manual `reader["ColumnName"]` mapping. FluentValidation would add validation to input DTOs.

---

QUESTION:
How are SOLID principles applied in this project?

ANSWER:
SOLID principles are partially applied. Let me explain each:

PROJECT EXAMPLE:
- **S (Single Responsibility)**: `WalletVerificationController` only handles HTTP. `WalletVerificationRepository` only handles data access. `UrlEncryptionUtility` only handles encryption.
- **O (Open/Closed)**: `IWalletVerificationRepository` interface allows adding new implementations without modifying existing code.
- **L (Liskov Substitution)**: `WalletVerificationRepository` implements `IWalletVerificationRepository` — any compliant implementation can replace it.
- **I (Interface Segregation)**: The project currently has ONE large interface (`IWalletVerificationRepository`) with 6 methods. Ideally it should be split by responsibility.
- **D (Dependency Inversion)**: Controller depends on `IWalletVerificationRepository` (abstraction), not `WalletVerificationRepository` (concrete).

FOLLOW-UP QUESTIONS:
1. How does the `[Authorize]` attribute violate or uphold SRP?
2. How would you refactor `IWalletVerificationRepository` to better follow ISP?
3. What is the Dependency Inversion Principle vs. Dependency Injection?

IMPORTANT FOR INTERVIEW:
DIP is a principle (depend on abstractions). DI is a mechanism to achieve DIP. This project demonstrates DIP through interface-based repository design. ISP violation: the single repository interface mixes wallet deposit operations, passbook operations, and PM wallet operations — these could be separate interfaces.

---

QUESTION:
What encryption is used in your project?

ANSWER:
Two encryption mechanisms are used: DES for URL encryption and AES (via external `PII_Crypter.dll`) for email encryption.

PROJECT EXAMPLE:
- File: `Utilities/UrlEncryptionUtility.cs`
  ```csharp
  // DES encryption with hardcoded key
  private static readonly byte[] Key = Encoding.ASCII.GetBytes("!5623a#de"); // 8 bytes
  private static readonly byte[] IV = { 0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF };
  public static string EncryptURL(string plainText) {
      using var des = DES.Create();
      // ... encrypt → Base64 → URL-encode
  }
  ```
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  // AES email decryption via external DLL
  var decryptedEmail = Crypter.Operations.Decrypt(reader["EmailAddress"].ToString());
  ```
- PassbookUrl is encrypted with `UrlEncryptionUtility.EncryptURL()` before returning to the client

FOLLOW-UP QUESTIONS:
1. Why is DES considered insecure today? What should replace it?
2. What are the risks of hardcoded encryption keys?
3. What is the difference between symmetric and asymmetric encryption?

IMPORTANT FOR INTERVIEW:
DES (56-bit key) was broken in 1998 — brute-forceable. Should be replaced with AES-256. Hardcoded keys in source code are a critical security vulnerability — keys should be in Key Vault or environment variables. The external `PII_Crypter.dll` suggests a shared encryption library across the organization for consistent PII protection.

---

QUESTION:
What is the Generic class / interface pattern and how is it seen in this project?

ANSWER:
Generics allow type-safe, reusable code. The `ILogger<T>` and `Task<T>` are built-in generics used extensively in this project.

PROJECT EXAMPLE:
- `ILogger<WalletVerificationController>` — generic logger bound to specific class for log categorization
- `Task<List<VerificationDetailsResponse>>` — generic async return type
- `Task<WalletCallResponse>` — typed async result
- The project does NOT define custom generic classes. Ideally a generic `ApiResponse<T>` wrapper could standardize all API responses.

FOLLOW-UP QUESTIONS:
1. What is a generic constraint (`where T : class`)?
2. How would you create a generic `ApiResponse<T>` wrapper for all endpoints?
3. What is covariance and contravariance in generics?

IMPORTANT FOR INTERVIEW:
A generic response wrapper is a common pattern: `ApiResponse<T> { bool Success; T Data; string ErrorMessage; }`. This project returns raw data — adding such a wrapper would standardize error handling across all endpoints.

---

QUESTION:
How does the `WalletAPIStatus` enum work and why is it used?

ANSWER:
Enums provide named constants instead of magic numbers, making code readable and maintainable.

PROJECT EXAMPLE:
- File: `Models/WalletAPIStatus.cs`
  ```csharp
  public enum WalletAPIStatus {
      NotVerified = 0,
      Verified = 1,
      Pending = 2,
      Error = 3
  }
  ```
- Used in `WalletUpdateVerifiedDetails` endpoint — the stored procedure `CS_Wallet_UpdateVerifiedDetails` returns an output parameter with these status codes
- `WalletCallResponse.Status` holds this integer value
- Angular reads `statusCode` property and displays corresponding UI state

FOLLOW-UP QUESTIONS:
1. How would you serialize this enum as a string ("Verified") instead of integer (1) in JSON?
2. What is `[Flags]` attribute on an enum?
3. How do you switch on an enum value in C#?

IMPORTANT FOR INTERVIEW:
Add `[JsonConverter(typeof(JsonStringEnumConverter))]` or configure `JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter())` in `Program.cs` to return enum names as strings in the API response.

---

# ANGULAR CONCEPTS

---

QUESTION:
What is Angular's architecture and how is it applied in your project?

ANSWER:
Angular uses a modular architecture of Modules → Components → Templates, with Services for shared logic, Interceptors for cross-cutting concerns, and Guards for route protection.

PROJECT EXAMPLE:
- Root Module: `app.module.ts` — declares all components, imports feature modules, registers providers
- Components: `WalletDepositsVerificationComponent`, `PaymentMatchingVerificationComponent`, `VerifyPaymentComponent`, `AutoLoginComponent`
- Services: `PaymentVerificationService`, `PMWalletVerificationService`, `TokenApiService`, `UserInfoService`
- Interceptor: `TokenInterceptor` — adds JWT to every HTTP request
- Guards: `AuthorizationGuard` (CanActivate), `AuthorizationCanGuard` (CanLoad)
- Material Module: `material.module.ts` — centralized Angular Material imports

FOLLOW-UP QUESTIONS:
1. What is the difference between a feature module and a shared module?
2. How does Angular's change detection work?
3. What is the difference between a component and a directive?

IMPORTANT FOR INTERVIEW:
This project uses a single-module architecture (all in AppModule). In larger applications, you'd split into feature modules (WalletModule, AuthModule) with lazy loading. The `material.module.ts` acts as a shared module for Material components.

---

QUESTION:
How is routing implemented in your Angular project?

ANSWER:
Angular Router maps URL paths to components. Routes are configured in `AppRoutingModule`.

PROJECT EXAMPLE:
- File: `app-routing.module.ts`
  ```typescript
  const routes: Routes = [
    { path: 'autologin', component: AutoLoginComponent },
    {
      path: 'VerifyWalletDeposits',
      component: WalletDepositsVerificationComponent,
      canActivate: [AuthorizationGuard],
      canLoad: [AuthorizationCanGuard]
    },
    { path: '', redirectTo: '/VerifyWalletDeposits', pathMatch: 'full' },
    { path: '**', redirectTo: '/VerifyWalletDeposits' }
  ];
  ```
- Default route redirects to wallet deposits page
- Wildcard `**` catches all unknown routes

FOLLOW-UP QUESTIONS:
1. What is the difference between `canActivate` and `canLoad`?
2. What is `pathMatch: 'full'` vs `pathMatch: 'prefix'`?
3. How would you implement lazy loading in this routing configuration?

IMPORTANT FOR INTERVIEW:
`canLoad` prevents the module from loading (useful with lazy-loaded modules). `canActivate` prevents navigation but the module may already be loaded. This project uses `canLoad` but all components are eagerly loaded — so `canLoad` has no practical effect here. Lazy loading would require feature modules.

---

QUESTION:
How is lazy loading used in your Angular project?

ANSWER:
This project currently does NOT implement true lazy loading. All components are eagerly loaded in `AppModule`.

PROJECT EXAMPLE:
- File: `app.module.ts` — all components declared directly in AppModule
- `canLoad` guard exists on the `VerifyWalletDeposits` route but is not effective without a lazy-loaded module
- Ideally: `{ path: 'VerifyWalletDeposits', loadChildren: () => import('./wallet/wallet.module').then(m => m.WalletModule) }`

This project currently does not implement this concept fully, but ideally it should be implemented using feature modules with `loadChildren` syntax, splitting the wallet verification feature into its own module that loads on demand.

FOLLOW-UP QUESTIONS:
1. What is the difference between `loadChildren` and `component` in route config?
2. How does lazy loading improve initial load time?
3. How does Angular know which chunks to split into separate bundles?

IMPORTANT FOR INTERVIEW:
Lazy loading splits the app into multiple JS bundles, reducing initial payload. Angular CLI automatically creates separate chunks for lazy-loaded modules. Preloading strategies (`PreloadAllModules`) can be used to load lazy modules in the background after initial load.

---

QUESTION:
How are Reactive Forms used in your project?

ANSWER:
Reactive Forms provide programmatic form control, validation, and state management.

PROJECT EXAMPLE:
- File: `components/payment-matching-verification/payment-matching-verification.component.ts`
  ```typescript
  searchControl = new FormControl('');
  ```
- The search control filters the PM wallet data table in real-time
- `ReactiveFormsModule` is imported in `app.module.ts`
- The form control subscribes to value changes to filter the displayed data

FOLLOW-UP QUESTIONS:
1. What is the difference between `FormControl`, `FormGroup`, and `FormArray`?
2. How do you add validators to a `FormControl`?
3. What is `valueChanges` and `statusChanges` observable on a FormControl?

IMPORTANT FOR INTERVIEW:
Reactive forms are preferred over template-driven forms for complex scenarios because they are:
- Easier to test (pure TypeScript)
- Better for dynamic forms
- Synchronous access to form state
The search filter uses `valueChanges` observable with `debounceTime` operator to avoid filtering on every keystroke.

---

QUESTION:
How are RxJS Observables used in your project?

ANSWER:
Observables are used for HTTP calls, OIDC authentication state, and reactive UI updates.

PROJECT EXAMPLE:
- File: `services/network-calls/get-payment-varification-list.service.ts`
  ```typescript
  getListOfPaymentVar(obj: any): Observable<PaymentVerify[]> {
      return this.http.post<PaymentVerify[]>(this.apiUrl, obj);
  }
  ```
- File: `app.component.ts`
  ```typescript
  this.oidcSecurityService.isAuthenticated$.subscribe(auth => { ... });
  this.oidcSecurityService.userData$.subscribe(userData => { ... });
  ```
- File: `guards/auth.guard.ts`
  ```typescript
  return this.oidcSecurityService.isAuthenticated$.pipe(
      map(isAuthenticated => isAuthenticated || (this.router.navigate(['/autologin']), false))
  );
  ```
- `BehaviorSubject` in `UserInfoService` for broadcasting user data

FOLLOW-UP QUESTIONS:
1. What is the difference between `Observable`, `Subject`, `BehaviorSubject`, and `ReplaySubject`?
2. What is the `async` pipe and why is it preferred over `.subscribe()`?
3. What operators are used in this project? (map, pipe, etc.)

IMPORTANT FOR INTERVIEW:
`BehaviorSubject` always emits the last value to new subscribers — perfect for `UserInfoService` where a late-subscribing component needs the current user immediately. `Subject` doesn't replay. `ReplaySubject(n)` replays the last n values. Using `async` pipe in templates auto-unsubscribes when component destroys — preventing memory leaks.

---

QUESTION:
How is the HTTP Interceptor implemented in your project?

ANSWER:
The `TokenInterceptor` intercepts every outgoing HTTP request to add the JWT Bearer token.

PROJECT EXAMPLE:
- File: `services/interceptors/token.interceptor.ts`
  ```typescript
  @Injectable()
  export class TokenInterceptor implements HttpInterceptor {
      intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
          if (request.headers.has('BypassInterceptor')) {
              return next.handle(request);
          }
          // Check sessionStorage for token
          const token = this.common.getSessionStorageValue('access_token');
          const expiry = this.common.getSessionStorageValue('token_expiry');
          if (token && !isExpired(expiry)) {
              request = request.clone({
                  setHeaders: { Authorization: `Bearer ${token}` }
              });
          } else {
              // Fetch new token from TokenApiService
          }
          // Show/hide NgxSpinner
          return next.handle(request);
      }
  }
  ```
- Registered in `app.module.ts` as: `{ provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true }`
- `BypassInterceptor` header allows the token-fetch request itself to skip token injection (prevents infinite loop)

FOLLOW-UP QUESTIONS:
1. What does `request.clone()` do and why is it necessary?
2. What is the `multi: true` flag in the provider registration?
3. How would you add retry logic (e.g., retry on 401) in this interceptor?

IMPORTANT FOR INTERVIEW:
HTTP requests are immutable — `request.clone()` creates a new request with modified headers. `multi: true` allows multiple interceptors to coexist. For retry on 401: use `catchError` + `switchMap` to refresh the token and retry the original request.

---

QUESTION:
How are Route Guards implemented in your project?

ANSWER:
Two guards protect the wallet deposits route: `AuthorizationGuard` (CanActivate) and `AuthorizationCanGuard` (CanLoad).

PROJECT EXAMPLE:
- File: `guards/auth.guard.ts`
  ```typescript
  @Injectable()
  export class AuthorizationGuard implements CanActivate {
      canActivate(route, state): Observable<boolean> {
          return this.oidcSecurityService.isAuthenticated$.pipe(
              map(isAuthenticated => {
                  if (!isAuthenticated) {
                      this.router.navigate(['/autologin']);
                      return false;
                  }
                  return true;
              })
          );
      }
  }
  ```
- File: `guards/authorization.can.guard.ts`
  ```typescript
  export class AuthorizationCanGuard implements CanLoad {
      canLoad(): boolean { return true; }  // Always returns true
  }
  ```
- Route: `canActivate: [AuthorizationGuard], canLoad: [AuthorizationCanGuard]`

FOLLOW-UP QUESTIONS:
1. What is the difference between `CanActivate`, `CanLoad`, `CanDeactivate`, and `CanActivateChild`?
2. Why does `AuthorizationCanGuard` always return true? Is this a problem?
3. How would you implement a role-based guard?

IMPORTANT FOR INTERVIEW:
`CanDeactivate` is useful for "unsaved changes" warnings. `CanActivateChild` protects child routes. The `CanLoad` always returning `true` is a design gap — it means the module (if lazy-loaded) would load for unauthenticated users. The actual auth check is in `CanActivate`.

---

QUESTION:
How is parent-child and sibling component communication done in your project?

ANSWER:
Components communicate via Angular Material Dialog (passing data) and through shared services (BehaviorSubject).

PROJECT EXAMPLE:
- **Parent to Dialog (Child)**: `WalletDepositsVerificationComponent` opens `PaymentMatchingVerificationComponent` dialog passing `PaymentVerify` data:
  ```typescript
  this.dialog.open(PaymentMatchingVerificationComponent, {
      data: { rowData: element }
  });
  ```
- **Dialog receives data**: `constructor(@Inject(MAT_DIALOG_DATA) public data: any)`
- **Service-based sharing**: `UserInfoService` uses `BehaviorSubject<UserInfo>`:
  ```typescript
  private userInfoSubject = new BehaviorSubject<UserInfo>(null);
  userInfo$ = this.userInfoSubject.asObservable();
  ```
  - `AppComponent` sets user info; `PaymentMatchingVerificationComponent` reads `VerifiedBy` from it

FOLLOW-UP QUESTIONS:
1. What is `@Input()` and `@Output()` and when would you use them vs a service?
2. What is `EventEmitter` and how does it work with `@Output()`?
3. How would you use a shared service to pass data between two unrelated components?

IMPORTANT FOR INTERVIEW:
`@Input()`/`@Output()` for direct parent-child relationships. Service + BehaviorSubject for sibling or distant components. `MatDialogRef` allows the dialog to return data back to the opener via `.afterClosed()` observable.

---

QUESTION:
What lifecycle hooks are used in your project?

ANSWER:
`OnInit` is the primary lifecycle hook used across components.

PROJECT EXAMPLE:
- File: `components/wallet-deposits-verification/wallet-deposits-verification.component.ts`
  ```typescript
  ngOnInit(): void {
      this.getListOfNotVerified();
  }
  ```
- File: `components/payment-matching-verification/payment-matching-verification.component.ts`
  ```typescript
  ngOnInit(): void {
      this.loadPMWalletData();
  }
  ```
- File: `app.component.ts`
  ```typescript
  ngOnInit(): void {
      // Setup OIDC subscriptions
      this.oidcSecurityService.isAuthenticated$.subscribe(...);
  }
  ```
- `OnDestroy`: This project currently does NOT implement `ngOnDestroy`. Subscriptions in `AppComponent` should be unsubscribed to prevent memory leaks.

FOLLOW-UP QUESTIONS:
1. What is the correct order of lifecycle hooks?
2. Why should you unsubscribe from observables in `ngOnDestroy`?
3. What is `ngOnChanges` and when does it fire?

IMPORTANT FOR INTERVIEW:
Lifecycle order: `ngOnChanges` → `ngOnInit` → `ngDoCheck` → `ngAfterContentInit` → `ngAfterContentChecked` → `ngAfterViewInit` → `ngAfterViewChecked` → `ngOnDestroy`. Missing `ngOnDestroy` with unsubscribe is a common memory leak in Angular apps.

---

QUESTION:
How are Pipes used in your Angular project?

ANSWER:
This project uses Angular's built-in pipes in templates for data formatting.

PROJECT EXAMPLE:
- `date` pipe: In `wallet-deposits-verification.component.html` — formats `entrymadeon` timestamps for display
- `currency` or `number` pipes likely used for `clientExpectedAmout`, `depositeamount` display
- Custom pipes: This project currently does NOT implement custom pipes. A status-to-label pipe (e.g., `0 → 'Pending'`, `1 → 'Verified'`) would clean up template logic.

FOLLOW-UP QUESTIONS:
1. What is the difference between a pure and impure pipe?
2. How do you create a custom pipe in Angular?
3. What is the `async` pipe and how does it work?

IMPORTANT FOR INTERVIEW:
Pure pipes only recalculate when the input reference changes. Impure pipes recalculate on every change detection cycle (expensive). The `async` pipe subscribes to an Observable/Promise, returns its latest value, and unsubscribes automatically on component destroy.

---

QUESTION:
How are Directives used in your project?

ANSWER:
The project uses Angular Material's structural and attribute directives for UI rendering.

PROJECT EXAMPLE:
- `*ngFor` structural directive: Iterates over payment records in tables
- `*ngIf` structural directive: Conditionally shows verification UI, spinner
- `mat-table`, `matSort`, `matPaginator`: Angular Material attribute directives applied to table
- `[formControl]`: Reactive forms attribute directive bound to `searchControl`
- Custom directives: This project currently does NOT implement custom directives.

FOLLOW-UP QUESTIONS:
1. What is the difference between a structural directive and an attribute directive?
2. How do you create a custom structural directive (like `*ngIf`)?
3. What is `ng-template` and how is it related to structural directives?

IMPORTANT FOR INTERVIEW:
Structural directives (prefixed with `*`) change DOM structure (add/remove elements). Attribute directives change element appearance/behavior. `*ngFor` is syntactic sugar for `<ng-template ngFor>`.

---

QUESTION:
How is Dependency Injection used in Angular in your project?

ANSWER:
Angular's DI system injects services into components and other services via constructor injection.

PROJECT EXAMPLE:
- File: `components/wallet-deposits-verification/wallet-deposits-verification.component.ts`
  ```typescript
  constructor(
      private paymentService: PaymentVerificationService,
      private dialog: MatDialog,
      private spinner: NgxSpinnerService
  ) {}
  ```
- File: `services/interceptors/token.interceptor.ts`
  ```typescript
  constructor(
      private tokenApiService: TokenApiService,
      private common: Common
  ) {}
  ```
- Services registered in `app.module.ts` providers array or with `@Injectable({ providedIn: 'root' })`

FOLLOW-UP QUESTIONS:
1. What is the difference between providing a service in `AppModule` vs `@Injectable({ providedIn: 'root' })`?
2. What is the Angular DI token and how do you create a custom one?
3. How does the `@Inject(MAT_DIALOG_DATA)` injection token work?

IMPORTANT FOR INTERVIEW:
`providedIn: 'root'` makes the service a singleton available app-wide without declaring in any module. Services provided in a feature module are scoped to that module. `InjectionToken` is used for injecting non-class values like `MAT_DIALOG_DATA`.

---

QUESTION:
How is state management handled in your Angular project?

ANSWER:
This project uses a simple service-based state management approach with `BehaviorSubject`.

PROJECT EXAMPLE:
- File: `services/internal/user-info.service.ts`
  ```typescript
  @Injectable({ providedIn: 'root' })
  export class UserInfoService {
      private userInfoSubject = new BehaviorSubject<UserInfo>(null);
      userInfo$ = this.userInfoSubject.asObservable();
      setUserInfo(info: UserInfo) { this.userInfoSubject.next(info); }
  }
  ```
- `AppComponent` calls `userInfoService.setUserInfo(deserializedUser)` after OIDC login
- `PaymentMatchingVerificationComponent` reads from `userInfoService.userInfo$` to get `VerifiedBy`

This project currently does NOT implement NgRx or any external state management library. The simple BehaviorSubject approach is appropriate for this project's size.

FOLLOW-UP QUESTIONS:
1. When would you use NgRx over a simple service with BehaviorSubject?
2. What is the Redux pattern and how does NgRx implement it?
3. What is the difference between `Subject` and `BehaviorSubject`?

IMPORTANT FOR INTERVIEW:
NgRx is appropriate for large apps with complex shared state, time-travel debugging needs, or multiple teams. For this project's scope (1-2 shared state objects), BehaviorSubject in a service is perfectly appropriate and much simpler.

---

QUESTION:
How is environment configuration managed in your Angular project?

ANSWER:
Angular environments are managed via separate `environment.*.ts` files, with build configurations selecting the appropriate file.

PROJECT EXAMPLE:
- Files: `src/environments/environment.ts` (dev), `environment.qat9.ts`, `environment.prod.ts`, `environment.stage.ts`
- File: `angular.json` — fileReplacements per configuration:
  ```json
  "production": {
      "fileReplacements": [
          { "replace": "src/environments/environment.ts",
            "with": "src/environments/environment.prod.ts" }
      ]
  }
  ```
- Different API URLs per environment:
  - Dev: `https://csservicesuat.enago.com:4205/api/wallet/...`
  - Prod: `https://csothapis.enago.com/api/wallet/...`
- `ServicesHelper.getServiceUrl(api)` reads from the imported environment object

FOLLOW-UP QUESTIONS:
1. How does Angular CLI swap environment files at build time?
2. Is it safe to put API URLs in Angular environment files? What about API keys?
3. How would you add a new environment (e.g., `staging`)?

IMPORTANT FOR INTERVIEW:
Angular environment files are compiled into the bundle — they are visible in the browser. NEVER put secrets (API keys, passwords) in environment files. API URLs are generally safe. Note: `environment.prod.ts` has `production: false` — this is a bug, it should be `true` to enable production optimizations.

---

QUESTION:
How is the OIDC authentication flow implemented in Angular?

ANSWER:
The project uses `angular-auth-oidc-client` library for OpenID Connect authentication.

PROJECT EXAMPLE:
- File: `app.module.ts` — configures OIDC:
  ```typescript
  AuthModule.forRoot({
      config: {
          authority: environment.oidcSettings.stsServer,
          redirectUrl: environment.oidcSettings.redirectUrl,
          clientId: environment.oidcSettings.clientId,
          responseType: 'id_token token',
          scope: 'openid profile email'
      }
  })
  ```
- Flow: User → `AuthorizationGuard` → `/autologin` → `AutoLoginComponent` → OIDC server → callback URL → `AppComponent.checkAuth()` → `UserInfoService`
- `AutoLoginComponent` handles redirect callbacks and clears stale OIDC state to prevent infinite loops
- Custom logout: clears auth storage, redirects to OIDC `end_session` endpoint

FOLLOW-UP QUESTIONS:
1. What is the difference between OAuth 2.0 and OpenID Connect?
2. What is `id_token` vs `access_token` in OIDC?
3. What is the PKCE flow and why is it more secure than implicit flow?

IMPORTANT FOR INTERVIEW:
This project uses `response_type: id_token token` (implicit flow), which is being deprecated in favor of Authorization Code + PKCE. `id_token` is a JWT containing user identity claims (sub, name, email). `access_token` is used to call resource APIs. The library handles token storage and silent refresh.

---

QUESTION:
How does Change Detection work and are there any optimizations in this project?

ANSWER:
Angular uses Zone.js-based automatic change detection. This project uses the default `ChangeDetectionStrategy.Default`.

PROJECT EXAMPLE:
- No `ChangeDetectionStrategy.OnPush` is used in any component
- `NgxSpinner` uses `changeDetectorRef.detectChanges()` internally for spinner updates
- Material table with `MatTableDataSource` handles internal change detection for table updates
- This project currently does NOT implement OnPush strategy. For a data-heavy table component like `WalletDepositsVerificationComponent`, `OnPush` with `async` pipe would improve performance.

FOLLOW-UP QUESTIONS:
1. What is the difference between Default and OnPush change detection?
2. What is Zone.js and how does it enable automatic change detection?
3. When should you manually call `markForCheck()` or `detectChanges()`?

IMPORTANT FOR INTERVIEW:
`OnPush` components only check when: Input references change, an async pipe emits, or `markForCheck()`/`detectChanges()` is called manually. This dramatically reduces change detection cycles for large lists. With `MatTableDataSource`, `OnPush` requires calling `markForCheck()` after updating the data source.

---

QUESTION:
What is JIT vs AOT compilation and what does your project use?

ANSWER:
JIT (Just-In-Time) compiles templates in the browser at runtime. AOT (Ahead-of-Time) compiles templates at build time, producing smaller and faster apps.

PROJECT EXAMPLE:
- File: `package.json` build scripts:
  ```json
  "build": "ng build --configuration production"
  ```
- Angular 16 uses AOT by default for production builds
- `ng build` without `--configuration production` uses JIT in older setups, but Angular 16 defaults to AOT even in dev
- AOT catches template errors at build time rather than runtime

FOLLOW-UP QUESTIONS:
1. What are the performance benefits of AOT?
2. What kind of template errors does AOT catch that JIT misses?
3. What is Ivy renderer and how does it improve over View Engine?

IMPORTANT FOR INTERVIEW:
AOT advantages: smaller bundle (no Angular compiler in bundle), faster rendering, earlier error detection. Ivy (Angular 9+) enables tree-shaking of unused Angular features, making bundles smaller. This project uses Angular 16 with Ivy by default.

---

# DATABASE / SQL CONCEPTS

---

QUESTION:
How are Stored Procedures used in your project?

ANSWER:
All database operations go through stored procedures — no inline SQL exists in the application code.

PROJECT EXAMPLE:
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  command.CommandText = "CS_Wallet_GetPaymentVerificationDetails";
  command.CommandType = CommandType.StoredProcedure;
  command.Parameters.AddWithValue("@ClientId", obj.ClientId);
  command.Parameters.AddWithValue("@Status", obj.Status);
  ```
- Procedures called:
  1. `CS_Wallet_GetPaymentVerificationDetails` — fetch pending verifications
  2. `CS_Wallet_UpdateVerifiedDetails` — update verification status
  3. `CS_Wallet_Client_Passbook` — get wallet passbook
  4. `CS_Wallet_GetDecrementalBalance` — get balance
  5. `CS_Wallet_InsertInitialTransaction` — insert deposit
  6. `PM_GetWalletVerificationList` — PM wallet statements

FOLLOW-UP QUESTIONS:
1. What are the advantages of stored procedures over inline SQL?
2. How do stored procedures prevent SQL injection?
3. How do you handle output parameters from stored procedures in ADO.NET?

IMPORTANT FOR INTERVIEW:
Stored procedure advantages: execution plan caching (performance), centralized business logic, reduced network traffic, DBA control over queries. SQL injection prevention: parameterized stored procedures treat inputs as data, not SQL code. Output parameters: `command.Parameters.Add("@Result", SqlDbType.Int).Direction = ParameterDirection.Output;`

---

QUESTION:
How are SQL parameters used to prevent injection in your project?

ANSWER:
All SQL parameters are passed via `SqlParameter` objects, never via string concatenation.

PROJECT EXAMPLE:
- File: `Repository/WalletVerificationRepository.cs`
  ```csharp
  // SAFE - parameterized
  command.Parameters.AddWithValue("@ClientId", obj.ClientId);
  command.Parameters.AddWithValue("@VerifiedAmt", obj.VerifiedAmt);
  command.Parameters.AddWithValue("@VerifiedBy", obj.VerifiedBy);
  
  // What NOT to do (SQL injection risk):
  // command.CommandText = $"EXEC CS_Wallet_UpdateVerifiedDetails {obj.ClientId}";
  ```
- All 6 stored procedure calls use parameterized inputs

FOLLOW-UP QUESTIONS:
1. What is SQL injection and how can it be exploited?
2. What is the difference between `AddWithValue` and explicitly typed `Add`?
3. How does parameterization work under the hood?

IMPORTANT FOR INTERVIEW:
Parameterization sends the SQL and parameters separately to SQL Server — the server treats parameters as literal values, never as SQL code. `AddWithValue` infers the SQL type from the .NET type which can cause type conversion issues (performance). Preferred: `cmd.Parameters.Add("@Amount", SqlDbType.Decimal, 18).Value = obj.VerifiedAmt;`

---

QUESTION:
How are transactions handled in your project?

ANSWER:
This project currently does NOT implement explicit ADO.NET transactions. Each stored procedure call is independent. The stored procedures themselves may handle transactions internally on the SQL Server side.

PROJECT EXAMPLE:
- File: `Repository/WalletVerificationRepository.cs` — no `SqlTransaction` usage
- `CS_Wallet_UpdateVerifiedDetails` and `CS_Wallet_InsertInitialTransaction` likely have `BEGIN TRAN / COMMIT / ROLLBACK` inside the stored procedures
- Ideally, if multiple repository operations need to be atomic, a `SqlTransaction` should be used:
  ```csharp
  using var transaction = connection.BeginTransaction();
  command.Transaction = transaction;
  // multiple operations
  transaction.Commit();
  ```

FOLLOW-UP QUESTIONS:
1. What are ACID properties of database transactions?
2. What is the difference between `READ COMMITTED` and `SERIALIZABLE` isolation levels?
3. How would you implement a distributed transaction across two databases?

IMPORTANT FOR INTERVIEW:
ACID: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don't interfere), Durability (committed data persists). SQL Server default isolation is `READ COMMITTED`. Higher isolation levels (`REPEATABLE READ`, `SERIALIZABLE`) reduce concurrency but increase data consistency.

---

QUESTION:
How is pagination implemented in your project?

ANSWER:
Pagination is implemented on the Angular frontend using Angular Material's `MatPaginator`, not server-side.

PROJECT EXAMPLE:
- File: `components/wallet-deposits-verification/wallet-deposits-verification.component.ts`
  ```typescript
  @ViewChild(MatPaginator) paginator: MatPaginator;
  dataSource = new MatTableDataSource<PaymentVerify>();
  ngAfterViewInit() {
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
  }
  ```
- All records are fetched from the API at once, then paginated client-side
- This project currently does NOT implement server-side pagination. For large datasets, the stored procedures should implement `OFFSET`/`FETCH NEXT` pagination.

FOLLOW-UP QUESTIONS:
1. What is the SQL syntax for server-side pagination in SQL Server?
2. What are the performance implications of client-side vs server-side pagination?
3. How would you implement cursor-based pagination for real-time data?

IMPORTANT FOR INTERVIEW:
Server-side pagination SQL: `SELECT * FROM Table ORDER BY CreatedOn OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;`. Client-side pagination loads all records — fine for small datasets (< 1000 rows) but problematic for large tables. The Angular `MatTableDataSource` handles client-side filtering, sorting, and pagination automatically.

---

QUESTION:
How is SQL query optimization considered in your project?

ANSWER:
The project uses stored procedures (which benefit from execution plan caching) and parameterized queries. The DBA team controls query optimization within the stored procedures.

PROJECT EXAMPLE:
- Execution plan caching: Stored procedures compile once, reuse plan on subsequent calls
- Parameterized queries prevent plan cache pollution (SQL Server can cache one plan per stored procedure vs. one per unique SQL string)
- `SqlCommand` `CommandTimeout` is increased in `Program.cs` (per commit message `CW-17695 increase Sp execution timeout`) — suggesting some procedures have performance concerns
- Indexing: Not visible in application code — managed at DB level by the DBA team

FOLLOW-UP QUESTIONS:
1. What is a query execution plan and how do you read it?
2. What is the difference between a clustered and non-clustered index?
3. When would you use a covering index vs a composite index?

IMPORTANT FOR INTERVIEW:
Clustered index: physically sorts rows (one per table, usually PK). Non-clustered: separate structure with pointers to rows. Covering index: includes all columns needed by a query so no row lookup is required. In the wallet verification context: indexing on `ClientId`, `Status`, `CreatedOn` would speed up the most common queries.

---

QUESTION:
What SQL joins would be used in the stored procedures called by this project?

ANSWER:
The wallet verification process inherently requires joining multiple tables — wallet transactions, client info, PM wallet statements.

PROJECT EXAMPLE:
Based on the stored procedures and response models:
- `CS_Wallet_GetPaymentVerificationDetails` likely joins:
  - `WalletInitializationTransaction` (for `WalletinitializationTransactionId`, `ClientId`)
  - `Client` (for `MemberShipID`, `EmailAddress`)
  - `WalletTransaction` (for `Debit`, `Credit`, `Balance`)
- `PM_GetWalletVerificationList` joins:
  - `PMWallet` statements with `WalletInitialization` records
  - Returns `MatchWalletInitialTransationID` for cross-referencing
- Response model has both `PMwalletID` and `StatementDetailID` suggesting a verification JOIN

FOLLOW-UP QUESTIONS:
1. What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?
2. What is a CROSS JOIN and when would you use it?
3. What is a self-join and give a practical example?

IMPORTANT FOR INTERVIEW:
INNER JOIN: only matching rows. LEFT JOIN: all left rows + matching right (NULL if no match). The verification matching process likely does a LEFT JOIN between wallet deposits and PM statements to show unmatched records. A `MatchWalletInitialTransationID` column suggests this matching is stored after verification.

---

QUESTION:
How are CTEs (Common Table Expressions) or Temp Tables potentially used in these stored procedures?

ANSWER:
While not visible in the C# code, stored procedures of this complexity likely use CTEs or temp tables internally.

PROJECT EXAMPLE:
- `CS_Wallet_GetPaymentVerificationDetails` likely uses a CTE or temp table to:
  - Join wallet transactions with client data
  - Calculate running balance (`Balance = Credits - Debits`)
  - Filter by `Status` and date ranges
- The `TransactionFrom` and `TransactionTo` date range parameters suggest complex filtering logic that benefits from CTEs

This project currently does NOT expose any CTE/temp table logic to the application layer — all complex logic is encapsulated in stored procedures.

FOLLOW-UP QUESTIONS:
1. What is the difference between a CTE and a subquery?
2. What is a recursive CTE and when would you use it?
3. What are the performance differences between temp tables (`#temp`) and table variables (`@table`)?

IMPORTANT FOR INTERVIEW:
CTEs are more readable than subqueries and can be referenced multiple times. Recursive CTEs build hierarchical data (org charts, category trees). Temp tables support indexes and statistics (better for large data). Table variables are scoped to the batch and don't persist stats.

---

QUESTION:
What is duplicate removal and how could it apply to this project?

ANSWER:
Duplicate removal in SQL uses `ROW_NUMBER()` window function or `DISTINCT`.

PROJECT EXAMPLE:
- The PM wallet verification list (`PM_GetWalletVerificationList`) could return duplicate statement rows if a transaction is matched multiple times — `ROW_NUMBER() OVER (PARTITION BY StatementDetailID ORDER BY TransactionDate DESC)` would identify duplicates
- `DISTINCT` on `PMwalletID` ensures each PM wallet entry appears once in the verification dialog
- `MatchWalletInitialTransationID` prevents re-matching — acts as a uniqueness constraint

FOLLOW-UP QUESTIONS:
1. Write a query to remove duplicate rows from a table using `ROW_NUMBER()`.
2. What is the difference between `DISTINCT` and `GROUP BY`?
3. How would you find duplicate records without deleting them?

IMPORTANT FOR INTERVIEW:
```sql
WITH CTE AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY PMwalletID ORDER BY TransactionDate DESC) AS rn
    FROM PMWalletStatements
)
DELETE FROM CTE WHERE rn > 1;
```
`DISTINCT` returns unique rows for SELECT. `GROUP BY` aggregates. For finding duplicates: `HAVING COUNT(*) > 1`.

---

# ADDITIONAL SECTIONS

---

# MOST IMPORTANT INTERVIEW QUESTIONS (Top 30 — Project-Specific)

1. Walk me through the complete request lifecycle when a user verifies a wallet deposit in your system.
2. How does the `TokenInterceptor` handle expired tokens, and how does it prevent duplicate token-fetch requests?
3. Why did you choose raw ADO.NET with stored procedures instead of Entity Framework?
4. How is the JWT token validated on the .NET backend? What parameters are validated?
5. Explain the OIDC authentication flow from when a user first visits the app to when they see the data.
6. What is the Repository pattern and how does your `IWalletVerificationRepository` implement it?
7. How does the `BehaviorSubject` in `UserInfoService` work and why was it chosen over `Subject`?
8. Why is `ValidateIssuer = false` set in JWT configuration? What are the security implications?
9. How does the `UrlEncryptionUtility` work? What algorithm does it use and what are its weaknesses?
10. How does the Angular Material `MatTableDataSource` handle filtering, sorting, and pagination?
11. What service lifetimes did you register in `Program.cs` and why?
12. How does the `PaymentMatchingVerificationComponent` dialog receive data and return results?
13. Why does the `AuthorizationCanGuard` always return `true`? Is this intentional?
14. How is Serilog configured and what does structured logging provide over `Console.WriteLine`?
15. Explain the CORS configuration in this project — why is `AllowAnyOrigin` used?
16. How does the `AutoLoginComponent` prevent infinite redirect loops during OIDC callback?
17. What is the purpose of `environment.ts` files and how does Angular CLI select the right one?
18. How are email addresses encrypted/decrypted in the repository? What library handles this?
19. What is the difference between `CanActivate` and `CanLoad` and how are both used in your routing?
20. How would you add server-side pagination to `GetWalletPaymentVerificationDetailsAsync`?
21. How does `CommandType.StoredProcedure` differ from `CommandType.Text` in ADO.NET?
22. How does the Angular Material dialog (`MatDialog`) work for the verification flow?
23. What is the purpose of `json2typescript` and how does it map OIDC user claims to `UserInfo`?
24. How would you implement unit tests for `WalletVerificationRepository`?
25. How would you add API versioning (e.g., `api/v1/wallet/`) to the existing controller?
26. What happens in your system if the stored procedure `CS_Wallet_UpdateVerifiedDetails` throws an exception?
27. How does the `NgxSpinner` get shown and hidden during API calls in this project?
28. How does the `Common.b64EncodeUnicode()` utility work in the token generation request?
29. What is the `WalletAPIStatus` enum and where is it used in the response lifecycle?
30. What improvements would you make to this project's security if moving to production?

---

# MISSING BEST PRACTICES

## Backend

1. **Global Exception Handling**: No `UseExceptionHandler` middleware or `IExceptionFilter`. Add a global handler returning `ProblemDetails` (RFC 7807).

2. **API Versioning**: Routes are not versioned. Add `Microsoft.AspNetCore.Mvc.Versioning` with `/api/v1/wallet/` prefix.

3. **Input Validation**: No `FluentValidation` or Data Annotations on DTOs. Requests with null/invalid fields reach the repository.

4. **DES Encryption**: `UrlEncryptionUtility` uses DES (broken since 1998). Upgrade to AES-256-GCM.

5. **Hardcoded Keys**: JWT key and DES key in source files/config. Move to Azure Key Vault or environment variables.

6. **ValidateIssuer/Audience = false**: JWT validation should include issuer and audience for zero-trust.

7. **AutoMapper**: Manual SqlDataReader mapping is error-prone. AutoMapper or Dapper would reduce boilerplate.

8. **IOptions Pattern**: `_configuration["PassbookURL"]` string indexing should use typed `IOptions<AppSettings>`.

9. **Health Checks**: `/health` endpoint exists but no detailed checks (DB connectivity, external service availability).

10. **Unit Tests**: No test project found. Add xUnit with Moq for controller and repository unit tests.

11. **production: false in prod environment**: `environment.prod.ts` has `production: false` — should be `true`.

## Frontend

1. **`ngOnDestroy` Missing**: `AppComponent` subscribes to OIDC observables but never unsubscribes — memory leak.

2. **No OnPush Change Detection**: All components use Default strategy. `OnPush` on table components would improve performance.

3. **No Error Handling in Services**: HTTP errors from API calls are not caught with `catchError` — uncaught errors crash the component.

4. **Client-Side Pagination**: All records loaded at once. For large datasets, implement server-side pagination.

5. **Lazy Loading**: All components are eagerly loaded. Split into feature modules with `loadChildren`.

6. **No Loading States for Errors**: NgxSpinner handles loading but there's no error UI state for failed API calls.

7. **`AuthorizationCanGuard` always true**: No actual auth check — remove or fix to prevent module loading for unauthenticated users.

8. **`CanLoad` Deprecated in Angular 16**: `CanLoad` is deprecated — use `CanMatch` guard instead.

9. **Token in SessionStorage**: SessionStorage is accessible to JavaScript — consider using HttpOnly cookies for token storage.

10. **OIDC Implicit Flow**: `id_token token` response type is deprecated. Migrate to Authorization Code + PKCE.

---

# REAL-TIME SCENARIOS

**Scenario 1**: A user verifies a payment, but the API returns status 3 (Error). How does your system handle this?
- The `WalletUpdateVerifiedDetails` endpoint returns `WalletCallResponse` with `Status = 3`
- Angular `PaymentMatchingVerificationComponent` checks the response status
- Currently: no explicit error toast/alert is shown — this is a gap. Ideally show a `MatSnackBar` with the error message.

**Scenario 2**: Two customer support agents verify the same wallet deposit simultaneously.
- `CS_Wallet_UpdateVerifiedDetails` stored procedure likely has a check to prevent double-verification
- `WalletAPIStatus.Pending = 2` or `Verified = 1` status indicates already processed
- The API returns the current status — the agent sees "Already verified" message via `WalletCallResponse.Message`
- Ideally: implement optimistic locking or row-level locking in the stored procedure

**Scenario 3**: The JWT token expires mid-session while the user is filling in verification details.
- `TokenInterceptor` checks `token_expiry` from sessionStorage before every request
- If expired, calls `TokenApiService.getApiToken()` to get a new token
- A shared promise prevents multiple simultaneous token requests (race condition prevention)
- New token stored in sessionStorage, original request retried with new token

**Scenario 4**: The database server is unreachable when a user tries to verify a payment.
- `SqlConnection.OpenAsync()` throws `SqlException`
- Repository catches it, logs with Serilog: `_logger.LogError(sqlEx, "SQL error...")`
- Exception is rethrown → controller receives it → ASP.NET returns 500
- Angular receives 500 → currently no error handling → UI shows no feedback. Gap: add `catchError` in service to show error message.

**Scenario 5**: A new environment (Stage) needs to be added to the Angular project.
- Create `src/environments/environment.stage.ts` with stage API URLs
- Add `stage` configuration in `angular.json` with `fileReplacements`
- Add npm script: `"build:stage": "ng build --configuration stage --base-href=/wallet/"`
- Update the `ServicesHelper` to use the new environment URLs

---

# HR + MANAGER ROUND QUESTIONS

1. **Tell me about the Payment Wallet Verification project.** 
   — "This is an internal customer support tool for verifying client wallet deposits. CS agents use it to match bank payments with wallet credit requests, then approve or reject them. It's a full-stack project with ASP.NET Core 8.0 Web API backend, Angular 16 frontend, and SQL Server database, deployed on AWS S3 (frontend) and internal servers (backend)."

2. **What was the most challenging part of building this project?**
   — "The authentication flow was complex — we use OpenID Connect for the Angular app and a separate JWT token for the API. The `TokenInterceptor` needed to handle token expiry gracefully without disrupting the user's workflow, including preventing race conditions when multiple API calls triggered simultaneous token refresh."

3. **How did you ensure data security in this project?**
   — "We use JWT authentication on all API endpoints, parameterized stored procedures to prevent SQL injection, and encrypt PII data (email addresses) using our shared `PII_Crypter` library. The passbook URLs are DES-encrypted before returning to the client."

4. **What would you improve about this project if given time?**
   — "I'd add FluentValidation for input validation, implement a global exception handler returning ProblemDetails, upgrade DES encryption to AES-256, add server-side pagination for better performance with large datasets, and add unit tests for the repository layer."

5. **How did you handle deployments across multiple environments?**
   — "We have four Angular build configurations (dev, qat9, stage, prod) with separate environment files and base-href settings. The backend reads configuration from `appsettings.json` with environment-specific overrides, and the connection string can be overridden via environment variable for cloud deployments."

6. **How do you approach code quality in this project?**
   — "We follow the Repository pattern to separate concerns, use interfaces for DI to keep code testable, and Serilog for structured logging to make debugging in production easier. The codebase could benefit from unit tests — that's something I'd prioritize in the next sprint."

---

# QUICK REVISION NOTES

## .NET Core

- `Program.cs`: Entry point → `WebApplication.CreateBuilder` → register services → `app.Build()` → configure middleware → `app.Run()`
- **Middleware order**: `UseCors` → `UseAuthentication` → `UseAuthorization` → `MapControllers`
- **Repository registered as**: `AddScoped<IWalletVerificationRepository, WalletVerificationRepository>()`
- **JWT key location**: `appsettings.json → Jwt:Key`
- **All methods are async**: `Task<T>` in interface, `async Task<T>` in implementation
- **Logging**: Serilog with `ILogger<T>` injection, `LogError(exception, "message", params)`
- **SQL access**: `SqlConnection` → `SqlCommand` (StoredProcedure) → `SqlDataReader` → manual mapping
- **Encryption**: DES for URLs (`UrlEncryptionUtility`), AES for emails (`Crypter.Operations`)
- **Enum**: `WalletAPIStatus` → `NotVerified=0, Verified=1, Pending=2, Error=3`

## Angular

- **App Module**: Declares 4 components, imports AuthModule (OIDC), MaterialModule, ReactiveFormsModule
- **Routing**: `/autologin` → `AutoLoginComponent`, `/VerifyWalletDeposits` → `WalletDepositsVerificationComponent` (guarded)
- **Guards**: `AuthorizationGuard` (CanActivate, checks OIDC auth), `AuthorizationCanGuard` (CanLoad, always true)
- **Interceptor**: `TokenInterceptor` → checks sessionStorage for JWT → fetches new token if expired → adds `Authorization: Bearer`
- **Services**: `PaymentVerificationService` (2 methods), `PMWalletVerificationService` (1 method), `TokenApiService` (token fetch), `UserInfoService` (BehaviorSubject)
- **State**: `UserInfoService.BehaviorSubject<UserInfo>` — set by AppComponent after OIDC login
- **Models**: `PaymentVerify`, `PaymentVerifySubmit`, `PMWalletVerificationData`, `UserInfo` (json2typescript)
- **Material**: `MatTable` + `MatSort` + `MatPaginator` for data display, `MatDialog` for verification popup
- **Environments**: 4 environments, API URLs differ per env, `environment.prod.ts` has bug: `production: false`

## SQL / Architecture

- **6 stored procedures** — all data access through stored procedures, no inline SQL
- **No EF** — raw ADO.NET with `SqlClient`
- **No transactions** in app code — likely handled inside stored procedures
- **Client-side pagination** — all records fetched, `MatPaginator` paginates in browser
- **Connection string** — from `appsettings.json` with env variable override

---

# TOP 10 STRONGEST CONCEPTS DEMONSTRATED IN THIS PROJECT

1. **Repository Pattern with Interface-based DI** — Clean separation via `IWalletVerificationRepository` and Scoped registration
2. **Async/Await End-to-End** — All DB operations are non-blocking async (interface, implementation, controller)
3. **JWT Bearer Authentication** — Full JWT validation pipeline with `[Authorize]` attribute protection
4. **OIDC Authentication Flow** — Complete OIDC integration with `angular-auth-oidc-client` including callback handling and loop prevention
5. **HTTP Interceptor with Token Management** — Sophisticated token caching, expiry detection, and race condition prevention
6. **SQL Parameterization (Anti-Injection)** — All stored procedure calls use `SqlParameter` objects
7. **Angular Material Data Table** — Full `MatTable` + `MatSort` + `MatPaginator` + `MatTableDataSource` implementation
8. **Multi-Environment Configuration** — 4 Angular environments + backend `appsettings` with env variable override
9. **Structured Logging with Serilog** — Named placeholders, `ILogger<T>`, request logging middleware
10. **Reactive State with BehaviorSubject** — `UserInfoService` broadcasting user state across components

---

# TOP 10 CONCEPTS MISSING OR WEAK IN THIS PROJECT

1. **Global Exception Handling** — No `ProblemDetails` middleware; unhandled exceptions return raw stack traces
2. **Input Validation** — No FluentValidation or DataAnnotations on request DTOs
3. **Unit Tests** — No test project; repository and controller logic is untested
4. **Angular Error Handling** — HTTP errors have no `catchError`; API failures silently fail in UI
5. **Lazy Loading** — `CanLoad` guard exists but all modules are eagerly loaded; no `loadChildren`
6. **Weak Encryption** — `UrlEncryptionUtility` uses DES (deprecated 1990s algorithm)
7. **Secrets Management** — JWT key and API key are in `appsettings.json`, not in Key Vault
8. **Server-Side Pagination** — All records fetched at once; performance will degrade with large datasets
9. **OnPush Change Detection** — All components use Default strategy; no performance optimization for large lists
10. **Observable Memory Leaks** — `AppComponent` OIDC subscriptions lack `ngOnDestroy` unsubscribe / `takeUntil` pattern
