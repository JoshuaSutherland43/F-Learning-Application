# -*- coding: utf-8 -*-
"""
Curriculum content, derived from the actual course material supplied by the user:
  - Slides/WHQV401 Lecture 01..08 (.pptx, current-year official slides)
  - Old Class Notes/WHQV401 Week 1..10 (.doc, same module under its earlier code
    WRHQ411 -- same lecturer's own notes, same progression, just an older cohort)
  - Class Tests 01 & 07, Homework Sets 1 & 7 (+ answers), Class Exercise, Timed
    Assignment (mcd Tree)
  - Old Exam Papers 2020/2022/2023/2024 (WHQV401)

Categories:
  core           - directly evidenced in the current lecture slides AND/OR recent
                   (2020-2024) exam papers. This is what the exam actually tests.
  legacy         - from the same module's own official notes (Weeks 9-10: OOP,
                   async workflows) but NOT present in any of the 4 exam papers
                   supplied, nor in the current Lecture 1-8 slide deck. Treated as
                   official-but-probably-not-examinable this year; flagged clearly
                   rather than silently included or silently dropped.
  supplementary  - general F# knowledge used to round out an explanation, sourced
                   from the purchased "Extra Modules" textbooks or general F#
                   knowledge, NOT tied to a specific lecture. Never presented as
                   something the lecturer taught.
"""

CATEGORIES = [
    {"id": "core", "label": "Official Curriculum", "color": "#3b82f6"},
    {"id": "legacy", "label": "Official but Not in Recent Exams", "color": "#a855f7"},
    {"id": "supplementary", "label": "Supplementary / Extra Modules", "color": "#f59e0b"},
]

# order = suggested study order (also roughly lecture order)
TOPIC_META = [
    {"id": "intro-fp", "title": "Functional Programming: Core Concepts", "category": "core", "order": 1,
     "summary": "Why F#, and the ideas that make functional programming different: immutability, referential transparency, purity, first-class functions.",
     "prereqs": []},
    {"id": "bindings-matching", "title": "Bindings, Functions & Pattern Matching", "category": "core", "order": 2,
     "summary": "let bindings, defining functions, match...with...when, if/elif/else.",
     "prereqs": ["intro-fp"]},
    {"id": "recursion-basics", "title": "Recursion Fundamentals", "category": "core", "order": 3,
     "summary": "The rec keyword, base cases, recursive cases, and why F# uses recursion instead of loops.",
     "prereqs": ["bindings-matching"]},
    {"id": "recursion-types", "title": "Types of Recursion (Forward / Backward / Tail)", "category": "core", "order": 4,
     "summary": "Forward vs backward recursion, linear vs tail recursion, and why it matters for performance.",
     "prereqs": ["recursion-basics"]},
    {"id": "lists-basics", "title": "Lists: Fundamentals", "category": "core", "order": 5,
     "summary": "The recursive definition of a list, :: and @, and pattern matching to take lists apart.",
     "prereqs": ["recursion-basics"]},
    {"id": "higher-order-currying", "title": "Higher-Order Functions, Currying & Pipelines", "category": "core", "order": 6,
     "summary": "Functions as values, currying, partial application, composition (>>/<<), the pipeline operator (|>), lambdas.",
     "prereqs": ["lists-basics"]},
    {"id": "tuples-records", "title": "Tuples, Records & Generics", "category": "core", "order": 7,
     "summary": "Grouping data: unnamed tuples vs named records, record update syntax, and generic type parameters.",
     "prereqs": ["bindings-matching"]},
    {"id": "lists-continued", "title": "Lists Continued: Ranges, Comprehensions & the List Module", "category": "core", "order": 8,
     "summary": "Range syntax, list comprehensions (for...do...yield), and List.map/filter/fold/reduce; sieve, quicksort, permutations.",
     "prereqs": ["lists-basics", "higher-order-currying"]},
    {"id": "induction", "title": "Structural Induction & Proofs", "category": "core", "order": 9,
     "summary": "Proving properties of recursive list functions correct using base case + inductive step, and the 10 list Laws.",
     "prereqs": ["lists-basics", "recursion-types"]},
    {"id": "lambda-calculus", "title": "Lambda Calculus", "category": "core", "order": 10,
     "summary": "Names, functions and applications; beta reduction; Church-encoded booleans and logic, exactly as used in every exam paper's Theory section.",
     "prereqs": ["bindings-matching"]},
    {"id": "discriminated-unions", "title": "Discriminated Unions", "category": "core", "order": 11,
     "summary": "Algebraic OR types: modelling mutually-exclusive alternatives, Option and Result.",
     "prereqs": ["tuples-records", "recursion-basics"]},
    {"id": "trees-structures", "title": "Trees & Custom Recursive Data Structures", "category": "core", "order": 12,
     "summary": "Binary search trees, tries, and custom linked lists built from discriminated unions -- the exam's favourite big practical question.",
     "prereqs": ["discriminated-unions", "recursion-types"]},
    {"id": "oop-fsharp", "title": "Object-Oriented Programming in F#", "category": "legacy", "order": 13,
     "summary": "Classes, inheritance, abstract classes and interfaces in F#. From the module's own Week 9 notes; not seen in any exam paper 2020-2024.",
     "prereqs": ["tuples-records"]},
    {"id": "async-workflows", "title": "Asynchronous Workflows & Parallelism", "category": "legacy", "order": 14,
     "summary": "async {...} workflows and Async.Parallel. From the module's own Week 10 notes; not seen in any exam paper 2020-2024.",
     "prereqs": ["higher-order-currying"]},
]

TOPICS = {t["id"]: t for t in TOPIC_META}


def curriculum_summary():
    return {"categories": CATEGORIES, "topics": TOPIC_META}


# ----------------------------------------------------------------------------
# Full per-topic content. Each entry has "levels" (markdown strings) using the
# 7 explanation levels from the spec (level 8, "Practice", is generated on
# demand by the question bank rather than stored as static content).
# ----------------------------------------------------------------------------

CONTENT = {}

CONTENT["intro-fp"] = {
    "levels": {
        "what_is_it": """
Functional programming (FP) is a different way of thinking about what a program *is*. In imperative
languages (Java, C, Python-as-usually-written) a program is a sequence of instructions that change
memory over time -- variables, loops, mutation. In FP, a program is built by combining **functions**
that transform values into other values, the way you'd write mathematics: `f(x) = x + 1`. There is
no "current state of the machine" to keep track of -- just values and the functions that produce them.

F# is a **functional-first** language: it strongly encourages the FP style (immutability, expressions,
recursion) but, being a .NET language, still lets you drop into an imperative or object-oriented style
when needed. Your lecturer's slides are explicit that in this module you should default to the
functional style and only reach for loops/mutation in special cases (populating arrays, file I/O).
""",
        "syntax": """
There's no single "syntax" for a paradigm, but the concepts below are expressed through specific F#
constructs you'll meet immediately:

- **`let`** -- binds a value to a name (not a variable assignment -- see "Common mistakes").
- **Basic types**: `int`, `float`, `bool`, `string`, `char`, and `unit` (written `()`), which is F#'s
  "nothing" value -- every function must return *something*, so a function that "does nothing" (e.g.
  just prints) returns `unit`.
- No semicolons at the end of lines. Indentation is significant, like Python.
""",
        "how_it_works": """
When you write `let x = 5`, F# doesn't allocate a mutable memory cell that can later hold something
else -- it binds the *name* `x` to the *value* `5`, permanently, for as long as `x` is in scope. This
gives you two of the core FP properties directly:

- **Immutability**: once bound, a value cannot change. There is no `x = x + 1` that mutates `x` --
  that would be a completely new binding that shadows the old one (and F# won't even let you do this
  with `let x = ...` twice in the same scope without the compiler treating it as a new, separate `x`).
- **Referential transparency**: because `x` can never change, every occurrence of `x` after its binding
  can be replaced by its value without changing what the program means. This is exactly how algebra
  works, and it's what makes formal reasoning (and later, induction proofs) possible at all.

**Purity** means a function's output depends *only* on its inputs -- no hidden reads of global mutable
state, no hidden writes (no "side effects" like mutating a file or a global variable). **First-class
functions** means a function is a value just like `5` or `"abc"` is a value: it can be bound to a name,
passed as an argument, returned from another function, or stored in a list. This is what makes
higher-order functions (Topic: Higher-Order Functions & Currying) possible at all.
""",
        "worked_example": """
```fsharp
let x = 5        // x is bound to 5, permanently
let y = x + 10   // y is bound to 15 (x's value substituted in)
// let x = x + 1   -- this does NOT mutate x; it creates a *new* shadowing binding
```
Line by line:
1. `let x = 5` -- the identifier `x` now refers to the value `5`. F# infers `x : int` from the literal.
2. `let y = x + 10` -- because `x` is referentially transparent, this means exactly the same thing as
   `let y = 5 + 10`. F# evaluates this to `15` and binds `y` to it.
3. The commented-out line would compile (as a *new* binding named `x` that shadows the old one within
   the rest of the scope) but it does **not** mean "increase x by one" the way it would in an imperative
   language -- the original `x` bound to `5` still exists underneath, just no longer visible by name.
""",
        "variations": """
- `let mutable x = 5` explicitly opts *out* of immutability for one identifier (needed for `for`/`while`
  loops with counters). The lecturer's guidance: avoid this in the module except in the specific
  imperative cases mentioned in class (loops that only populate/print/do I/O).
- Type annotations can be added explicitly, e.g. `let x : int = 5`, but are usually unnecessary because
  F#'s type inference figures it out. You'll need explicit annotations more often on function
  *parameters* when the type would otherwise be ambiguous.

**Supplementary (from the purchased Extra Modules, not part of the official course):** *Expert F# 4.0*
(Syme, Granicz & Cisternino) Chapter 3, "Introducing Functional Programming", and *Learning F#
Functional Data Structures and Algorithms* (Adnan) Chapter 1, "Embrace the Truth", both cover this same
immutability/referential-transparency ground with additional worked examples if you want a second
explanation of the same ideas in different words.
""",
        "exam_application": """
This topic is rarely tested directly with its own question, but it is the *reason* every other topic
works the way it does: every "prove using induction" question in the Theory section relies on
referential transparency (an expression can always be replaced by its value), and every practical
question expects a solution built from function composition and recursion rather than mutable loops --
using `for`/`while` with mutable accumulators where a recursive or higher-order solution was expected
is a good way to lose style/approach marks even if the output is correct.
""",
        "common_mistakes": """
- Thinking `let` is like `=` in Java/Python/C -- treating it as a mutable variable and expecting to
  "update" it later.
- Writing `let x = x + 1` and being confused why F# either errors ("Duplicate definition") in some
  contexts or silently shadows in others -- remember this creates a *new* binding, it never mutates.
- Reaching for `for`/`while` loops with mutable counters out of habit from other languages, when a
  recursive function is what's expected in this module.
- Forgetting that a function that "just prints" still needs to return `unit` (`()`), and that mismatched
  return types across branches of an `if` or `match` is a compile error, not a warning.
""",
    },
    "syntax_refs": ["let-binding", "basic-types", "unit-type"],
}

