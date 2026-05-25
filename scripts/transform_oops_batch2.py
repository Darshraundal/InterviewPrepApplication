"""Transform oops-013..024 answers to new 6-section emoji format."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src/InterviewPrepPortal/Data/JsonData/questions-oops.json"
OUT = ROOT / "src/InterviewPrepPortal/Data/JsonData/oops_batch2.json"

# User-specified metadata overrides (followUps, tips)
OVERRIDES = {
    "oops-013": {
        "followUps": [
            {
                "question": "What is the difference between Dispose and Finalize?",
                "answer": "<p><strong>Dispose</strong> is deterministic — called explicitly by the developer via <code>using</code> or direct call. Releases resources immediately. <strong>Finalize</strong> is non-deterministic — called by the GC at an unknown time as a safety net. The standard pattern implements both: <code>Dispose()</code> releases resources and calls <code>GC.SuppressFinalize(this)</code>; the finalizer calls <code>Dispose(false)</code> as a backstop.</p>",
            },
            {
                "question": "What does GC.SuppressFinalize do?",
                "answer": '<p><code>GC.SuppressFinalize(this)</code> tells the GC: "Don\'t call the finalizer on this object." When an object has a finalizer, the GC places it in the finalization queue before collecting it. If you\'ve already released resources in <code>Dispose()</code>, the finalizer is unnecessary. Calling <code>GC.SuppressFinalize(this)</code> in <code>Dispose()</code> removes the object from the finalization queue — it can be collected immediately.</p>',
            },
            {
                "question": "What is IAsyncDisposable?",
                "answer": "<p><code>IAsyncDisposable</code> (C# 8+) allows async cleanup. Implement <code>ValueTask DisposeAsync()</code>. Use with <code>await using</code>. EF Core's <code>DbContext</code> implements both <code>IDisposable</code> and <code>IAsyncDisposable</code>.</p>",
            },
        ],
        "tip": "<strong>In ASP.NET Core DI, registered services are automatically disposed</strong> at the end of the request (Scoped) or app shutdown (Singleton). You still need <code>using</code> for objects created manually.",
    },
    "oops-014": {
        "followUps": [
            {
                "question": "What is string interning?",
                "answer": "<p><strong>String interning</strong> is an optimization where the CLR maintains a pool of unique string literals. At compile time, identical string literals share the same memory object. You can manually intern: <code>string interned = string.Intern(dynamicString)</code>. Don't over-use — interned strings are never GC'd.</p>",
            },
            {
                "question": "What is Span<char> for string operations?",
                "answer": "<p><code>Span&lt;char&gt;</code> and <code>ReadOnlySpan&lt;char&gt;</code> allow zero-allocation string slicing — you get a view into an existing string without copying characters. APIs like <code>int.Parse(ReadOnlySpan&lt;char&gt;)</code> work directly on spans, avoiding the intermediate string allocation.</p>",
            },
        ],
        "tip": "<strong>string.Join is often faster than StringBuilder for collections:</strong> <code>string.Join(\", \", items)</code> is cleaner and optimized. Use StringBuilder when you're building a string step-by-step with conditional logic.",
    },
    "oops-015": {
        "followUps": [
            {
                "question": "Does sealing a class improve performance?",
                "answer": "<p>Yes, marginally. When the JIT knows a class is sealed, it can <em>devirtualize</em> virtual method calls — instead of an indirect dispatch through the vtable, it can call the method directly (or inline it). The performance difference is measurable in microbenchmarks but negligible for most application code.</p>",
            },
            {
                "question": "Why is string sealed in .NET?",
                "answer": "<p><code>string</code> is sealed primarily for <strong>security and correctness</strong>. If <code>string</code> were extensible, an attacker could create a subclass that overrides <code>GetHashCode()</code> — breaking all Dictionary and HashSet lookups. Many framework types are sealed for the same reason.</p>",
            },
        ],
        "tip": "<strong>String is sealed for safety:</strong> If string were extensible, an attacker could create a malicious subclass with a modified <code>GetHashCode()</code> or <code>Equals()</code> — breaking Dictionary lookups and security checks.",
    },
    "oops-016": {
        "followUps": [
            {
                "question": "What is AggregateException?",
                "answer": "<p><code>AggregateException</code> wraps one or more exceptions from parallel or async operations. It's thrown by <code>Task.Wait()</code> and <code>Task.WhenAll()</code>. When awaiting with <code>await</code>, the first inner exception is unwrapped automatically.</p>",
            },
            {
                "question": "What is custom exception creation?",
                "answer": "<p>Create custom exceptions by inheriting from <code>Exception</code>. Include three standard constructors: parameterless, message-only, and message+inner. Add domain-specific properties. Custom exceptions make catch blocks precise and carry domain context.</p>",
            },
            {
                "question": "What is exception filter?",
                "answer": "<p>An <strong>exception filter</strong> is a <code>when</code> clause on a catch block: <code>catch (SqlException ex) when (ex.Number == 1205)</code>. Evaluated <em>before</em> the stack unwinds — if false, the exception continues propagating. This preserves the full stack trace for diagnostics.</p>",
            },
        ],
        "tip": "<strong>Always use <code>throw</code> not <code>throw ex</code></strong> when rethrowing. The stack trace is your most valuable debugging tool in production.",
    },
    "oops-017": {
        "followUps": [
            {
                "question": "What is the difference between Func and Action?",
                "answer": "<p><strong><code>Action</code></strong> is a delegate for a method that returns <code>void</code>. <strong><code>Func</code></strong> is a delegate for a method that returns a value — the last type parameter is always the return type: <code>Func&lt;string, int&gt;</code> (takes string, returns int). <strong><code>Predicate&lt;T&gt;</code></strong> is equivalent to <code>Func&lt;T, bool&gt;</code>.</p>",
            },
            {
                "question": "What is a closure and what are the capture gotchas?",
                "answer": "<p>A <strong>closure</strong> captures variables from the enclosing scope — the lambda holds a reference to the variable, not a copy of its value. Classic gotcha: loop variable capture — all lambdas see the final value of the loop variable. Fix: copy to a local variable before capturing.</p>",
            },
        ],
        "tip": "<strong>Closure capture gotcha with loops:</strong> Capturing a loop variable in a lambda captures the variable, not its current value. By the time the lambda executes, the loop may have finished. Fix: <code>var captured = loopVar; var lambda = () =&gt; Use(captured);</code>",
    },
    "oops-018": {
        "followUps": [
            {
                "question": "What is the default access modifier for class members in C#?",
                "answer": "<p>For <strong>class members</strong>: the default is <code>private</code>. For <strong>top-level types</strong>: the default is <code>internal</code>. For <strong>members of an interface</strong>: the default is <code>public</code>. Always write access modifiers explicitly rather than relying on defaults.</p>",
            },
            {
                "question": "What is the InternalsVisibleTo attribute?",
                "answer": "<p><code>[InternalsVisibleTo(\"AssemblyName\")]</code> grants a specific external assembly access to <code>internal</code> members. Most common use: unit testing — production code stays internal, but the test project gets access. Add to AssemblyInfo.cs: <code>[assembly: InternalsVisibleTo(\"MyApp.Tests\")]</code>.</p>",
            },
        ],
        "tip": "<strong>Interview tip:</strong> Default for class members = <code>private</code>. Default for top-level types = <code>internal</code>. The most restrictive access modifier that still works is always preferred.",
    },
    "oops-019": {
        "followUps": [
            {
                "question": "Why does 0.1 + 0.2 not equal 0.3 in double?",
                "answer": "<p>Computers store <code>float</code> and <code>double</code> in <strong>binary floating-point</strong> (IEEE 754). Just as 1/3 cannot be represented exactly in decimal, many decimal fractions cannot be represented exactly in binary. <code>decimal</code> avoids this because it stores numbers in base-10, so 0.1, 0.2, and 0.3 are stored exactly. Always use <code>decimal</code> for money.</p>",
            },
            {
                "question": "What suffix do you use for decimal and float literals?",
                "answer": "<p><code>1.5f</code> = <code>float</code>. Without suffix, <code>1.5</code> = <code>double</code>. <code>1.5m</code> = <code>decimal</code>. Without the <code>m</code> suffix, assigning to a decimal variable causes compile error CS0664. Always write <code>decimal price = 19.99m;</code>.</p>",
            },
        ],
        "tip": "<strong>Rule:</strong> Money and financial calculations → always <code>decimal</code>. Scientific/physics calculations → <code>double</code>. GPU/graphics → <code>float</code>. Never mix <code>float</code>/<code>double</code> with <code>decimal</code> without explicit cast.",
    },
    "oops-020": {
        "followUps": [
            {
                "question": "What is AOT (Ahead-Of-Time) compilation and when would you use it?",
                "answer": "<p><strong>AOT</strong> compiles IL to native code at build time rather than at runtime. <strong>ReadyToRun (R2R)</strong> — partial AOT, reduces startup time. <strong>Native AOT</strong> — full native executable, sub-millisecond startup. Best for Lambda functions, CLI tools. Enable with <code>&lt;PublishAot&gt;true&lt;/PublishAot&gt;</code>.</p>",
            },
            {
                "question": "What is the CLR and what services does it provide?",
                "answer": "<p>The <strong>CLR</strong> provides: JIT compilation, Garbage Collection, type safety, exception handling, thread management, and interop (P/Invoke, COM). In .NET Core/.NET 5+, it is called <strong>CoreCLR</strong> and is open source.</p>",
            },
        ],
        "tip": "<strong>Interview flow:</strong> C# → IL (build time, Roslyn) → Native code (runtime, RyuJIT). JIT = first-call compilation, cached thereafter. Native AOT eliminates JIT entirely for scenarios needing instant startup.",
    },
    "oops-021": {
        "followUps": [
            {
                "question": "What is the difference between a static class and a singleton?",
                "answer": "<p>A <strong>static class</strong> has no instance, all methods called on the type itself. Cannot implement interfaces, cannot be mocked. A <strong>Singleton</strong> (DI) is a regular class with a single instance. Can implement interfaces and be substituted/mocked in tests. Use static class for pure functions; use Singleton via DI for services needing interfaces.</p>",
            },
            {
                "question": "What are extension methods and what makes them special about static classes?",
                "answer": "<p>Extension methods let you add methods to existing types without modifying them. They must be <code>static</code> methods in a <code>static</code> class, with the first parameter prefixed by <code>this</code>. LINQ is built entirely on extension methods on <code>IEnumerable&lt;T&gt;</code>.</p>",
            },
        ],
        "tip": "<strong>When to use static:</strong> Utility methods (no state, no side effects), extension methods, constants. <strong>When NOT to use static:</strong> Services that need DI, anything you'd want to mock in tests, anything with mutable shared state.",
    },
    "oops-022": {
        "followUps": [
            {
                "question": "What is the difference between a nested class and an inner class?",
                "answer": "<p>In C#, all classes defined inside another class are called <strong>nested classes</strong>. Unlike Java inner classes, C# nested classes do NOT have an implicit reference to an outer class instance — they are independent. A C# nested class must receive the outer instance explicitly if it needs it.</p>",
            },
            {
                "question": "When is a nested class better than a separate class?",
                "answer": "<p>Use a nested class when: (1) It's an implementation detail only the outer class needs. (2) Strong coupling is intentional (LinkedList.Node). (3) Builder/Factory patterns where tight association communicates the API design (MyClass.Builder). Don't use nested classes just to reduce file count.</p>",
            },
        ],
        "tip": "<strong>Most common real-world uses:</strong> Private helper/state types that only make sense in context of the outer class. Builder pattern where <code>MyClass.Builder</code> makes the association obvious.",
    },
    "oops-023": {
        "followUps": [
            {
                "question": "When should you use LinkedList<T> instead of List<T>?",
                "answer": "<p>Use <code>LinkedList&lt;T&gt;</code> when you frequently <strong>insert or remove from the middle</strong> AND you have a reference to the node — these are O(1) operations. Trade-off: no random access by index (O(n) traversal), more memory per node (previous + next pointers), cache-unfriendly. In practice, <code>List&lt;T&gt;</code> outperforms for most real-world scenarios.</p>",
            },
            {
                "question": "What is the difference between List<T>, IList<T>, IEnumerable<T>, and ICollection<T>?",
                "answer": "<p>Interface hierarchy: <code>IEnumerable&lt;T&gt;</code> (forward-only iteration) → <code>ICollection&lt;T&gt;</code> (adds Count, Add, Remove) → <code>IList&lt;T&gt;</code> (adds index access) → <code>List&lt;T&gt;</code> (concrete, Sort, BinarySearch). Rule: accept the most restrictive interface your method needs — take <code>IEnumerable&lt;T&gt;</code> if you only iterate.</p>",
            },
        ],
        "tip": "<strong>Rule:</strong> Always use <code>Add()</code> when building a list. Only use <code>Insert()</code> when position within the list truly matters — remember it's O(n). Pre-allocate with <code>new List&lt;T&gt;(capacity)</code> when you know the approximate size.",
    },
    "oops-024": {
        "followUps": [
            {
                "question": "What is MSIL / CIL and how does the CLR execute it?",
                "answer": "<p>When you compile C# code, Roslyn produces <strong>MSIL (Microsoft Intermediate Language)</strong> / <strong>CIL (Common Intermediate Language)</strong> — CPU-independent bytecode stored in a .dll. At runtime, the CLR's JIT compiler translates MSIL to native machine code on the fly the first time each method is called, then caches the result.</p>",
            },
            {
                "question": "What are the benefits of managed code over unmanaged code?",
                "answer": "<p>Benefits: Automatic memory management (GC), type safety (CLR verifies types), structured exception handling, cross-language interoperability (C# and F# interop via same CIL). Choose unmanaged for game engines, device drivers, or legacy COM/Win32 integration.</p>",
            },
        ],
        "tip": "<strong>Interviewer shortcut:</strong> 'Managed = CLR controls memory; Unmanaged = you control memory'. The CLR's garbage collector is the defining difference.",
        "tags": ["clr", "managed", "unmanaged", "pinvoke", "gc"],
    },
}

# Custom analogies appended to simple definitions
ANALOGIES = {
    "oops-013": " Like returning a rented locker key the moment you are done, instead of waiting for the building manager to find it later.",
    "oops-014": " Think of string as a whiteboard you erase and redraw every time; StringBuilder is a notepad where you keep appending.",
    "oops-015": " Like sealing a bank vault door — no one can extend or override the security mechanism.",
    "oops-016": " Like a bank's error-handling protocol — catch the problem, log it, but never destroy the paper trail of where it started.",
    "oops-017": " Like sticky notes with instructions you hand to a payment processor: \"do this when you need me.\"",
    "oops-018": " Like bank security levels — public lobby, internal staff-only areas, and private vault rooms.",
    "oops-019": " Like choosing the right scale: decimal is a precise jeweler's scale for rupees; double is a lab scale for physics.",
    "oops-020": " Like a translator who writes down the translation the first time you speak, then reads from notes instantly afterward.",
    "oops-021": " Like a toolbox mounted on the wall — you don't carry it around, you just walk up and use the tools.",
    "oops-022": " Like a locked room inside a house — only the house owner knows about a private nested helper.",
    "oops-023": " Add() is joining the back of a queue instantly; Insert() is cutting in front and making everyone shuffle back.",
    "oops-024": " Managed code is flying with a safety net (CLR/GC); unmanaged code is walking a tightrope without one.",
}

# Advantage mapping: old li text -> (advantage, why it matters) when pattern doesn't fit auto-convert
ADVANTAGE_WHY = {
    "Resources freed immediately — not waiting for GC": ("Deterministic cleanup", "Resources freed immediately — not waiting for GC"),
    "using statement ensures cleanup even on exceptions": ("using statement", "Guarantees Dispose() even when exceptions occur"),
    "Prevents connection pool exhaustion and file lock issues": ("Prevents resource leaks", "Avoids connection pool exhaustion and file lock issues"),
    "ASP.NET Core DI auto-disposes scoped services at request end": ("ASP.NET Core DI integration", "Scoped services auto-disposed at request end"),
}


def extract_section(answer: str, num: int, title: str) -> str:
    pattern = rf"<h4>{num}\.\s*{re.escape(title)}</h4>(.*?)(?=<h4>\d+\.|$)"
    m = re.search(pattern, answer, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def ul_to_advantage_table(ul_html: str) -> str:
    items = re.findall(r"<li>(.*?)</li>", ul_html, re.DOTALL)
    rows = []
    for item in items:
        text = re.sub(r"\s+", " ", item.strip())
        adv, why = None, None
        if " — " in text:
            adv, why = text.split(" — ", 1)
        elif ": " in text:
            left, right = text.split(": ", 1)
            if len(left) <= 55:
                adv, why = left, right
        if adv is None:
            lowered = text.lower()
            for sep in (" ensures ", " prevents ", " enables ", " allows ", " avoids ", " provides "):
                idx = lowered.find(sep)
                if idx > 0:
                    adv = text[:idx].strip()
                    why = text[idx + len(sep) :].strip().capitalize()
                    break
        if adv is None:
            adv, why = text, "Improves reliability and maintainability in production fintech systems"
        rows.append(
            f'<tr><td style="border:1px solid #555;padding:4px;">{adv.strip()}</td>'
            f'<td style="border:1px solid #555;padding:4px;">{why.strip()}</td></tr>'
        )
    header = (
        '<table style="width:100%;font-size:.85rem;border-collapse:collapse;">'
        '<tr><th style="border:1px solid #555;padding:4px;">Advantage</th>'
        '<th style="border:1px solid #555;padding:4px;">Why It Matters</th></tr>'
    )
    return header + "".join(rows) + "</table>"


def strip_p(html: str) -> str:
    return re.sub(r"</?p>", "", html).strip()


def extract_diff_table(old: str) -> str:
    m = re.search(
        r"<h4>7\.\s*Difference Table.*?</h4>(.*?)(?=<h4>8\.|$)",
        old,
        re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else ""


def transform_answer(qid: str, old: str) -> str:
    definition = strip_p(extract_section(old, 1, "Simple Definition"))
    advantages_ul = extract_section(old, 3, "Advantages")
    code_section = extract_section(old, 4, "Small C# Example")
    fintech = strip_p(extract_section(old, 5, "Real-Time Fintech Example"))
    diff_table = extract_diff_table(old)
    best = strip_p(extract_section(old, 8, "Best Interview Answer"))
    trick = strip_p(extract_section(old, 9, "Easy Trick to Remember"))

    # Build simple definition with analogy (keep concise — 1-2 lines)
    analogy = ANALOGIES.get(qid, "")
    simple = definition.rstrip(".")
    if analogy and analogy.strip() not in simple:
        simple = f"{simple}.{analogy}"
    else:
        simple = definition

    # Extract code block
    code_match = re.search(r"(<pre><code class=\"language-csharp\">.*?</code></pre>)", code_section, re.DOTALL)
    code_block = code_match.group(1) if code_match else code_section
    if "// Output:" not in code_block and "Output:" not in code_block:
        code_block = code_block.replace("</code></pre>", "\n// Output: see comments above</code></pre>")

    adv_table = ul_to_advantage_table(advantages_ul)

    parts = [
        "<h4>📌 SIMPLE DEFINITION</h4>",
        f"<p>{simple}</p>",
        "<h4>✅ ADVANTAGES</h4>",
        adv_table,
        "<h4>🏦 FINTECH EXAMPLE (C#)</h4>",
        f"<p>{fintech}</p>",
        code_block,
    ]

    # Include difference table if meaningful content exists
    table_match = re.search(r"(<table style=\"width:100%;.*?</table>)", diff_table, re.DOTALL)
    if table_match:
        parts.extend(["<h4>📊 DIFFERENCE TABLE</h4>", table_match.group(1)])

    parts.extend(
        [
            "<h4>🎤 FINAL INTERVIEW ANSWER</h4>",
            f"<p>{best}</p>",
            "<h4>🧠 ONE LINE MEMORY TRICK</h4>",
            f"<p>{trick}</p>",
        ]
    )
    return "".join(parts)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    target_ids = {f"oops-{i:03d}" for i in range(13, 25)}
    result = []

    for q in data["questions"]:
        if q["id"] not in target_ids:
            continue
        item = dict(q)
        item["answer"] = transform_answer(q["id"], q["answer"])
        if q["id"] in OVERRIDES:
            item.update(OVERRIDES[q["id"]])
        result.append(item)

    result.sort(key=lambda x: x["sortOrder"])
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(result)} questions to {OUT}")


if __name__ == "__main__":
    main()
