var Views = window.Views = window.Views || {};

function mountQuestionSession(container, cfg) {
  // cfg: { mode: 'practice'|'drill'|'weakness', title, subtitle, showTopicPicker, showDifficultyPicker, fastUi }
  return Components.ensureCurriculumLoaded().then(function (curriculum) {
    const topics = curriculum.topics.slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
    let state = { topic: "", difficulty: "" };

    let html = '<h1 class="page-title">' + escapeHtml(cfg.title) + '</h1>';
    html += '<p class="page-subtitle">' + escapeHtml(cfg.subtitle) + '</p>';

    if (cfg.showTopicPicker || cfg.showDifficultyPicker) {
      html += '<div class="card" style="display:flex;gap:14px;align-items:flex-end;flex-wrap:wrap;">';
      if (cfg.showTopicPicker) {
        html += '<div class="field" style="min-width:240px;margin-bottom:0;"><label>Topic</label><select id="sess-topic"><option value="">All core topics</option>';
        topics.forEach(function (t) { html += '<option value="' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</option>'; });
        html += '</select></div>';
      }
      if (cfg.showDifficultyPicker) {
        html += '<div class="field" style="min-width:160px;margin-bottom:0;"><label>Difficulty</label><select id="sess-diff">' +
          '<option value="">Any</option><option value="1">1 — Basic</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5 — Exam level</option></select></div>';
      }
      html += '<button class="primary" id="sess-new">New question</button>';
      html += '</div>';
    }

    html += '<div id="sess-info" style="margin-bottom:10px;color:var(--text-dim);font-size:13px;"></div>';
    html += '<div id="sess-question"><div class="empty-state">Click "New question" to begin.</div></div>';

    container.innerHTML = html;

    const topicSel = document.getElementById("sess-topic");
    const diffSel = document.getElementById("sess-diff");
    const newBtn = document.getElementById("sess-new");
    const qArea = document.getElementById("sess-question");
    const infoArea = document.getElementById("sess-info");

    let streak = 0, seen = 0;

    function loadQuestion() {
      state.topic = topicSel ? topicSel.value : "";
      state.difficulty = diffSel ? diffSel.value : "";
      qArea.innerHTML = '<div class="loading-shell">Generating question…</div>';
      const params = { mode: cfg.mode };
      if (state.topic) params.topic = state.topic;
      if (state.difficulty) params.difficulty = state.difficulty;
      Api.getQuestion(params).then(function (q) {
        renderSessionQuestion(qArea, q, curriculum, cfg, function (wasCorrect) {
          seen++;
          streak = wasCorrect ? streak + 1 : 0;
          if (infoArea) {
            infoArea.textContent = "Answered: " + seen + (cfg.fastUi ? "  ·  Streak: " + streak : "");
          }
        }, loadQuestion);
        if (cfg.mode === "weakness" && infoArea) {
          const meta = Components.getTopicMeta(curriculum, q.topic_id);
          infoArea.textContent = "Focusing on " + (meta ? meta.title : q.topic_id) + " — flagged as a weak area from your practice history.";
        }
      }).catch(function (e) {
        Components.reportError(e, "Could not generate question");
        qArea.innerHTML = '<div class="empty-state">Could not generate a question. Try a different topic.</div>';
      });
    }

    if (newBtn) newBtn.addEventListener("click", loadQuestion);

    // Auto-start for drill/weakness modes (no manual "new question" click needed first time)
    if (!cfg.showTopicPicker && !cfg.showDifficultyPicker) loadQuestion();
    else if (cfg.mode === "weakness") loadQuestion();
  });
}

function renderSessionQuestion(qArea, q, curriculum, cfg, onAnswered, loadNext) {
  const meta = Components.getTopicMeta(curriculum, q.topic_id);
  const startedAt = Date.now();
  const ctl = Components.renderQuestionCard(qArea, q, { topicCategory: meta ? meta.category : "core" });

  const btnRow = document.createElement("div");
  btnRow.className = "btn-row";
  const submitBtn = document.createElement("button");
  submitBtn.className = "primary";
  submitBtn.textContent = "Submit";
  btnRow.appendChild(submitBtn);
  ctl.block.appendChild(btnRow);

  function doSubmit() {
    const answer = ctl.getAnswer();
    submitBtn.disabled = true;
    Api.submitAnswer({
      question_id: q.id, question: q, answer: answer,
      time_taken_seconds: Math.round((Date.now() - startedAt) / 1000)
    }).then(function (result) {
      ctl.disable();
      submitBtn.remove();
      Components.renderResultPanel(ctl.block, result);
      const nextBtn = document.createElement("button");
      nextBtn.className = "primary";
      nextBtn.style.marginTop = "12px";
      nextBtn.textContent = cfg.fastUi ? "Next →" : "Next question";
      nextBtn.addEventListener("click", loadNext);
      ctl.block.appendChild(nextBtn);
      if (cfg.fastUi) setTimeout(function () { nextBtn.focus(); }, 20);
      onAnswered(result.correct === true);
    }).catch(function (e) {
      Components.reportError(e, "Could not submit answer");
      submitBtn.disabled = false;
    });
  }

  submitBtn.addEventListener("click", doSubmit);

  // Enter-to-submit for fast text-input drills
  const textInput = ctl.block.querySelector('input[type="text"]');
  if (textInput && cfg.fastUi) {
    textInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") doSubmit();
    });
  }
}

Views.practice = function (container) {
  return mountQuestionSession(container, {
    mode: "practice", title: "Practice",
    subtitle: "Targeted exercises across the curriculum, at your pace.",
    showTopicPicker: true, showDifficultyPicker: true, fastUi: false
  });
};

Views.drill = function (container) {
  return mountQuestionSession(container, {
    mode: "drill", title: "Drill",
    subtitle: "Rapid-fire syntax and concept checks. Answer, submit, move on.",
    showTopicPicker: true, showDifficultyPicker: false, fastUi: true
  });
};

Views.weaknesses = function (container) {
  return mountQuestionSession(container, {
    mode: "weakness", title: "Weaknesses",
    subtitle: "The system picks what you most need to work on right now.",
    showTopicPicker: false, showDifficultyPicker: false, fastUi: false
  });
};
