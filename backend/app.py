# -*- coding: utf-8 -*-
import sys
import os
import random
import uuid
import datetime

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.stderr.reconfigure(encoding="utf-8") if hasattr(sys.stderr, "reconfigure") else None

from flask import Flask, jsonify, request, send_from_directory

import curriculum
import syntax_reference
import questions as Q
import induction_proofs as IP
import lambda_calc as LC
import db
from fsharp_runner import run_fsharp, grade_code_write

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
db.init_db()

EXAM_STORE = {}  # exam_id -> {"questions": [...], "mode":..., "duration_minutes":...}


# ------------------------------------------------------------------ static --

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    full = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


# --------------------------------------------------------------- curriculum -

@app.route("/api/curriculum")
def api_curriculum():
    return jsonify(curriculum.curriculum_summary())


@app.route("/api/topic/<topic_id>")
def api_topic(topic_id):
    t = curriculum.get_topic(topic_id)
    if not t:
        return jsonify({"error": f"Unknown topic '{topic_id}'"}), 404
    return jsonify(t)


@app.route("/api/syntax")
def api_syntax():
    return jsonify({"entries": syntax_reference.get_syntax_entries()})


# ---------------------------------------------------------------- questions -

INDUCTION_TOPIC = "induction"
LAMBDA_TOPIC = "lambda-calculus"

ALL_CORE_TOPICS = [t["id"] for t in curriculum.TOPIC_META if t["category"] == "core"]


def _fill_common_fields(q):
    q.setdefault("id", "q_" + uuid.uuid4().hex[:10])
    q.setdefault("code", None)
    q.setdefault("choices", None)
    q.setdefault("blanks", None)
    q.setdefault("blank_options", None)
    q.setdefault("starter_code", None)
    q.setdefault("lambda_expr", None)
    q.setdefault("meta", {})
    return q


def build_question_for_topic(rng, topic_id, difficulty=None):
    """Spec section 10 (80% novel practice / 20% deliberate reuse): each call looks up
    how many times this user has already seen each candidate question template/proof
    under this topic, and biases selection towards whichever they've seen least --
    while still allowing an already-seen one to come up ~20% of the time, since exam
    questions/concepts legitimately do recur. Exposure is tracked per (topic, template
    or proof id), not per exact parameter values, since those are randomised fresh
    every time regardless."""
    if topic_id == INDUCTION_TOPIC:
        exposure = db.get_exposure_counts(INDUCTION_TOPIC)
        q = IP.generate_proof_question(rng, num_blanks=rng.choice([2, 3, 3, 4]), exposure_counts=exposure)
        q["id"] = "q_" + uuid.uuid4().hex[:10]
        db.bump_exposure(INDUCTION_TOPIC, q["meta"]["proof_id"])
        return _fill_common_fields(q)
    if topic_id == LAMBDA_TOPIC:
        lq = LC.generate_lambda_question(rng)
        q = {
            "type": "lambda_reduce",
            "topic_id": LAMBDA_TOPIC,
            "difficulty": lq["difficulty"],
            "prompt": lq["prompt"],
            "lambda_expr": lq["lambda_expr"],
            "meta": lq["meta"],
        }
        return _fill_common_fields(q)
    exposure = db.get_exposure_counts(topic_id)
    q = Q.generate_generic_question(rng, topic_id, exposure_counts=exposure)
    if q is None:
        return None
    db.bump_exposure(topic_id, q["meta"]["template_name"])
    return _fill_common_fields(q)


def pick_weakness_topic():
    stats = db.get_topic_stats()
    candidates = []
    for tid in ALL_CORE_TOPICS:
        row = stats.get(tid)
        if not row or row["attempted"] == 0:
            candidates.append((tid, -1))  # untouched topics are prioritised too, but slightly less than weak ones
        else:
            accuracy = row["correct"] / row["attempted"]
            candidates.append((tid, accuracy))
    # weakest-accuracy first; untouched (-1) sorts even before 0% since arguably unknown risk,
    # but we prefer genuinely-attempted-and-weak topics slightly higher than never-tried ones
    candidates.sort(key=lambda x: (x[1] if x[1] >= 0 else 0.05))
    return candidates[0][0] if candidates else rng_default_topic()


