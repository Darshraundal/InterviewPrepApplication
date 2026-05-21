# FolioTrack — Complete Interview Preparation Guide
> Project: FolioTrack (Portfolio Management SaaS)
> Stack: Angular 19 + ASP.NET Core 10 + MySQL + Python FastAPI
> Target: 3–5 Years Experienced Developer Interviews

---

## PROJECT ARCHITECTURE SUMMARY

### Complete Architecture Flow

FolioTrack is a three-tier SaaS application:

```
[Angular 19 SPA :4200]
       │  JWT in every HTTP header (AuthInterceptor)
       ▼
[ASP.NET Core 10 API :5031]
       │  EF Core + MySQL queries
       ▼
[MySQL 8 — portfolio_db]

       + side integration:
[ASP.NET Core 10 API] ──HTTP──► [FastAPI CAS Parser :8001]
[ASP.NET Core 10 API] ──HTTP──► [mfapi.in — live NAV]
[ASP.NET Core 10 API] ──HTTP──► [Google Gemini 2.0 Flash]
[ASP.NET Core 10 API] ──HTTP──► [Razorpay — payments]
[ASP.NET Core 10 API] ──HTTP──► [AMFI — fund holdings data]
```

### Frontend-to-Backend Request Lifecycle

1. User action in Angular component (e.g., click "Load Dashboard")
2. Component calls a service method (e.g., `InvestmentService.getDashboardSummary()`)
3. Service issues `HttpClient.get()` — Angular's `HttpClientModule` pipes the request through `AuthInterceptor`
4. `AuthInterceptor` reads JWT from localStorage and appends `Authorization: Bearer <token>` header
5. Request hits the .NET API at port 5031
6. `ExceptionMiddleware` wraps the pipeline — any unhandled exception is caught and mapped to an HTTP status
7. JWT middleware validates the Bearer token; if invalid → 401
8. Controller action runs — extracts `UserId` from `ClaimTypes.NameIdentifier`
9. Controller calls the relevant Service; Service uses `AppDbContext` (EF Core) to query MySQL
10. External calls (NAV, Gemini, etc.) happen inside Services
11. Service returns DTO; Controller returns `Ok(dto)`
12. Response travels back through `ExceptionMiddleware` and Angular `HttpClient` → observable emits in component

### Authentication Flow

```
Register:
  Angular RegisterComponent → POST /auth/register
  → AuthService.RegisterAsync: hash password (BCrypt), save User (FREE plan)
  → JwtHelper.GenerateToken(userId, email, "FREE") — 7-day expiry
  → Returns AuthResponseDto {token, userId, email, fullName, subscriptionPlan}
  → Angular: localStorage.setItem + BehaviorSubject update

Login:
  Angular LoginComponent → POST /auth/login
  → AuthService.LoginAsync: verify BCrypt hash, sync subscription plan from Subscriptions table
  → JwtHelper.GenerateToken — same structure
  → Returns same AuthResponseDto

Subsequent requests:
  → AuthInterceptor reads token → adds header
  → .NET JWT middleware validates HS256 signature + expiry + issuer/audience
  → ClaimsPrincipal available in controllers via User.FindFirst()

Logout:
  → Angular: localStorage.clear() + BehaviorSubject(null) + router.navigate('/auth/login')
```

### API Communication Flow

- RESTful JSON over HTTP
- All endpoints except `/auth/register`, `/auth/login`, `/webhook/razorpay` require `[Authorize]`
- Controllers read `userId` via `int.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value)`
- DTOs flow both ways — request bodies are strongly typed, responses are structured DTO objects
- Error responses: `ExceptionMiddleware` returns `{ message: "..." }` JSON with the appropriate HTTP status

### Database Interaction Flow

- EF Core Code-First with migrations
- `AppDbContext` exposes `DbSet<T>` for each entity
- Services inject `AppDbContext` directly (no explicit repository pattern)
- LINQ queries translated to MySQL SQL by EF Core provider
- Unique indexes enforced at DB level: `User.Email`, `MutualFundScheme.SchemeCode`, composite `(AiUsageLog.UserId, YearMonth)`

---

# .NET / ASP.NET CORE

---

QUESTION:
What is the MVC architecture and how does your project use it?

ANSWER:
MVC stands for Model-View-Controller. In ASP.NET Core Web API, we use the MC part — Models (entities + DTOs) and Controllers. There are no server-rendered Views because Angular is the frontend. The separation keeps business logic in Services, data shape in DTOs, and HTTP routing in Controllers.

PROJECT EXAMPLE:
- File: `Controllers/DashboardController.cs`
- Class: `DashboardController`
- Method: `GetSummary()`
- The controller calls `DashboardService.GetSummaryAsync(userId)`, which performs all business logic, and the controller simply returns `Ok(result)`. The model is `DashboardSummaryDto`.

FOLLOW-UP QUESTIONS:
1. Why use Web API instead of MVC with Razor views?
2. How do you handle model validation in your controllers?
3. What is the difference between `[ApiController]` and `[Controller]`?

IMPORTANT FOR INTERVIEW:
`[ApiController]` attribute enables automatic model validation (400 if ModelState is invalid), binding source inference, and problem details responses. This project uses it on all controllers.

---

QUESTION:
Explain the middleware pipeline in your project. How does ExceptionMiddleware work?

ANSWER:
Middleware in ASP.NET Core is a pipeline of components that process HTTP requests and responses in order. Each middleware calls `next()` to pass to the next component. In this project, the custom `ExceptionMiddleware` wraps the entire pipeline to catch unhandled exceptions globally.

PROJECT EXAMPLE:
- File: `Middleware/ExceptionMiddleware.cs`
- Class: `ExceptionMiddleware`
- Method: `InvokeAsync(HttpContext)`

Implementation:
```csharp
public async Task InvokeAsync(HttpContext context) {
    try {
        await _next(context);  // run the rest of the pipeline
    } catch (UnauthorizedAccessException ex) {
        context.Response.StatusCode = 401;
        await context.Response.WriteAsJsonAsync(new { message = ex.Message });
    } catch (KeyNotFoundException ex) {
        context.Response.StatusCode = 404;
        // ...
    } catch (Exception ex) {
        context.Response.StatusCode = 500;
        // ...
    }
}
```

Registered in `Program.cs` before `app.UseAuthentication()` so it catches auth errors too.

FOLLOW-UP QUESTIONS:
1. What is the order of middleware registration and why does it matter?
2. How is this different from action filters or `[ExceptionFilter]`?
3. Can you add middleware per-route? (No — middleware is global; use filters for per-route)

IMPORTANT FOR INTERVIEW:
Order matters critically: `ExceptionMiddleware` → `UseAuthentication` → `UseAuthorization` → `MapControllers`. If you put authorization before exception middleware, 401 errors won't be caught properly.

---

QUESTION:
Explain Dependency Injection in your project. What service lifetimes are used?

ANSWER:
ASP.NET Core has a built-in IoC container. Services are registered in `Program.cs` and injected via constructor parameters. There are three lifetimes:
- **Transient**: New instance every time requested
- **Scoped**: One instance per HTTP request
- **Singleton**: One instance for the entire application lifetime

PROJECT EXAMPLE:
- File: `Program.cs`

```csharp
// Scoped (default for most services)
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<InvestmentService>();
builder.Services.AddScoped<DashboardService>();
builder.Services.AddScoped<OverlapService>();
builder.Services.AddScoped<AiInsightService>();
builder.Services.AddScoped<SubscriptionService>();

// Singleton (for in-memory caching and background work)
builder.Services.AddSingleton<FundHoldingsService>();

// HttpClient via factory (manages connection pooling)
builder.Services.AddHttpClient<MfApiService>();
builder.Services.AddHttpClient<CasParserClient>(client => {
    client.BaseAddress = new Uri(config["CasParserService:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(60);
});
```

`FundHoldingsService` is a Singleton because it caches fund holdings in memory and runs background fetch tasks. Making it Scoped would lose the cache on every request.

FOLLOW-UP QUESTIONS:
1. What happens if you inject a Scoped service into a Singleton? (Captive dependency — throws at runtime)
2. How does `AddHttpClient` differ from `new HttpClient()`?
3. What is `IServiceProvider` and when would you use it directly?

IMPORTANT FOR INTERVIEW:
Captive dependency anti-pattern: Singleton holding a Scoped dependency leads to the Scoped service never being disposed. The runtime warns about this. Solution: inject `IServiceScopeFactory` into the Singleton and create scopes manually (as `FundHoldingsService` does with background tasks).

---

QUESTION:
How does JWT authentication and authorization work in your project?

ANSWER:
JWT (JSON Web Token) is a stateless authentication mechanism. The server creates a signed token containing claims (userId, email, subscriptionPlan), and the client sends it in the `Authorization: Bearer` header. The server validates the signature and reads claims without a DB lookup.

PROJECT EXAMPLE:
- File: `Helpers/JwtHelper.cs`
- File: `Program.cs` (JWT middleware config)
- File: `frontend/src/app/core/interceptors/auth.interceptor.ts`

Token Generation (`JwtHelper.cs`):
```csharp
var tokenDescriptor = new SecurityTokenDescriptor {
    Subject = new ClaimsIdentity(new[] {
        new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
        new Claim(ClaimTypes.Email, email),
        new Claim("subscriptionPlan", subscriptionPlan)
    }),
    Expires = DateTime.UtcNow.AddDays(7),
    SigningCredentials = new SigningCredentials(
        new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secret)),
        SecurityAlgorithms.HmacSha256Signature)
};
```

Validation in `Program.cs`:
```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(keyBytes),
            ValidateIssuer = true, ValidIssuer = "PortfolioApp",
            ValidateAudience = true, ValidAudience = "PortfolioApp",
            ValidateLifetime = true
        };
    });
```

Angular side (`auth.interceptor.ts`): reads token from localStorage, clones request with `Authorization` header, catches 401 to trigger logout.

