# Questions Index — Quick Reference

> Auto-maintained index for scanning what's already in the JSON files before adding new questions.
> Format: `ID | Question text`
> Update this file whenever you add new questions to any JSON.

---

## Azure & Cloud (`questions-azure.json`) — 6 questions

| ID | Question |
|----|----------|
| azure-001 | What is Azure? What are the key Azure services relevant to .NET developers? |
| azure-002 | What is Azure Key Vault and how do you integrate it with an ASP.NET Core API? |
| azure-003 | What is Azure Blob Storage and how do you use it in a .NET application? |
| azure-004 | What are Azure Functions and how do you use them in .NET? |
| azure-005 | How do you troubleshoot an API issue when it's deployed to Azure? |
| azure-006 | What is CI/CD and how do you set it up for a .NET application using Azure DevOps? |

---

## Dependency Injection (`questions-di.json`) — 13 questions

| ID | Question |
|----|----------|
| di-001 | What is Dependency Injection (DI) and why do we need it? |
| di-002 | Explain the three service lifetimes in .NET Core: Transient, Scoped, Singleton. |
| di-003 | What is captive dependency? How do you safely inject a Scoped service into a Singleton? |
| di-004 | What is the difference between IServiceCollection.Add() vs TryAdd()? What about AddScoped vs AddScopedKeyed? |
| di-005 | How does property injection work in .NET Core? Why is constructor injection preferred? |
| di-006 | What is IOptions<T>, IOptionsSnapshot<T>, and IOptionsMonitor<T>? When do you use each? |
| di-007 | How do you register open generic types in .NET DI? Give a real example. |
| di-008 | What is IHttpClientFactory and why should you always use it instead of new HttpClient()? |
| di-009 | What is the service locator pattern? Why is it considered an anti-pattern? |
| di-010 | How do you configure DI in a Worker Service (.NET BackgroundService)? How does it differ from Web API? |
| di-011 | What are extension methods for IServiceCollection and why do you create them? |
| di-012 | What is Scrutor? How does assembly scanning work for automatic DI registration? |
| di-013 | Where does an injected dependency reside in memory? How does the DI container manage its lifetime? |

---

## Database & SQL (`questions-database.json`) — 68 questions