def rng_default_topic():
    return random.choice(ALL_CORE_TOPICS)


@app.route("/api/question")
def api_question():
    mode = request.args.get("mode", "practice")
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty", type=int)
    rng = random.Random()

    if mode == "weakness" or (mode == "explore" and not topic):
        topic = pick_weakness_topic()
    elif not topic:
        topic = rng_default_topic()

    if topic not in [t["id"] for t in curriculum.TOPIC_META]:
        return jsonify({"error": f"Unknown topic '{topic}'"}), 400

    q = build_question_for_topic(rng, topic, difficulty)
    if q is None:
        return jsonify({"error": f"No questions available for topic '{topic}'"}), 404

    return jsonify(q)


# ------------------------------------------------------------------ answers -

def grade_question(question, answer):
    qtype = question["type"]
    meta = question.get("meta", {})

    if qtype == "mcq":
        correct = (answer == meta.get("correct_choice"))
        return {
            "correct": correct,
            "score": 1.0 if correct else 0.0,
            "correct_answer": meta.get("correct_choice"),
            "explanation": meta.get("explanation", ""),
            "mistake_category": _guess_mistake_category(question) if not correct else None,
            "run_result": None,
        }

    if qtype in ("trace", "fill_blank"):
        accept = [a.strip().lower() for a in meta.get("accept", [meta.get("expected", "")])]
        given = (answer or "").strip().lower()
        correct = given in accept
        return {
            "correct": correct,
            "score": 1.0 if correct else 0.0,
            "correct_answer": meta.get("expected"),
            "explanation": meta.get("explanation", ""),
            "mistake_category": _guess_mistake_category(question) if not correct else None,
            "run_result": None,
        }

    if qtype == "short_answer":
        given = (answer or "").strip().lower()
        keywords = meta.get("keywords", [])
        if keywords:
            hits = sum(1 for k in keywords if k.lower() in given)
            score = hits / len(keywords) if keywords else 0.0
            correct = "partial" if 0 < score < 1.0 else (score >= 1.0)
        else:
            correct = given == (meta.get("expected") or "").strip().lower()
            score = 1.0 if correct else 0.0
        return {
            "correct": correct,
            "score": score,
            "correct_answer": meta.get("expected"),
            "explanation": meta.get("explanation", ""),
            "mistake_category": None if correct is True else _guess_mistake_category(question),
            "run_result": None,
        }

    if qtype == "proof_step":
        result = IP.grade_proof_answer(question, answer)
        result["run_result"] = None
        return result

    if qtype == "lambda_reduce":
        result = LC.grade_lambda_answer(meta, answer if isinstance(answer, str) else "")
        result["run_result"] = None
        return result

    if qtype == "code_write":
        user_code = answer if isinstance(answer, str) else ""
        run_result, passed, total = grade_code_write(meta, user_code)
        if total == 0:
            correct = False
            score = 0.0
        else:
            score = passed / total
            correct = "partial" if 0 < score < 1.0 else (score >= 1.0)
        explanation = meta.get("explanation", "")
        if not run_result["success"] and run_result["stderr"]:
            explanation = (
                "**Your code did not compile/run successfully.** Compiler/runtime output:\n\n"
                f"```\n{run_result['stderr'][:1500]}\n```\n\n**Explanation of the intended approach:**\n\n" + explanation
            )
        return {
            "correct": correct,
            "score": score,
            "correct_answer": meta.get("reference_solution") or "(see explanation / harness for expected behaviour)",
            "explanation": explanation,
            "mistake_category": _guess_mistake_category(question) if correct is not True else None,
            "run_result": {"stdout": run_result["stdout"], "stderr": run_result["stderr"], "success": run_result["success"]},
        }

    return {"correct": False, "score": 0.0, "correct_answer": None, "explanation": "Unknown question type.", "mistake_category": None, "run_result": None}


def _decode_correct(raw):
    """DB stores correct as str(python_value) i.e. 'True' / 'False' / 'partial'.
    Decode back to a proper JSON-friendly value: True / False / 'partial'."""
    if raw == "partial":
        return "partial"
    return raw == "True" or raw == "true"


