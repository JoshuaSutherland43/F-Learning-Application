# -*- coding: utf-8 -*-
"""
Question bank: parameterised templates per topic. Each template is a function
(rng) -> question dict (missing 'id'/'meta.seed', which the caller fills in).
Grading info (correct answer / reference solution / expected trace output) is
embedded directly in the question's `meta` and round-tripped by the client --
this is a single-user local study tool, not a shared quiz, so there is no
cheating concern in exposing it, and it keeps the backend fully stateless
between question-generation and answer-submission.
"""
import random
import uuid


def fl(items):
    """Format a Python list/tuple as an F# list literal, e.g. [1,2,3] -> '[1; 2; 3]'.
    Python's str() on a list uses commas, which F# parses as a list-of-one-tuple --
    this must be used anywhere a Python list is interpolated into F# source text.
    Strings are rendered as quoted F# string literals; bools as lowercase true/false."""
    def one(x):
        if isinstance(x, bool):
            return "true" if x else "false"
        if isinstance(x, str):
            return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if isinstance(x, tuple):
            return "(" + ", ".join(one(e) for e in x) + ")"
        if isinstance(x, list):
            return fl(x)
        return str(x)
    return "[" + "; ".join(one(x) for x in items) + "]"


def qid():
    return "q_" + uuid.uuid4().hex[:10]


def mcq(topic, difficulty, prompt, choices, correct_index, explanation, code=None):
    return {
        "type": "mcq", "topic_id": topic, "difficulty": difficulty,
        "prompt": prompt, "code": code, "choices": choices,
        "meta": {"correct_choice": choices[correct_index], "explanation": explanation},
    }


def trace(topic, difficulty, prompt, code, expected, explanation, accept=None):
    return {
        "type": "trace", "topic_id": topic, "difficulty": difficulty,
        "prompt": prompt, "code": code,
        "meta": {"expected": expected, "accept": accept or [expected], "explanation": explanation},
    }


def fill_blank(topic, difficulty, prompt, expected, explanation, accept=None, code=None):
    return {
        "type": "fill_blank", "topic_id": topic, "difficulty": difficulty,
        "prompt": prompt, "code": code,
        "meta": {"expected": expected, "accept": accept or [expected], "explanation": explanation},
    }


def short_answer(topic, difficulty, prompt, expected, explanation, keywords=None):
    return {
        "type": "short_answer", "topic_id": topic, "difficulty": difficulty,
        "prompt": prompt, "code": None,
        "meta": {"expected": expected, "keywords": keywords or [], "explanation": explanation},
    }


def code_write(topic, difficulty, prompt, starter_code, reference_solution, harness, explanation):
    return {
        "type": "code_write", "topic_id": topic, "difficulty": difficulty,
        "prompt": prompt, "starter_code": starter_code,
        "meta": {
            "reference_solution": reference_solution,
            "harness": harness,
            "explanation": explanation,
        },
    }


# ============================================================== intro-fp ====

def t_intro_1(rng):
    return mcq(
        "intro-fp", 1,
        "In F#, once `let x = 5` has executed, what happens if you later write `let x = x + 1` in the same scope?",
        [
            "It mutates x to become 6",
            "It creates a new, separate binding named x (shadowing the old one); the original x=5 still exists underneath",
            "It raises a runtime exception",
            "It is a compile error under all circumstances",
        ],
        1,
        "F# bindings are immutable. `let x = x + 1` does not mutate the original x -- it creates a *new* binding that shadows the old one for the rest of the scope. This is different from assignment in imperative languages.",
    )


def t_intro_2(rng):
    return mcq(
        "intro-fp", 1,
        "Which property means 'an identifier can always be replaced by its value without changing what the program means'?",
        ["Purity", "Referential transparency", "First-class functions", "Immutability"],
        1,
        "Referential transparency: because a bound name never changes, every use of it can be substituted with its value -- exactly like algebra.",
    )


def t_intro_3(rng):
    return mcq(
        "intro-fp", 2,
        "Why must every F# function accept exactly one parameter, even ones that 'look like' they take several?",
        [
            "It's a syntax restriction with no deeper reason",
            "Multi-parameter functions are implemented as a chain of one-parameter functions returning functions (currying)",
            "F# doesn't actually support this -- all functions take a tuple",
            "Only mathematical functions are allowed, and those take one input",
        ],
        1,
        "This is currying: `let g x y = ...` really has type `int -> (int -> int)` -- one parameter, returning a function that takes the next one.",
    )


def t_intro_4(rng):
    return mcq(
        "intro-fp", 1,
        "What does a function that only prints something and does no other computation return in F#?",
        ["null", "void", "unit, written ()", "It doesn't need to return anything"],
        2,
        "Every F# function must return a value; a function whose job is a side effect (like printing) returns `unit`, written `()`.",
    )


def t_intro_5(rng):
    a = rng.randint(2, 9)
    return trace(
        "intro-fp", 1,
        f"What does this evaluate to?\n```fsharp\nlet x = {a}\nlet y = x + 10\nlet x = 99   // shadowing\nprintfn \"%d\" y\n```",
        None, str(a + 10),
        f"`y` was already computed as `x + 10` using the *original* x ({a}), before the shadowing `let x = 99` even happens. Shadowing only affects code written *after* it -- y is unaffected, so y = {a+10}.",
    )


TEMPLATES_INTRO = [t_intro_1, t_intro_2, t_intro_3, t_intro_4, t_intro_5]

# ======================================================= bindings-matching ==