| ID | Question |
|----|----------|
| db-001 | What is the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN? |
| db-002 | What is the difference between WHERE and HAVING? |
| db-003 | What is an index and how does it improve query performance? |
| db-004 | What is a stored procedure and what are its advantages over inline SQL? |
| db-005 | What are SQL transactions and what are ACID properties? |
| db-006 | What are SQL isolation levels and what concurrency problems do they solve? |
| db-007 | What is normalisation and what are the normal forms (1NF, 2NF, 3NF)? |
| db-008 | What is a deadlock in SQL and how do you prevent it? |
| db-009 | What is the difference between DELETE, TRUNCATE, and DROP? |
| db-010 | What are window functions in SQL? Give an example. |
| db-011 | What is a CTE (Common Table Expression) and when would you use it? |
| db-012 | What is query plan and how do you use EXPLAIN/execution plan to optimise a query? |
| db-013 | What is the N+1 problem in database queries? |
| db-014 | What is the difference between clustered and non-clustered indexes? |
| db-015 | What is a view in SQL and when would you use it? |
| db-016 | How does SQL Server handle concurrency? Explain optimistic vs pessimistic concurrency. |
| db-017 | What is a foreign key and how does it enforce referential integrity? |
| db-018 | What is database sharding and when would you use it? |
| db-019 | Write a SQL query to find the second highest salary from an Employee table. |
| db-020 | What are SQL triggers and when should you use them? |
| db-021 | What is the difference between UNION and UNION ALL? |
| db-022 | How do you handle pagination in SQL? |
| db-023 | What is the difference between a temp table and a table variable? |
| db-024 | What is SQL injection and how do you prevent it? |
| db-025 | What is the difference between primary key and unique key? |
| db-026 | What is database partitioning in SQL Server? |
| db-027 | What is a composite index and when should you use it? |
| db-028 | What are aggregate functions in SQL? Give examples. |
| db-029 | Explain the SQL Server query execution pipeline. |
| db-030 | What is the difference between CHAR, VARCHAR, and NVARCHAR? |
| db-031 | What is a CROSS JOIN and how does it differ from FULL OUTER JOIN? |
| db-032 | How does NULL behave in SQL JOINs, comparisons, and aggregate functions? |
| db-033 | Can DML statements (INSERT, UPDATE, DELETE) be used inside a SQL function? Why or why not? |
| db-034 | What is a Recursive CTE and how do you write one? |
| db-035 | What is the difference between a Materialized View and a regular View in SQL? |
| db-036 | What are Magic Tables (INSERTED and DELETED) in SQL Server triggers? |
| db-037 | How do you handle errors in SQL Server using TRY/CATCH? |
| db-038 | How do you retrieve the identity value after an INSERT? Explain SCOPE_IDENTITY(), @@IDENTITY, and IDENT_CURRENT(). |
| db-039 | What is the difference between OLTP and OLAP? How do they affect database design? |
| db-040 | What is index fragmentation in SQL Server and how do you fix it? |
| db-041 | How do you delete duplicate rows in SQL Server while keeping one copy? |
| db-042 | How do you optimise a slow SQL query or stored procedure? |
| db-043 | What is the difference between a stored procedure and a function in SQL Server? |
| db-044 | Write a SQL query to count the number of employees in each department. |
| db-045 | What is denormalization? When do you intentionally break normal form? |
| db-046 | What is SQL Server Connection Pooling? How does it work and what are the pitfalls? |
| db-047 | What are subqueries in SQL? What is the difference between a correlated and non-correlated subquery? |
| db-048 | What are constraints in SQL? Explain all types with examples. |
| db-049 | What are the types of database relationships? Explain one-to-one, one-to-many, and many-to-many. |
| db-050 | What is SET NOCOUNT ON/OFF in SQL Server? When should you use it? |
| db-051 | What is RAISERROR in SQL Server? How does it differ from THROW? |
| db-052 | What is the difference between a Table Scan, Index Scan, and Index Seek in SQL Server? |
| db-053 | How do you reseed an identity column in SQL Server? What is DBCC CHECKIDENT? |
| db-054 | What are the types of SQL Server backups? Explain Full, Differential, and Transaction Log backups. |
| db-055 | What are the High Availability solutions in SQL Server? Explain Mirroring, Log Shipping, Replication, and Always On. |
| db-056 | What are DCL commands in SQL? Explain GRANT, DENY, and REVOKE. |
| db-057 | What is Fill Factor in SQL Server? What is the default value and when do you change it? |
| db-058 | What are the Recovery Models in SQL Server? Explain Simple, Full, and Bulk-Logged. |
| db-059 | What are the types of SQL commands? Explain DDL, DML, DQL, DCL, and TCL. |
| db-060 | What is a CASE statement in SQL? Explain SIMPLE vs SEARCHED CASE with examples. |
| db-061 | What is a Self Join in SQL? When and why would you use one? |
| db-062 | What is a Cursor in SQL Server? When should you use one and when should you avoid it? |
| db-063 | What is the COALESCE() function in SQL Server? How is it different from ISNULL()? |
| db-064 | What is the difference between DBMS and RDBMS? |
| db-065 | How do you find the Nth highest salary from an Employee table? |
| db-066 | Write a SQL query to find departments that have zero employees. |
| db-067 | How do you identify missing indexes in SQL Server? |
| db-068 | Can a SQL function return multiple result types? What are the types of SQL Server functions? |

---

## Web API (`questions-webapi.json`) — 46 questions

