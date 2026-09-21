#!/usr/bin/env python3
"""Drive the mechanism and check what it does, which no other gate can see.

    python Source/tools/audit-motion.py
    python Source/tools/audit-motion.py --self-test
    python Source/tools/audit-motion.py --json findings.json

WHY THIS EXISTS. Three things are now true of the two worlds and none of them was
asserted by anything. The pinion's ratio against the drawings, the momentum's
constants against the notes, and the drawings against the script are all
build-time facts, and `verify-links.py` holds them. What no build-time fact can
reach is BEHAVIOUR: that a careful read leaves the wheel exactly where the scroll
put it, that a thrown page charges it, that the coast ends, that the hand turns
it, that a touch is never taken, and that with motion reduced the world is never
written at all. Each of those was verified once by hand, in a browser, through
probes that lived in `.improvement/` and were deleted with the session that wrote
them. Twice in one night a claim in the notes turned out to describe a gate that
no longer existed. This is the answer to that: the claims become assertions.

WHY IT IS AN audit- AND NOT A verify-. The three `verify-*.py` tools run in CI and
install nothing, which is why they are pure standard library. This one drives
headless Chrome, exactly like `audit-contrast.py`, and it cannot run there for the
same reason. The two audits divide the same way: that one asks what a reader is
GIVEN, this one asks what the page DOES when it is used.

WHAT MAKES IT DETERMINISTIC, and this is the lesson that cost the most to learn.
Chrome advances virtual time under `--virtual-time-budget`, so a scenario of eight
seconds of gestures finishes in the time it takes to parse it, and timers fire in
the order this file wrote them down. The events are DISPATCHED at instants this
file chooses rather than read from the browser's own stream, because a real stream
coalesces: during one evening's probing, eight scrolls arrived as three events with
gaps of 1.1 seconds, and a single 500px delivery then looked exactly like a fast
gesture. A gate that depends on the compositor's delivery is a gate that reports the
machine. The scenario therefore scrolls instantaneously and dispatches its own
scroll event, so the page's handler sees the timing this file wrote down.

WHY IT DOES NOT REUSE `audit-contrast.py`'s HARNESS, since it borrows the rest of
that tool's approach. That harness reads its answer out of the DOM with
`--dump-dom`, which fires when the page loads, so it needs `--virtual-time-budget`
to make the browser wait for a scenario at all - and under the virtual clock this
renderer produces almost no animation frames. A probe that counted them saw FOUR in
three seconds: old headless and new, with and without every frame switch worth
trying, and with a running CSS animation in the page to force invalidation. Since
the momentum is advanced by `requestAnimationFrame`, the wheel would receive its
charge and never turn. Worse, a page that keeps requesting frames STALLS the virtual
clock instead of finishing, and two runs sat for the full 420-second subprocess
timeout rather than reporting anything.

So here the answer is DELIVERED rather than dumped: the harness posts the scenario's
value back to this tool's own server, Chrome runs in REAL TIME, and the scenario's
waits are the waits a reader's browser would make. That is what makes the coast and
the settle assertable rather than merely measurable, and it is why this file can
claim twelve things where the first draft could honestly claim nine.

IT REUSES `audit-contrast.py` BY PATH. That harness already solves the two hard
parts of putting a page under a controlled browser: a server that can hand the page
over patched, and an iframe whose size decides the media queries (a `--window-size`
request comes back clamped, and then the page resolves against a width nobody
asked for). A second copy of that would be a second thing to keep in step, and the
repo's own note on duplication settles where the line is: a shared module is worth
it once the shared code is more than a handful of lines. It is several hundred.
"""
from __future__ import annotations

import argparse
import http.server
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load_sibling(name: str):
    """Import `audit-contrast.py`, whose hyphen keeps it out of an import statement."""
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        sys.exit("audit-motion: %s is missing, and this tool is built on its "
                 "harness rather than on a second copy of one" % path)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


AC = load_sibling("audit-contrast.py")


