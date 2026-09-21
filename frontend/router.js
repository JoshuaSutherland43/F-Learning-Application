// Minimal hash router. Routes are registered as a name -> render(container, params[]) function.
// URL shape: #/route/param1/param2

const Router = (function () {
  const routes = {};
  let defaultRoute = "dashboard";
  const appEl = document.getElementById("app");

  function register(name, handler) {
    routes[name] = handler;
  }

  function setDefault(name) {
    defaultRoute = name;
  }

  function parseHash() {
    let hash = window.location.hash || "";
    hash = hash.replace(/^#\/?/, "");
    if (!hash) return { name: defaultRoute, params: [] };
    const parts = hash.split("/").filter(function (p) { return p.length > 0; });
    return { name: parts[0] || defaultRoute, params: parts.slice(1) };
  }

  function updateNav(routeName) {
    document.querySelectorAll("#main-nav a").forEach(function (a) {
      if (a.getAttribute("data-route") === routeName) {
        a.classList.add("active");
      } else {
        a.classList.remove("active");
      }
    });
  }

  function render() {
    const r = parseHash();
    updateNav(r.name);
    const handler = routes[r.name];
    appEl.innerHTML = '<div class="loading-shell">Loading…</div>';
    window.scrollTo(0, 0);
    if (!handler) {
      appEl.innerHTML = '<div class="empty-state"><div class="icon">?</div><div>Unknown view.</div></div>';
      return;
    }
    try {
      const result = handler(appEl, r.params);
      if (result && typeof result.catch === "function") {
        result.catch(function (e) { Components.reportError(e, "Failed to load view"); });
      }
    } catch (e) {
      Components.reportError(e, "Failed to render view");
    }
  }

  function go(path) {
    window.location.hash = path;
  }

  window.addEventListener("hashchange", render);

  return { register: register, setDefault: setDefault, start: render, go: go };
})();