def _guess_mistake_category(question):
    topic = question.get("topic_id", "")
    qtype = question.get("type", "")
    mapping = {
        "induction": "induction",
        "lambda-calculus": "lambda-calculus",
        "recursion-basics": "recursion",
        "recursion-types": "recursion",
        "lists-basics": "list-manipulation",
        "lists-continued": "list-manipulation",
        "higher-order-currying": "higher-order-functions",
        "discriminated-unions": "pattern-matching",
        "trees-structures": "pattern-matching",
        "bindings-matching": "pattern-matching",
    }
    if qtype == "code_write":
        return mapping.get(topic, "logic")
    return mapping.get(topic, "syntax")


@app.route("/api/answer", methods=["POST"])
def api_answer():
    body = request.get_json(force=True)
    question = body.get("question")
    answer = body.get("answer")
    mode = body.get("mode", "practice")
    time_taken = body.get("time_taken_seconds")
    if not question:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    result = grade_question(question, answer)
    db.record_attempt(
        question, mode, result["correct"], result["score"], result.get("mistake_category"),
        answer, result["explanation"], time_taken,
    )
    return jsonify(result)


# ---------------------------------------------------------------- code lab --

@app.route("/api/run-fsharp", methods=["POST"])
def api_run_fsharp():
    body = request.get_json(force=True)
    code = body.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code supplied"}), 400
    result = run_fsharp(code)
    return jsonify(result)


@app.route("/api/debug-fsharp", methods=["POST"])
def api_debug_fsharp():
    body = request.get_json(force=True)
    code = body.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code supplied"}), 400
    compiler_result = run_fsharp(code)

    if compiler_result["success"]:
        return jsonify({
            "diagnosis": "Your code compiled and ran without errors.",
            "why": "There is no compiler or runtime error to diagnose.",
            "how_to_fix_reasoning": "If the OUTPUT is still wrong (logic error), re-check your base case(s), your recursive case(s), and whether you're using the right list/tree operator (`::` vs `@`, forward vs backward recursion). Compare a small hand-traced example against your actual output.",
            "corrected_code": None,
            "compiler_output": compiler_result,
        })

    stderr = compiler_result["stderr"] or ""
    diagnosis, why, how_to_fix = _diagnose_fsharp_error(stderr, compiler_result["timed_out"])

    return jsonify({
        "diagnosis": diagnosis,
        "why": why,
        "how_to_fix_reasoning": how_to_fix,
        "corrected_code": None,
        "compiler_output": compiler_result,
    })


def _diagnose_fsharp_error(stderr, timed_out):
    if timed_out:
        return (
            "Your program did not finish within the time limit -- most likely infinite recursion or an infinite loop.",
            "A recursive function needs to reach a base case on every possible path. If a recursive call is made with the same (or a non-shrinking) argument, or if a base-case pattern is never actually matched, the function calls itself forever.",
            "Trace your function by hand on a SMALL input. At each recursive call, check: is the argument strictly getting closer to a base case (e.g. decreasing towards 0, or the list getting shorter)? Is there a base-case pattern that will actually be reached?",
        )
    if "error FS0025" in stderr or "incomplete" in stderr.lower():
        return (
            "Incomplete pattern match -- your `match` (or function parameter pattern) doesn't cover every possible case.",
            "F# requires (and warns about) exhaustive matches. If an unhandled case occurs at runtime, you get a MatchFailureException.",
            "List every distinct shape the input could take (e.g. for a list: `[]` and `(h::t)`; for a DU: every case) and make sure each has a `match` branch, or add a catch-all `_` if appropriate.",
        )
    if "error FS0001" in stderr:
        return (
            "Type mismatch -- an expression's type doesn't match what's expected in that position.",
            "Common causes: mixing `int` and `float` without converting (`float x`), returning different types from different `match`/`if` branches, or passing the wrong shape of argument (e.g. a tuple where a curried pair of arguments was expected, or vice versa).",
            "Read the two types the compiler prints ('expected X but here has type Y') and work out which one is wrong for what you intended -- then either change the expression or add an explicit conversion/annotation.",
        )
    if "error FS0039" in stderr:
        return (
            "Undefined value or constructor -- you're referring to a name that doesn't exist in scope at that point.",
            "The most common cause in this module is forgetting the `rec` keyword on a function that calls itself, or a typo in a function/constructor name, or using a value before its `let` binding.",
            "Check spelling, check that `rec` is present if the function is recursive, and check the value/function is actually defined ABOVE where you use it (or is a parameter/pattern-bound name in scope).",
        )
    if "error FS0037" in stderr:
        return (
            "Duplicate definition -- a name (function, type, or DU case) is declared more than once in a scope where that's not allowed.",
            "This often happens when re-pasting a `type` declaration that already exists elsewhere in the same script, or defining the same helper function name twice inside one function body.",
            "Search for the other declaration of that exact name and remove or rename one of them.",
        )
    return (
        "The F# compiler reported an error (see the raw output below).",
        "Compiler errors point at the exact line/column of the problem -- read the first error first, since later errors are often just knock-on effects of the first one.",
        "Isolate the smallest piece of code that still reproduces the error (comment out unrelated functions) and re-run to narrow down exactly which construct is misused.",
    )