FOLLOW-UP QUESTIONS:
1. Why store the JWT in localStorage vs httpOnly cookies? (XSS risk vs CSRF risk tradeoff)
2. How would you implement token refresh? (Not in this project — would need a refresh token endpoint)
3. What claims are in your token and why?

IMPORTANT FOR INTERVIEW:
The `subscriptionPlan` claim in the JWT means the frontend doesn't need a separate API call to check if user is PRO. But the claim becomes stale after upgrade — this project handles it by returning a new JWT after successful payment verification (`SubscriptionService.VerifyAndUpgradeAsync` returns fresh JWT).

---

QUESTION:
How does your project implement API routing?

ANSWER:
ASP.NET Core uses attribute routing. Each controller has a `[Route]` attribute and each action has `[HttpGet]`, `[HttpPost]`, etc. The route template uses `[controller]` placeholder which resolves to the controller name minus "Controller".

PROJECT EXAMPLE:
- File: `Controllers/InvestmentController.cs`

```csharp
[ApiController]
[Route("api/[controller]")]   // → /api/investment
[Authorize]
public class InvestmentController : ControllerBase {
    [HttpGet]                          // GET /api/investment
    [HttpPost]                         // POST /api/investment
    [HttpPut("{id}")]                  // PUT /api/investment/5
    [HttpDelete("{id}")]               // DELETE /api/investment/5
    [HttpPost("import-cas")]           // POST /api/investment/import-cas
    [HttpPost("refresh-holdings")]     // POST /api/investment/refresh-holdings
}
```

FOLLOW-UP QUESTIONS:
1. What is the difference between attribute routing and conventional routing?
2. How do you handle route conflicts?
3. How does `[FromBody]`, `[FromQuery]`, `[FromRoute]` differ?

IMPORTANT FOR INTERVIEW:
This project uses `api/[controller]` prefix for all API routes. The `[ApiController]` attribute enables automatic binding source inference — parameters that match route tokens are `[FromRoute]`, complex types from body are `[FromBody]` automatically.

---

QUESTION:
Explain Entity Framework Core usage in your project. Is it Code First or Database First?

ANSWER:
This project uses Code First with EF Core. Entity classes are defined in C#, and EF Core generates the database schema via migrations. The `AppDbContext` configures relationships using Fluent API and Data Annotations.

PROJECT EXAMPLE:
- File: `Data/AppDbContext.cs`
- File: `Migrations/`

Key configuration in `AppDbContext`:
```csharp
modelBuilder.Entity<User>()
    .HasIndex(u => u.Email).IsUnique();

modelBuilder.Entity<AiUsageLog>()
    .HasIndex(a => new { a.UserId, a.YearMonth }).IsUnique();

modelBuilder.Entity<Investment>()
    .HasOne(i => i.User)
    .WithMany(u => u.Investments)
    .HasForeignKey(i => i.UserId);
```

Migrations:
- `CreateInitialCreate` — baseline schema (Users, Investments, MutualFundSchemes, FundHoldings, etc.)
- `AddWithdrawalDateToInvestment` — added `WithdrawalDate` column

Running migrations:
```bash
dotnet ef migrations add <Name>
dotnet ef database update
```

FOLLOW-UP QUESTIONS:
1. What is the difference between Code First and Database First?
2. How do you handle migrations in production? (Apply on startup or CI/CD pipeline)
3. What is the difference between `.Include()` (eager loading) and lazy loading?

IMPORTANT FOR INTERVIEW:
The project does not use `.Include()` extensively — it loads related data in subsequent queries. This is intentional in some places (like `DashboardService`) to avoid over-fetching. In an enterprise app, you'd consider explicit loading or projections with `.Select()` for better performance.

---

QUESTION:
What is IQueryable vs IEnumerable in EF Core? How is it relevant to your project?

ANSWER:
- `IQueryable<T>`: Query is built as an expression tree and executed in the database. Filters and projections are translated to SQL — only matching rows are fetched.
- `IEnumerable<T>`: Once you call `.ToList()` or iterate, all rows are loaded into memory. Further LINQ runs in C#, not SQL.

PROJECT EXAMPLE:
- File: `Services/DashboardService.cs`

```csharp
// IQueryable — filter translated to SQL, only user's investments fetched
var investments = await _db.Investments
    .Where(i => i.UserId == userId)    // WHERE clause in SQL
    .ToListAsync();                     // executes here

// After .ToListAsync(), it's in-memory IEnumerable
var grouped = investments.GroupBy(i => i.Isin ?? $"__noisin_{i.Id}");
// GroupBy runs in C# (complex grouping logic not easily SQL-translatable)
```

FOLLOW-UP QUESTIONS:
1. When would you use `.AsNoTracking()`?
2. What is the N+1 query problem and does your project have it?
3. How do you view the SQL generated by EF Core?

IMPORTANT FOR INTERVIEW:
This project does `.Where(userId).ToListAsync()` and then does grouping in C#. For the current scale (personal portfolio, <100 holdings), this is fine. At larger scale, you'd push more computation to SQL or use raw SQL queries via `FromSqlRaw()`. The project has a potential N+1 in `GetAllAsync` where it calls `MfApiService` per ISIN — mitigated by batch NAV fetch.

---

QUESTION:
How does your project use async/await?

ANSWER:
All I/O-bound operations (DB queries, HTTP calls) use async/await throughout. This prevents thread blocking on the thread pool, enabling the server to handle more concurrent requests.

PROJECT EXAMPLE:
- File: `Services/InvestmentService.cs`

```csharp
public async Task<List<InvestmentDto>> GetAllAsync(int userId) {
    var investments = await _db.Investments
        .Where(i => i.UserId == userId)
        .ToListAsync();                    // async DB call

    var navMap = await _mfApiService       // async HTTP call
        .GetCurrentNavBatchAsync(isins);
    
    return investments.Select(inv => MapToDto(inv, navMap)).ToList();
}
```

Background work in `InvestmentController.ImportCas`:
```csharp
// Fire-and-forget for non-critical background work
_ = Task.Run(() => _fundHoldingsService.EnsureHoldingsInBackground(schemeCodes));
```

FOLLOW-UP QUESTIONS:
1. What is `ConfigureAwait(false)` and when should you use it?
2. What is the difference between `Task.Run()` and `await`?
3. What happens when you use `async void`?

IMPORTANT FOR INTERVIEW:
`Task.Run()` is used for the background fund holdings fetch — fire-and-forget so the CAS import response returns immediately to the user without waiting for AMFI scraping (which can take several seconds). The risk is unhandled exceptions in the background task are swallowed — the project logs them but doesn't propagate to the user.

---

QUESTION:
Explain SOLID principles in the context of your project.

ANSWER:

**S — Single Responsibility**: Each service handles one domain. `AuthService` only handles auth. `DashboardService` only aggregates portfolio data. `GeminiService` only calls the Gemini API.

**O — Open/Closed**: Not fully demonstrated — there's no explicit interface abstraction for services (most are concrete classes). For extension, you'd add `IGeminiService` and swap implementations.

**L — Liskov Substitution**: Not directly applicable since there's no inheritance hierarchy in services.

**I — Interface Segregation**: The project currently does NOT implement service interfaces (e.g., no `IInvestmentService`). This is a missing best practice.

**D — Dependency Inversion**: High-level modules (Controllers) depend on abstractions/services injected by DI, not on `new ClassName()`. Controllers never instantiate services directly.

PROJECT EXAMPLE:
- File: `Controllers/DashboardController.cs`
```csharp
public DashboardController(DashboardService dashboardService) {
    _dashboardService = dashboardService;  // DI — not new DashboardService()
}
```

FOLLOW-UP QUESTIONS:
1. How would you add unit tests without interfaces?
2. How would you refactor to add `IDashboardService`?
3. What is the practical benefit of dependency inversion here?

IMPORTANT FOR INTERVIEW:
This project demonstrates DI (Dependency Inversion) through the container but does not define interfaces for services. For interviews, acknowledge this and say: "Ideally, each service would have an interface like `IInvestmentService`. This enables mocking in unit tests and allows swapping implementations (e.g., replacing MySQL with MongoDB) without touching controllers."

---

QUESTION:
Explain exception handling in your project.

ANSWER:
The project uses a two-layer exception handling strategy:
1. **Custom ExceptionMiddleware** — global catch-all for unhandled exceptions, maps exception types to HTTP status codes
2. **Service-level exceptions** — Services throw typed exceptions (`KeyNotFoundException`, `InvalidOperationException`, `ArgumentException`) which the middleware catches and translates

PROJECT EXAMPLE:
- File: `Middleware/ExceptionMiddleware.cs`

```csharp
catch (UnauthorizedAccessException ex) → 401
catch (KeyNotFoundException ex)        → 404
catch (ArgumentException ex)           → 400
catch (InvalidOperationException ex)   → 409 Conflict
catch (Exception ex)                   → 500
```

Services throw:
```csharp
// AiInsightService.cs
if (user.SubscriptionPlan != "PRO")
    throw new UnauthorizedAccessException("Pro plan required");

if ((usage?.RequestCount ?? 0) >= limit)
    throw new InvalidOperationException("Monthly AI insight limit reached");
```

FOLLOW-UP QUESTIONS:
1. What is the difference between middleware-based and filter-based exception handling?
2. How would you add correlation IDs to error responses for debugging?
3. Should you log the full stack trace in production?

IMPORTANT FOR INTERVIEW:
The exception-to-HTTP-status mapping is explicit and predictable. The pattern: Services speak in domain exceptions, middleware speaks in HTTP. This separation means Service code never directly writes to `HttpContext` — cleaner and more testable.

---

QUESTION:
How is CORS configured in your project?

ANSWER:
CORS (Cross-Origin Resource Sharing) is needed because the Angular app on port 4200 calls the API on port 5031 — different ports = different origin. The server must explicitly allow this.

PROJECT EXAMPLE:
- File: `Program.cs`

