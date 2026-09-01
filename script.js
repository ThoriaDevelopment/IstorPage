// Istor site behaviour: theme toggle + the timed privacy rotator.
// Deliberately small; the page works without this script.

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
    // The toggle flips the visible world and stores a plain light/dark
    // choice; a "system" preference resolves to one of the two.
    var nextDark = !isDark();
    try { localStorage.setItem(KEY, nextDark ? "dark" : "light"); } catch (_) {}
    applyTheme(nextDark);
  });

  // ── privacy rotator ────────────────────────────────────────────
  // The bar is the clock: it sweeps the full width once per interval and,
  // when it hits the end, the list advances to the next claim. Hovering
  // pauses the sweep in place; leaving resumes from where it stopped. The
  // dots below the bar jump straight to a claim.
  var rotator = document.querySelector(".rotator");
  if (!rotator) return;

  var items = rotator.querySelectorAll("li");
  var tabs = rotator.querySelectorAll(".rotor-dots [role='tab']");
  var bar = rotator.querySelector(".rotor-bar span");
  var INTERVAL = 4200;
  var index = 0;
  var elapsed = 0;          // ms into the current sweep
  var paused = false;
  var last = null;

  function show(n) {
    items[index].classList.remove("active");
    tabs[index].classList.remove("active");
    tabs[index].setAttribute("aria-selected", "false");
    index = n;
    items[index].classList.add("active");
    tabs[index].classList.add("active");
    tabs[index].setAttribute("aria-selected", "true");
  }

  function frame(ts) {
    if (last === null) last = ts;
    var delta = ts - last;
    last = ts;
    if (!paused) {
      elapsed += delta;
      if (elapsed >= INTERVAL) {
        elapsed = 0;
        show((index + 1) % items.length);
      }
    }
    bar.style.width = (Math.min(elapsed / INTERVAL, 1) * 100) + "%";
    requestAnimationFrame(frame);
  }

  // Reduced motion: no sweep. The bar sits full width as an active marker
  // and the list still rotates on its own.
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    elapsed = 0;
    bar.style.width = "100%";
    setInterval(function () { show((index + 1) % items.length); }, INTERVAL);
  } else {
    requestAnimationFrame(frame);

    rotator.addEventListener("mouseenter", function () { paused = true; });
    rotator.addEventListener("mouseleave", function () { paused = false; });
    rotator.addEventListener("focusin", function () { paused = true; });
    rotator.addEventListener("focusout", function () { paused = false; });
  }

  tabs.forEach(function (tab, n) {
    tab.addEventListener("click", function () {
      elapsed = 0;
      show(n);
    });
  });
})();