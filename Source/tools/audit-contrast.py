#!/usr/bin/env python3
"""Audit every piece of text in the built site against WCAG AA, in both themes.

    python Source/tools/audit-contrast.py
    python Source/tools/audit-contrast.py --pages / /library/ --json audit.json

**This is an audit, not a gate, and the difference is deliberate.** The three
`verify-*.py` tools run in CI and install nothing, which is why they are pure
standard library. This one drives headless Chrome, so it cannot run there; it is
the tool to run by hand before a release, or after any change to a colour token,
a ground, or a face. It exits non-zero when it finds a real failure, so it can
still be wired into a local pre-push hook.

It renders each page in a **sized iframe** rather than in a sized window, because
`--window-size` sets the OS window and headless Chrome clamps it, so a 1440px
request can come back at something else and the page's media queries then resolve
against a width nobody asked for. The iframe has no such opinion.

WHAT IT MEASURES. For every element with its own text: its computed colour, its
computed size and weight, the ground it actually sits on, and the ratio. AA wants
4.5:1, or 3:1 at 24px, or at 18.66px bold.

IT ALSO MEASURES MOTION, WHICH IS NOT A COLOUR. Every motion item on this site lives
inside `prefers-reduced-motion: no-preference`, so a reader who asks for less motion
is handed the finished page. That is a claim about content that may never appear,
which is why it is checked instead of trusted: the page is rendered twice, once
ordinarily and once with `--force-prefers-reduced-motion`, and the two renders are
compared with each other. Nothing may still be running in the reduced render, and
nothing may be invisible there that the settled ordinary render shows. The
comparison is what makes the check usable: a hover disclosure is invisible in both
renders and is therefore not a finding, so the pass needs no whitelist, and the
first version of it (which trusted the cascade emulation the colour states use)
reported 16 animations running on a page that has none. `--self-test` keeps it
honest: it builds a three-panel page for the question, an entrance inside the
guard, the same entrance outside it, and a paragraph hidden in both renders, and
insists the pass names exactly the one that is wrong.

THE GROUND IS THE HARD PART, and the two wrong ways of doing it are recorded here
because both returned confident numbers rather than errors, which is the only kind
of bug worth writing down:

  * **The ancestor walk.** v1 climbed the parent chain looking for a background.
    That is how CSS is normally written. It is not how this page is written: the
    fields here are absolutely positioned layers, so the ground is a SIBLING
    behind the text. The walk climbed straight past the teal field to the
    document background and reported light ink on paper three times at 1.13:1,
    all of them false. The ground now comes from a hit test, which returns every
    element under the text in front-to-back order, composited back to front.
  * **The pseudo-element.** v2 read the CTA's ink against the button's own
    background, at 1:1, because the button's gradient belongs to a `::before` and
    pseudo-elements are not in a hit test at all. They are now composited in,
    immediately above their host's own background and below its text.
  * **The frame.** v2's first run audited 7 elements of a 3,000px document and
    reported zero failures, because a hit test only sees the viewport. The page is
    therefore swept in viewport-sized steps with instant scrolling, and the report
    prints how many viewports were walked so that a thin run is visible as thin.
    (`html { scroll-behavior: smooth }` is why the scroll is instant: a smooth
    scroll under Chrome's virtual-time clock can still be in flight at the end.)
  * **The screenshot.** A single full-page capture is not available: Chrome
    clamps a very tall window, so the pixels past the clamp do not exist and a
    first attempt read white for everything below it. It is one screenshot per
    viewport instead, and each element names the viewport it was measured in.
  * **The untranslated rect.** The scroll offset has to come off every rect, line
    boxes included. v3 subtracted it from the block box and left the line rects in
    page coordinates, so sticky elements, which move with the scroll, were sampled
    tens of pixels away from their own text. What found it was the diagnostic that
    prints a rect beside its lines and its image size.

A GRADIENT IS MEASURED FROM ITS PIXELS, not from the cascade. Each element's ground
is read from the rendered pixels just above and just below its text boxes, where
the ground shows through untouched by glyphs, and the worst sample wins, so the
number errs toward failure rather than toward a pass. Its three stated limits: the
strips bracket a vertical gradient at its two ends and would miss a dip between
them; anything else painted in a strip (a hairline, a neighbouring label) lands in
the sample, which can report a failure a human would call a false alarm while still
never passing a ground that is darker somewhere; and the sampled luminance range is
printed beside every ratio, so a wide spread reads as a wide spread instead of
hiding behind one number. A ground that is a photograph or a mask is still not
measured, and is still counted rather than guessed.

WHAT IT EMULATES, AND IN TWO PLACES. Chrome's command line has no switch for these
features, so the audit fakes them where a browser resolves them, which turns out to
be two places and not one.

  * **The cascade.** The framed page is asked for its own `@media` rules, the ones
    whose condition matches the requested state are unwrapped, and their inner
    rules are appended as one plain stylesheet at the end of the head, which is
    where they would have landed anyway.
  * **`matchMedia`.** The server that feeds the iframe injects a patch into the
    head of every page it serves while a state is being emulated, and it has to,
    because a media feature is not only a CSS feature. This site's theme stamp runs
    in the page's head, asks `matchMedia('(prefers-color-scheme: dark)')` and writes
    `data-theme` from the answer, and an attribute outranks every media rule: the
    first version emulated the scheme in the cascade only, matched the rule,
    injected it, and then measured the LIGHT tokens because the stamp had already
    decided. Everything outside the emulated features is answered by the real
    browser, and a compound query keeps its real half, so `dark and (min-width:
    900px)` matches a 1440px window and does not match a 3000px one.

Nothing is invented here, no colour is written down in this file, and the tool is
asserting the stylesheet's own promise back at it rather than restating it. Which
makes the failure mode the honest one: a page that does not style the state comes
back with **zero rules**, and the report prints that count on every emulated state,
because zero rules is a gap and not a pass. The patch sets a marker, and a run that
asked for a state it could not install is reported as an ERROR rather than as a
clean page: the first version of the patch threw inside its own IIFE (a Python
string was eating its backslashes), `matchMedia` stayed the browser's, and the
report said `ok` about a dark-OS state it had never entered. The other stated limit:
a media rule nested inside a `@supports` would not be reached by the walk.

WHAT STATES THAT MEANS, and why the list is not arbitrary. The landing page ships
one world and is audited in it, plus the two emulated states it can be asked for.
A library page ships four, and all four are rendered: as authored by a reader who
has never touched the theme control (which on a light machine is light), that same
reader on a dark machine with no stored choice, a reader who has stored a choice,
and each of those under `prefers-contrast: more`. The dark-OS state is the one this
tool spent its whole life assuming: headless Chrome reports a light OS, so the
`:root:not([data-theme="light"])` half of the library's theme was asserted from the
source and never rendered, which is exactly the claim this file exists not to make.
Two facts it now measures rather than repeats: a dark machine with no stored choice
gets the dark world, and a stored light choice still wins on that same machine.

WHAT IT SETTLES FIRST. `is-cold` is this site's name for not-yet-revealed, and the
revealing observers answer a real visitor's scrolling rather than a programmatic
one. Every cold class is therefore cleared before anything is measured, which
measures the page a visitor reads rather than one frame of the animation they
watch.

THE CLOCK IS THEN ADVANCED, NOT WAITED OUT, and this tool had to learn that twice.
Clearing `is-cold` was not enough, because this page also has ordinary entrance
animations WITH DELAYS: the hero's answer arrives as six children on a stagger, the
last chip at 1,780ms, and `both` means a delayed animation holds its from-state,
which for these is `opacity: 0`. A fixed settle is therefore a bet on where the
page's clock is, and the audit lost it about half the time: **163 text elements in
one run, 150 in the next, same build, same width**, the difference being five
paragraphs and a citation that a visitor sees and the audit had walked past. What
found it was the element count the report prints on every line, and what fixed it
was `document.getAnimations().forEach(a => a.finish())`, which is exact and needs
no number that drifts when somebody retimes the page. An infinite animation cannot
be finished and is caught and skipped. The cost is stated rather than hidden: an
entrance state that was genuinely unreadable would be finished away instead of
reported, which is the same trade the cold-class settle already makes.

AND THE FIXED BAR IS FIXED, WHICH THE WALK FORGOT. The walk stops at multiples
of the viewport, and the nav is `position: fixed`, so an element can be seen for
the first time inside the band the bar occupies. The pixel pass then sampled the
bar: the notes act's caption, 38px from the top at the stop it was recorded at,
came back at 1.7:1 against the nav's own surface, a confident number about a
ground the text never sits on. The fix is not to trust that, and not to drop the
element either: the probe HIT-TESTS the sample points (`elementFromPoint`, which
is what the browser uses to decide what is on top), and when the thing on top is
fixed or sticky it records the scroll that clears the bar. The pixel pass then
takes that element's picture at that scroll, so the element is still measured.
Only a fixed or sticky occluder is treated this way: it moves with the viewport,
so covering this element was a fact about where the walk stopped. A badge
positioned over a caption covers it at every scroll, and that overlap is real,
so it is measured rather than dodged.

TWO TRAPS IN THE HARNESS ITSELF:

  * The harness page and the Chrome profile are written to a temp directory, NOT
    into `_site/`. An earlier version wrote into the artifact and broke
    `verify-budget.py`'s file count, and an earlier version reused a profile,
    which is how a run that had clicked the theme toggle once reported the wrong
    starting theme. A temp profile per run makes every run hermetic.
  * Git Bash rewrites an argument that starts with `/` into a Windows path, so
    `--pages /changelog/` can arrive as `C:/Program Files/Git/changelog/`. This
    script refuses a page that looks like that, because the iframe would then
    load nothing and the audit would report a clean page that does not exist.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

# One page per template the site actually ships, which is the point: the landing
# page, the generated directory, a carried article, the two sub-page shapes, and
# the not-found page. The directory is here because it was the page nothing had
# ever measured, and it is the one with 75 entries whose titles sit within half a
# step of the bar. The 404 is here because it carries a page's worth of ink (a
# heading, a box of links, a form and a button) on a stylesheet of its own, which
# is the other way a template goes unmeasured: not large, just separate.
DEFAULT_PAGES = ["/", "/library/", "/what-is-a-local-llm/", "/changelog/",
                 "/vs-chatgpt/", "/404.html"]

# The width the target-size pass is run at in addition to `--width`, because a
# target is small where the layout is narrow and this is the width the site's own
# breakpoints are written for. §3.2's phone column.
PHONE_WIDTH = 390


def find_chrome() -> str:
    env = os.environ.get("CHROME")
    if env:
        return env
    for c in CHROME_CANDIDATES:
        if os.path.sep in c or "/" in c:
            if os.path.isfile(c):
                return c
        else:
            found = shutil.which(c)
            if found:
                return found
    sys.exit("audit-contrast: no Chrome found. Set CHROME=/path/to/chrome.")


def page_path(raw: str) -> str:
    """A site-relative path, or exit explaining the Git Bash rewrite."""
    if re.match(r"^[A-Za-z]:[\\/]", raw) or "Program Files" in raw:
        sys.exit(
            "audit-contrast: --pages arrived as %r, which is Git Bash rewriting a\n"
            "               leading slash into a Windows path. Prefix the command\n"
            "               with MSYS_NO_PATHCONV=1." % raw)
    return raw if raw.startswith("/") else "/" + raw


# The probe. It is one expression: the harness evaluates it with `d` (the framed
# document) and `w` (its window) in scope.
PROBE = r"""
(async () => {
  const rel = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = ([r, g, b]) => 0.2126 * rel(r) + 0.7152 * rel(g) + 0.0722 * rel(b);
  const parse = s => {
    const m = /rgba?\(([^)]+)\)/.exec(s || '');
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(x => x).map(Number);
    return { rgb: p.slice(0, 3), a: p.length > 3 ? p[3] : 1 };
  };
  const over = (fg, bg) => fg.rgb.map((v, i) => v * fg.a + bg[i] * (1 - fg.a));
  const ratio = (a, b) => {
    const la = lum(a), lb = lum(b), hi = Math.max(la, lb), lo = Math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  };

  const groundAt = (x, y) => {
    let base = [255, 255, 255], gradient = false;
    const layers = [];
    for (const host of d.elementsFromPoint(x, y).slice().reverse()) {
      const cs = getComputedStyle(host);
      const op = parseFloat(cs.opacity);
      const a = isNaN(op) ? 1 : op;
      if (a === 0) continue;
      for (const pseudo of [null, '::before', '::after']) {
        const pcs = pseudo ? getComputedStyle(host, pseudo) : cs;
        if (pseudo && pcs.content === 'none') continue;
        if (pcs.backgroundImage && pcs.backgroundImage !== 'none') gradient = true;
        const bg = parse(pcs.backgroundColor);
        if (bg && bg.a > 0) layers.push({ rgb: bg.rgb, a: bg.a * a });
      }
      if (cs.backgroundImage && cs.backgroundImage !== 'none') gradient = true;
    }
    for (const L of layers) base = over(L, base);
    return { rgb: base, gradient: gradient };
  };

  const textOf = el => {
    let s = '';
    for (const n of el.childNodes) if (n.nodeType === 3) s += n.nodeValue;
    return s.replace(/\s+/g, ' ').trim();
  };

  const audit = async () => {
    const seen = new Set(), fails = [], gradient = [];
    let checked = 0;
    const vh = w.innerHeight, vw = w.innerWidth;
    /* Settle the page's entrance states ONCE, before anything is measured.

       `is-cold` is this site's name for not-yet-revealed. The revealing
       observers answer a real visitor's scrolling and do not fire reliably
       under a programmatic scroll on Chrome's virtual-time clock, so without
       this the poster's closing wordmark was measured in its pre-reveal coral
       at 2.55:1. Clearing the class and then waiting out the longest transition
       measures the page a visitor reads rather than one frame of the animation
       they watch. */
    d.querySelectorAll('.is-cold').forEach(function (el) {
      el.classList.remove('is-cold');
    });
    /* THE CLOCK IS ADVANCED, NOT WAITED OUT, and this is the second time this
       tool has had to learn the same lesson. The hero's answer arrives as six
       children each with its own animation DELAY, the last at 1,780ms, and
       `both` means a delayed animation holds its from-state: opacity 0. A fixed
       wait therefore measures whichever children have started. Measured on this
       page: 163 elements in one run and 150 in the next, same build, same
       width, the difference being five paragraphs and a citation that a
       visitor sees and the audit did not. Nobody would have noticed if the
       report did not print its own element count on every line. Finishing every
       animation and transition is exact and needs no number that drifts with
       the stylesheet. */
    try {
      d.getAnimations().forEach(function (a) {
        try { a.finish(); } catch (e) {}   /* an infinite one cannot finish */
      });
    } catch (e) {}
    await new Promise(r => setTimeout(r, 250));
    const steps = Math.min(24, Math.ceil(d.documentElement.scrollHeight / vh));
    for (let i = 0; i < steps; i++) {
      w.scrollTo({ top: i * vh, behavior: 'instant' });
      await new Promise(r => setTimeout(r, 40));
      /* Belt and braces. The settle above clears every cold state before the
         first scroll, so this block should find nothing; it stays as a guard
         in case a later observer adds one mid-walk. */
      d.querySelectorAll('.is-cold').forEach(function (el) {
        const r = el.getBoundingClientRect();
        if (r.top < vh && r.bottom > 0) el.classList.remove('is-cold');
      });
      for (const el of d.body.querySelectorAll('*')) {
        if (seen.has(el)) continue;
        const txt = textOf(el);
        if (!txt) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (el.closest('[hidden]')) continue;
        if (parseFloat(cs.opacity) === 0) continue;
        /* Decorative glyphs are exempt from contrast, and this site already
           marks them the standard way. The dot after the wordmark is a full
           stop used as a mark, exactly like the nav's cite-dot, which carries
           aria-hidden for the same reason. */
        if (el.closest('[aria-hidden="true"]')) continue;
        const r0 = el.getClientRects()[0];
        if (!r0 || r0.width < 2 || r0.height < 2) { seen.add(el); continue; }
        if (r0.bottom < 0 || r0.top > vh) continue;
        seen.add(el);
        const x = Math.min(Math.max(r0.left + 1, 1), vw - 2);
        const y = Math.min(Math.max(r0.top + r0.height / 2, 1), vh - 2);
        const size = parseFloat(cs.fontSize), weight = Number(cs.fontWeight) || 400;
        const need = (size >= 24 || (size >= 18.66 && weight >= 700)) ? 3 : 4.5;
        const c = parse(cs.color);
        if (!c) continue;
        const fg = over(c, [255, 255, 255]);
        const g = groundAt(x, y);
        const r = ratio(fg, g.rgb);
        checked++;
        const rec = {
          sel: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).trim().split(/\s+/).join('.') : ''),
          text: txt.slice(0, 48),
          color: cs.color,
          ground: 'rgb(' + g.rgb.map(v => Math.round(v)).join(', ') + ')',
          ratio: Number(r.toFixed(2)),
          need: need,
          size: size.toFixed(1),
          weight: weight,
          replica: !!el.closest('.win'),
        };
        if (g.gradient) {
          /* Rects are reported in DOCUMENT coordinates, because they are sampled
             from a full-page screenshot in a later run, where the scroll offset
             that produced them no longer exists. */
          rec.rect = {
            x: Math.round(r0.left + w.scrollX), y: Math.round(r0.top + w.scrollY),
            w: Math.round(r0.width), h: Math.round(r0.height),
          };
          /* LINE BOXES, not the block box. Sampling just above and below a
             block works for one line and fails for four: the strip below the
             block is the NEXT element's ground, so a label on the dark poster
             came back as dark ink on a light panel at 1.0:1. The leading inside
             each line box is the same ground as the text and carries no glyph. */
          const rr = d.createRange();
          rr.selectNodeContents(el);
          rec.lines = Array.prototype.slice.call(rr.getClientRects(), 0, 3).map(function (r) {
            return { x: Math.round(r.left + w.scrollX), y: Math.round(r.top + w.scrollY),
                     w: Math.round(r.width), h: Math.round(r.height) };
          }).filter(function (r) { return r.w > 1 && r.h > 1; });
          /* A replica of the app is not this site's typography: its inks are
             sampled from the product, and changing one to satisfy a contrast
             checker would make the reproduction lie about the thing it exists
             to show. Reported, never counted. */
          rec.replica = !!el.closest('.win');
          /* The scroll this rect was taken at. A sticky element is not at a
             fixed document position: the nav is at y=20 when the page is at the
             top and at y=20 somewhere else when the page is not. Sampling a
             rect from one scroll against a picture taken at another is how a
             nav link came back as unmeasurable. Each rect is sampled in the
             viewport it was measured in. */
          rec.anchor = Math.round(w.scrollY);
          rec.ink = [c.rgb[0], c.rgb[1], c.rgb[2]];
          rec.alpha = c.a;
          /* Whether this element paints its own ground. If it does, the pixels
             BESIDE its box are somebody else's ground, and sampling there is how
             the CTA first came back at 1.00:1: white ink against the white page
             it sits on, instead of the gradient it sits in. Those elements are
             sampled inside their own padding instead. */
          const own = getComputedStyle(el);
          const ownBg = parse(own.backgroundColor);
          let ownArt = !!(own.backgroundImage && own.backgroundImage !== 'none') ||
                        !!(ownBg && ownBg.a >= 1);
          for (const pseudo of ['::before', '::after']) {
            const pcs = getComputedStyle(el, pseudo);
            if (pcs.content === 'none') continue;
            const pbg = parse(pcs.backgroundColor);
            if ((pbg && pbg.a > 0) || (pcs.backgroundImage && pcs.backgroundImage !== 'none')) ownArt = true;
          }
          rec.hasOwn = ownArt;
          /* THE WALK STOPS AT MULTIPLES OF THE VIEWPORT, so an element can land
             in the band a FIXED bar occupies, and the pixels sampled there
             belong to the bar. The notes act's caption, first seen at the stop
             where it sat 38px from the top, was sampled through the nav that
             way: a confident 1.7:1 against the nav's own surface, which is a
             ratio about a ground the text never sits on. Hit-testing is exact,
             so it is asked rather than guessed, and the scroll that clears the
             bar is recorded: the pixel pass takes that element's picture there
             instead, which keeps the element MEASURED rather than dropping it
             into the unmeasured pile.

             Only a fixed or sticky occluder is treated this way, because only
             that one moves with the viewport: a fixed bar covers a different
             band at every scroll, so what covered this element is a fact about
             where the walk stopped. A badge positioned over a caption covers it
             at every scroll, and that overlap is real: it is measured, not
             dodged. */
          const sampleDocY = rec.hasOwn
            ? rec.rect.y + rec.rect.h / 2
            : (rec.lines && rec.lines.length
                ? rec.lines[0].y + Math.max(1, Math.min(2, rec.lines[0].h * 0.12))
                : rec.rect.y + rec.rect.h / 2);
          const pts = rec.hasOwn
            ? [[rec.rect.x + 4, sampleDocY], [rec.rect.x + rec.rect.w - 4, sampleDocY]]
            : (rec.lines && rec.lines.length ? rec.lines : [rec.rect]).map(function (L) {
                return [L.x + 3, L.y + Math.max(1, Math.min(2, L.h * 0.12))];
              });
          for (let pi = 0; pi < pts.length; pi++) {
            const pvx = pts[pi][0] - w.scrollX, pvy = pts[pi][1] - w.scrollY;
            if (pvx < 0 || pvx > vw - 1 || pvy < 0 || pvy > vh - 1) continue;
            const hit = d.elementFromPoint(pvx, pvy);
            if (!hit || hit === el || el.contains(hit) || hit.contains(el)) continue;
            let bar = null;
            for (let o = hit; o && o !== d.documentElement; o = o.parentElement) {
              const pos = getComputedStyle(o).position;
              if (pos === 'fixed' || pos === 'sticky') { bar = o; break; }
            }
            if (!bar) continue;
            /* 24px of daylight, so the sample lands below the bar's own edge
               rather than on it. The bar is measured at THIS scroll, which is
               the same stuck state it will be in at the scroll recorded here.*/
            rec.covered = Math.max(0, Math.round(sampleDocY - bar.getBoundingClientRect().bottom - 24));
            rec.coveredBy = bar.tagName.toLowerCase() +
              (bar.className ? '.' + String(bar.className).trim().split(/\s+/)[0] : '');
            break;
          }
          gradient.push(rec);
          continue;
        }
        if (r < need) fails.push(rec);
      }
    }
    w.scrollTo({ top: 0, behavior: 'instant' });
    await new Promise(r => setTimeout(r, 40));
    /* The theme is read HERE and not at return time. Reading it in the returned
       object literal gave both states the FINAL theme, because the object is
       built after the toggle has been clicked: the audits were right and their
       labels were wrong, which is the most annoying shape a bug can have. */
    return { theme: d.documentElement.getAttribute('data-theme'),
             checked: checked, viewports: steps, fails: fails, gradient: gradient,
             /* What a reader can actually read on this render. `innerText`
                respects display and visibility, so it is the text that was
                painted rather than the text that is in the file, which is the
                only figure worth comparing against a render with no script. */
             chars: (d.body.innerText || '').replace(/\s+/g, ' ').trim().length };
  };

  const one = await audit();
  /* ONE THEME PER RUN. This probe used to audit the page, click the control and
     audit again, which was elegant and wrong: the screenshot that samples
     gradient grounds is a SEPARATE Chrome invocation, so its render was always
     the first theme, and the dark pass was measured against a light-theme
     picture. That returned a confident 2.58:1 for the CTA by comparing the dark
     page's rects with the light page's pixels. Each state now gets its own run,
     with the stored choice set before the page loads. */
  const btn = d.querySelector('.theme-toggle');
  let control = { found: !!btn && !btn.hidden };
  if (control.found) {
    control.from = one.theme;
    btn.click();
    await new Promise(r => setTimeout(r, 150));
    control.to = d.documentElement.getAttribute('data-theme');
    control.flipped = control.from !== control.to;
    btn.click();
    await new Promise(r => setTimeout(r, 100));
  }
  return {
    /* A flat ground is measured here, in the page, against the cascade. A
       gradient or photographic ground cannot be: the ratio would be arithmetic
       on one sample of a wash. Those elements come back with their rects so a
       later run can sample the pixels Chrome actually painted. */
    state: one.theme,
    /* How many of the page's own media rules the harness unwrapped to emulate
       the requested state. Zero means the page does not style that state. */
    mediaRules: w.__auditMediaRules || 0,
    mediaPatch: w.__auditMediaPatch || "",
    checked: one.checked,
    viewports: one.viewports,
    viewportHeight: w.innerHeight,
    fails: one.fails,
    gradient: one.gradient,
    themeControl: control,
    docHeight: Math.ceil(d.documentElement.scrollHeight),
  };
})()
"""

NOSCRIPT_PROBE = r"""
(async () => {
  /* `d` and `w` are parameters of the function the harness builds around this
     expression, and are the FRAMED page's document and window. Declaring them
     here from `document` compiled, ran, and reported on the harness instead: 0
     characters, 0 links, and two invisible elements that were the harness's own. */
  await new Promise(r => setTimeout(r, 60));

  /* EVERY ANIMATION FINISHED before anything is called invisible, and this is the
     third time this tool has had to learn it. The hero's answer is six children
     with animation DELAYS and `both` fill, so for the first 1.8 seconds they sit
     at opacity 0 while being perfectly visible to a reader a moment later. The
     first run of this probe reported the hero's opening answer as content behind
     script, which it is not and never was: it is an entrance. What is asked here
     is whether an element EVER gets a box, not whether it has one this
     millisecond. */
  d.getAnimations().forEach(function (a) { try { a.finish(); } catch (e) {} });
  await new Promise(r => setTimeout(r, 60));
  const reason = el => {
    /* An ancestor's state is checked first, because otherwise a paragraph inside
       a `hidden` answer reports whatever its own rules say, and an entrance
       animation's from-state is `opacity: 0`: the first version of this listed
       the two answers the hero keeps in reserve as content behind script, which
       they are not, they are content behind a button. */
    const hidden = el.closest('[hidden]');
    if (hidden) return 'inside an element carrying the hidden attribute';
    const cs = getComputedStyle(el);
    if (el.hidden) return 'the hidden attribute';
    if (cs.display === 'none') return 'display: none';
    if (cs.visibility === 'hidden') return 'visibility: hidden';
    if (parseFloat(cs.opacity || '1') === 0) return 'opacity: 0';
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return 'no box';
    return '';
  };
  /* Every element that carries text of its own and is not rendered. A container
     whose text is in a child is not listed: the child is. */
  const invisible = [];
  let elements = 0;
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  /* One line per closed disclosure, not one per paragraph inside it. A reader
     opening it gets the whole answer, so the finding is the disclosure, and a
     list that reports its twelve paragraphs as twelve findings is a list nobody
     reads to the end. */
  const collapsed = new Set();
  for (const el of d.body.querySelectorAll('*')) {
    const own = [].slice.call(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.nodeValue).join('').replace(/\s+/g, ' ').trim();
    if (!own) continue;
    elements++;
    /* A closed disclosure is NOT the same finding as a hidden one: the prose is
       one click away with no script at all. Chrome also does not run the
       entrance animations of an element it is not rendering, so without this
       branch the hero's reserved answers reported `opacity: 0` — their own
       from-state — which reads as content behind script rather than content
       behind a summary. The summary itself is the visible half of the pair. */
    const box = el.tagName === 'SUMMARY' ? null : el.closest('details:not([open])');
    if (box) {
      if (collapsed.has(box)) continue;
      collapsed.add(box);
      const sum = box.querySelector('summary');
      invisible.push({
        sel: name(box),
        why: 'a closed <details>, reachable in one click',
        text: (sum ? sum.textContent.trim() + ': ' : '') + own.slice(0, 120),
      });
      continue;
    }
    const why = reason(el);
    if (!why) continue;
    invisible.push({sel: name(el), why: why, text: own.slice(0, 120)});
  }
  return {
    scripts: false,
    chars: (d.body.innerText || '').replace(/\s+/g, ' ').trim().length,
    elements: elements,
    links: d.querySelectorAll('a[href]').length,
    controls: d.querySelectorAll('button, input, select, textarea, summary').length,
    invisible: invisible,
  };
})()
"""

TAP_PROBE = r"""
(async () => {
  /* WCAG 2.5.8 at AA: a target is at least 24 by 24 CSS px, unless it is inline
     in a sentence (the exception every citation chip and in-text link relies on),
     or unless a 24px-diameter circle centred on it intersects no other target.

     The spacing exception is measured rather than assumed, because it is the one
     that lets a row of small controls stand: a link that is 20px tall passes if
     nothing else comes within 12px of its centre. Nested targets are skipped from
     that test: a link inside a link, or a chip filling its own list item, is one
     control with two boxes rather than two controls, and counting it as the other
     would excuse nothing and only add noise, and "nested" means one box encloses
     the other, not merely that the two overlap.

     The inline exception is the one this probe has had to learn twice. v1 asked
     only whether the target's display was `inline` and its parent held MORE text.
     On the directory that granted the exception to seventy of ninety-one targets:
     each entry is `<li><a>title</a><span class="index-desc">blurb</span></li>`, so
     the parent does hold more text, in a different block, on the next line. A link
     that heads its own list item is not a word in a sentence, and excusing it also
     skipped its spacing test. The test is now the real one: the exception needs an
     inline formatting context, which means a non-empty text node or an inline-level
     sibling next to the target. A `display: block` sibling starts its own line and
     does not count, however much text it carries. */
  const MIN = 24;
  await new Promise(r => setTimeout(r, 60));
  d.getAnimations().forEach(function (a) { try { a.finish(); } catch (e) {} });
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  /* Is there inline content beside this element, in the same line box? */
  const hasInlineRun = el => {
    const p = el.parentElement;
    if (!p) return false;
    for (const n of p.childNodes) {
      if (n === el) continue;
      if (n.nodeType === 3) { if (n.nodeValue.trim()) return true; continue; }
      if (n.nodeType !== 1) continue;
      const ncs = getComputedStyle(n);
      if (ncs.display !== 'inline' || ncs.visibility === 'hidden') continue;
      if ((n.textContent || '').trim()) return true;
    }
    return false;
  };
  const els = [].slice.call(d.querySelectorAll(
    'a[href], button, input, select, textarea, summary, [role="button"]'));
  const targets = [];
  for (const el of els) {
    const cs = getComputedStyle(el);
    if (el.hidden || cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const words = (el.textContent || '').replace(/\s+/g, ' ').trim();
    targets.push({
      sel: name(el), text: words.slice(0, 70),
      box: {x: r.left, y: r.top, w: r.width, h: r.height},
      /* `display: inline` alone is not the exception: it needs a run of text to be
         inline IN. A non-empty text node, or an inline-level sibling, beside the
         target is that run. A block sibling is the next line, not the same one. */
      inline: cs.display === 'inline' && !!words && hasInlineRun(el),
    });
  }
  const small = t => t.box.w < MIN - 0.5 || t.box.h < MIN - 0.5;
  const under = targets.filter(small);
  /* Enclosure, not intersection, and the difference is the whole value of this
     test. This predicate was written first as `contains(a,b) || contains(b,a)`
     where each half was `a.x <= b.x+b.w && b.x <= a.x+a.w && a.y <= b.y+b.h &&
     b.y <= a.y+a.h`. Read it once: that is x-overlap AND y-overlap, which is
     rectangle intersection. Symmetric, so the `||` was noise and the test
     simplified to "the two boxes touch at all always means one control".
     That excuse swallowed every overlapping pair, which is precisely the set
     the spacing exception exists to judge: two 20px rows 16px apart overlap by
     4px and were skipped before the circle was ever drawn. A negative test
     caught it: collapsing the directory into a dense column changed nothing at
     all, and a check that cannot fail is not a check. A target is nested only
     when one box encloses the other outright. */
  const encloses = (a, b) => a.x <= b.x + 0.5 && a.y <= b.y + 0.5 &&
                             b.x + b.w <= a.x + a.w + 0.5 &&
                             b.y + b.h <= a.y + a.h + 0.5;
  const circleHits = (c, box) => {
    const nx = Math.max(box.x, Math.min(c.cx, box.x + box.w));
    const ny = Math.max(box.y, Math.min(c.cy, box.y + box.h));
    const dx = c.cx - nx, dy = c.cy - ny;
    return dx * dx + dy * dy < c.r * c.r;
  };
  /* The spec's second condition, and not the same as the first: the circle must
     miss the other TARGET's box, and it must also miss the other UNDER-SIZED
     target's own circle. That circle is centred on a box smaller than itself, so
     it pokes out past the box, and two small controls can clear each other's boxes
     while their circles still overlap. Checking only the box is the looser read. */
  const circlesOverlap = (a, b) => {
    const dx = a.cx - b.cx, dy = a.cy - b.cy;
    return dx * dx + dy * dy < (a.r + b.r) * (a.r + b.r);
  };
  const fails = [], inline = [], spaced = [];
  for (const t of under) {
    if (t.inline) { inline.push(t); continue; }
    const c = {cx: t.box.x + t.box.w / 2, cy: t.box.y + t.box.h / 2, r: MIN / 2};
    let blocked = null;
    for (const other of targets) {
      if (other === t) continue;
      if (encloses(t.box, other.box) || encloses(other.box, t.box)) continue;
      const oc = {cx: other.box.x + other.box.w / 2,
                  cy: other.box.y + other.box.h / 2, r: MIN / 2};
      if (circleHits(c, other.box) || (small(other) && circlesOverlap(c, oc))) {
        blocked = other; break;
      }
    }
    if (blocked) {
      t.blockedBy = blocked.sel;
      fails.push(t);
    } else {
      spaced.push(t);
    }
  }
  return {
    tap: true,
    width: Math.round(w.innerWidth),
    targets: targets.length,
    under: under.length,
    inline: inline.length,
    spaced: spaced.length,
    fails: fails.map(t => ({sel: t.sel, text: t.text, w: Math.round(t.box.w),
                            h: Math.round(t.box.h), blockedBy: t.blockedBy})),
  };
})()
"""

SEAM_PROBE = r"""
(async () => {
  /* The separator rule, measured instead of read off the stylesheet.

     As §3.4 now states it: a window on a DARK ground is separated by a 1px seam
     in --field-rule plus --shadow-field; a window on a LIGHT ground by
     --shadow-paper alone. Two decisions make this a measurement rather than a
     restatement:

       * the expected values are read from the tokens, so a token edit cannot
         leave this check behind;
       * the ground is found by WALKING THE CASCADE for the first opaque
         background, not by looking for a class name. A new dark band whose window
         never got a seam is exactly the failure this exists for, and a check that
         looked for `.field` would not see it -- which is the mistake the old
         version of §3.4 made, and why it claimed a rule the page does not follow.

     Line art is out of scope by construction: the ring's plate has no fill, so it
     is not a window on a ground, and nothing about it should be asserted here. */

  const inner = s => {
    const t = String(s), a = t.indexOf('('), b = t.indexOf(')');
    return a < 0 ? '' : t.slice(a + 1, b < 0 ? t.length : b);
  };
  const nums = s => inner(s).split(/[^0-9.]+/).filter(Boolean).map(Number);
  const px = s => (String(s).match(/[0-9.]+px/g) || []).map(v => parseFloat(v));
  const trim0 = a => { const b = a.slice(); while (b.length && !b[0]) b.shift();
                       while (b.length && !b[b.length - 1]) b.pop(); return b; };
  const lum = c => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92
                                                  : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const key = a => a.map(n => Math.round(n * 100) / 100).join(',');

  const ground = el => {
    let n = el.parentElement;
    while (n && n !== d.documentElement) {
      const c = nums(getComputedStyle(n).backgroundColor);
      if (c.length >= 3 && (c.length < 4 || c[3] > 0.5)) {
        return { sel: n.tagName.toLowerCase() + (n.className ? '.' + String(
          n.className.baseVal !== undefined ? n.className.baseVal : n.className
        ).split(' ')[0] : ''), c: c, lum: lum(c) };
      }
      n = n.parentElement;
    }
    return { sel: 'body', c: [250, 249, 246], lum: 1 };
  };

  const targets = [...d.querySelectorAll('main .exhibit > picture > img, main .win')];
  /* A page with no windows is not a page that failed: it is a page this question
     does not apply to, and the answer is to say so. Returning BEFORE the tokens
     are read is the whole difference -- the library's stylesheet declares none of
     these three tokens, and the first version of this pass reported every one of
     the 75 carried pages as a failure that had "measured nothing". A check that
     fails on the pages it does not apply to is a check that gets switched off. */
  if (!targets.length) {
    return { seam: true, width: Math.round(w.innerWidth), windows: 0, onDark: 0,
             onPaper: 0, fails: [] };
  }

  const T = n => getComputedStyle(d.documentElement).getPropertyValue(n).trim();
  const seamColor = key(nums(T('--field-rule')));
  const fieldShadow = { c: key(nums(T('--shadow-field')).slice(0, 3)), px: px(T('--shadow-field')) };
  const paperShadow = { c: key(nums(T('--shadow-paper')).slice(0, 3)), px: px(T('--shadow-paper')) };
  if (!seamColor || !fieldShadow.c || !paperShadow.c) {
    return { error: 'this page HAS windows and its stylesheet does not resolve the '
                    + 'separator tokens (--field-rule ' + seamColor + ', --shadow-field '
                    + fieldShadow.c + ', --shadow-paper ' + paperShadow.c
                    + '), so their separators were not measured' };
  }
  const fails = [], rows = [];
  for (const el of targets) {
    const cs = getComputedStyle(el);
    const g = ground(el);
    const dark = g.lum < 0.15;
    const bw = parseFloat(cs.borderTopWidth) || 0;
    const bcolor = key(nums(cs.borderTopColor));
    const sh = cs.boxShadow === 'none' ? null : cs.boxShadow;
    const scolor = sh ? key(nums(sh).slice(0, 3)) : '';
    const spx = sh ? trim0(px(sh)) : [];
    const want = dark ? fieldShadow : paperShadow;
    const why = [];
    if (dark && (bw !== 1 || bcolor !== seamColor)) {
      why.push('no seam: border is ' + cs.borderTopWidth + ' ' + cs.borderTopColor +
               ', expected 1px ' + T('--field-rule'));
    }
    if (!dark && bw !== 0) {
      why.push('a seam on paper: ' + cs.borderTopWidth + ' ' + cs.borderTopColor +
               ', expected none');
    }
    if (scolor !== want.c) {
      why.push('shadow is ' + (scolor || 'none') + ', expected ' + want.c +
               (dark ? ' (--shadow-field)' : ' (--shadow-paper)'));
    } else if (sh && trim0(want.px).join() !== spx.join()) {
      why.push('shadow geometry is ' + spx.join(' ') + ', expected ' + trim0(want.px).join(' '));
    }
    const row = { sel: (el.tagName.toLowerCase() + '.' + String(
      el.className && el.className.baseVal !== undefined ? el.className.baseVal
      : el.className || '').split(' ').slice(0, 2).join('.')).replace(/\.$/, ''),
      ground: g.sel, groundLum: Math.round(g.lum * 1000) / 1000, dark: dark,
      border: cs.borderTopWidth + ' ' + cs.borderTopColor, shadow: scolor || 'none' };
    rows.push(row);
    if (why.length) fails.push(Object.assign({ why: why.join('; ') }, row));
  }
  return {
    seam: true,
    width: Math.round(w.innerWidth),
    windows: rows.length,
    onDark: rows.filter(r => r.dark).length,
    onPaper: rows.filter(r => !r.dark).length,
    fails: fails
  };
})()
"""

HARNESS = """<!doctype html>
<html><head><meta charset="utf-8"><title>audit</title>
<style>html,body{{margin:0;padding:0}}iframe{{border:0;display:block}}</style>
<script>
/* The stored choice is set BEFORE the framed page is parsed, which is the only
   moment that can force its theme: the page's own stamp reads this key in its
   head, so a harness that sets it afterwards has already lost the race. */
var THEME = {theme};
if (THEME) {{ try {{ localStorage.setItem('istor.site.theme', THEME); }} catch (e) {{}} }}
/* Screenshots are taken ONE VIEWPORT AT A TIME, because Chrome clamps a window
   taller than the screen: a request for 1440x15000 comes back as an image of
   something else, and every sample below its real height reads whatever is in
   the last row. That returned 59 confident failures on the home page, all of
   them white ground under dark-ground text. */
var SCROLL = parseInt((new URLSearchParams(location.search).get('scroll') || '0'), 10);

/* THE MEDIA STATE IS EMULATED HERE, and that is a choice worth stating. Chrome's
   command line has no switch for these features, and the honest place to fake one
   is the same place a browser resolves one: in the cascade. So the framed page is
   asked for its own @media rules, the ones whose condition matches the requested
   state are unwrapped, and their inner rules are appended as one plain stylesheet
   at the end of the head, which is where they would have landed. Nothing is
   invented; no colour is written down here. Which means the failure mode is the
   honest one: a page that does not style this state comes back with zero rules,
   and zero rules is REPORTED rather than read as a pass.

   THE ANSWER TO "DOES THIS CONDITION MATCH" COMES FROM THE PATCHED matchMedia, and
   not from a parser here. That is the whole trick, and it took a wrong version to
   find: the library's theme stamp runs in the page's head and writes `data-theme`
   from `matchMedia('(prefers-color-scheme: dark)')`, which outranks every media
   rule in the stylesheet. Emulating the feature in the cascade alone therefore
   emulated nothing at all on the one page that has a dark OS world to test: the
   run matched the rule, injected it, and measured the LIGHT tokens, because the
   stamp had already decided. The server that feeds this iframe now injects a
   matchMedia patch before the page's first script (see MEDIA_PATCH), so the CSS
   and the script see one world. */
var MEDIA = {media};
var EMULATED = [];
for (var k in MEDIA) if (MEDIA.hasOwnProperty(k)) EMULATED.push(k);
function mediaMatches(cond, w) {{
  var q = String(cond || '').trim();
  return w.matchMedia(q || 'all').matches;
}}
function emulateMedia(d, w, want) {{
  var n = 0, sheets = d.styleSheets;
  var named = new RegExp('(' + EMULATED.join('|') + ')', 'i');
  var walk = function (rules) {{
    for (var i = 0; i < rules.length; i++) {{
      var r = rules[i];
      if (r.type !== 4) continue;                 /* 4 is CSSRule.MEDIA_RULE */
      /* Only a rule that NAMES an emulated feature is touched. A width query
         matches at this width anyway, so unwrapping one would inject a second
         copy of rules that already apply, and the count reported beside every
         emulated state would then be a count of nothing in particular. */
      var cond = String(r.conditionText || '');
      if (EMULATED.length && named.test(cond) && mediaMatches(cond, w)) {{
        var st = d.createElement('style');
        var label = [];
        for (var k in want) if (want.hasOwnProperty(k)) label.push(k + ':' + want[k]);
        st.setAttribute('data-audit-media', label.join(' '));
        st.textContent = [].map.call(r.cssRules, function (x) {{ return x.cssText; }}).join('\\n');
        d.head.appendChild(st);
        n += 1;
      }}
      if (r.cssRules) walk(r.cssRules);           /* a media rule inside a media rule */
    }}
  }};
  for (var i = 0; i < sheets.length; i++) {{
    var rules = null;
    try {{ rules = sheets[i].cssRules; }} catch (e) {{ continue; }}
    if (rules) walk(rules);
  }}
  return n;
}}
</script>
</head>
<body>
<iframe id="f" width="{w}" height="{h}" src="{url}"></iframe>
<pre id="out" style="display:none">PENDING</pre>
<script>
var f = document.getElementById('f'), out = document.getElementById('out');
f.addEventListener('load', async function () {{
  try {{
    var d = f.contentDocument, w = f.contentWindow;
    if (!d || !d.body || !d.body.childElementCount) throw new Error('iframe is empty: ' + f.src);
    /* Injected BEFORE the settle, so anything the page transitions between the
       two palettes has finished by the time anything is measured. */
    if (EMULATED.length) w.__auditMediaRules = emulateMedia(d, w, MEDIA);
    await new Promise(function (r) {{ setTimeout(r, {settle}); }});
    if (SCROLL) {{
      w.scrollTo({{ top: SCROLL, behavior: 'instant' }});
      await new Promise(function (r) {{ setTimeout(r, 250); }});
    }}
    var fn = new Function('d', 'w', 'return (' + {expr} + ')');
    out.textContent = 'RESULT:' + JSON.stringify({{ value: await fn(d, w),
                                                    scrolled: SCROLL }});
  }} catch (e) {{
    out.textContent = 'RESULT:' + JSON.stringify({{ error: String((e && e.stack) || e) }});
  }}
}});
setTimeout(function () {{ if (out.textContent === 'PENDING') out.textContent = 'RESULT:' + JSON.stringify({{ error: 'no load event' }}); }}, {settle} + 8000);
</script>
</body></html>
"""


# What the server injects into the head of every page it serves while a media
# state is being emulated. It exists because `prefers-color-scheme` is not only a
# CSS feature: this site's theme stamp reads it through `matchMedia` and writes
# `data-theme` before first paint, and an attribute beats any media rule. Patch
# the API and the page's own decision agrees with the stylesheet's; skip it and
# the audit measures the light world while reporting that it matched the dark
# rule, which is the quietest way a tool can lie.
#
# Only queries that NAME an emulated feature are answered here. Everything else
# goes to the real `matchMedia`, and a compound query keeps its real half: the
# emulated parts are removed, the rest is asked of the browser, and the two are
# combined. A bare `(prefers-contrast)` asks for more, which is that feature's
# own shorthand and the only one of these with a bare form.
# Written as a RAW string on purpose. It is JavaScript full of backslashes inside
# a template that is also formatted, and the first version was not raw: `\\(` in
# a normal Python string arrives in the browser as `\(`, which a JS *string*
# literal reads as a bare `(`, so the regex became a different regex with the
# wrong groups. It threw, the exception killed the whole IIFE before the
# assignment, `matchMedia` stayed the browser's, and the audit reported a
# dark-OS run that had measured a light page with `0 media rules`. Nothing was
# wrong with the finding; the run had not happened. Hence the marker below, which
# run_state insists on seeing: a state that was not emulated is an ERROR here, not
# a state that passed.
MEDIA_PATCH = r"""<script>
(function () {{
  var EMU = {media}, keys = [], k;
  for (k in EMU) if (EMU.hasOwnProperty(k)) keys.push(k);
  if (!keys.length || !window.matchMedia) return;
  var real = window.matchMedia.bind(window);
  var NAMED = new RegExp('^\\(\\s*(' + keys.join('|') + ')\\s*(?::\\s*([^)]+?)\\s*)?\\)$', 'i');
  window.matchMedia = function (query) {{
    var q = String(query == null ? '' : query);
    var parts = q.split(/\s+and\s+/i), keep = [], emulated = false, ok = true;
    for (var i = 0; i < parts.length; i++) {{
      var p = parts[i].trim(), m = NAMED.exec(p);
      if (m) {{
        emulated = true;
        if ((m[2] || 'more').trim().toLowerCase() !== EMU[m[1].toLowerCase()]) ok = false;
      }} else if (p) {{
        keep.push(p);
      }}
    }}
    if (!emulated) return real(q);
    var rest = keep.length ? real(keep.join(' and ')) : {{ matches: true }};
    var noop = function () {{}};
    return {{ matches: ok && rest.matches, media: q, onchange: null,
             addListener: noop, removeListener: noop,
             addEventListener: noop, removeEventListener: noop,
             dispatchEvent: function () {{ return false; }} }};
  }};
  window.__auditMediaPatch = keys.join(',');
}})();
</script>
"""


def inject_patch(html, patch):
    """Put the media patch at the top of `<head>`, which is before anything the
    page runs on its own. A document with no head gets it prepended."""
    m = re.search(r"<head[^>]*>", html, re.I)
    if not m:
        return patch + html
    return html[:m.end()] + patch + html[m.end():]


# The pixel sampler. A ground that carries a gradient cannot be composited from
# the cascade, and a ratio computed from one sample of a wash is a guess wearing
# a number's clothes. So: Chrome writes a full-page screenshot of the same page
# at the same width, and this second harness loads that PNG into a canvas (same
# origin, so the canvas is not tainted) and reads the pixels just above and just
# below each text box, where the ground shows through untouched by glyphs.
#
# The method's limits, stated rather than discovered later:
#   * The strip above the first line and below the last one brackets a vertical
#     gradient at its two ends. A dip between them would be missed.
#   * Anything else painted in those strips (a hairline, a neighbouring label)
#     lands in the sample too. The worst sample wins, so that is conservative:
#     it can report a failure that a human would call a false alarm, and it
#     cannot report a pass on a ground that is really darker somewhere.
#   * Reported with every ratio: the sampled luminance range, so a wide spread is
#     visible as a wide spread instead of hiding behind one number.
SAMPLER = """<!doctype html>
<html><head><meta charset="utf-8"><title>sampler</title></head>
<body>
<pre id="out" style="display:none">PENDING</pre>
<script>
var out = document.getElementById('out');
var RECTS = {rects}, SHOTS = {shots};
function rel(c) {{ c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }}
function lum(p) {{ return 0.2126 * rel(p[0]) + 0.7152 * rel(p[1]) + 0.0722 * rel(p[2]); }}
function over(inK, bg) {{
  var c = inK.rgb || inK, a = inK.a === undefined ? 1 : inK.a;
  return c.map(function (v, i) {{ return v * a + bg[i] * (1 - a); }});
}}
function ratio(a, b) {{
  var la = lum(a), lb = lum(b), hi = Math.max(la, lb), lo = Math.min(la, lb);
  return (hi + 0.05) / (lo + 0.05);
}}
(async function () {{
  try {{
    /* Every viewport's image is loaded up front; each element names the one it
       was measured in, and each draw resizes the canvas to that image so the
       coordinates in its rect are the coordinates in its pixels. */
    var IMG = [];
    for (var i = 0; i < SHOTS.length; i++) {{
      var img = new Image();
      img.src = SHOTS[i];
      await new Promise(function (res, rej) {{ img.onload = res; img.onerror = function () {{ rej(new Error('png did not load: ' + SHOTS[i])); }}; }});
      IMG.push(img);
    }}
    var cv = document.createElement('canvas');
    var ctx = cv.getContext('2d', {{ willReadFrequently: true }});
    var px = null;
    var size = function (img) {{ cv.width = img.naturalWidth; cv.height = img.naturalHeight; }};
    size(IMG[0]);
    var at = function (x, y) {{
      x = Math.max(0, Math.min(cv.width - 1, Math.round(x)));
      y = Math.max(0, Math.min(cv.height - 1, Math.round(y)));
      var i = (y * cv.width + x) * 4;
      return [px[i], px[i + 1], px[i + 2]];
    }};

    var probes = function (r) {{
      if (r.hasOwn) {{
        /* Its own ground: sample INSIDE the box, in the padding at the vertical
           centre, where no glyph reaches. For a centred label that is the left
           and right edges of its own gradient, which is what the text sits in. */
        var ym = r.rect.y + r.rect.h / 2;
        return [r.rect.x + 4, r.rect.x + r.rect.w - 4].map(function (x) {{ return [x, ym]; }});
      }}
      /* No ground of its own: sample the leading at the top and the bottom of
         each LINE box, which is inside the text's own block and still carries
         no glyph. */
      /* The TOP of each line box only. Sampling its bottom looked symmetric and
         was wrong: the bottom edge of a line box is where descenders and their
         anti-aliasing live, so the "ground" came back as ink at luminance 0.35
         and the hero's lede was reported at 1.16:1 against a wash it is not on.
         The leading above the caps carries no glyph at all. */
      var lines = (r.lines && r.lines.length) ? r.lines : [r.rect];
      var out = [];
      lines.forEach(function (L) {{
        var y = L.y + Math.max(1, Math.min(2, L.h * 0.12));
        /* Clamped into the frame rather than skipped. An element whose box ends
           at the very bottom of the viewport has its line top a few pixels past
           the edge, and the first version dropped those as unsampleable: the
           landing page reported elements unmeasured for being six pixels too
           low. The ground at the last visible row is the same field as the row
           just past it, so the nearest visible row is the honest sample. */
        y = Math.max(1, Math.min(cv.height - 2, y));
        [L.x + 3, L.x + L.w / 2, L.x + L.w - 3].forEach(function (x) {{
          x = Math.max(0, Math.min(cv.width - 1, x));
          out.push([x, y]);
        }});
      }});
      return out;
    }};
    var results = RECTS.map(function (r) {{
      size(IMG[r.shot || 0]);
      ctx.drawImage(IMG[r.shot || 0], 0, 0);
      px = ctx.getImageData(0, 0, cv.width, cv.height).data;
      var pts = probes(r);
      if (!pts.length) {{
        return Object.assign({{ sampled: 0,
                                reason: 'no sample inside the frame: shot=' + (r.shot)
                                        + ' rect=' + JSON.stringify(r.rect)
                                        + ' lines=' + JSON.stringify(r.lines || null)
                                        + ' img=' + cv.width + 'x' + cv.height }}, r);
      }}
      var samples = [], worst = null, lums = [];
      pts.forEach(function (pt) {{
        var s = at(pt[0], pt[1]);
        samples.push(s);
        var ink = over({{ rgb: r.ink, a: r.alpha === undefined ? 1 : r.alpha }}, s);
        var q = ratio(ink, s);
        if (!worst || q < worst.ratio) worst = {{ ratio: q, ground: s }};
        lums.push(Math.round(lum(s) * 1000) / 1000);
      }});
      /* A photograph is not a gradient, and a number from one is worse than no
         number at all. Measured spread decides: a linear wash across one text
         box moves a little (the field's own gradient measures 0.003 to 0.024
         across a caption), while an app screenshot under a caption gives 0.012
         to 0.186 and 0.012 to 0.750. Above the threshold the element is reported
         unmeasured with its range, which is what the two app captions and the
         hero's photograph wanted all along. */
      var lo = Math.min.apply(null, lums), hi = Math.max.apply(null, lums);
      if (hi - lo > 0.12) {{
        return Object.assign({{ sampled: 0,
                                reason: 'ground varies too much to be a gradient (photo or mask?): '
                                        + 'luminance ' + lo + ' to ' + hi }}, r);
      }}

      /* `replica` has to be carried through: the first version of this dropped
         it, so the app's own surfaces were counted as site failures. */
      return {{ sampled: samples.length, need: r.need,
                ratio: Math.round(worst.ratio * 100) / 100,
                ground: 'rgb(' + worst.ground.join(', ') + ')',
                lumMin: Math.min.apply(null, lums),
                lumMax: Math.max.apply(null, lums),
                size: r.size, weight: r.weight, sel: r.sel, text: r.text,
                replica: !!r.replica }};
    }});
    out.textContent = 'RESULT:' + JSON.stringify({{ value: {{ width: cv.width, height: cv.height, results: results }} }});
  }} catch (e) {{
    out.textContent = 'RESULT:' + JSON.stringify({{ error: String((e && e.stack) || e) }});
  }}
}})();
</script>
</body></html>
"""


_SCRIPT_ELEMENT = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.S | re.I)


class Handler(http.server.SimpleHTTPRequestHandler):
    """`_site/` for everything, except our harnesses and screenshots, which live
    in a temp dir. Nothing of ours may write into the artifact.

    When a media state is being emulated, the served HTML carries MEDIA_PATCH at
    the top of its head. The artifact on disk is untouched: what changes is the
    copy this run is looking at, which is the only way to change what the page's
    own scripts read out of `matchMedia`."""

    harness = ""
    sampler = ""
    shots: dict = {}
    patch = ""
    patch_scope = ""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=kw.pop("directory"), **kw)

    # Set for the scriptless pass: the served HTML has its script elements
    # removed, which is the only faithful way to ask a browser what a reader
    # whose script never ran is given. Chrome's own `--disable-javascript` would
    # disable the harness too, and the harness is how anything gets measured at
    # all, so the copy is what changes rather than the browser.
    strip_scripts = False

    def do_GET(self):
        patch = type(self).patch
        strip = type(self).strip_scripts
        path = self.translate_path(self.path)
        # A directory is served as its index.html, and that resolution happens in
        # send_head, which is one frame too late for us: asking for `/library/`
        # arrived here as a directory and went out unpatched, which is exactly the
        # shape of bug that looks like "the emulation does nothing".
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        # Both sides absolute: `--site` may arrive relative, and the directory the
        # server was built with is not necessarily the one `abspath` was given.
        scope = type(self).patch_scope
        inside = bool(scope) and os.path.abspath(path).startswith(scope)
        if not (patch or strip) or not inside or not path.lower().endswith((".html", ".htm")):
            return super().do_GET()
        try:
            with open(path, "rb") as fh:
                body = fh.read().decode("utf-8", "replace")
        except OSError:
            return super().do_GET()
        if strip:
            body = _SCRIPT_ELEMENT.sub("", body)
            if "<script" in body.lower():
                # Half-stripped is worse than not stripped: a src script left
                # behind would run and the pass would report the scripted page.
                return super().do_GET()
        data = inject_patch(body, patch).encode("utf-8") if patch else body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def translate_path(self, path):
        p = urllib.parse.urlsplit(path).path
        if p == "/_audit.html":
            return self.harness
        if p == "/_sampler.html":
            return self.sampler
        if p in self.shots:
            return self.shots[p]
        return super().translate_path(path)

    def log_message(self, *a):
        pass


def run_chrome(chrome, profile, args, budget, extra=None):
    """`extra` carries switches a state needs from the BROWSER rather than from the
    cascade, and there is exactly one of those: `--force-prefers-reduced-motion`.

    The reduced-motion pass cannot use the cascade trick the colour states use.
    That trick unwraps the media rules that MATCH the state we are emulating, which
    works when the page's rules for that state are inside such a block and the
    machine is in the other one. Motion is guarded the OPPOSITE way round here: this
    site puts its motion inside `prefers-reduced-motion: no-preference`, so on a
    machine that reports no preference those rules are already applied, and adding
    the reduce rules on top measures a page in both states at once. The first run of
    this pass reported 16 animations running and 31 elements still hidden, all of it
    the no-preference page being measured as though it were the reduced one. The
    browser is asked instead, and Blink answers honestly."""
    cmd = [chrome, "--headless", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--hide-scrollbars",
           "--user-data-dir=" + profile,
           "--virtual-time-budget=" + str(budget)] + list(extra or []) + args
    # encoding= is not optional: without it Python decodes subprocess output with
    # the locale codec, which on a Windows box is cp1252, and the page contains
    # characters cp1252 cannot map. The decode then fails inside subprocess and
    # the error surfaces several frames away as a regex on None.
    return subprocess.run(cmd, capture_output=True, text=True, timeout=420,
                          encoding="utf-8", errors="replace")


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def result_from(proc, what):
    m = re.search(r"RESULT:(.*?)</pre>", proc.stdout, re.S)
    if not m:
        return {"error": "%s produced no result" % what,
                "tail": (proc.stdout[-600:] + proc.stderr[-600:])}
    doc = json.loads(m.group(1))
    return doc


def dump_dom(chrome, profile, url, budget=60000, extra=None):
    return run_chrome(chrome, profile, ["--dump-dom", url], budget, extra)


def screenshot(chrome, profile, url, width, height, out):
    """Write a full-page PNG. Chrome's --screenshot captures the WINDOW, so the
    window is sized to the page: the iframe is already the document's full
    height, and the harness page adds nothing around it."""
    if os.path.exists(out):
        os.remove(out)
    run_chrome(chrome, profile,
               ["--window-size=%d,%d" % (width, height), "--screenshot=" + out, url],
               60000)
    return out if os.path.exists(out) else None


TAP_MIN = 24            # WCAG 2.5.8's minimum, in CSS px


SELF_TEST_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>motion self-test</title>
<style>
  body { margin: 0; padding: 40px; background: #101418; color: #E8ECEE;
         font: 16px/1.5 system-ui, sans-serif; }
  /* Hidden in BOTH states, so it is a hover disclosure rather than a motion
     finding, and the pass must stay quiet about it. */
  .hidden-by-design { visibility: hidden; }
  /* Right: the entrance lives inside the guard, so a reader who asked for less
     motion never sees it run and never sees its from-state. */
  @media (prefers-reduced-motion: no-preference) {
    .guarded { animation: rise 400ms both; }
  }
  /* Wrong: the same entrance outside the guard. This is the defect the pass
     exists to find, and it must be named. */
  .unguarded { animation: rise 3000ms both; }
  @keyframes rise { from { opacity: 0 } to { opacity: 1 } }
</style></head>
<body>
  <p class="guarded">entrance inside the guard</p>
  <p class="unguarded">entrance outside the guard</p>
  <p class="hidden-by-design">hover-only copy</p>
</body></html>
"""


MOTION_PROBE = r"""
(async () => {
  /* REDUCED MOTION, MEASURED RATHER THAN TRUSTED.

     The stylesheet's rule is that every motion item lives inside
     `prefers-reduced-motion: no-preference`, so a reader who asks for less motion
     is handed the FINISHED page: no entrance to sit through, nothing looping, and
     -- the part that is easy to get wrong and impossible to see by reading a
     comment -- no text that is visible only because an entrance was going to lift
     it later.

     This probe runs TWICE and is compared with itself, which is the only reason it
     can be trusted. In the ordinary render (no switch) it finishes every animation
     and transition and then lists what is still invisible: that list is the content
     the page hides ON PURPOSE, the hover disclosures and closed disclosures, and it
     is the baseline. In the reduced render the same list is taken with the switch
     forced and NOTHING finished. Anything invisible there and visible in the
     baseline is invisible because a motion rule was needed to lift it, which is the
     whole defect this pass exists to find. Without the comparison the pass would
     report the citation witnesses, which are a hover affordance and have nothing to
     do with motion; with it, a hand-maintained whitelist is not needed either.

     Finishing animations in the ORDINARY run is the file's usual trade, applied
     where it cannot hide anything: under no preference the finishing is exactly
     what the reader gets a moment later. The reduced run is deliberately left
     unfinished, because there the question is what a reader is given, not what
     they would have been given. */
  let reduced = false;
  try { reduced = w.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  d.querySelectorAll('.is-cold').forEach(function (el) { el.classList.remove('is-cold'); });
  if (!reduced) {
    d.getAnimations().forEach(function (a) { try { a.finish(); } catch (e) {} });
  }
  await new Promise(r => setTimeout(r, 80));

  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');

  /* Named, not just counted. "14 animations still running" is a number nobody can
     act on; the name of each one and of the element it runs on is a repair. */
  let running = 0, animations = 0;
  const moving = [];
  try {
    const all = d.getAnimations();
    animations = all.length;
    for (const a of all) {
      if (a.playState !== 'running') continue;
      running++;
      const target = a.effect && a.effect.target ? name(a.effect.target) : 'the document';
      const what = a.animationName ? 'animation ' + a.animationName
        : a.transitionProperty ? 'transition ' + a.transitionProperty
        : a.constructor && a.constructor.name ? String(a.constructor.name) : 'animation';
      moving.push({ sel: target, why: what + (a.effect && a.effect.getTiming
        ? ' (' + Math.round(Number(a.effect.getTiming().duration) || 0) + 'ms)' : ''),
        text: '' });
    }
  } catch (e) {}

  const fails = [];
  const reason = el => {
    const hidden = el.closest('[hidden]');
    if (hidden) return 'inside an element carrying the hidden attribute';
    const cs = getComputedStyle(el);
    if (el.hidden) return 'the hidden attribute';
    if (cs.display === 'none') return 'display: none';
    if (cs.visibility === 'hidden') return 'visibility: hidden';
    if (parseFloat(cs.opacity || '1') === 0) return 'opacity: 0 with no motion to lift it';
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return 'no box';
    return '';
  };
  let elements = 0;
  for (const el of d.body.querySelectorAll('*')) {
    const own = [].slice.call(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.nodeValue).join('').replace(/\s+/g, ' ').trim();
    if (!own) continue;
    elements++;
    /* Content behind a control is not content that needed motion: a closed
       disclosure is one click away, and the hero's reserved answers are behind
       their chips. Neither is a script or a style block's source text. The
       question here is narrow on purpose, because a motion pass that reports the
       page's own hidden plumbing is a pass nobody reads. */
    if (el.closest('[hidden], details:not([open]), script, style, template, noscript')) continue;
    const why = reason(el);
    if (why) fails.push({ sel: name(el), why: why, text: own.slice(0, 48) });
  }

  return { motion: true, running: running, animations: animations, texts: elements,
           moving: moving, invisible: fails, hidden: fails.length, reduced: reduced,
           /* The same marker every probe carries: a state that was not emulated is
              an error here, not a state that passed. Without it this pass would
              report a page in the machine's own motion setting and call it the
              reduced-motion answer. */
           mediaPatch: w.__auditMediaPatch || "" };
})()
"""


def self_test(chrome, keep=False):
    """Prove the reduced-motion pass can still fail.

    A check that has never failed is a check nobody can trust, and this one nearly
    shipped unable to fail at all: the first version emulated the state in the
    cascade, which for motion meant measuring the ordinary page and reporting 16
    animations running on a site that has none, and a version that reported nothing
    would have looked exactly as convincing. So the pass carries its own site: an
    entrance inside the guard, the same entrance outside it, and a paragraph hidden
    in both renders. It must name the unguarded one, and only that one.

    Run by hand with `--self-test`, after any change to the motion pass.
    """
    tmp = tempfile.mkdtemp(prefix="istor-selftest-")
    site = os.path.join(tmp, "site")
    os.makedirs(site)
    write(os.path.join(site, "index.html"), SELF_TEST_PAGE)
    try:
        v = run_motion_pass(chrome, site, tmp, "/", 1024, 700, 400)
        if v.get("error"):
            print("self-test FAILED - the pass did not run: %s" % v["error"])
            return 1
        named = sorted({f.get("sel") for f in v.get("fails") or []})
        if named != ["p.unguarded"]:
            print("self-test FAILED - expected the unguarded entrance and nothing "
                  "else, and the pass named %r" % (named,))
            return 1
        print("self-test ok - the pass named the entrance outside the guard and "
              "stayed quiet about the guarded one and about the paragraph that is "
              "hidden in both renders")
        return 0
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)


