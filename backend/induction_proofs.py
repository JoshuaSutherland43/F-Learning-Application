"""
Structural induction proof bank, built directly from the course's real materials:
- Class Exercise / Lecture 7 (reverse(xs@ys) = reverse ys @ reverse xs)
- Lecture 7 Example 1 (associativity of @, i.e. proving Law 5 itself)
- Lecture 7 Example 2 (leng (xs@ys) = leng xs + leng ys)
- Homework Set 7 (sum (xs@ys) = sum xs + sum ys; reverse (reverse xs) = xs)
- Class Test 07 / 2022 exam Q1 (elem e (xs@ys) = elem e xs || elem e ys)
- 2024 exam Q1 (mult xs * mult ys = mult (xs @ ys))

This is the single most exam-heavy, and (per the user's Class Test 7 score of 2/5)
the single weakest, topic -- so it gets a dedicated, carefully-structured engine
rather than generic templating.

Each proof is stored as an ordered list of "chains" (base LHS, base RHS, inductive
LHS, inductive RHS, or a labelled case for proofs needing a case split) where each
chain is a list of (expression, justification) steps. The first element of a chain
is the starting expression (justification None); every subsequent element's
justification explains the rewrite from the previous line.
"""
import random

LAWS = {
    "Law 1": "head (x::xs) = x",
    "Law 2": "tail (x::xs) = xs",
    "Law 3": "[] @ xs = xs",
    "Law 4": "xs @ [] = xs",
    "Law 5": "xs @ (ys @ zs) = (xs @ ys) @ zs   (@ is associative)",
    "Law 6": "(x::xs) @ ys = x :: (xs @ ys)",
    "Law 7": "length (xs @ ys) = length ys + length xs",
    "Law 8": "reverse (reverse xs) = xs",
    "Law 9": "(take n xs) @ (drop n xs) = xs",
    "Law 10": "[x] @ xs = x :: xs",
}

GENERIC_JUSTIFICATIONS = [
    "Inductive Assumption",
    "+ is associative",
    "* is associative",
    "|| is associative / false is its identity",
]


def _func_lines(name, lines):
    return {"name": name, "lines": lines}