```csharp
builder.Services.AddCors(options => {
    options.AddPolicy("AllowAngular", policy => {
        policy.WithOrigins("http://localhost:4200")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

app.UseCors("AllowAngular");  // placed before UseAuthentication
```

FOLLOW-UP QUESTIONS:
1. What is a preflight request and when does it happen?
2. How would you configure CORS for production? (Environment-specific allowed origins)
3. What is the difference between CORS and CSRF?

IMPORTANT FOR INTERVIEW:
This project allows only `localhost:4200`. For production, this needs to be updated to the actual domain. Hardcoding localhost in production is a security misconfiguration — the CLAUDE.md notes this explicitly. Best practice: read allowed origins from `appsettings.json`.

---

QUESTION:
How does your project use LINQ?

ANSWER:
LINQ (Language Integrated Query) is used extensively in Services for both database queries (translated to SQL via EF Core) and in-memory collection manipulation.

PROJECT EXAMPLE:
- File: `Services/DashboardService.cs`

```csharp
// DB query (translated to SQL)
var investments = await _db.Investments
    .Where(i => i.UserId == userId && i.Quantity > 0)
    .ToListAsync();

// In-memory grouping and projection
var grouped = investments
    .GroupBy(i => i.Isin ?? $"__noisin_{i.Id}")
    .Select(g => new {
        FundName = g.First().FundName,
        TotalInvested = g.Where(x => x.AmountInvested > 0).Sum(x => x.AmountInvested),
        TotalUnits = g.Sum(x => x.Quantity ?? 0m)
    }).ToList();
```

Overlap calculation (`OverlapService.cs`):
```csharp
var common = mapA.Keys.Intersect(mapB.Keys);
decimal overlap = common.Sum(s => Math.Min(mapA[s], mapB[s]));
```

FOLLOW-UP QUESTIONS:
1. What is deferred execution in LINQ?
2. What is the difference between `.Select()` and `.SelectMany()`?
3. How would you optimize a LINQ query that's causing N+1?