def media_label(media):
    """`{"prefers-color-scheme": "dark", "prefers-contrast": "more"}` reads as
    `os-dark+contrast-more`, sorted so the label is stable."""
    if not media:
        return ""
    short = {"prefers-contrast": "contrast", "prefers-color-scheme": "os",
             "prefers-reduced-motion": "motion"}
    return "+".join("%s-%s" % (short.get(k, k.replace("prefers-", "")), v)
                    for k, v in sorted(media.items()))


def run_tap_pass(chrome, site, tmp, page, width, height, settle):
    """One render at one width, asking only about target size.

    Its own pass rather than a field on the contrast probe, because the answer
    depends on the WIDTH and the other passes are per theme: tap targets do not
    change with the colour scheme, they change when the layout does.
    """
    return run_state(chrome, site, tmp, page, width, height, settle, None, False,
                     None, probe=TAP_PROBE)


def run_motion_pass(chrome, site, tmp, page, width, height, settle):
    """One render with `prefers-reduced-motion: reduce`, asking what a reader who
    asked for less motion is actually given.

    Its own pass rather than a field on the contrast probe, for the reason the
    separator and target checks have their own: the answer is not a colour, it does
    not change with the theme, and the question is about content that may never
    appear at all. Folding it into the AA verdict would let "nothing animating" pass
    as a colour result, which is the kind of silent substitution this tool exists to
    refuse."""
    # The browser is asked, not the cascade: see run_chrome's note. No media map
    # here on purpose, because the state must come from one place, and a run that
    # both forced the flag and unwrapped rules would be measuring neither.
    def key(of):
        return (of.get("sel"), (of.get("text") or "")[:24])

    ordinary = run_state(chrome, site, tmp, page, width, height, settle, None, False,
                         probe=MOTION_PROBE)
    if "error" in ordinary:
        return ordinary
    # A run that did not get the state it asked for is an error, not a pass. This is
    # the same insistence the media patch gets, and it is the more necessary of the
    # two: without it, a browser that ignored the switch would report the ordinary
    # page as the reduced-motion page and call every entrance animation "running
    # with motion reduced", which is exactly what the first version of this pass
    # did.
    if ordinary.get("reduced"):
        return {"error": "the ordinary render reported prefers-reduced-motion: reduce, "
                         "so there was no baseline to compare the reduced render with"}
    v = run_state(chrome, site, tmp, page, width, height, settle, None, False,
                  probe=MOTION_PROBE, extra=["--force-prefers-reduced-motion"])
    if "error" in v:
        return v
    if not v.get("reduced"):
        return {"error": "the browser did not report prefers-reduced-motion: reduce, "
                         "so the reduced-motion state was NOT audited"}

    # What the page hides on purpose, settled and with motion allowed. Everything
    # invisible in the reduced render that is NOT in this set is invisible because a
    # motion rule was needed to lift it.
    by_design = {key(of): of for of in (ordinary.get("invisible") or [])}
    v["byDesign"] = len(by_design)
    v["fails"] = list(v.get("moving") or [])
    for of in (v.get("invisible") or []):
        if key(of) in by_design:
            continue
        v["fails"].append(dict(of, why=(of.get("why") or "invisible") +
                               ", and the ordinary render shows it"))
    return v


