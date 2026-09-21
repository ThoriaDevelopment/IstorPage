/* theme.js — the library's theme control.
 *
 * The stylesheet has carried `.theme-toggle`, `.icon-sun` and `.icon-moon`
 * since the library was built, and DESIGN.md documents the mechanism this file
 * completes: "A head script stamps `data-theme` before first paint from the
 * stored choice (`istor.site.theme` in localStorage) or the OS preference." The
 * stamp exists, and it runs before paint, which is why the page never flashes
 * the wrong theme. What was missing was anything that WRITES the stored choice:
 * the only theme a reader could get was their operating system's, and the
 * explicit choice the CSS has a rule for ("an explicit light choice still wins
 * over the media query") was unreachable.
 *
 * FOUR DECISIONS, each a place this could have gone wrong:
 *
 * 1. The control is AUTHORED `hidden` in the markup and this file reveals it. A
 *    button that cannot do anything is worse than no button, so a reader whose
 *    script is blocked gets the page as it was: following their system, with no
 *    inert control on it. Same rule as the hero's question chips.
 *
 * 2. It is one shared file rather than a script in each page. The library is 75
 *    documents that already duplicate an inline theme stamp, and the toggle is
 *    ~1.4 KB: inline it would be 105 KB of duplicated bytes for the same
 *    behaviour, and a fix would be 75 edits.
 *
 * 3. `aria-pressed` carries the state and the label names the state with it —
 *    "Dark theme, pressed" — while `title` names the ACTION a pointer user gets
 *    on hover. A toggle whose label changes to the action it performs reads as
 *    contradictory to a screen reader, which hears the name, not the hover.
 *
 * 4. There is no third "follow the system" position. Removing the stored key
 *    would restore it, but a control that cycles through three states has to
 *    explain itself, and the documented contract is that an explicit choice
 *    wins. So while NO choice is stored the page keeps following the OS as it
 *    always did, live; the first click ends that and makes the choice explicit.
 */

(function () {
  var KEY = 'istor.site.theme';
  var root = document.documentElement;
  var buttons = document.querySelectorAll('.theme-toggle');
  if (!buttons.length) return;

  function stored() {
    try {
      return localStorage.getItem(KEY);
    } catch (e) {
      return null;              /* private mode, or storage disabled */
    }
  }

  function paint() {
    var dark = root.getAttribute('data-theme') === 'dark';
    for (var i = 0; i < buttons.length; i++) {
      var b = buttons[i];
      b.setAttribute('aria-pressed', dark ? 'true' : 'false');
      b.setAttribute('aria-label', dark ? 'Dark theme' : 'Light theme');
      b.setAttribute('title', dark ? 'Switch to the light theme'
                                   : 'Switch to the dark theme');
      b.hidden = false;
    }
  }

  function choose(dark) {
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    try {
      localStorage.setItem(KEY, dark ? 'dark' : 'light');
    } catch (e) { /* the choice still applies to this page */ }
    paint();
  }

  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function () {
      choose(root.getAttribute('data-theme') !== 'dark');
    });
  }
  paint();

  /* While no choice is stored, follow the system as it changes. Once the reader
     has chosen, an OS flip must not overrule them, which is the whole point of
     storing it. */
  if (!stored() && window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var follow = function () {
      if (!stored()) {
        root.setAttribute('data-theme', mq.matches ? 'dark' : 'light');
        paint();
      }
    };
    if (mq.addEventListener) mq.addEventListener('change', follow);
    else if (mq.addListener) mq.addListener(follow);   /* Safari < 14 */
  }
})();

/* ── the arrivals (M21) ───────────────────────────────────────────────────────
 *
 * The stylesheet carried `.enter` and `.reveal` since the library was built, and
 * for the same reason the theme control was needed: the classes described an
 * arrival nothing could trigger. No library page was ever wired to them, which is
 * why the fix is here rather than in 78 carried pages - this file is the only
 * shared behaviour every page already loads.
 *
 * FOUR DECISIONS, in the same shape as the theme control's above:
 *
 * 1. AUTHORED VISIBLE, HIDDEN BY SCRIPT. A block is marked `.is-cold` only if it
 *    is below the fold when the script runs, so a reader with no script sees the
 *    finished page and a reader who loads mid-page sees the part they landed on.
 *    The stylesheet's rule and this one are the same rule written twice, which is
 *    the failure this file's sibling note in the landing's markup keeps naming; it
 *    is written twice deliberately, because here the CSS must be safe for pages
 *    that never load this file.
 *
 * 2. ONE CLOCK, AND THE READER'S PACE SETS IT. `--arrive` is the library's single
 *    multiplier (styles.css declares it), and this script adds `.is-quick` to a
 *    block when the reader arrived too fast to watch an arrival finish. The test
 *    is the landing's inequality rather than a threshold picked by feel: the
 *    authored arrival runs ARRIVE_MS, so a reader moving at `pace` px/ms covers
 *    pace * ARRIVE_MS px meanwhile, and if that is further than the screen the
 *    arrival ends off it. Measured, then stated: at 900px this is 1.29 px/ms, which
 *    a flick sustains and a notched read never reaches.
 *
 * 3. THE SAME SAMPLE WINDOW AS THE LANDING. 150ms of scroll samples, trimmed by
 *    TIME (a window that can hold a stale sample is not a window), with the reading
 *    stamped so a stopped scroll cannot leave its last speed standing forever. One
 *    question - how fast is the page moving - and no second listener.
 *
 * 4. REDUCED MOTION IS NOT PACE. Under `prefers-reduced-motion: reduce` nothing is
 *    marked and nothing is observed: the arrivals do not exist, the authored page
 *    is the finished page, and the stylesheet's own reduced-motion block is a
 *    second guard for a page that somehow arrived cold.
 */
(function () {
  var blocks = document.querySelectorAll('.enter, .reveal');
  if (!blocks.length) return;
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var ARRIVE_MS = 700;   /* the longest authored arrival in this library */
  var fly = [], pace = 0, paceAt = -1e9;

  addEventListener('scroll', function () {
    var now = performance.now(), y = window.scrollY;
    fly.push([now, y]);
    while (fly.length && now - fly[0][0] > 150) fly.shift();
    pace = Math.abs(y - fly[0][1]) / Math.max(1, now - fly[0][0]);
    paceAt = now;
  }, { passive: true });

  var io = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (!entries[i].isIntersecting) continue;
      var block = entries[i].target;
      if (performance.now() - paceAt < 320 && pace * ARRIVE_MS > window.innerHeight) {
        block.classList.add('is-quick');
      }
      block.classList.remove('is-cold');
      io.unobserve(block);
    }
  }, { rootMargin: '0px 0px -12% 0px' });

  for (var i = 0; i < blocks.length; i++) {
    var el = blocks[i];
    if (el.getBoundingClientRect().top < window.innerHeight) continue;
    el.classList.add('is-cold');
    io.observe(el);
  }
})();
