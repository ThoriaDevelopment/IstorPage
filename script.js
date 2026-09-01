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
    // dark is stamped directly; light is stamped too, so it beats a
    // dark OS preference in the stylesheet
    document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
  }

  document.querySelector(".theme-toggle").addEventListener("click", function () {
    // The toggle flips the visible world and stores a plain light/dark
    // choice; a "system" preference resolves to one of the two.
    var nextDark = !isDark();
    try { localStorage.setItem(KEY, nextDark ? "dark" : "light"); } catch (_) {}
    applyTheme(nextDark);
  });

  // A stored choice survives the reload; "system" resolves the same
  // way the stylesheet's media query does, with or without this script.
  applyTheme(isDark());

  // ── hero entrance ──────────────────────────────────────────────
  // A short staggered rise on load, applied from here only so a
  // visitor without JavaScript sees the hero immediately.
  if (matchMedia("(prefers-reduced-motion: no-preference)").matches) {
    var heroBits = document.querySelectorAll(".hero > *");
    var entering = [];
    heroBits.forEach(function (el, i) {
      el.classList.add("enter");
      el.style.transitionDelay = (i * 0.07).toFixed(2) + "s";
      entering.push(el);
    });
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        entering.forEach(function (el) {
          el.classList.add("on");
          el.style.transitionDelay = "";
        });
      });
    });
  }

  // ── scroll reveal ──────────────────────────────────────────────
  // Classes are added here rather than in the HTML, so a visitor
  // without JavaScript still sees the full page. Elements already on
  // screen are shown without waiting for the observer.
  if ("IntersectionObserver" in window) {
    var targets = document.querySelectorAll(".story-row, .loop-grid > article");
    var shown = [];
    targets.forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) return;
      el.classList.add("reveal");
      shown.push(el);
    });
    if (shown.length) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("on");
          io.unobserve(entry.target);
        });
      }, { threshold: 0.12 });
      shown.forEach(function (el) { io.observe(el); });
    }
  }

  // ── the 3d page ────────────────────────────────────────────────
  // The sheet rotates as the reader moves through its section: the
  // scroll progress across the stage maps onto rotateX/rotateY.
  var sheet = document.getElementById("sheet");
  if (sheet && matchMedia("(prefers-reduced-motion: no-preference)").matches) {
    // The scroll progress across the section sets the base pose; the
    // pointer (fine pointers only) leans the sheet a few degrees on
    // top of it. Both feed the same rAF-throttled repaint.
    var baseRX = 9, baseRY = -26;
    var leanX = 0, leanY = 0;
    var flip = document.getElementById("flip");

    function paint() {
      sheet.style.transform = "rotateX(" + (baseRX + leanX).toFixed(2) + "deg) rotateY(" + (baseRY + leanY).toFixed(2) + "deg)";
      if (flip) flip.style.transform = "rotateY(" + flipDeg.toFixed(2) + "deg)";
    }

    var flipDeg = 0;
    var stage = document.getElementById("inside");

    function pose() {
      // progress runs across the whole section while the sheet stays
      // pinned, so the reader always sees the page and its turn
      var r = stage.getBoundingClientRect();
      var p = (window.innerHeight - r.top) / (r.height + window.innerHeight);
      p = Math.max(0, Math.min(1, p));
      baseRY = -30 + 16 * p;
      baseRX = 12 - 8 * p;
      // past the midpoint the page turns over to the answer face
      var q = (p - 0.5) / 0.22;
      flipDeg = Math.max(0, Math.min(1, q)) * 180;
      paint();
    }

    var sheetTick = false;
    function schedule() {
      if (sheetTick) return;
      sheetTick = true;
      requestAnimationFrame(function () { sheetTick = false; pose(); });
    }
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });

    var scene = sheet.closest(".scene");
    if (scene && matchMedia("(pointer: fine)").matches) {
      scene.addEventListener("mousemove", function (e) {
        var r = scene.getBoundingClientRect();
        leanY = ((e.clientX - r.left) / r.width - 0.5) * 7;
        leanX = -((e.clientY - r.top) / r.height - 0.5) * 5;
        schedule();
      });
      scene.addEventListener("mouseleave", function () {
        leanX = 0;
        leanY = 0;
        schedule();
      });
    }

    pose();
  }

  // ── citation preview ───────────────────────────────────────────
  // The mock answer on the landing page carries two live citations;
  // clicking one swaps the quoted passage shown underneath.
  document.querySelectorAll(".answer-mock").forEach(function (mock) {
    var cites = mock.querySelectorAll(".cite");
    var passages = mock.querySelectorAll(".am-passage");
    cites.forEach(function (cite) {
      cite.addEventListener("click", function () {
        var n = cite.getAttribute("data-passage");
        cites.forEach(function (c) { c.classList.toggle("active", c === cite); });
        passages.forEach(function (p) {
          p.classList.toggle("active", p.getAttribute("data-for") === n);
        });
      });
    });
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