def run_seam_pass(chrome, site, tmp, page, width, height, settle):
    """One render, asking only whether each window has the right separator.

    Its own pass for the same reason target size has one: the answer is a fact
    about the ground a window stands on, which is decided by layout and the
    cascade rather than by the colour scheme. One render per page is enough, and it
    keeps the finding on its own line instead of buried in a contrast verdict.
    """
    return run_state(chrome, site, tmp, page, width, height, settle, None, False,
                     None, probe=SEAM_PROBE)


def run_state(chrome, site, tmp, page, width, height, settle, theme, pixels,
              media=None, scripts=True, probe=None, extra=None):
    """One theme and one media state, one render: probe the cascade, then sample
    the pixels of the SAME render. The theme is forced by the harness before the
    page is parsed, and the media state by unwrapping the page's own media rules
    before anything is measured. `media` is a map of feature to emulated value,
    or None for the state the machine is actually in.

    `scripts=False` is the reader whose script never ran: the served page has its
    script elements removed, no theme is forced and no media state is emulated,
    and a different probe asks what got painted rather than what passes AA."""
    profile = os.path.join(tmp, "profile")
    tag = "-".join(x for x in (theme or "asis", media_label(media),
                               "" if scripts else "noscript",
                               "tap%d" % width if probe else "") if x)
    if extra:
        tag += "-forced"
    write(os.path.join(tmp, "audit-%s.html" % tag),
          HARNESS.format(w=width, h=height, url=page,
                         expr=json.dumps(probe or (PROBE if scripts else NOSCRIPT_PROBE)),
                         settle=settle, theme=json.dumps(theme or ""),
                         media=json.dumps(media or {})))
    Handler.harness = os.path.join(tmp, "audit-%s.html" % tag)
    Handler.strip_scripts = not scripts
    # The patch rides on the page the iframe loads, not on the harness, so it can
    # only touch files under the site it was pointed at.
    Handler.patch = MEDIA_PATCH.format(media=json.dumps(media or {})) if media else ""
    Handler.patch_scope = os.path.abspath(site) + os.sep
    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), lambda *a, **kw: Handler(*a, directory=site, **kw))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        doc = result_from(dump_dom(chrome, profile, base + "/_audit.html", 60000, extra),
                          "probe")
        if "error" in doc:
            return doc
        v = doc["value"]
        v["media"] = media
        v["scripts"] = scripts
        v["mediaRules"] = v.get("mediaRules") or 0
        # The patched matchMedia is what decides BOTH halves of this: whether the
        # page's own scripts pick a world, and whether the emulation finds any rule
        # to unwrap. If it did not install, this state was not audited at all, and
        # saying "ok" about it would be the tool's worst possible answer.
        if media and v.get("mediaPatch") != ",".join(sorted(media)):
            v["error"] = ("the matchMedia patch did not install (%r), so the %s state "
                          "was NOT emulated" % (v.get("mediaPatch"), media_label(media)))
        if not pixels or not v.get("gradient"):
            v["onPixels"] = []
            return v

        # One screenshot per viewport, and the rects translated into that
        # image's own coordinates. A single tall capture is not available:
        # Chrome clamps the window, and everything below the clamp reads as the
        # image's last row.
        vh = int(v.get("viewportHeight") or height)
        per_view: dict[int, list[dict]] = {}
        for g in v["gradient"]:
            # A record the probe found covered by the fixed bar names the scroll
            # that clears it (see the occlusion note in PROBE). Its rect is
            # translated by THAT scroll and its picture is taken there, so the
            # element stays measured instead of being sampled through the bar.
            # Anchors that only this record asked for cost one extra screenshot,
            # which is why the probe only records one when hit-testing proved it.
            covered = g.pop("covered", None)
            anchor = int(covered) if covered is not None else int(g.get("anchor") or 0)
            g["rect"]["y"] -= anchor
            for L in g.get("lines") or []:
                L["y"] -= anchor
            g["_anchor"] = anchor
            per_view.setdefault(anchor, []).append(g)

        shots, shots_url = [], []
        write(os.path.join(tmp, "shot-%s.html" % tag),
              HARNESS.format(w=width, h=vh, url=page, expr=json.dumps("null"),
                             settle=settle, theme=json.dumps(theme or ""),
                             media=json.dumps(media or {})))
        Handler.harness = os.path.join(tmp, "shot-%s.html" % tag)
        # The image index is the POSITION in the shot list, not the viewport
        # number: the list only holds the viewports that had gradient text in
        # them, and the sampler indexes its images by position.
        for pos, anchor in enumerate(sorted(per_view)):
            for g in per_view[anchor]:
                g["shot"] = pos
            out = os.path.join(tmp, "shot-%s-%d.png" % (tag, anchor))
            url = base + "/_audit.html?scroll=" + str(anchor)
            if not screenshot(chrome, profile, url, width, vh, out):
                v["error"] = "screenshot at scroll %d was not written" % anchor
                return v
            shots.append(out)
            shots_url.append("/_shot-%d.png" % pos)
            Handler.shots["/_shot-%d.png" % pos] = out

        # The sampler is its own harness: it loads each PNG into a canvas and
        # reads the pixels beside every text box. Same origin, so the canvas is
        # readable, and this needs no image library on the machine.
        write(os.path.join(tmp, "sampler-%s.html" % tag),
              SAMPLER.format(rects=json.dumps(v["gradient"]),
                             shots=json.dumps(shots_url)))
        Handler.sampler = os.path.join(tmp, "sampler-%s.html" % tag)
        doc2 = result_from(dump_dom(chrome, profile, base + "/_sampler.html"), "sampler")
        if "error" in doc2:
            v["error"] = doc2["error"]
            return v
        v["onPixels"] = doc2["value"]["results"]
        v["unpixelled"] = [{"sel": g.get("sel"), "text": g.get("text"),
                            "reason": g.get("reason") or "no sample point"}
                           for g in doc2["value"]["results"] if not g.get("sampled")]
        v["shots"] = len(shots)
        v["clipped"] = False
        return v
    finally:
        srv.shutdown()