IMPORTANT FOR INTERVIEW:
LINQ deferred execution means the query is built but not executed until iterated. `.ToList()` / `.ToListAsync()` forces execution. In this project, after `.ToListAsync()`, all LINQ runs in-memory (C#), not SQL — GroupBy, Sum, OrderBy on the list are all in-process.

---

QUESTION:
Does your project use the Repository Pattern?

ANSWER:
No, this project does NOT implement the Repository Pattern formally. Services inject `AppDbContext` directly and query it using EF Core's `DbSet<T>`. This is a valid approach for small-to-medium projects where the added abstraction of a repository doesn't justify the complexity.

PROJECT EXAMPLE:
- File: `Services/AuthService.cs`

```csharp
public class AuthService {
    private readonly AppDbContext _db;
    
    public async Task<AuthResponseDto> LoginAsync(LoginRequestDto request) {
        var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == request.Email);
        // Direct DbSet query — no repository layer
    }
}
```

FOLLOW-UP QUESTIONS:
1. What are the benefits of Repository Pattern? (Abstraction, testability, swappable data store)
2. When would you add it to this project?
3. What is the Unit of Work pattern and how does EF Core already implement it?

IMPORTANT FOR INTERVIEW:
EF Core's `DbContext` is itself an implementation of the Unit of Work pattern — it tracks changes and commits them all at once via `SaveChangesAsync()`. Adding another repository layer on top is often redundant. For this project, acknowledge the trade-off: "I chose direct DbContext access for simplicity. If the project grew to need multiple data sources or complex unit testing, I'd add repository interfaces."

---

QUESTION:
How does your project handle logging?

ANSWER:
This project uses the built-in ASP.NET Core `ILogger<T>` injected into services. It relies on the default logging pipeline (Console provider in development). There is no structured logging library (like Serilog) or centralized log aggregation.

PROJECT EXAMPLE:
- File: `Services/MfApiService.cs`

```csharp
private readonly ILogger<MfApiService> _logger;

_logger.LogWarning("Failed to fetch NAV for {SchemeCode}, using cached value", schemeCode);
_logger.LogError(ex, "Error calling mfapi.in: {Message}", ex.Message);
```

FOLLOW-UP QUESTIONS:
1. What is the difference between `LogWarning`, `LogError`, and `LogCritical`?
2. How would you add Serilog with file/Seq output?
3. How do log levels filter output?

IMPORTANT FOR INTERVIEW:
This project does not implement structured logging (Serilog/NLog), distributed tracing (OpenTelemetry), or centralized log storage. For production, this should be enhanced. Mention: "I'd add Serilog with a sink to a service like Seq or Application Insights for searchable, structured logs."

---

QUESTION:
How does your project manage configuration?

ANSWER:
Configuration is managed via `appsettings.json` (with environment-specific overrides) and .NET User Secrets for local development (to keep API keys out of source control).

PROJECT EXAMPLE:
- File: `Program.cs`

```csharp
var config = builder.Configuration;
// Reads from appsettings.json, then appsettings.Development.json, then env vars, then user secrets
var connectionString = config.GetConnectionString("DefaultConnection");
var jwtSecret = config["Jwt:Secret"];
var geminiKey = config["Gemini:ApiKey"];
```

User secrets (local dev):
```bash
dotnet user-secrets set "Jwt:Secret" "your-secret-here"
dotnet user-secrets set "Gemini:ApiKey" "your-key-here"
```

FOLLOW-UP QUESTIONS:
1. What is the configuration provider precedence order in ASP.NET Core?
2. How do you use `IOptions<T>` for strongly-typed configuration?
3. How would you manage secrets in production (Azure Key Vault, AWS SSM)?

IMPORTANT FOR INTERVIEW:
The project uses User Secrets for local dev (secrets not in source control). The `appsettings.json` in the repo has placeholder values. The configuration provider priority (lowest to highest): `appsettings.json` → `appsettings.{Environment}.json` → Environment Variables → User Secrets.

---

QUESTION:
How does your project use DTOs and why are they important?

ANSWER:
DTOs (Data Transfer Objects) decouple the API contract from the internal database entities. They shape exactly what data enters and leaves the API, preventing over-posting and over-fetching.

PROJECT EXAMPLE:
- File: `Models/DTOs/Investment/InvestmentDto.cs`

The `Investment` entity has: `Id, UserId, AssetType, FundName, Isin, SchemeCode, AmountInvested, Quantity, PurchaseDate, WithdrawalDate`

The `InvestmentDto` adds computed fields: `CurrentNav, CurrentValue, Gain, RoiPct` — which are not in the DB, calculated at service time from live NAV data.

```csharp
public class InvestmentDto {
    public int Id { get; set; }
    public string FundName { get; set; }
    public decimal AmountInvested { get; set; }
    public decimal CurrentValue { get; set; }   // computed
    public decimal RoiPct { get; set; }          // computed — not in DB
}
```

FOLLOW-UP QUESTIONS:
1. Why not use AutoMapper? (Project chose manual mapping — less magic, easier debugging)
2. What is over-posting and how do DTOs prevent it?
3. When would you use FluentValidation vs data annotations for DTO validation?

IMPORTANT FOR INTERVIEW:
This project does NOT use AutoMapper — all DTO mapping is manual in Services. This is a deliberate choice for clarity. The benefit: explicit control over what's mapped. The cost: more boilerplate. For production, AutoMapper or Mapster would reduce repetition.

---

QUESTION:
How does your project implement API security beyond JWT?

ANSWER:
1. **JWT authentication** on all endpoints except public ones
2. **Subscription-level authorization**: `AiInsightService` and `SubscriptionService` check `subscriptionPlan` claim — PRO features reject FREE users at service level
3. **Razorpay webhook signature verification**: HMAC-SHA256 to authenticate webhook calls
4. **CORS restriction**: Only `localhost:4200` origin
5. **Password hashing**: BCrypt with default work factor
6. **Input validation**: `[Required]`, `[EmailAddress]`, model binding validates requests

PROJECT EXAMPLE:
- File: `Services/RazorpayService.cs`

```csharp
// HMAC-SHA256 signature verification for webhooks
var generatedSignature = GenerateHmacSignature(payload, _webhookSecret);
return CryptographicOperations.FixedTimeEquals(
    Encoding.UTF8.GetBytes(generatedSignature),
    Encoding.UTF8.GetBytes(receivedSignature)
);
```

FOLLOW-UP QUESTIONS:
1. Why use `FixedTimeEquals` instead of `==` for signature comparison? (Timing attack prevention)
2. What is HMAC and how does it differ from symmetric encryption?
3. What are the missing security headers (HSTS, X-Frame-Options, CSP)?

IMPORTANT FOR INTERVIEW:
`FixedTimeEquals` is crucial — regular `==` comparison short-circuits on first mismatch, making it vulnerable to timing attacks that could guess the signature byte by byte. The project correctly uses constant-time comparison.

---

QUESTION:
Explain how GeminiService handles rate limiting and retries.

ANSWER:
Gemini has an API rate limit. The service uses a `SemaphoreSlim(1,1)` to serialize all Gemini calls (only one at a time), plus retry logic with exponential backoff.

PROJECT EXAMPLE:
- File: `Services/GeminiService.cs`

```csharp
private static readonly SemaphoreSlim _semaphore = new SemaphoreSlim(1, 1);
private static readonly int[] _retryDelays = { 3000, 8000 };  // ms

public async Task<string> GenerateInsightAsync(string prompt) {
    await _semaphore.WaitAsync();  // acquire lock — blocks other calls
    try {
        for (int attempt = 0; attempt <= _retryDelays.Length; attempt++) {
            var response = await _httpClient.PostAsJsonAsync(url, body);
            if (response.StatusCode == HttpStatusCode.TooManyRequests) {
                if (attempt < _retryDelays.Length)
                    await Task.Delay(_retryDelays[attempt]);
                else
                    throw new InvalidOperationException("Gemini rate limit");
                continue;
            }
            return await ParseResponse(response);
        }
    } finally {
        _semaphore.Release();  // always release, even on exception
    }
}
```

FOLLOW-UP QUESTIONS:
1. What is the difference between `SemaphoreSlim` and `Mutex`?
2. When would exponential backoff with jitter be better than fixed delays?
3. What are the downsides of serializing all AI calls?

IMPORTANT FOR INTERVIEW:
`static readonly SemaphoreSlim` means it's shared across all requests. If User A is generating an insight, User B's request waits at `WaitAsync()`. This prevents 429s but adds latency. For production, you'd use a distributed rate limiter (e.g., Redis token bucket) and process user requests independently.

---

QUESTION:
What is Task vs Thread in .NET? How does your project use them?

ANSWER:
- **Thread**: OS-level thread. Creating threads is expensive (1MB stack, OS scheduling overhead).
- **Task**: Abstraction over thread pool. Reuses threads from a pool; `async/await` uses Tasks to handle I/O without blocking threads.

PROJECT EXAMPLE:
- File: `Controllers/InvestmentController.cs`

```csharp
// Task.Run — offloads work to thread pool, fire-and-forget
_ = Task.Run(() => _fundHoldingsService.EnsureHoldingsInBackground(schemeCodes));
```

All service methods return `Task<T>` for async operations:
```csharp
public async Task<DashboardSummaryDto> GetSummaryAsync(int userId) { ... }
```

FOLLOW-UP QUESTIONS:
1. What is `ValueTask` and when is it preferred over `Task`?
2. When would you use `Parallel.ForEachAsync()`?
3. What is thread starvation and how does async/await prevent it?

IMPORTANT FOR INTERVIEW:
The fire-and-forget `Task.Run()` in `ImportCas` has a risk: if `EnsureHoldingsInBackground` throws an unhandled exception, it's silently swallowed (no user feedback). The project logs it, but in production you'd want to at minimum log a critical error and potentially send it to an error tracking service.

---

QUESTION:
Does your project use AutoMapper or manual DTO mapping?

ANSWER:
Manual mapping — no AutoMapper. Services explicitly create DTOs from entities, including computed fields that have no source in the entity.

PROJECT EXAMPLE:
- File: `Services/InvestmentService.cs`

```csharp
private InvestmentDto MapToDto(Investment inv, Dictionary<string, decimal> navMap) {
    var nav = navMap.GetValueOrDefault(inv.Isin ?? "");
    var currentValue = (inv.Quantity ?? 0) * nav;
    var gain = currentValue - inv.AmountInvested;
    return new InvestmentDto {
        Id = inv.Id,
        FundName = inv.FundName,
        AmountInvested = inv.AmountInvested,
        CurrentNav = nav,
        CurrentValue = currentValue,
        Gain = gain,
        RoiPct = inv.AmountInvested > 0 ? (gain / inv.AmountInvested) * 100 : 0
    };
}
```

FOLLOW-UP QUESTIONS:
1. What are the pros/cons of AutoMapper vs manual mapping?
2. How does AutoMapper handle complex mappings like this one with computed fields?
3. What is Mapster and how does it differ from AutoMapper?

IMPORTANT FOR INTERVIEW:
Manual mapping works well here because many DTO fields are computed (ROI, current value) and require business logic — AutoMapper is best for simple 1:1 property mapping. For the CRUD-heavy parts (create/update investment), AutoMapper would save boilerplate.

---

QUESTION:
Explain how Garbage Collection works in .NET and any relevant patterns in your project.

ANSWER:
.NET GC is generational (Gen0, Gen1, Gen2). Short-lived objects are collected quickly from Gen0. Long-lived objects survive to Gen2. Large objects go to the LOH (Large Object Heap).

PROJECT EXAMPLE:
- File: `Services/FundHoldingsService.cs`

`FundHoldingsService` is a Singleton — its in-memory data lives in Gen2 (long-lived). This is intentional: the fund holdings data is expensive to fetch and should persist across requests.

The service does NOT implement `IDisposable` — not an issue here since it has no unmanaged resources. However, the `HttpClient` instances it creates should ideally be pooled (via `IHttpClientFactory`).

FOLLOW-UP QUESTIONS:
1. What is `IDisposable` and when should you implement it?
2. What is the difference between `GC.Collect()` and letting GC run naturally?
3. What is memory pressure and how does large object allocation affect GC?

IMPORTANT FOR INTERVIEW:
The project registers `HttpClient` via `AddHttpClient<T>()` (IHttpClientFactory pattern) for `MfApiService` and `CasParserClient` — this correctly avoids socket exhaustion that occurs when creating `new HttpClient()` repeatedly, since HttpClient does not properly release connections when disposed.

---

# ANGULAR

---

QUESTION:
Describe the Angular architecture of your project.

ANSWER:
The project uses feature-based NgModule architecture (not standalone components). Each feature is a lazy-loaded module. Core services and guards live in a `CoreModule`-style directory. Shared/reusable components are in `SharedModule`.

PROJECT EXAMPLE:
- File: `frontend/src/app/app-routing.module.ts`
- File: `frontend/src/app/app.module.ts`

```typescript
const routes: Routes = [
  { path: '', component: ShellComponent, canActivate: [AuthGuard], children: [
    { path: 'dashboard',         loadChildren: () => import('./features/dashboard/...')},
    { path: 'portfolio',         loadChildren: () => import('./features/portfolio/...')},
    { path: 'overlap-analysis',  loadChildren: () => import('./features/overlap-analysis/...'),
                                 canActivate: [ProPlanGuard] },
    { path: 'ai-insights',       loadChildren: () => import('./features/ai-insights/...'),
                                 canActivate: [ProPlanGuard] },
    { path: 'subscription',      loadChildren: () => import('./features/subscription/...')},
    { path: 'calculators',       loadChildren: () => import('./features/calculators/...')},
  ]},
  { path: 'auth', loadChildren: () => import('./features/auth/...') }
];
```

FOLLOW-UP QUESTIONS:
1. What is the difference between NgModules and Standalone components (Angular 14+)?
2. Why choose feature-based module structure over type-based (all services in one folder)?
3. What is the difference between `AppModule` declarations and feature module declarations?

IMPORTANT FOR INTERVIEW:
The project uses Angular 19 but with NgModules (not the newer standalone API). This is a valid choice for existing codebases. Acknowledge that Angular 14+ introduced standalone components as the preferred approach, but NgModules are fully supported and widely used in enterprise projects.

---

QUESTION:
How does lazy loading work in your Angular project?

ANSWER:
Lazy loading means feature module JavaScript bundles are only downloaded when the user navigates to that route. This reduces the initial bundle size (faster first load). Angular's router handles this transparently.

PROJECT EXAMPLE:
- File: `frontend/src/app/app-routing.module.ts`

```typescript
{
  path: 'overlap-analysis',
  loadChildren: () => import('./features/overlap-analysis/overlap-analysis.module')
    .then(m => m.OverlapAnalysisModule),
  canActivate: [ProPlanGuard]
}
```

Without lazy loading: all modules bundled in `main.js`, downloaded on initial load.
With lazy loading: `overlap-analysis-overlap-analysis-module.js` downloaded only when user navigates to `/overlap-analysis`.

FOLLOW-UP QUESTIONS:
1. How do you preload lazy modules? (`PreloadAllModules` strategy)
2. What is the difference between `loadChildren` and `loadComponent` (Angular 14+)?
3. How does the Angular CLI create separate chunks for lazy modules?

IMPORTANT FOR INTERVIEW:
The `canActivate: [ProPlanGuard]` on overlap-analysis and ai-insights routes means free users are redirected before the lazy module is even loaded — an additional performance benefit (no download of PRO features).

---

QUESTION:
Explain HTTP Interceptors in your Angular project.

ANSWER:
HTTP Interceptors intercept all `HttpClient` requests/responses globally. This project uses `AuthInterceptor` to automatically attach the JWT to every outbound request and handle 401 unauthorized responses.

PROJECT EXAMPLE:
- File: `frontend/src/app/core/interceptors/auth.interceptor.ts`

```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    
    if (token) {
      req = req.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
    }
    
    return next.handle(req).pipe(
      catchError(error => {
        if (error.status === 401) {
          this.authService.logout();  // clear session, redirect to login
        }
        return throwError(() => error);
      })
    );
  }
}
```

Registered in `AppModule`:
```typescript
providers: [{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }]
```

FOLLOW-UP QUESTIONS:
1. What does `multi: true` mean in the provider registration?
2. How would you add a loading spinner interceptor?
3. How would you implement token refresh in the interceptor?

IMPORTANT FOR INTERVIEW:
`multi: true` allows multiple interceptors to be stacked. The `req.clone()` creates an immutable copy — HttpRequest objects are immutable, you can't mutate them directly. The interceptor re-throws the error after logout so components can still handle error state if needed.

---

QUESTION:
How do route guards work in your Angular project?

ANSWER:
Route guards control navigation. `AuthGuard` blocks unauthenticated users and redirects to login. `ProPlanGuard` blocks free-tier users from PRO routes and redirects to the subscription page.

PROJECT EXAMPLE:
- File: `frontend/src/app/core/guards/auth.guard.ts`
- File: `frontend/src/app/core/guards/pro.guard.ts`

```typescript
// AuthGuard
canActivate(): boolean {
  if (this.authService.isLoggedIn()) return true;
  this.router.navigate(['/auth/login']);
  return false;
}

// ProPlanGuard
canActivate(): boolean {
  if (this.authService.isPro()) return true;
  this.router.navigate(['/subscription']);
  return false;
}
```

`AuthService` helper methods:
```typescript
isLoggedIn(): boolean { return !!this.getToken(); }
isPro(): boolean { return this.currentUser?.subscriptionPlan === 'PRO'; }
```

FOLLOW-UP QUESTIONS:
1. What is the difference between `CanActivate` and `CanDeactivate`?
2. What is `CanLoad` and how does it differ from `CanActivate` for lazy modules?
3. What is the newer `CanActivateFn` functional guard in Angular 15+?

IMPORTANT FOR INTERVIEW:
`CanLoad` (now `canMatch` in Angular 15+) prevents even the lazy module from being downloaded for unauthorized users — stronger than `CanActivate` which just blocks rendering but still allows the bundle download. The project uses `CanActivate` — the PRO module JavaScript would still download even for free users who hit the URL directly.

---

QUESTION:
How does your project use RxJS Observables and services?

ANSWER:
Angular services expose data as Observables (via `HttpClient`). The project uses `BehaviorSubject` for reactive state (current user), and operators like `catchError`, `switchMap`, `debounceTime`, `distinctUntilChanged` for reactive data flows.

PROJECT EXAMPLE:
- File: `frontend/src/app/core/services/auth.service.ts`

```typescript
// BehaviorSubject for current user state
private currentUserSubject = new BehaviorSubject<User | null>(this.loadFromStorage());
currentUser$ = this.currentUserSubject.asObservable();

login(request: LoginRequest): Observable<AuthResponse> {
  return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, request).pipe(
    tap(response => this.saveSession(response))  // side effect: save to localStorage
  );
}
```

Overlap Analysis component (search with debounce):
```typescript
this.searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(query => this.mfSchemeService.search(query).pipe(
    catchError(() => of([]))  // on error, return empty array
  ))
).subscribe(results => this.searchResults = results);
```

FOLLOW-UP QUESTIONS:
1. What is the difference between `BehaviorSubject` and `Subject`?
2. What is `switchMap` and why use it instead of `mergeMap` for search?
3. What is the `async` pipe and when is it preferable to `.subscribe()`?

IMPORTANT FOR INTERVIEW:
`switchMap` is critical for search: when a new search term arrives, it cancels the previous in-flight HTTP request. `mergeMap` would fire all requests and potentially display results out of order. The project correctly uses `switchMap` for the fund search in overlap analysis.

---

QUESTION:
Explain lifecycle hooks in Angular. Which ones are used in your project?

ANSWER:
Lifecycle hooks are called by Angular at specific points during component creation, change detection, and destruction.

PROJECT EXAMPLE:
- File: `frontend/src/app/features/dashboard/dashboard.component.ts`

`ngOnInit` — used in virtually all components to fetch initial data:
```typescript
ngOnInit(): void {
  this.loadDashboardData();  // fetch from API on component creation
}
```

- `ngOnInit`: All feature components (dashboard, portfolio, overlap, AI insights, subscription) use it for initial data loading
- `ngOnDestroy`: Should be used to unsubscribe from observables (prevent memory leaks) — this project does NOT consistently implement it (missing best practice)
- `ngOnChanges`: Used in `StatCardComponent` when `@Input()` values change

FOLLOW-UP QUESTIONS:
1. What is the difference between `ngOnInit` and constructor for initialization?
2. How do you unsubscribe from observables to prevent memory leaks?
3. What is `ChangeDetectorRef.detectChanges()` and when do you need it?

IMPORTANT FOR INTERVIEW:
The project does not consistently implement `ngOnDestroy` with subscription cleanup (using `Subject` + `takeUntil` pattern or the `DestroyRef` inject in Angular 16+). For long-running components or components with multiple subscriptions, this could cause memory leaks if the user navigates back and forth. Mention this as a known improvement: "I'd add `takeUntil(this.destroy$)` pattern to all subscriptions."

---

QUESTION:
How does your project use shared components and the SharedModule?

ANSWER:
The `SharedModule` exports reusable UI components and pipes that are used across multiple feature modules. This prevents duplication and ensures consistency.

PROJECT EXAMPLE:
- File: `frontend/src/app/shared/shared.module.ts`

Exports:
- `StatCardComponent` — displays metric cards (Total Invested, Total Gain, etc.)
- `PageHeaderComponent` — consistent page title + description
- `EmptyStateComponent` — empty portfolio/no-data state
- `IndianCurrencyPipe` — formats numbers in INR with lakhs/crores notation

Usage in DashboardComponent:
```html
<app-stat-card title="Total Invested" [value]="summary.totalInvested | indianCurrency">
</app-stat-card>
```

FOLLOW-UP QUESTIONS:
1. What is the difference between declaring a component in SharedModule vs CoreModule?
2. How do you avoid circular imports between shared and feature modules?
3. What are standalone components and how do they replace SharedModule?

IMPORTANT FOR INTERVIEW:
`SharedModule` should only contain stateless, reusable components. It should NOT contain services (those belong in CoreModule or root providers). The `IndianCurrencyPipe` is a great example — formatting logic isolated in one pipe, reused across dashboard, portfolio, and overlap views.

---

QUESTION:
How does your project implement a custom pipe? Explain IndianCurrencyPipe.

ANSWER:
A custom pipe implements `PipeTransform` with a `transform()` method. The `IndianCurrencyPipe` formats numbers in Indian currency notation (lakhs and crores instead of millions/billions).

PROJECT EXAMPLE:
- File: `frontend/src/app/shared/pipes/indian-currency.pipe.ts`

```typescript
@Pipe({ name: 'indianCurrency' })
export class IndianCurrencyPipe implements PipeTransform {
  transform(value: number | null | undefined): string {
    if (value == null) return '₹0';
    
    // Format with Indian grouping: 1,00,000 instead of 100,000
    if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  }
}
```

Usage: `{{ totalInvested | indianCurrency }}` → displays `₹5.25L` or `₹1.20Cr`

FOLLOW-UP QUESTIONS:
1. What is the difference between pure and impure pipes?
2. When would you use an impure pipe?
3. How do you pass parameters to a custom pipe?

IMPORTANT FOR INTERVIEW:
Pure pipes (default) only re-execute when the input reference changes — efficient for performance. Impure pipes run on every change detection cycle. `IndianCurrencyPipe` is pure — correct behavior since the number value itself changes, not a mutable object.

---

QUESTION:
How does your project handle authentication flow end-to-end in Angular?

ANSWER:
The Angular auth flow combines `AuthService`, `AuthInterceptor`, `AuthGuard`, `ProPlanGuard`, and localStorage for a complete session management system.

PROJECT EXAMPLE:
Files: `auth.service.ts`, `auth.interceptor.ts`, `auth.guard.ts`, `pro.guard.ts`

Complete flow:
1. User submits login form → `LoginComponent` calls `AuthService.login()`
2. HTTP POST returns `{token, userId, email, fullName, subscriptionPlan}`
3. `AuthService.saveSession()` stores in `localStorage` AND updates `BehaviorSubject`
4. Router navigates to `/dashboard`
5. All subsequent HTTP calls: `AuthInterceptor` adds `Authorization: Bearer <token>`
6. Guards check `isLoggedIn()` / `isPro()` on route changes
7. On 401 response: `AuthInterceptor` calls `authService.logout()` → clears storage → redirects to `/auth/login`
8. On successful PRO upgrade: new JWT returned, `AuthService.updateSession()` refreshes the BehaviorSubject

FOLLOW-UP QUESTIONS:
1. How would you implement "remember me" functionality?
2. How do you handle token expiry gracefully (auto-logout vs refresh)?
3. What are the security risks of localStorage for JWT storage?

IMPORTANT FOR INTERVIEW:
The 7-day JWT expiry means if a user's subscription plan changes (upgrade/downgrade), the stale JWT claim persists until expiry — unless the app issues a new JWT. The project handles upgrade correctly (issues new JWT), but downgrade (cancellation) relies on the webhook updating the DB; the old JWT with "PRO" claim would still work for up to 7 days. Mention this as a known limitation.

---

QUESTION:
How does your project use environment configuration in Angular?

ANSWER:
Angular provides `environments/environment.ts` and `environments/environment.prod.ts`. The Angular CLI replaces the file during production builds.

PROJECT EXAMPLE:
- File: `frontend/src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5031/api'
};
```

Production:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.foliotrack.com/api'  // production URL
};
```

Services use it:
```typescript
private apiUrl = environment.apiUrl;
```

FOLLOW-UP QUESTIONS:
1. How does `ng build --configuration=production` handle environment files?
2. How would you add a staging environment?
3. What is the difference between build-time and runtime configuration?

IMPORTANT FOR INTERVIEW:
Environment files are baked in at build time (not runtime). For runtime configuration (e.g., different configs for blue/green deployments), you'd use a config endpoint or inject config via `APP_INITIALIZER`. The project uses build-time config — appropriate for a straightforward deployment model.

---

QUESTION:
How does your project use parent-child component communication?

ANSWER:
Parent passes data down via `@Input()` properties. Children emit events up via `@Output()` and `EventEmitter`. Angular Material dialogs pass data via `MAT_DIALOG_DATA` injection token.

PROJECT EXAMPLE:
- File: `frontend/src/app/shared/components/stat-card/stat-card.component.ts`

```typescript
@Component({ selector: 'app-stat-card' })
export class StatCardComponent {
  @Input() title: string = '';
  @Input() value: string | number = '';
  @Input() subtitle: string = '';
  @Input() icon: string = '';
  @Input() trend: number = 0;
}
```

Parent (`DashboardComponent`):
```html
<app-stat-card
  title="Total Invested"
  [value]="summary.totalInvested | indianCurrency"
  [trend]="summary.totalRoiPct">