# The scenario. The harness evaluates ONE EXPRESSION and awaits the result, so the
# expression ends by calling itself with `d` (the framed document) and `w` (its
# window) in scope. Everything here runs inside the real page, against the real
# listeners, in the order a reader would produce it. Forgetting the call is the
# quiet failure worth naming: the harness still reports success, with the probe's
# value simply absent, and a checker that only looked for "error" would read that
# as a page that behaved perfectly.
SCENARIO = r"""
(async (d, w) => {
  const wheel = d.querySelector('[data-gear-a]');
  const pinion = d.querySelector('[data-gear-b]');
  const hero = d.querySelector('.hero');
  if (!wheel || !pinion || !hero) {
    return { error: 'the hero world is not in this document, so there is nothing ' +
                    'to drive: wheel=' + !!wheel + ' pinion=' + !!pinion + ' hero=' + !!hero };
  }
  const angle = (el) => {
    const m = /rotate\(([-0-9.]+)/.exec(el.getAttribute('transform') || '');
    return m ? parseFloat(m[1]) : 0;
  };
  // The position's own mapping, computed here rather than read, so the free
  // rotation is measured as the difference between what the wheel shows and what
  // the scroll alone owes it. Recomputed from live geometry because the framed
  // document's height is whatever the audit asked for.
  const heroBottom = hero.getBoundingClientRect().bottom + w.scrollY;
  const position = () => Math.round(Math.min(1, w.scrollY / heroBottom) * 80) / 10;
  const ratio = () => angle(pinion) / angle(wheel);
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  const pe = (type, x, y, extra) => new w.PointerEvent(type, Object.assign({
    pointerId: 7, pointerType: 'mouse', button: 0, buttons: 1,
    clientX: x, clientY: y, bubbles: true }, extra || {}));

  d.documentElement.style.scrollBehavior = 'auto';
  w.scrollTo({ top: 0, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(300);

  const out = { heroBottom: Math.round(heroBottom), viewport: w.innerWidth + 'x' + w.innerHeight };

  // 1 · the calm case a mouse wheel produces: one notch per event, 200ms apart.
  let before = angle(wheel), pos = position();
  for (let i = 0; i < 6; i++) { step(100); await wait(200); }
  await wait(600);
  out.notched = +(angle(wheel) - before - (position() - pos)).toFixed(3);

  // 2 · the teleport: a page-sized jump is not a gesture, whatever speed it implies.
  before = angle(wheel); pos = position();
  for (let i = 0; i < 3; i++) { step(700); await wait(400); }
  await wait(600);
  out.jumps = +(angle(wheel) - before - (position() - pos)).toFixed(3);

  // 3 · the sustained gesture: continued motion across many samples.
  before = angle(wheel);
  for (let i = 0; i < 12; i++) { step(60); await wait(16); }
  out.charged = +(angle(wheel) - before).toFixed(3);
  out.ratioAtRelease = +ratio().toFixed(4);
  out.wroteTransform = wheel.hasAttribute('transform');

  // 4 · the coast, and then the stop.
  const coastFrom = angle(wheel);
  await wait(1200);
  out.coasted = +(angle(wheel) - coastFrom).toFixed(3);
  out.ratioInCoast = +ratio().toFixed(4);
  await wait(1500);
  const settled = angle(wheel);
  await wait(600);
  out.settledDelta = +(angle(wheel) - settled).toFixed(3);

  // 5 · the hand. A drag around the pivot must turn the wheel and keep the mesh.
  const r = hero.getBoundingClientRect();
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  before = angle(wheel);
  hero.dispatchEvent(pe('pointerdown', cx + 220, cy));
  for (const dy of [30, 60, 90, 120]) {
    w.dispatchEvent(pe('pointermove', cx + 220, cy + dy));
    await wait(16);
  }
  out.handTurned = +(angle(wheel) - before).toFixed(3);
  out.ratioUnderHand = +ratio().toFixed(4);
  w.dispatchEvent(new w.PointerEvent('pointerup', { pointerId: 7, pointerType: 'mouse',
    clientX: cx + 220, clientY: cy + 120, bubbles: true }));
  await wait(700);

  // 6 · a control keeps its own pointer, and a touch is never taken.
  const control = d.querySelector('.hero .ask-chip') || d.querySelector('.hero .win');
  const cb = control.getBoundingClientRect();
  const hit = d.elementFromPoint(cb.left + cb.width / 2, cb.top + cb.height / 2) || control;
  hero.classList.remove('is-turning');
  hit.dispatchEvent(pe('pointerdown', cb.left + cb.width / 2, cb.top + cb.height / 2));
  await wait(40);
  out.controlTarget = hit.tagName.toLowerCase() + (hit.className ? '.' + String(hit.className).split(' ')[0] : '');
  out.controlStartsATurn = hero.classList.contains('is-turning');
  w.dispatchEvent(new w.PointerEvent('pointerup', { pointerId: 7, pointerType: 'mouse',
    clientX: cb.left, clientY: cb.top, bubbles: true }));

  hero.classList.remove('is-turning');
  hero.dispatchEvent(pe('pointerdown', cx + 220, cy, { pointerType: 'touch', pointerId: 9 }));
  await wait(40);
  out.touchStartsATurn = hero.classList.contains('is-turning');
  w.dispatchEvent(new w.PointerEvent('pointerup', { pointerId: 9, pointerType: 'touch',
    clientX: cx, clientY: cy, bubbles: true }));
  return out;
})(d, w)
"""

