// Thin fetch wrapper around the backend REST API.
// Every function returns a Promise resolving to parsed JSON, and throws
// an Error (with a human-readable .message) on failure so callers can
// catch once and show a toast.

const Api = (function () {
  const BASE = "";

  async function handle(res) {
    let body = null;
    const text = await res.text();
    try {
      body = text ? JSON.parse(text) : null;
    } catch (e) {
      body = null;
    }
    if (!res.ok) {
      const msg = (body && body.error) ? body.error : ("Request failed (" + res.status + ")");
      throw new Error(msg);
    }
    return body;
  }

  function qs(params) {
    if (!params) return "";
    const parts = [];
    Object.keys(params).forEach(function (k) {
      const v = params[k];
      if (v === undefined || v === null) return;
      parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
    });
    return parts.length ? ("?" + parts.join("&")) : "";
  }

  function get(path, params) {
    return fetch(BASE + path + qs(params), {
      method: "GET",
      headers: { "Accept": "application/json" }
    }).then(handle);
  }

  function post(path, body) {
    return fetch(BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(body || {})
    }).then(handle);
  }

  return {
    getCurriculum: function () { return get("/api/curriculum"); },
    getTopic: function (id) { return get("/api/topic/" + encodeURIComponent(id)); },
    getSyntax: function () { return get("/api/syntax"); },
    getQuestion: function (params) { return get("/api/question", params); },
    submitAnswer: function (payload) { return post("/api/answer", payload); },
    runFsharp: function (code) { return post("/api/run-fsharp", { code: code }); },
    debugFsharp: function (code, question) { return post("/api/debug-fsharp", { code: code, question: question || "" }); },
    startExam: function (payload) { return post("/api/exam/start", payload); },
    submitExam: function (payload) { return post("/api/exam/submit", payload); },
    getProgress: function () { return get("/api/progress"); },
    getReview: function (params) { return get("/api/review", params); },
    tutor: function (payload) { return post("/api/tutor", payload); }
  };
})();