</app-stat-card>
```

Dialog communication (`PortfolioComponent`):
```typescript
// Open dialog with data
const dialogRef = this.dialog.open(InvestmentDialogComponent, {
  data: { investment: selectedInvestment }  // pass via MAT_DIALOG_DATA
});

// Listen for result
dialogRef.afterClosed().subscribe(result => {
  if (result) this.loadInvestments();  // refresh list
});
```

FOLLOW-UP QUESTIONS:
1. What is `@ViewChild` and when would you use it for parent-child communication?
2. How do you communicate between sibling components? (Shared service + Subject)
3. What is `ContentProjection` with `ng-content`?

IMPORTANT FOR INTERVIEW:
For sibling communication, this project uses services with `BehaviorSubject` (e.g., `currentUser$` in `AuthService` allows any component to react to auth state changes). This is the standard Angular pattern — no NgRx needed for this scale.

---

QUESTION:
What forms approach does your project use?

ANSWER:
The project uses Reactive Forms for complex forms (login, register, investment dialogs) with programmatic form control and validation. It does NOT use Template-driven forms.

PROJECT EXAMPLE:
- File: `frontend/src/app/features/auth/login/login.component.ts`

```typescript
loginForm = this.fb.group({
  email: ['', [Validators.required, Validators.email]],
  password: ['', [Validators.required, Validators.minLength(6)]]
});