CONTENT["bindings-matching"] = {
    "levels": {
        "what_is_it": """
This topic covers the everyday building blocks you use in *every* F# program: binding names to values
and functions with `let`, choosing between alternatives with `match ... with`, and simple `if/elif/else`
expressions. Pattern matching is F#'s single most important control-flow tool -- far more powerful than
a `switch` statement, and used constantly for lists, tuples, records and discriminated unions alike.
""",
        "syntax": """
```fsharp
// A function has exactly ONE parameter (see "Common mistakes" for the "multi-parameter" illusion)
let square x = x * x

// match ... with ... when
match expression with
| pattern1 -> expression1
| pattern2 when <condition> -> expression2
| _ -> expressionDefault
```
Pattern options:
- a **literal** value, e.g. `1`, `true`, `"hello"` -- matches only that exact value.
- an **identifier**, e.g. `n` -- matches *anything*, and binds that value to the name `n` for use in the
  expression on the right of `->`.
- the **wildcard** `_` -- matches anything, binds nothing.
- a `when` **guard** -- an extra boolean condition attached to a pattern; the pattern only matches if
  both the pattern *and* the guard are true.

Every branch of a `match` (and of an `if/elif/else`) must produce a value of the *same type* -- F# will
not let you return an `int` from one branch and a `string` from another.
""",
        "how_it_works": """
`match n with | 1 -> ... | 2 -> ... | _ -> ...` is evaluated top to bottom: F# tries each pattern in
order against `n` and executes the expression to the right of the *first* one that matches. Because `_`
matches anything, it must go last -- patterns after a catch-all are unreachable (the compiler will warn
you).

A `when` guard is checked only *after* its pattern already matches -- so `| x when x >= 0 -> x` first
binds `x` to whatever value was matched, then checks `x >= 0` before committing to that branch; if the
guard fails, F# moves on to try the *next* pattern, it does not fall through into some default.

`if...then...elif...then...else` is not a statement -- it's an **expression** that evaluates to a value,
exactly like `match`. `if x < 5 then "a" else "b"` has type `string`, and can be used anywhere a value
is expected (bound with `let`, passed as an argument, etc).
""",
        "worked_example": """
```fsharp
// Absolute value, using match + when (Week 1 class notes)
let abs x =
    match x with
    | x when x >= 0 -> x
    | x -> -1 * x
```
1. `match x with` -- we're matching the parameter `x` against patterns.
2. `| x when x >= 0 -> x` -- the pattern `x` (an identifier) matches *any* value and (re)binds it to the
   name `x` (this shadows the outer `x`, but it's the same value). The guard `x >= 0` is then checked;
   if true, the branch's result is `x` itself.
3. `| x -> -1 * x` -- if the guard above was false, control falls through to this pattern (still matches
   anything), and returns `-1 * x`, flipping the sign.
4. Both branches return `int`, so the whole `match` expression has type `int`, and `abs` has type
   `int -> int`.
""",
        "variations": """
- Matching a `bool` directly is common: `match x > y with | true -> x | _ -> y` (this *is* valid F#, even
  though an `if` would usually read more naturally here).
- Multiple guards can be chained as separate `when` cases to partition a value fully, e.g. even/odd:
  `| n when n % 2 = 0 -> ... | n when n % 2 <> 0 -> ...`.
- `if` without `else` is only legal when the `then` branch has type `unit` (since the "implicit else"
  must also produce `unit`).
""",
        "exam_application": """
Pattern matching with `when` guards appears in almost every practical question that isn't purely about
lists (e.g. classifying values, handling special cases in tree/record questions). Examiners often expect
you to use a guard rather than nesting an `if` inside a `match` branch -- nesting works, but a clean
guard is the idiomatic, markable style the lecturer's own example solutions consistently use.
""",
        "common_mistakes": """
- Believing `match` works like a C-style `switch` that "falls through" without a `break` -- it doesn't;
  exactly one branch executes.
- Forgetting `_` must come last, or writing overlapping patterns where an earlier catch-all silently
  swallows a later, more specific case.
- Returning different types from different branches (e.g. `int` in one, `string` in another) -- this is
  a compile-time type error, not something you discover at runtime.
- Confusing `=` (equality *test*, used inside expressions/guards) with `<-` (mutation, only valid for
  `mutable` bindings) -- a very common source of confusion coming from other languages.
""",
    },
    "syntax_refs": ["match-expr", "if-else-expr", "let-binding", "wildcard-pattern"],
}

CONTENT["recursion-basics"] = {
    "levels": {
        "what_is_it": """
Recursion is how functional programs "loop": a function that calls itself, working on a smaller version
of the problem each time, until it reaches a case simple enough to answer directly (the **base case**).
F# does not encourage `for`/`while` loops with mutable counters in this module -- recursion is the
default looping mechanism, and it's used *everywhere*: processing lists, trees, numbers, anything with
a naturally recursive structure.
""",
        "syntax": """
```fsharp
let rec functionName parameters =
    match parameters with
    | <base case pattern> -> <base result>
    | <recursive case pattern> -> <expression involving functionName ...>
```
The **`rec`** keyword is mandatory whenever a function calls itself. Without it, the compiler doesn't
know the function's own name yet while it's being defined, and you'll get an "undefined value" error
inside the function body.
""",
        "how_it_works": """
F# functions aren't "known" to the rest of the program until their definition finishes -- so a function
that wants to refer to *itself*, inside its own body, needs the `rec` keyword to tell the compiler
"this name is allowed to appear in its own definition". Each call creates a new stack frame that
remembers where to return to; when a call hits the base case, it returns a concrete value, and each
waiting frame above it can then complete its own computation using that returned value, one level at a
time, back up to the original call.

A recursive function needs (at minimum):
1. One or more **base cases** -- patterns that stop the recursion and return a direct answer.
2. One or more **recursive cases** -- patterns that reduce the problem (e.g. `n-1`, or the tail of a
   list) and call the function again on that smaller problem.

Miss the base case, or fail to actually shrink the problem on each call, and you get infinite recursion
-- which in F# manifests as a `StackOverflowException` once the call stack is exhausted.
""",
        "worked_example": """
```fsharp
// Factorial, from Week 1 class notes
let rec factorial k =
    match k with
    | 1 -> 1
    | k -> k * factorial (k-1)
```
1. `let rec factorial k = ...` -- `rec` is required because `factorial` calls itself in its own body.
2. `| 1 -> 1` -- the base case: `factorial 1` is defined directly as `1`, with no further recursive call.
3. `| k -> k * factorial (k-1)` -- the recursive case: for any other `k`, the answer is `k` multiplied by
   the factorial of the smaller problem `k-1`.
4. Tracing `factorial 3`: `3 * factorial 2` -> `3 * (2 * factorial 1)` -> `3 * (2 * 1)` -> `6`. Each
   nested call waits for the one inside it to finish before it can multiply.

Often a public, non-recursive function wraps a **recursive helper** so that extra "accumulator"
parameters don't have to be part of the public API:
```fsharp
let sumBetween m n =
    let rec sumTo value acc =
        if value = n then acc + value
        else sumTo (value + 1) (acc + value)
    if m > n then 0 else sumTo m 0
```
""",
        "variations": """
- Recursion on numbers (count down/up to a base case), on lists (base case `[]`, recursive case
  `x::xs`), and on trees (base case `Empty`/leaf, recursive case a `Node` with sub-trees) all follow
  exactly the same shape.
- A **nested helper function** (as in `sumBetween` above) is extremely common when you need extra
  "accumulator" parameters that shouldn't appear in the outer function's signature.
- Multiple base cases are fine, e.g. Fibonacci needs `| 1 -> 1 | 2 -> 1 | q -> ...`.
""",
        "exam_application": """
Every practical exam question that processes a list, tree, or numeric sequence expects a recursive
solution with a clearly identifiable base case and recursive case. Examiners specifically instruct
"do not use F#'s built-in functions unless explicitly stated" -- meaning you're expected to *write the
recursion yourself*, not call `List.sum` or similar.
""",
        "common_mistakes": """
- Forgetting the `rec` keyword -- immediate compile error the moment the function refers to itself.
- Missing a base case, or writing a base case that never actually gets reached (e.g. testing for `0`
  when the recursive step can skip over `0`, such as stepping down by 2 from an odd start).
- Not actually shrinking the problem on the recursive call (e.g. accidentally calling `factorial k`
  again instead of `factorial (k-1)`) -- causes infinite recursion / stack overflow.
- Writing the base case's *return type* inconsistently with the recursive case's return type.
""",
    },
    "syntax_refs": ["rec-keyword", "match-expr"],
}

