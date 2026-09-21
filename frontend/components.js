// Shared, reusable UI building blocks: badges, toasts, topic cache,
// and the generic Question renderer used by Practice/Drill/Weaknesses/Exam/Explore.

const Components = (function () {

  // ---- Topic metadata cache (id -> {title, category}) ----
  let curriculumPromise = null;
  function ensureCurriculumLoaded() {
    if (!curriculumPromise) {
      curriculumPromise = Api.getCurriculum().catch(function (e) {
        curriculumPromise = null;
        throw e;
      });
    }
    return curriculumPromise;
  }
  function getTopicMeta(curriculum, topicId) {
    if (!curriculum || !topicId) return null;
    for (let i = 0; i < curriculum.topics.length; i++) {
      if (curriculum.topics[i].id === topicId) return curriculum.topics[i];
    }
    return null;
  }

  // ---- Toasts ----
  function showToast(message, kind) {
    const root = document.getElementById("toast-root");
    if (!root) { window.alert(message); return; }
    const el = document.createElement("div");
    el.className = "toast" + (kind === "info" ? " info" : "");
    el.textContent = message;
    root.appendChild(el);
    setTimeout(function () {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.3s";
      setTimeout(function () { el.remove(); }, 300);
    }, 4200);
  }

  function reportError(err, context) {
    console.error(context || "", err);
    showToast((context ? context + ": " : "") + (err && err.message ? err.message : String(err)));
  }

  // ---- Badges ----
  function badgeHtml(category) {
    const map = { core: "Official", legacy: "Legacy", supplementary: "Supplementary" };
    const cls = { core: "badge-core", legacy: "badge-legacy", supplementary: "badge-supplementary" };
    const label = map[category] || category || "Unknown";
    const c = cls[category] || "badge-unknown";
    return '<span class="badge ' + c + '">' + escapeHtml(label) + "</span>";
  }

  function difficultyDotsHtml(n) {
    n = n || 1;
    let out = '<span class="difficulty-dots">';
    for (let i = 1; i <= 5; i++) {
      out += '<span class="' + (i <= n ? "on" : "") + '"></span>';
    }
    return out + "</span>";
  }

  function statusLabel(status) {
    const map = { strong: "Strong", developing: "Developing", weak: "Weak", untouched: "Untouched" };
    return map[status] || status;
  }

  function barFillClass(status) {
    if (status === "strong") return "good";
    if (status === "developing") return "";
    if (status === "weak") return "bad";
    return "";
  }

  // ---- Generic Question renderer ----
  // Returns { el: HTMLElement, getAnswer: () => answerValue, disable: () => void }
  function renderQuestionInput(question) {
    const wrap = document.createElement("div");
    wrap.className = "question-input";
    let getAnswer = function () { return null; };
    let disableFn = function () {};

    if (question.type === "mcq") {
      const choices = question.choices || [];
      let selected = null;
      const rows = [];
      choices.forEach(function (choiceText) {
        const row = document.createElement("label");
        row.className = "choice-row";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = "mcq_" + question.id;
        input.value = choiceText;
        input.addEventListener("change", function () {
          selected = choiceText;
          rows.forEach(function (r) { r.classList.remove("selected"); });
          row.classList.add("selected");
        });
        const span = document.createElement("span");
        span.innerHTML = mdInline(choiceText);
        row.appendChild(input);
        row.appendChild(span);
        wrap.appendChild(row);
        rows.push(row);
      });
      getAnswer = function () { return selected; };
      disableFn = function () {
        wrap.querySelectorAll("input").forEach(function (i) { i.disabled = true; });
      };
    } else if (question.type === "proof_step") {
      const blanks = question.blanks || [];
      const options = question.blank_options || [];
      const selects = [];
      blanks.forEach(function (blankLabel, idx) {
        const row = document.createElement("div");
        row.className = "blank-row";
        const num = document.createElement("div");
        num.className = "blank-index";
        num.textContent = String(idx + 1);
        const select = document.createElement("select");
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select justification…";
        select.appendChild(placeholder);
        (options[idx] || []).forEach(function (opt) {
          const o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          select.appendChild(o);
        });
        row.appendChild(num);
        row.appendChild(select);
        wrap.appendChild(row);
        selects.push(select);
      });
      getAnswer = function () { return selects.map(function (s) { return s.value; }); };
      disableFn = function () { selects.forEach(function (s) { s.disabled = true; }); };
    } else if (question.type === "code_write") {
      const textarea = document.createElement("textarea");
      textarea.rows = 10;
      textarea.spellcheck = false;
      textarea.value = question.starter_code || "";
      textarea.addEventListener("keydown", function (e) {
        if (e.key === "Tab") {
          e.preventDefault();
          const s = textarea.selectionStart, en = textarea.selectionEnd;
          textarea.value = textarea.value.substring(0, s) + "    " + textarea.value.substring(en);
          textarea.selectionStart = textarea.selectionEnd = s + 4;
        }
      });
      wrap.appendChild(textarea);

      const btnRow = document.createElement("div");
      btnRow.className = "btn-row";
      const runBtn = document.createElement("button");
      runBtn.type = "button";
      runBtn.textContent = "Run code";
      btnRow.appendChild(runBtn);
      wrap.appendChild(btnRow);

      const consoleEl = document.createElement("div");
      consoleEl.className = "console";
      consoleEl.style.marginTop = "10px";
      consoleEl.innerHTML = '<span class="placeholder">Output will appear here.</span>';
      wrap.appendChild(consoleEl);

      runBtn.addEventListener("click", function () {
        runBtn.disabled = true;
        runBtn.textContent = "Running…";
        consoleEl.innerHTML = '<span class="placeholder">Running…</span>';
        Api.runFsharp(textarea.value).then(function (res) {
          renderConsole(consoleEl, res);
        }).catch(function (e) {
          consoleEl.innerHTML = '<span class="stderr">' + escapeHtml(e.message) + "</span>";
        }).finally(function () {
          runBtn.disabled = false;
          runBtn.textContent = "Run code";
        });
      });

      getAnswer = function () { return textarea.value; };
      disableFn = function () { textarea.disabled = true; runBtn.disabled = true; };
    } else if (question.type === "lambda_reduce") {
      if (question.lambda_expr) {
        const exprBox = document.createElement("pre");
        exprBox.innerHTML = "<code>" + escapeHtml(question.lambda_expr) + "</code>";
        wrap.appendChild(exprBox);
      }
      const input = document.createElement("input");
      input.type = "text";
      input.placeholder = "Fully reduced normal form, e.g. \\x.x";
      wrap.appendChild(input);
      getAnswer = function () { return input.value; };
      disableFn = function () { input.disabled = true; };
    } else {
      // trace | fill_blank | short_answer
      const input = document.createElement("input");
      input.type = "text";
      input.placeholder = question.type === "trace" ? "Predicted output…" : "Your answer…";
      wrap.appendChild(input);
      getAnswer = function () { return input.value; };
      disableFn = function () { input.disabled = true; };
      wrap.dataset.autofocus = "1";
      setTimeout(function () { input.focus(); }, 30);
    }

    return { el: wrap, getAnswer: getAnswer, disable: disableFn };
  }

  function renderConsole(consoleEl, res) {
    let html = "";
    if (res.stdout) html += '<div class="stdout">' + escapeHtml(res.stdout) + "</div>";
    if (res.stderr) html += '<div class="stderr">' + escapeHtml(res.stderr) + "</div>";
    if (!res.stdout && !res.stderr) html = '<span class="placeholder">(no output)</span>';
    if (res.timed_out) html += '<div class="stderr">Execution timed out.</div>';
    consoleEl.innerHTML = html;
  }

  // Renders a full question card (meta + prompt + code + input) into a container.
  // Returns { getAnswer, disable, inputEl }
  function renderQuestionCard(container, question, opts) {
    opts = opts || {};
    container.innerHTML = "";
    const block = document.createElement("div");
    block.className = "question-block";

    const meta = document.createElement("div");
    meta.className = "question-meta";
    meta.innerHTML = badgeHtml(opts.topicCategory || "core") +
      '<span style="color:var(--text-faint);font-size:12px;">' + escapeHtml(question.topic_id || "") + "</span>" +
      difficultyDotsHtml(question.difficulty) +
      '<span style="color:var(--text-faint);font-size:11px;text-transform:uppercase;letter-spacing:.04em;">' + escapeHtml(question.type.replace("_", " ")) + "</span>";
    block.appendChild(meta);

    const promptEl = document.createElement("div");
    promptEl.innerHTML = renderMarkdown(question.prompt || "");
    block.appendChild(promptEl);

    if (question.code) {
      const codePre = document.createElement("pre");
      codePre.innerHTML = "<code>" + escapeHtml(question.code) + "</code>";
      block.appendChild(codePre);
    }

    const inputArea = document.createElement("div");
    inputArea.style.marginTop = "14px";
    block.appendChild(inputArea);
    const inputCtl = renderQuestionInput(question);
    inputArea.appendChild(inputCtl.el);

    container.appendChild(block);
    return { block: block, getAnswer: inputCtl.getAnswer, disable: inputCtl.disable };
  }

  function renderResultPanel(container, result) {
    const panel = document.createElement("div");
    const kind = result.correct === true ? "correct" : (result.correct === "partial" ? "partial" : "incorrect");
    panel.className = "result-panel " + kind;
    const title = kind === "correct" ? "Correct" : (kind === "partial" ? "Partially correct" : "Not quite");
    let html = '<div class="result-title">' + title + (typeof result.score === "number" ? " — " + Math.round(result.score * 100) + "%" : "") + "</div>";
    html += renderMarkdown(result.explanation || "");
    if (result.mistake_category) {
      html += '<span class="mistake-tag">Mistake type: ' + escapeHtml(result.mistake_category) + "</span>";
    }
    panel.innerHTML = html;

    if (result.run_result) {
      const consoleEl = document.createElement("div");
      consoleEl.className = "console";
      consoleEl.style.marginTop = "10px";
      renderConsole(consoleEl, result.run_result);
      panel.appendChild(consoleEl);
    }
    container.appendChild(panel);
    return panel;
  }

  return {
    ensureCurriculumLoaded: ensureCurriculumLoaded,
    getTopicMeta: getTopicMeta,
    showToast: showToast,
    reportError: reportError,
    badgeHtml: badgeHtml,
    difficultyDotsHtml: difficultyDotsHtml,
    statusLabel: statusLabel,
    barFillClass: barFillClass,
    renderQuestionCard: renderQuestionCard,
    renderResultPanel: renderResultPanel,
    renderConsole: renderConsole
  };
})();