| ID | Question |
|----|----------|
| webapi-001 | What is REST and what are its core principles? |
| webapi-002 | What is the difference between GET, POST, PUT, PATCH, and DELETE HTTP verbs? |
| webapi-003 | What are common HTTP status codes and what do they mean? |
| webapi-004 | How does routing work in ASP.NET Core Web API? |
| webapi-005 | What is model binding in ASP.NET Core and how does it work? |
| webapi-006 | What is model validation in ASP.NET Core and how do you use it? |
| webapi-007 | What is CORS and how do you configure it in ASP.NET Core? |
| webapi-008 | What are action filters in ASP.NET Core Web API and how do you create a custom one? |
| webapi-009 | How do you implement API versioning in ASP.NET Core? |
| webapi-010 | How do you implement global exception handling in ASP.NET Core Web API? |
| webapi-011 | What is Swagger/OpenAPI and how do you set it up in ASP.NET Core? |
| webapi-012 | What is content negotiation in Web API? |
| webapi-013 | How do you implement rate limiting in ASP.NET Core? |
| webapi-014 | What is the IActionResult return type vs specific types like Ok(), NotFound()? |
| webapi-015 | What is minimal API in ASP.NET Core and when would you use it over controllers? |
| webapi-016 | What is the difference between RESTful and SOAP web services? |
| webapi-017 | What is Kestrel and what role does it play in ASP.NET Core? |
| webapi-018 | What is ADO.NET? How does it compare to EF Core? |
| webapi-019 | What is MediaTypeFormatter (Web API) / IOutputFormatter (ASP.NET Core)? How does content negotiation work? |
| webapi-020 | How do you consume an ASP.NET Core Web API from a console application? |
| webapi-021 | Can you perform INSERT or UPDATE operations using an HTTP GET request? What are the consequences? |
| webapi-022 | How do you secure an ASP.NET Core Web API? What are the key practices? |
| webapi-023 | How do you implement caching in ASP.NET Core? What are IMemoryCache and IDistributedCache? |
| webapi-024 | How do you implement structured logging in ASP.NET Core? Tell me about Serilog. |
| webapi-025 | What are Health Checks in ASP.NET Core and how do you set them up? |
| webapi-026 | How does JSON serialization work in ASP.NET Core? System.Text.Json vs Newtonsoft.Json? |
| webapi-027 | How do you improve ASP.NET Core Web API performance? What's your checklist? |
| webapi-028 | How do you store and read configuration in ASP.NET Core? Where should DB connection strings live? |
| webapi-029 | Why do we use Kestrel if IIS already exists? What is a reverse proxy? |
| webapi-030 | What is the difference between Web API and WCF? When would you still use WCF? |
| webapi-031 | What is HTTP stateless protocol? Why does that mean we need session management? |
| webapi-032 | What is the difference between .NET SDK and .NET Runtime? |
| webapi-033 | What is the difference between a DLL and an EXE in .NET? What are the types of assemblies? |
| webapi-034 | What is DelegatingHandler in ASP.NET Web API? How does it differ from ASP.NET Core Middleware? |
| webapi-035 | What is HATEOAS and how does it relate to REST API design? |
| webapi-036 | What is idempotency in REST? Which HTTP methods are idempotent and why does it matter? |
| webapi-037 | What is the difference between REST and GraphQL? When would you choose one over the other? |
| webapi-038 | What is the difference between query parameters and path parameters in REST API? When do you use each? |
| webapi-039 | What are REST API best practices? What are the key design principles you follow? |
| webapi-040 | What is Swagger/OpenAPI? How do you implement it in ASP.NET Core? |
| webapi-041 | What is IHostedService in ASP.NET Core? How do you use BackgroundService? |
| webapi-042 | What are HTTP status codes? Explain the main categories and common codes. |
| webapi-043 | Can you use the [HttpPost] attribute on a GET action method? What happens? |
| webapi-044 | What is the DRY principle and how does it apply to ASP.NET Core development? |
| webapi-045 | How do you return meaningful error messages to the client in ASP.NET Core Web API? |
| webapi-046 | How do you handle performance issues with dropdown/select list population in ASP.NET Core MVC or API? |

---

## MVC (`questions-mvc.json`) — 24 questions

| ID | Question |
|----|----------|
| mvc-001 | What is the MVC pattern and how does ASP.NET Core implement it? |
| mvc-002 | What is a ViewModel and why should you use it instead of domain models in views? |
| mvc-003 | What is TempData and when do you use it? |
| mvc-004 | What are Tag Helpers in ASP.NET Core Razor views? |
| mvc-005 | What are partial views and view components? When do you use each? |
| mvc-006 | What is the difference between MVC and MVVM? |
| mvc-007 | What is the difference between .NET Framework and .NET Core / .NET 5+? |
| mvc-008 | What is the difference between Session and Cookie in ASP.NET Core? |
| mvc-009 | What is the ASP.NET Core MVC request lifecycle / pipeline? |
| mvc-010 | What is the difference between ViewBag, ViewData, and TempData in ASP.NET Core MVC? |
| mvc-011 | What is the Razor view engine in ASP.NET Core MVC? |
| mvc-012 | What is the entry point of an ASP.NET Core MVC application? What happens at startup? |
| mvc-013 | What is Bundling and Minification in ASP.NET Core? |
| mvc-014 | What are the types of routing in ASP.NET Core MVC? |
| mvc-015 | What is RenderBody() and RenderSection() in ASP.NET Core Razor layouts? |
| mvc-016 | What is the default session timeout in ASP.NET Core and how do you configure it? |
| mvc-017 | What are Data Annotations in ASP.NET Core? How do you use them for validation? |
| mvc-018 | What is the difference between TempData.Keep() and TempData.Peek() in ASP.NET Core MVC? |
| mvc-019 | What is a strongly typed view in ASP.NET Core MVC? Why is it better than ViewBag? |
| mvc-020 | What are Razor Pages in ASP.NET Core? How are they different from MVC? |
| mvc-021 | What is the folder structure of an ASP.NET Core MVC project? |
| mvc-022 | What are filters in ASP.NET Core MVC? Explain the different types. |
| mvc-023 | How do you handle exceptions globally in ASP.NET Core? |
| mvc-024 | Can multiple controllers share the same view? Can one controller use multiple views? |