# The reduced-motion question is a different one, and a smaller one: not what the
# wheel does, but whether it is written at all. The world is nulled under reduce,
# so the honest assertion is that no gesture produces a transform.
REDUCED_SCENARIO = r"""
(async (d, w) => {
  const wheel = d.querySelector('[data-gear-a]');
  if (!wheel) return { reduced: w.matchMedia('(prefers-reduced-motion: reduce)').matches,
                       worldPresent: false, wroteTransform: false };
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  d.documentElement.style.scrollBehavior = 'auto';
  w.scrollTo({ top: 0, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(300);
  for (let i = 0; i < 12; i++) { step(60); await wait(16); }
  await wait(400);
  // And the hand, which is the other writer.
  const hero = d.querySelector('.hero');
  const r = hero.getBoundingClientRect();
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  hero.dispatchEvent(new w.PointerEvent('pointerdown', { pointerId: 5, pointerType: 'mouse',
    button: 0, buttons: 1, clientX: cx + 220, clientY: cy, bubbles: true }));
  w.dispatchEvent(new w.PointerEvent('pointermove', { pointerId: 5, pointerType: 'mouse',
    buttons: 1, clientX: cx + 220, clientY: cy + 140, bubbles: true }));
  await wait(200);
  return { reduced: w.matchMedia('(prefers-reduced-motion: reduce)').matches,
           worldPresent: true,
           wroteTransform: wheel.hasAttribute('transform'),
           scrolled: Math.round(w.scrollY) };
})(d, w)
"""