PROOFS = {
    "sum-append": {
        "title": "sum (xs @ ys) = sum xs + sum ys",
        "difficulty": 2,
        "func": _func_lines(
            "sum",
            {
                1: "| [] -> 0",
                2: "| (x::xs) -> x + sum xs",
            },
        ),
        "func_code": "let rec sum list =\n    match list with\n    | [] -> 0                    (* Line 1 *)\n    | (x::xs) -> x + sum xs      (* Line 2 *)",
        "statement": "sum (xs @ ys) = sum xs + sum ys",
        "hypothesis": "H(xs): sum (xs @ ys) = sum xs + sum ys",
        "chains": {
            "base_lhs": [("sum ([] @ ys)", None), ("sum ys", "Law 3")],
            "base_rhs": [("sum [] + sum ys", None), ("0 + sum ys", "Line 1 of sum"), ("sum ys", "arithmetic")],
            "ind_lhs": [
                ("sum ((x::xs) @ ys)", None),
                ("sum (x :: (xs @ ys))", "Law 6"),
                ("x + sum (xs @ ys)", "Line 2 of sum"),
                ("x + (sum xs + sum ys)", "Inductive Assumption"),
                ("(x + sum xs) + sum ys", "+ is associative"),
                ("sum (x::xs) + sum ys", "Line 2 of sum"),
            ],
        },
        "case_split": None,
    },
    "leng-append": {
        "title": "leng (xs @ ys) = leng xs + leng ys",
        "difficulty": 2,
        "func": _func_lines(
            "leng",
            {
                1: "| [] -> 0",
                2: "| (_::xs) -> 1 + leng xs",
            },
        ),
        "func_code": "let rec leng list =\n    match list with\n    | [] -> 0                (* Line 1 *)\n    | (_::xs) -> 1 + leng xs  (* Line 2 *)",
        "statement": "leng (xs @ ys) = leng xs + leng ys",
        "hypothesis": "H(xs): leng (xs @ ys) = leng xs + leng ys",
        "chains": {
            "base_lhs": [("leng ([] @ ys)", None), ("leng ys", "Law 3")],
            "base_rhs": [("leng [] + leng ys", None), ("0 + leng ys", "Line 1 of leng"), ("leng ys", "arithmetic")],
            "ind_lhs": [
                ("leng ((x::xs) @ ys)", None),
                ("leng (x :: (xs @ ys))", "Law 6"),
                ("1 + leng (xs @ ys)", "Line 2 of leng"),
                ("1 + (leng xs + leng ys)", "Inductive Assumption"),
            ],
            "ind_rhs": [
                ("leng (x::xs) + leng ys", None),
                ("(1 + leng xs) + leng ys", "Line 2 of leng"),
            ],
        },
        "case_split": None,
    },
    "mult-append": {
        "title": "mult xs * mult ys = mult (xs @ ys)",
        "difficulty": 3,
        "func": _func_lines(
            "mult",
            {
                1: "| [] -> 1",
                2: "| (h::t) -> h * mult t",
            },
        ),
        "func_code": "let rec mult b =\n    match b with\n    | [] -> 1                (* Line 1 *)\n    | (h::t) -> h * mult t   (* Line 2 *)",
        "statement": "mult (xs @ ys) = mult xs * mult ys",
        "hypothesis": "H(xs): mult (xs @ ys) = mult xs * mult ys",
        "chains": {
            "base_lhs": [("mult ([] @ ys)", None), ("mult ys", "Law 3")],
            "base_rhs": [("mult [] * mult ys", None), ("1 * mult ys", "Line 1 of mult"), ("mult ys", "arithmetic")],
            "ind_lhs": [
                ("mult ((x::xs) @ ys)", None),
                ("mult (x :: (xs @ ys))", "Law 6"),
                ("x * mult (xs @ ys)", "Line 2 of mult"),
                ("x * (mult xs * mult ys)", "Inductive Assumption"),
                ("(x * mult xs) * mult ys", "* is associative"),
                ("mult (x::xs) * mult ys", "Line 2 of mult"),
            ],
        },
        "case_split": None,
    },
    "assoc-append": {
        "title": "xs @ (ys @ zs) = (xs @ ys) @ zs   (proving Law 5 itself)",
        "difficulty": 2,
        "func": None,
        "func_code": None,
        "statement": "xs @ (ys @ zs) = (xs @ ys) @ zs",
        "hypothesis": "H(xs): xs @ (ys @ zs) = (xs @ ys) @ zs",
        "chains": {
            "base_lhs": [("[] @ (ys @ zs)", None), ("ys @ zs", "Law 3")],
            "base_rhs": [("([] @ ys) @ zs", None), ("ys @ zs", "Law 3")],
            "ind_lhs": [
                ("(x::xs) @ (ys @ zs)", None),
                ("x :: (xs @ (ys @ zs))", "Law 6"),
                ("x :: ((xs @ ys) @ zs)", "Inductive Assumption"),
                ("(x :: (xs @ ys)) @ zs", "Law 6"),
                ("((x::xs) @ ys) @ zs", "Law 6"),
            ],
        },
        "case_split": None,
    },
    "reverse-append": {
        "title": "reverse (xs @ ys) = reverse ys @ reverse xs",
        "difficulty": 3,
        "func": _func_lines(
            "reverse",
            {
                1: "| [] -> []",
                2: "| (x::xs) -> reverse xs @ [x]",
            },
        ),
        "func_code": "let rec reverse list =\n    match list with\n    | [] -> []                      (* Line 1 *)\n    | (x::xs) -> reverse xs @ [x]   (* Line 2 *)",
        "statement": "reverse (xs @ ys) = reverse ys @ reverse xs",
        "hypothesis": "H(xs): reverse (xs @ ys) = reverse ys @ reverse xs",
        "chains": {
            "base_lhs": [("reverse ([] @ ys)", None), ("reverse ys", "Law 3")],
            "base_rhs": [
                ("reverse ys @ reverse []", None),
                ("reverse ys @ []", "Line 1 of reverse"),
                ("reverse ys", "Law 4"),
            ],
            "ind_lhs": [
                ("reverse ((x::xs) @ ys)", None),
                ("reverse (x :: (xs @ ys))", "Law 6"),
                ("reverse (xs @ ys) @ [x]", "Line 2 of reverse"),
                ("(reverse ys @ reverse xs) @ [x]", "Inductive Assumption"),
                ("reverse ys @ (reverse xs @ [x])", "Law 5"),
                ("reverse ys @ reverse (x::xs)", "Line 2 of reverse"),
            ],
        },
        "case_split": None,
    },
    "reverse-reverse": {
        "title": "reverse (reverse xs) = xs",
        "difficulty": 4,
        "func": _func_lines(
            "reverse",
            {
                1: "| [] -> []",
                2: "| (x::xs) -> reverse xs @ [x]",
            },
        ),
        "func_code": "let rec reverse list =\n    match list with\n    | [] -> []                      (* Line 1 *)\n    | (x::xs) -> reverse xs @ [x]   (* Line 2 *)",
        "statement": "reverse (reverse xs) = xs",
        "hypothesis": "H(xs): reverse (reverse xs) = xs",
        "chains": {
            "base_lhs": [("reverse (reverse [])", None), ("reverse []", "Line 1 of reverse"), ("[]", "Line 1 of reverse")],
            "helper": [
                ("reverse [x]", None),
                ("reverse (x :: [])", "notation"),
                ("reverse [] @ [x]", "Line 2 of reverse"),
                ("[] @ [x]", "Line 1 of reverse"),
                ("[x]", "Law 3"),
            ],
            "ind_lhs": [
                ("reverse (reverse (x::xs))", None),
                ("reverse (reverse xs @ [x])", "Line 2 of reverse"),
                ("reverse [x] @ reverse (reverse xs)", "Lemma L: reverse (xs @ ys) = reverse ys @ reverse xs"),
                ("reverse [x] @ xs", "Inductive Assumption"),
                ("[x] @ xs", "helper fact: reverse [x] = [x]"),
                ("x :: xs", "Law 10"),
            ],
        },
        "case_split": None,
        "note": "Uses Lemma L (reverse (xs @ ys) = reverse ys @ reverse xs), proved separately -- see the reverse-append proof.",
    },
    "elem-append": {
        "title": "elem e (xs @ ys) = elem e xs || elem e ys",
        "difficulty": 5,
        "func": _func_lines(
            "elem",
            {
                1: "| [] -> false",
                2: "| (z::zs) when z = a -> true",
                3: "| (z::zs) -> elem a zs",
            },
        ),
        "func_code": "let rec elem a lis =\n    match lis with\n    | [] -> false                  (* Line 1 *)\n    | (z::zs) when z = a -> true   (* Line 2 *)\n    | (z::zs) -> elem a zs         (* Line 3 *)",
        "statement": "elem e (xs @ ys) = elem e xs || elem e ys",
        "hypothesis": "H(xs): elem e (xs @ ys) = elem e xs || elem e ys",
        "chains": {
            "base_lhs": [("elem e ([] @ ys)", None), ("elem e ys", "Law 3")],
            "base_rhs": [
                ("elem e [] || elem e ys", None),
                ("false || elem e ys", "Line 1 of elem"),
                ("elem e ys", "|| is associative / false is its identity"),
            ],
        },
        "case_split": {
            "note": "The inductive step needs a case split on whether x = e, because elem's recursive case itself branches on that test.",
            "case_x_eq_e": {
                "label": "Case x = e",
                "lhs": [
                    ("elem e ((x::xs) @ ys)", None),
                    ("elem e (x :: (xs @ ys))", "Law 6"),
                    ("true", "Line 2 of elem (since x = e)"),
                ],
                "rhs": [
                    ("elem e (x::xs) || elem e ys", None),
                    ("true || elem e ys", "Line 2 of elem (since x = e)"),
                    ("true", "|| is associative / false is its identity"),
                ],
            },
            "case_x_neq_e": {
                "label": "Case x ≠ e",
                "lhs": [
                    ("elem e ((x::xs) @ ys)", None),
                    ("elem e (x :: (xs @ ys))", "Law 6"),
                    ("elem e (xs @ ys)", "Line 3 of elem (since x ≠ e)"),
                    ("elem e xs || elem e ys", "Inductive Assumption"),
                ],
                "rhs": [
                    ("elem e (x::xs) || elem e ys", None),
                    ("elem e xs || elem e ys", "Line 3 of elem (since x ≠ e)"),
                ],
            },
        },
    },
}


