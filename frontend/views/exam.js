var Views = window.Views = window.Views || {};

Views.exam = function (container) {
  return Components.ensureCurriculumLoaded().then(function (curriculum) {
    renderSetup(container, curriculum);
  });
};

function renderSetup(container, curriculum) {
  const coreTopics = curriculum.topics.filter(function (t) { return t.category === "core"; })
    .sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
  const selectedTopics = new Set();

  let html = '<h1 class="page-title">Exam Simulation</h1>';
  html += '<p class="page-subtitle">Sit a realistic, curriculum-balanced paper — or focus on specific topics.</p>';
  html += '<div class="card">';
  html += '<div class="grid-2">';
  html += '<div class="field"><label>Mode</label><select id="exam-mode"><option value="timed">Timed</option><option value="untimed">Untimed</option></select></div>';
  html += '<div class="field"><label>Duration (minutes)</label><input type="number" id="exam-duration" value="60" min="10" max="180"></div>';
  html += '<div class="field"><label>Number of questions</label><input type="number" id="exam-count" value="10" min="3" max="30"></div>';
  html += '<div class="field"><label>Topics</label><div style="font-size:12.5px;color:var(--text-faint);padding-top:6px;">Leave empty for a curriculum-balanced paper</div></div>';
  html += '</div>';
  html += '<div class="chip-row" id="exam-topic-chips">';
  coreTopics.forEach(function (t) {
    html += '<div class="chip" data-id="' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</div>';
  });
  html += '</div>';
  html += '<div class="btn-row"><button class="primary" id="exam-start">Start Exam</button></div>';
  html += '</div>';

  container.innerHTML = html;

  document.getElementById("exam-topic-chips").addEventListener("click", function (e) {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    const id = chip.dataset.id;
    if (selectedTopics.has(id)) { selectedTopics.delete(id); chip.classList.remove("active"); }
    else { selectedTopics.add(id); chip.classList.add("active"); }
  });

  document.getElementById("exam-start").addEventListener("click", function () {
    const btn = document.getElementById("exam-start");
    btn.disabled = true;
    btn.textContent = "Preparing exam…";
    const payload = {
      mode: document.getElementById("exam-mode").value,
      duration_minutes: parseInt(document.getElementById("exam-duration").value, 10) || 60,
      question_count: parseInt(document.getElementById("exam-count").value, 10) || 10,
      topics: selectedTopics.size ? Array.from(selectedTopics) : null
    };
    Api.startExam(payload).then(function (session) {
      runExam(container, session, curriculum);
    }).catch(function (e) {
      Components.reportError(e, "Could not start exam");
      btn.disabled = false;
      btn.textContent = "Start Exam";
    });
  });
}