---

## OOPS (`questions-oops.json`) — 54 questions

| ID | Question |
|----|----------|
| oops-001 | What are the four pillars of OOP? |
| oops-002 | What is the difference between an interface and an abstract class? |
| oops-003 | What is polymorphism and what are its types in C#? |
| oops-004 | What is encapsulation and how do you implement it in C#? |
| oops-005 | What is inheritance in C# and what are its limitations? |
| oops-006 | What are generics in C# and why are they useful? |
| oops-007 | What are delegates and events in C#? |
| oops-008 | What is the difference between value types and reference types in C#? |
| oops-009 | What is CLR and how does .NET code execute? |
| oops-010 | How does Garbage Collection work in .NET? What are generations? |
| oops-011 | What is the difference between var and dynamic in C#? |
| oops-012 | What is the difference between const, readonly, and static readonly? |
| oops-013 | What is the IDisposable pattern and when do you implement it? |
| oops-014 | What is the difference between string and StringBuilder in C#? |
| oops-015 | What is a sealed class and when would you use it? |
| oops-016 | What is exception handling in C#? What is the difference between throw and throw ex? |
| oops-017 | What are lambda expressions and how are they used in C#? |
| oops-018 | What are access modifiers in C#? Explain public, private, protected, internal, and protected internal. |
| oops-019 | What is the difference between float, double, and decimal in C#? When do you use each? |
| oops-020 | What is JIT (Just-In-Time) compilation and how does .NET code execute? |
| oops-021 | What is a static class in C# and when would you use one? |
| oops-022 | What is a nested class in C# and when would you use one? |
| oops-023 | What is the difference between List<T>.Add() and List<T>.Insert()? What are their time complexities? |
| oops-024 | What is the difference between managed code and unmanaged code in .NET? |
| oops-025 | What is boxing and unboxing in C#? What are the performance implications? |
| oops-026 | What is the difference between a namespace and an assembly in .NET? |
| oops-027 | What are the ref and out keywords in C#? When do you use each? |
| oops-028 | What are the different types of constructors in C#? |
| oops-029 | What are the different uses of the 'using' keyword in C#? |
| oops-030 | What is early binding and late binding in C#? Give real examples. |
| oops-031 | Can an abstract class have a parameterized constructor? How do you call it from a derived class? |
| oops-032 | Can a class implement two interfaces that have the same method name? How do you handle conflicts? |
| oops-033 | What is the difference between Array and ArrayList in C#? When do you use List<T>? |
| oops-034 | What is the difference between virtual/override and the new keyword for method hiding in C#? |
| oops-035 | What are extension methods in C#? How do you create one and when do you use them? |
| oops-036 | What is CTS (Common Type System) and CLS (Common Language Specification) in .NET? |
| oops-037 | What is Reflection in .NET? When have you actually used it? |
| oops-038 | What is the difference between method overloading and method overriding in C#? |
| oops-039 | What are the most commonly used String methods in C#? Give practical examples. |
| oops-040 | What are the types of inheritance in C#? Give examples. |
| oops-041 | What are the types of errors in C#? How does exception handling work? |
| oops-042 | Why would you use multiple catch blocks? When is it useful? |
| oops-043 | What are the types of collections in C#? Generic vs non-generic. |
| oops-044 | What is the difference between Dispose() and Finalize() in C#? |
| oops-045 | What is yield return in C#? When do you use it? |
| oops-046 | What are anonymous types in C#? When would you use them? |
| oops-047 | What causes memory leaks in C#? How do you detect and fix them? |
| oops-048 | What is C# and what makes it different from Java or C++? |
| oops-049 | What is the Stack and Heap in .NET? How are they different? |
| oops-050 | What is a partial class in C# and when do you use it? |
| oops-051 | What is constructor chaining in C# and how do you implement it? |
| oops-052 | How do you prevent a class from being instantiated without using the static or abstract keyword? |
| oops-053 | What is the difference between Hashtable, Dictionary, HashSet, and List in C#? |
| oops-054 | What causes a NullReferenceException in C# and how do you prevent it? |