# ------------------------------------------------------------------- exam ---

EXAM_TOPIC_WEIGHTS = [
    (INDUCTION_TOPIC, 0.14),
    (LAMBDA_TOPIC, 0.14),
    ("recursion-basics", 0.08),
    ("recursion-types", 0.08),
    ("lists-basics", 0.10),
    ("lists-continued", 0.08),
    ("higher-order-currying", 0.06),
    ("tuples-records", 0.14),
    ("discriminated-unions", 0.09),
    ("trees-structures", 0.09),
]


def build_exam_questions(rng, question_count, topics=None):
    weights = EXAM_TOPIC_WEIGHTS
    if topics:
        weights = [(t, w) for t, w in EXAM_TOPIC_WEIGHTS if t in topics]
        if not weights:
            weights = [(t, 1.0) for t in topics]
    total_w = sum(w for _, w in weights)
    counts = {}
    remaining = question_count
    for i, (t, w) in enumerate(weights):
        if i == len(weights) - 1:
            counts[t] = remaining
        else:
            c = round(question_count * (w / total_w))
            c = min(c, remaining)
            counts[t] = c
            remaining -= c

    questions = []
    for topic, count in counts.items():
        for _ in range(max(0, count)):
            q = build_question_for_topic(rng, topic)
            if q:
                questions.append(q)
    rng.shuffle(questions)
    return questions


@app.route("/api/exam/start", methods=["POST"])
def api_exam_start():
    body = request.get_json(force=True) or {}
    mode = body.get("mode", "timed")
    duration = body.get("duration_minutes", 120)
    count = body.get("question_count", 12)
    topics = body.get("topics")
    rng = random.Random()

    questions = build_exam_questions(rng, count, topics)
    exam_id = "exam_" + uuid.uuid4().hex[:10]
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    EXAM_STORE[exam_id] = {"questions": questions, "mode": mode, "duration_minutes": duration}
    db.save_exam(exam_id, mode, duration, len(questions), questions)

    return jsonify({
        "exam_id": exam_id,
        "questions": questions,
        "duration_minutes": duration,
        "started_at": started_at,
    })