function runExam(container, session, curriculum) {
  const questions = session.questions;
  const answers = new Array(questions.length).fill(null);
  const answeredTimes = new Array(questions.length).fill(0);
  let current = 0;
  let intervalId = null;
  const endAt = session.duration_minutes ? (new Date(session.started_at).getTime() + session.duration_minutes * 60000) : null;

  function teardown() {
    if (intervalId) clearInterval(intervalId);
    window.removeEventListener("hashchange", teardown);
  }
  window.addEventListener("hashchange", teardown);

  function captureCurrentAnswer(ctl) {
    if (ctl) answers[current] = ctl.getAnswer();
  }

  let activeCtl = null;

  function renderShell() {
    let html = '<h1 class="page-title">Exam in progress</h1>';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">';
    html += '<div class="exam-nav" id="exam-nav"></div>';
    html += endAt ? '<div class="exam-timer" id="exam-timer">--:--</div>' : '<div></div>';
    html += '</div>';
    html += '<div id="exam-question-area"></div>';
    html += '<div class="btn-row">';
    html += '<button id="exam-prev">← Previous</button>';
    html += '<button id="exam-next">Next →</button>';
    html += '<button class="primary" id="exam-submit" style="margin-left:auto;">Submit Exam</button>';
    html += '</div>';
    container.innerHTML = html;

    document.getElementById("exam-prev").addEventListener("click", function () { goTo(current - 1); });
    document.getElementById("exam-next").addEventListener("click", function () { goTo(current + 1); });
    document.getElementById("exam-submit").addEventListener("click", submit);
    document.getElementById("exam-nav").addEventListener("click", function (e) {
      const item = e.target.closest(".exam-nav-item");
      if (item) goTo(parseInt(item.dataset.idx, 10));
    });

    if (endAt) {
      intervalId = setInterval(updateTimer, 1000);
      updateTimer();
    }
  }

  function updateTimer() {
    const el = document.getElementById("exam-timer");
    if (!el) return;
    const remainingMs = endAt - Date.now();
    if (remainingMs <= 0) {
      el.textContent = "00:00";
      clearInterval(intervalId);
      Components.showToast("Time's up — submitting your exam.", "info");
      submit();
      return;
    }
    const totalSec = Math.floor(remainingMs / 1000);
    const mm = String(Math.floor(totalSec / 60)).padStart(2, "0");
    const ss = String(totalSec % 60).padStart(2, "0");
    el.textContent = mm + ":" + ss;
    if (totalSec < 300) el.style.color = "var(--bad)";
  }

  function renderNav() {
    const navEl = document.getElementById("exam-nav");
    if (!navEl) return;
    navEl.innerHTML = questions.map(function (q, idx) {
      const cls = ["exam-nav-item"];
      if (idx === current) cls.push("current");
      if (answers[idx] !== null && answers[idx] !== "" && !(Array.isArray(answers[idx]) && answers[idx].every(function (a) { return !a; }))) cls.push("answered");
      return '<div class="' + cls.join(" ") + '" data-idx="' + idx + '">' + (idx + 1) + '</div>';
    }).join("");
  }

  function goTo(idx) {
    if (activeCtl) captureCurrentAnswer(activeCtl);
    if (idx < 0 || idx >= questions.length) return;
    current = idx;
    renderQuestion();
  }

  function renderQuestion() {
    const q = questions[current];
    const meta = Components.getTopicMeta(curriculum, q.topic_id);
    const area = document.getElementById("exam-question-area");
    const ctl = Components.renderQuestionCard(area, q, { topicCategory: meta ? meta.category : "core" });
    prefillAnswer(ctl.block, q, answers[current]);
    activeCtl = ctl;
    renderNav();
    document.getElementById("exam-prev").disabled = current === 0;
    document.getElementById("exam-next").textContent = current === questions.length - 1 ? "Next →" : "Next →";
  }

  function submit() {
    if (activeCtl) captureCurrentAnswer(activeCtl);
    teardown();
    container.innerHTML = '<div class="loading-shell">Grading your exam…</div>';
    const payload = {
      exam_id: session.exam_id,
      answers: questions.map(function (q, idx) {
        return { question_id: q.id, question: q, answer: answers[idx], time_taken_seconds: answeredTimes[idx] || 0 };
      })
    };
    Api.submitExam(payload).then(function (result) {
      renderResults(container, result, curriculum);
    }).catch(function (e) {
      Components.reportError(e, "Could not submit exam");
      container.innerHTML = '<div class="empty-state">Could not grade the exam. Your answers were not saved.</div>';
    });
  }

  renderShell();
  renderQuestion();
}

function prefillAnswer(block, question, stored) {
  if (stored === undefined || stored === null) return;
  if (question.type === "mcq") {
    block.querySelectorAll('input[type="radio"]').forEach(function (r) {
      if (r.value === stored) { r.checked = true; r.dispatchEvent(new Event("change")); }
    });
  } else if (question.type === "proof_step") {
    const selects = block.querySelectorAll("select");
    selects.forEach(function (s, i) { if (Array.isArray(stored) && stored[i] !== undefined) s.value = stored[i]; });
  } else if (question.type === "code_write") {
    const ta = block.querySelector("textarea");
    if (ta) ta.value = stored;
  } else {
    const inp = block.querySelector('input[type="text"]');
    if (inp) inp.value = stored;
  }
}