CONTENT["recursion-types"] = {
    "levels": {
        "what_is_it": """
Not all recursive functions are equally efficient. This topic (Lecture 3) classifies recursion by
*when the work happens* relative to the recursive call, because that classification directly determines
how much memory a function uses on the call stack and whether the F# compiler can optimise it into a
plain loop.
""",
        "syntax": """
No new syntax here -- the classification is about the *shape* of existing recursive definitions:

- **Forward recursion**: work is done *before* the recursive call (using the current parameters), i.e.
  the recursive call is passed the "work so far" as an argument (an accumulator).
- **Backward recursion**: work is done *after* the recursive call returns -- the function calls itself
  first, then does something with the result on the way back up.
- **Linear recursion**: a function that makes exactly one recursive call to itself.
- **Tail recursion**: linear recursion where the recursive call is the *very last action* -- nothing
  happens to its result before it's returned.
""",
        "how_it_works": """
```fsharp
// Backward recursion (bad): each call must stay "alive" on the stack, waiting to
// multiply its own x by the result of the smaller call once it comes back.
let rec doubleAll list =
    match list with
    | [] -> []
    | (x::xs) -> (2*x) :: (doubleAll xs)     // work (::) happens AFTER the recursive call

// Forward, tail-recursive with an accumulator (good): nothing is left to do after
// the recursive call -- it's the last thing that happens.
let doubleAll3 list =
    let rec doubleHelp xs ys =
        match xs with
        | [] -> ys
        | (x::xs) -> doubleHelp xs ((x*2)::ys)   // recursive call is the LAST action
    reverse (doubleHelp list [])
```
Because a tail call is the last action, the compiler doesn't need to remember anything about the
current call once it makes that final call -- it can reuse the same stack frame, effectively turning
the recursion into a loop (this optimisation is called **tail-call elimination**). Backward recursion
can *never* be tail recursive, because there's always more work (the `::`, the `+`, etc.) waiting to
happen after the call returns -- so every pending call must keep its own stack frame alive, giving
`O(n)` stack usage and real risk of a stack overflow for large inputs.

**Rule of thumb from the slides: tail recursion = good, backward recursion = bad.**
""",
        "worked_example": """
The class exercise (Lecture 3) compares three ways to double every element of a list:

| Function | Time | Stack space |
|---|---|---|
| `doubleAll` (backward) | O(n) | O(n) -- risk of stack overflow |
| `doubleAll2` (forward, tail, but uses `@`) | O(n²) | O(1) |
| `doubleAll3` (forward, tail, `::` + final `reverse`) | O(n) | O(1) |

`doubleAll2` looks tail-recursive (its recursive call is last), but it builds the result with
`ys @ [x*2]`, and `@` itself is `O(n)` (it has to walk the whole left list to append at the end) -- so
even though the *stack* is fine, the *total work* becomes `O(n²)`. `doubleAll3` avoids this by
prepending with `::` (`O(1)`) and reversing once at the end (`O(n)`), giving `O(n) + O(n) = O(n)`
overall -- this "build reversed, then reverse once" pattern is one of the most useful tricks in the
whole module.
""",
        "variations": """
- Forward recursion is not automatically good -- as `doubleAll2` shows, you must also pick `O(1)`
  operations (`::`, not `@`) inside the accumulator step.
- A linear recursive function can sometimes be rewritten as tail recursive by introducing an
  accumulator parameter (as in `sumBetween`/`doubleHelp` above), but this is not always possible for
  every algorithm (e.g. some tree algorithms fundamentally need to combine two recursive results, which
  is inherently non-tail, non-linear recursion -- see Trees & Custom Recursive Data Structures).
""",
        "exam_application": """
"Write the same function using forward/backward recursion" is a recurring, near-guaranteed practical
question type (it appears, in some form, on 2023's and 2024's papers, and in Homework 3/Week 3).
Examiners expect you to *name* which kind of recursion you used and, often, to justify efficiency
(state the time/stack complexity), not just produce working code.
""",
        "common_mistakes": """
- Calling any recursive function "tail recursive" just because you can't see explicit extra work --
  check specifically whether the recursive call is the very last thing evaluated, with nothing (not
  even an operator like `::` or `+`) applied to its result afterwards.
- Assuming forward recursion is automatically efficient -- forgetting that `@` (list append) is `O(n)`,
  so accumulating with `xs @ [x]` inside a "forward" recursive loop is still quadratic overall.
- Confusing "linear recursion" (one recursive call) with "tail recursion" (a *stronger* condition: one
  recursive call **and** it's the last action) -- every tail-recursive function is linear recursive, but
  not every linear recursive function is tail recursive.
""",
    },
    "syntax_refs": ["rec-keyword", "tail-recursion", "list-append-op"],
}

CONTENT["lists-basics"] = {
    "levels": {
        "what_is_it": """
Lists are F#'s core linear data structure -- think of them as a singly-linked list, not an array. This
topic covers how lists are actually built up (recursively!) and how pattern matching is used to take
them apart, which is the foundation for almost every list-processing function you'll write in this
module.
""",
        "syntax": """
A list is defined recursively: it is *either* the empty list `[]`, *or* an element `h` followed by
another (smaller) list, written `h :: list` (`::` is the **cons** operator).

```fsharp
let mylist = [43; 28; 11; 73; 22]           // literal list syntax
let x = 5 :: 2 :: 1 :: 4 :: []               // exactly the same list, built with ::
let combined = list1 @ list2                 // @ concatenates two whole lists
```
Pattern matching a list:
```fsharp
let rec sum b =
    match b with
    | [] -> 0
    | (h::t) -> h + sum t
```
`(h::t)` matches any *non-empty* list, binding `h` (the first element) and `t` (the rest of the list,
itself a list -- possibly `[]`).
""",
        "how_it_works": """
`::` only ever attaches **one element** to the front of an **existing list** -- `x :: mylist` works
(`x` is an int, `mylist` is a list of ints), but `x :: 3` does not, because `3` is not a list. `@`, by
contrast, joins two whole *lists* together and has to walk every element of its left-hand argument to
attach the right-hand list at the end, making `@` an `O(n)` operation where `n` is the length of the
left list -- whereas `::` is `O(1)`, since it just wraps the existing list with one new head.

When you `match` a list against `(h::t)`, F# only succeeds if the list has at least one element --
`[]` will *not* match `(h::t)`, and vice versa, which is exactly why every list-recursive function needs
both an `[]` case and an `(h::t)` case (this is the base case / recursive case split from Recursion
Fundamentals, specialised to lists).
""",
        "worked_example": """
```fsharp
// Remove consecutive duplicates (Week 2 class notes)
let rec remdups x =
    match x with
    | (q::y::xs) -> if q = y then remdups (y::xs)
                    else q :: (remdups (y::xs))
    | xs -> xs
```
1. `(q::y::xs)` -- `::` can be *stacked*: this pattern matches a list of **at least two** elements,
   binding `q` to the first, `y` to the second, and `xs` to everything after that (so `xs` might be
   `[]`).
2. If the first two elements are equal (`q = y`), we drop `q` and recurse on `y::xs` (i.e. we keep only
   one copy of the repeated value, by not re-adding `q`).
3. Otherwise, we keep `q` at the front (`q :: ...`) and recurse on the rest.
4. `| xs -> xs` -- the fallback pattern: this matches when the first pattern *doesn't* (i.e. the list
   has 0 or 1 elements), and simply returns it unchanged -- a list that short can't have "consecutive
   duplicates" to remove.
""",
        "variations": """
- `take n list` / `drop n list` use a **3-way match on a tuple** `(n, list)` to handle the base cases
  cleanly: `match (n, list) with | (0, _) -> [] | (_, []) -> [] | (n, (x::xs)) -> ...`.
- Building a list in a different base (`ConvertToBase`) shows the same "cons pattern applied
  recursively" idea used to build up output, not just consume input.
- `list1 @ list2` vs manually recursing with `::` -- know both, but prefer `::` for building results
  one element at a time (see Recursion Types for why).

**Supplementary (from the purchased Extra Modules, not part of the official course):** F#'s built-in
`Array` type (fixed-size, mutable, index-accessed) is covered in *F# in Action* (Abraham) Chapter 7,
"Working with collections", alongside lists -- useful general context, but the lecturer's own material
and every supplied exam question work exclusively with F#'s recursive `list` type, so `Array` is not
examinable here.
""",
        "exam_application": """
This is the most fundamental practical skill in the whole module -- essentially every practical exam
question (general list questions, record-list questions, tree flattening) is built on top of confidently
pattern-matching lists with `[]` / `(h::t)` / stacked patterns like `(a::b::rest)`. Expect a "manipulate
a list without built-in functions" question in some form on every paper.
""",
        "common_mistakes": """
- Trying `x :: 3` or `x :: mylist` the wrong way round -- `::` needs (element, list), not (list,
  element) or (element, element).
- Forgetting the `[]` base case for a list-recursive function, causing a "MatchFailureException" at
  runtime on an empty input.
- Using `@` where `::` would do -- functionally correct, but far less efficient, and markers may
  penalise it in an efficiency-focused question.
- Writing `(h::t)` and forgetting it does not match `[]` -- if you need to handle "any list including
  empty" in one pattern, you need a separate `[]` case (or use `_`, but then you lose access to `h`/`t`).
""",
    },
    "syntax_refs": ["cons-operator", "append-operator", "list-literal", "list-pattern-match"],
}