onSubmit(): void {
  if (this.loginForm.invalid) return;
  const { email, password } = this.loginForm.value;
  this.authService.login({ email: email!, password: password! }).subscribe({
    next: () => this.router.navigate(['/dashboard']),
    error: (err) => this.errorMessage = err.error?.message
  });
}
```

Template:
```html
<input [formControl]="loginForm.get('email')" />
<mat-error *ngIf="loginForm.get('email')?.hasError('email')">
  Invalid email address
</mat-error>
```

FOLLOW-UP QUESTIONS:
1. What is the difference between Reactive Forms and Template-driven forms?
2. How do you create custom validators?
3. What is `FormArray` and when is it used?

IMPORTANT FOR INTERVIEW:
Reactive Forms keep form logic in the component class (testable, explicit). Template-driven forms use `ngModel` (simpler but harder to test). This project consistently uses Reactive Forms — the correct choice for complex validation requirements like investment entry with conditional fields.

---

QUESTION:
What is change detection in Angular? What strategy does your project use?

ANSWER:
Change detection is Angular's mechanism to sync the component model with the DOM. The default strategy (`Default`) checks all components on every event. `OnPush` only checks when an `@Input` reference changes or an Observable emits.

PROJECT EXAMPLE:
This project uses the **default** change detection strategy on all components — no `ChangeDetectionStrategy.OnPush` is set. This is simpler but potentially less performant for complex views.

FOLLOW-UP QUESTIONS:
1. What is `ChangeDetectorRef.markForCheck()` and when do you need it with OnPush?
2. What is zone.js and how does it trigger change detection?
3. How would you measure change detection performance issues?

IMPORTANT FOR INTERVIEW:
"This project currently uses the default change detection strategy. For better performance, particularly on the Dashboard with multiple charts and the Portfolio table with many rows, I'd add `ChangeDetectionStrategy.OnPush` to components that receive data via `@Input()` (like `StatCardComponent`). This would reduce unnecessary re-renders."

---

# DATABASE / SQL

---

QUESTION:
What indexes does your project use and why?

ANSWER:
The project defines unique indexes for lookup and uniqueness enforcement, and has implied primary key indexes on all entity IDs.

PROJECT EXAMPLE:
- File: `Data/AppDbContext.cs`

```csharp
// Unique index on User.Email — prevents duplicate registrations
modelBuilder.Entity<User>()
    .HasIndex(u => u.Email).IsUnique();

// Unique index on MutualFundScheme.SchemeCode — cached fund data lookup
modelBuilder.Entity<MutualFundScheme>()
    .HasIndex(s => s.SchemeCode).IsUnique();

// Composite unique index on (UserId, YearMonth) — one row per user per month
modelBuilder.Entity<AiUsageLog>()
    .HasIndex(a => new { a.UserId, a.YearMonth }).IsUnique();
```

Foreign key indexes: EF Core auto-creates indexes on FK columns by convention.

FOLLOW-UP QUESTIONS:
1. What is the difference between clustered and non-clustered indexes?
2. What is index cardinality and why does it matter?
3. How would you add an index to speed up the dashboard query that filters by UserId?

IMPORTANT FOR INTERVIEW:
The `Investments` table is queried heavily by `UserId`. While EF Core creates an index on the FK `UserId` by convention, an explicit covering index on `(UserId, AssetType, Quantity)` would speed up the dashboard allocation query. The current implicit FK index is sufficient for the project's scale but should be explicitly created for production.

---

QUESTION:
What constraints does the database use?

ANSWER:
The project uses several constraint types enforced at the database level via EF Core configuration:

- **Primary Keys**: Auto-increment `Id` on all entities
- **Unique Constraints**: `User.Email`, `MutualFundScheme.SchemeCode`, composite `(AiUsageLog.UserId, YearMonth)`
- **Foreign Keys**: `Investment.UserId → User.Id`, `FundHolding.SchemeCode → MutualFundScheme.SchemeCode`, `Subscription.UserId → User.Id`, `PaymentTransaction.SubscriptionId → Subscription.Id`
- **NOT NULL**: Most required fields
- **Data types**: Decimal precision for financial values (e.g., `decimal(18,4)` for quantities and NAV)

PROJECT EXAMPLE:
- File: `Models/Entities/AiUsageLog.cs`

The composite unique constraint on `(UserId, YearMonth)` implements the monthly rate limiting: you can't `INSERT` a second row for the same user+month, enforcing at DB level that there's always a single counter row that gets `UPDATE`d.

FOLLOW-UP QUESTIONS:
1. What is the difference between UNIQUE constraint and UNIQUE index in MySQL?
2. How do you handle concurrent inserts that would violate a unique constraint?
3. What is `ON DELETE CASCADE` and does your project use it?

IMPORTANT FOR INTERVIEW:
The project handles concurrent AI usage updates with the unique composite index — if two requests simultaneously try to create the first `AiUsageLog` row for a user+month, one will get a unique constraint violation. The service uses `upsert` logic (check-then-insert/update in a single transaction) to handle this, though without explicit transactions it could still have a race condition.

---

QUESTION:
How does your project implement pagination?

ANSWER:
This project currently does NOT implement server-side pagination. All investments are returned in a single query. For the current use case (personal portfolio, typically under 100 holdings), this is acceptable.

PROJECT EXAMPLE:
- File: `Services/InvestmentService.cs`

```csharp
// No pagination — returns all user investments
var investments = await _db.Investments
    .Where(i => i.UserId == userId)
    .ToListAsync();
```

Ideally, it should be implemented using:
```csharp
// Skip/Take pagination
var pagedInvestments = await _db.Investments
    .Where(i => i.UserId == userId)
    .OrderByDescending(i => i.PurchaseDate)
    .Skip((pageNumber - 1) * pageSize)
    .Take(pageSize)
    .ToListAsync();
```

FOLLOW-UP QUESTIONS:
1. What is the difference between offset pagination and cursor-based pagination?
2. How would you return total count alongside paginated results?
3. What is keyset pagination and when is it better?

IMPORTANT FOR INTERVIEW:
"Offset pagination (`SKIP/TAKE`) has performance issues on large tables — the DB must scan and skip N rows. Cursor/keyset pagination (WHERE id > lastSeenId) is more efficient for deep pages. For this project's personal finance use case, offset pagination at 20-50 items per page would work well."

---

QUESTION:
How are joins used in this project's database queries?

ANSWER:
The project uses EF Core LINQ which translates to SQL JOINs implicitly when navigating entity relationships. Explicit joins are written using `.Join()` or navigation properties.

PROJECT EXAMPLE:
- File: `Services/SubscriptionService.cs`

EF Core query that results in a JOIN:
```csharp
var subscription = await _db.Subscriptions
    .Include(s => s.User)  // → LEFT JOIN Users ON Subscriptions.UserId = Users.Id
    .FirstOrDefaultAsync(s => s.UserId == userId);
```

Dashboard aggregation using navigation:
```csharp
// Conceptual — payment transactions loaded with subscription
var transactions = await _db.PaymentTransactions
    .Where(t => t.Subscription.UserId == userId)  // → implicit JOIN
    .ToListAsync();
```

FOLLOW-UP QUESTIONS:
1. What is the difference between INNER JOIN, LEFT JOIN, and CROSS JOIN?
2. How does EF Core's `Include()` translate to SQL?
3. What is the N+1 problem and how do you detect it?

IMPORTANT FOR INTERVIEW:
The project does not extensively use `.Include()` (eager loading). In `InvestmentService.GetAllAsync()`, user investments are loaded first, then NAV data is fetched separately (via `MfApiService`). This is an application-level join rather than a SQL join — intentional because live NAV comes from an external HTTP API, not the database.

---

QUESTION:
Does your project use transactions? How should it?

ANSWER:
The project does NOT use explicit database transactions (`using var transaction = await _db.Database.BeginTransactionAsync()`). EF Core's `SaveChangesAsync()` is atomic per-call but there's no multi-step transaction coordination.

The risk: In `SubscriptionService.VerifyAndUpgradeAsync()`, multiple DB operations run sequentially:
1. Update `User.SubscriptionPlan`
2. Upsert `Subscription` record
3. Insert `PaymentTransaction`

If step 3 fails, steps 1 and 2 are committed — inconsistent state (user has PRO but no payment record).

Ideal implementation:
```csharp
using var transaction = await _db.Database.BeginTransactionAsync();
try {
    // all three operations
    await _db.SaveChangesAsync();
    await transaction.CommitAsync();
} catch {
    await transaction.RollbackAsync();
    throw;
}
```

FOLLOW-UP QUESTIONS:
1. What is ACID in database transactions?
2. What is the difference between `BeginTransaction` and `SaveChanges` atomicity?
3. When would you use distributed transactions?

IMPORTANT FOR INTERVIEW:
"The payment verification flow should use explicit transactions to ensure atomicity. Currently, if a crash occurs mid-operation, the DB could be in an inconsistent state. I'd wrap the upgrade sequence in a transaction. For idempotency, the Razorpay `paymentId` unique constraint on `PaymentTransactions` prevents double-processing the same payment."

---

QUESTION:
How does your project optimize SQL queries?

ANSWER:
Several optimizations are in place:

1. **Filter early**: `.Where(i => i.UserId == userId)` before `.ToListAsync()` — filters in SQL, not C#
2. **Batch NAV fetch**: `GetCurrentNavBatchAsync()` fetches multiple schemes in one call instead of N calls
3. **Caching**: `MutualFundSchemes` table caches NAV — avoids repeated external API calls
4. **Staleness check**: `FundHoldingsService` only re-fetches if 45+ days old
5. **Projection**: Only required fields selected in DTO projections

PROJECT EXAMPLE:
```csharp
// Good: filter in DB
var investments = await _db.Investments
    .Where(i => i.UserId == userId)    // SQL: WHERE UserId = @userId
    .ToListAsync();