@app.route("/api/exam/submit", methods=["POST"])
def api_exam_submit():
    body = request.get_json(force=True) or {}
    exam_id = body.get("exam_id")
    answers = body.get("answers", [])

    per_question = []
    topic_scores = {}
    mistake_counts = {}
    total_score = 0.0

    for a in answers:
        question = a.get("question")
        answer = a.get("answer")
        time_taken = a.get("time_taken_seconds")
        if not question:
            continue
        result = grade_question(question, answer)
        db.record_attempt(question, "exam", result["correct"], result["score"], result.get("mistake_category"), answer, result["explanation"], time_taken)

        topic_id = question.get("topic_id")
        topic_scores.setdefault(topic_id, {"attempted": 0, "score": 0.0})
        topic_scores[topic_id]["attempted"] += 1
        topic_scores[topic_id]["score"] += result["score"]

        if result.get("mistake_category"):
            mistake_counts[result["mistake_category"]] = mistake_counts.get(result["mistake_category"], 0) + 1

        total_score += result["score"]
        per_question.append({
            "question_id": question.get("id"),
            "correct": result["correct"],
            "explanation": result["explanation"],
            "topic_id": topic_id,
        })

    n = len(answers) if answers else 1
    score_percent = round((total_score / n) * 100, 1) if n else 0.0

    topic_meta_by_id = {t["id"]: t for t in curriculum.TOPIC_META}
    topic_breakdown = []
    weak_concepts = []
    for tid, s in topic_scores.items():
        pct = round((s["score"] / s["attempted"]) * 100, 1) if s["attempted"] else 0.0
        title = topic_meta_by_id.get(tid, {}).get("title", tid)
        topic_breakdown.append({"topic_id": tid, "title": title, "percent": pct, "attempted": s["attempted"], "correct": round(s["score"], 2)})
        if pct < 60:
            weak_concepts.append(tid)
    topic_breakdown.sort(key=lambda x: x["percent"])

    mistake_categories = [{"category": k, "count": v} for k, v in sorted(mistake_counts.items(), key=lambda x: -x[1])]

    recommended_revision = weak_concepts[:4] if weak_concepts else [tb["topic_id"] for tb in topic_breakdown[:2]]

    rng = random.Random()
    recommended_questions = []
    for tid in recommended_revision[:3]:
        q = build_question_for_topic(rng, tid)
        if q:
            recommended_questions.append(q)

    db.submit_exam(exam_id, score_percent)
    if exam_id in EXAM_STORE:
        del EXAM_STORE[exam_id]

    return jsonify({
        "score_percent": score_percent,
        "total_marks": 100,
        "marks_achieved": score_percent,
        "per_question": per_question,
        "topic_breakdown": topic_breakdown,
        "mistake_categories": mistake_categories,
        "weak_concepts": weak_concepts,
        "recommended_revision": recommended_revision,
        "recommended_questions": recommended_questions,
    })


# --------------------------------------------------------------- progress ---

def _topic_status(pct, attempted):
    if attempted == 0:
        return "untouched"
    if pct >= 75:
        return "strong"
    if pct >= 45:
        return "developing"
    return "weak"


@app.route("/api/progress")
def api_progress():
    stats = db.get_topic_stats()
    topics_out = []
    total_attempted = 0
    total_correct = 0.0
    weak_topics = []
    strong_topics = []

    for t in curriculum.TOPIC_META:
        if t["category"] != "core":
            continue
        row = stats.get(t["id"])
        attempted = row["attempted"] if row else 0
        correct = row["correct"] if row else 0.0
        pct = round((correct / attempted) * 100, 1) if attempted else 0.0
        status = _topic_status(pct, attempted)
        topics_out.append({"topic_id": t["id"], "title": t["title"], "mastery_percent": pct, "attempted": attempted, "correct": round(correct, 1), "status": status})
        total_attempted += attempted
        total_correct += correct
        if status == "weak":
            weak_topics.append(t["id"])
        elif status == "strong":
            strong_topics.append(t["id"])

    touched = sum(1 for t in topics_out if t["attempted"] > 0)
    coverage_percent = round((touched / len(topics_out)) * 100, 1) if topics_out else 0.0

    recent = db.get_recent_attempts(limit=15)
    recent_activity = []
    for a in recent:
        recent_activity.append({
            "date": a["created_at"], "type": a["mode"], "topic_id": a["topic_id"],
            "correct": _decode_correct(a["correct"]), "score_percent": round((a["score"] or 0) * 100, 1) if a["score"] is not None else None,
        })

    exam_history_rows = db.get_exam_history(limit=10)
    exam_history = [{"exam_id": r["exam_id"], "date": r["submitted_at"], "score_percent": r["score_percent"], "duration_minutes": r["duration_minutes"]} for r in exam_history_rows]

    if weak_topics:
        study_now = {"topic_id": weak_topics[0], "reason": f"Your accuracy here is below 45% -- this is your single weakest tested area right now."}
    else:
        untouched = [t["topic_id"] for t in topics_out if t["status"] == "untouched"]
        if untouched:
            study_now = {"topic_id": untouched[0], "reason": "You haven't practised this topic yet -- it's still an unknown for the exam."}
        else:
            study_now = {"topic_id": topics_out[0]["topic_id"] if topics_out else INDUCTION_TOPIC, "reason": "Solid across the board -- keep sharpening with mixed exam-style practice and timed exams."}

    return jsonify({
        "overall_coverage_percent": coverage_percent,
        "topics": topics_out,
        "questions_attempted": total_attempted,
        "questions_correct": round(total_correct, 1),
        "questions_incorrect": round(total_attempted - total_correct, 1),
        "recent_activity": recent_activity,
        "exam_history": exam_history,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "study_now_recommendation": study_now,
    })