def media_states(contrast_more, os_dark, as_authored):
    """The media states worth rendering for one theme pass.

    `prefers-color-scheme` is emulated ONLY for the pass that forces no theme,
    and deliberately: the library's rule for a dark OS is written as
    `:root:not([data-theme="light"])`, so a stored choice outranks the machine and
    a dark-OS run against a stamped theme would measure a world the reader does
    not get. `contrast_more` is orthogonal and applies to both, because the stamp
    and the contrast world are independent decisions."""
    out = []
    if contrast_more:
        out.append({"prefers-contrast": "more"})
    if os_dark and as_authored:
        out.append({"prefers-color-scheme": "dark"})
        if contrast_more:
            out.append({"prefers-color-scheme": "dark", "prefers-contrast": "more"})
    return out


def audit_page(chrome, site, tmp, page, width, height, settle, pixels=True,
               contrast_more=True, os_dark=True, scriptless=True, tap_widths=True,
               seam=True, motion=True):
    """Every theme and media state this page can be delivered in, as a list.

    The first pass forces nothing, so a page with no theme control is audited in
    the state it actually ships in, and a page with one is audited in the state a
    reader who has never touched that control arrives to. Each of those passes is
    then repeated under the emulated media states from media_states(): what the
    stylesheets promise a reader who asks for more contrast, and, for the unstamped
    pass, what a reader on a dark machine is given with no stored choice at all.
    Both were asserted before they were measured, and the second one is the state
    no render on this machine had ever covered, because headless Chrome reports a
    light OS."""
    first = run_state(chrome, site, tmp, page, width, height, settle, None, pixels)
    if first.get("error"):
        return first
    states = [first]
    for media in media_states(contrast_more, os_dark, True):
        states.append(run_state(chrome, site, tmp, page, width, height, settle,
                                None, pixels, media))
    # The reader whose script never ran, in the state they would arrive in: no
    # forced theme (the stamp is gone, so the media queries alone decide) and no
    # emulated media state, because both of those are things this site does with
    # script. Its probe is a different question from the rest of this tool's, so
    # it reports on its own line.
    if scriptless:
        states.append(run_state(chrome, site, tmp, page, width, height, settle,
                                None, False, None, scripts=False))
    if seam:
        states.append(run_seam_pass(chrome, site, tmp, page, width, height, settle))
    if motion:
        states.append(run_motion_pass(chrome, site, tmp, page, width, height, settle))
    for tap_width in ([width, PHONE_WIDTH] if tap_widths and width != PHONE_WIDTH
                      else [width] if tap_widths else []):
        states.append(run_tap_pass(chrome, site, tmp, page, tap_width, height, settle))
    if (first.get("themeControl") or {}).get("found"):
        other = "dark" if first.get("state") != "dark" else "light"
        states.append(run_state(chrome, site, tmp, page, width, height, settle,
                                other, pixels))
        for media in media_states(contrast_more, os_dark, False):
            states.append(run_state(chrome, site, tmp, page, width, height, settle,
                                    other, pixels, media))
    return {"states": states}


