var Views = window.Views = window.Views || {};

const LEVEL_ORDER = [
  ["what_is_it", "1. What is it?"],
  ["syntax", "2. Syntax"],
  ["how_it_works", "3. How it works"],
  ["worked_example", "4. Worked example"],
  ["variations", "5. Variations"],
  ["exam_application", "6. Exam application"],
  ["common_mistakes", "7. Common mistakes"]
];

Views.learn = function (container, params) {
  const requested = params && params[0] ? decodeURIComponent(params[0]) : null;

  return Components.ensureCurriculumLoaded().then(function (curriculum) {
    const showSyntax = requested === "syntax";
    let activeId = requested;
    if (!activeId || activeId === "syntax") {
      const sorted = curriculum.topics.slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
      activeId = sorted.length ? sorted[0].id : null;
    }

    container.innerHTML =
      '<h1 class="page-title">Learn</h1>' +
      '<p class="page-subtitle">Work through every concept from first principles to exam application.</p>' +
      '<div class="split">' +
      '<div class="topic-list" id="learn-nav">' + renderNav(curriculum, showSyntax ? "syntax" : activeId) + '</div>' +
      '<div id="learn-detail"><div class="loading-shell">Loading…</div></div>' +
      '</div>';

    document.getElementById("learn-nav").addEventListener("click", function (e) {
      const item = e.target.closest(".topic-item");
      if (!item) return;
      Router.go("/learn/" + item.dataset.id);
    });

    if (showSyntax) {
      return renderSyntaxReference(document.getElementById("learn-detail"));
    } else if (activeId) {
      return renderTopicDetail(document.getElementById("learn-detail"), activeId, curriculum);
    }
  });
};

function renderNav(curriculum, activeId) {
  const parts = [];
  parts.push('<div class="topic-item' + (activeId === "syntax" ? " active" : "") + '" data-id="syntax">\u{1F4D1} Syntax Reference</div>');
  curriculum.categories.forEach(function (cat) {
    const topics = curriculum.topics
      .filter(function (t) { return t.category === cat.id; })
      .sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
    if (!topics.length) return;
    parts.push('<div class="topic-group-label">' + escapeHtml(cat.label) + '</div>');
    topics.forEach(function (t) {
      parts.push('<div class="topic-item' + (t.id === activeId ? " active" : "") + '" data-id="' + escapeHtml(t.id) + '">' + escapeHtml(t.title) + '</div>');
    });
  });
  return parts.join("\n");
}

function renderTopicDetail(el, topicId, curriculum) {
  el.innerHTML = '<div class="loading-shell">Loading…</div>';
  return Api.getTopic(topicId).then(function (topic) {
    const meta = Components.getTopicMeta(curriculum, topicId);
    let html = '<div class="card">';
    html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">';
    html += '<h2 style="margin:0;font-size:19px;">' + escapeHtml(topic.title) + '</h2>';
    html += Components.badgeHtml(topic.category);
    html += '</div>';
    if (meta && meta.summary) html += '<p style="color:var(--text-dim);margin:0;">' + escapeHtml(meta.summary) + '</p>';
    html += '</div>';

    LEVEL_ORDER.forEach(function (pair, idx) {
      const key = pair[0], label = pair[1];
      const content = topic.levels && topic.levels[key];
      if (!content) return;
      html += '<div class="level-section' + (idx === 0 ? " open" : "") + '" data-level="' + key + '">';
      html += '<div class="level-header"><span>' + escapeHtml(label) + '</span><span class="level-chevron">▸</span></div>';
      html += '<div class="level-body">' + renderMarkdown(content) + '</div>';
      html += '</div>';
    });

    // Level 8: practice
    html += '<div class="level-section" data-level="practice">';
    html += '<div class="level-header"><span>8. Practice</span><span class="level-chevron">▸</span></div>';
    html += '<div class="level-body"><p style="color:var(--text-dim);">Generate a question on this topic right now.</p>';
    html += '<button class="primary" id="learn-practice-btn">Give me a question</button>';
    html += '<div id="learn-practice-area" style="margin-top:14px;"></div>';
    html += '</div></div>';

    if (topic.syntax_refs && topic.syntax_refs.length) {
      html += '<div class="card"><div class="card-title">Related Syntax</div><div class="chip-row">';
      topic.syntax_refs.forEach(function (ref) {
        html += '<a class="chip" href="#/learn/syntax">' + escapeHtml(ref) + '</a>';
      });
      html += '</div></div>';
    }

    el.innerHTML = html;

    el.querySelectorAll(".level-header").forEach(function (h) {
      h.addEventListener("click", function () {
        h.parentElement.classList.toggle("open");
      });
    });

    const practiceTopicId = (topic.practice_topic_ids && topic.practice_topic_ids[0]) || topicId;
    const btn = document.getElementById("learn-practice-btn");
    if (btn) {
      btn.addEventListener("click", function () {
        loadInlinePractice(document.getElementById("learn-practice-area"), practiceTopicId, topic.category);
      });
    }
  }).catch(function (e) {
    Components.reportError(e, "Could not load topic");
    el.innerHTML = '<div class="empty-state">Could not load this topic.</div>';
  });
}