def _all_justification_options(proof):
    """Build a pool of plausible justification distractors for a given proof."""
    opts = set(LAWS.keys()) | set(GENERIC_JUSTIFICATIONS)
    fn = proof.get("func")
    if fn:
        for ln in fn["lines"]:
            opts.add(f"Line {ln} of {fn['name']}")
    opts.add("arithmetic")
    opts.add("notation")
    opts.add("helper fact: reverse [x] = [x]")
    opts.add("Lemma L: reverse (xs @ ys) = reverse ys @ reverse xs")
    return sorted(opts)


CHAIN_LABELS = {
    "base_lhs": "Base case -- LHS",
    "base_rhs": "Base case -- RHS",
    "ind_lhs": "Inductive step -- LHS",
    "ind_rhs": "Inductive step -- RHS",
    "helper": "Helper fact",
}


def list_proof_ids():
    return list(PROOFS.keys())


def generate_proof_question(rng: random.Random, proof_id=None, num_blanks=3, exposure_counts=None):
    if proof_id is None:
        proof_ids = list(PROOFS.keys())
        if exposure_counts and rng.random() < 0.8:
            # 80% novel / 20% deliberate reuse (spec section 10): prefer the least-seen
            # proof(s) most of the time, but occasionally allow any proof to recur --
            # a different random subset of blanks each time keeps it a fresh exercise.
            counts = [exposure_counts.get(pid, 0) for pid in proof_ids]
            min_count = min(counts)
            proof_ids = [pid for pid, c in zip(proof_ids, counts) if c == min_count]
        proof_id = rng.choice(proof_ids)
    proof = PROOFS[proof_id]

    # Flatten all steps (with justification, i.e. skip the first line of each chain)
    # from both the plain chains and any case-split chains, tagging with chain name.
    flat = []  # list of dicts: chain_label, expr, justification, index_in_chain
    if proof.get("case_split") is None:
        for chain_name, steps in proof["chains"].items():
            label = CHAIN_LABELS.get(chain_name, chain_name)
            for i in range(1, len(steps)):
                flat.append(
                    {
                        "chain": chain_name,
                        "chain_label": label,
                        "prev_expr": steps[i - 1][0],
                        "expr": steps[i][0],
                        "justification": steps[i][1],
                    }
                )
    else:
        for chain_name, steps in proof["chains"].items():
            label = CHAIN_LABELS.get(chain_name, chain_name)
            for i in range(1, len(steps)):
                flat.append(
                    {
                        "chain": chain_name,
                        "chain_label": label,
                        "prev_expr": steps[i - 1][0],
                        "expr": steps[i][0],
                        "justification": steps[i][1],
                    }
                )
        cs = proof["case_split"]
        for case_key in ("case_x_eq_e", "case_x_neq_e"):
            case = cs[case_key]
            for side in ("lhs", "rhs"):
                steps = case[side]
                for i in range(1, len(steps)):
                    flat.append(
                        {
                            "chain": f"{case_key}_{side}",
                            "chain_label": f"{case['label']} -- {side.upper()}",
                            "prev_expr": steps[i - 1][0],
                            "expr": steps[i][0],
                            "justification": steps[i][1],
                        }
                    )

    n = min(num_blanks, len(flat))
    blank_indices = sorted(rng.sample(range(len(flat)), n))

    justification_pool = _all_justification_options(proof)
    blank_options = []
    correct_answers = []
    for idx in blank_indices:
        correct = flat[idx]["justification"]
        distractors = [j for j in justification_pool if j != correct]
        rng.shuffle(distractors)
        options = [correct] + distractors[:3]
        rng.shuffle(options)
        blank_options.append(options)
        correct_answers.append(correct)

    # Build a readable, ordered rendering of the whole proof with blanks marked.
    lines = [f"**Statement to prove:** `{proof['statement']}`", ""]
    if proof.get("func_code"):
        lines.append("```fsharp\n" + proof["func_code"] + "\n```")
    lines.append("")
    lines.append(f"**Hypothesis:** {proof['hypothesis']}")
    if proof.get("note"):
        lines.append("")
        lines.append(f"_Note: {proof['note']}_")
    if proof.get("case_split") and proof["case_split"].get("note"):
        lines.append("")
        lines.append(f"_{proof['case_split']['note']}_")
    lines.append("")

    current_chain = None
    blank_num = 0
    for i, step in enumerate(flat):
        if step["chain"] != current_chain:
            current_chain = step["chain"]
            lines.append(f"\n**{step['chain_label']}:**")
            lines.append(f"```\n  {step['prev_expr']}\n```")
        if i in blank_indices:
            blank_num += 1
            lines.append(f"```\n= {step['expr']}      [BLANK {blank_num}]\n```")
        else:
            lines.append(f"```\n= {step['expr']}      ({step['justification']})\n```")

    prompt = "\n".join(lines)

    return {
        "type": "proof_step",
        "topic_id": "induction",
        "difficulty": proof["difficulty"],
        "prompt": prompt,
        # NOTE: func_code (if any) is already embedded as a fenced block inside `prompt`
        # above -- don't also set `code` here, or the frontend renders it a second time.
        "code": None,
        "blanks": [f"blank_{i+1}" for i in range(n)],
        "blank_options": blank_options,
        "meta": {"proof_id": proof_id, "blank_indices": blank_indices, "correct_answers": correct_answers},
    }