CONTENT["higher-order-currying"] = {
    "levels": {
        "what_is_it": """
Because functions are first-class values in F# (Core Concepts topic), you can pass a function *as a
parameter* to another function, or return one *as a result*. A function that does either is called a
**higher-order function** -- `map`, `filter`, `fold` are the classic examples. This topic also covers
**currying**: the fact that every multi-parameter F# function is secretly a chain of single-parameter
functions, which is what makes **partial application**, **composition**, and the **pipeline operator**
possible.
""",
        "syntax": """
```fsharp
let applyFtoFive f = f 5           // f : (int -> 'a), a function passed as a parameter

let g x y = x + y + 1              // g : int -> int -> int   (NOT "two parameters" -- see below)
let temp = g 5                     // partial application: temp : int -> int
temp 3                             // = 4

let fog = f << g                   // composition:  fog x  =  f (g x)
let gof = g >> f                   // composition, other direction: gof x = f (g x) as well!

let complex2 x = x |> square |> add5 |> toString   // pipeline: data flows left-to-right
```
""",
        "how_it_works": """
A function's type signature like `int -> int -> int` should be read as `int -> (int -> int)`: `g` is
actually a function that takes one `int` and returns *another function* (`int -> int`), which then
takes the second `int` and returns the final `int`. This is called **currying**, and it's why you can
supply *fewer* arguments than the function "seems" to need: `g 5` alone is perfectly valid and produces
a new function, of type `int -> int`, that's "waiting" for its second argument.

`>>` and `<<` build a new function by chaining two existing ones: `f << g` means "first apply `g`, then
apply `f` to the result" (`(f << g) x = f (g x)`), while `f >> g` reads left-to-right: "first `f`, then
`g`" (`(f >> g) x = g (f x)`). The pipeline operator `|>` is not really new syntax for functions at
all -- it's syntactic sugar for "put this value as the last argument of the function on the right":
`x |> f y` desugars to `f y x`. It exists purely to let you write a chain of transformations in the
same left-to-right order that the data actually flows, instead of nesting calls inside-out:
`f (g (h x))` becomes the far more readable `x |> h |> g |> f`.
""",
        "worked_example": """
```fsharp
// Standard deviation, rewritten with |>, currying and an anonymous function
// (Week 4 class notes)
let div (a : float) b = b / a
let subsquare (m : float) (x : int) = (float x) - m |> (fun x -> x * x)
let rec ApplyAndSum lis f =
    match lis with
    | [] -> 0.0
    | (x::xs) -> f x + ApplyAndSum xs f

let stdev2 lis =
    average lis |> subsquare |> ApplyAndSum lis |> div (float (length lis)) |> sqrt
```
Reading the last pipeline left to right: compute `average lis`; pipe it into `subsquare`, which is
curried so `subsquare mean` is itself a function `int -> float` (still waiting for `x`); pipe *that
function* into `ApplyAndSum lis`, which applies it to every element of `lis` and sums the results; pipe
the sum into `div (float (length lis))` (a curried, partially-applied division); finally pipe the result
through `sqrt`. Each `|>` feeds the value on its left in as the *last* argument to the call on its right.
""",
        "variations": """
- Anonymous (lambda) functions: `fun x -> x * x`, used inline wherever a full `let`-bound function would
  be overkill, especially inside pipelines: `x |> (fun x -> x * x) |> (fun x -> x + 5)`.
- `Double2 = Mult 2` -- naming a partially-applied function directly, rather than immediately calling it
  further, is a very common exam trick to test whether you understand currying.
- `>>` and `<<` are mirror images of each other -- know which reads left-to-right (`>>`) and which reads
  right-to-left (`<<`, matching ordinary mathematical function composition `f∘g`).

**Supplementary (from the purchased Extra Modules, not part of the official course):** *F# in Action*
(Abraham) Chapter 6, "Functions and modules", covers currying and composition from a slightly different
angle with more real-world examples if the lecture's treatment doesn't click on first read.
""",
        "exam_application": """
Expect direct "what is the type of this partially-applied function?" questions, and expect (or be
rewarded for) using `|>` and composition idiomatically in general practical questions -- e.g. the 2024
exam's "filter function that accepts some other function f" question is a direct higher-order-function
exercise.
""",
        "common_mistakes": """
- Thinking a function like `let g x y = ...` "has two parameters" in the C/Java sense -- it has one
  parameter and returns a function; this matters when you partially apply it or pass it around.
- Getting `>>` and `<<` backwards -- always double-check by substituting a concrete `x` and expanding by
  hand if unsure.
- Misremembering how `|>` desugars -- it's specifically "value becomes the **last** argument"
  (`x |> f y` = `f y x`), not the first.
- Writing `(fun x -> x * x) x` style double-application by accident when a plain `x * x` would do --
  lambdas are for when you need a function *value*, not just an inline calculation.
""",
    },
    "syntax_refs": ["lambda-expr", "pipeline-operator", "composition-operators", "currying"],
}

CONTENT["tuples-records"] = {
    "levels": {
        "what_is_it": """
Tuples and records both group multiple pieces of data into one value, but differently: a **tuple**
groups a fixed number of *unnamed* fields where *order* is what identifies each one; a **record** groups
*named* fields, accessed by name, where order doesn't matter. **Generics** let a function or type work
across many types at once using a placeholder like `'a`.
""",
        "syntax": """
```fsharp
// Tuple: (v1, v2, ..., vn); type written v1_type * v2_type * ... e.g. int * int
let y = (5, 9)
let average (a, b) = (a + b) / 2      // pattern-match a pair directly in the parameter
let x = fst y                          // built-in: first element of a pair
let z = snd y                          // built-in: second element of a pair

// Record: named fields
type person = { name : string; age : int }
let mc = { name = "Alex Smith"; age = 24 }
let mc2 = { mc with name = "Alexander J. Smith" }   // record UPDATE: copies mc, changes one field
```
""",
        "how_it_works": """
A tuple is a single value even though it holds several things -- `(5, 9)` has type `int * int`, and a
function that "returns two things" in F# really returns one tuple value. Because a tuple's fields are
unnamed, you either **pattern match** them apart (`let (a, b) = pair`, or directly in a parameter list
like `average (a, b) = ...`) or use the built-ins `fst`/`snd` (pairs only).

A record's type must be declared up-front with `type ... = { field1 : type1; ... }` -- you cannot define
an anonymous record type inline the way you can just write a tuple literal. Record values are still
**immutable** by default: `{ item with name = newN }` does not mutate `item` -- it builds a brand-new
record, copying every field from `item` except the ones you explicitly override after `with`. This is
the record equivalent of the fact that `let` bindings can't be mutated: instead of changing a field, you
construct a new value that differs in that one field.

Record pattern matching can match on some fields and ignore others, and can include literal values to
match specific records:
```fsharp
match item with
| { name = "Alex Smith"; age = 24 } -> "exact match"
| item when item.name = "Alex" -> "guard using a named field"
| _ -> "anything else"
```
Generics (`'a`, `'b`, ...) let F# express "this works for *any* type here", e.g. `swap : 'a * 'b -> 'b *
'a` works on a pair of any two types. You rarely need to write `'a` explicitly -- F#'s type inference
adds it automatically when your code doesn't force a specific type -- but you'll need to *recognise* it
in signatures and understand why some functions are generic and others aren't.
""",
        "worked_example": """
```fsharp
// Sum and product of a list, as a tuple result (Week 5 class exercise, forward recursion)
let rec sumprod2 list =
    match list with
    | [] -> (0, 1)
    | (x::xs) ->
        let y = sumprod2 xs
        (x + (fst y), x * (snd y))
```
1. Base case: an empty list has sum `0` and product `1` (the identities for `+` and `*`), returned
   together as the pair `(0, 1)`.
2. Recursive case: first recursively solve the rest of the list (`sumprod2 xs`), binding the resulting
   pair to `y`.
3. Build the new pair: add `x` to the previous sum (`fst y`) and multiply `x` into the previous product
   (`snd y`) -- both computed from the *same* recursive call, which is why this is more efficient than
   calling `sumprod2 xs` twice (once via `fst`, once via `snd`).
""",
        "variations": """
- Tuples of any size: `scalarMult (s) (a, b, c, d, e) = (a*s, b*s, c*s, d*s, e*s)` -- a 5-tuple.
- `zip`/`unzip`: converting between two parallel lists and one list of pairs, and back.
- Records can be updated on multiple fields at once: `{ item with name = n; age = a }`.
- Sorting/ranking a list of records (e.g. by exam mark) is a very common combined records+recursion
  exercise (Week 5 homework).

**Supplementary (from the purchased Extra Modules, not part of the official course):** *F# in Action*
(Abraham) Chapter 5, "Shaping data", and *Learning F# Functional Data Structures and Algorithms* (Adnan)
Chapter 3, "What's in the Bag Anyway?", both cover tuples/records alongside F#'s built-in `Set` and `Map`
collection types. Sets/Maps were never mentioned in the lecture material or any supplied exam, but are
worth knowing exist -- e.g. `Set.ofList` removes duplicates in one call, which is conceptually related
to several "distinct elements" style homework questions you've solved by hand with recursion instead.
""",
        "exam_application": """
Records are their own dedicated exam section every year ("2.2 Records", worth 12-33 marks across the
sample papers): define a record type, build a list of them, then write functions over that list
(filter/insert-sorted/single-pass aggregate). The "single pass" requirement recurs often -- markers
specifically check you're not scanning the list three times to get sum/min/max separately when one
recursive pass computing a tuple `(sum, min, max)` would do.
""",
        "common_mistakes": """
- Confusing tuples and records: reaching for a tuple when named fields would make the code far clearer
  (or vice versa, over-engineering a record for something that's just a pair).
- Forgetting record update syntax copies-and-overrides rather than mutating -- `{ item with age = 30 }`
  produces a *new* record; `item` itself is unchanged.
- Writing `fst`/`snd` on a tuple that isn't a pair (they only exist for 2-tuples in F#'s standard
  library) -- for a 3-tuple or larger you must pattern-match instead.
- Scanning a list multiple times (once per statistic) when a single recursive pass accumulating a tuple
  of results would satisfy a "single pass" requirement.
""",
    },
    "syntax_refs": ["tuple-literal", "fst-snd", "record-type", "record-update", "generics"],
}