def t_bind_1(rng):
    return mcq(
        "bindings-matching", 1,
        "In `match n with | x when x >= 0 -> x | x -> -1 * x`, what does the `when` clause do?",
        [
            "It's a separate pattern, unrelated to the identifier pattern before it",
            "It adds an extra boolean condition that must ALSO hold for that branch to be chosen, checked after the pattern already matched",
            "It repeats the match for each guard",
            "It's optional syntax with no effect",
        ],
        1,
        "A `when` guard is checked only after its pattern matches. If the guard is false, F# tries the NEXT pattern -- it does not fall through to a default.",
    )


def t_bind_2(rng):
    n = rng.choice([3, 4, 7, 10])
    return trace(
        "bindings-matching", 2,
        f"What is the result of `classify {n}` given:\n```fsharp\nlet classify n =\n    match n with\n    | n when n % 2 = 0 -> \"even\"\n    | n when n % 3 = 0 -> \"div3\"\n    | _ -> \"other\"\n```",
        None,
        ("even" if n % 2 == 0 else ("div3" if n % 3 == 0 else "other")),
        f"{n} is checked against each guard in order. " + (
            f"{n} % 2 = 0 so the first branch matches: \"even\"." if n % 2 == 0 else
            (f"{n} % 2 <> 0, but {n} % 3 = 0, so the second branch matches: \"div3\"." if n % 3 == 0 else
             f"{n} is odd and not divisible by 3, so it falls through to \"other\".")
        ),
    )


def t_bind_3(rng):
    return mcq(
        "bindings-matching", 1,
        "Which of these is legal F#: an `if` expression with no `else` branch?",
        [
            "Never legal",
            "Legal only if the `then` branch has type unit",
            "Legal only inside a match expression",
            "Legal, and returns null if the condition is false",
        ],
        1,
        "`if cond then expr` with no `else` is only valid when `expr : unit`, because the implicit missing else-branch is `()`, and both branches of an if must agree in type.",
    )


def t_bind_4(rng):
    x = rng.randint(1, 20)
    return code_write(
        "bindings-matching", 2,
        f"Write a function `classifyNum` that takes an int `x` and returns the string `\"negative\"` if x < 0, `\"zero\"` if x = 0, and `\"positive\"` otherwise. Use `match ... with ... when`.",
        "let classifyNum x =\n    // TODO\n    \"\"",
        "let referenceClassifyNum x =\n    match x with\n    | x when x < 0 -> \"negative\"\n    | x when x = 0 -> \"zero\"\n    | _ -> \"positive\"",
        harness=(
            "let testInputs = [-5; 0; 7; -1; 100]\n"
            "let mutable allPass = true\n"
            "for v in testInputs do\n"
            "    let expected = referenceClassifyNum v\n"
            "    let actual = classifyNum v\n"
            "    if expected = actual then printfn \"PASS %d\" v\n"
            "    else (allPass <- false; printfn \"FAIL input=%d expected=%s actual=%s\" v expected actual)\n"
        ),
        explanation="A guard-based match cleanly partitions the three cases. Note `_` catches everything left (positive) once negative and zero are handled.",
    )


TEMPLATES_BINDINGS = [t_bind_1, t_bind_2, t_bind_3, t_bind_4]

# ========================================================= recursion-basics =

def t_recb_1(rng):
    return mcq(
        "recursion-basics", 1,
        "What is the compile-time consequence of omitting `rec` from `let factorial n = ... factorial (n-1) ...`?",
        [
            "Nothing, `rec` is optional style",
            "F# infers rec automatically",
            "Compile error: `factorial` is not defined yet inside its own body",
            "It runs but infinitely loops at runtime instead",
        ],
        2,
        "Without `rec`, the name being defined isn't in scope inside its own body yet, so referring to it is a compile-time 'undefined value' error.",
    )


def t_recb_2(rng):
    n = rng.randint(3, 6)
    return trace(
        "recursion-basics", 1,
        f"What does `power 2 {n}` return, given:\n```fsharp\nlet rec power a b =\n    match b with\n    | 0 -> 1\n    | b -> a * power a (b-1)\n```",
        None, str(2 ** n),
        f"power 2 {n} unfolds to 2 * 2 * ... ({n} twos) = {2**n}.",
    )


def t_recb_3(rng):
    return mcq(
        "recursion-basics", 2,
        "A recursive function has a base case that can never actually be reached from any starting input. What happens at runtime?",
        [
            "It returns 0 by default",
            "Infinite recursion, eventually a StackOverflowException",
            "F# detects this at compile time and refuses to compile",
            "It behaves like a tail-recursive loop and runs forever without crashing",
        ],
        1,
        "If the recursive case never actually lands on the base case pattern, calls keep stacking up until the runtime call stack is exhausted.",
    )