// Not optimal: would load all investments then filter in C#
// var all = await _db.Investments.ToListAsync();
// var userInvestments = all.Where(i => i.UserId == userId);
```

FOLLOW-UP QUESTIONS:
1. How do you view the actual SQL generated by EF Core queries?
2. What is `AsNoTracking()` and when does it improve performance?
3. What is the difference between `Find()` and `FirstOrDefault()` in EF Core?

IMPORTANT FOR INTERVIEW:
`AsNoTracking()` should be used for read-only queries (dashboard, portfolio list) — EF Core won't track entity state changes, reducing memory overhead. The project does not use it consistently — a quick performance win by adding `.AsNoTracking()` to all read-only `ToListAsync()` calls.

---

# ADDITIONAL CONCEPTS

---

QUESTION:
Does your project use stored procedures, views, or CTEs?

ANSWER:
No. This project uses EF Core LINQ for all data access — no stored procedures, database views, or CTEs. All business logic runs in C# application code.

FOLLOW-UP QUESTIONS:
1. What are the pros and cons of stored procedures vs ORM?
2. When would you use a database view in this project?
3. How do you call a stored procedure from EF Core if needed?

IMPORTANT FOR INTERVIEW:
"This project keeps all business logic in the application layer, which is the standard approach with EF Core. A database view could be useful for the dashboard aggregation query (grouping investments by ISIN with total values). A stored procedure for the overlap analysis (set intersection calculations) would potentially be faster for large holdings datasets. However, for the current scale, LINQ is clear, maintainable, and sufficient."

---

# PROJECT ARCHITECTURE SUMMARY (DETAILED)

### Top-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Angular 19 SPA                       │
│  Features: Auth | Dashboard | Portfolio              │
│            Overlap | AI Insights | Subscription     │
│                                                      │
│  Core: AuthService, Interceptor, Guards              │
│  Shared: StatCard, IndianCurrencyPipe                │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP + JWT Bearer
                   ▼
┌─────────────────────────────────────────────────────┐
│           ASP.NET Core 10 Web API                    │
│                                                      │
│  Middleware: ExceptionMiddleware → Authentication    │
│             → Authorization → Controllers            │
│                                                      │
│  Controllers: Auth | Investment | Dashboard          │
│               Overlap | AI Insight | Subscription   │
│               MfScheme | Webhook                    │
│                                                      │
│  Services: AuthService | InvestmentService          │
│            DashboardService | OverlapService        │
│            GeminiService (+ Semaphore)              │
│            MfApiService (+ NAV cache)               │
│            FundHoldingsService (Singleton)          │
│            RazorpayService                          │
│                                                      │
│  Data: AppDbContext → EF Core → MySQL               │
└──────┬─────────────────────┬───────────────────────┘
       │                     │
       ▼                     ▼
 FastAPI :8001          External APIs
 CAS PDF Parser         ├── mfapi.in (NAV data)
                        ├── Google Gemini 2.0 Flash
                        ├── Razorpay (payments)
                        └── AMFI (fund holdings)
```

---

# TOP 30 MOST IMPORTANT INTERVIEW QUESTIONS

1. Walk me through the full request lifecycle from Angular to database in FolioTrack.
2. How does JWT authentication work in your project — from token generation to validation?
3. Why is `FundHoldingsService` a Singleton while other services are Scoped? What would break if it were Scoped?
4. Explain the Gemini service's rate limiting approach with `SemaphoreSlim` — why `static readonly`?
5. How does the CAS import flow work end-to-end, including the microservice interaction?
6. Explain the investment data model — why store per-transaction rows instead of aggregated positions?
7. How does `ExceptionMiddleware` work and why register it before `UseAuthentication`?
8. How does the overlap analysis calculate the diversification score?
9. How does the project handle the NAV caching strategy — when does it use cached vs fresh data?
10. What is a `BehaviorSubject` and how is it used for auth state in Angular?
11. Explain lazy loading in Angular — which routes are lazy-loaded and why?
12. How does `AuthInterceptor` work? What happens on a 401 response?
13. How does `ProPlanGuard` work? What would happen without it?
14. How are DTOs used in this project? Give an example of a DTO with computed fields.
15. How does the Razorpay payment flow work from order creation to subscription upgrade?
16. Why use `Task.Run()` for the holdings background fetch? What are the risks?
17. How does the composite unique index on `AiUsageLog(UserId, YearMonth)` enforce rate limiting?
18. What is `switchMap` and why is it used in the fund search?
19. How does `PasswordHelper` hash and verify passwords? Why BCrypt?
20. Explain the subscription tier enforcement — where does it happen (frontend, backend, or both)?
21. How does `DashboardService` compute portfolio ROI and sector allocation?
22. What are the CORS settings and why are they restrictive?
23. How would you add unit tests to this project? What's missing architecturally?
24. How does the `IndianCurrencyPipe` work and why is it a pure pipe?
25. How does the AMFI holdings fetch work — what is the staleness strategy?
26. Explain how `WebhookController` handles Razorpay events securely.
27. How would you add API versioning to this project?
28. What is the difference between `IQueryable` and `IEnumerable` in `DashboardService`?
29. How does EF Core Code First differ from Database First? Which approach and why?
30. What database transactions are missing from this project and where would you add them?

---

# MISSING BEST PRACTICES

### Backend (.NET)

1. **No Service Interfaces** — Services don't implement interfaces (no `IAuthService`, `IInvestmentService`). Required for unit testing with mocks and for Dependency Inversion principle compliance.

2. **No Unit Tests** — No test project exists. Without interfaces, mocking is also harder. Should add `PortfolioApp.Tests` with xUnit and Moq.

3. **No Explicit Transactions** — `SubscriptionService.VerifyAndUpgradeAsync` performs 3 DB operations without wrapping them in a transaction. Risk of partial updates.

4. **No Structured Logging** — Using basic `ILogger`. Production needs Serilog + Seq/Application Insights for searchable structured logs with correlation IDs.

5. **No `AsNoTracking()`** — Read-only dashboard/portfolio queries don't use `.AsNoTracking()`. EF Core tracks entities unnecessarily.

6. **No API Versioning** — No `v1/` or header-based versioning. Breaking API changes would require coordinated frontend updates.

