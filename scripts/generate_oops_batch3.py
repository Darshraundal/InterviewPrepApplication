import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src/InterviewPrepPortal/Data/JsonData/questions-oops.json"
OUTPUT = Path(__file__).resolve().parents[1] / "src/InterviewPrepPortal/Data/JsonData/oops_batch3.json"

TABLE = 'style="width:100%;font-size:.85rem;border-collapse:collapse;"'
CELL = 'style="border:1px solid #555;padding:4px;"'


def cell(text, header=False):
    tag = "th" if header else "td"
    return f'<{tag} {CELL}>{text}</{tag}>'


def table(headers, rows):
    parts = [f'<table {TABLE}><tr>']
    parts.extend(cell(h, True) for h in headers)
    parts.append('</tr>')
    for row in rows:
        parts.append('<tr>')
        parts.extend(cell(c) for c in row)
        parts.append('</tr>')
    parts.append('</table>')
    return ''.join(parts)


def code_block(body: str) -> str:
    return f'<pre><code class="language-csharp">{body}</code></pre>'


def build_answer(simple, advantages, fintech_p, code, diff_table, final, trick):
    parts = [
        '<h4>📌 SIMPLE DEFINITION</h4>',
        f'<p>{simple}</p>',
        '<h4>✅ ADVANTAGES</h4>',
        table(['Advantage', 'Why It Matters'], advantages),
        '<h4>🏦 FINTECH EXAMPLE (C#)</h4>',
        f'<p>{fintech_p}</p>',
        code_block(code),
    ]
    if diff_table:
        parts.append('<h4>📊 DIFFERENCE TABLE</h4>')
        parts.append(diff_table)
    parts.extend([
        '<h4>🎤 FINAL INTERVIEW ANSWER</h4>',
        f'<p>{final}</p>',
        '<h4>🧠 ONE LINE MEMORY TRICK</h4>',
        f'<p>{trick}</p>',
    ])
    return ''.join(parts)