def t_recb_amicable(rng):
    a, b = rng.choice([(220, 284), (1184, 1210), (2620, 2924), (6, 6), (28, 28)])
    return code_write(
        "recursion-basics", 3,
        (f"Write a function `isAmicable a b` that returns `true` if `a` and `b` are an amicable pair: "
         f"the sum of the proper divisors of `a` (excluding `a` itself) equals `b`, AND the sum of the "
         f"proper divisors of `b` (excluding `b` itself) equals `a`. (This is the exact Week 1 class exercise.) "
         f"Test it on `isAmicable {a} {b}`."),
        "let isAmicable a b =\n    // TODO: write helper(s) using recursion, no built-in list/sum functions\n    false",
        (
            "let rec sumDivisorsHelper a b =\n"
            "    match b with\n"
            "    | 0 -> 0\n"
            "    | b when a % b = 0 -> b + sumDivisorsHelper a (b-1)\n"
            "    | b -> sumDivisorsHelper a (b-1)\n"
            "let referenceIsAmicable a b =\n"
            "    (sumDivisorsHelper a (a-1) = b) && (sumDivisorsHelper b (b-1) = a)"
        ),
        harness=(
            f"let testPairs = [({a},{b}); ({b},{a}); (12,3); (10,10)]\n"
            "let mutable allPass = true\n"
            "for (x,y) in testPairs do\n"
            "    let expected = referenceIsAmicable x y\n"
            "    let actual = isAmicable x y\n"
            "    if expected = actual then printfn \"PASS %d %d\" x y\n"
            "    else (allPass <- false; printfn \"FAIL input=(%d,%d) expected=%b actual=%b\" x y expected actual)\n"
        ),
        explanation=(
            "A recursive helper walks candidate divisors `b-1, b-2, ..., 1`, summing those that divide `a` "
            "exactly (`a % b = 0`), then checks the sum equals the *other* number, both ways round."
        ),
    )


def t_recb_prime(rng):
    n = rng.choice([17, 18, 27, 29, 49, 97, 100])
    is_p = n > 1 and all(n % d != 0 for d in range(2, int(n ** 0.5) + 1))
    return code_write(
        "recursion-basics", 2,
        f"Write a function `isPrime x` that returns `true` if `x` is a prime number, `false` otherwise, using recursion (no built-in primality helpers). Test on `isPrime {n}`.",
        "let isPrime x =\n    // TODO\n    false",
        (
            "let rec testDivisor x i =\n"
            "    if i >= x then true\n"
            "    elif x % i = 0 then false\n"
            "    else testDivisor x (i+1)\n"
            "let referenceIsPrime x = if x < 2 then false else testDivisor x 2"
        ),
        harness=(
            f"let testInputs = [2; 3; 4; {n}; 1; 97]\n"
            "let mutable allPass = true\n"
            "for v in testInputs do\n"
            "    let expected = referenceIsPrime v\n"
            "    let actual = isPrime v\n"
            "    if expected = actual then printfn \"PASS %d\" v\n"
            "    else (allPass <- false; printfn \"FAIL input=%d expected=%b actual=%b\" v expected actual)\n"
        ),
        explanation="Recurse upward from 2, checking whether any candidate divides x exactly; if we reach x itself without finding one, x is prime. Don't forget x < 2 is not prime.",
    )


TEMPLATES_RECURSION_BASICS = [t_recb_1, t_recb_2, t_recb_3, t_recb_amicable, t_recb_prime]

# ========================================================== recursion-types =

def t_rect_1(rng):
    return mcq(
        "recursion-types", 2,
        "Which best describes BACKWARD recursion?",
        [
            "Work is done before the recursive call, passed forward as an accumulator",
            "Work is done after the recursive call returns, on the way back up the call stack",
            "The function never actually calls itself",
            "It always runs faster than forward recursion",
        ],
        1,
        "Backward recursion does its work on the way back UP the stack, after the recursive call has already returned -- e.g. `x + sum xs` (the `x +` happens after `sum xs` returns).",
    )


def t_rect_2(rng):
    return mcq(
        "recursion-types", 3,
        "A function's recursive call is the very last action performed, with nothing done to its result afterwards. What is this called, and what can the compiler do with it?",
        [
            "Backward recursion; nothing special happens",
            "Tail recursion; the compiler can convert it into a loop (O(1) stack space)",
            "Mutual recursion; requires two functions",
            "Linear recursion; always O(n^2) time",
        ],
        1,
        "This is tail recursion -- since nothing happens after the call returns, the compiler can reuse the current stack frame instead of growing the stack, turning it into an efficient loop.",
    )


def t_rect_3(rng):
    return mcq(
        "recursion-types", 3,
        "`let doubleAll2 list = let rec go xs ys = match xs with | [] -> ys | (x::xs) -> go xs (ys @ [x*2]) in go list []` is tail recursive (O(1) stack), yet it's still O(n^2) overall. Why?",
        [
            "Because `match` is slow",
            "Because `@` (list append) is O(n), so appending inside a loop that runs n times gives O(n^2) total work",
            "Because tail recursion is always O(n^2)",
            "It isn't actually O(n^2), it's O(n)",
        ],
        1,
        "Tail recursion only fixes STACK usage. Total TIME still depends on what work each step does -- and `ys @ [x*2]` is O(n) per step, giving O(n) steps * O(n) work = O(n^2) overall.",
    )