CONTENT["lists-continued"] = {
    "levels": {
        "what_is_it": """
Building on List Fundamentals, this topic covers F#'s *convenience* syntax for creating lists (ranges,
comprehensions) and the standard `List` module's ready-made higher-order functions (`map`, `filter`,
`fold`, `reduce`, ...). It also covers three classic algorithms the course uses as running examples:
the Sieve of Eratosthenes, Quicksort, and generating permutations.
""",
        "syntax": """
```fsharp
[1 .. 10]                 // [1;2;...;10]
[1 .. 2 .. 10]             // [1;3;5;7;9]           (step of 2)
['a' .. 'e']               // character ranges work too

// List comprehension: [ for x in range do yield expression ]
[ for a in 1 .. 5 do yield a * a ]          // [1;4;9;16;25]
[ for a in 1 .. 100 do if odd a then yield a ]   // comprehension with a filter condition
[ for a in 1 .. 5 do yield! [a .. a+3] ]     // yield! splices in a whole sub-list (flattening)
```
`List` module highlights: `List.map f lis`, `List.filter f lis`, `List.fold f initial lis`,
`List.reduce f lis`, `List.head`, `List.tail`, `List.distinct`.
""",
        "how_it_works": """
A list comprehension `[ for a in start .. step .. end do yield expr ]` is really a compact way of
writing "for every value `a` in this range, compute `expr` and include it in the result list" -- and
crucially you can add an `if` condition inside to only `yield` some of them (this *is* filtering, done
inline, without calling `List.filter` at all). `yield!` (with the `!`) is different from `yield`: plain
`yield` adds *one* element per iteration, while `yield! someList` splices *all* the elements of
`someList` into the result, which is essential when each iteration itself produces a sub-list you want
flattened rather than nested.

`List.fold f initial lis` generalises `sum`/`product`-style recursion: it walks the list left to right,
starting from `initial`, repeatedly combining the running result with the next element using `f`. Every
recursive "accumulate a single value over a list" function you've hand-written so far (`sum`, `mult`,
`length`) is a specific case of `fold`. `List.reduce` is the same idea but uses the list's *first*
element as the starting value instead of a separate `initial` (so it fails on an empty list, unlike
`fold`).
""",
        "worked_example": """
```fsharp
// Sieve of Eratosthenes (Week 6 class notes) -- find all primes up to n
let rec sieve lis =
    match lis with
    | [] -> []
    | (x::xs) -> x :: sieve [ for n in xs do if n % x <> 0 then yield n ]
let primes = sieve [2 .. 100]
```
1. Base case: sieving an empty list gives an empty list.
2. Recursive case: the head `x` of the remaining list is guaranteed prime (nothing smaller has divided
   it out yet), so keep it (`x :: ...`).
3. Build the list to recurse on using a **comprehension with a filter**: keep only the elements of `xs`
   that are *not* divisible by `x` (`n % x <> 0`) -- this strips out all of `x`'s multiples in one pass.
4. Recurse on that filtered list, which is strictly smaller each time, until it's empty.

```fsharp
// Quicksort (Week 6), using two comprehensions to partition
let rec qs lis =
    match lis with
    | [] -> []
    | (x::xs) ->
        let smalls = [ for y in xs do if y < x then yield y ]
        let bigs   = [ for y in xs do if y >= x then yield y ]
        qs smalls @ [x] @ qs bigs
```
Pick the head `x` as pivot, partition the rest into `smalls`/`bigs` using comprehensions, recursively
sort each partition, then reassemble with `@` (average case `O(n log n)`, worst case `O(n²)` if the
list is already sorted, since the pivot then splits it as unevenly as possible every time).
""",
        "variations": """
- `perms` (permutations) uses **backward recursion** and a nested comprehension: for each choice of
  first element `a`, recursively find all permutations of the rest (with `a` removed), and prepend `a`
  to each -- a good example of a comprehension whose `yield` expression is itself the result of a
  recursive call.
- `List.filter f l` can always be replaced by a comprehension `[for a in l do if f a then yield a]`, and
  vice versa -- know both idioms, since some exam questions explicitly forbid built-ins.
- Nested comprehensions (`for a in ... do for b in ... do yield (a, b)`) generate all *pairs* -- this is
  exactly the 2020 exam's "produce all pairs from two lists" question.

**Supplementary (from the purchased Extra Modules, not part of the official course):** F#'s lazy `seq {
}` (sequence) syntax, covered in *Learning F# Functional Data Structures and Algorithms* (Adnan) Chapter
4, "Are We There Yet?", and *Expert F# 4.0* (Syme, Granicz & Cisternino) Chapter 9, "Working with
Sequences and Tree-Structured Data", looks almost identical to the list comprehensions used in this
module but evaluates elements on demand rather than building the whole list upfront. Interesting general
F# knowledge, but not used anywhere in the lecture material or supplied exams -- this module's
comprehensions always produce an eager `list`.
""",
        "exam_application": """
List comprehensions are frequently the fastest correct way to answer a "no built-in functions" practical
question, since they're comprehension syntax, not a call to `List.filter`/`List.map` -- always check the
exam's instructions on which built-ins (if any) are banned for that specific question.
""",
        "common_mistakes": """
- Using `yield` where `yield!` was needed (or vice versa) -- `yield` for a single item, `yield!` to
  splice in a whole list, mixing them up either nests lists unexpectedly or fails to compile.
- Forgetting `List.reduce` throws on an empty list (unlike `List.fold`, which has an explicit initial
  value and handles empty lists fine).
- Re-scanning the same source list many times across several separate comprehensions when one combined
  pass would be more efficient (mirrors the "single pass" expectation from Records).
- Quicksort worst-case complexity: assuming it's always `O(n log n)` and forgetting the `O(n²)`
  worst case on already-sorted input with this naive pivot-is-always-the-head strategy.
""",
    },
    "syntax_refs": ["range-syntax", "list-comprehension", "yield-bang", "list-module-fns"],
}