# THIS TOOL'S HARNESS IS NOT audit-contrast's, and the reason is a measurement
# rather than a preference. That one reads its answer out of the DOM with
# `--dump-dom`, which fires when the page loads, so it needs `--virtual-time-budget`
# to make the browser wait for a scenario at all. Under the virtual clock this
# renderer produces almost no animation frames - a probe that counted them saw FOUR
# in three seconds, in old headless and new, with and without every frame switch
# worth trying, and with a running CSS animation in the page to force invalidation -
# and the momentum is advanced by `requestAnimationFrame`. The wheel would receive
# its charge and never turn. Worse, a page that keeps requesting frames STALLS the
# virtual clock instead of finishing: two self-test runs sat for the full 420-second
# subprocess timeout rather than reporting anything, which is the least useful thing
# a gate can do.
#
# So the answer is DELIVERED rather than dumped. The harness posts the scenario's
# value back to this server and Chrome runs in REAL TIME, at a real frame rate, for
# as long as the scenario needs. The waits in the scenario are then the waits a
# reader's browser would make, which is what makes the coast and the settle
# assertable at all. The page is loaded in a sized iframe for the reason
# audit-contrast documents at length: `--window-size` gets clamped, and the page
# then resolves its media queries against a width nobody asked for.
HARNESS = """<!doctype html>
<html><head><meta charset="utf-8"><title>motion</title>
<style>html,body{{margin:0;padding:0}}iframe{{border:0;display:block}}</style>
</head><body>
<iframe id="f" width="{w}" height="{h}" src="{url}"></iframe>
<script>
function report(payload) {{
  document.title = payload.error ? 'ERROR' : 'DONE';
  try {{ fetch('/_result', {{method: 'POST', body: JSON.stringify(payload)}}); }}
  catch (e) {{}}
}}
var f = document.getElementById('f');
f.addEventListener('load', async function () {{
  try {{
    var d = f.contentDocument, w = f.contentWindow;
    if (!d || !d.body || !d.body.childElementCount) throw new Error('iframe is empty: ' + f.src);
    await new Promise(function (r) {{ setTimeout(r, {settle}); }});
    var fn = new Function('d', 'w', 'return (' + {expr} + ')');
    report({{ value: await fn(d, w) }});
  }} catch (e) {{ report({{ error: String((e && e.stack) || e) }}); }}
}});
/* A scenario that never returns, or a page that never loads, must end as a FINDING
   rather than as a wait for the timeout. */
setTimeout(function () {{ report({{ error: 'the scenario did not finish within 60s' }}); }},
           60000);
</script>
</body></html>
"""


class Rig:
    """The answer the harness posts back, shared with the server thread."""

    answer: dict | None = None

    @classmethod
    def post_result(cls, body: bytes) -> None:
        try:
            cls.answer = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            cls.answer = {"error": "the harness posted something unreadable: %s" % exc}