def grade_proof_answer(question, answer):
    correct_answers = question["meta"]["correct_answers"]
    if not isinstance(answer, list):
        answer = [answer]
    n = len(correct_answers)
    given = (answer + [None] * n)[:n]
    num_correct = sum(1 for g, c in zip(given, correct_answers) if g == c)
    score = num_correct / n if n else 0.0
    correct = score == 1.0
    proof = PROOFS[question["meta"]["proof_id"]]
    explanation_lines = []
    for i, (g, c) in enumerate(zip(given, correct_answers)):
        mark = "correct" if g == c else f"incorrect (you chose '{g}')"
        explanation_lines.append(f"- Blank {i+1}: correct justification is **{c}** -- {mark}.")
    explanation_lines.append("")
    explanation_lines.append(
        "**Why this matters:** structural induction proofs always follow the same shape -- "
        "prove the base case `H([])` directly, then assume `H(xs)` (the inductive assumption) "
        "and mechanically rewrite one side of `H(x::xs)` using the list laws and the function's "
        "own recursive definition until it matches the other side. The most common mistake is "
        "forgetting that `(x::xs) @ ys` must first be rewritten with **Law 6** before anything "
        "else can be unfolded."
    )
    return {
        "correct": correct,
        "score": score,
        "correct_answer": correct_answers,
        "explanation": "\n".join(explanation_lines),
        "mistake_category": "induction" if not correct else None,
    }