CONTENT["induction"] = {
    "levels": {
        "what_is_it": """
Recursive functions look elegant, but "it looks right" isn't a proof. **Mathematical induction** is the
formal tool for proving a property holds for *every* possible input, by proving it for the smallest case
(the **base case**) and then proving that *if* it holds for some case, it must also hold for the "next"
case (the **inductive step**). Because F# lists are themselves defined recursively (empty list, or an
element consed onto a smaller list), induction over lists -- **structural induction** -- mirrors the
recursive structure of the list exactly, and mirrors the base-case/recursive-case structure of the
function you're proving something about.

This is, going by the user's own Class Test 7 result, the single area most worth deliberately drilling.
""",
        "syntax": """
The proof always has the same skeleton:

1. State the **hypothesis** `H(xs)`: the equation you're trying to prove, for an arbitrary list `xs`.
2. **Base case**: prove `H([])` directly -- substitute `[]` for `xs` on both sides and simplify each
   side (usually using the list Laws below and the function's own defining equations) until they match.
3. **Inductive step**: *assume* `H(xs)` is true (this is the **Inductive Assumption**, sometimes
   written I.A.) and use it to prove `H(x::xs)` -- i.e. show the property also holds when you cons one
   more element `x` onto the front.
4. **Conclusion**: since the base case and inductive step both hold, `H(xs)` is true for *every* list
   `xs`.

The 10 Laws (identities) you're allowed to cite as justification for each rewrite step:
```
1. head (x::xs) = x
2. tail (x::xs) = xs
3. [] @ xs = xs
4. xs @ [] = xs
5. xs @ (ys @ zs) = (xs @ ys) @ zs        (@ is associative)
6. (x::xs) @ ys = x :: (xs @ ys)
7. length (xs @ ys) = length ys + length xs
8. reverse (reverse xs) = xs
9. (take n xs) @ (drop n xs) = xs
10. [x] @ xs = x :: xs                     (given in Homework 7; follows from Law 6 + Law 4)
```
""",
        "how_it_works": """
Every step in a proof must be justified by *one* of: a numbered Law, one of the function's own defining
lines (its `match` cases), the Inductive Assumption, or ordinary algebra (associativity of `+`/`*`, or
of `||`). **Law 6 is the single most-used step in almost every proof in this module** -- because the
thing being proved almost always involves `(x::xs) @ ys` somewhere, and Law 6 is the *only* rule that
tells you how to unfold `@` when its left argument is a cons cell rather than `[]`. If you get stuck in
a proof, "can I apply Law 6 to something that looks like `(x::xs) @ ys`?" is the first thing to check.

The general strategy for the inductive step is: take the more complex side (usually the LHS), and
mechanically rewrite it -- unfold `@` with Law 6, unfold the function call using its own recursive
definition line, substitute in the Inductive Assumption wherever the smaller sub-problem `xs` appears --
until it becomes syntactically identical to the RHS. Some proofs (like `elem`) need a **case split**
inside the inductive step, when the function itself branches on a condition (e.g. whether the new head
`x` equals the target value) -- in that situation you must prove *both* resulting cases separately.
""",
        "worked_example": """
The exact proof from Homework Set 7 (a proof the user has already seen marked correct), for
`sum (xs @ ys) = sum xs + sum ys`, given:
```fsharp
let rec sum list =
    match list with
    | [] -> 0                    (* Line 1 *)
    | (x::xs) -> x + sum xs      (* Line 2 *)
```
**Base case, H([]):** `sum ([] @ ys) = sum [] + sum ys`
- LHS: `sum ([] @ ys) = sum ys` (Law 3)
- RHS: `sum [] + sum ys = 0 + sum ys` (Line 1) `= sum ys`
- LHS = RHS ✓

**Inductive step, H(x::xs)**, assuming `H(xs): sum (xs @ ys) = sum xs + sum ys`:
Prove `sum ((x::xs) @ ys) = sum (x::xs) + sum ys`.
```
  sum ((x::xs) @ ys)
= sum (x :: (xs @ ys))          Law 6
= x + sum (xs @ ys)             Line 2
= x + (sum xs + sum ys)         Inductive Assumption
= (x + sum xs) + sum ys         + is associative
= sum (x::xs) + sum ys          Line 2 (in reverse)
= RHS
```
Since the base case and inductive step both hold, `H(xs)` holds for every list `xs`. **QED.**
""",
        "variations": """
The same skeleton proves many different statements once you recognise the pattern -- practice these,
they cover essentially every induction proof this module has ever examined:
- `leng (xs @ ys) = leng xs + leng ys` (Lecture 7 Example 2) -- structurally identical to `sum`.
- `mult xs * mult ys = mult (xs @ ys)` (2024 exam Q1) -- same shape again, with `*` instead of `+`.
- `xs @ (ys @ zs) = (xs @ ys) @ zs` (Lecture 7 Example 1) -- this is the proof *of* Law 5 itself.
- `reverse (xs @ ys) = reverse ys @ reverse xs` (Class Exercise) -- needs Law 5 in the inductive step.
- `reverse (reverse xs) = xs` (Homework 7 Q2) -- needs the *previous* proof as a lemma, plus a small
  extra helper fact (`reverse [x] = [x]`).
- `elem e (xs @ ys) = elem e xs || elem e ys` (Class Test 7 / 2022 exam) -- the hardest of these,
  because `elem`'s own definition branches with a guard, forcing a **case split** (`x = e` vs `x ≠ e`)
  inside the inductive step.
""",
        "exam_application": """
A structural induction proof is a guaranteed Theory-section question on every one of the four sample
papers (worth 7-9 marks). Markers grade the *structure* as much as the final answer: you need an
explicit hypothesis statement, a clearly separated base case and inductive step, an explicitly stated
inductive assumption, and a law/line citation on every single rewrite -- an unjustified jump, even to a
"clearly true" step, loses marks.
""",
        "common_mistakes": """
- Skipping the explicit hypothesis / inductive assumption statement and jumping straight to algebra --
  markers want to see `H(xs)` and `H(x::xs)` written out, not just implied.
- Forgetting Law 6 is needed the moment `(x::xs) @ ys` appears -- trying to unfold the function's own
  recursive case directly on `(x::xs) @ ys` without first rewriting it as `x :: (xs @ ys)`.
- Proving only *one* direction of an equality and treating it as done, instead of chaining all the way
  from one side to the other (or reducing both sides to a common expression).
- For functions with guards (like `elem`), forgetting the case split entirely and only proving the
  "easy" branch.
- Citing "Inductive Assumption" for a step that hasn't actually reached the smaller sub-problem `xs`
  yet (the I.A. can only be used once the expression literally contains `... xs ...`, matching the
  hypothesis `H(xs)` exactly).
""",
    },
    "syntax_refs": ["induction-laws", "match-expr"],
}

CONTENT["lambda-calculus"] = {
    "levels": {
        "what_is_it": """
Lambda calculus is the tiny mathematical system (Alonzo Church, 1930s) that functional programming --
and F# itself -- is built on. It has exactly three kinds of expression (a name, a function, an
application) and one computation rule (beta reduction), yet it's powerful enough to encode numbers,
booleans, and any computable function. It appears in **every single one** of the four supplied exam
papers, always in the Theory section, always worth a substantial chunk of marks.
""",
        "syntax": """
```
<expression>  ::= <name> | <function> | <application>
<function>    ::= λ<name>.<expression>        (course also writes this as \\name.expression)
<application> ::= (<function> <expression>)
```
- A **name** is just an identifier: `x`, `bob`, `y16`.
- A **function** `λx.x` binds the name `x` as its parameter; the part after the `.` is its body.
- An **application** `(f a)` applies function `f` to argument `a` -- always written with the function
  first, argument second, wrapped in parens.

The course's standard **Church encodings**, given in every exam's appendix (you don't need to memorise
these -- they're always provided):
```
True      = λa.λb.a
False     = λc.λd.d
Condition = λe.λf.λg.((g e) f)
Not (¬)   = λh.((h False) True)
And (∧)   = λi.λj.((i j) False)
Or  (∨)   = λk.λm.((k True) m)
```
""",
        "how_it_works": """
The single computation rule is **beta reduction**:
```
(λv.<body>  <arg>)   becomes   <body> with every occurrence of v replaced by <arg>
```
When an expression has more than one place you *could* apply beta reduction, this course always reduces
the **leftmost, outermost** redex first (work from the outside in, left to right) -- this is the
convention every worked example and memo in the course material follows, so match it to get partial
marks even if you don't reach the final answer.

`True` and `False` are functions that, when given two arguments, pick the first or the second
respectively -- that's the entire trick behind Church-encoded booleans: `((True a) b)` reduces to `a`,
and `((False a) b)` reduces to `b`. `And`, `Or`, `Not` and `Condition` are all built purely by combining
`True`/`False` with this "pick an argument" behaviour -- e.g. `And i j` reduces to `((i j) False)`: *if*
`i` is `True`, this becomes `(True j) False`, which (by `True`'s own behaviour) picks `j` -- so `And`
correctly returns `j`'s truth value exactly when `i` is true, and `False` otherwise.
""",
        "worked_example": """
Evaluating `(λs.(s s) λx.x)`, step by step (leftmost-outermost, exactly the course's own style):
```
(λs.(s s) λx.x)
```
The whole expression is already a redex: function `λs.(s s)` applied to argument `λx.x`. Substitute
every `s` in `(s s)` with `λx.x`:
```
(λx.x λx.x)
```
This is a new redex: `λx.x` applied to `λx.x`. Substitute `x := λx.x` into the body `x`:
```
λx.x
```
No more redexes remain (a lone function with nothing applied to it) -- this is the **normal form**, and
the whole reduction is finished.

A self-application example that does **not** terminate (from the course's own lambda calculus notes):
`(λs.(s s) λs.(s s))` reduces to `(λs.(s s) λs.(s s))` -- itself, forever. Recognising when a reduction
loops (rather than assuming you made a mistake) is itself a useful exam skill.
""",
        "variations": """
- Boolean logic questions: given a truth table, first *build* the matching lambda expression out of
  `True`/`False`/`And`/`Or`/`Not`/`Condition` (this is closer to "translation" than computation), then
  *evaluate* it for specific input values by substituting the named `True`/`False` values in for the
  variables and reducing to normal form -- these are usually two separate sub-questions on the exam.
- `Condition` implements if/then/else: `((Condition e1) e2) c` conceptually means "if `c` then `e1` else
  `e2`" once you unfold its definition -- different exam years phrase its parameter order slightly
  differently in the appendix, always re-read the specific year's definition rather than assuming.
- Expressions can nest arbitrarily deep (see the 2023 exam Q1) -- track *which* variable belongs to
  *which* lambda carefully; renaming on paper as you go (e.g. underlining matching pairs) avoids the
  most common error.
""",
        "exam_application": """
Expect: (1) a "evaluate this lambda expression" pure-mechanics question (6-8 marks), and (2) a
"represent this truth table / logic statement as lambda calculus, then evaluate it for specific values"
question (11-17 marks combined) -- together these make lambda calculus one of the highest, most
reliably-marked question types across all four sample papers. Show every single reduction step; partial
credit is given for correct intermediate steps even if the final answer is wrong.
""",
        "common_mistakes": """
- Reducing an *inner* redex before an outer one exists to reduce -- stick to leftmost-outermost so your
  working matches the expected memo style step-for-step.
- Variable capture: substituting into a function whose parameter has the *same name* as a variable free
  in the argument, without renaming first -- this course's exercises rarely force you to actually hit
  this edge case, but be alert to it in nested expressions with repeated variable names like `x`, `y`.
- Forgetting that `True`/`False`/`And`/etc. are *not* built-in magic -- they are themselves just lambda
  expressions and must be substituted in (expanded) before you can reduce through them.
- Stopping one step early -- a partially-applied `True`/`False` (e.g. `λb.a` instead of fully reduced
  down through both arguments) is not yet in normal form if there's still an argument waiting to be
  applied to it.
""",
    },
    "syntax_refs": ["lambda-syntax", "beta-reduction", "church-booleans"],
}