# ----------------------------------------------------------------- review ---

@app.route("/api/review")
def api_review():
    filt = request.args.get("filter", "all")
    limit = request.args.get("limit", 50, type=int)
    rows = db.get_attempts_filtered(filt, limit)
    items = []
    import json as _json
    for r in rows:
        try:
            question = _json.loads(r["question_json"]) if r["question_json"] else None
        except Exception:
            question = None
        try:
            answer_given = _json.loads(r["answer_given"]) if r["answer_given"] else None
        except Exception:
            answer_given = r["answer_given"]
        items.append({
            "question": question,
            "answer_given": answer_given,
            "correct": _decode_correct(r["correct"]),
            "explanation": r["explanation"],
            "date": r["created_at"],
        })
    return jsonify({"items": items})


# ----------------------------------------------------------------- tutor ----

TUTOR_ACTIONS_NEEDING_QUESTION = {"test_me", "exam_question", "similar_problem", "harder_problem"}


@app.route("/api/tutor", methods=["POST"])
def api_tutor():
    body = request.get_json(force=True) or {}
    topic_id = body.get("topic_id")
    action = body.get("action")
    context = body.get("context") or {}

    topic = curriculum.get_topic(topic_id) if topic_id else None
    if not topic:
        return jsonify({"error": f"Unknown topic '{topic_id}'"}), 400

    rng = random.Random()
    response_markdown = ""
    question = None

    levels = topic["levels"]

    if action == "explain_simple":
        response_markdown = levels.get("what_is_it", "No explanation available.")
    elif action == "explain_deep":
        response_markdown = (levels.get("what_is_it", "") + "\n\n" + levels.get("how_it_works", "")).strip()
    elif action == "syntax":
        response_markdown = levels.get("syntax", "No syntax reference available.")
    elif action == "example":
        response_markdown = levels.get("worked_example", "No example available.")
    elif action == "line_by_line":
        response_markdown = levels.get("worked_example", "No worked example available to break down line by line.")
    elif action == "hint":
        response_markdown = "**Hint:** " + _first_sentence(levels.get("exam_application", levels.get("how_it_works", "Think about the base case and recursive case.")))
    elif action == "solution":
        response_markdown = levels.get("worked_example", "No solution available.")
    elif action == "why_wrong":
        wrong = context.get("wrong_answer", "")
        response_markdown = (
            f"You answered: `{wrong}`.\n\n**Common mistakes for this topic:**\n\n" + levels.get("common_mistakes", "")
        )
    elif action == "another_example":
        response_markdown = levels.get("worked_example", "") + "\n\n**Variations:**\n\n" + levels.get("variations", "")
    elif action in TUTOR_ACTIONS_NEEDING_QUESTION:
        q = build_question_for_topic(rng, topic_id)
        question = q
        if action == "harder_problem" and q:
            q["difficulty"] = min(5, (q.get("difficulty") or 3) + 1)
        response_markdown = f"Here's a question on **{topic['title']}** for you to try:"
    elif action == "algorithm":
        response_markdown = levels.get("how_it_works", "No algorithm explanation available.")
    elif action == "compare":
        other_id = context.get("compare_with")
        other = curriculum.get_topic(other_id) if other_id else None
        if other:
            response_markdown = (
                f"**{topic['title']}**:\n{levels.get('what_is_it','')}\n\n"
                f"**{other['title']}**:\n{other['levels'].get('what_is_it','')}"
            )
        else:
            response_markdown = "Specify `context.compare_with` as another topic id to compare against."
    else:
        response_markdown = levels.get("what_is_it", "")

    return jsonify({"response_markdown": response_markdown, "question": question})


def _first_sentence(text):
    text = (text or "").strip().replace("\n", " ")
    for sep in [". ", ".\n"]:
        if sep in text:
            return text.split(sep)[0] + "."
    return text[:200]


if __name__ == "__main__":
    print("F# Exam Prep server starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
