var Views = window.Views = window.Views || {};

const TUTOR_ACTIONS = [
  ["explain_simple", "Explain simply"],
  ["explain_deep", "Explain in depth"],
  ["syntax", "Show syntax"],
  ["example", "Show example"],
  ["line_by_line", "Explain line-by-line"],
  ["similar_problem", "Similar problem"],
  ["harder_problem", "Harder problem"],
  ["hint", "Give me a hint"],
  ["solution", "Show solution"],
  ["another_example", "Another example"],
  ["test_me", "Test me"],
  ["exam_question", "Exam question"],
  ["algorithm", "Explain the algorithm"],
  ["compare", "Compare with…"]
];

Views.explore = function (container) {
  return Components.ensureCurriculumLoaded().then(function (curriculum) {
    const topics = curriculum.topics.slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
    let currentTopic = topics.length ? topics[0].id : null;
    let lastQuestionCtl = null;
    let lastQuestion = null;

    let html = '<h1 class="page-title">Explore</h1>';
    html += '<p class="page-subtitle">Ask the tutor for exactly what you need, on any topic.</p>';
    html += '<div class="card">';
    html += '<div class="field"><label>Topic</label><select id="explore-topic">';
    topics.forEach(function (t) { html += '<option value="' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</option>'; });
    html += '</select></div>';
    html += '<div class="field" id="explore-compare-field" style="display:none;"><label>Compare with</label><select id="explore-compare">';
    topics.forEach(function (t) { html += '<option value="' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</option>'; });
    html += '</select></div>';
    html += '<div class="btn-row" id="explore-actions">';
    TUTOR_ACTIONS.forEach(function (pair) {
      html += '<button data-action="' + pair[0] + '">' + escapeHtml(pair[1]) + '</button>';
    });
    html += '</div>';
    html += '</div>';
    html += '<div id="explore-output"></div>';

    container.innerHTML = html;

    const topicSel = document.getElementById("explore-topic");
    const compareField = document.getElementById("explore-compare-field");
    const compareSel = document.getElementById("explore-compare");
    const outputEl = document.getElementById("explore-output");

    topicSel.addEventListener("change", function () { currentTopic = topicSel.value; });
    compareSel.addEventListener("change", function () {
      if (compareField.style.display !== "none") runAction("compare");
    });

    document.getElementById("explore-actions").addEventListener("click", function (e) {
      const btn = e.target.closest("button");
      if (!btn) return;
      const action = btn.dataset.action;
      if (action === "compare") {
        compareField.style.display = "block";
      }
      runAction(action);
    });

    function runAction(action) {
      outputEl.innerHTML = '<div class="loading-shell">Thinking…</div>';
      const payload = { topic_id: topicSel.value, action: action, context: {} };
      if (action === "compare") payload.context.compare_with = compareSel.value;

      Api.tutor(payload).then(function (resp) {
        let html2 = '<div class="card">' + renderMarkdown(resp.response_markdown || "") + '</div>';
        outputEl.innerHTML = html2;
        if (resp.question) {
          renderInlineQuestion(outputEl, resp.question, curriculum);
        }
      }).catch(function (e) {
        Components.reportError(e, "Tutor could not respond");
        outputEl.innerHTML = '<div class="empty-state">The tutor could not respond to that request.</div>';
      });
    }

    function renderInlineQuestion(container2, question, curriculum2) {
      const wrap = document.createElement("div");
      wrap.className = "card";
      container2.appendChild(wrap);
      const meta = Components.getTopicMeta(curriculum2, question.topic_id);
      const ctl = Components.renderQuestionCard(wrap, question, { topicCategory: meta ? meta.category : "core" });
      lastQuestionCtl = ctl;
      lastQuestion = question;
      const startedAt = Date.now();

      const btn = document.createElement("button");
      btn.className = "primary";
      btn.style.marginTop = "10px";
      btn.textContent = "Check answer";
      ctl.block.appendChild(btn);

      btn.addEventListener("click", function () {
        const answer = ctl.getAnswer();
        btn.disabled = true;
        Api.submitAnswer({
          question_id: question.id, question: question, answer: answer,
          time_taken_seconds: Math.round((Date.now() - startedAt) / 1000)
        }).then(function (result) {
          ctl.disable();
          btn.remove();
          Components.renderResultPanel(ctl.block, result);
          if (result.correct !== true) {
            const whyBtn = document.createElement("button");
            whyBtn.style.marginTop = "10px";
            whyBtn.textContent = "Why is this wrong?";
            whyBtn.addEventListener("click", function () {
              whyBtn.disabled = true;
              Api.tutor({
                topic_id: question.topic_id, action: "why_wrong",
                context: { wrong_answer: answer, question: question }
              }).then(function (resp) {
                const explainDiv = document.createElement("div");
                explainDiv.className = "card";
                explainDiv.innerHTML = renderMarkdown(resp.response_markdown || "");
                ctl.block.appendChild(explainDiv);
                whyBtn.remove();
              }).catch(function (e) { Components.reportError(e); whyBtn.disabled = false; });
            });
            ctl.block.appendChild(whyBtn);
          }
        }).catch(function (e) {
          Components.reportError(e, "Could not submit answer");
          btn.disabled = false;
        });
      });
    }
  });
};