def make_handler(site: str, harness: str):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=site, **kw)

        def do_GET(self):
            if urllib.parse.urlsplit(self.path).path == "/_motion.html":
                body = open(harness, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            return super().do_GET()

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            Rig.post_result(self.rfile.read(n))
            self.send_response(204)
            self.end_headers()

        def log_message(self, *a):
            pass

    return Handler


def run(chrome, site, tmp, page, width, height, scenario, extra=None, tag="motion",
        timeout=180):
    """Drive one page with one scenario, in real time, and wait for its answer."""
    profile = os.path.join(tmp, "profile-" + tag)
    harness = os.path.join(tmp, "harness-%s.html" % tag)
    AC.write(harness, HARNESS.format(w=width, h=height, url=page,
                                     expr=json.dumps(scenario), settle=700))
    Rig.answer = None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(site, harness))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    cmd = [chrome, "--headless", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--hide-scrollbars",
           "--user-data-dir=" + profile] + list(extra or []) + [base + "/_motion.html"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")
    deadline = time.time() + timeout
    try:
        while time.time() < deadline and Rig.answer is None:
            time.sleep(0.1)
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
        srv.shutdown()
    if Rig.answer is None:
        return {"error": "no answer in %ds; the browser was killed. A page that keeps "
                         "requesting animation frames can hold a headless renderer "
                         "open, so this is reported rather than waited on forever" % timeout}
    doc = Rig.answer
    if "error" in doc:
        return doc
    # An absent answer is its own finding rather than a pass: a scenario that never
    # calls itself evaluates to a function, `JSON.stringify` drops it, and the run
    # then looks exactly like a page that behaved. That was this tool's first bug.
    if doc.get("value") is None:
        return {"error": "the scenario returned nothing (it must end by calling itself "
                         "with (d, w)); the harness reports success either way"}
    return doc["value"]


RATIO = 223 / 48          # the drawing's own count, mirrored in the script
DRIFT_MAX = 0.15          # one rounding step of the writer, which is 0.1 degrees
SETTLE_MAX = 0.1          # the last write the momentum is allowed to make


# Counted, so the verdict line can say how much was asserted rather than how
# confident it sounds. A claim that is not counted is a claim that can be deleted
# without the total moving, which is what the count is for.
CHECKED = [0]


def check(doc: dict, failures: list) -> None:
    """The behaviour, asserted. Every line names the reader-visible claim it holds."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the scenario ran", False, doc["error"])
        return
    v = doc

    for key, label in (("notched", "a notched read leaves the wheel where the scroll put it"),
                       ("jumps", "a page-sized jump is not a gesture")):
        ok(label, abs(v[key]) <= DRIFT_MAX,
           "%.3f degrees of free rotation (the writer rounds to %.1f)" % (v[key], SETTLE_MAX))

    # The two claims that CAN be asserted about the gesture are the decision and the
    # arithmetic: that a sustained flick reaches the wheel at all, where a notched
    # read and a page-sized jump leave it untouched, and that the pinion is the
    # wheel's own ratio. The coast and the settle are integration rather than
    # decision, and they need frames - see the note printed below the claims.
    ok("a sustained flick reaches the wheel", v["charged"] >= 2,
       "%.2f degrees of free rotation from the gesture, against %.3f from a notched "
       "read" % (v["charged"], abs(v["notched"])))
    ok("the mesh ratio holds at the moment of release",
       abs(abs(v["ratioAtRelease"]) - RATIO) < 0.001,
       "pinion/wheel = %.4f, and 223/48 = %.4f" % (v["ratioAtRelease"], RATIO))
    ok("the wheel coasts after the gesture ends", v["coasted"] >= 3,
       "%.2f degrees after the reader stopped, on top of the %.2f already charged"
       % (v["coasted"], v["charged"]))
    ok("the mesh ratio holds through the coast",
       abs(abs(v["ratioInCoast"]) - RATIO) < 0.001,
       "pinion/wheel = %.4f" % v["ratioInCoast"])
    ok("and then it stops", abs(v["settledDelta"]) <= SETTLE_MAX,
       "%.2f degrees in the 600ms after the coast was given 1.5s to finish"
       % v["settledDelta"])

    ok("the hand turns the wheel", abs(v["handTurned"]) >= 0.5,
       "%.2f degrees from a 120px drag" % v["handTurned"])
    ok("the mesh ratio holds under the hand",
       abs(abs(v["ratioUnderHand"]) - RATIO) < 0.001,
       "pinion/wheel = %.4f" % v["ratioUnderHand"])

    ok("a control keeps its own pointer", not v["controlStartsATurn"],
       "the pointer was over %s" % v["controlTarget"])
    ok("a touch is never taken", not v["touchStartsATurn"],
       "a touch drag is the reader scrolling")



def check_reduced(doc: dict, failures: list) -> None:
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the reduced-motion scenario ran", False, doc["error"])
        return
    if not doc.get("reduced"):
        # A run that did not get the state it asked for is an error, not a pass.
        ok("the browser reported reduced motion", False,
           "the forced switch did not take, so nothing here was measured")
        return
    ok("in the reduced world nothing is written",
       not doc.get("wroteTransform"),
       "after a flick and a drag, and the page still scrolled %s px" % doc.get("scrolled"))


# Each of these makes the page wrong in one way that the behaviour claims to catch,
# and `--self-test` insists the audit reports exactly that. A gate whose failures
# were never seen is a gate nobody can trust; this is the copy of that rule the
# build-time tools already keep.
SELF_TESTS = [
    # The bug the first window version actually shipped: a window that holds a
    # sample old enough to belong to a different gesture, so a teleport reads as
    # continued motion. 1.2s of history is what does it - long enough to contain a
    # whole page-sized jump, short enough to still look like a gesture.
    ("the window holds a stale sample, so a teleport counts as motion",
     [("> 150) fly.shift();", "> 1200) fly.shift();")],
     "a page-sized jump is not a gesture"),
    ("the flywheel's charge silenced across the board",
     [("Math.min(SPIN_CAP, surge * 22)", "Math.min(SPIN_CAP, surge * 0)")],
     "a sustained flick reaches the wheel"),
    ("the touch guard dropped",
     [("if (e.pointerType === 'touch' || e.button) return;", "if (e.button) return;")],
     "a touch is never taken"),
    # The scenario drives the chips, which are buttons, so this patch removes the
    # exclusions down to links: a narrower one that left `button` in place would be a
    # patch of nothing, which the self-test reported as "nothing failed" the first
    # time it was written.
    ("the world's controls no longer keep their own pointer",
     [("!target.closest('a, button, .win, p, h1, li')", "!target.closest('a')")],
     "a control keeps its own pointer"),
    ("the reduced-motion world built anyway",
     [("var world = reduced ? null : document.querySelector('.hero-world');",
       "var world = document.querySelector('.hero-world');")],
     "in the reduced world nothing is written"),
]


def self_test(chrome, site, width, height, tmp) -> int:
    print("self-test: four doctored pages, each of which must fail one named claim")
    worst = 0
    for i, (what, edits, expected) in enumerate(SELF_TESTS):
        broken = os.path.join(tmp, "broken-%d" % i)
        if os.path.isdir(broken):
            shutil.rmtree(broken)
        shutil.copytree(site, broken)
        page = os.path.join(broken, "index.html")
        html = open(page, encoding="utf-8").read()
        missing = [old for old, _ in edits if old not in html]
        if missing:
            print("  FAIL  %s: the text it patches is not in the built page (%r), so the "
                  "self-test is checking nothing" % (what, missing[0]))
            worst = 1
            continue
        for old, new in edits:
            html = html.replace(old, new, 1)
        AC.write(page, html)

        failures: list = []
        doc = run(chrome, broken, tmp, "/", width, height, SCENARIO,
                  extra=None, tag="st%d" % i)
        check(doc, failures)
        reduced_failures: list = []
        rdoc = run(chrome, broken, tmp, "/", width, height, REDUCED_SCENARIO,
                   extra=["--force-prefers-reduced-motion"], tag="st%d-reduced" % i)
        check_reduced(rdoc, reduced_failures)
        named = expected in failures or expected in reduced_failures
        print("  %s  %s -> %s" % ("ok  " if named else "FAIL", what,
                                  (", ".join(failures + reduced_failures) or "nothing failed")))
        if not named:
            worst = 1
    if worst == 0:
        print("self-test ok - every doctored page is caught by the claim it breaks")
    return worst


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--json", default="")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.site):
        print("error: %s is not a directory - run build-site.py first" % a.site,
              file=sys.stderr)
        return 1
    chrome = AC.find_chrome()
    tmp = tempfile.mkdtemp(prefix="istor-motion-")
    try:
        if a.self_test:
            return self_test(chrome, a.site, a.width, a.height, tmp)

        print("the mechanism, driven: %s at %dpx" % (a.site, a.width))
        failures: list = []
        doc = run(chrome, a.site, tmp, "/", a.width, a.height, SCENARIO)
        check(doc, failures)
        rdoc = run(chrome, a.site, tmp, "/", a.width, a.height, REDUCED_SCENARIO,
                   extra=["--force-prefers-reduced-motion"], tag="reduced")
        check_reduced(rdoc, failures)

        if a.json:
            with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"motion": doc, "reduced": rdoc, "failures": failures}, fh, indent=1)
            print("\nfindings written to %s" % a.json)

        print()
        if failures:
            print("FAILED - %d of %d claims are not true of the page:\n  %s"
                  % (len(failures), CHECKED[0], "\n  ".join(failures)))
            return 1
        band = "%dpx" % doc["heroBottom"] if isinstance(doc.get("heroBottom"), int) else "not measured"
        print("motion ok - %d claims about the two worlds, verified by driving the page "
              "rather than by reading it (hero band %s of %s)"
              % (CHECKED[0], band, doc.get("viewport", "?")))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
