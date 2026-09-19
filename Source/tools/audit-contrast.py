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

WHAT IT SETTLES FIRST. `is-cold` is this site's name for not-yet-revealed, and the
revealing observers answer a real visitor's scrolling rather than a programmatic
one. Every cold class is therefore cleared, and the longest transition waited out,
before anything is measured, which measures the page a visitor reads rather than one
frame of the animation they watch. The cost is stated rather than hidden: a
pre-reveal state that was genuinely unreadable would be settled away instead of
reported.

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

DEFAULT_PAGES = ["/", "/changelog/", "/vs-chatgpt/"]


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
    await new Promise(r => setTimeout(r, 800));
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
             checked: checked, viewports: steps, fails: fails, gradient: gradient };
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


class Handler(http.server.SimpleHTTPRequestHandler):
    """`_site/` for everything, except our harnesses and screenshots, which live
    in a temp dir. Nothing of ours may write into the artifact."""

    harness = ""
    sampler = ""
    shots: dict = {}

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=kw.pop("directory"), **kw)

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


def run_chrome(chrome, profile, args, budget):
    cmd = [chrome, "--headless", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--hide-scrollbars",
           "--user-data-dir=" + profile,
           "--virtual-time-budget=" + str(budget)] + args
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


def dump_dom(chrome, profile, url, budget=60000):
    return run_chrome(chrome, profile, ["--dump-dom", url], budget)


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


def run_state(chrome, site, tmp, page, width, height, settle, theme, pixels):
    """One theme, one render: probe the cascade, then sample the pixels of the
    SAME render. The theme is forced by the harness before the page is parsed."""
    profile = os.path.join(tmp, "profile")
    tag = theme or "asis"
    write(os.path.join(tmp, "audit-%s.html" % tag),
          HARNESS.format(w=width, h=height, url=page, expr=json.dumps(PROBE),
                         settle=settle, theme=json.dumps(theme or "")))
    Handler.harness = os.path.join(tmp, "audit-%s.html" % tag)
    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), lambda *a, **kw: Handler(*a, directory=site, **kw))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        doc = result_from(dump_dom(chrome, profile, base + "/_audit.html"), "probe")
        if "error" in doc:
            return doc
        v = doc["value"]
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
            anchor = int(g.get("anchor") or 0)
            g["rect"]["y"] -= anchor
            for L in g.get("lines") or []:
                L["y"] -= anchor
            g["_anchor"] = anchor
            per_view.setdefault(anchor, []).append(g)

        shots, shots_url = [], []
        write(os.path.join(tmp, "shot-%s.html" % tag),
              HARNESS.format(w=width, h=vh, url=page, expr=json.dumps("null"),
                             settle=settle, theme=json.dumps(theme or "")))
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


def audit_page(chrome, site, tmp, page, width, height, settle, pixels=True):
    """Both themes of one page. The first pass forces nothing, so a page with no
    theme control is audited in the state it actually ships in."""
    first = run_state(chrome, site, tmp, page, width, height, settle, None, pixels)
    if first.get("error"):
        return first
    out = {"first": first, "second": None}
    if (first.get("themeControl") or {}).get("found"):
        other = "dark" if first.get("state") != "dark" else "light"
        out["second"] = run_state(chrome, site, tmp, page, width, height, settle,
                                  other, pixels)
    return out


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
    ap.add_argument("--json", default=None, help="write the findings here")
    a = ap.parse_args(argv[1:])

    if not os.path.isdir(a.site):
        sys.exit("audit-contrast: %s is missing. Run python Source/tools/build-site.py"
                 % a.site)
    chrome = find_chrome()
    pages = [page_path(p) for p in a.pages]

    findings, failures = [], 0
    with tempfile.TemporaryDirectory(prefix="istor-audit-") as tmp:
        for page in pages:
            r = audit_page(chrome, a.site, tmp, page, a.width, a.height, a.settle,
                           pixels=not a.no_pixels)
            if r.get("error"):
                print("  FAIL  %s  %s" % (page, r["error"]))
                failures += 1
                findings.append({"page": page, "error": r["error"]})
                continue
            for state in ("first", "second"):
                s = r.get(state)
                if not s:
                    continue
                if s.get("unpixelled"):
                    for u in s["unpixelled"][:4]:
                        print("  --    not sampled  %s  %s  %r"
                              % (u["sel"], u["reason"], u["text"]))
                if s.get("error"):
                    print("  FAIL  %s %s  %s" % (page, state, s["error"]))
                    failures += 1
                    continue
                label = "%s %s" % (page, s.get("state") or "single-theme")
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
                if ctl.get("found"):
                    ctl_note = "  control %s->%s" % (ctl.get("from"), ctl.get("to"))
                    if not ctl.get("flipped"):
                        ctl_note += " NOT FLIPPED"
                        failures += 1
                elif state == "first":
                    ctl_note = "  no theme control"
                print("  %s  %-32s %3d elements  %2d views  %2d flat-fail  "
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
                                 "themeControl": ctl,
                                 "flatFails": s["fails"], "onPixels": on_pixels,
                                 "unmeasured": unpixelled,
                                 "gradient": s["gradient"], "checked": s["checked"],
                                 "viewports": s["viewports"]})

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(findings, fh, indent=1)
        print("\nfindings written to %s" % a.json)

    pages_audited = sum(1 for f in findings if "checked" in f)
    print("\n%d page-states audited at %dpx" % (pages_audited, a.width))
    if failures:
        print("FAILED - %d below AA" % failures)
        return 1
    print("contrast ok - nothing below AA where the ground could be measured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