function renderResults(container, result, curriculum) {
  let html = '<h1 class="page-title">Exam Results</h1>';
  html += '<div class="card" style="text-align:center;">';
  html += '<div style="font-size:42px;font-weight:700;">' + result.score_percent.toFixed(1) + '%</div>';
  html += '<div style="color:var(--text-faint);">' + result.marks_achieved.toFixed(1) + ' / ' + result.total_marks + ' marks</div>';
  html += '</div>';

  html += '<div class="grid-2">';
  html += '<div class="card"><div class="card-title">Topic Breakdown</div>';
  (result.topic_breakdown || []).forEach(function (t) {
    const status = t.percent >= 70 ? "strong" : (t.percent >= 40 ? "developing" : "weak");
    html += '<div class="bar-row"><div class="bar-label">' + escapeHtml(t.title || t.topic_id) + '</div>' +
      '<div class="bar-track" style="flex:1;"><div class="bar-fill ' + Components.barFillClass(status) + '" style="width:' + t.percent + '%;"></div></div>' +
      '<div class="bar-value">' + Math.round(t.percent) + '%</div></div>';
  });
  html += '</div>';

  html += '<div class="card"><div class="card-title">Mistake Categories</div>';
  const mc = result.mistake_categories || [];
  if (!mc.length) {
    html += '<p style="color:var(--text-faint);font-size:13px;">No recurring mistake pattern detected.</p>';
  } else {
    const max = Math.max.apply(null, mc.map(function (m) { return m.count; }));
    mc.forEach(function (m) {
      html += '<div class="bar-row"><div class="bar-label">' + escapeHtml(m.category) + '</div>' +
        '<div class="bar-track" style="flex:1;"><div class="bar-fill warn" style="width:' + (m.count / max * 100) + '%;"></div></div>' +
        '<div class="bar-value">' + m.count + '</div></div>';
    });
  }
  html += '</div>';
  html += '</div>';

  html += '<div class="card"><div class="card-title">Weak Concepts &amp; Recommended Revision</div>';
  html += '<div class="chip-row">' + (result.weak_concepts || []).map(function (c) { return '<span class="chip">' + escapeHtml(c) + '</span>'; }).join("") + '</div>';
  html += '<div class="btn-row">' + (result.recommended_revision || []).map(function (t) {
    return '<a class="btn" href="#/learn/' + encodeURIComponent(t) + '">Review ' + escapeHtml(t.replace(/-/g, " ")) + '</a>';
  }).join("") + '</div>';
  html += '</div>';

  html += '<div class="card"><div class="card-title">Question-by-Question</div><div id="exam-pq"></div></div>';

  if (result.recommended_questions && result.recommended_questions.length) {
    html += '<div class="card"><div class="card-title">Recommended Follow-Up Questions</div><div id="exam-followups"></div></div>';
  }

  container.innerHTML = html;

  const pqEl = document.getElementById("exam-pq");
  (result.per_question || []).forEach(function (pq, idx) {
    const item = document.createElement("div");
    item.className = "review-item";
    const kind = pq.correct === true ? "correct" : (pq.correct === "partial" ? "partial" : "incorrect");
    const icon = kind === "correct" ? "✓" : (kind === "partial" ? "±" : "✗");
    item.innerHTML = '<div class="review-item-head"><span>Q' + (idx + 1) + ' · ' + escapeHtml((pq.topic_id || "").replace(/-/g, " ")) + '</span><span class="status-' + (kind === "correct" ? "strong" : kind === "partial" ? "developing" : "weak") + '">' + icon + '</span></div>' +
      '<div class="review-item-body">' + renderMarkdown(pq.explanation || "") + '</div>';
    item.querySelector(".review-item-head").addEventListener("click", function () { item.classList.toggle("open"); });
    pqEl.appendChild(item);
  });

  if (result.recommended_questions && result.recommended_questions.length) {
    const followEl = document.getElementById("exam-followups");
    result.recommended_questions.forEach(function (q, i) {
      const holder = document.createElement("div");
      holder.style.marginBottom = "16px";
      followEl.appendChild(holder);
      const meta = Components.getTopicMeta(curriculum, q.topic_id);
      const ctl = Components.renderQuestionCard(holder, q, { topicCategory: meta ? meta.category : "core" });
      const btn = document.createElement("button");
      btn.className = "primary";
      btn.style.marginTop = "10px";
      btn.textContent = "Check answer";
      ctl.block.appendChild(btn);
      btn.addEventListener("click", function () {
        Api.submitAnswer({ question_id: q.id, question: q, answer: ctl.getAnswer(), time_taken_seconds: 0 }).then(function (r) {
          ctl.disable();
          btn.remove();
          Components.renderResultPanel(ctl.block, r);
        }).catch(function (e) { Components.reportError(e); });
      });
    });
  }
}
