"""
Lambda calculus engine matching the course's exact conventions (see Old Class Notes
lambdaCalculusLecture1.docx and the exam appendices):

  <expression> ::= <name> | <function> | <application>
  <function>   ::= \\<name>.<expression>          (course writes it as the greek letter lambda)
  <application>::= (<function> <expression>)

Beta reduction: (\\v.body  arg) -> body with free occurrences of v replaced by arg
(with capture-avoiding substitution / alpha-renaming as needed).

The course's own worked examples always reduce the LEFTMOST-OUTERMOST redex first
(normal order), so this engine does the same, and produces a step-by-step trace
that mirrors exam memo style, e.g.:

  (\\s.(s s) \\x.x)
  (\\x.x \\x.x)
  \\x.x

We represent expressions as an AST (Name/Fun/App) rather than raw strings so we can
reliably alpha-rename, compare structurally (for auto-grading), and pretty print in
the course's exact textual style.
"""
import itertools
import re

_id_counter = itertools.count()


class Name:
    __slots__ = ("n",)

    def __init__(self, n):
        self.n = n

    def __eq__(self, o):
        return isinstance(o, Name) and self.n == o.n

    def __repr__(self):
        return self.n


class Fun:
    __slots__ = ("param", "body")

    def __init__(self, param, body):
        self.param = param
        self.body = body

    def __eq__(self, o):
        return isinstance(o, Fun) and alpha_equivalent(self, o)


class App:
    __slots__ = ("fn", "arg")

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __eq__(self, o):
        return isinstance(o, App) and self.fn == o.fn and self.arg == o.arg


# ---------------------------------------------------------------- parsing ----
# Accepts both 'λ' and '\' as the lambda symbol, and '.' as the separator, matching
# the course's notation: \x.x  or  λx.x  and applications written (f a).

TOKEN_RE = re.compile(r"\s*(\(|\)|\.|λ|\\|[A-Za-z_][A-Za-z0-9_']*)")


def tokenize(s):
    pos = 0
    toks = []
    while pos < len(s):
        m = TOKEN_RE.match(s, pos)
        if not m:
            if s[pos].isspace():
                pos += 1
                continue
            raise ValueError(f"Unexpected character {s[pos]!r} at {pos}")
        pos = m.end()
        tok = m.group(1)
        toks.append(tok)
    return toks


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def next(self):
        t = self.peek()
        self.i += 1
        return t

    def expect(self, t):
        got = self.next()
        if got != t:
            raise ValueError(f"Expected {t!r}, got {got!r}")

    def parse_expr(self):
        t = self.peek()
        if t in ("λ", "\\"):
            return self.parse_fun()
        elif t == "(":
            return self.parse_app()
        else:
            return self.parse_name()

    def parse_fun(self):
        self.next()  # lambda symbol
        param = self.next()
        self.expect(".")
        body = self.parse_expr()
        return Fun(param, body)

    def parse_app(self):
        self.expect("(")
        fn = self.parse_expr()
        arg = self.parse_expr()
        self.expect(")")
        return App(fn, arg)

    def parse_name(self):
        t = self.next()
        if t is None or t in (")", "."):
            raise ValueError(f"Expected a name, got {t!r}")
        return Name(t)


def parse(s):
    s = s.strip()
    toks = tokenize(s)
    p = Parser(toks)
    expr = p.parse_expr()
    if p.i != len(toks):
        raise ValueError(f"Trailing tokens after parse: {toks[p.i:]}")
    return expr


# ------------------------------------------------------------- printing ----

def to_str(e):
    if isinstance(e, Name):
        return e.n
    if isinstance(e, Fun):
        return f"\\{e.param}.{to_str(e.body)}"
    if isinstance(e, App):
        return f"({to_str(e.fn)} {to_str(e.arg)})"
    raise TypeError(e)


# --------------------------------------------------------- free vars / subst ----

def free_vars(e):
    if isinstance(e, Name):
        return {e.n}
    if isinstance(e, Fun):
        return free_vars(e.body) - {e.param}
    if isinstance(e, App):
        return free_vars(e.fn) | free_vars(e.arg)
    raise TypeError(e)


def fresh_name(base, avoid):
    n = base
    while n in avoid:
        n = n + "'"
    return n


def substitute(e, var, val):
    """Return e[var := val], capture-avoiding."""
    if isinstance(e, Name):
        return val if e.n == var else e
    if isinstance(e, App):
        return App(substitute(e.fn, var, val), substitute(e.arg, var, val))
    if isinstance(e, Fun):
        if e.param == var:
            return e  # var is shadowed, no substitution inside
        if e.param not in free_vars(val):
            return Fun(e.param, substitute(e.body, var, val))
        # alpha-rename to avoid capture
        avoid = free_vars(val) | free_vars(e.body) | {var}
        new_param = fresh_name(e.param, avoid)
        renamed_body = substitute(e.body, e.param, Name(new_param))
        return Fun(new_param, substitute(renamed_body, var, val))
    raise TypeError(e)