def t_rect_convert_forward(rng):
    base = rng.choice([2, 3, 8, 16])
    x = rng.randint(20, 200)
    def to_base(x, b):
        if x == 0:
            return []
        return to_base(x // b, b) + [x % b]
    expected = to_base(x, base)
    return code_write(
        "recursion-types", 4,
        (f"The following uses BACKWARD recursion:\n```fsharp\nlet rec ConvertToBase x b =\n"
         f"    match x with\n    | 0 -> []\n    | x -> (ConvertToBase (x/b) b) @ [(x % b)]\n```\n"
         f"Rewrite it as `ConvertToBaseFwd x b` using FORWARD, tail recursion with an accumulator "
         f"(build the result with `::`, not `@`, then reverse once at the end if needed). "
         f"Test on `ConvertToBaseFwd {x} {base}`."),
        "let ConvertToBaseFwd x b =\n    // TODO\n    []",
        (
            "let referenceConvertToBaseFwd x b =\n"
            "    let rec go x acc =\n"
            "        if x = 0 then acc\n"
            "        else go (x / b) ((x % b) :: acc)\n"
            "    if x = 0 then [0] else go x []"
        ),
        harness=(
            f"let testCases = [({x},{base}); (0,{base}); (255,16); (10,2)]\n"
            "let mutable allPass = true\n"
            "for (xv, bv) in testCases do\n"
            "    let expected = referenceConvertToBaseFwd xv bv\n"
            "    let actual = ConvertToBaseFwd xv bv\n"
            "    if expected = actual then printfn \"PASS %d %d\" xv bv\n"
            "    else (allPass <- false; printfn \"FAIL input=(%d,%d) expected=%A actual=%A\" xv bv expected actual)\n"
        ),
        explanation=(
            "Forward/tail version: build the accumulator by consing the *new* least-significant digit "
            "onto the FRONT each step -- since we compute digits least-significant-first but want them "
            "printed most-significant-first, consing onto the front naturally reverses them into the "
            "right order without a separate reverse step, unlike the doubleAll-style examples."
        ),
    )


TEMPLATES_RECURSION_TYPES = [t_rect_1, t_rect_2, t_rect_3, t_rect_convert_forward]

# ============================================================ lists-basics ==

def t_listb_1(rng):
    return mcq(
        "lists-basics", 1,
        "Which pattern correctly matches ANY non-empty list, binding its first element and the rest?",
        ["| [] -> ...", "| (h::t) -> ...", "| (h, t) -> ...", "| [h; t] -> ..."],
        1,
        "`(h::t)` uses the cons operator as a pattern: it matches a list with at least one element, `h` the head and `t` the (possibly empty) tail. `[h; t]` would only match a list of EXACTLY two elements.",
    )


def t_listb_2(rng):
    lst = [rng.randint(1, 9) for _ in range(rng.randint(3, 6))]
    return trace(
        "lists-basics", 2,
        f"Given `let rec sum b = match b with | [] -> 0 | (h::t) -> h + sum t`, what is `sum {fl(lst)}`?",
        None, str(sum(lst)),
        f"Each element is added recursively until the base case `[]` contributes 0: {' + '.join(map(str, lst))} = {sum(lst)}.",
    )


def t_listb_3(rng):
    return mcq(
        "lists-basics", 1,
        "What's wrong with `let y = x :: mylist2` if `x` is an `int` and `mylist2` is an `int list`? (Trick question!)",
        [
            "Nothing -- this is perfectly valid",
            "You need `mylist2 :: x` instead (order reversed)",
            "You need `@` instead of `::` since both are lists",
            "`::` can never be used with a named list, only literals",
        ],
        0,
        "This one is actually fine -- `::` needs (element, list) and that's exactly what's supplied. The classic mistake is the REVERSE: `mylist2 :: x`, or `x :: y` where both are elements, e.g. `x :: 3`.",
    )


def t_listb_lastelem(rng):
    lst = [rng.randint(1, 99) for _ in range(rng.randint(3, 6))]
    return code_write(
        "lists-basics", 2,
        f"Write a function `lastElement` that returns the last element of a non-empty list (Lecture 2 Class Exercise #3). Test on `lastElement {fl(lst)}`.",
        "let rec lastElement lis =\n    // TODO\n    0",
        (
            "let rec referenceLastElement lis =\n"
            "    match lis with\n"
            "    | [x] -> x\n"
            "    | (_::xs) -> referenceLastElement xs\n"
            "    | [] -> failwith \"empty\""
        ),
        harness=(
            f"let testCases = [{fl(lst)}; [1]; [7;7;7]]\n"
            "let mutable allPass = true\n"
            "for lis in testCases do\n"
            "    let expected = referenceLastElement lis\n"
            "    let actual = lastElement lis\n"
            "    if expected = actual then printfn \"PASS %A\" lis\n"
            "    else (allPass <- false; printfn \"FAIL input=%A expected=%A actual=%A\" lis expected actual)\n"
        ),
        explanation="Base case is a SINGLE-element list `[x]` (not `[]`!) -- that's the last element. Otherwise recurse on the tail.",
    )


def t_listb_occurrences(rng):
    n = rng.randint(1, 5)
    lst = [rng.randint(1, 5) for _ in range(8)]
    return code_write(
        "lists-basics", 2,
        f"Write a function `numOccur n lis` that returns how many times `n` occurs in list `lis` (Lecture 2 Class Exercise #4). Test on `numOccur {n} {fl(lst)}`.",
        "let rec numOccur n lis =\n    // TODO\n    0",
        (
            "let rec referenceNumOccur n lis =\n"
            "    match lis with\n"
            "    | [] -> 0\n"
            "    | (x::xs) -> (if x = n then 1 else 0) + referenceNumOccur n xs"
        ),
        harness=(
            f"let testCases = [({n}, {fl(lst)}); (9, {fl(lst)}); (0, [])]\n"
            "let mutable allPass = true\n"
            "for (nv, lis) in testCases do\n"
            "    let expected = referenceNumOccur nv lis\n"
            "    let actual = numOccur nv lis\n"
            "    if expected = actual then printfn \"PASS %d %A\" nv lis\n"
            "    else (allPass <- false; printfn \"FAIL input=(%d,%A) expected=%d actual=%d\" nv lis expected actual)\n"
        ),
        explanation="Standard list-recursion accumulator pattern: add 1 when the head matches, 0 otherwise, plus the recursive count over the tail.",
    )


def t_listb_takedrop(rng):
    n = rng.randint(1, 4)
    lst = [rng.randint(1, 9) for _ in range(6)]
    return code_write(
        "lists-basics", 3,
        f"Write a function `take n lis` that returns the first `n` elements of `lis` (or the whole list if it has fewer than `n` elements), matching on the tuple `(n, lis)`. Test on `take {n} {fl(lst)}`.",
        "let rec take n lis =\n    // TODO\n    []",
        (
            "let rec referenceTake n lis =\n"
            "    match (n, lis) with\n"
            "    | (0, _) -> []\n"
            "    | (_, []) -> []\n"
            "    | (n, (x::xs)) -> x :: referenceTake (n-1) xs"
        ),
        harness=(
            f"let testCases = [({n}, {fl(lst)}); (0, {fl(lst)}); (100, {fl(lst)})]\n"
            "let mutable allPass = true\n"
            "for (nv, lis) in testCases do\n"
            "    let expected = referenceTake nv lis\n"
            "    let actual = take nv lis\n"
            "    if expected = actual then printfn \"PASS %d %A\" nv lis\n"
            "    else (allPass <- false; printfn \"FAIL input=(%d,%A) expected=%A actual=%A\" nv lis expected actual)\n"
        ),
        explanation="Matching the TUPLE (n, lis) lets you cleanly express both base cases (n=0, or list exhausted) before the general recursive case.",
    )


TEMPLATES_LISTS_BASICS = [t_listb_1, t_listb_2, t_listb_3, t_listb_lastelem, t_listb_occurrences, t_listb_takedrop]

# =================================================== higher-order-currying ==

def t_hoc_1(rng):
    return mcq(
        "higher-order-currying", 2,
        "What is the type of `g` given `let g x y = x + y + 1` (where + is used on ints)?",
        ["int * int -> int", "int -> int -> int", "(int, int) -> int", "int list -> int"],
        1,
        "Every 'multi-parameter' function is curried: `g` takes one int and returns a function `int -> int`, overall written `int -> int -> int` (right-associative, i.e. `int -> (int -> int)`).",
    )


def t_hoc_2(rng):
    a = rng.randint(2, 5)
    return trace(
        "higher-order-currying", 2,
        f"Given `let mult a b = a * b` and `let double = mult {a}`, what does `double 10` evaluate to?",
        None, str(a * 10),
        f"`double` is `mult {a}` partially applied -- a function still waiting for one more argument. `double 10` = `mult {a} 10` = {a*10}.",
    )


def t_hoc_3_fixed(rng):
    x = rng.randint(1, 5)
    add_amt = rng.randint(1, 5)
    g_result = x + add_amt
    f_result = g_result * g_result

    correct = f_result
    candidates = [
        (x * x) + add_amt,               # wrong order: g(f(x)) style slip
        x * x + add_amt * add_amt,       # squares both then adds
        x + add_amt * add_amt,           # only squares add_amt
        g_result + g_result,             # doubles instead of squares
        g_result * 2,
        f_result + 1,
        f_result - 1,
    ]
    distractors = []
    seen = {correct}
    for c in candidates:
        if c not in seen:
            distractors.append(c)
            seen.add(c)
        if len(distractors) == 3:
            break
    choices = [str(correct)] + [str(d) for d in distractors]
    rng.shuffle(choices)
    correct_index = choices.index(str(correct))

    return mcq(
        "higher-order-currying", 3,
        f"Given `let f x = x * x` and `let g x = x + {add_amt}`, what does `(f << g) {x}` evaluate to?",
        choices, correct_index,
        f"`f << g` applied to {x} means `f (g {x}))`: first g: {x}+{add_amt}={g_result}, then f: {g_result}*{g_result}={f_result}. (`f << g` reads right-to-left: g runs first.)",
    )


def t_hoc_pipeline(rng):
    x = rng.randint(2, 6)
    return trace(
        "higher-order-currying", 2,
        f"What does this evaluate to?\n```fsharp\nlet square x = x * x\nlet add5 x = x + 5\nlet result = {x} |> square |> add5\n```",
        None, str(x * x + 5),
        f"`|>` feeds the left value as input to the right function, left to right: {x} |> square = {x*x}, then {x*x} |> add5 = {x*x+5}.",
    )


def t_hoc_composition_write(rng):
    return code_write(
        "higher-order-currying", 3,
        "Write `applyTwice f x` which applies function `f` to `x` twice (i.e. `f (f x)`), using currying/higher-order style (f is a parameter). Test with `f = (fun n -> n * 2)`, `x = 3`.",
        "let applyTwice f x =\n    // TODO\n    x",
        "let referenceApplyTwice f x = f (f x)",
        harness=(
            "let testFn = (fun n -> n * 2)\n"
            "let testInputs = [3; 0; -4; 10]\n"
            "let mutable allPass = true\n"
            "for v in testInputs do\n"
            "    let expected = referenceApplyTwice testFn v\n"
            "    let actual = applyTwice testFn v\n"
            "    if expected = actual then printfn \"PASS %d\" v\n"
            "    else (allPass <- false; printfn \"FAIL input=%d expected=%d actual=%d\" v expected actual)\n"
        ),
        explanation="Since f is just a value (first-class function), `f (f x)` applies it, takes the result, and applies it again.",
    )


TEMPLATES_HOC = [t_hoc_1, t_hoc_2, t_hoc_3_fixed, t_hoc_pipeline, t_hoc_composition_write]

# ======================================================= tuples-records ====

def t_tup_1(rng):
    return mcq(
        "tuples-records", 1,
        "What is the type of `(5, \"hi\", true)`?",
        ["int, string, bool", "int * string * bool", "int -> string -> bool", "tuple<int,string,bool>"],
        1,
        "Tuple types are written with `*` between the field types: `int * string * bool`.",
    )


def t_tup_2(rng):
    return mcq(
        "tuples-records", 2,
        "What does `{ p with age = 30 }` do, if `p` is a record value?",
        [
            "Mutates p's age field to 30",
            "Creates a brand-new record, copying every field from p except age, which becomes 30",
            "Is a compile error -- records can't be updated",
            "Deletes all fields except age",
        ],
        1,
        "Records are immutable; `{ p with ... }` always builds a new value. `p` itself is never changed.",
    )


def t_tup_sumprod(rng):
    lst = [rng.randint(1, 5) for _ in range(rng.randint(3, 5))]
    prod = 1
    for v in lst:
        prod *= v
    return code_write(
        "tuples-records", 3,
        (f"Write a function `sumProd lis` that returns a tuple `(sum, product)` of all the ints in `lis`, "
         f"in a SINGLE recursive pass (Week 5 class exercise). Test on `sumProd {fl(lst)}`."),
        "let rec sumProd lis =\n    // TODO\n    (0, 1)",
        (
            "let rec referenceSumProd lis =\n"
            "    match lis with\n"
            "    | [] -> (0, 1)\n"
            "    | (x::xs) ->\n"
            "        let (s, p) = referenceSumProd xs\n"
            "        (x + s, x * p)"
        ),
        harness=(
            f"let testCases = [{fl(lst)}; [1]; [2;2;2]]\n"
            "let mutable allPass = true\n"
            "for lis in testCases do\n"
            "    let expected = referenceSumProd lis\n"
            "    let actual = sumProd lis\n"
            "    if expected = actual then printfn \"PASS %A\" lis\n"
            "    else (allPass <- false; printfn \"FAIL input=%A expected=%A actual=%A\" lis expected actual)\n"
        ),
        explanation="Base case (0,1) are the identities for +/*. Recurse once, destructure the pair, combine x into both sum and product from that SAME call (single pass, not two separate recursive calls).",
    )


def t_tup_record_filter(rng):
    # NOTE: starter_code declares `type product` itself, so the grading harness must NOT
    # declare its own copy (F# records/DUs are nominal types -- two separately-declared
    # `type product` would be incompatible even if structurally identical, and simply
    # redeclaring the name is a compile error outright). Expected results are precomputed
    # in Python and embedded as literals; the harness only ever touches the student's
    # own type and functions.
    sample = [("A", 54.00), ("B", 85.99), ("C", 12.50), ("D", 125.00)]
    thresholds = [50.0, 0.0, 200.0]
    expected_per_threshold = [[n for n, p in sample if p > t] for t in thresholds]
    return code_write(
        "tuples-records", 3,
        (
            "Given:\n```fsharp\ntype product = { name : string; price : float }\n```\n"
            "Write a function `filterAbove threshold products` that returns the sub-list of products whose "
            "price is greater than `threshold` (2024-exam-style records question). Do not use `List.filter`."
        ),
        "type product = { name : string; price : float }\nlet rec filterAbove threshold products =\n    // TODO\n    []",
        None,
        harness=(
            "let sample = [ {name=\"A\"; price=54.00}; {name=\"B\"; price=85.99}; {name=\"C\"; price=12.50}; {name=\"D\"; price=125.00} ]\n"
            f"let testCases = {fl(thresholds)}\n"
            f"let expectedNames = {fl(expected_per_threshold)}\n"
            "let mutable allPass = true\n"
            "for (t, expNames) in List.zip testCases expectedNames do\n"
            "    let actual = filterAbove t sample |> List.map (fun p -> p.name)\n"
            "    if expNames = actual then printfn \"PASS %f\" t\n"
            "    else (allPass <- false; printfn \"FAIL input=%f expected=%A actual=%A\" t expNames actual)\n"
        ),
        explanation="Standard list recursion, but the predicate looks at a record field (`p.price`) rather than the element itself directly.",
    )


TEMPLATES_TUPLES_RECORDS = [t_tup_1, t_tup_2, t_tup_sumprod, t_tup_record_filter]

# ====================================================== lists-continued ====

def t_lc_1(rng):
    return trace(
        "lists-continued", 1,
        "What does `[ for x in 1 .. 5 do if x % 2 = 0 then yield x * x ]` evaluate to?",
        None, "[4; 16]",
        "Only even x in 1..5 are 2 and 4; their squares are 4 and 16 -- so the result is [4; 16].",
    )


def t_lc_2(rng):
    return mcq(
        "lists-continued", 2,
        "What's the difference between `yield` and `yield!` inside a list comprehension?",
        [
            "No difference, purely stylistic",
            "`yield` adds one element per iteration; `yield!` splices in a whole list, flattening it",
            "`yield!` is faster but otherwise identical",
            "`yield!` is only for strings",
        ],
        1,
        "`yield! subList` merges every element of subList directly into the result (flattening), whereas `yield subList` would add the WHOLE LIST as a single nested element.",
    )


def t_lc_pythagorean(rng):
    limit = rng.choice([15, 20, 25])
    triples = [(a, b, c) for a in range(1, limit+1) for b in range(a, limit+1) for c in range(b, limit+1) if a*a+b*b == c*c]
    return code_write(
        "lists-continued", 3,
        (f"Using list comprehensions, write `pythagoreanTriples limit` that returns all triples (a,b,c) with "
         f"1 <= a <= b <= c <= limit and a^2+b^2=c^2 (2022-exam-style question). Test on `pythagoreanTriples {limit}`."),
        "let pythagoreanTriples limit =\n    // TODO\n    []",
        (
            "let referencePythagoreanTriples limit =\n"
            "    [ for a in 1 .. limit do\n"
            "        for b in a .. limit do\n"
            "          for c in b .. limit do\n"
            "            if a*a + b*b = c*c then yield (a, b, c) ]"
        ),
        harness=(
            f"let testCases = [{limit}; 5; 30]\n"
            "let mutable allPass = true\n"
            "for lim in testCases do\n"
            "    let expected = referencePythagoreanTriples lim |> List.sort\n"
            "    let actual = pythagoreanTriples lim |> List.sort\n"
            "    if expected = actual then printfn \"PASS %d\" lim\n"
            "    else (allPass <- false; printfn \"FAIL input=%d expected=%A actual=%A\" lim expected actual)\n"
        ),
        explanation="Triple-nested comprehension generates all ordered triples; the `if` condition inside filters to only the ones satisfying the Pythagorean equation.",
    )


def t_lc_factors(rng):
    n = rng.choice([12, 18, 24, 30, 36])
    factors = [d for d in range(1, n + 1) if n % d == 0]
    return code_write(
        "lists-continued", 2,
        f"Using a list comprehension, write `factorsOf n` returning all factors of `n` in ascending order (2022-exam-style). Test on `factorsOf {n}`.",
        "let factorsOf n =\n    // TODO\n    []",
        "let referenceFactorsOf n = [ for d in 1 .. n do if n % d = 0 then yield d ]",
        harness=(
            f"let testCases = [{n}; 1; 17]\n"
            "let mutable allPass = true\n"
            "for v in testCases do\n"
            "    let expected = referenceFactorsOf v\n"
            "    let actual = factorsOf v\n"
            "    if expected = actual then printfn \"PASS %d\" v\n"
            "    else (allPass <- false; printfn \"FAIL input=%d expected=%A actual=%A\" v expected actual)\n"
        ),
        explanation="Iterate d from 1 to n, keeping only those that divide n exactly -- the comprehension's `if` does the filtering inline.",
    )


TEMPLATES_LISTS_CONTINUED = [t_lc_1, t_lc_2, t_lc_pythagorean, t_lc_factors]

# =================================================== discriminated-unions ==

def t_du_1(rng):
    return mcq(
        "discriminated-unions", 1,
        "Which best describes a discriminated union?",
        [
            "A type that always has ALL of its fields at once (an 'AND' type)",
            "A type whose value is EXACTLY ONE of a fixed set of named alternatives (an 'OR' type), each optionally carrying data",
            "Another name for a tuple",
            "A mutable class hierarchy",
        ],
        1,
        "DUs model mutually-exclusive alternatives -- exactly one case is 'active' for any given value, unlike a record/tuple which always has every field.",
    )


def t_du_2(rng):
    return mcq(
        "discriminated-unions", 2,
        "Given `type shape = | Circle of float | Rectangle of float * float`, which correctly matches a Rectangle and computes its area?",
        [
            "| Rectangle w h -> w * h",
            "| Rectangle (w, h) -> w * h",
            "| Rectangle w -> w * w",
            "| Rectangle -> 0.0",
        ],
        1,
        "A case with multiple unnamed fields (`float * float`) is matched with a tuple pattern: `Rectangle (w, h)`.",
    )


def t_du_switch(rng):
    return code_write(
        "discriminated-unions", 2,
        (
            "Given (Lecture 8):\n```fsharp\ntype switchState =\n    | On\n    | Off\n    | Adjustable of float\n```\n"
            "Write `isOn state` that returns `true` for `On`, `true` for `Adjustable b` when `b > 0.0`, and `false` otherwise."
        ),
        "type switchState =\n    | On\n    | Off\n    | Adjustable of float\nlet isOn state =\n    // TODO\n    false",
        None,  # starter_code already declares switchState -- don't redeclare it in a reference solution
        harness=(
            "let testCases = [On; Off; Adjustable 0.5; Adjustable 0.0; Adjustable -0.2]\n"
            "let expected =    [true; false;      true;         false;       false]\n"
            "let mutable allPass = true\n"
            "for (s, exp) in List.zip testCases expected do\n"
            "    let actual = isOn s\n"
            "    if exp = actual then printfn \"PASS %A\" s\n"
            "    else (allPass <- false; printfn \"FAIL input=%A expected=%b actual=%b\" s exp actual)\n"
        ),
        explanation="Every case must be handled explicitly; `Adjustable b` binds the float payload so its value can be tested.",
    )


TEMPLATES_DU = [t_du_1, t_du_2, t_du_switch]

# ===================================================== trees-structures ====

def t_tree_1(rng):
    return mcq(
        "trees-structures", 2,
        "Given `type tree = | Empty | Node of tree * int * tree`, why is `flatten` (in-order traversal to a sorted list) not tail recursive?",
        [
            "It doesn't use `rec`",
            "It makes TWO recursive calls (left and right sub-trees) that both must complete before being combined with `@`, so neither call is 'the last action alone'",
            "Trees can never be traversed recursively",
            "It actually IS tail recursive",
        ],
        1,
        "Tail recursion requires a SINGLE recursive call as the very last action. Combining two recursive results (`flatten l @ [n] @ flatten r`) inherently needs both to finish first -- this is not linear recursion at all.",
    )


def t_tree_insert(rng):
    vals = [rng.randint(1, 50) for _ in range(6)]

    def insert(t, n):
        if t is None:
            return (None, n, None)
        l, x, r = t
        if n < x:
            return (insert(l, n), x, r)
        else:
            return (l, x, insert(r, n))

    def flatten(t):
        if t is None:
            return []
        l, x, r = t
        return flatten(l) + [x] + flatten(r)

    tree = None
    for v in vals:
        tree = insert(tree, v)
    expected_sorted = flatten(tree)

    return code_write(
        "trees-structures", 3,
        (
            "Given (Week 8):\n```fsharp\ntype tree =\n    | Empty\n    | Node of tree * int * tree\n```\n"
            f"Write `insertSorted t n` (inserts n keeping the tree sorted, duplicates go right) and `flatten t` "
            f"(returns the sorted, in-order list of all values). Build a tree by folding insertSorted over "
            f"{fl(vals)} starting from Empty, then flatten it; it should equal `{fl(expected_sorted)}`."
        ),
        (
            "type tree =\n    | Empty\n    | Node of tree * int * tree\n"
            "let rec insertSorted t n =\n    // TODO\n    Empty\n"
            "let rec flatten t =\n    // TODO\n    []"
        ),
        None,  # starter_code already declares `tree` -- don't redeclare it in a reference solution
        harness=(
            f"let vals = {fl(vals)}\n"
            "let userTree = List.fold insertSorted Empty vals\n"
            "let actual = flatten userTree\n"
            f"let expected = {fl(expected_sorted)}\n"
            "if expected = actual then printfn \"PASS %A\" vals\n"
            "else printfn \"FAIL input=%A expected=%A actual=%A\" vals expected actual\n"
        ),
        explanation="insertSorted rebuilds only the path from the root to the new node's spot; flatten does an in-order traversal (left, value, right) to read values back out sorted.",
    )


TEMPLATES_TREES = [t_tree_1, t_tree_insert]

# ============================================================ legacy topics =

def t_oop_1(rng):
    return mcq(
        "oop-fsharp", 1,
        "(Legacy topic -- not seen in any supplied exam paper.) What does `inherit Person(n, a)` do inside a derived class declaration?",
        ["Nothing, it's a comment", "Calls the base class's constructor with those arguments, establishing inheritance", "Declares an interface", "Copies Person's fields by value only, no relationship retained"],
        1,
        "`inherit BaseClass(args)` sets up the class hierarchy and initialises the base part of the object.",
    )


def t_async_1(rng):
    return mcq(
        "async-workflows", 1,
        "(Legacy topic -- not seen in any supplied exam paper.) What does `Async.RunSynchronously` return when applied after `Async.Parallel`?",
        ["A list", "An array", "A single value", "A tuple"],
        1,
        "The Week 10 notes explicitly point out the result is an ARRAY, accessed with `.[i]`, not F# list syntax.",
    )


TEMPLATES_LEGACY = {"oop-fsharp": [t_oop_1], "async-workflows": [t_async_1]}

# ============================================================ registry =====

TEMPLATE_REGISTRY = {
    "intro-fp": TEMPLATES_INTRO,
    "bindings-matching": TEMPLATES_BINDINGS,
    "recursion-basics": TEMPLATES_RECURSION_BASICS,
    "recursion-types": TEMPLATES_RECURSION_TYPES,
    "lists-basics": TEMPLATES_LISTS_BASICS,
    "higher-order-currying": TEMPLATES_HOC,
    "tuples-records": TEMPLATES_TUPLES_RECORDS,
    "lists-continued": TEMPLATES_LISTS_CONTINUED,
    "discriminated-unions": TEMPLATES_DU,
    "trees-structures": TEMPLATES_TREES,
    "oop-fsharp": TEMPLATES_LEGACY["oop-fsharp"],
    "async-workflows": TEMPLATES_LEGACY["async-workflows"],
}

ALL_GENERIC_TOPICS = list(TEMPLATE_REGISTRY.keys())


def pick_template_with_exposure(rng, templates, exposure_counts):
    """80% novel practice / 20% deliberate reuse (spec section 10): four times out of
    five, prefer whichever template(s) this user has seen least so far (ties broken
    randomly); the rest of the time, pick uniformly at random from everything,
    deliberately allowing an already-seen template to come up again -- with new
    randomised values each time, so it's a fresh instance of a familiar objective,
    not a verbatim repeat."""
    if not exposure_counts:
        return rng.choice(templates)
    if rng.random() < 0.8:
        counts = [exposure_counts.get(t.__name__, 0) for t in templates]
        min_count = min(counts)
        least_exposed = [t for t, c in zip(templates, counts) if c == min_count]
        return rng.choice(least_exposed)
    return rng.choice(templates)


def generate_generic_question(rng, topic_id, exposure_counts=None):
    templates = TEMPLATE_REGISTRY.get(topic_id)
    if not templates:
        return None
    template_fn = pick_template_with_exposure(rng, templates, exposure_counts)
    q = template_fn(rng)
    while q is None:
        template_fn = pick_template_with_exposure(rng, templates, exposure_counts)
        q = template_fn(rng)
    q["id"] = qid()
    q.setdefault("choices", None)
    q.setdefault("blanks", None)
    q.setdefault("blank_options", None)
    q.setdefault("starter_code", None)
    q.setdefault("lambda_expr", None)
    q["meta"]["template_name"] = template_fn.__name__
    return q