---

## SOLID Principles (`questions-solid.json`) — 5 questions

| ID | Question |
|----|----------|
| solid-001 | What is the Single Responsibility Principle (SRP)? |
| solid-002 | What is the Open/Closed Principle (OCP)? |
| solid-003 | What is the Liskov Substitution Principle (LSP)? |
| solid-004 | What is the Interface Segregation Principle (ISP)? |
| solid-005 | What is the Dependency Inversion Principle (DIP)? |

---

## Angular (`questions-angular.json`) — 18 questions

| ID | Question |
|----|----------|
| angular-001 | What are Angular components and how do you create one? |
| angular-002 | What are Angular lifecycle hooks and when do you use each? |
| angular-003 | What is RxJS and how do you use it in Angular? |
| angular-004 | What is Angular's change detection and how does OnPush work? |
| angular-005 | What is the difference between Reactive Forms and Template-driven Forms in Angular? |
| angular-006 | How does Angular routing work and what is lazy loading? |
| angular-007 | What is data binding in Angular and what are its four types? |
| angular-008 | What are Angular directives and what are the different types? |
| angular-009 | What are Angular decorators? Explain @Component, @Input, @Output, and @Injectable. |
| angular-010 | How do you implement parent-to-child and child-to-parent communication in Angular? |
| angular-011 | How do sibling components communicate in Angular? |
| angular-012 | What are Angular pipes and how do you create a custom pipe? |
| angular-013 | What are HTTP Interceptors in Angular and how do you create one? |
| angular-014 | What is NgModule in Angular? Explain declarations, imports, exports, providers, and bootstrap. |
| angular-015 | What is the difference between constructor and ngOnInit in Angular? |
| angular-016 | What is the difference between JIT and AOT compilation in Angular? |
| angular-017 | How does Dependency Injection work in Angular? What is @Injectable? |
| angular-018 | What is Angular and what are its core features? |

---

## Authentication & Authorization (`questions-auth.json`) — 10 questions

| ID | Question |
|----|----------|
| auth-001 | What is JWT (JSON Web Token) and how does it work? |
| auth-002 | How do you implement JWT authentication in ASP.NET Core? |
| auth-003 | What is the difference between Authentication and Authorization? |
| auth-004 | What is OAuth 2.0 and how does it differ from OIDC? |
| auth-005 | What is ASP.NET Core Identity and when would you use it? |
| auth-006 | What are claims and how are they used in ASP.NET Core authorization? |
| auth-007 | What is CSRF (Cross-Site Request Forgery) and how do you prevent it in ASP.NET Core? |
| auth-008 | What is XSS (Cross-Site Scripting) and how do you prevent it in ASP.NET Core? |
| auth-009 | What is the structure of a JWT token? Explain Header, Payload, and Signature. |
| auth-010 | What is a Refresh Token? How do you implement token refresh in ASP.NET Core? |

---

## Async, Threading & Tasks (`questions-async.json`) — 11 questions

| ID | Question |
|----|----------|
| async-001 | What is async/await in C# and how does it work? |
| async-002 | What causes a deadlock with async/await and how do you fix it? |
| async-003 | What is the difference between Task.WhenAll and Task.WhenAny? |
| async-004 | What is CancellationToken and how do you use it? |
| async-005 | What is the difference between a Thread, Task, and async/await? |
| async-006 | What is async void and why is it dangerous? |
| async-007 | What is SemaphoreSlim and when do you use it for throttling? |
| async-008 | What is ValueTask and when should you use it instead of Task? |
| async-009 | How do you run CPU-bound work without blocking the ASP.NET Core request thread? |
| async-010 | What is IAsyncEnumerable and when do you use it? |
| async-011 | What is the lock keyword in C#? When do you use it and what are its gotchas? |

---