def alpha_equivalent(a, b, mapping=None):
    if mapping is None:
        mapping = {}
    if isinstance(a, Name) and isinstance(b, Name):
        if a.n in mapping:
            return mapping[a.n] == b.n
        return a.n == b.n and a.n not in mapping.values()
    if isinstance(a, Fun) and isinstance(b, Fun):
        m2 = dict(mapping)
        m2[a.param] = b.param
        return alpha_equivalent(a.body, b.body, m2)
    if isinstance(a, App) and isinstance(b, App):
        return alpha_equivalent(a.fn, b.fn, mapping) and alpha_equivalent(a.arg, b.arg, mapping)
    return False


# ----------------------------------------------------------- beta reduction ----

def find_and_reduce_leftmost_outermost(e):
    """Return (reduced_expr, reduced_something: bool). Normal order: leftmost outermost redex."""
    if isinstance(e, App) and isinstance(e.fn, Fun):
        return substitute(e.fn.body, e.fn.param, e.arg), True
    if isinstance(e, App):
        new_fn, changed = find_and_reduce_leftmost_outermost(e.fn)
        if changed:
            return App(new_fn, e.arg), True
        new_arg, changed = find_and_reduce_leftmost_outermost(e.arg)
        if changed:
            return App(e.fn, new_arg), True
        return e, False
    if isinstance(e, Fun):
        new_body, changed = find_and_reduce_leftmost_outermost(e.body)
        if changed:
            return Fun(e.param, new_body), True
        return e, False
    return e, False


def reduce_to_normal_form(expr_str, max_steps=200):
    """Returns list of (step_str) starting with the original expression, each a
    single beta-reduction step, ending at normal form (or stopping at max_steps)."""
    e = parse(expr_str)
    steps = [to_str(e)]
    for _ in range(max_steps):
        new_e, changed = find_and_reduce_leftmost_outermost(e)
        if not changed:
            break
        e = new_e
        steps.append(to_str(e))
    return steps


def normal_form(expr_str, max_steps=200):
    steps = reduce_to_normal_form(expr_str, max_steps)
    return steps[-1]


def normalize_for_comparison(s):
    """Parse then re-print, so equivalent-but-differently-spaced/parenthesised
    strings compare equal; also alpha-normalizes."""
    try:
        e = parse(s.replace("λ", "\\"))
    except Exception:
        return s.strip()
    return to_str(alpha_normalize(e))


_alpha_counter_names = [f"v{i}" for i in range(1, 50)]


def alpha_normalize(e, depth=0):
    """Rename all bound variables to a canonical v1, v2, ... scheme (by binding order)
    so structurally-identical-up-to-renaming expressions produce identical strings."""
    counter = itertools.count(1)
    mapping = {}

    def go(e):
        if isinstance(e, Name):
            return Name(mapping.get(e.n, e.n))
        if isinstance(e, Fun):
            old = mapping.get(e.param)
            new_name = f"v{next(counter)}"
            mapping[e.param] = new_name
            body = go(e.body)
            if old is not None:
                mapping[e.param] = old
            else:
                del mapping[e.param]
            return Fun(new_name, body)
        if isinstance(e, App):
            return App(go(e.fn), go(e.arg))
        raise TypeError(e)

    return go(e)


def expressions_equal(s1, s2):
    try:
        return alpha_equivalent(parse(s1.replace("λ", "\\")), parse(s2.replace("λ", "\\")))
    except Exception:
        return s1.strip() == s2.strip()


# --------------------------------------------------- course's Church encodings ----
# Exactly as given in every exam appendix (2020/2022/2023/2024) and the lecture notes.

CHURCH_DEFS = {
    "True": r"\a.\b.a",
    "False": r"\c.\d.d",
    "Condition": r"\e.\f.\g.((g e) f)",   # (course's most common form: Cond a b cond)
    "Not": r"\h.((h False) True)",
    "And": r"\i.\j.((i j) False)",
    "Or": r"\k.\m.((k True) m)",
}


_CHURCH_AST_CACHE = None


def _church_ast():
    global _CHURCH_AST_CACHE
    if _CHURCH_AST_CACHE is None:
        _CHURCH_AST_CACHE = {k: parse(v) for k, v in CHURCH_DEFS.items()}
    return _CHURCH_AST_CACHE


def expand_defs(expr_str):
    """Replace free occurrences of named defs (True/False/Not/And/Or/Condition)
    with their (parsed) lambda bodies, at the AST level, via capture-avoiding
    substitution -- so definitions nested inside other definitions (e.g. False
    appearing inside And's body) also get expanded correctly. Repeats to a
    fixed point since a def's body may itself mention another def name."""
    e = parse(expr_str.replace("λ", "\\"))
    defs = _church_ast()
    for _ in range(10):
        fv = free_vars(e)
        names_to_expand = [n for n in defs if n in fv]
        if not names_to_expand:
            break
        for name in names_to_expand:
            e = substitute(e, name, defs[name])
    return to_str(e)


