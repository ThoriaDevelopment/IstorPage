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

WHAT IT DOES NOT MEASURE, and refuses to guess: a ground carrying a gradient,
a photograph or a mask. The ratio there is arithmetic on one sample of a wash
that changes across the box, so those elements are counted as "gradient" and
listed, never as a pass. `SITE_DESIGN_PLAN_V2.md`'s measured pairs are what
covers them.

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
    const steps = Math.min(24, Math.ceil(d.documentElement.scrollHeight / vh));
    for (let i = 0; i < steps; i++) {
      w.scrollTo({ top: i * vh, behavior: 'instant' });
      await new Promise(r => setTimeout(r, 40));
      for (const el of d.body.querySelectorAll('*')) {
        if (seen.has(el)) continue;
        const txt = textOf(el);
        if (!txt) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (el.closest('[hidden]')) continue;
        if (parseFloat(cs.opacity) === 0) continue;
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
        };
        if (g.gradient) { gradient.push(rec); continue; }
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

  const first = await audit();
  const btn = d.querySelector('.theme-toggle');
  let second = null;
  if (btn && !btn.hidden) {
    btn.click();
    await new Promise(r => setTimeout(r, 150));
    second = await audit();
  }
  return {
    first: { theme: first.theme, checked: first.checked, viewports: first.viewports,
             fails: first.fails, gradient: first.gradient.length },
    second: second ? { theme: second.theme, checked: second.checked,
                       viewports: second.viewports, fails: second.fails,
                       gradient: second.gradient.length } : null,
  };
})()
"""

HARNESS = """<!doctype html>
<html><head><meta charset="utf-8"><title>audit</title>
<style>html,body{{margin:0;padding:0}}iframe{{border:0;display:block}}</style></head>
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
    var fn = new Function('d', 'w', 'return (' + {expr} + ')');
    out.textContent = 'RESULT:' + JSON.stringify({{ value: await fn(d, w) }});
  }} catch (e) {{
    out.textContent = 'RESULT:' + JSON.stringify({{ error: String((e && e.stack) || e) }});
  }}
}});
setTimeout(function () {{ if (out.textContent === 'PENDING') out.textContent = 'RESULT:' + JSON.stringify({{ error: 'no load event' }}); }}, {settle} + 8000);
</script>
</body></html>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    """`_site/` for everything, except the harness, which lives in a temp dir."""

    harness = ""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=kw.pop("directory"), **kw)

    def translate_path(self, path):
        if path.split("?")[0] == "/_audit.html":
            return self.harness
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


def audit_page(chrome, site, tmp, page, width, height, settle):
    harness = os.path.join(tmp, "audit.html")
    with open(harness, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HARNESS.format(w=width, h=height, url=page, expr=json.dumps(PROBE),
                                settle=settle))
    Handler.harness = harness
    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), lambda *a, **kw: Handler(*a, directory=site, **kw))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/_audit.html" % srv.server_address[1]
    try:
        p = run_chrome(chrome, os.path.join(tmp, "profile"), ["--dump-dom", url], 30000)
        m = re.search(r"RESULT:(.*?)</pre>", p.stdout, re.S)
        if not m:
            return {"error": "no result", "tail": (p.stdout[-800:] + p.stderr[-800:])}
        doc = json.loads(m.group(1))
        if "error" in doc:
            return doc
        return doc["value"]
    finally:
        srv.shutdown()


def main(argv):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--pages", nargs="+", default=DEFAULT_PAGES)
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--settle", type=int, default=700)
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
            r = audit_page(chrome, a.site, tmp, page, a.width, a.height, a.settle)
            if r.get("error"):
                print("  FAIL  %s  %s" % (page, r["error"]))
                failures += 1
                findings.append({"page": page, "error": r["error"]})
                continue
            for state in ("first", "second"):
                s = r.get(state)
                if not s:
                    continue
                label = "%s %s" % (page, s["theme"] or "single-theme")
                n = len(s["fails"])
                failures += n
                mark = "ok  " if n == 0 else "FAIL"
                print("  %s  %-38s %3d text elements  %2d viewports  %2d gradient  %d below AA"
                      % (mark, label, s["checked"], s["viewports"], s["gradient"], n))
                for f in s["fails"]:
                    print("          %.2f:1 (needs %s)  %s  %s on %s\n              %r"
                          % (f["ratio"], f["need"], f["sel"], f["color"], f["ground"], f["text"]))
                findings.append({"page": page, "theme": s["theme"], **s})

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
