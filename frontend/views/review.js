var Views = window.Views = window.Views || {};

Views.review = function (container) {
  return Components.ensureCurriculumLoaded().then(function (curriculum) {
    const coreTopics = curriculum.topics.slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });

    let html = '<h1 class="page-title">Review</h1>';
    html += '<p class="page-subtitle">Revisit past attempts and mistakes.</p>';
    html += '<div class="chip-row" id="review-filters">';
    html += '<div class="chip active" data-filter="incorrect">Incorrect only</div>';
    html += '<div class="chip" data-filter="all">All attempts</div>';
    html += '<select id="review-topic" style="width:auto;margin-left:8px;"><option value="">Filter by topic…</option>';
    coreTopics.forEach(function (t) { html += '<option value="topic:' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</option>'; });
    html += '</select>';
    html += '</div>';
    html += '<div id="review-list"><div class="loading-shell">Loading…</div></div>';
    container.innerHTML = html;

    let currentFilter = "incorrect";

    function load(filter) {
      document.getElementById("review-list").innerHTML = '<div class="loading-shell">Loading…</div>';
      Api.getReview({ filter: filter, limit: 50 }).then(function (data) {
        renderList(data.items || []);
      }).catch(function (e) {
        Components.reportError(e, "Could not load review items");
        document.getElementById("review-list").innerHTML = '<div class="empty-state">Could not load review history.</div>';
      });
    }

    function renderList(items) {
      const listEl = document.getElementById("review-list");
      if (!items.length) {
        listEl.innerHTML = '<div class="empty-state"><div class="icon">✓</div>Nothing to review here yet.</div>';
        return;
      }
      listEl.innerHTML = "";
      items.forEach(function (item) {
        const q = item.question || {};
        const kind = item.correct === true ? "correct" : (item.correct === "partial" ? "partial" : "incorrect");
        const div = document.createElement("div");
        div.className = "review-item";
        div.innerHTML =
          '<div class="review-item-head"><span>' + escapeHtml((q.topic_id || "").replace(/-/g, " ")) + ' · ' + escapeHtml(q.type || "") +
          '<span style="color:var(--text-faint);"> · ' + escapeHtml(item.date ? new Date(item.date).toLocaleString() : "") + '</span></span>' +
          '<span class="status-' + (kind === "correct" ? "strong" : kind === "partial" ? "developing" : "weak") + '">' + kind + '</span></div>' +
          '<div class="review-item-body"></div>';
        const body = div.querySelector(".review-item-body");
        body.innerHTML = renderMarkdown(q.prompt || "") +
          (q.code ? "<pre><code>" + escapeHtml(q.code) + "</code></pre>" : "") +
          '<div style="margin:8px 0;"><strong>Your answer:</strong> <code>' + escapeHtml(JSON.stringify(item.answer_given)) + '</code></div>' +
          renderMarkdown(item.explanation || "");
        div.querySelector(".review-item-head").addEventListener("click", function () { div.classList.toggle("open"); });
        listEl.appendChild(div);
      });
    }

    document.getElementById("review-filters").addEventListener("click", function (e) {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      document.querySelectorAll("#review-filters .chip").forEach(function (c) { c.classList.remove("active"); });
      chip.classList.add("active");
      document.getElementById("review-topic").value = "";
      currentFilter = chip.dataset.filter;
      load(currentFilter);
    });
    document.getElementById("review-topic").addEventListener("change", function (e) {
      if (!e.target.value) return;
      document.querySelectorAll("#review-filters .chip").forEach(function (c) { c.classList.remove("active"); });
      currentFilter = e.target.value;
      load(currentFilter);
    });

    load(currentFilter);
  });
};