MECHANICAL_EXPRESSIONS = [
    r"(\y.y \q.q)",
    r"(\x.x \x.x)",
    r"(\s.(s s) \x.x)",
    r"((\func.\arg.(func arg) \x.x) \s.(s s))",
    r"(\a.\b.a \c.c)",
    r"((\a.\b.a \p.p) \q.q)",
    r"((\x.\y.x \a.a) \b.b)",
    r"(((\x.\y.\z.((x y) z) \d.d) \e.e) \f.f)",
]

BOOLEAN_OPS = ["And", "Or"]


def _random_bool_name(rng):
    return rng.choice(["True", "False"])


def generate_lambda_question(rng, difficulty=None):
    """Returns a dict with: lambda_expr (string, may contain True/False/And/Or/Not
    named defs), prompt (markdown), and meta with the correct normal form + an
    accepted label ("True"/"False") when applicable, plus the full step trace for
    the explanation shown after grading."""
    kind = rng.choice(["mechanical", "boolean_simple", "boolean_nested"])

    if kind == "mechanical":
        expr = rng.choice(MECHANICAL_EXPRESSIONS)
        steps = reduce_to_normal_form(expr, max_steps=30)
        result = steps[-1]
        prompt = "Evaluate the following lambda calculus expression (reduce to normal form, leftmost-outermost):"
        return {
            "lambda_expr": expr,
            "prompt": prompt,
            "difficulty": 3,
            "meta": {"steps": steps, "normal_form": result, "accepted_label": None},
        }

    if kind == "boolean_simple":
        op = rng.choice(BOOLEAN_OPS)
        a = _random_bool_name(rng)
        b = _random_bool_name(rng)
        expr = f"(({op} {a}) {b})"
        evald = eval_boolean_expr(expr)
        prompt = (
            "Using the standard Church encodings (provided every exam), evaluate the expression below. "
            "Give your answer either as the fully-reduced lambda expression, or simply as `True`/`False`."
        )
        return {
            "lambda_expr": expr,
            "prompt": prompt,
            "difficulty": 2,
            "meta": {"steps": evald["steps"], "normal_form": evald["result"], "accepted_label": evald["label"]},
        }

    # boolean_nested: Not (And/Or a b)
    op = rng.choice(BOOLEAN_OPS)
    a = _random_bool_name(rng)
    b = _random_bool_name(rng)
    expr = f"(Not (({op} {a}) {b}))"
    evald = eval_boolean_expr(expr)
    prompt = (
        "Using the standard Church encodings (provided every exam), evaluate the expression below. "
        "Give your answer either as the fully-reduced lambda expression, or simply as `True`/`False`."
    )
    return {
        "lambda_expr": expr,
        "prompt": prompt,
        "difficulty": 4,
        "meta": {"steps": evald["steps"], "normal_form": evald["result"], "accepted_label": evald["label"]},
    }


def grade_lambda_answer(meta, answer):
    answer = (answer or "").strip()
    accepted_label = meta.get("accepted_label")
    normal_form = meta["normal_form"]

    correct = False
    if accepted_label and answer.lower() == accepted_label.lower():
        correct = True
    elif expressions_equal(answer, normal_form):
        correct = True

    steps_md = "\n".join(f"{i+1}. `{s}`" for i, s in enumerate(meta["steps"]))
    label_note = f" (this is Church-encoded **{accepted_label}**)" if accepted_label and accepted_label != "unknown" else ""
    explanation = (
        f"**Full leftmost-outermost reduction:**\n\n{steps_md}\n\n"
        f"**Normal form:** `{normal_form}`{label_note}"
    )
    return {
        "correct": correct,
        "score": 1.0 if correct else 0.0,
        "correct_answer": normal_form if not accepted_label else f"{normal_form}  (i.e. {accepted_label})",
        "explanation": explanation,
        "mistake_category": "lambda-calculus" if not correct else None,
    }


def eval_boolean_expr(expr_with_defs):
    """Expand True/False/And/Or/Not/Condition names, reduce to normal form, and
    classify the result as True/False/unknown (by alpha-equivalence to the
    canonical Church True/False)."""
    expanded = expand_defs(expr_with_defs)
    steps = reduce_to_normal_form(expanded)
    result = steps[-1]
    is_true = expressions_equal(result, CHURCH_DEFS["True"])
    is_false = expressions_equal(result, CHURCH_DEFS["False"])
    label = "True" if is_true else ("False" if is_false else "unknown")
    return {"steps": steps, "result": result, "label": label}
