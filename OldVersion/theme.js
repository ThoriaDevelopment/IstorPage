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