## EF Core & Dapper (`questions-efcore.json`) — 13 questions

| ID | Question |
|----|----------|
| efcore-001 | What is Entity Framework Core and how does it differ from Dapper? |
| efcore-002 | What is DbContext and how should it be used? |
| efcore-003 | What is the difference between eager loading, lazy loading, and explicit loading? |
| efcore-004 | What are EF Core migrations and how do they work? |
| efcore-005 | What is the Repository pattern with EF Core? Should you use it? |
| efcore-006 | What is AsNoTracking() and when should you use it? |
| efcore-007 | How do you handle concurrency conflicts in EF Core? |
| efcore-008 | How do you use raw SQL in EF Core? |
| efcore-009 | What is the difference between Add(), Attach(), and Update() in EF Core? |
| efcore-010 | How do you configure EF Core using Fluent API vs Data Annotations? |
| efcore-011 | What is the difference between Code First and Database First approaches in Entity Framework Core? |
| efcore-012 | What are shadow properties in EF Core? When would you use them? |
| efcore-013 | How do you use Stored Procedures with ADO.NET? What is the difference vs inline SQL in ADO.NET? |

---

## Middleware & Filters (`questions-middleware.json`) — 7 questions

| ID | Question |
|----|----------|
| middleware-001 | What is middleware in ASP.NET Core? How does the pipeline work? |
| middleware-002 | What is the difference between middleware and filters in ASP.NET Core? |
| middleware-003 | How do you create custom middleware in ASP.NET Core? |
| middleware-004 | What is the order of middleware execution and why does it matter? |
| middleware-005 | What are the different types of filters in ASP.NET Core MVC? |
| middleware-006 | How do you implement request/response logging middleware? |
| middleware-007 | What is short-circuiting in middleware? When and why do you do it? |

---

## Design Patterns (`questions-patterns.json`) — 8 questions

| ID | Question |
|----|----------|
| patterns-001 | What is the Repository pattern and why is it used? |
| patterns-002 | What is the Strategy pattern and how do you implement it in C#? |
| patterns-003 | What is the Factory pattern and its variants? |
| patterns-004 | What is the Decorator pattern and how do you use it in .NET? |
| patterns-005 | What is the Observer pattern and how is it implemented in C#? |
| patterns-006 | What is CQRS (Command Query Responsibility Segregation)? |
| patterns-007 | What is the Singleton pattern and how is it different from Singleton lifetime in DI? |
| patterns-008 | What is Clean Architecture? How do you structure a .NET project using it? |

---

## Microservices & Architecture (`questions-microservices.json`) — 10 questions

| ID | Question |
|----|----------|
| ms-001 | What are microservices and how do they differ from a monolith? |
| ms-002 | What is an API Gateway and what does it do? |
| ms-003 | What is event-driven architecture and how does it apply to microservices? |
| ms-004 | What is the Circuit Breaker pattern and why is it important in microservices? |
| ms-005 | What is Clean Architecture and how does it relate to microservices? |
| ms-006 | What is Docker and how do you containerize an ASP.NET Core application? |
| ms-007 | What is gRPC and when would you use it instead of REST? |
| ms-008 | What is SignalR and when would you use it over regular REST polling? |
| ms-009 | What is CI/CD and how do you set it up for a .NET application? |
| ms-010 | What is Azure App Service? How do you deploy an ASP.NET Core app to it? |

---

## LINQ (`questions-linq.json`) — 10 questions

| ID | Question |
|----|----------|
| linq-001 | What is LINQ in C#? What are the two syntax styles? |
| linq-002 | What is deferred execution vs immediate execution in LINQ? |
| linq-003 | What are the most commonly used LINQ methods? Give examples of each. |
| linq-004 | How do you implement a LEFT JOIN in LINQ? What is the difference from an INNER JOIN? |
| linq-005 | How does GroupBy work in LINQ? Give a practical example with multiple aggregates. |
| linq-006 | What is the difference between LINQ to Objects and LINQ to Entities? What operations are not translatable? |
| linq-007 | How do you use Aggregate() in LINQ? What is it equivalent to? |
| linq-008 | What is the difference between Select() and SelectMany() in LINQ? |
| linq-009 | What is the difference between IEnumerable<T> and IQueryable<T> in C#? |
| linq-010 | What is the difference between First() vs FirstOrDefault() and Single() vs SingleOrDefault()? |

---

