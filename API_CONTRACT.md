# F# Exam Prep — API Contract

Backend: Flask, runs on `http://localhost:5000`. All responses JSON unless serving static files.
Frontend: static files in `app/frontend/` (`index.html`, `app.js`, `styles.css`, maybe more `.js` files), served by Flask from `/` (Flask `static_folder` points at `frontend`, `index.html` served at `/`).

No build step. No frameworks required (no React/Vue) — plain HTML/CSS/JS, using `fetch()` to talk to the API. Single-page app: one `index.html`, client-side view switching (show/hide `<section>`s or inject into a `#app` div), simple hash-based routing (`#/dashboard`, `#/learn`, `#/practice`, etc.) so back/forward + refresh keep the current view.

## Study modes / navigation (left sidebar, always visible)
Dashboard, Learn, Practice, Drill, Weaknesses, Exam, Review, Explore, Code Lab.

## Data shapes

### Topic (curriculum tree)
```
GET /api/curriculum
-> {
  "categories": [
    {"id": "core", "label": "Official Curriculum", "color": "..."},
    {"id": "legacy", "label": "Official but Not in Recent Exams", "color": "..."},
    {"id": "supplementary", "label": "Supplementary / Extra Modules", "color": "..."}
  ],
  "topics": [
    {"id": "recursion-types", "title": "Types of Recursion", "category": "core",
     "order": 4, "summary": "one-liner", "prereqs": ["recursion-basics"]}
    , ...
  ]
}
```

### Full topic content
```
GET /api/topic/<topic_id>
-> {
  "id": "...", "title": "...", "category": "core",
  "levels": {
    "what_is_it": "markdown string",
    "syntax": "markdown string (may include ```fsharp code blocks```)",
    "how_it_works": "markdown",
    "worked_example": "markdown (with code)",
    "variations": "markdown",
    "exam_application": "markdown",
    "common_mistakes": "markdown",
  },
  "syntax_refs": ["cons-operator", "match-expr"],   // ids into /api/syntax
  "practice_topic_ids": ["recursion-types"]          // topic id(s) to request practice for
}
```
Markdown subset actually used: `#`/`##` headings, `**bold**`, `` `inline code` ``, fenced ```fsharp code blocks```, `-` bullet lists, numbered lists. Frontend ships a tiny hand-rolled markdown-to-HTML renderer (no CDN dependency) — do NOT pull an external markdown library (keep it dependency-free / offline-friendly).

### Syntax reference
```
GET /api/syntax
-> { "entries": [
   {"id": "cons-operator", "title": "Cons operator ::", "category": "Lists",
    "syntax": "element :: list", "meaning": "...", "example": "```fsharp\n...\n```",
    "common_mistake": "...", "exam_use": "..."} , ...
]}
```
Frontend: searchable/filterable table or card list, grouped by `category`, acts as the "cheat sheet".

### Question object (generic, used by practice/drill/weakness/exam/review)
```
{
  "id": "q_ab12cd34",              // opaque string, stable for this instance
  "topic_id": "lists-basics",
  "type": "mcq" | "trace" | "fill_blank" | "code_write" | "proof_step" | "lambda_reduce" | "short_answer",
  "difficulty": 1-5,
  "prompt": "markdown string (question text, may include ```fsharp``` code)",
  "code": "fsharp code shown for tracing/debugging questions, or null",
  "choices": ["a","b","c","d"] | null,          // mcq only
  "blanks": ["law_choice", ...] | null,          // proof_step: list of blank slots, each rendered as a <select>
  "blank_options": [["Law 3","Law 6","Ind. Ass."], ...] | null,  // options per blank, same length as blanks
  "starter_code": "fsharp starter code" | null,  // code_write
  "lambda_expr": "((\\x.x) \\y.y)" | null,       // lambda_reduce: expression to reduce, using \ for λ
  "meta": { ... arbitrary extra data the frontend just round-trips back on submit, e.g. generation seed }
}
```

### Requesting a question
```
GET /api/question?mode=practice&topic=lists-basics&difficulty=2
GET /api/question?mode=drill&topic=lists-basics          (difficulty ignored/auto, fast small questions)
GET /api/question?mode=weakness                          (topic auto-picked from weakness model)
GET /api/question?mode=explore&topic=recursion-types&kind=harder|similar|hint  (used by the tutor "give me a harder/similar problem" actions)
-> single Question object (see above)
```

### Submitting an answer
```
POST /api/answer
body: { "question_id": "...", "question": <the full Question object as received>, "answer": <depends on type>, "time_taken_seconds": 12 }

answer shapes by type:
  mcq          -> "choice text" or index (frontend sends the exact string from choices)
  trace        -> "predicted output string"
  fill_blank   -> "text"
  code_write   -> "fsharp source code the user wrote"
  proof_step   -> ["Law 3", "Ind. Ass.", ...]   (one string per blank)
  lambda_reduce-> ["step1 expr", "step2 expr", ...] or final "normal form string" — see note below
  short_answer -> "text"

-> {
  "correct": true|false|"partial",
  "score": 0.0-1.0,
  "correct_answer": <canonical answer, same shape as expected, for display>,
  "explanation": "markdown: what's wrong -> why -> how to reason -> corrected/annotated solution",
  "mistake_category": "syntax" | "recursion" | "pattern-matching" | "higher-order-functions" |
                       "type-error" | "logic" | "induction" | "lambda-calculus" | "off-by-one" |
                       "list-manipulation" | null,
  "run_result": { "stdout": "...", "stderr": "...", "success": true } | null   // present for code_write when auto-run
}
```
For `code_write`, the backend may compile+run the user's code against hidden test cases via `dotnet fsi` (see `/api/run-fsharp`) to auto-grade; `run_result` carries the last run's output for display. Frontend should render `run_result.stdout`/`stderr` in a monospace console block when present.

