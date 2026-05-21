# CS PM Service APIs — Interview Preparation Guide
> Based on: `D:\Projects\CS_PM_Service_APIs` | .NET 6.0 Microservices | Generated: 2026-05-18

> **Note:** This project is a **pure .NET 6.0 backend** — no Angular frontend exists in this repo.
> All SQL and .NET Core sections are fully covered based on actual code.

---

# PROJECT ARCHITECTURE SUMMARY

## Complete Architecture Flow

This is a **.NET 6.0 microservices monorepo** — an integration layer between two systems:
- **CS** (Content/Customer Service platform — source of truth, SQL Server)
- **PM** (Project Management platform — Odoo-based, receives pushed data)

```
CS SQL Server DB
      │
      ├── Worker Services (push data OUT to PM)
      │     ├── cs-pm-asn-push-srv       → Pushes assignments + QB assignments
      │     ├── cs-pm-asn-revi-push-srv  → Pushes assignment revisions
      │     ├── cs-pm-config-srv         → Pushes service/subject area/website config
      │     ├── cs-pm-lookup-srv         → Pushes lookup data
      │     ├── cs-pm-del-srv            → Pushes delivery data
      │     ├── cs-pm-fldetails-fetch-srv→ Fetches flight details
      │     ├── cs-pm-ulatus-config-srv  → Pushes Ulatus brand config
      │     └── cs-pm-ulatus-lookup-srv  → Pushes Ulatus lookup data
      │
      └── Web APIs (receive data IN from PM / other systems)
            ├── cs-pm-subject-area-api   → Receives subject area update requests (port 4041)
            └── cs-pm-del-api            → Receives delivery file data (port 4025)
```

## Request Lifecycle (Web API)

```
External caller (PM system)
    → HTTP POST with JWT Bearer token
    → Kestrel (port from appsettings.json HostPort key)
    → JWT Middleware validates token (SymmetricSecurityKey, ASCII-encoded key)
    → [Authorize] attribute on controller
    → Controller (SubjectAreaController / CSDeliveryController)
    → Business logic + validation
    → Repository / Direct SqlCommand
    → SQL Server (Stored Procedure via Dapper or SqlCommand)
    → Returns StatusCode(200/400)
```

## Worker Service Lifecycle

```
Program.cs → CreateHostBuilder()
    → Coravel scheduler (cron) OR BackgroundService (Task.Delay interval loop)
    → Worker.Invoke() / ExecuteAsync()
    → Check session token from Environment variables
    → If expired: call PM Auth endpoint → read Set-Cookie → store in env var
    → Call SQL Server (Dapper QueryMultiple) → fetch pending records
    → Build JSON-RPC 2.0 payload
    → POST to PM REST API (RestSharp / WebClient / HttpClient)
    → If response.error.code == 100: re-authenticate and retry
    → On success: UPDATE SQL Server to mark records as pushed
```

## Authentication Flow

**APIs (JWT):**
- Key: `appsettings.json` → `JWT:JWTAuthenticationKey`
- Algorithm: HS256 symmetric — `SymmetricSecurityKey(Encoding.ASCII.GetBytes(key))`
- `ValidateIssuer = false`, `ValidateAudience = false` — only signing key is validated
- `[Authorize]` attribute enforces auth on all controllers

**Workers (Cookie/Session with PM/Odoo):**
- Calls PM auth endpoint (GET) with credentials in request body
- Reads `Set-Cookie` header, extracts `session_id` value and expiry
- Stores in `Environment.SetEnvironmentVariable("sessiontoken", ...)`
- Sends `X-openerp-session-id` and `Cookie: session_id=...` headers on every API call
- If PM returns `error.code == 100` (session expired): re-authenticates and retries

## Database Interaction Flow

- **Dapper** (micro-ORM): `QueryMultiple`, `QuerySingle`, `ExecuteAsync` with `DynamicParameters`
- **Stored Procedures**: All DB calls use `CommandType.StoredProcedure`
- **Table-Valued Parameters**: `DataTable.AsTableValuedParameter()` for bulk inserts/updates
- **Direct SqlCommand**: `CSDeliveryController.ExecuteProc()` uses raw ADO.NET for structured type
- **Dual DB support**: `MoveToLive` config flag switches between UAT and Live connection strings at runtime

---

# .NET / .NET CORE — INTERVIEW Q&A

---

QUESTION:
What is the middleware pipeline in your project and how is it configured?

ANSWER:
The middleware pipeline in ASP.NET Core is a chain of components that process HTTP requests and
responses in order. Each middleware can short-circuit the pipeline or pass control to the next.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Program.cs and cs-pm-del-api/Startup.cs
* Order in Subject Area API: UseCors → UseAuthentication → UseAuthorization → MapControllers
* Order in Delivery API: UseRouting → UseAuthentication → UseAuthorization → UseEndpoints
* Explanation:
  - CORS is configured first with `options.WithOrigins("*").AllowAnyMethod().AllowAnyHeader()`
  - `UseAuthentication()` validates the JWT token
  - `UseAuthorization()` enforces the `[Authorize]` attribute on controllers
  - `UseDeveloperExceptionPage()` is added in DeliveryAPI for dev environment
  - `UseHttpsRedirection()` is in DeliveryAPI but missing in Subject Area API (security gap)

FOLLOW-UP QUESTIONS:
1. What happens if you call `UseAuthorization()` before `UseAuthentication()`?
2. Why is `UseCors()` placed before authentication?
3. What is the difference between terminal and non-terminal middleware?

