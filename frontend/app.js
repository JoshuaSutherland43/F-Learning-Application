// Entry point: registers all routes and boots the router.
(function () {
  Router.register("dashboard", Views.dashboard);
  Router.register("learn", Views.learn);
  Router.register("practice", Views.practice);
  Router.register("drill", Views.drill);
  Router.register("weaknesses", Views.weaknesses);
  Router.register("exam", Views.exam);
  Router.register("review", Views.review);
  Router.register("explore", Views.explore);
  Router.register("codelab", Views.codelab);
  Router.setDefault("dashboard");

  document.addEventListener("DOMContentLoaded", function () {
    Router.start();
  });
  // In case the script runs after DOMContentLoaded already fired.
  if (document.readyState === "complete" || document.readyState === "interactive") {
    Router.start();
  }
})();