function loadInlinePractice(container, topicId, category) {
  container.innerHTML = '<div class="loading-shell">Generating question…</div>';
  Api.getQuestion({ mode: "practice", topic: topicId }).then(function (q) {
    const startedAt = Date.now();
    const ctl = Components.renderQuestionCard(container, q, { topicCategory: category });
    const btnRow = document.createElement("div");
    btnRow.className = "btn-row";
    const submitBtn = document.createElement("button");
    submitBtn.className = "primary";
    submitBtn.textContent = "Check answer";
    btnRow.appendChild(submitBtn);
    ctl.block.appendChild(btnRow);

    submitBtn.addEventListener("click", function () {
      const answer = ctl.getAnswer();
      submitBtn.disabled = true;
      Api.submitAnswer({
        question_id: q.id, question: q, answer: answer,
        time_taken_seconds: Math.round((Date.now() - startedAt) / 1000)
      }).then(function (result) {
        ctl.disable();
        Components.renderResultPanel(ctl.block, result);
        submitBtn.remove();
        const again = document.createElement("button");
        again.textContent = "Another question";
        again.className = "btn-row-btn";
        again.style.marginTop = "10px";
        again.addEventListener("click", function () { loadInlinePractice(container, topicId, category); });
        container.appendChild(again);
      }).catch(function (e) {
        Components.reportError(e, "Could not submit answer");
        submitBtn.disabled = false;
      });
    });
  }).catch(function (e) {
    Components.reportError(e, "Could not generate question");
    container.innerHTML = '<div class="empty-state">No question available for this topic yet.</div>';
  });
}

function renderSyntaxReference(el) {
  el.innerHTML = '<div class="loading-shell">Loading…</div>';
  return Api.getSyntax().then(function (data) {
    const entries = data.entries || [];
    let html = '<input type="text" class="search-input" id="syntax-search" placeholder="Search syntax (e.g. match, fold, tuple)…">';
    html += '<div id="syntax-list"></div>';
    el.innerHTML = html;

    function draw(filter) {
      const f = (filter || "").toLowerCase();
      const filtered = entries.filter(function (e) {
        if (!f) return true;
        return (e.title + " " + e.category + " " + e.syntax + " " + e.meaning).toLowerCase().indexOf(f) !== -1;
      });
      const groups = {};
      filtered.forEach(function (e) {
        groups[e.category] = groups[e.category] || [];
        groups[e.category].push(e);
      });
      let out = "";
      Object.keys(groups).sort().forEach(function (cat) {
        out += '<h3 style="color:var(--text-faint);font-size:12px;text-transform:uppercase;letter-spacing:.05em;margin:18px 0 8px;">' + escapeHtml(cat) + '</h3>';
        groups[cat].forEach(function (e) {
          out += '<div class="syntax-card"><h4>' + escapeHtml(e.title) + '</h4>';
          out += '<div class="syntax-row"><div class="k">Syntax</div><div class="v"><pre><code>' + escapeHtml(e.syntax) + '</code></pre></div></div>';
          out += '<div class="syntax-row"><div class="k">Meaning</div><div class="v">' + escapeHtml(e.meaning) + '</div></div>';
          if (e.example) out += '<div class="syntax-row"><div class="k">Example</div><div class="v">' + renderMarkdown(e.example) + '</div></div>';
          if (e.common_mistake) out += '<div class="syntax-row"><div class="k">Common mistake</div><div class="v">' + escapeHtml(e.common_mistake) + '</div></div>';
          if (e.exam_use) out += '<div class="syntax-row"><div class="k">Exam use</div><div class="v">' + escapeHtml(e.exam_use) + '</div></div>';
          out += '</div>';
        });
      });
      document.getElementById("syntax-list").innerHTML = out || '<div class="empty-state">No matches.</div>';
    }

    document.getElementById("syntax-search").addEventListener("input", function (e) { draw(e.target.value); });
    draw("");
  }).catch(function (e) {
    Components.reportError(e, "Could not load syntax reference");
    el.innerHTML = '<div class="empty-state">Could not load syntax reference.</div>';
  });
}
