// Tiny dependency-free markdown -> HTML renderer.
// Supports: # / ## / ### headings, **bold**, `inline code`, fenced ```lang code blocks,
// "- " bullet lists, "1. " numbered lists, and paragraphs. Nothing else.

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function mdInline(text) {
  let s = escapeHtml(text);
  // inline code `x`
  s = s.replace(/`([^`]+)`/g, function (m, code) { return "<code>" + code + "</code>"; });
  // bold **x**
  s = s.replace(/\*\*([^*]+)\*\*/g, function (m, b) { return "<strong>" + b + "</strong>"; });
  return s;
}

function renderMarkdown(src) {
  if (!src) return "";
  const lines = String(src).replace(/\r\n/g, "\n").split("\n");
  let html = [];
  let i = 0;
  let para = [];

  function flushPara() {
    if (para.length) {
      html.push("<p>" + mdInline(para.join(" ")) + "</p>");
      para = [];
    }
  }

  while (i < lines.length) {
    const line = lines[i];

    // fenced code block
    const fence = line.match(/^```(\w*)\s*$/);
    if (fence) {
      flushPara();
      const lang = fence[1] || "";
      const codeLines = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing fence
      html.push('<pre><code class="lang-' + escapeHtml(lang) + '">' + escapeHtml(codeLines.join("\n")) + "</code></pre>");
      continue;
    }

    // headings
    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      flushPara();
      const level = heading[1].length;
      html.push("<h" + level + ">" + mdInline(heading[2]) + "</h" + level + ">");
      i++;
      continue;
    }

    // bullet list
    if (/^\s*[-*]\s+/.test(line)) {
      flushPara();
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
        i++;
      }
      html.push("<ul>" + items.map(function (it) { return "<li>" + mdInline(it) + "</li>"; }).join("") + "</ul>");
      continue;
    }

    // numbered list
    if (/^\s*\d+\.\s+/.test(line)) {
      flushPara();
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
        i++;
      }
      html.push("<ol>" + items.map(function (it) { return "<li>" + mdInline(it) + "</li>"; }).join("") + "</ol>");
      continue;
    }

    // blank line
    if (/^\s*$/.test(line)) {
      flushPara();
      i++;
      continue;
    }

    // paragraph text
    para.push(line.trim());
    i++;
  }
  flushPara();
  return '<div class="md">' + html.join("\n") + "</div>";
}