## Testing (`questions-testing.json`) — 5 questions

| ID | Question |
|----|----------|
| testing-001 | What is unit testing and what makes a good unit test? |
| testing-002 | How do you mock dependencies in .NET using Moq? |
| testing-003 | What is integration testing in ASP.NET Core and how do you write one? |
| testing-004 | What is TDD (Test-Driven Development)? How does it work? |
| testing-005 | What is code coverage and how do you measure it in .NET? |

---

## Coding Problems (`questions-coding.json`) — 19 questions

| ID | Question |
|----|----------|
| coding-001 | Reverse a string in C# — multiple approaches |
| coding-002 | Check if a string is a palindrome |
| coding-003 | Find the factorial of a number — recursive and iterative |
| coding-004 | Find the Fibonacci sequence — iterative, recursive, and dynamic programming |
| coding-005 | Find duplicates in an array |
| coding-006 | Find the two numbers in an array that sum to a target (Two Sum) |
| coding-007 | Remove duplicates from a sorted array in-place |
| coding-008 | Find the maximum subarray sum (Kadane's Algorithm) |
| coding-009 | Implement a stack using a queue and a queue using a stack |
| coding-010 | Implement binary search |
| coding-011 | Print a pyramid (triangle) star pattern with N rows in C# |
| coding-012 | Swap two numbers without using a temporary variable in C# |
| coding-013 | Reverse each word individually in a sentence while keeping the words in their original positions |
| coding-014 | Find the first non-repeating character in a string |
| coding-015 | Find the largest number in an array in C# |
| coding-016 | Check whether a number is prime in C# |
| coding-017 | Count occurrences of each character in a string in C# |
| coding-018 | Find the missing numbers from a sorted integer array in C# |
| coding-019 | Find the second highest number in an array in C# |

---

## Behavioral & HR (`questions-behavioral.json`) — 54 questions

> (beh-001 through beh-054 — HR/soft skills questions, not enumerated here for brevity)

---

## GRAND TOTAL

| Category | Count |
|----------|-------|
| Azure & Cloud | 6 |
| Dependency Injection | 13 |
| Database & SQL | 68 |
| Web API | 46 |
| MVC | 24 |
| OOPS | 54 |
| SOLID | 5 |
| Angular | 18 |
| Auth & Authorization | 10 |
| Async / Threading | 11 |
| EF Core & Dapper | 13 |
| Middleware & Filters | 7 |
| Design Patterns | 8 |
| Microservices | 10 |
| LINQ | 10 |
| Testing | 5 |
| Coding Problems | 19 |
| Behavioral & HR | 54 |
| **TOTAL** | **381** |

---

## Coverage: Infosys Round 1 — All Mapped

| # | Question | Covered By |
|---|----------|------------|
| 1 | Tell me about yourself | beh category |
| 2 | Explain your project | beh + project guides |
| 3 | IEnumerable vs IQueryable | linq-009 ✓ |
| 4 | LINQ Coding Question | linq-003 ✓ |
| 5 | First vs FirstOrDefault | linq-010 ✓ |
| 6 | Single vs SingleOrDefault | linq-010 ✓ |
| 7 | Managed Code vs Unmanaged Code | oops-024 ✓ |
| 8 | Explain Caching | webapi-023 ✓ |
| 9 | Entity Framework Approaches | efcore-011 ✓ |
| 10 | SOLID Principles | solid-001 to solid-005 ✓ |
| 11 | Dependency Injection | di-001 ✓ |
| 12 | Service Lifetimes | di-002 ✓ |
| 13 | Explain Singleton | di-002, patterns-007 ✓ |
| 14 | What is C# | oops-048 ✓ |
| 15 | .NET vs .NET Core | mvc-007 ✓ |
| 16 | Abstract Class vs Interface | oops-002 ✓ |
| 17 | What is Constructor | oops-028 ✓ |
| 18 | Explain Kestrel | webapi-017 ✓ |
| 19 | What is Web API | webapi-001 ✓ |
| 20 | HTTP Status Codes | webapi-003, webapi-042 ✓ |
| 21 | Explain Microservices | ms-001 ✓ |
| 22 | Explain MVC | mvc-001 ✓ |
| 23 | appsettings.json | webapi-028 ✓ |
| 24 | OOP Concepts | oops-001 ✓ |
| 25 | Overloading vs Overriding | oops-038 ✓ |
| 26 | REST APIs | webapi-001, webapi-039 ✓ |
| 27 | Delegates | oops-007 ✓ |
| 28 | Array vs ArrayList | oops-033 ✓ |
| 29 | Partial vs Sealed | oops-050 (partial), oops-015 (sealed) ✓ |
| 30 | Routing | webapi-004, mvc-014 ✓ |
| 31 | Authentication vs Authorization | auth-003 ✓ |
| 32 | Azure Services | azure-001 ✓ |
| 33 | Azure Key Vault | azure-002 ✓ |
| 34 | Azure Blob Storage | azure-003 ✓ |
| 35 | Explain CI/CD | azure-006, ms-009 ✓ |
| 36 | What is Angular | angular-018 ✓ |
| 37 | Directives | angular-008 ✓ |
| 38 | Components | angular-001 ✓ |
| 39 | Angular Routing | angular-006 ✓ |
| 40 | Component Communication | angular-010, angular-011 ✓ |
| 41 | DI in Angular | angular-017 ✓ |

## Coverage: LTI Mindtree — All Mapped

| Topic | Covered By |
|-------|------------|
| Stack vs Heap | oops-049 ✓ |
| Garbage Collector | oops-010 ✓ |
| Prevent instantiation (no static/abstract) | oops-052 ✓ |
| How to create DI | di-001 ✓ |
| Where does injected dependency reside | di-013 ✓ |
| Constructor chaining | oops-051 ✓ |
| Partial class | oops-050 ✓ |
| Partial class in different projects? | oops-050 ✓ |
| NullReferenceException types | oops-054 ✓ |
| Task vs Thread / Multithreading | async-005 ✓ |
| IEnumerable vs IQueryable | linq-009 ✓ |
| Hashtable vs Dictionary / HashSet vs Dictionary | oops-053 ✓ |
| Ref vs Out | oops-027 ✓ |
| IDisposable | oops-013 ✓ |
| .NET Framework vs .NET Core | mvc-007 ✓ |
| Async & Await | async-001 ✓ |
| What is ADO.NET | webapi-018 ✓ |
| SP with ADO.NET | efcore-013 ✓ |
| SQL query vs SP in ADO.NET | efcore-013 ✓ |
| EF Migrations commands | efcore-004 ✓ |
| AsNoTracking | efcore-006 ✓ |
| Code First vs Database First | efcore-011 ✓ |
| Eager loading | efcore-003 ✓ |
| Views vs Indexes | db-003, db-015 ✓ |
| Index types | db-003, db-014 ✓ |
| Triggers | db-020 ✓ |
| SP vs Function | db-043 ✓ |
| What is SP | db-004 ✓ |
| Where vs Having | db-002 ✓ |
| CTE | db-011 ✓ |
| SQL function multiple return types | db-068 ✓ |
| Types of joins | db-001 ✓ |
| If commission is null return 0 | db-063 (COALESCE) ✓ |
| Get Nth highest salary | db-065 ✓ |
| Department with 0 employees | db-066 ✓ |
| How to identify missing index | db-067 ✓ |
| SQL optimization techniques | db-042 ✓ |
| Last inserted record | db-038 ✓ |
| Authentication & Authorization | auth-003 ✓ |
| JWT | auth-001, auth-009 ✓ |
| Logging | webapi-024 ✓ |
| Exception handling | webapi-010, mvc-023 ✓ |
| Middlewares | middleware category ✓ |
| REST principles | webapi-001 ✓ |
| Routing | webapi-004, mvc-014 ✓ |
| Model validation | webapi-006 ✓ |
| HTTP methods | webapi-002 ✓ |
| 200 vs 201 | webapi-003 ✓ |
| [HttpPost] on GET action | webapi-043 ✓ |
| DRY / clean code | webapi-044 ✓ |
| Return error to client | webapi-045 ✓ |
| DropDown performance | webapi-046 ✓ |
| Multiple views / shared views | mvc-024 ✓ |
| Azure Functions | azure-004 ✓ |
| Azure Key Vault + .NET | azure-002 ✓ |
| Handling API issues in Azure | azure-005 ✓ |
| Design patterns (Factory) | patterns-003 ✓ |
| SOLID principles | solid category ✓ |
| OCP violation example | solid-002 ✓ |
| Caching (memory vs Redis) | webapi-023 ✓ |
| Microservices | ms-001 ✓ |