7. **No Health Check Endpoints** — Missing `/health` endpoint (the microservice has one, but the .NET API doesn't). Required for Kubernetes liveness/readiness probes.

8. **No Input Sanitization** — SQL injection is prevented by EF Core parameterization, but no explicit content sanitization on string fields.

9. **No Rate Limiting on API Endpoints** — Only Gemini has rate limiting. The public auth endpoints (`/register`, `/login`) should have IP-based rate limiting to prevent brute force.

10. **JWT Stored in localStorage** — Vulnerable to XSS. Production apps should use httpOnly cookies or a secure cookie-based approach.

### Frontend (Angular)

11. **No `ngOnDestroy` Subscription Cleanup** — Components subscribe to observables without unsubscribing. Memory leaks on component destroy.

12. **No Loading/Error States in All Components** — Some components lack proper loading spinners and error display.

13. **No `ChangeDetectionStrategy.OnPush`** — Default change detection used everywhere. Performance improvement possible for StatCard and read-heavy components.

14. **No E2E Tests** — No Cypress or Playwright test suite.

15. **No Service Worker / PWA** — Could enable offline access to portfolio data.

### Database

16. **No Stored Procedures** — Complex overlap and dashboard queries could be stored procedures for better DB-level optimization.

17. **No Database-Level Soft Delete** — Investments are hard-deleted. A `DeletedAt` soft delete column would preserve audit trails.

18. **No Audit Trail** — No `CreatedAt`/`UpdatedAt` tracking on most entities.

---

# REAL-TIME SCENARIO QUESTIONS

**Scenario 1**: A user imports a CAS PDF with 50 mutual funds. After import, the holdings data for all 50 funds needs to be fetched from AMFI. How does your project handle this without blocking the user?

*Answer*: `InvestmentController.ImportCas()` calls `CasParserClient` synchronously (needed for the import result), then fires `Task.Run(() => _fundHoldingsService.EnsureHoldingsInBackground(schemeCodes))` — a fire-and-forget Task. The HTTP response returns immediately to the user. The background task fetches AMFI data asynchronously, possibly taking 30-60 seconds. The user sees portfolio data on next page load.

---

**Scenario 2**: The Gemini API returns a 429 rate-limit error during peak hours when 5 users simultaneously request AI insights. How does your project handle this?

*Answer*: `GeminiService` uses `SemaphoreSlim(1,1)` — a static semaphore that allows only one call at a time. All 5 user requests queue up at `_semaphore.WaitAsync()`. The first request executes; if it gets 429, it retries with backoff (3s, 8s). The other 4 requests wait. This serializes calls but increases latency under load. Better at scale: distributed queue with per-user rate buckets.

---

**Scenario 3**: A user's payment goes through on Razorpay but the webhook fails to reach your server. The user paid but their subscription isn't upgraded. How would you debug and fix this?

*Answer*: Check Razorpay dashboard for webhook delivery failure. The project also has a `/subscription/verify` endpoint that the frontend calls immediately after payment — this is the primary upgrade path. The webhook is a backup. If both fail, manual recovery: query `PaymentTransactions` by RazorpayOrderId, verify the payment, manually update `Subscription` and `User.SubscriptionPlan`.

---

**Scenario 4**: The live NAV API (mfapi.in) is down for 2 hours. What happens to your dashboard?

*Answer*: `MfApiService.GetCurrentNavBatchAsync()` catches the HTTP exception, logs a warning, and falls back to the cached NAV in `MutualFundSchemes.Nav`. Users see dashboard data with stale NAV (from yesterday or whenever last successful fetch). A warning is not shown to users — this could be improved by adding a "NAV as of [date]" indicator.

---

**Scenario 5**: The portfolio table has 200 rows after years of SIP transactions. The dashboard is slow. How would you optimize it?

*Answer*: 
1. Add `AsNoTracking()` to all read queries
2. Add a database index on `(UserId, AssetType, Quantity)` for the main filter
3. Add `.Select()` projection to fetch only needed columns (not full entity)
4. Consider aggregating investments at import time (current NAV × quantity), not on every dashboard load
5. Cache dashboard results for 5 minutes per user (add Redis or in-memory cache)
6. Add server-side pagination to the portfolio table

---

**Scenario 6**: You need to add a new "Stocks" feature that requires PRO subscription. What changes are needed end-to-end?

*Answer*:
- Backend: Add `[Authorize]` + check `subscriptionPlan == "PRO"` in the new service
- Database: New entity + EF Core migration + `dotnet ef database update`
- Frontend: New feature module → `app-routing.module.ts` add lazy route with `canActivate: [ProPlanGuard]`
- Angular: Add sidebar link with PRO badge indicator
- No Razorpay changes — PRO plan tier already exists

---

# HR + MANAGER ROUND QUESTIONS

**Q: Tell me about FolioTrack. What does it do and what problem does it solve?**

*Answer*: FolioTrack is a personal investment portfolio management SaaS for Indian retail investors. The core problem it solves is fragmentation — investors hold mutual funds across multiple folios, stocks, and ETFs, with no single view of their overall portfolio. FolioTrack imports Consolidated Account Statement (CAS) PDFs from CAMS/KARVY to automatically import all mutual fund holdings. The dashboard shows real-time NAV-based returns, and the overlap analysis feature helps users understand if their multiple mutual funds are actually holding the same underlying stocks — a common issue in India where large-cap funds often have 80%+ overlap.

---

**Q: What was the most technically challenging feature you built?**

*Answer*: The fund overlap analysis was the most interesting. The challenge was: AMFI publishes fund portfolios as text files with inconsistent formatting. I built a scraper in `FundHoldingsService.FetchFromAmfiAsync()` that handles multi-month lookups (current month, then tries previous 2 months if not published yet). The actual overlap calculation uses set-intersection math: for each pair of funds, the overlap percentage is the sum of `min(stock% in fund1, stock% in fund2)` across common holdings — this gives the weighted overlap, not just a count of common stocks.

---

**Q: How did you handle the payment integration?**

*Answer*: I integrated Razorpay for one-time subscription purchases (₹199/month for PRO plan). The backend creates an order via Razorpay's API, the Angular frontend opens the Razorpay checkout modal, and after payment the client receives a paymentId + signature. The frontend sends this to our `/subscription/verify` endpoint, which verifies the HMAC-SHA256 signature using our Razorpay secret, upgrades the user's plan, and returns a fresh JWT with the "PRO" subscription claim. The webhook endpoint handles asynchronous payment events as a backup.

---

**Q: If you had 3 more months on this project, what would you add?**

*Answer*: 
1. **Unit & integration tests** — No test coverage currently. I'd add xUnit tests with a real test DB (not mocks).
2. **Portfolio analytics** — Annualized returns (XIRR calculation), benchmark comparison against Nifty 50, and SIP goal tracking.
3. **Production hardening** — HTTPS, structured logging (Serilog + Seq), health checks, CORS for real domain, Kubernetes deployment manifests.
4. **Mobile support** — Progressive Web App (PWA) with service worker for offline portfolio viewing.

---

**Q: How would you scale this if it had 10,000 users?**

*Answer*:
- Database: Add read replicas, connection pooling (PgBouncer), proper indexes
- Caching: Redis for NAV data and dashboard results (per-user 5-min cache)
- Background jobs: Move CAS processing and AMFI scraping to Hangfire/background queue
- Gemini: Distributed rate limiter with Redis instead of in-process semaphore
- CDN: Static Angular assets via CDN, not served by the API
- Horizontal scaling: Multiple API instances behind a load balancer (JWT is stateless — no session affinity needed)

---

# QUICK REVISION NOTES

## .NET Core Key Points
- **JWT**: HS256, 7-day expiry, claims: `NameIdentifier` (userId), `Email`, `subscriptionPlan`
- **Middleware order**: ExceptionMiddleware → CORS → Authentication → Authorization → Controllers
- **Service lifetimes**: All Scoped EXCEPT `FundHoldingsService` (Singleton, cached + background)
- **HTTP clients**: `AddHttpClient<T>()` pattern (IHttpClientFactory) for `MfApiService` and `CasParserClient`
- **Exception mapping**: `UnauthorizedAccessException`→401, `KeyNotFoundException`→404, `ArgumentException`→400, `InvalidOperationException`→409
- **No AutoMapper** — manual DTO mapping with computed fields (ROI, currentValue)
- **No Repository pattern** — direct `AppDbContext` injection in services
- **No explicit transactions** — risk in SubscriptionService upgrade flow
- **Gemini rate limiting**: `SemaphoreSlim(1,1)` + 3 retries with backoff (3s, 8s)

## Angular Key Points
- **Modules**: NgModule-based (not standalone), all feature modules lazy-loaded
- **Guards**: `AuthGuard` (isLoggedIn), `ProPlanGuard` (isPro)
- **Interceptor**: `AuthInterceptor` — adds JWT, handles 401 logout
- **State**: `BehaviorSubject` in `AuthService` — no NgRx
- **Forms**: Reactive Forms (FormBuilder, FormGroup, Validators)
- **Charts**: ng-apexcharts (donut charts for allocation and sectors)
- **Currency**: `IndianCurrencyPipe` — custom pure pipe, Indian number format
- **Missing**: `ngOnDestroy` unsubscribe, `OnPush` change detection

## Database Key Points
- **MySQL 8**, database: `portfolio_db`
- **Unique indexes**: `User.Email`, `MutualFundScheme.SchemeCode`, `(AiUsageLog.UserId, YearMonth)`
- **Per-transaction investment rows** — not aggregated positions
- **NAV caching**: `MutualFundSchemes.Nav` + `NavDate`, re-fetched if date mismatch
- **Holdings staleness**: 45-day threshold, AMFI monthly data, tries 3 months back
- **No stored procedures, views, CTEs, or explicit transactions**

## Key Business Logic
- **CAS import**: Delete old ISINs → insert per-transaction rows → background holdings fetch
- **Dashboard**: Group by ISIN → live NAV → calculate ROI, allocation, sector data
- **Overlap**: `sum(min(fund1%, fund2%))` per common stock → diversification = `100 - avgOverlap`
- **AI insights**: Check PRO + monthly limit (50) → build prompt → Gemini → increment counter
- **Subscription**: Razorpay order → checkout → verify HMAC → upgrade plan → new JWT

---

# TOP 10 STRONGEST CONCEPTS DEMONSTRATED

1. **JWT Authentication End-to-End** — Complete flow: BCrypt password hashing, HS256 token generation with custom claims, Angular interceptor injection, 401 auto-logout
2. **Layered Architecture** — Clean separation: Controllers → Services → DbContext; no business logic in controllers
3. **Async/Await Throughout** — All I/O is async; fire-and-forget background tasks for non-critical operations
4. **HttpClient Factory Pattern** — Correct `AddHttpClient<T>()` usage preventing socket exhaustion
5. **Reactive Angular with RxJS** — BehaviorSubject for state, switchMap for search, catchError for resilience
6. **External API Integration** — Multiple third-party integrations (Razorpay, Gemini, AMFI, mfapi.in) with resilient fallback strategies
7. **Payment Integration with Webhook Security** — HMAC-SHA256 constant-time signature verification for Razorpay
8. **Rate Limiting Strategy** — In-process semaphore for Gemini, monthly usage table for per-user limits
9. **Lazy Loading + Route Guards** — Feature modules lazy-loaded, subscription tier enforced at routing level
10. **NAV Caching Strategy** — DB-level caching with date-based staleness, fallback to stale on API failure

---

# TOP 10 CONCEPTS MISSING OR WEAK

1. **No Unit Tests** — Zero test coverage; no service interfaces for mocking; highest risk area for production
2. **No Service Interfaces** — Direct concrete class injection; violates Interface Segregation and Dependency Inversion principles
3. **No Database Transactions** — Multi-step operations (subscription upgrade) lack ACID guarantees; risk of inconsistent state
4. **No Subscription Cleanup (ngOnDestroy)** — Angular components don't unsubscribe from observables; memory leak risk on SPA navigation
5. **No Structured Logging** — Basic ILogger only; no Serilog/Seq; no correlation IDs; insufficient for production debugging
6. **No API Versioning** — No `/api/v1/` prefix; breaking changes require coordinated full-stack deploys
7. **No Rate Limiting on Auth Endpoints** — `/auth/login` and `/auth/register` vulnerable to brute force; need IP-based throttling
8. **No Pagination** — All investments returned in a single query; will degrade at scale
9. **CORS Hardcoded to localhost** — Production deployment requires config change; should be environment-driven
10. **JWT in localStorage** — XSS vulnerability; production should use httpOnly cookies or a secure token storage strategy

---

*Generated by Claude Code based on full codebase analysis of FolioTrack — D:\Project\Portfolio Management system*
*Date: 2026-05-19 | Model: claude-sonnet-4-6*