ANSWERS = {
    'oops-025': build_answer(
        'Boxing wraps a value type (int, decimal, struct) in a heap-allocated object reference; unboxing extracts it back with an explicit cast. Both are expensive compared to direct value-type operations — like putting a coin in a gift box (boxing) and taking it back out (unboxing), costing memory and time every time.',
        [
            ['Generics eliminate boxing in collections', 'List&lt;decimal&gt; stores value types directly — no heap allocation per Add()'],
            ['Understanding boxing reveals hidden performance costs', 'ArrayList and non-generic collections silently box every value type'],
            ['Avoiding boxing reduces GC pressure', 'High-throughput payment engines avoid millions of unnecessary heap allocations'],
            ['Compile-time type safety with generics', 'No runtime InvalidCastException when unboxing from object'],
            ['Modern .NET optimizes common paths', '.NET 6+ string interpolation overloads reduce implicit boxing'],
        ],
        'A high-throughput transaction engine processing 100,000 transactions/second: storing decimal amounts in ArrayList boxes every Add() and unboxes every retrieval — 200,000 heap allocations per second. List&lt;decimal&gt; eliminates all boxing.',
        '// Explicit boxing and unboxing\nint transactionCount = 42;\nobject boxed = transactionCount;         // BOXING: heap allocation, value copied\nint unboxed = (int)boxed;                // UNBOXING: type check + value copy\n\n// Wrong unbox type throws at runtime\n// double wrong = (double)boxed;         // InvalidCastException!\n\n// HIDDEN boxing: ArrayList stores object\nvar legacyList = new System.Collections.ArrayList();\nlegacyList.Add(100m);    // decimal BOXED — heap allocation!\nlegacyList.Add(200m);    // another boxing\ndecimal val = (decimal)legacyList[0]; // UNBOXING + cast\n\n// NO boxing: generic List&lt;T&gt;\nvar modernList = new List&lt;decimal&gt;();\nmodernList.Add(100m);    // no boxing — stored directly\nmodernList.Add(200m);\ndecimal val2 = modernList[0]; // no unboxing — direct access\n\n// Hidden boxing: struct through interface\ninterface ITransaction { decimal GetAmount(); }\nstruct SimpleTransaction : ITransaction\n{\n    public decimal Amount;\n    public decimal GetAmount() => Amount;\n}\nSimpleTransaction t = new() { Amount = 5000m };\nITransaction iFace = t;          // BOXING: struct copied to heap\nConsole.WriteLine(iFace.GetAmount()); // Expected: 5000',
        table(
            ['Operation', 'Direction', 'Cost'],
            [
                ['Boxing', 'value type → object', 'Heap allocation + copy'],
                ['Unboxing', 'object → value type', 'Type check + copy'],
            ],
        ),
        'Boxing wraps a value type in a heap-allocated object — it requires a heap allocation and a copy of the value. Unboxing extracts the value back — requires a runtime type check and another copy. Performance cost: heap allocation triggers GC pressure; type check has overhead; both involve memory copies. The solution is generics — List&lt;decimal&gt; stores decimals directly without boxing, unlike the legacy ArrayList which stores object. In any performance-sensitive fintech code, I always use generic collections and avoid any code path that implicitly boxes value types in hot loops. Watch for hidden boxing: passing an int to a method accepting object, storing value types in ArrayList or Hashtable, calling an interface method on a struct through an interface variable, and string interpolation before .NET 6. Generics were invented largely to eliminate boxing from collection operations.',
        'Boxing = putting a coin (value type) into a gift box (heap object). Unboxing = taking the coin back out. Every box costs memory and GC time. Generics = carrying coins directly without ever boxing them.',
    ),
    'oops-026': build_answer(
        'A namespace is a logical grouping of types in source code — it exists only as metadata to organize types and prevent name collisions. An assembly is a physical deployment unit — a compiled DLL or EXE containing IL code, metadata, and resources. Think of namespace as a folder path (logical) and assembly as the actual file on disk (physical).',
        [
            ['Namespaces organize code without physical boundaries', 'System.Text.Json and Newtonsoft.Json coexist via different namespaces'],
            ['Same namespace can span multiple assemblies', 'PaymentPlatform.Models can exist in Core.dll and Infrastructure.dll'],
            ['Assemblies enable independent versioning and deployment', 'Core assembly ships v1.2 without changing the API assembly'],
            ['Using aliases resolve name collisions', 'SystemJson vs NewtonsoftJson for two JsonSerializer types'],
            ['Assemblies are the security and deployment unit', 'NuGet packages ship as assemblies with version metadata'],
        ],
        'A payment platform ships as three assemblies: PaymentPlatform.Core.dll (domain models), PaymentPlatform.Infrastructure.dll (database, HTTP), and PaymentPlatform.Api.dll (controllers). All use the PaymentPlatform namespace hierarchy but version independently.',
        '// Namespace: logical grouping — no physical boundary\nnamespace PaymentPlatform.Services.Payments\n{\n    public class UpiPaymentService { }\n    public class NeftPaymentService { }\n}\n\nnamespace PaymentPlatform.Services.Notifications\n{\n    public class SmsNotificationService { }\n}\n\n// One assembly can contain both namespaces\n// One namespace can span multiple assemblies\n\nusing PaymentPlatform.Services.Payments;\nusing SystemJson = System.Text.Json.JsonSerializer;\nusing NewtonsoftJson = Newtonsoft.Json.JsonConvert;\n\nvar assembly = Assembly.GetExecutingAssembly();\nConsole.WriteLine(assembly.GetName().Name);    // PaymentPlatform\nConsole.WriteLine(assembly.GetName().Version); // 1.2.0.0\n\nvar types = assembly.GetTypes()\n    .Where(t => t.Namespace == "PaymentPlatform.Services.Payments")\n    .ToList();\nConsole.WriteLine($"Payment types: {types.Count}"); // Expected: count of payment service types',
        table(
            ['Feature', 'Namespace', 'Assembly'],
            [
                ['Nature', 'Logical grouping', 'Physical file (.dll/.exe)'],
                ['Versioning', 'No', 'Yes'],
                ['Deployment unit', 'No', 'Yes'],
                ['Span multiple files', 'Yes', 'No (one file)'],
            ],
        ),
        'Namespace is a logical concept — it groups types to avoid name collisions and organizes code. No physical boundary exists. The same namespace can span multiple assemblies, and one assembly can contain multiple namespaces. Assembly is a physical file — a DLL or EXE containing compiled IL, metadata, and resources. It is the unit of deployment and versioning. When you reference a NuGet package, you are referencing its assembly. The namespace just tells the compiler how to resolve type names — it has no runtime meaning beyond metadata. In .NET Framework, the GAC was a machine-wide cache for shared assemblies; in modern .NET Core / .NET 5+, each app bundles its own copy, eliminating DLL Hell.',
        'Namespace = folder path (logical). Assembly = the actual file on disk (physical). Same folder name can exist on different drives; one file can contain multiple folders.',
    ),
    'oops-027': build_answer(
        'ref passes a variable by reference — the method can read and modify the caller\'s variable; the variable must be initialized before passing. out also passes by reference but the variable does not need to be initialized — the method must assign it before returning. Think: out = the method gives you a package (empty box in); ref = the method modifies your existing package (filled box).',
        [
            ['out enables the TryXxx pattern', 'bool TryParse returns success without exceptions for expected failures'],
            ['ref enables efficient two-way communication', 'Modify payment amount in place during multi-step discount chain'],
            ['in (C# 7.2) passes large structs by reference read-only', 'Avoids copying 200-byte structs without mutation risk'],
            ['Both allow returning multiple values', 'TryParseUpiId returns bool + VPA + bank code via out parameters'],
            ['Inline out declaration (C# 7+)', 'if (TryParse("5000", out decimal amount)) — cleaner syntax'],
        ],
        'TryParseUpiId uses out parameters to return VPA and bank code without throwing for invalid input. ApplyLoyaltyDiscount uses ref to modify the payment amount in place during a multi-step discount calculation chain.',
        '// ref: must be assigned before call, method can read AND write\npublic void ApplyLoyaltyDiscount(ref decimal amount, decimal discountPercent)\n{\n    amount = amount - (amount * discountPercent / 100);\n}\n\ndecimal paymentAmount = 10000m;\nApplyLoyaltyDiscount(ref paymentAmount, 10m);\nConsole.WriteLine(paymentAmount); // Expected: 9000.00\n\n// out: no prior assignment needed, method MUST assign\npublic bool TryParseUpiId(string input, out string vpa, out string bank)\n{\n    vpa = string.Empty;\n    bank = string.Empty;\n    if (string.IsNullOrWhiteSpace(input) || !input.Contains(\'@\')) return false;\n    var parts = input.Split(\'@\');\n    vpa = parts[0]; bank = parts[1];\n    return true;\n}\n\nif (TryParseUpiId("darshan@okicici", out string vpa, out string bankCode))\n    Console.WriteLine($"VPA: {vpa}, Bank: {bankCode}");\n// Expected: VPA: darshan, Bank: okicici\n\nif (decimal.TryParse("5000.50", out decimal amount))\n    Console.WriteLine($"Parsed: {amount}"); // Expected: Parsed: 5000.50\n\n// in: read-only ref for large structs\npublic decimal CalculateTax(in PaymentDetails details)\n    => details.Amount * details.TaxRate;\npublic record PaymentDetails(decimal Amount, decimal TaxRate);',
        table(
            ['Keyword', 'Must Initialize Before', 'Method Can Read', 'Method Can Write'],
            [
                ['ref', 'Yes', 'Yes', 'Yes'],
                ['out', 'No', 'No (until assigned)', 'Yes (required)'],
                ['in', 'Yes', 'Yes', 'No (compile error)'],
            ],
        ),
        'ref passes a variable by reference — the caller must initialize it, and the method can both read and modify it. out also passes by reference but the caller doesn\'t need to initialize the variable — the method must assign it before returning. The TryXxx pattern uses out: bool TryGetValue, bool TryParse, Dictionary.TryGetValue. in (C# 7.2) is a read-only ref — the method receives a reference to avoid copying a large struct but cannot modify it. You cannot overload a method by changing only ref/out — they are not part of the signature for distinguishing overloads from each other. Also, ref and out cannot be used with async methods or iterators. Memory aid: out = output (method gives something). ref = reference (two-way exchange). in = input reference (no copy, no modification).',
        'out = the method gives you a package (you bring an empty box). ref = the method modifies your existing package (you bring a filled box). in = the method reads your package but doesn\'t touch it.',
    ),
    'oops-028': build_answer(
        'A constructor is a special method called automatically when an object is created to initialize its state. C# supports five types: default (no parameters), parameterized, copy, static, and private constructors — like assembly instructions in a factory for different product configurations.',
        [
            ['Guarantees objects start in a valid state', 'BankAccount rejects null account number or negative balance at creation'],
            ['Constructor overloading provides convenient creation paths', 'Zero-balance overload chains to primary constructor via :this()'],
            ['Private constructor enforces Singleton or Factory patterns', 'Controlled instantiation through CreateEmpty() factory method'],
            ['Static constructor runs class-level init exactly once', 'Loads reserved account number ranges before any instance is created'],
            ['Constructor chaining avoids duplicate logic', 'Convenience overloads delegate validation to one primary constructor'],
        ],
        'BankAccount constructor validates AccountNumber and initial balance. The convenience overload creates a zero-balance account. Static constructor loads reserved account numbers once at startup. Private constructor supports a Factory method with business-specific creation rules.',
        'public class BankAccount\n{\n    public string AccountNumber { get; }\n    public decimal Balance { get; private set; }\n    private static readonly HashSet&lt;string&gt; _reservedNumbers;\n\n    // 1. Parameterized constructor (primary)\n    public BankAccount(string accountNumber, string holderName, decimal initialBalance)\n    {\n        if (string.IsNullOrWhiteSpace(accountNumber)) throw new ArgumentException("Account number required");\n        if (initialBalance &lt; 0) throw new ArgumentException("Initial balance cannot be negative");\n        AccountNumber = accountNumber;\n        Balance = initialBalance;\n    }\n\n    // 2. Constructor chaining via :this()\n    public BankAccount(string accountNumber, string holderName)\n        : this(accountNumber, holderName, 0m) { }\n\n    // 3. Copy constructor\n    public BankAccount(BankAccount source)\n        : this(source.AccountNumber + "-COPY", source.HolderName, source.Balance) { }\n\n    // 4. Static constructor — runs once before first use\n    static BankAccount()\n    {\n        _reservedNumbers = new HashSet&lt;string&gt; { "0000000000", "9999999999" };\n        Console.WriteLine("BankAccount type initialized");\n    }\n\n    // 5. Private constructor for Factory\n    private BankAccount() { }\n    public static BankAccount CreateEmpty() => new BankAccount { Balance = 0 };\n}\n// Expected on first use: BankAccount type initialized',
        table(
            ['Type', 'When Called', 'Use Case'],
            [
                ['Default', 'new MyClass()', 'Zero-arg creation (auto-generated if no other ctor)'],
                ['Parameterized', 'new MyClass(args)', 'Enforce required state with validation'],
                ['Static', 'Before first use of type', 'One-time class initialization'],
                ['Private', 'Via Factory/Singleton', 'Controlled instantiation'],
            ],
        ),
        'C# has five constructor types: default (no params, auto-generated if no other constructor is defined), parameterized (enforces required initial state), copy (manual in C#, copies another instance), static (runs once before first use of the type for class-level initialization), and private (prevents direct instantiation — used for Singleton and Factory patterns). Constructor chaining with :this() avoids duplicate initialization — convenience overloads delegate to a primary constructor with all validation. When you define any constructor, the compiler stops generating the default one. Static constructor gotcha: you cannot control when it runs, you cannot call it explicitly, and if it throws, the type becomes permanently unusable for the AppDomain lifetime. In inheritance, :base() calls the parent constructor before the derived body runs.',
        'Constructors are like assembly instructions: default = basic assembly, parameterized = custom order, static = factory setup once before any product, private = only the factory manager starts the line.',
    ),
    'oops-029': build_answer(
        'The using keyword in C# has four distinct meanings: importing namespaces (using directive), deterministic resource cleanup (using statement), scope-based disposal without braces (using declaration in C# 8+), and project-wide namespace imports (global using in C# 10+). For cleanup, it means "I\'m done with this — clean it up automatically when I leave."',
        [
            ['Guarantees resource cleanup even on exceptions', 'SqlConnection and file handles always disposed — no finally boilerplate'],
            ['Global using reduces repetitive imports', 'One GlobalUsings.cs covers 50+ controller and service files'],
            ['Type aliases resolve naming conflicts', 'DecimalList alias for List&lt;decimal&gt; in large codebases'],
            ['C# 8 using declaration eliminates nesting', 'Cleaner single-resource scopes without brace blocks'],
            ['await using supports async disposal', 'IAsyncDisposable for DbContext and network streams'],
        ],
        'In a payment data export job, using declarations for SqlConnection, SqlCommand, and StreamWriter guarantee all connections and files are closed even if an exception occurs mid-export — preventing connection pool exhaustion.',
        '// 1. Using directive: import namespace\nusing System.Data.SqlClient;\nusing static System.Math;\nusing DecimalList = System.Collections.Generic.List&lt;decimal&gt;;\n\n// 2. Using statement: scoped disposal with braces\npublic string GenerateBankStatement(string accountId)\n{\n    using (var conn = new SqlConnection(_connString))\n    using (var cmd = conn.CreateCommand())\n    {\n        conn.Open();\n        cmd.CommandText = "SELECT * FROM Transactions WHERE AccountId = @id";\n        cmd.Parameters.AddWithValue("@id", accountId);\n        using var reader = cmd.ExecuteReader();\n        var sb = new StringBuilder();\n        while (reader.Read())\n            sb.AppendLine($"{reader["Date"]}: {reader["Amount"]:C}");\n        return sb.ToString();\n    } // conn and cmd disposed here\n}\n\n// 3. Using declaration (C# 8+): disposed at end of scope\npublic async Task ProcessTransactionFileAsync(string path)\n{\n    using var file = File.OpenRead(path);\n    using var reader = new StreamReader(file);\n    string? line;\n    while ((line = await reader.ReadLineAsync()) != null)\n        await ProcessLineAsync(line);\n} // file and reader disposed when method ends\n\n// 4. Global using (C# 10+): in GlobalUsings.cs\n// global using System.Text.Json;\n// global using PaymentPlatform.Models;',
        table(
            ['Form', 'C# Version', 'Purpose'],
            [
                ['using directive', 'All', 'Import namespace or type alias'],
                ['using statement', 'All', 'Scoped disposal (braces) — compiles to try/finally'],
                ['using declaration', 'C# 8+', 'Scoped disposal (no braces)'],
                ['global using', 'C# 10+', 'Project-wide namespace import'],
            ],
        ),
        'The using keyword has four uses in C#. First, namespace import: using System.Collections.Generic. Second, using statement: using (var conn = new SqlConnection(...)) { } — compiles to try/finally, guarantees Dispose() on scope exit. Third, using declaration (C# 8+): using var conn = new SqlConnection(...) — no braces, disposed at end of enclosing scope. Fourth, global using (C# 10+): global using MyNamespace — imports the namespace for every file in the project. Any class holding unmanaged resources (file handles, DB connections, network sockets) should implement IDisposable, and callers should always wrap it in using. If Dispose() throws inside a using block while the body also throws, the original exception is lost — best practice is to write Dispose() so it never throws.',
        'using for cleanup = "I\'m done with this, clean it up automatically when I leave." The compiler writes the try/finally for you so you don\'t forget.',
    ),
    'oops-030': build_answer(
        'Early binding (static binding) means the compiler resolves which method to call at compile time — the call target is fixed in the IL. Late binding (dynamic binding) means the method is determined at runtime — via virtual methods (vtable), the dynamic keyword, or reflection. Early binding = GPS with a fixed route; late binding = navigation that decides turn by turn as you drive.',
        [
            ['Early binding: maximum performance and type safety', 'FeeCalculator.Calculate() resolved at compile time — full IntelliSense'],
            ['Late binding via virtual: enables polymorphism', 'PaymentGateway.ChargeAsync() dispatches to Razorpay or PayU at runtime'],
            ['Late binding via dynamic: runtime flexibility', 'COM interop and JSON responses without compile-time type info'],
            ['Late binding via reflection: plugin architectures', 'Load partner bank DLLs and register IPaymentGateway at startup'],
            ['Strategy pattern powered by virtual dispatch', 'Add new payment rail without changing the routing engine'],
        ],
        'The payment routing engine holds a PaymentGateway reference and calls ChargeAsync() — late binding via vtable selects RazorpayGateway or PayUGateway at runtime. Reflection loads partner bank plugins as DLLs without compile-time references.',
        '// Early binding: method resolved at compile time\nvar calculator = new FeeCalculator();\ndecimal fee = calculator.Calculate(5000m);  // compiler knows exactly which Calculate\n\npublic abstract class PaymentGateway\n{\n    public abstract Task&lt;bool&gt; ChargeAsync(decimal amount, string token);\n}\n\npublic class RazorpayGateway : PaymentGateway\n{\n    public override async Task&lt;bool&gt; ChargeAsync(decimal amount, string token)\n    {\n        Console.WriteLine($"Razorpay: charging {amount}");\n        return true;\n    }\n}\n\npublic class PayUGateway : PaymentGateway\n{\n    public override async Task&lt;bool&gt; ChargeAsync(decimal amount, string token)\n    {\n        Console.WriteLine($"PayU: charging {amount}");\n        return true;\n    }\n}\n\nPaymentGateway gateway = new RazorpayGateway();\nawait gateway.ChargeAsync(5000m, "tok_123");\n// Expected output: Razorpay: charging 5000\n\n// Late binding via dynamic\ndynamic response = await httpClient.GetFromJsonAsync&lt;dynamic&gt;("/api/rates");\nConsole.WriteLine(response.usdToInr); // resolved at runtime via DLR',
        table(
            ['Binding Type', 'When Resolved', 'Performance', 'Type Safety'],
            [
                ['Early (static)', 'Compile time', 'Fastest', 'Full'],
                ['Late via virtual', 'Runtime (vtable)', 'Near native', 'Full'],
                ['Late via dynamic', 'Runtime (DLR)', 'Slower', 'None at compile time'],
                ['Late via reflection', 'Runtime', 'Slowest', 'Runtime only'],
            ],
        ),
        'Early binding means the compiler decides which method to call at compile time — it is the default for all regular method calls and produces the most efficient IL. Late binding defers that decision to runtime. The most common form is virtual dispatch: calling ChargeAsync() on a PaymentGateway reference dispatches to the actual implementation at runtime via the vtable — this is polymorphism. Every class with virtual methods has a vtable — an array of function pointers. When you call animal.Speak() on a Dog instance through an Animal reference, the CLR looks up Speak in Dog\'s vtable. The dynamic keyword uses the DLR for runtime dispatch with no compile-time type checking. Reflection uses GetMethod().Invoke() — most flexible but slowest. In fintech, virtual dispatch powers the payment strategy pattern; reflection powers plugin discovery at startup.',
        'Early binding = GPS with a fixed route calculated before you leave. Late binding = navigation that decides turn by turn. Virtual dispatch is a fast GPS; reflection is asking for directions at every intersection.',
    ),
    'oops-031': build_answer(
        'Yes, an abstract class can have a parameterized constructor. Since abstract classes cannot be instantiated directly, their constructors are always called through derived class constructors using the : base(...) syntax — like a building foundation you cannot live in, but every floor must be built on top of it first.',
        [
            ['Centralizes common initialization in one place', 'Gateway name, logger, and transaction limit set once in base constructor'],
            ['Compiler enforces derived classes supply required args', 'All processors must call : base("Razorpay", 500000m, logger)'],
            ['Base class invariants established before derived runs', 'ValidateAmount() uses _maxTransactionLimit set only by base constructor'],
            ['Protected constructor prevents direct instantiation', 'Abstract class cannot be new\'d — only derived classes call base()'],
            ['Shared validation logic without duplication', 'Every gateway enforces its limit consistently via base class method'],
        ],
        'BasePaymentProcessor holds gateway name, logger, and transaction limit — common to all gateways. RazorpayProcessor calls : base("Razorpay", 500000m, logger) to initialize shared state. ValidateAmount() in the base class uses _maxTransactionLimit without copy-pasting validation in every gateway.',
        'public abstract class BasePaymentProcessor\n{\n    public string GatewayName { get; }\n    protected readonly ILogger _logger;\n    protected readonly decimal _maxTransactionLimit;\n\n    protected BasePaymentProcessor(string gatewayName, decimal maxLimit, ILogger logger)\n    {\n        if (string.IsNullOrWhiteSpace(gatewayName))\n            throw new ArgumentException("Gateway name required");\n        GatewayName = gatewayName;\n        _maxTransactionLimit = maxLimit;\n        _logger = logger;\n    }\n\n    public abstract Task&lt;PaymentResult&gt; ChargeAsync(decimal amount, string token);\n\n    protected void ValidateAmount(decimal amount)\n    {\n        if (amount &lt;= 0) throw new ArgumentException("Amount must be positive");\n        if (amount &gt; _maxTransactionLimit)\n            throw new InvalidOperationException(\n                $"{GatewayName}: amount {amount} exceeds limit {_maxTransactionLimit}");\n    }\n}\n\npublic class RazorpayProcessor : BasePaymentProcessor\n{\n    public RazorpayProcessor(string apiKey, ILogger&lt;RazorpayProcessor&gt; logger)\n        : base("Razorpay", 500000m, logger)  // base(...) called first\n    { }\n\n    public override async Task&lt;PaymentResult&gt; ChargeAsync(decimal amount, string token)\n    {\n        ValidateAmount(amount);\n        _logger.LogInformation("{Gateway}: charging {Amount}", GatewayName, amount);\n        return new PaymentResult(true);\n    }\n}\n\npublic record PaymentResult(bool Success, string? Error = null);\n// Expected: Razorpay logs charge, ValidateAmount rejects amounts over 500000',
        table(
            ['Step', 'Execution Order'],
            [
                ['new RazorpayProcessor(...) called', ':base() resolves and runs BasePaymentProcessor constructor first'],
                ['Base constructor completes', 'RazorpayProcessor constructor body runs second'],
                ['In chain A → B → C', 'A executes first, then B, then C — top-down'],
            ],
        ),
        'Yes, abstract classes can have parameterized constructors. They are typically marked protected since the class cannot be instantiated directly. Derived classes call the base constructor using : base(args) in their constructor declaration — this runs the base constructor before the derived constructor body. If the abstract class has only a parameterized constructor and no default, all derived classes must provide the base() call explicitly or the code will not compile. Constructors run top-down in an inheritance chain: for A → B → C, C\'s constructor is called, then :base() invokes B, which invokes A — A\'s body executes first, then B\'s, then C\'s. This guarantees base class invariants are established before the derived class can use them. Common mistake: adding a parameterized constructor to an abstract base without keeping a default constructor breaks all existing derived classes until they add : base(...).',
        'Abstract class constructor = the foundation of a building. You can\'t live in the foundation (can\'t instantiate), but every floor (derived class) must be built on top of it first (:base() runs first).',
    ),
    'oops-032': build_answer(
        'Yes, a class can implement two interfaces with the same method name. If signatures match and behavior should be the same, one method body satisfies both. If behavior should differ, use explicit interface implementation — prefix the method with the interface name. Explicit methods are only accessible through the interface reference — like a disguise visible only through the interface lens.',
        [
            ['One public method can satisfy multiple interfaces', 'UnifiedLogger.Log() fulfills both IPaymentLogger and IAuditLogger'],
            ['Explicit implementation resolves naming conflicts', 'IUpiProcessor.ProcessAsync vs INeftProcessor.ProcessAsync with different logic'],
            ['Keeps class public API clean', 'Interface methods hidden from concrete type when not part of natural API'],
            ['Enables different behavior per interface', 'UPI instant transfer vs NEFT batch transfer on same processor class'],
            ['Default interface methods (C# 8+) evolve interfaces safely', 'Add new methods without breaking all implementing classes'],
        ],
        'HybridPaymentProcessor implements both IUpiProcessor and INeftProcessor. UPI has instant transfer with Rs.1 lakh limit; NEFT is batch with no upper limit. Explicit implementation keeps them separate — the payment router casts to the correct interface based on the payment rail.',
        '// Case 1: Same signature, same behavior — one method satisfies both\ninterface IPaymentLogger  { void Log(string message); }\ninterface IAuditLogger    { void Log(string message); }\n\npublic class UnifiedLogger : IPaymentLogger, IAuditLogger\n{\n    public void Log(string message) => Console.WriteLine($"[LOG] {message}");\n}\n\nvar logger = new UnifiedLogger();\nlogger.Log("Test");                    // public method\n((IPaymentLogger)logger).Log("Test"); // same\n\n// Case 2: Different behavior — explicit implementation\ninterface IUpiProcessor  { Task&lt;bool&gt; ProcessAsync(decimal amount); }\ninterface INeftProcessor { Task&lt;bool&gt; ProcessAsync(decimal amount); }\n\npublic class HybridPaymentProcessor : IUpiProcessor, INeftProcessor\n{\n    async Task&lt;bool&gt; IUpiProcessor.ProcessAsync(decimal amount)\n    {\n        Console.WriteLine($"UPI: instant transfer of {amount}");\n        return amount &lt;= 100000m;\n    }\n\n    async Task&lt;bool&gt; INeftProcessor.ProcessAsync(decimal amount)\n    {\n        Console.WriteLine($"NEFT: batch transfer of {amount}");\n        return amount &gt;= 1m;\n    }\n}\n\nHybridPaymentProcessor p = new();\n// p.ProcessAsync(1000m);  // COMPILE ERROR\nawait ((IUpiProcessor)p).ProcessAsync(1000m);  // Expected: UPI: instant transfer of 1000',
        table(
            ['Implementation', 'Accessible on Class Type', 'Accessible via Interface'],
            [
                ['Implicit (public)', 'Yes', 'Yes'],
                ['Explicit (InterfaceName.Method)', 'No', 'Yes'],
            ],
        ),
        'Yes. If both interfaces have the same method signature and the behavior should be the same, one public method satisfies both — the compiler routes both interface calls to it. If the behavior should differ, use explicit interface implementation: async Task&lt;bool&gt; IUpiProcessor.ProcessAsync() and async Task&lt;bool&gt; INeftProcessor.ProcessAsync() — each prefixed with the interface name. Explicitly implemented methods are hidden on the concrete class and only accessible via the interface reference. You cannot mark explicitly implemented methods as public or virtual. Since C# 8, interfaces can have default method implementations — adding new methods without breaking implementers, but default methods are only accessible through the interface reference. I use explicit implementation to resolve naming conflicts and hide interface members not part of the class\'s natural public API.',
        'Explicit interface implementation = a disguise. Look at the class directly — the method is hidden. Look through the interface lens — you see it.',
    ),
    'oops-033': build_answer(
        'Array is a fixed-size, strongly-typed collection — size is set at creation and cannot change. ArrayList is a legacy dynamic collection storing object — not type-safe, requires casting, and boxes value types. List&lt;T&gt; is the modern generic dynamic collection — type-safe, no boxing, no casting. Array = fixed parking lot; ArrayList = mixed parking chaos; List&lt;T&gt; = type-safe expandable lot.',
        [
            ['Array: fixed size, zero-copy with Span&lt;T&gt;', '4-byte transaction header as byte[] for zero-copy parsing'],
            ['List&lt;T&gt;: dynamic, type-safe, LINQ-friendly', 'Build Transaction collection as payments arrive — no casting'],
            ['List&lt;T&gt; eliminates boxing for value types', 'Millions of decimal amounts stored without heap allocation'],
            ['Array best for known fixed size and interop', 'dailyTotals[31] for one entry per day of month'],
            ['Pre-allocate List capacity when size is approximate', 'new List&lt;Transaction&gt;(1000) avoids internal resizing'],
        ],
        'Transaction processing uses List&lt;Transaction&gt; — dynamic, type-safe, LINQ-friendly. The 4-byte transaction header is byte[] — fixed size, works with Span&lt;byte&gt; for zero-copy parsing. Legacy bank middleware might use ArrayList — cast immediately and never pass it further into modern code.',
        '// Array: fixed size, typed\nstring[] paymentMethods = new string[4] { "UPI", "NEFT", "IMPS", "Card" };\ndecimal[] dailyTotals = new decimal[31];\n// paymentMethods[4] = "RTGS"; // IndexOutOfRangeException\n\n// ArrayList: dynamic, stores object — avoid in new code\nvar legacyCollection = new System.Collections.ArrayList();\nlegacyCollection.Add(5000m);      // decimal BOXED!\nlegacyCollection.Add("UPI-REF");  // mixed types allowed\ndecimal amount = (decimal)legacyCollection[0]; // cast required\n\n// List&lt;T&gt;: dynamic, typed — use this always\nvar transactions = new List&lt;Transaction&gt;();\ntransactions.Add(new Transaction { Id = 1, Amount = 5000m });\nTransaction t = transactions[0]; // no cast needed\n\n// When Array IS better: Span operations\nbyte[] headerBytes = new byte[4];\nReadOnlySpan&lt;byte&gt; span = headerBytes.AsSpan();\n\nvar results = new List&lt;Transaction&gt;(capacity: 1000);\nConsole.WriteLine($"Methods: {paymentMethods.Length}, Txns: {transactions.Count}");\n// Expected: Methods: 4, Txns: 1\n\npublic class Transaction { public int Id { get; init; } public decimal Amount { get; init; } }',
        table(
            ['Feature', 'Array', 'ArrayList', 'List&lt;T&gt;'],
            [
                ['Size', 'Fixed', 'Dynamic', 'Dynamic'],
                ['Type safety', 'Yes', 'No', 'Yes'],
                ['Boxing', 'No', 'Yes', 'No'],
                ['Use in new code', 'When size is fixed', 'Never', 'Default choice'],
            ],
        ),
        'Array is fixed-size and strongly typed — use it when the size is known upfront and doesn\'t change, or when working with Span&lt;T&gt; for zero-copy buffer operations, interop, or multidimensional data. ArrayList is a legacy type from .NET 1.x — it stores object, requires casting, and boxes value types. It should never appear in modern C# code. List&lt;T&gt; is the correct replacement: dynamic sizing, type-safe, no boxing, full LINQ support. Prefer arrays when size is fixed and known, you need maximum performance in hot paths, working with interop/unsafe code, multidimensional data, or Spans and Memory&lt;T&gt;. In most application-level code, List&lt;T&gt; is simpler and the performance difference is negligible.',
        'Array = parking lot with fixed spaces. ArrayList = lot accepting cars, trucks, and bicycles mixed (object) — chaos. List&lt;T&gt; = lot that only accepts cars (type-safe) and can add more spaces as needed.',
    ),
    'oops-034': build_answer(
        'virtual + override enables true runtime polymorphism — calling through a base reference dispatches to the derived implementation via the vtable. The new keyword hides the base method — when called through a base reference, the BASE method runs. override = "I am the new version"; new = "same name, completely separate thing."',
        [
            ['virtual/override: true polymorphism via vtable', 'PaymentProcessor[] calls each gateway\'s GetGatewayName correctly'],
            ['override follows open/closed principle', 'Add new processor without changing routing engine code'],
            ['new documents intentional method hiding', 'Explicit new silences compiler warning about hiding inherited member'],
            ['Understanding difference prevents subtle routing bugs', 'UpiProcessor with new returns "Base" through base reference — wrong gateway!'],
            ['Compiler warns when hiding without new keyword', 'Same behavior as new but signals possible unintentional hiding'],
        ],
        'A payment routing engine holds List&lt;PaymentProcessor&gt; and calls GetGatewayName() on each. With override, polymorphism works — each processor returns its own name. If UpiProcessor uses new instead of override, calling through the base reference returns "Base" — the routing engine never sees "UPI".',
        '// virtual + override: TRUE polymorphism\npublic class PaymentProcessor\n{\n    public virtual string GetGatewayName() => "Base";\n}\n\npublic class RazorpayProcessor : PaymentProcessor\n{\n    public override string GetGatewayName() => "Razorpay";\n}\n\nPaymentProcessor p1 = new RazorpayProcessor();\nConsole.WriteLine(p1.GetGatewayName()); // Expected: Razorpay\n\n// new keyword: METHOD HIDING\npublic class UpiProcessor : PaymentProcessor\n{\n    public new string GetGatewayName() => "UPI"; // HIDES base method\n}\n\nUpiProcessor u1 = new UpiProcessor();\nConsole.WriteLine(u1.GetGatewayName()); // Expected: UPI\n\nPaymentProcessor u2 = new UpiProcessor();\nConsole.WriteLine(u2.GetGatewayName()); // Expected: Base — SURPRISE!\n\nPaymentProcessor[] gateways = { new RazorpayProcessor(), new UpiProcessor() };\nforeach (var g in gateways)\n    Console.WriteLine(g.GetGatewayName());\n// Expected output:\n// Razorpay\n// Base',
        table(
            ['Keyword', 'Accessed via Derived Ref', 'Accessed via Base Ref'],
            [
                ['override', 'Derived method', 'Derived method (vtable)'],
                ['new', 'Derived method', 'BASE method (hiding!)'],
            ],
        ),
        'virtual marks a base class method as overridable. override in the derived class replaces it — virtual dispatch ensures that even when the object is accessed through a base reference, the derived implementation runs. This is runtime polymorphism. The new keyword hides the base method — when accessed through a base reference, the base method runs. This is method hiding, not polymorphism. The classic interview test: Animal a = new Dog(); a.Speak() — if Speak is override, Dog\'s version runs; if Speak is new, Animal\'s version runs. If you define a method without override or new, C# compiles but warns that the inherited member is hidden — behavior is the same as new. Rule: always use override for polymorphism. Use new only when intentionally breaking the virtual dispatch chain.',
        'override = "I am the new version of what was there before" (vtable updated, polymorphism works). new = "I am a completely separate thing that happens to have the same name" (no vtable entry, base reference ignores you).',
    ),
    'oops-035': build_answer(
        'Extension methods add new methods to existing types without modifying the original source — even sealed classes and third-party types. They are static methods in a static class with the first parameter prefixed by this. Think of them as Post-it notes with new instructions on something you don\'t own.',
        [
            ['Adds methods to sealed and third-party types', 'decimal.WithGst() and string.IsValidUpiId() without modifying built-in types'],
            ['Discovered by IntelliSense like instance methods', 'Domain helpers appear everywhere the type is used'],
            ['LINQ built entirely on extension methods', 'Where, Select, OrderBy are extensions on IEnumerable&lt;T&gt;'],
            ['Can be called on null without NullReferenceException', 'Static dispatch — extension handles null internally'],
            ['Composable with LINQ for readable queries', 'AboveThreshold().OrderByDescending().ToList() reads naturally'],
        ],
        'decimal.WithGst() and decimal.ToRupees() are used across the payment platform — in controllers formatting API responses, in services calculating fees, in view models displaying amounts. LINQ chain combines built-in extensions with custom ones like AboveThreshold and TotalAmount.',
        'public static class PaymentExtensions\n{\n    public static string ToRupees(this decimal amount)\n        => $"\\u20b9{amount:N2}";\n\n    public static decimal WithGst(this decimal amount, decimal gstRate = 0.18m)\n        => Math.Round(amount * (1 + gstRate), 2);\n\n    public static bool IsValidUpiId(this string? upiId)\n        => !string.IsNullOrWhiteSpace(upiId) && upiId.Contains(\'@\');\n\n    public static decimal TotalAmount(this IEnumerable&lt;Transaction&gt; transactions)\n        => transactions.Sum(t => t.Amount);\n\n    public static IEnumerable&lt;Transaction&gt; AboveThreshold(\n        this IEnumerable&lt;Transaction&gt; transactions, decimal threshold)\n        => transactions.Where(t => t.Amount &gt; threshold);\n}\n\ndecimal fee = 1000m.WithGst();\nstring display = fee.ToRupees();               // Expected: ₹1,180.00\nbool valid = "darshan@okicici".IsValidUpiId(); // Expected: true\nbool nullCheck = ((string?)null).IsValidUpiId(); // Expected: false, no NullRef\n\nvar large = transactions.AboveThreshold(50000m).OrderByDescending(t => t.Amount).ToList();\ndecimal total = transactions.TotalAmount();\n\npublic record Transaction(int Id, decimal Amount);',
        table(
            ['Feature', 'Instance Method', 'Extension Method'],
            [
                ['Modifies type source', 'Yes', 'No'],
                ['Access private members', 'Yes', 'No'],
                ['Works on sealed types', 'N/A', 'Yes'],
                ['Called on null', 'NullReferenceException', 'Works if method handles null'],
            ],
        ),
        'Extension methods add methods to existing types without modifying them. They are static methods in a static class with the first parameter prefixed by this — the this parameter is the type being extended. After importing the namespace, they appear as instance methods in IntelliSense. LINQ is the most prominent example — Where, Select, OrderBy are all extension methods on IEnumerable&lt;T&gt;. When you write list.Where(x => x.Active), the compiler translates it to Enumerable.Where(list, x => x.Active). I use extension methods for domain-specific helpers: decimal.WithGst(), string.IsValidUpiId(), IEnumerable&lt;Transaction&gt;.TotalAmount(). Because they are static calls, they can be invoked on null without NullReferenceException as long as the method handles null. Limitations: cannot access private members, instance methods take priority over extensions with the same signature.',
        'Extension method = sticking a Post-it note with new instructions on something you don\'t own. The original stays unchanged; you just gave it a new capability.',
    ),
    'oops-036': build_answer(
        'CTS (Common Type System) defines all data types and programming constructs the CLR supports and the rules for how they interact. CLS (Common Language Specification) is the subset of CTS that every .NET language must support for cross-language interoperability. CTS = full restaurant menu; CLS = items every chain restaurant must serve.',
        [
            ['CTS ensures type consistency across all .NET languages', 'C# int and VB.NET Integer are both System.Int32 at runtime'],
            ['CLS compliance makes public libraries consumable from any language', 'Payment SDK works from C#, VB.NET, and F# without conversion issues'],
            ['[CLSCompliant(true)] warns on public API violations', 'Compiler flags uint and ulong in public methods of NuGet packages'],
            ['Enables cross-language interop in same solution', 'C# and F# assemblies reference each other seamlessly'],
            ['Value and reference type rules defined by CTS', 'Explains stack vs heap allocation and copy semantics'],
        ],
        'A payment SDK published as a NuGet package should be marked [CLSCompliant(true)]. The compiler warns if public methods use uint (transaction count) or ulong — ensuring banks using VB.NET legacy systems or F# pipelines can consume the SDK without type conversion issues.',
        '// CTS: C# int and VB.NET Integer are the same CTS type\nint x = 42;\nSystem.Int32 y = 42;\nConsole.WriteLine(x.GetType().FullName); // System.Int32\n\n[assembly: CLSCompliant(true)]\n\nnamespace PaymentPlatform.PublicApi\n{\n    public class TransactionService\n    {\n        // COMPLIANT: int, long, string, decimal are in CLS\n        public decimal GetBalance(long accountId) => 50000m;\n\n        // NOT CLS-compliant: uint not in CLS — VB.NET has no equivalent\n        // public uint GetTransactionCount() => 42; // Warning\n\n        // FIX: use long instead\n        public long GetTransactionCount() => 42L;\n    }\n}\n\n// CTS type categories\nint number = 42;                // value type\nstring text = "hello";          // reference type (special)\nDateTime date = DateTime.UtcNow; // value type (struct)\n\nConsole.WriteLine($"Balance: {new TransactionService().GetBalance(1):C}");\n// Expected: Balance: ₹50,000.00',
        table(
            ['Concept', 'Scope', 'Purpose'],
            [
                ['CTS', 'Full CLR type system', 'Defines all types, value/reference rules, inheritance'],
                ['CLS', 'Subset of CTS', 'Cross-language compatibility minimum for public APIs'],
            ],
        ),
        'CTS is the type system defined by the CLR — it specifies all types (value types: int, struct, enum; reference types: class, interface, delegate) and the rules for type safety and inheritance. CTS is why C# int and VB.NET Integer are the same type at runtime — both are System.Int32. At the memory level, CTS value types are allocated on the stack and copied on assignment; reference types are allocated on the heap and variables hold references to the same object. CLS is a subset of CTS representing the minimum feature set every .NET language must support for cross-language interoperability. CLS excludes types like uint, ulong, and sbyte because not all .NET languages have equivalents. Mark a public library [CLSCompliant(true)] to get compiler warnings when public members use non-CLS types. CTS = the full type system the runtime defines. CLS = the safe subset every language understands.',
        'CTS = the full menu at a restaurant (all food available). CLS = items every restaurant in the chain must serve (the common minimum). Serve only from the CLS menu and any .NET language customer can eat.',
    ),
}


def main():
    with SOURCE.open(encoding='utf-8') as f:
        data = json.load(f)

    ids = {f'oops-{i:03d}' for i in range(25, 37)}
    questions = []
    for q in data['questions']:
        if q['id'] in ids:
            updated = dict(q)
            updated['answer'] = ANSWERS[q['id']]
            questions.append(updated)

    questions.sort(key=lambda q: q['sortOrder'])
    assert len(questions) == 12, f'Expected 12 questions, got {len(questions)}'

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f'Wrote {len(questions)} questions to {OUTPUT}')


if __name__ == '__main__':
    main()