IMPORTANT FOR INTERVIEW:
Order matters critically. `UseAuthentication` MUST come before `UseAuthorization`. Missing
`UseHttpsRedirection` in Subject Area API is a notable gap. The wildcard CORS (`*`) is acceptable
for internal microservices but a security weakness for public APIs.

---

QUESTION:
How is Dependency Injection implemented and what service lifetimes are used?

ANSWER:
DI is the built-in IoC container in .NET Core. Dependencies are registered in Program.cs/Startup.cs
and injected via constructors.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Program.cs:16
  `builder.Services.AddScoped<IRepository, Repository>()`
* File: cs-pm-asn-push-srv/Program.cs:118-119
  `services.AddTransient<PMASNWorker>()`
  `services.AddScoped<IAPIOperation, ApiOperation>()`
* Class: SubjectAreaController receives `ILogger<SubjectAreaController>` and `IRepository`
  via constructor injection
* Lifetimes used:
  - Scoped   → IRepository (one instance per HTTP request)
  - Transient → PMASNWorker (new instance per Coravel scheduler invocation)
  - Singleton → Config static class (manual singleton, outside DI)

FOLLOW-UP QUESTIONS:
1. What is the difference between Scoped, Singleton, and Transient?
2. What is "captive dependency" — injecting Scoped into Singleton?
3. Why is PMASNWorker Transient instead of Singleton?

IMPORTANT FOR INTERVIEW:
Transient for the worker is correct — Coravel instantiates it per scheduled run and the worker
holds per-run state. The static `Config` class is effectively a manual Singleton outside DI,
which means it cannot be mocked in unit tests — a testability weakness.

---

QUESTION:
How is JWT authentication implemented in your project?