CONTENT["discriminated-unions"] = {
    "levels": {
        "what_is_it": """
A discriminated union (DU) is an "OR" type: a value of that type is *exactly one* of a fixed set of
named alternatives ("cases"), each of which can optionally carry its own data. This is different from a
tuple or record, which are "AND" types (they always have *all* their fields at once). DUs are how you
model "one of several possibilities" precisely -- and they make **illegal states unrepresentable**: you
literally cannot construct a value that isn't one of the declared cases.
""",
        "syntax": """
```fsharp
type unionName =
    | Case1
    | Case2 of dataType
    | Case3 of type1 * type2       // multiple UNNAMED fields, separated by *
    | Case4 of field1 : type1 * field2 : type2   // NAMED fields

// Example (Week 8 / Lecture 8)
type switchState =
    | On
    | Off
    | Adjustable of float

let toggle stat =
    match stat with
    | On -> Off
    | Off -> On
    | Adjustable bright -> if bright + 0.5 > 1.0 then Adjustable 0.0
                            else Adjustable (bright + 0.5)
```
F# ships two predefined DUs you'll use constantly: `Option<'T>` (cases `Some x` / `None`, for "a value
that might not exist") and `Result<'T,'E>` (cases `Ok x` / `Error e`, for "an operation that might
fail").
""",
        "how_it_works": """
Each case name acts as a **constructor** -- `Adjustable 0.3` builds a value of type `switchState` that
"remembers" both which case it is (`Adjustable`) and the data attached to it (`0.3`). Pattern matching
is how you get that data back out: `match stat with | Adjustable bright -> ...` only matches values
built with the `Adjustable` constructor, and binds `bright` to whatever float was stored inside.

Because the compiler knows the *complete, fixed* list of cases for a DU, it will warn you (an
"incomplete match" warning) if your `match` doesn't cover every case -- this is a real safety net:
forgetting to handle `Off` in the `toggle` function above would be flagged, unlike an equivalent
if/else-chain in an imperative language, where a missed case just silently does nothing.

Unnamed-field cases (`Case3 of type1 * type2`) must be matched positionally, pattern-matching *all* the
fields at once (`| Case3 (a, b) -> ...`); named-field cases let you refer to fields by name and can
ignore ones you don't need.
""",
        "worked_example": """
```fsharp
type tree =
    | Empty
    | Node of tree * int * tree

let mytree = Node(Node(Empty, 1, Empty), 3, Node(Empty, 7, Empty))

let rec sumTree t =
    match t with
    | Empty -> 0
    | Node (l, n, r) -> sumTree l + n + sumTree r
```
1. `tree` has exactly two cases: `Empty` (a leaf/empty tree, carries no data) and `Node` (carries a left
   sub-tree, an int value, and a right sub-tree -- three unnamed fields).
2. `mytree` is built by nesting `Node` constructors -- this *is* the tree, there's no separate "build"
   step; construction and the data structure are the same thing.
3. `sumTree`'s base case handles `Empty` (sum of nothing is `0`); its recursive case destructures a
   `Node` into `(l, n, r)` and recursively sums both sub-trees plus the node's own value `n`.
4. This is a **binary tree**, i.e. a discriminated union used to build a recursive data structure -- see
   Trees & Custom Recursive Data Structures for much more on this pattern.
""",
        "variations": """
- Enum-like DUs with no data at all in any case behave much like a C-style enum, but can still be
  pattern-matched exhaustively.
- Mixing cases with and without data in the same type (as `switchState` does: `On`/`Off` carry nothing,
  `Adjustable` carries a `float`) is completely normal and common.
- `Option`/`Result` in practice: `Some 5`, `None`, `Ok result`, `Error "message"` -- pattern match these
  exactly like any user-defined DU.

**Supplementary (from the purchased Extra Modules, not part of the official course):** *F# in Action*
(Abraham) Chapter 8, "Patterns and unions", and *Learning F# Functional Data Structures and Algorithms*
(Adnan) Chapter 3, "What's in the Bag Anyway?", both go on to cover **active patterns** (a way to define
your own custom, named pattern-matching cases over existing types) -- a genuinely useful F# feature, but
one that never appears in the lecture slides or any of the four supplied exam papers, so treat it as
interesting background rather than something to prepare for the exam.
""",
        "exam_application": """
"Discriminated Unions" is its own dedicated, usually the *largest*, exam section every year (24-39
marks across the sample papers) -- almost always framed as "design a data type for X, then write
functions over it" (a proposition/boolean-formula type, a trie, a compressed BST). Defining the type
correctly in part 1 is worth marks on its own, and getting it wrong cascades into every later
sub-question, so read the described structure very carefully before writing the `type` declaration.
""",
        "common_mistakes": """
- Modelling something that's really an "AND" (always has all these fields) as a DU, or vice versa --
  modelling mutually-exclusive alternatives as a record with lots of "unused when..." fields instead of
  a proper DU.
- Forgetting a case in a `match`, especially after adding a new case to a DU during a multi-part
  question -- always revisit every existing `match` on that type when you extend it.
- Confusing named-field syntax (`Case of name: type`) with tuple-of-types syntax (`Case of type1 *
  type2`) and getting the pattern-matching syntax for one wrong by using the other's style.
- Forgetting `Some`/`Ok` need to be pattern-matched to extract their inner value -- treating an
  `Option<'T>` as if it directly *were* a `'T`.
""",
    },
    "syntax_refs": ["discriminated-union-syntax", "option-type", "result-type"],
}