def main(argv):
    # The pages contain Greek, curly quotes and dashes, and a Windows console is
    # cp1252 by default: printing a finding would then crash INSIDE the report,
    # which is the one place a tool must not fail. Same lesson as the subprocess
    # decoding above, one layer up.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--pages", nargs="+", default=DEFAULT_PAGES)
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--settle", type=int, default=700)
    ap.add_argument("--no-pixels", action="store_true",
                    help="skip the screenshot pass; gradient grounds stay unmeasured")
    ap.add_argument("--no-contrast-more", action="store_true",
                    help="skip the emulated prefers-contrast: more pass")
    ap.add_argument("--no-os-dark", action="store_true",
                    help="skip the emulated dark-OS pass on the unstamped theme")
    ap.add_argument("--no-tap", action="store_true",
                    help="skip the WCAG 2.5.8 target-size pass")
    ap.add_argument("--no-seam", action="store_true",
                    help="skip the pass that asks whether every window carries the "
                         "separator its ground calls for")
    ap.add_argument("--no-motion", action="store_true",
                    help="skip the reduced-motion pass, which asks what a reader "
                         "who asked for less motion is given")
    ap.add_argument("--no-scriptless", action="store_true",
                    help="skip the pass that serves each page with its scripts "
                         "removed, for the reader whose script never ran")
    ap.add_argument("--self-test", action="store_true",
                    help="check that the reduced-motion pass can still fail, against "
                         "a tiny site built for it, and exit")
    ap.add_argument("--json", default=None, help="write the findings here")
    a = ap.parse_args(argv[1:])

    if not os.path.isdir(a.site):
        sys.exit("audit-contrast: %s is missing. Run python Source/tools/build-site.py"
                 % a.site)
    chrome = find_chrome()
    if a.self_test:
        return self_test(chrome)
    pages = [page_path(p) for p in a.pages]

    findings, failures, tap_fails, seam_fails, motion_fails = [], 0, 0, 0, 0
    with tempfile.TemporaryDirectory(prefix="istor-audit-") as tmp:
        for page in pages:
            r = audit_page(chrome, a.site, tmp, page, a.width, a.height, a.settle,
                           pixels=not a.no_pixels,
                           contrast_more=not a.no_contrast_more,
                           os_dark=not a.no_os_dark,
                           scriptless=not a.no_scriptless,
                           tap_widths=not a.no_tap,
                           seam=not a.no_seam,
                           motion=not a.no_motion)
            if r.get("error"):
                print("  FAIL  %s  %s" % (page, r["error"]))
                failures += 1
                findings.append({"page": page, "error": r["error"]})
                continue
            for index, s in enumerate(r["states"]):
                if not s:
                    continue
                if s.get("unpixelled"):
                    for u in s["unpixelled"][:4]:
                        print("  --    not sampled  %s  %s  %r"
                              % (u["sel"], u["reason"], u["text"]))
                if s.get("error"):
                    print("  FAIL  %s state %d  %s" % (page, index, s["error"]))
                    # Counted against the pass it belongs to rather than against
                    # contrast: a separator pass that measured nothing is not five
                    # text elements below AA, and the final line reports both.
                    if s.get("seam"):
                        seam_fails += 1
                    else:
                        failures += 1
                    continue
                if s.get("seam"):
                    # §3.4's separator rule, measured at every width this page is
                    # drawn at. Reported per page rather than per state: a window's
                    # ground does not change with the colour scheme, and a pass that
                    # claimed to check it twice would only be checking twice.
                    seam_fails += len(s["fails"])
                    print("  %s  %-42s %3d windows  %2d on a dark ground  "
                          "%2d on paper  %d FAIL"
                          % ("ok  " if not s["fails"] else "FAIL",
                             "%s separators@%dpx" % (page, s["width"]), s["windows"],
                             s["onDark"], s["onPaper"], len(s["fails"])))
                    for f in s["fails"]:
                        print("          %s on %s (luminance %.3f)  %s\n              %s"
                              % (f["sel"], f["ground"], f["groundLum"], f["why"], f["border"]))
                    findings.append({"page": page, "seam": True, "width": s["width"],
                                     "windows": s["windows"], "onDark": s["onDark"],
                                     "onPaper": s["onPaper"], "fails": s["fails"]})
                    continue
                if s.get("tap"):
                    # WCAG 2.5.8 at AA, measured rather than assumed. The two
                    # exceptions are counted separately and printed, because an
                    # exception that is not itemised is indistinguishable from a
                    # check that did not run.
                    tap_fails += len(s["fails"])
                    print("  %s  %-42s %3d targets  %2d under %dpx  %2d inline  "
                          "%2d spacing-exempt  %d FAIL"
                          % ("ok  " if not s["fails"] else "FAIL",
                             "%s targets@%dpx" % (page, s["width"]), s["targets"],
                             s["under"], TAP_MIN, s["inline"], s["spaced"],
                             len(s["fails"])))
                    for t in s["fails"]:
                        print("          %dx%d  %s  %r  (blocked by %s)"
                              % (t["w"], t["h"], t["sel"], t["text"], t["blockedBy"]))
                    findings.append({"page": page, "tap": True, "width": s["width"],
                                     "targets": s["targets"], "under": s["under"],
                                     "inline": s["inline"], "spaced": s["spaced"],
                                     "fails": s["fails"]})
                    continue
                if s.get("motion"):
                    # REDUCED MOTION, MEASURED. The stylesheet promises that every
                    # motion item sits inside `prefers-reduced-motion: no-preference`,
                    # so a reader who asks for less motion gets the finished page. Two
                    # questions are asked rather than assumed: is anything still
                    # moving, and is any text invisible in a render where no entrance
                    # will ever lift it. The second one is the same test the scriptless
                    # pass makes, for the same reason.
                    motion_fails += len(s["fails"])
                    print("  %s  %-42s %3d text elements  %2d running  %2d hidden "
                          "either way  %d FAIL"
                          % ("ok  " if not s["fails"] else "FAIL",
                             "%s reduced-motion" % page, s["texts"], s["running"],
                             s["byDesign"], len(s["fails"])))
                    for f in s["fails"]:
                        print("          %s  %s  %r" % (f["sel"], f["why"], f["text"]))
                    findings.append({"page": page, "motion": True, "running": s["running"],
                                     "animations": s["animations"], "texts": s["texts"],
                                     "byDesign": s["byDesign"], "fails": s["fails"]})
                    continue
                if s.get("scripts") is False:
                    # The scriptless reader gets the comparison and the inventory
                    # instead of an AA verdict: this render was not about
                    # contrast, it was about whether the page still says anything.
                    base = next((x.get("chars", 0) for x in r["states"]
                                 if x.get("scripts") is not False), 0)
                    share = ("%.0f%% of the %d characters the scripted page paints"
                             % (100.0 * s["chars"] / base, base)) if base else ""
                    print("  --    %-42s %5d chars  %3d links  %2d controls  "
                          "%2d elements present but invisible  %s"
                          % ("%s scriptless" % page, s["chars"], s["links"],
                             s["controls"], len(s["invisible"]), share))
                    for item in s["invisible"][:8]:
                        print("          %s  %s  %r" % (item["sel"], item["why"], item["text"]))
                    if len(s["invisible"]) > 8:
                        print("          and %d more" % (len(s["invisible"]) - 8))
                    findings.append({"page": page, "scripts": False,
                                     "chars": s["chars"], "links": s["links"],
                                     "controls": s["controls"],
                                     "scriptedChars": base,
                                     "invisible": s["invisible"]})
                    continue
                label = "%s %s" % (page, s.get("state") or "single-theme")
                if s.get("media"):
                    label += " +" + media_label(s["media"])
                n_grad = len(s["gradient"])
                on_pixels = [g for g in s.get("onPixels", []) if g.get("sampled")]
                unpixelled = n_grad - len(on_pixels)
                # Replica content is the app's own surface, measured against the
                # product's inks rather than this site's. Reported, not counted.
                flat = [f for f in s["fails"] if not f.get("replica")]
                in_replica = (len(s["fails"]) - len(flat)
                              + len([g for g in on_pixels if g.get("replica")]))
                on_pixels = [g for g in on_pixels if not g.get("replica")]
                below = list(flat)
                for g in on_pixels:
                    if g["ratio"] < g["need"]:
                        below.append(g)
                failures += len(below)
                mark = "ok  " if not below else "FAIL"
                ctl = s.get("themeControl") or {}
                ctl_note = ""
                if s.get("media"):
                    # Say how many media rules the emulation found, because zero is
                    # a page that does not style this state, which is not the same
                    # result as a state that passed.
                    ctl_note = "  %d media rules" % s.get("mediaRules", 0)
                elif ctl.get("found"):
                    ctl_note = "  control %s->%s" % (ctl.get("from"), ctl.get("to"))
                    if not ctl.get("flipped"):
                        ctl_note += " NOT FLIPPED"
                        failures += 1
                elif index == 0:
                    ctl_note = "  no theme control"
                print("  %s  %-42s %3d elements  %2d views  %2d flat-fail  "
                      "%3d on pixels  %2d unmeasured  %2d replica  %d below AA%s"
                      % (mark, label, s["checked"], s["viewports"], len(flat),
                         len(on_pixels), unpixelled, in_replica, len(below), ctl_note))
                for f in flat:
                    print("          %.2f:1 (needs %s)  %s  %s on %s\n              %r"
                          % (f["ratio"], f["need"], f["sel"], f["color"], f["ground"], f["text"]))
                for g in on_pixels:
                    if g["ratio"] >= g["need"]:
                        continue
                    print("          %.2f:1 (needs %s)  %s  ink on sampled %s "
                          "(luminance %.3f to %.3f, %d samples)\n              %r"
                          % (g["ratio"], g["need"], g["sel"], g["ground"],
                             g["lumMin"], g["lumMax"], g["sampled"], g["text"]))
                findings.append({"page": page, "theme": s.get("state"),
                                 "media": s.get("media"),
                                 "mediaRules": s.get("mediaRules", 0),
                                 "themeControl": ctl,
                                 "flatFails": s["fails"], "onPixels": on_pixels,
                                 "unmeasured": unpixelled,
                                 "gradient": s["gradient"], "checked": s["checked"],
                                 "viewports": s["viewports"]})

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(findings, fh, indent=1)
        print("\nfindings written to %s" % a.json)

    states = [f for f in findings if "checked" in f]
    emulated = [f for f in states if f.get("media")]
    # Name the emulated states rather than counting them: "3 of them emulated" is
    # not a report anybody can act on, and a run that silently dropped one because
    # a page has no theme control would look identical to one that did not.
    kinds = sorted({media_label(f["media"]) for f in emulated})
    note = ("%d of them emulated (%s)" % (len(emulated), ", ".join(kinds))
            if emulated else "no media state emulated")
    seam = [f for f in findings if f.get("seam")]
    if seam:
        print("\n%d separator passes: %d windows, %d standing on a dark ground and "
              "%d on paper"
              % (len(seam), sum(f["windows"] for f in seam),
                 sum(f["onDark"] for f in seam), sum(f["onPaper"] for f in seam)))

    tap = [f for f in findings if f.get("tap")]
    if tap:
        print("\n%d target-size passes: %d controls, %d under %dpx, %d excused as "
              "inline text and %d by spacing"
              % (len(tap), sum(f["targets"] for f in tap),
                 sum(f["under"] for f in tap), TAP_MIN,
                 sum(f["inline"] for f in tap), sum(f["spaced"] for f in tap)))

    motion_passes = [f for f in findings if f.get("motion")]
    if motion_passes:
        print("\n%d reduced-motion passes, each compared against its own ordinary "
              "render: %d text elements seen, %d animations running with motion "
              "reduced, %d elements hidden either way"
              % (len(motion_passes), sum(f["texts"] for f in motion_passes),
                 sum(f["running"] for f in motion_passes),
                 sum(f["byDesign"] for f in motion_passes)))

    scriptless = [f for f in findings if f.get("scripts") is False]
    print("\n%d page-states audited at %dpx, %s%s"
          % (len(states), a.width, note,
             ", plus %d scriptless pass%s"
             % (len(scriptless), "es" if len(scriptless) != 1 else "")
             if scriptless else ""))
    if failures or tap_fails or seam_fails or motion_fails:
        print("FAILED - %d below AA, %d targets under %dpx with neither exception, "
              "%d windows without the separator their ground calls for, "
              "%d in a reduced-motion render that is not the finished page"
              % (failures, tap_fails, TAP_MIN, seam_fails, motion_fails))
        return 1
    print("contrast ok - nothing below AA where the ground could be measured")
    if seam:
        print("separators ok - every window carries the separator its ground calls for")
    if tap:
        print("targets ok - every control reaches %dpx, or is excused" % TAP_MIN)
    if motion_passes:
        print("motion ok - with motion reduced nothing runs and nothing is held "
              "invisible by an entrance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
