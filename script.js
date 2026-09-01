// Istor site behaviour: theme toggle + the timed privacy rotator.
// Deliberately small; the page must work with JS disabled.

(function () {
  "use strict";

  // ── theme toggle ───────────────────────────────────────────────
  var KEY = "istor.site.theme";

  function currentPref() {
    try { return localStorage.getItem(KEY) || "system"; } catch (_) { return "system"; }
  }

  function isDark() {
    return currentPref() === "dark" ||
      (currentPref() === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
  }

  function applyTheme(dark) {
    if (dark) document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
  }

  document.querySelector(".theme-toggle").addEventListener("click", function () {
    // The toggle flips the actual world on screen and stores a plain
    // light/dark choice, so a "system" pref resolves to one of the two.
    var nextDark = !isDark();
    try { localStorage.setItem(KEY, nextDark ? "dark" : "light"); } catch (_) {}
    applyTheme(nextDark);
  });

  // ── privacy rotator ────────────────────────────────────────────
  var rotator = document.querySelector(".rotator");
  if (rotator) {
    var items = rotator.querySelectorAll("li");
    var bar = rotator.querySelector(".rotor-bar span");
    var INTERVAL = 4200;
    var index = 0;
    var timer = null;
    var started = null;

    function show(n) {
      items[index].classList.remove("active");
      index = n;
      items[index].classList.add("active");
    }

    // The bar is the clock: when its run finishes, the list advances.
    function tick(ts) {
      if (!started) started = ts;
      var t = Math.min((ts - started) / INTERVAL, 1);
      bar.style.width = (t * 100) + "%";
      if (t >= 1) {
        started = ts;
        show((index + 1) % items.length);
      }
      requestAnimationFrame(tick);
    }

    function start() { requestAnimationFrame(tick); }

    // Respect reduced motion: the list still rotates, the bar just does
    // not sweep. A full bar marks the active item instead.
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      bar.style.width = "100%";
    } else {
      var running = false;
      function run() { if (!running) { running = true; start(); } }
      run();
      // Pause while the visitor is reading up close.
      rotator.addEventListener("mouseenter", function () { started = null; });
      rotator.addEventListener("mouseleave", function () { started = null; if (!running) { running = true; start(); } });
    }

    rotator.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { started = null; show((index + 1) % items.length); }
      if (e.key === "ArrowLeft") { started = null; show((index - 1 + items.length) % items.length); }
    });
  }
})();