ANSWER:
JWT authentication validates a signed Bearer token in the Authorization header.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Program.cs:30-45
* File: cs-pm-del-api/Startup.cs:72-87
* Code:
  ```csharp
  builder.Services.AddAuthentication(x => {
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
* `[Authorize]` on SubjectAreaController and CSDeliveryController enforces token validation
* DeliveryAPI Swagger has `AddSecurityDefinition("Bearer")` for JWT testing in Swagger UI

FOLLOW-UP QUESTIONS:
1. What are ValidateIssuer and ValidateAudience, and why are they false here?
2. What is the risk of RequireHttpsMetadata = false?
3. Difference between Authentication and Authorization in .NET Core?

IMPORTANT FOR INTERVIEW:
`ValidateIssuer = false` and `ValidateAudience = false` means any token signed with the same key
from any issuer/audience is accepted — acceptable for internal microservices but a security
weakness. The JWT key is in appsettings.json — ideally it should be in Azure Key Vault or
environment variables.

---

QUESTION:
How is the Repository pattern implemented in your project?

ANSWER:
The Repository pattern abstracts data access behind an interface, decoupling the controller from
HOW data is fetched or stored.

PROJECT EXAMPLE:

* Interface: cs-pm-subject-area-api/Contracts/IRepository.cs
  `int UpdateOtherSubjectAreaDetails(RequestDetails requestDetails);`
* Implementation: cs-pm-subject-area-api/Repository/Repository.cs
  Uses Dapper + SQL Server stored procedure
* Controller: SubjectAreaController.cs:35
  `int result = _IRepository.UpdateOtherSubjectAreaDetails(requestDetails);`
* DI: Program.cs:16 — `AddScoped<IRepository, Repository>()`

FOLLOW-UP QUESTIONS:
1. What is the difference between Repository pattern and Unit of Work pattern?
2. How would you unit test SubjectAreaController using this pattern?
3. Why interface in a Contracts folder?

IMPORTANT FOR INTERVIEW:
CSDeliveryController does NOT use the repository pattern — it has direct Dapper/SqlCommand
calls inside the controller (SaveDeliveryDetails, ExecuteProc, ExceptionLog). This violates
SRP. Mention this as a technical debt point and explain what the fix would look like.

---

QUESTION:
How do you use Dapper in this project?

ANSWER:
Dapper is a lightweight micro-ORM extending IDbConnection to map SQL results directly to C#
objects — faster and more explicit than Entity Framework.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Repository/Repository.cs:42
  ```csharp
  result = con.QuerySingle<int>(SqlConstants.CS_UpdateOtherSubject_PMReplatform,
      param, commandType: CommandType.StoredProcedure);
  ```
* File: cs-pm-asn-push-srv/PMASNWorker.cs:101
  ```csharp
  var result = await con.QueryMultipleAsync(
      SqlConstants.CS_GetAssignmentDetails_PMReplatform, parameter,
      commandType: CommandType.StoredProcedure, commandTimeout: 180);
  var AssignmentDetailResponse = result.Read<PMAssignmentDetailDTO>().ToList();
  var AddonDetailsResponse = result.Read<AddOnDetailsDTO>().ToList();
  // ... 3 more result sets
  ```
* DynamicParameters used for all stored procedure parameters
* TVP: `AssignmentList.AsTableValuedParameter(SqlConstants.AssignmentListTableType)` for bulk update

FOLLOW-UP QUESTIONS:
1. What is QueryMultiple in Dapper and when is it useful?
2. How does Dapper differ from EF Core in performance?
3. What is DynamicParameters and why use it over anonymous types?

IMPORTANT FOR INTERVIEW:
QueryMultiple is a key design decision here — 1 DB call fetches 5 result sets (assignments,
addons, original files, reference files, CS instructions), then LINQ FindAll joins them in-memory.
This eliminates the N+1 query problem. commandTimeout: 180 (3 minutes) handles heavy batch queries.

---

QUESTION:
How is async/await used in your project?

ANSWER:
async/await allows non-blocking I/O, freeing threads while waiting for DB or HTTP responses.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/PMASNWorker.cs:64-70
  ```csharp
  public async Task ProcessASN() {
      var task1 = ProcessAssignments();
      var task2 = ProcessQBAssignments();
      await Task.WhenAll(task1, task2);  // parallel execution
  }
  ```
* ProcessAssignments() uses `await con.QueryMultipleAsync(...)` and `await con.ExecuteAsync(...)`
* File: cs-pm-config-srv/Worker.cs:85
  `await Task.Delay(TimeSpan.FromMinutes(Config.IntervalMinutes), stoppingToken)`
* Anti-pattern: PMASNWorker.Invoke() calls `ProcessASN().Wait()` — sync-over-async

FOLLOW-UP QUESTIONS:
1. What is Task.WhenAll vs Task.WhenAny?
2. What is the deadlock risk of calling .Wait() or .Result on a Task?
3. What is the difference between Task and ValueTask?

IMPORTANT FOR INTERVIEW:
Task.WhenAll is a real performance win — both assignment types process in parallel.
However, Invoke() calls .Wait() (blocking) because Coravel's IInvocable.Invoke() is a
sync interface — this is a known Coravel limitation workaround. Mention you're aware of
the sync-over-async risk.

---

QUESTION:
How is configuration management handled?

ANSWER:
Configuration is loaded from appsettings.json and accessed via a static Config class or
IConfiguration injection.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Config.cs — static class, initialized once at startup:
  ```csharp
  public static class Config {
      public static void Initialize(IConfiguration configuration) {
          JWTAuthenticationKey = Configuration["JWT:JWTAuthenticationKey"];
          MoveToLive = Configuration["MoveToLive"];
          ConnectionStringUAT = Configuration["CsDatabase:ConnectionStringUAT"];
          ConnectionStringLive = Configuration["CsDatabase:ConnectionStringLive"];
      }
  }
  ```
* File: cs-pm-del-api/CSDeliveryController.cs:31
  IConfiguration injected: `_configuration.GetConnectionString("DefaultConnection")`
* MoveToLive flag switches between UAT and Live DB/API URLs without redeployment

FOLLOW-UP QUESTIONS:
1. What is the difference between IConfiguration, IOptions<T>, and a static Config class?
2. How would you reload config changes at runtime?
3. What are the risks of storing secrets in appsettings.json?

IMPORTANT FOR INTERVIEW:
Two patterns coexist — static Config (workers, subject-area API) and IConfiguration injection
(delivery API). Static Config is simpler but not testable/mockable. IOptions<T> is the modern
recommended approach. The MoveToLive feature flag for environment switching without redeployment
is a practical real-world pattern worth explaining.

---

QUESTION:
How is exception handling implemented?

ANSWER:
try/catch blocks with differentiated SqlException vs Exception catching, plus structured logging.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Repository/Repository.cs:46-54
  ```csharp
  catch(SqlException ex) {
      _logger.LogError($"SQL Error in SaveSubjectAreaDetails: {ex}");
  }
  catch(Exception ex) {
      _logger.LogError($"Error in SaveSubjectAreaDetails: {ex}");
  }
  ```
* File: cs-pm-del-api/CSDeliveryController.cs:185-203
  ExceptionLog() inserts errors to tbl_GeneralError_Log table via raw SQL
* File: cs-pm-asn-push-srv/PMASNWorker.cs:184-207
  Uses StackTrace to extract file and line number from exception
* Controllers return StatusCode(400, message) on all failures

FOLLOW-UP QUESTIONS:
1. Why catch SqlException before Exception?
2. What is global exception handling middleware?
3. What is the problem with empty catch blocks?

IMPORTANT FOR INTERVIEW:
No global exception middleware exists — every method catches locally, which leads to
repetitive code. A better pattern: custom exception middleware or Problem Details RFC 7807.
The ExceptionLog() writing to tbl_GeneralError_Log is a DB-level audit log — pragmatic
but duplicates what NLog/Serilog already does. One empty catch block exists in
PMASNWorker constructor — a code smell worth flagging.

---

QUESTION:
How is logging implemented?

ANSWER:
Two logging frameworks: NLog (workers + subject-area API) and Serilog (delivery API),
both sending to Elasticsearch for centralized log management.

PROJECT EXAMPLE:

* NLog: `builder.Services.AddLogging(x => x.AddNLog("NLog.config"))` — file + console sinks
* Serilog → Elasticsearch (cs-pm-del-api/Program.cs:89-98):
  ```csharp
  Log.Logger = new LoggerConfiguration()
      .Enrich.FromLogContext()
      .Enrich.WithMachineName()
      .WriteTo.Console()
      .WriteTo.Elasticsearch(ConfigureElasticSink(configuration, environment))
      .Enrich.WithProperty("Environment", environment)
      .CreateLogger();
  ```
* Elasticsearch index format: `{logName}-{yyyy.MM.dd}` (daily rolling index)
* Basic auth configured: `.BasicAuthentication(username, password)`

FOLLOW-UP QUESTIONS:
1. What is structured logging vs string interpolation logging?
2. What is the Elasticsearch sink's advantage for centralized logging?
3. Why is using both NLog static logger and ILogger<T> in the same class a problem?

IMPORTANT FOR INTERVIEW:
Some services use both `NLog.LogManager.GetCurrentClassLogger()` (static) AND `ILogger<T>`
(DI-injected) — inconsistent and harder to configure centrally. Serilog with Elasticsearch
in DeliveryAPI is production-grade: machine name enrichment, environment tagging, daily indices.

---

QUESTION:
What is the .NET Generic Host and BackgroundService? How are they used?

ANSWER:
The Generic Host is the foundation for long-running .NET services. BackgroundService is an
abstract class implementing IHostedService for background loops.

PROJECT EXAMPLE:

* File: cs-pm-config-srv/Worker.cs — Worker : BackgroundService
  ```csharp
  protected override async Task ExecuteAsync(CancellationToken stoppingToken) {
      while (!stoppingToken.IsCancellationRequested) {
          ScheduleService();
          await Task.Delay(
              TimeSpan.FromMinutes(Config.IntervalMinutes), stoppingToken);
      }
  }
  ```
* File: cs-pm-asn-push-srv/Program.cs — uses Coravel cron scheduler:
  ```csharp
  host.Services.UseScheduler(scheduler => {
      scheduler.Schedule<PMASNWorker>().Cron(Config.SchedulerCron);
  });
  ```
* UseWindowsService() enables deployment as a Windows Service

FOLLOW-UP QUESTIONS:
1. What is the difference between IHostedService and BackgroundService?
2. How does Coravel cron differ from BackgroundService Task.Delay?
3. What happens when CancellationToken is requested (service stop)?

IMPORTANT FOR INTERVIEW:
Two scheduling approaches in this monorepo: BackgroundService (config-srv) and Coravel (asn-push-srv).
Coravel's cron expression is more precise for exact-time scheduling (e.g., "run at 2AM").
BackgroundService Task.Delay is simpler but drifts over time. UseWindowsService() means
deployment is via `sc create` or NSSM as a Windows Service.

---

QUESTION:
What SOLID principles are demonstrated (and which are missing)?

ANSWER:

PRESENT:
- SRP: Config.cs only manages config. Repository.cs only handles DB access. ApiOperation.cs
  only handles HTTP calls to PM.
- OCP: IRepository and IAPIOperation interfaces allow swapping implementations without
  changing controllers or workers.
- DIP: SubjectAreaController depends on IRepository (abstraction), not Repository (concrete).
  PMASNWorker depends on IAPIOperation, not ApiOperation.
- LSP: ApiOperation : IAPIOperation and Repository : IRepository fully implement their contracts.

MISSING / WEAK:
- ISP: IAPIOperation bundles PostASNRequest, PostQBRequest, and GetCookiesForAuthorization —
  could be split into IAssignmentPusher and IAuthProvider.
- SRP VIOLATION: CSDeliveryController does HTTP handling + file validation (IsValidFile) +
  DB operations (ExecuteProc) + error logging (ExceptionLog) — should be split into service classes.

FOLLOW-UP QUESTIONS:
1. How would you refactor CSDeliveryController to follow SRP?
2. What is the Open/Closed Principle and how does IRepository implement it?
3. Give an example of DIP violation in this project.

---

QUESTION:
How is CORS configured?

ANSWER:
CORS controls which origins can make cross-origin requests to the API.

PROJECT EXAMPLE:

* File: cs-pm-subject-area-api/Program.cs:58-60
  ```csharp
  app.UseCors(options => options
      .WithOrigins("*")
      .AllowAnyMethod()
      .AllowAnyHeader());
  ```
* DeliveryAPI: CORS middleware is commented out — no CORS configured (network-level access only)

IMPORTANT FOR INTERVIEW:
WithOrigins("*") (wildcard) is acceptable for internal microservices but insecure for
public APIs. Note that `AllowCredentials()` cannot be used with wildcard origins in .NET —
they are mutually exclusive. DeliveryAPI likely doesn't need CORS since it's called
from server-to-server, not from a browser.

---

QUESTION:
How is LINQ used in this project?

ANSWER:
LINQ is used for in-memory filtering and projection of Dapper-fetched collections.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/PMASNWorker.cs:125-128
  ```csharp
  asn.AddOnDetails = asnDetails.AddonDetails
      .FindAll(x => x.AssignmentID == asn.AssignmentID).ToList();
  asn.OriginalFiles = asnDetails.OriginalFiles
      .FindAll(x => x.AssignmentID == asn.AssignmentID).ToList();
  ```
* File: cs-pm-config-srv/ConfigDataPushService.cs:43
  `lst.Select(x => x.ServiceMasterId).ToArray()`
* File: cs-pm-config-srv/ConfigDataPushService.cs:49-57
  LINQ query syntax for filtering and projection of service details

FOLLOW-UP QUESTIONS:
1. What is the difference between IQueryable and IEnumerable?
2. What is deferred execution in LINQ?
3. What is the performance difference between FindAll and Where?

IMPORTANT FOR INTERVIEW:
IQueryable is NOT used because Dapper doesn't support it — Dapper returns fully materialized
IEnumerable<T>. All LINQ here is in-memory. The QueryMultiple + FindAll pattern is deliberate:
1 DB call fetches all data, in-memory LINQ does the "join" — avoids N+1.

---

QUESTION:
How are DTOs used in this project?

ANSWER:
DTOs (Data Transfer Objects) are plain classes used to carry data between layers, decoupling
DB schema from API contracts.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/Models/PMAssignmentDetails.cs
  PMAssignmentDetailDTO with nested: AddOnDetailsDTO, OriginalFilesDTO, ReferenceFilesDTO,
  CSInstructionDTO — a hierarchical DTO built in-memory from flat DB result sets
* File: cs-pm-subject-area-api/Models/RequestDetails.cs
  RequestDetails — inbound DTO for the subject area update API
* File: cs-pm-del-api/Model/DeliveryFileDetails.cs
  DeliveryFileDetails (line item) + DeliveryDetails (header) + CombinedDeliveryDetails
  (flattened, created by merging header + each file for bulk DB insert)

IMPORTANT FOR INTERVIEW:
AutoMapper is NOT used — all DTO mapping is manual. The CombinedDeliveryDetails creation
in CSDeliveryController (foreach loop copying fields) is verbose boilerplate that AutoMapper
would eliminate. The hierarchical DTO building in PMASNWorker (5 flat lists → nested objects)
is a clean data assembly pattern worth explaining.

---

QUESTION:
How does the session/cookie authentication work in worker services?

ANSWER:
Workers authenticate with PM (Odoo) via cookie-based sessions. The token is stored in
process environment variables and refreshed when expired.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/APIOperation/APIOperation.cs:189-227
  GetCookiesForAuthorization(): calls PM auth endpoint, reads Set-Cookie header,
  parses session_id and expiry

* Flow:
  1. GET to PM auth URL with credentials in request body
  2. Read Set-Cookie response header, extract session_id value
  3. Environment.SetEnvironmentVariable("sessiontoken", authdata.SessionId)
  4. On each PM API call: AddHeader("X-openerp-session-id", sessionid)
                          AddHeader("Cookie", "session_id=" + sessionid)
  5. If PM returns error.code == 100: re-authenticate, store new token, retry

* File: cs-pm-asn-push-srv/PMASNWorker.cs:29-53 — checks expiry on constructor:
  ```csharp
  if (string.IsNullOrEmpty(sessionid) || Convert.ToDateTime(sessionExpire) < DateTime.Now)
      AuthorizationData();
  ```

FOLLOW-UP QUESTIONS:
1. Why use Environment variables for token storage rather than a singleton service?
2. What is the risk of infinite recursive retry on re-authentication?
3. How would you improve this with Polly?

IMPORTANT FOR INTERVIEW:
Environment variables as token storage is process-global and not thread-safe for concurrent
access. The recursive retry (PostASNRequest calls itself) has no depth limit — if auth keeps
failing, it loops forever. Improvement: Polly RetryPolicy with max 3 retries + exponential
backoff. Config-srv manages TWO sessions (Enago + Ulatus brands) using separate env vars.

---

QUESTION:
How is the Table-Valued Parameter (TVP) pattern used?

ANSWER:
TVPs pass a DataTable as a structured SQL parameter — enables bulk insert/update in one call.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/PMASNWorker.cs:166-170 (Dapper approach):
  ```csharp
  AssignmentList = pushedAssignmentList.ToDataTable();
  DynamicParameters param = new DynamicParameters();
  param.Add("@PushedAssignments",
      AssignmentList.AsTableValuedParameter(SqlConstants.AssignmentListTableType));
  isSuccess = await con.ExecuteAsync(
      SqlConstants.CS_UpdatePushedAssignmentStatus_PMReplatform,
      param, commandType: CommandType.StoredProcedure);
  ```
* File: cs-pm-del-api/CSDeliveryController.cs:161-182 (raw ADO.NET approach):
  ```csharp
  SqlParameter parameters = new SqlParameter("@Assignment", SqlDbType.Structured);
  parameters.Value = dataTable;
  parameters.TypeName = "dbo.ASNDeliveryFiles_IntermediateTableType";
  ```
* DataTableHelper uses reflection to convert List<T> to DataTable generically

FOLLOW-UP QUESTIONS:
1. What SQL object must exist for a TVP to work (user-defined table type)?
2. What is the benefit of TVP over multiple individual INSERT calls?
3. How does the DataTableHelper use reflection?

IMPORTANT FOR INTERVIEW:
TVPs require a matching `CREATE TYPE ... AS TABLE` in SQL Server. Two TVP approaches coexist:
Dapper's AsTableValuedParameter() (clean, recommended) and raw ADO.NET SqlParameter
(older style). Both work. Bulk status update via TVP (one call for N records) vs N individual
UPDATEs is a significant performance win.

---

QUESTION:
How is Base64 encoding/decoding used?

ANSWER:
Base64 converts binary or Unicode data to safe ASCII — used here for file name encoding
and full JSON payload encoding.

PROJECT EXAMPLE:

* Encoding file names (sender):
  File: cs-pm-asn-push-srv/PMASNWorker.cs:330-338
  ```csharp
  static string StringToBase64(string input) {
      byte[] utf8Bytes = Encoding.UTF8.GetBytes(input);
      return Convert.ToBase64String(utf8Bytes);
  }
  ```
  Applied to OriginalFiles[i].FileName and ReferenceFiles[i].RefFileName before pushing to PM.
  Reason: file names may contain Unicode/special characters unsafe in JSON.

* Decoding full payload (receiver):
  File: cs-pm-del-api/CSDeliveryController.cs:41-43
  ```csharp
  var base64 = Delivery.DeliveryDet;
  var blob = Convert.FromBase64String(base64);
  var json = Encoding.UTF8.GetString(blob);
  var Det = JsonConvert.DeserializeObject<DeliveryDetails>(json);
  ```
  The PM system wraps the entire JSON delivery payload in Base64 before sending.

FOLLOW-UP QUESTIONS:
1. Why Base64 encode file names instead of URL-encoding?
2. What is the overhead of Base64 encoding (size increase)?
3. How would you handle Base64 decode failure gracefully?

---

# SQL DATABASE PATTERNS

---

QUESTION:
What stored procedures are used and what is their purpose?

ANSWER:
All DB operations use stored procedures — no inline SQL except the error log INSERT.

PROJECT EXAMPLE:

* CS_UpdateOtherSubject_PMReplatform
  Updates subject area for an assignment.
  Returns int: 1=success, 2=assignment not found, 3=not in CS master, 4=not "Others" type.

* CS_GetAssignmentDetails_PMReplatform
  Returns 5 result sets in one call: assignments, addons, original files, reference files,
  CS instructions. Called with 180s timeout.

* CS_UpdatePushedAssignmentStatus_PMReplatform
  Bulk-updates push status via TVP for successfully pushed assignments.

* CS_GetQBAssignmentDetails_PMReplatform
  Returns 3 result sets: QB assignments, question details, question document details.

* CS_UpdatePushedQBAssignmentStatus_PMReplatform
  Bulk-updates QB push status via TVP.

* CS_ASNDeliveryFiles_IntermediateInsert
  Inserts delivery file records via structured TVP (dbo.ASNDeliveryFiles_IntermediateTableType).

IMPORTANT FOR INTERVIEW:
Using only stored procedures provides: SQL injection prevention, cached execution plans,
centralized DB logic, and easier DBA review. The return code pattern (1/2/3/4) from
CS_UpdateOtherSubject_PMReplatform encodes business rules at the DB level — better than
raising exceptions for expected business cases.

---

QUESTION:
What is QueryMultiple and when do you use it?

ANSWER:
QueryMultiple in Dapper executes a stored procedure returning multiple result sets,
reading them sequentially from a single SqlDataReader.

PROJECT EXAMPLE:

* File: cs-pm-asn-push-srv/PMASNWorker.cs:101-119
  ```csharp
  var result = await con.QueryMultipleAsync(
      SqlConstants.CS_GetAssignmentDetails_PMReplatform,
      parameter, commandType: CommandType.StoredProcedure, commandTimeout: 180);

  var assignments  = result.Read<PMAssignmentDetailDTO>().ToList();
  var addons       = result.Read<AddOnDetailsDTO>().ToList();
  var origFiles    = result.Read<OriginalFilesDTO>().ToList();
  var refFiles     = result.Read<ReferenceFilesDTO>().ToList();
  var instructions = result.Read<CSInstructionDTO>().ToList();
  ```
  Then in-memory LINQ joins them per assignment.

IMPORTANT FOR INTERVIEW:
Without QueryMultiple, the alternative would be 5 separate DB calls or 5 separate stored
procedures — 5x the round trips. QueryMultiple is ideal when related entities need to
be fetched together and the SP already produces multiple SELECT results.

---

QUESTION:
What is the pagination / batch strategy?

ANSWER:
The project relies on the stored procedures to control batch size — the SP decides which
records are "pending push" and returns only those. The application processes all returned
records in a single run.

PROJECT EXAMPLE:

* CS_GetAssignmentDetails_PMReplatform filters by IsDataSent = 0 (not yet pushed)
* After pushing, CS_UpdatePushedAssignmentStatus_PMReplatform marks them IsDataSent = 1
* This ensures records are not double-pushed across scheduler runs

IMPORTANT FOR INTERVIEW:
The DB-side filtering (IsDataSent flag) is the batching mechanism — the SP is the
"pagination" here. If a batch is too large and times out, the transaction rolls back
and records remain IsDataSent = 0, so they retry on the next scheduler run.
This provides at-least-once delivery semantics.

---

QUESTION:
What is the inline SQL usage in the project?

ANSWER:
The project uses stored procedures exclusively, with one exception: ExceptionLog() uses
inline SQL for the error log table.

PROJECT EXAMPLE:

* File: cs-pm-del-api/CSDeliveryController.cs:188-201
  ```csharp
  using (SqlCommand cmd = new SqlCommand(
      "INSERT INTO tbl_GeneralError_Log (ErrorMessage, ErrorProcedure, DateOfOperation) " +
      "VALUES (@Error, @EntrySource, @ErrorDateTime);", con))
  {
      cmd.Parameters.AddWithValue("@Error", Convert.ToString(error));
      cmd.Parameters.AddWithValue("@EntrySource", "CS PM Delivery Code");
      cmd.Parameters.AddWithValue("@ErrorDateTime", DateTime.Now);
  }
  ```
  Note: Uses parameterized queries, NOT string concatenation — SQL injection safe.

IMPORTANT FOR INTERVIEW:
Even though this is inline SQL, it correctly uses parameterized queries (AddWithValue)
rather than string concatenation, so it is NOT vulnerable to SQL injection.
This is the only inline SQL in the entire project — a good pattern.

---

# MISSING BEST PRACTICES (Enterprise Improvements)

1. **Global exception middleware** — No IMiddleware or ProblemDetails; every method catches locally.
   Fix: Add `app.UseExceptionHandler()` or a custom `ExceptionHandlingMiddleware`.

2. **No unit/integration tests** — Zero test projects in the monorepo.
   Fix: xUnit + Moq for unit tests; TestContainers for integration tests.

3. **Polly retry/circuit breaker** — Recursive re-authentication with no depth limit.
   Fix: `Policy.Handle<HttpRequestException>().WaitAndRetryAsync(3, ...)`

4. **IHttpClientFactory** — `new HttpClient()` and `new WebClient()` inside loops risk socket exhaustion.
   Fix: Register typed/named HttpClient via `services.AddHttpClient<IAPIOperation, ApiOperation>()`.

5. **Secrets in appsettings.json** — JWT key, connection strings, credentials in config files.
   Fix: Azure Key Vault + `builder.Configuration.AddAzureKeyVault(...)`.

6. **AutoMapper** — Manual DTO mapping is verbose and fragile.
   Fix: `services.AddAutoMapper(typeof(Program))` + profile classes.

7. **IOptions<T> pattern** — Static Config class is not DI-injectable or mockable.
   Fix: `services.Configure<DatabaseConfig>(configuration.GetSection("CsDatabase"))` 
   + inject `IOptions<DatabaseConfig>`.

8. **API versioning** — Routes like `/OtherSubjectArea/Update` have no version prefix.
   Fix: `services.AddApiVersioning()` + route prefix `/api/v1/...`.

9. **[FromBody] attribute missing** — SubjectAreaController reads Request.Body manually
   instead of using model binding.
   Fix: `public ActionResult Post([FromBody] RequestDetails requestDetails)`.

10. **Health check probes** — `AddHealthChecks()` is registered but only the default
    endpoint is mapped with no custom checks.
    Fix: Add `.AddSqlServer(connectionString)` health check probe.

11. **Mixed logging frameworks** — NLog static + ILogger<T> DI in same services.
    Fix: Standardize on one framework (Serilog recommended for modern .NET).

12. **No structured logging** — String interpolation like `$"Result: {result}"` loses
    structure in Elasticsearch.
    Fix: `_logger.LogInformation("Result: {Result}", result)` (named properties).

---

# MOST IMPORTANT INTERVIEW QUESTIONS (Top 30 — specific to this project)

1.  Walk me through the overall architecture — what does each service type do?
2.  Why are there two types of services — Web APIs and Worker Services?
3.  How does session authentication work for PM API calls? Why environment variables?
4.  Explain the QueryMultiple pattern and why you used it instead of separate queries.
5.  What is the MoveToLive config flag and how is it used at runtime?
6.  How does Coravel cron scheduling differ from BackgroundService.ExecuteAsync?
7.  Why does PMASNWorker.Invoke() call .Wait() on an async method? What is the risk?
8.  How does Task.WhenAll(task1, task2) benefit the assignment push worker?
9.  Why is PMASNWorker registered as Transient rather than Singleton?
10. Walk through the Delivery API request lifecycle from HTTP to database.
11. What is Base64 decoding used for in CSDeliveryController?
12. Why is IRepository in a Contracts folder? What is the benefit of this abstraction?
13. How does JWT middleware validate a token — step by step?
14. Why are ValidateIssuer and ValidateAudience set to false?
15. How does the ExceptionLog method work and what table does it write to?
16. What is a Table-Valued Parameter? Show me where it is used here.
17. How does DataTableHelper convert a List<T> to a DataTable?
18. What does StackTrace in the catch blocks of PMASNWorker give you?
19. What happens when PM returns error.code == 100?
20. What is the risk of the recursive re-authentication retry pattern?
21. What is UseWindowsService() and how are these services deployed?
22. Why does SubjectAreaController.Post() read Request.Body manually instead of [FromBody]?
23. How is CORS configured differently in the two APIs?
24. What is Kestrel and why is the port configured in appsettings.json?
25. How would you refactor CSDeliveryController to follow SOLID principles?
26. What is IDbConnection and why use it instead of SqlConnection directly?
27. What is commandTimeout: 180 and when is it needed?
28. Why are there two logging frameworks (NLog and Serilog) in the same monorepo?
29. How would you add a Polly retry policy to the PM API calls?
30. If you had to push a new data type to PM, which files would you touch?

---

# REAL-TIME SCENARIO QUESTIONS

Scenario 1: The PM system is down for 30 minutes. What happens to your workers?
> Current: REST calls fail, exceptions are logged, the scheduler skips that run,
> next cron run retries. Records stay IsDataSent=0 in DB — no data loss.
> Improvement: Polly circuit breaker to stop retrying during outage, exponential backoff.

Scenario 2: A file name contains Chinese/Japanese Unicode characters. How does your system handle it?
> PMASNWorker calls StringToBase64() on FileName and RefFileName before serializing to JSON.
> This converts UTF-8 bytes to Base64 ASCII — safe for JSON transmission to PM.
> On receive side, CSDeliveryController uses Path.GetInvalidFileNameChars() for validation.

Scenario 3: Session token expired between two scheduler runs. What happens?
> Worker constructor checks: if sessionExpire < DateTime.Now → calls GetCookiesForAuthorization()
> to refresh. Also: if PM returns error.code == 100 mid-run, PostASNRequest recursively
> re-authenticates and retries. Token is refreshed in environment variable.

Scenario 4: 500 assignments need to be pushed in one run. How does the current code handle it?
> All fetched in one QueryMultiple call (5 result sets). Pushed one-by-one in a foreach loop
> via RestSharp. Successful IDs collected in a list, then bulk-updated via TVP in one
> ExecuteAsync call. Risk: if the loop exceeds 120s timeout for any single RestSharp call,
> that assignment is skipped (exception caught, loop continues).

Scenario 5: You need to add support for a third brand (e.g., Crimson). What would you add?
> Follow cs-pm-ulatus-config-srv pattern: add new env vars (sessiontokenCrimson, sessionExpireCrimson),
> new Config keys for Crimson auth URL + API URLs, add GetCookiesForAuthorization("Crimson")
> branch, add AuthorizationDataCrimson() in Worker, add CallFor*DataForCrimson() methods.

Scenario 6: A SQL stored procedure times out at peak load. What do you do?
> Increase commandTimeout in Dapper call (currently 180s). Add SQL indexes on filtering
> columns (IsDataSent, AssignmentID). Review SP execution plan for missing indexes or
> parameter sniffing issues. Consider batching — SP returns top N records, process N,
> loop until empty.

---

# HR + MANAGER ROUND QUESTIONS

Q: Describe your project in 2 minutes.
> This is a microservices integration layer built in .NET 6.0. It's a monorepo with 11
> services — 2 REST APIs and 9 background workers. The APIs receive incoming data from
> the PM (Project Management / Odoo) system, while the workers push data to PM on scheduled
> intervals. Tech stack: Dapper for data access, SQL Server as the database, NLog/Serilog
> for structured logging to Elasticsearch, RestSharp for HTTP, JWT for API security,
> and Coravel for cron scheduling. Key contributions include: Base64 file name encoding
> for Unicode safety (CW-13176, CW-14073), parallel task execution using Task.WhenAll,
> and session token management with auto-refresh for PM API authentication.

Q: What was the most challenging part?
> Managing session tokens across scheduled worker runs. The PM system uses cookie-based
> Odoo sessions with expiry. I had to implement startup checks, expiry detection in the
> constructor, and mid-run refresh when PM returns error code 100. Storing tokens in
> environment variables and handling recursive re-authentication carefully (avoiding
> infinite loops) required thinking through edge cases.

Q: What would you improve if given more time?
> 1. Replace static Config class with IOptions<T> for testability.
> 2. Add Polly retry/circuit breaker for HTTP resilience.
> 3. Move secrets (JWT key, connection strings) to Azure Key Vault.
> 4. Refactor CSDeliveryController — extract IDeliveryService, IFileValidator, IErrorLogger.
> 5. Add unit tests with xUnit + Moq.
> 6. Standardize on one logging framework (Serilog).
> 7. Use IHttpClientFactory instead of new HttpClient() in loops.

Q: How did you ensure no data was lost if the PM system was temporarily down?
> The IsDataSent flag pattern in SQL Server. Records are only marked as pushed AFTER
> the PM API confirms success. If a push fails, records remain IsDataSent=0 and are
> retried on the next scheduler run. The bulk status update uses TVP so all successful
> records in a batch are marked atomically.

---

# QUICK REVISION NOTES (Read before the interview)

SERVICES:
- 2 Web APIs (JWT-protected, Kestrel): Subject Area (port 4041) + Delivery (port 4025)
- 9 Workers: Coravel (cron expression) or BackgroundService (interval), deployed as Windows Services

DATABASE:
- SQL Server + Dapper only — no Entity Framework
- All DB calls via Stored Procedures
- DynamicParameters for SP params
- TVP (AsTableValuedParameter) for bulk operations
- QueryMultiple: 5 result sets in 1 DB call, joined in-memory with LINQ FindAll

AUTHENTICATION:
- APIs: JWT Bearer, SymmetricSecurityKey, ValidateIssuer/Audience = false
- Workers: Cookie session from PM Odoo, stored in env vars, refreshed on error.code==100

HTTP CLIENTS:
- RestSharp → asn-push-srv (with Timeout=120000)
- HttpClient → config-srv (newer services)
- WebClient → config-srv (legacy parts)

LOGGING:
- NLog (most workers + subject-area API)
- Serilog → Elasticsearch (delivery API) with daily index rotation

KEY PATTERNS:
- Parallel push: Task.WhenAll(ProcessAssignments(), ProcessQBAssignments())
- Batch fetch: QueryMultiple (5 result sets) → in-memory LINQ join → TVP bulk update
- Config switch: MoveToLive flag selects UAT vs Live DB/API at runtime
- Environment switching: MoveUAT / MoveLIVE booleans for multi-brand Enago/Ulatus

DATA FLOW:
  Fetch pending from CS DB (IsDataSent=0)
    → Build JSON-RPC 2.0 payload
      → POST to PM API (RestSharp/WebClient)
        → Parse response (result.IsSuccess or error.code)
          → Mark as pushed in CS DB (IsDataSent=1) via TVP

---

# TOP 10 STRONGEST CONCEPTS DEMONSTRATED

1. Microservices design — 11 independent services with clear bounded responsibilities
2. JWT authentication — properly configured in 2 APIs with SymmetricSecurityKey validation
3. Dapper + QueryMultiple — 5 result sets in 1 DB round trip, N+1 avoided
4. Parallel async execution — Task.WhenAll for simultaneous assignment type processing
5. Table-Valued Parameters — bulk status update via custom SQL structured types
6. Repository + Interface pattern — DI-backed abstraction enabling testability
7. Coravel cron scheduling — cron expression-based task scheduling in worker services
8. Session token management — cookie auth with expiry check and auto-refresh
9. Structured centralized logging — Serilog + Elasticsearch with environment enrichment
10. Environment switching — MoveToLive / MoveUAT / MoveLIVE flags for zero-redeployment env selection

---

# TOP 10 MISSING OR WEAK CONCEPTS

1. Global exception handling middleware — no IMiddleware or ProblemDetails RFC 7807
2. Unit / integration tests — zero test projects exist in the repo
3. Polly retry / circuit breaker — no resilience policy; recursive retry has no depth limit
4. IHttpClientFactory — new HttpClient() in loops risks socket exhaustion (well-known .NET anti-pattern)
5. Secrets management — JWT key and DB credentials stored in appsettings.json
6. AutoMapper — all DTO mapping is manual and verbose
7. IOptions<T> pattern — static Config class cannot be injected or mocked in tests
8. API versioning — no versioned routes; breaking changes would affect all callers
9. [FromBody] model binding — SubjectAreaController reads Request.Body stream manually
10. Detailed health check probes — AddHealthChecks() registered but no SQL/external checks configured