For `lambda_reduce`, the simplest robust contract (use this): user submits a **single string** — the fully-reduced normal form — as `answer` (a text input), not a list of steps. Backend normalizes whitespace/parens and compares structurally. Response `explanation` includes the full step-by-step reduction (backend already computed it) regardless of correctness, so the user always sees how it's done. (i.e. treat `answer` as a plain string here, don't build a multi-step UI unless you want to — a single text input is sufficient and simpler.)

### Code execution (Code Lab)
```
POST /api/run-fsharp
body: { "code": "full .fsx script text" }
-> { "stdout": "...", "stderr": "...", "success": true|false, "timed_out": false, "duration_ms": 1234 }
```
Timeout ~10s server-side. Frontend: textarea + "Run" button + console output pane. This is a real `dotnet fsi` subprocess — treat stderr as compiler/runtime errors, show verbatim in a `<pre>`.

### Debug tutor
```
POST /api/debug-fsharp
body: { "code": "...", "question": "optional: what the user says is wrong / expected behaviour" }
-> {
  "diagnosis": "markdown: What is wrong",
  "why": "markdown: Why it is wrong",
  "how_to_fix_reasoning": "markdown: How to reason about fixing it",
  "corrected_code": "fsharp source, or null if code actually compiles fine",
  "compiler_output": { "stdout": "...", "stderr": "...", "success": true|false }
}
```

### Exam mode
```
POST /api/exam/start
body: { "mode": "timed"|"untimed", "duration_minutes": 120, "question_count": 12, "topics": ["..."] | null (null = curriculum-balanced across all core topics, weighted like real papers: theory ~25%, general practical ~30%, records ~20%, discriminated-unions/trees ~25%) }
-> { "exam_id": "...", "questions": [ Question, ... ], "duration_minutes": 120, "started_at": "iso8601" }

POST /api/exam/submit
body: { "exam_id": "...", "answers": [ {"question_id": "...", "question": <Question>, "answer": <...>, "time_taken_seconds": N}, ... ] }
-> {
  "score_percent": 63.5,
  "total_marks": 100, "marks_achieved": 63.5,
  "per_question": [ { "question_id": "...", "correct": true|"partial"|false, "explanation": "...", "topic_id": "..." }, ... ],
  "topic_breakdown": [ {"topic_id": "...", "title": "...", "percent": 40.0, "attempted": 3, "correct": 1} ],
  "mistake_categories": [ {"category": "induction", "count": 3} ],
  "weak_concepts": ["structural-induction", "..."],
  "recommended_revision": ["topic_id", ...],
  "recommended_questions": [ Question, ... ]   // 3-5 targeted follow-ups, already generated
}
```

### Progress dashboard
```
GET /api/progress
-> {
  "overall_coverage_percent": 62,
  "topics": [ {"topic_id": "...", "title": "...", "mastery_percent": 0-100, "attempted": N, "correct": N, "status": "strong"|"developing"|"weak"|"untouched"} ],
  "questions_attempted": N, "questions_correct": N, "questions_incorrect": N,
  "recent_activity": [ {"date": "iso8601", "type": "practice"|"exam"|"drill", "topic_id": "...", "correct": bool|null, "score_percent": number|null} ],
  "exam_history": [ {"exam_id": "...", "date": "...", "score_percent": ..., "duration_minutes": ...} ],
  "weak_topics": ["topic_id", ...], "strong_topics": ["topic_id", ...],
  "study_now_recommendation": { "topic_id": "...", "reason": "markdown one-liner" }
}
```

### Review
```
GET /api/review?filter=incorrect|all|topic:<id>&limit=50
-> { "items": [ {"question": Question, "answer_given": ..., "correct": ..., "explanation": "...", "date": "..."} ] }
```

### Explore / tutor free actions
```
POST /api/tutor
body: { "topic_id": "...", "action": "explain_simple"|"explain_deep"|"syntax"|"example"|"line_by_line"|
        "similar_problem"|"harder_problem"|"hint"|"solution"|"why_wrong"|"another_example"|"test_me"|
        "exam_question"|"algorithm"|"compare", "context": { ...optional, e.g. {"wrong_answer": "...", "question": Question} or {"compare_with": "other-topic-id"} } }
-> { "response_markdown": "...", "question": Question | null }   // question present when action implies generating one (test_me, exam_question, similar_problem, harder_problem)
```

## Error shape
Any 4xx/5xx: `{ "error": "message" }`.

## Persistence
SQLite at `app/backend/study.db`, single implicit local user (no auth/login — this is a personal local tool). Backend creates/migrates the schema on first run automatically.

## General frontend requirements
- Clean, professional, calm dark-mode-friendly study-tool aesthetic. Not flashy. Code blocks use a monospace font with F# keyword-ish highlighting is a nice-to-have but NOT required — plain `<pre><code>` is fine.
- Every place content is shown, category badges (Official Curriculum / Legacy / Supplementary) must be visually distinct (small colored pill) per section 18 of the spec — never blur these.
- Must work by opening `http://localhost:5000` after the Flask server (`python app.py`) is started — no separate frontend server, no npm.
- Mobile/narrow layout not a priority (desktop study tool), but don't hard-code huge fixed widths that break on a laptop.
