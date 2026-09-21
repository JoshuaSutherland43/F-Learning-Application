var Views = window.Views = window.Views || {};

const CODELAB_DEFAULT = "// Write F# here and press Run, or Debug this if something's wrong.\nlet rec factorial n =\n    match n with\n    | 0 -> 1\n    | n -> n * factorial (n - 1)\n\nprintfn \"%d\" (factorial 5)\n";

Views.codelab = function (container) {
  let html = '<h1 class="page-title">Code Lab</h1>';
  html += '<p class="page-subtitle">Write, run, and debug real F# — executed locally via <code>dotnet fsi</code>.</p>';
  html += '<div class="card">';
  html += '<textarea id="lab-code" rows="16" spellcheck="false">' + escapeHtml(CODELAB_DEFAULT) + '</textarea>';
  html += '<div class="btn-row">';
  html += '<button class="primary" id="lab-run">Run</button>';
  html += '<button id="lab-debug">Debug this</button>';
  html += '<span id="lab-status" style="align-self:center;color:var(--text-faint);font-size:12px;"></span>';
  html += '</div>';
  html += '<div class="field" style="margin-top:12px;"><label>What did you expect to happen? (optional, helps the debug tutor)</label>';
  html += '<input type="text" id="lab-expectation" placeholder="e.g. I expected it to print the sum of the list"></div>';
  html += '</div>';

  html += '<div class="card"><div class="card-title">Console</div><div class="console" id="lab-console"><span class="placeholder">Run your code to see output here.</span></div></div>';
  html += '<div id="lab-debug-output"></div>';

  container.innerHTML = html;

  const codeEl = document.getElementById("lab-code");
  codeEl.addEventListener("keydown", function (e) {
    if (e.key === "Tab") {
      e.preventDefault();
      const s = codeEl.selectionStart, en = codeEl.selectionEnd;
      codeEl.value = codeEl.value.substring(0, s) + "    " + codeEl.value.substring(en);
      codeEl.selectionStart = codeEl.selectionEnd = s + 4;
    }
  });

  document.getElementById("lab-run").addEventListener("click", function () {
    const btn = document.getElementById("lab-run");
    const consoleEl = document.getElementById("lab-console");
    const statusEl = document.getElementById("lab-status");
    btn.disabled = true;
    statusEl.textContent = "Running…";
    consoleEl.innerHTML = '<span class="placeholder">Running…</span>';
    const t0 = Date.now();
    Api.runFsharp(codeEl.value).then(function (res) {
      Components.renderConsole(consoleEl, res);
      statusEl.textContent = (res.duration_ms || (Date.now() - t0)) + " ms · " + (res.success ? "success" : "failed");
    }).catch(function (e) {
      consoleEl.innerHTML = '<span class="stderr">' + escapeHtml(e.message) + "</span>";
      statusEl.textContent = "";
    }).finally(function () { btn.disabled = false; });
  });

  document.getElementById("lab-debug").addEventListener("click", function () {
    const btn = document.getElementById("lab-debug");
    const outEl = document.getElementById("lab-debug-output");
    btn.disabled = true;
    outEl.innerHTML = '<div class="loading-shell">Analysing your code…</div>';
    const expectation = document.getElementById("lab-expectation").value;
    Api.debugFsharp(codeEl.value, expectation).then(function (res) {
      renderDebugResult(outEl, res, codeEl);
    }).catch(function (e) {
      Components.reportError(e, "Debug tutor failed");
      outEl.innerHTML = '<div class="empty-state">Could not analyse this code.</div>';
    }).finally(function () { btn.disabled = false; });
  });
};

function renderDebugResult(outEl, res, codeEl) {
  let html = '<div class="card"><div class="card-title">1. What is wrong</div>' + renderMarkdown(res.diagnosis || "_Nothing detected — your code looks fine._") + '</div>';
  if (res.why) html += '<div class="card"><div class="card-title">2. Why it is wrong</div>' + renderMarkdown(res.why) + '</div>';
  if (res.how_to_fix_reasoning) html += '<div class="card"><div class="card-title">3. How to reason about fixing it</div>' + renderMarkdown(res.how_to_fix_reasoning) + '</div>';

  outEl.innerHTML = html;

  if (res.corrected_code) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = '<div class="card-title">4. Corrected solution</div>';
    const revealBtn = document.createElement("button");
    revealBtn.textContent = "Reveal corrected code";
    card.appendChild(revealBtn);
    const codeBlock = document.createElement("pre");
    codeBlock.style.display = "none";
    codeBlock.innerHTML = "<code>" + escapeHtml(res.corrected_code) + "</code>";
    card.appendChild(codeBlock);
    const useBtn = document.createElement("button");
    useBtn.textContent = "Use this in the editor";
    useBtn.style.display = "none";
    useBtn.style.marginTop = "8px";
    card.appendChild(useBtn);
    revealBtn.addEventListener("click", function () {
      codeBlock.style.display = "block";
      useBtn.style.display = "inline-block";
      revealBtn.remove();
    });
    useBtn.addEventListener("click", function () { codeEl.value = res.corrected_code; Components.showToast("Editor updated.", "info"); });
    outEl.appendChild(card);
  }

  if (res.compiler_output && (res.compiler_output.stdout || res.compiler_output.stderr)) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = '<div class="card-title">Compiler / runtime output</div>';
    const consoleEl = document.createElement("div");
    consoleEl.className = "console";
    Components.renderConsole(consoleEl, res.compiler_output);
    card.appendChild(consoleEl);
    outEl.appendChild(card);
  }
}