CONTENT["trees-structures"] = {
    "levels": {
        "what_is_it": """
Trees, tries, and custom linked lists are all built the exact same way: a discriminated union with one
"empty/leaf" case and one "node" case that recursively contains more of the same structure. This is
consistently the exam's biggest single practical section (24-39 marks), usually framed as "design and
implement a tree-shaped data structure", and it's where Discriminated Unions, Recursion, and (often)
Records/Tuples all get combined into one larger problem.
""",
        "syntax": """
```fsharp
// Binary search tree (Week 8)
type tree =
    | Empty
    | Node of tree * int * tree

// Custom linked list (needed whenever a question says "you may not use F#'s built-in list")
type myList =
    | MEmpty
    | MCons of int * myList

// Trie (2024 exam) -- each node has several NAMED children plus a flag
type trie =
    | TrieNode of isWord: bool * a: trie option * b: trie option * c: trie option
```
""",
        "how_it_works": """
**Insertion** into a sorted binary tree recurses down, comparing the new value against the current
node's value, and rebuilds the path it walked with the new value inserted at the correct empty spot:
```fsharp
let rec insertSorted t n =
    match t with
    | Empty -> Node (Empty, n, Empty)
    | Node (l, x, r) when x > n -> Node (insertSorted l n, x, r)
    | Node (l, x, r) -> Node (l, x, insertSorted r n)
```
Because the tree is immutable, "inserting" doesn't mutate anything -- it builds a *new* tree that shares
all the unaffected sub-trees with the old one, only rebuilding the path from the root down to the new
node's position (`insertSorted l n` recurses left, but `x` and `r` are reused unchanged; symmetrically
on the right).

**Flattening** to a sorted list is an in-order traversal: recursively flatten the left sub-tree, put the
node's own value in the middle, recursively flatten the right sub-tree, and join with `@`:
```fsharp
let rec flatten t =
    match t with
    | Empty -> []
    | Node (l, n, r) -> flatten l @ [n] @ flatten r
```
This is **not** tail recursive and involves two recursive calls (not linear recursion at all) -- trees
generally can't be flattened with simple tail recursion the way lists can, because you must combine
*two* recursive results (left and right), not just one.

A **trie** stores strings by sharing common prefixes as a shared path through the tree -- inserting a
word walks/creates one branch per character; searching walks the same path checking each character
exists, and finally checks a per-node "is this the end of a complete word" flag (since a valid word can
also be a *prefix* of a longer stored word, e.g. "do" and "dog" both being valid entries).
""",
        "worked_example": """
```fsharp
// Sort a list by building then flattening a BST (Week 8)
let rec MakeSortedBTree t lis =
    match lis with
    | [] -> t
    | (x::xs) -> MakeSortedBTree (insertSorted t x) xs

let mylist = [8; 3; 7; 5; 2; 1; 9; 4]
let sortedList = flatten (MakeSortedBTree Empty mylist)
```
1. `MakeSortedBTree` folds `insertSorted` over the whole input list, starting from `Empty`, building up
   one tree that contains everything.
2. `flatten` then performs the in-order traversal to read the values back out, in sorted order.
3. This combination (build a BST, then flatten it) *is* an `O(n log n)` average-case sorting algorithm
   -- structurally very similar to quicksort's partition-and-recurse approach, but expressed as
   insert-then-traverse instead.
""",
        "variations": """
- **Compressed BST / mcdTree** (2023 exam / Timed Assignment): each node stores a *list of duplicate
  values* rather than just one value, using your own custom linked list type inside the tree -- combines
  three ideas (BST, custom list, DU) into one structure.
- **Trie / suffix tree** (2024 exam): the "value" domain is characters, not integers, and each node can
  have several children (one per possible next character) rather than exactly two.
- **B3-Tree / ternary tree** (2020 exam): a node can have *three* children and store *two* values,
  generalising the binary case.
- Computing tree **height**, counting internal nodes, or applying a function to every node (a tree
  "map") are all common Week 8 homework variants of the same recursive pattern.

**Supplementary (from the purchased Extra Modules, not part of the official course):** *Learning F#
Functional Data Structures and Algorithms* (Adnan) devotes a whole chapter, 6 ("See the Forest for the
Trees"), specifically to binary search trees in F#, and follow-on chapters cover stacks, queues, and
graphs built the same recursive-DU way -- useful if you want more worked BST examples than the lecture
material alone provides, though none of those further data structures (stacks/queues/graphs) appear in
any supplied exam paper.
""",
        "exam_application": """
This is the exam's largest, most heavily-weighted practical section every single year, and it is
cumulative: part 1 (define the type) is usually worth the fewest marks but everything after depends on
getting it right; parts 2-3 (insert, build-from-list) are usually worth the most (10-14 marks each);
later parts (flatten, count, search, invert) build on the earlier functions. Budget your exam time
accordingly -- this section rewards a clear, correct type definition above almost everything else.
""",
        "common_mistakes": """
- Designing the type before fully reading how the structure's invariants work (e.g. missing that a
  compressed BST node needs a *list* of equal values, not just one int) -- re-read the full description
  before writing the `type` declaration.
- Forgetting that inserting/updating an immutable tree means *rebuilding the path*, not mutating a node
  in place -- code that tries to mutate a `Node`'s fields won't compile (they're not `mutable`).
- Using `@` inside `flatten` when it's on the "hot path" of a large recursive traversal without
  realising the cumulative cost -- for this module's exam-sized examples it's fine and expected, but be
  aware it's not free.
- For tries specifically: forgetting to check the "is this the end of a word" flag, and instead treating
  "the path for these characters exists in the trie" as equivalent to "this exact word was inserted".
""",
    },
    "syntax_refs": ["discriminated-union-syntax", "tree-pattern-match"],
}

CONTENT["oop-fsharp"] = {
    "levels": {
        "what_is_it": """
**Legacy / not seen in the 2020-2024 exam papers supplied.** F# is a .NET language and fully supports
object-oriented programming (classes, inheritance, interfaces) alongside its functional features. This
was covered in the module's own Week 9 notes in an earlier version of the course, but does not appear
in the current Lecture 1-8 slide deck, nor in any of the four exam papers available. It's included here
for completeness and because it's genuinely part of this lecturer's own historical course material --
but you should **not** prioritise it over the core topics above with four weeks to go, unless your
lecturer has told you this year's exam covers it.
""",
        "syntax": """
```fsharp
type Person(n : string, a : int) =
    let mutable age = a
    member this.Name = n
    member this.Age
        with get () = age
        and set (value) = age <- value
    member this.getString = "The person is " + this.Name + " " + this.Age.ToString()
    static member Copy (p : Person) = new Person(p.Name, p.Age)

type Student(n : string, a : int, num : int) =
    inherit Person(n, a)
    member this.StNum = num
```
""",
        "how_it_works": """
The `type Name(params) = ...` syntax declares a class whose constructor parameters are `params`;
`member this.X` declares a property or method, `this` being the instance reference (like `self` in
Python). `let mutable` inside a class body declares real mutable state -- classes are where F# embraces
mutation far more readily than its functional core. `inherit Base(args)` sets up inheritance; marking a
member `abstract` in a base class and `override`/`default` in a derived class gives you polymorphism,
exactly like Java/C#. `[<AbstractClass>]` prevents a type from being instantiated directly, and F#
interfaces (`interface X with ...`) work similarly to C#'s.
""",
        "worked_example": """
```fsharp
let mc = new Person("MC", 24)
let mc2 = new Lecturer("Mathys", 21, 10000.78)     // Lecturer inherits Person
let peopleList : Person list = [mc; mc2 :> Person]  // :> upcasts to the base type
```
`:>` is an explicit upcast (derived type to base type) -- needed here so a list can hold a mix of
`Person` and its subtypes uniformly typed as `Person`.
""",
        "variations": """
Abstract classes (`[<AbstractClass>]`), interfaces (`interface X with member ...`), and combining
inheritance with interface implementation (a class both `inherit`-ing a base class and implementing an
interface) were all shown in the Week 9 notes, mirroring standard OOP feature sets from Java/C#.

**Supplementary (from the purchased Extra Modules, not part of the official course):** *Expert F# 4.0*
(Syme, Granicz & Cisternino) Chapter 6, "Programming with Objects", is a far more thorough treatment of
F# OOP than the Week 9 notes if you want it, covering interfaces, operator overloading, and object
expressions in more depth -- again, purely background, since this isn't in the current course material
or any supplied exam.
""",
        "exam_application": """
**Not present in any of the 4 supplied exam papers (2020, 2022, 2023, 2024).** Treat as background
knowledge only unless your lecturer explicitly tells you otherwise this year -- don't spend limited
study time here before the core topics are solid.
""",
        "common_mistakes": """
Not applicable in the same way as the core topics, since this isn't currently being examined -- if it
does come up, the most likely trip-up is applying F#'s *functional* immutability instincts inside a
class where `mutable` state and `this.Member <- value` are the idiomatic, expected style.
""",
    },
    "syntax_refs": [],
}

CONTENT["async-workflows"] = {
    "levels": {
        "what_is_it": """
**Legacy / not seen in the 2020-2024 exam papers supplied.** `async { ... }` workflows let F# code run
concurrently (e.g. across multiple CPU cores) without manually managing threads. This was covered in the
module's own Week 10 notes but, like OOP, does not appear in the current Lecture 1-8 slide deck or in
any of the four supplied exam papers.
""",
        "syntax": """
```fsharp
let pmatSequential f l = [ for a in l do yield f a ]

let pmatParallel f l =
    [ for a in l do yield async { return f a } ]
    |> Async.Parallel
    |> Async.RunSynchronously   // note: returns an ARRAY, not a list
```
""",
        "how_it_works": """
Wrapping a computation in `async { return ... }` produces an `Async<'T>` *description* of work, not the
result itself -- nothing runs yet. `Async.Parallel` takes a sequence of these descriptions and runs them
concurrently; `Async.RunSynchronously` actually kicks off execution and blocks until every one finishes,
collecting the results into an **array** (accessed with `.[i]`, not F# list syntax).
""",
        "worked_example": """
```fsharp
let stopwatch = System.Diagnostics.Stopwatch.StartNew()
let results = pmatParallel fib [600000000; 600000000; 600000000]
Console.WriteLine(results.[0])
stopwatch.Stop()
Console.WriteLine("Time: " + stopwatch.Elapsed.TotalMilliseconds.ToString())
```
Running the same expensive `fib` computation across several inputs concurrently, rather than one after
another, and timing the difference with a `Stopwatch` -- exactly the demonstration in the Week 10 notes.
""",
        "variations": """
The Week 10 notes show only this one pattern (map a function over a list, sequentially vs. in parallel,
and compare timings) -- there isn't a wider variety of async syntax covered in the supplied material.

**Supplementary (from the purchased Extra Modules, not part of the official course):** *Expert F# 4.0*
(Syme, Granicz & Cisternino) Chapter 11, "Reactive, Asynchronous, and Parallel Programming", and *F# in
Action* (Abraham) Chapter 12, "Asynchronous programming", both cover `async` workflows in much greater
depth (cancellation, error handling, `Async.StartChild`, agents) than the one demonstration in the Week
10 notes -- purely background reading, since this isn't in the current course material or any supplied
exam.
""",
        "exam_application": """
**Not present in any of the 4 supplied exam papers (2020, 2022, 2023, 2024).** Treat as background only.
""",
        "common_mistakes": """
Forgetting `Async.RunSynchronously` returns an array, not a list, if you did decide to use this (e.g.
trying to pattern-match it with `::` the way you would a list).
""",
    },
    "syntax_refs": [],
}


def get_topic(topic_id):
    if topic_id not in TOPICS:
        return None
    meta = TOPICS[topic_id]
    content = CONTENT.get(topic_id, {"levels": {}, "syntax_refs": []})
    return {
        "id": topic_id,
        "title": meta["title"],
        "category": meta["category"],
        "summary": meta["summary"],
        "levels": content["levels"],
        "syntax_refs": content.get("syntax_refs", []),
        "practice_topic_ids": [topic_id],
    }
