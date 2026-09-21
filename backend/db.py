import sqlite3
import os
import json
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "study.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT,
    topic_id TEXT,
    mode TEXT,
    q_type TEXT,
    difficulty INTEGER,
    correct TEXT,        -- 'true' | 'false' | 'partial'
    score REAL,
    mistake_category TEXT,
    answer_given TEXT,    -- JSON
    question_json TEXT,   -- JSON snapshot of the full question
    explanation TEXT,
    time_taken_seconds REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS question_exposure (
    template_key TEXT,
    seed_key TEXT,
    times_seen INTEGER DEFAULT 0,
    last_seen TEXT,
    PRIMARY KEY (template_key, seed_key)
);

CREATE TABLE IF NOT EXISTS exams (
    exam_id TEXT PRIMARY KEY,
    mode TEXT,
    duration_minutes INTEGER,
    question_count INTEGER,
    started_at TEXT,
    submitted_at TEXT,
    score_percent REAL,
    questions_json TEXT
);

CREATE TABLE IF NOT EXISTS topic_stats (
    topic_id TEXT PRIMARY KEY,
    attempted INTEGER DEFAULT 0,
    correct REAL DEFAULT 0,
    last_practiced TEXT
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def record_attempt(question, mode, correct, score, mistake_category, answer_given, explanation, time_taken_seconds):
    conn = get_conn()
    conn.execute(
        """INSERT INTO attempts
           (question_id, topic_id, mode, q_type, difficulty, correct, score, mistake_category,
            answer_given, question_json, explanation, time_taken_seconds, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            question.get("id"),
            question.get("topic_id"),
            mode,
            question.get("type"),
            question.get("difficulty"),
            str(correct),
            score,
            mistake_category,
            json.dumps(answer_given),
            json.dumps(question),
            explanation,
            time_taken_seconds,
            now_iso(),
        ),
    )
    topic_id = question.get("topic_id")
    if topic_id:
        row = conn.execute("SELECT * FROM topic_stats WHERE topic_id=?", (topic_id,)).fetchone()
        num_score = 1.0 if correct == True or correct == "true" else (0.5 if correct == "partial" else 0.0)
        if score is not None:
            num_score = score
        if row:
            conn.execute(
                "UPDATE topic_stats SET attempted = attempted + 1, correct = correct + ?, last_practiced = ? WHERE topic_id=?",
                (num_score, now_iso(), topic_id),
            )
        else:
            conn.execute(
                "INSERT INTO topic_stats (topic_id, attempted, correct, last_practiced) VALUES (?,1,?,?)",
                (topic_id, num_score, now_iso()),
            )
    conn.commit()
    conn.close()


def bump_exposure(template_key, seed_key):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM question_exposure WHERE template_key=? AND seed_key=?", (template_key, seed_key)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE question_exposure SET times_seen = times_seen + 1, last_seen=? WHERE template_key=? AND seed_key=?",
            (now_iso(), template_key, seed_key),
        )
    else:
        conn.execute(
            "INSERT INTO question_exposure (template_key, seed_key, times_seen, last_seen) VALUES (?,?,1,?)",
            (template_key, seed_key, now_iso()),
        )
    conn.commit()
    conn.close()


def get_exposure_counts(template_key):
    """Return {seed_key: times_seen} for every seed_key seen under this template_key.
    Used to bias question-template selection towards novelty (see questions.py /
    induction_proofs.py 80% novel / 20% deliberate-reuse selection)."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT seed_key, times_seen FROM question_exposure WHERE template_key=?", (template_key,)
    ).fetchall()
    conn.close()
    return {r["seed_key"]: r["times_seen"] for r in rows}


def get_exposure_count(template_key, seed_key):
    conn = get_conn()
    row = conn.execute(
        "SELECT times_seen FROM question_exposure WHERE template_key=? AND seed_key=?", (template_key, seed_key)
    ).fetchone()
    conn.close()
    return row["times_seen"] if row else 0


def get_topic_stats():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM topic_stats").fetchall()
    conn.close()
    return {r["topic_id"]: dict(r) for r in rows}


def get_recent_attempts(limit=20):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attempts_filtered(filter_str, limit=50):
    conn = get_conn()
    if filter_str == "incorrect":
        # `correct` is stored as str(python_value): 'True' / 'False' / 'partial'.
        # Anything not exactly 'True' counts as needing review.
        rows = conn.execute(
            "SELECT * FROM attempts WHERE correct != 'True' ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    elif filter_str and filter_str.startswith("topic:"):
        topic_id = filter_str.split(":", 1)[1]
        rows = conn.execute(
            "SELECT * FROM attempts WHERE topic_id=? ORDER BY id DESC LIMIT ?", (topic_id, limit)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mistake_category_counts(limit=200):
    conn = get_conn()
    rows = conn.execute(
        "SELECT mistake_category, COUNT(*) as c FROM attempts WHERE mistake_category IS NOT NULL "
        "AND correct != 'True' GROUP BY mistake_category ORDER BY c DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_exam(exam_id, mode, duration_minutes, question_count, questions):
    conn = get_conn()
    conn.execute(
        """INSERT INTO exams (exam_id, mode, duration_minutes, question_count, started_at, questions_json)
           VALUES (?,?,?,?,?,?)""",
        (exam_id, mode, duration_minutes, question_count, now_iso(), json.dumps(questions)),
    )
    conn.commit()
    conn.close()


def submit_exam(exam_id, score_percent):
    conn = get_conn()
    conn.execute(
        "UPDATE exams SET submitted_at=?, score_percent=? WHERE exam_id=?",
        (now_iso(), score_percent, exam_id),
    )
    conn.commit()
    conn.close()


def get_exam(exam_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM exams WHERE exam_id=?", (exam_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_exam_history(limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM exams WHERE submitted_at IS NOT NULL ORDER BY submitted_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
