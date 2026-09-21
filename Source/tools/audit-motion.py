#!/usr/bin/env python3
"""Drive the mechanism and check what it does, which no other gate can see.

    python Source/tools/audit-motion.py
    python Source/tools/audit-motion.py --self-test
    python Source/tools/audit-motion.py --self-test --family lib
    python Source/tools/audit-motion.py --json findings.json

The self-test doctors fifteen pages in three families - the landing's world and
reduced claims, the arrivals' pacing pair, and the library's fold test and clock -
and `--family` runs one of them. The flag exists because the whole set takes a
quarter of an hour once each patch has to be driven on the page that can catch it,
and a self-test that long stops being run; a family is between forty and eighty
seconds. A patch pays for one page load per browser it needs and no others: a world
claim is not evidence about the reduced page, and the library's claims are about a
different document entirely.

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
claim thirteen things where the first draft could honestly claim nine, and a session
probe has since handed it a fourteenth reason to exist (see the boundary in the
scenario): a claim list is only worth what the next measurement adds to it. Eighteen
when the arrivals' clock (M20) joined it and twenty-four when the library's own
arrivals did (M21), because behaviour that is not asserted is behaviour that quietly
stops working - and the library is a different page on different files, where none of
the landing's claims would move if its fold test or its pace sample disappeared.

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

  // Every claim below is measured from the world's own ground, and that is not
  // tidiness: the page only charges the wheel where the world is on screen (see
  // 4b), so a gesture driven at a scroll position left over from the previous step
  // would report zero for a reason that has nothing to do with the claim. The probe
  // made exactly that mistake before the boundary existed, and the boundary is what
  // exposed it: steps 1 to 3 all ran at scrollY ~2700 on a 1975px hero.
  const home = async () => {
    w.scrollTo({ top: 0, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
    await wait(400);
  };

  // 1 · the calm case a mouse wheel produces: one notch per event, 200ms apart.
  await home();
  let before = angle(wheel), pos = position();
  for (let i = 0; i < 6; i++) { step(100); await wait(200); }
  await wait(600);
  out.notched = +(angle(wheel) - before - (position() - pos)).toFixed(3);

  // 2 · the teleport: a page-sized jump is not a gesture, whatever speed it implies.
  await home();
  before = angle(wheel); pos = position();
  for (let i = 0; i < 3; i++) { step(700); await wait(400); }
  await wait(600);
  out.jumps = +(angle(wheel) - before - (position() - pos)).toFixed(3);

  // 3 · the sustained gesture: continued motion across many samples. This is free
  // rotation too, and it has to be: the gesture also moves the reader 720px down
  // the hero, which the position's own mapping is entitled to turn the wheel for.
  // Measuring the raw delta would credit the flywheel for M14's work and would let
  // a page whose charge had been silenced pass on the position's 2.9 degrees.
  await home();
  before = angle(wheel); pos = position();
  for (let i = 0; i < 12; i++) { step(60); await wait(16); }
  out.charged = +(angle(wheel) - before - (position() - pos)).toFixed(3);
  out.gestureEnd = Math.round(w.scrollY);
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

  // 4b · the boundary. The SAME sustained gesture, made where no world is on
  // screen, must not charge the wheel. This is the clause that closes a measured
  // bug rather than a hypothetical one: with no boundary a 24-gesture scroll down
  // the page left the wheel 484 degrees from where its own scroll position says it
  // is, which is invisible rotation that stops the angle meaning the reader's
  // position. `position()` is clamped to 1 past the hero, so below it the free
  // rotation is the whole measurement.
  w.scrollTo({ top: heroBottom + w.innerHeight * 2, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(400);
  out.belowHero = Math.round(w.scrollY);
  pos = position(); before = angle(wheel);
  for (let i = 0; i < 12; i++) { step(60); await wait(16); }
  await wait(900);
  out.belowHeroCharged = +(angle(wheel) - before - (position() - pos)).toFixed(3);

  // Back to the world: the hand and the controls below are on the hero, and a
  // probe that leaves it scrolled away measures elementFromPoint instead of the
  // page's guards.
  await home();

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
# M22 asks the question every other scenario ignores: what the machine does
# when the reader does NOTHING. The wheel's stillness ticks are on setTimeout
# chains, which virtual time would burn through in an instant, so this too is
# driven in real time - about 28s of scenario, mostly waiting, which is the
# honest cost of measuring patience.
DWELL_SCENARIO = r"""
(async (d, w) => {
  const wheel = d.querySelector('[data-gear-a]');
  const pinion = d.querySelector('[data-gear-b]');
  const hero = d.querySelector('.hero');
  if (!wheel || !pinion || !hero) {
    return { error: 'the dwell scenario needs the hero world: wheel=' + !!wheel +
                    ' pinion=' + !!pinion + ' hero=' + !!hero };
  }
  const angle = (el) => {
    const m = /rotate\(([-0-9.]+)/.exec(el.getAttribute('transform') || '');
    return m ? parseFloat(m[1]) : 0;
  };
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  const pe = (type, x, y) => new w.PointerEvent(type, {
    pointerId: 7, pointerType: 'mouse', button: 0, buttons: 1,
    clientX: x, clientY: y, bubbles: true });
  d.documentElement.style.scrollBehavior = 'auto';
  w.scrollTo({ top: 0, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  const t0 = performance.now();
  // Every WHEEL change, with its time and the pinion's answer at that moment.
  // The poll is SEEDED with the angle it starts at, so the page's initial
  // rotate(0) write - which happens at load, before this scenario begins - is
  // not a mark: the marks are the machine's CHANGES, not its existence.
  const marks = [];
  let lastA = angle(wheel);
  const poll = setInterval(() => {
    const a = angle(wheel);
    if (a !== lastA) {
      lastA = a;
      marks.push({ a, pa: angle(pinion), t: Math.round(performance.now() - t0) });
    }
  }, 40);
  // Headless Chrome is BORN hidden, and the reader's tab is not: the guard
  // the page keeps (a hidden tab holds the tick) would otherwise make every
  // claim here unmeasurable in the one browser this audit runs in. The
  // scenario states what it does - the reader is present until Phase D says
  // otherwise - and Phase D is where the guard itself is measured. The shadow
  // lands on `d`, the iframe's own document, because that is the one the
  // page's guard reads; the top page's `document` is the harness's.
  Object.defineProperty(d, 'hidden', { get: () => false, configurable: true });

  // Phase A - stillness. Three teeth are owed; a fourth (at ~12s) would be a
  // clock that never rests, and the 13.4s window exists to see one if it comes.
  await wait(13400);
  const phaseA = marks.length;

  // Phase B - a scroll re-arms the clock, RESTARTED: the next tooth must wait
  // the full first interval again. This is also where the interlock with the
  // momentum claims above is measured exactly: the scroll instant is ours, so
  // the first tooth after it is the page's own DWELL_FIRST to the millisecond.
  const bScroll = performance.now();
  step(100);
  await wait(4800);
  const bStart = Math.round(bScroll - t0);
  // The scroll's own M14 write lands within ~50ms of the event and is the
  // position's echo, not the clock's work, so the window opens 500ms in.
  const sinceB = marks.filter((m) => m.t >= bStart + 500);
  const bFirst = sinceB.length ? sinceB[0].t - bStart : null;
  // The clock's work is what the window saw, not what the scroll echoed:
  // counting every mark after Phase A would credit the scroll's own M14
  // write, which the 500ms filter exists to exclude, as a tick.
  const newB = sinceB.length;

  // Phase C - the hand holds. A grip is not stillness; and there is a live
  // timer in flight here (Phase B's tick scheduled its successor at +2.6s,
  // which lands inside this hold), so what blocks it is the pointerdown's
  // dwellStop, not the absence of a timer.
  const r = hero.getBoundingClientRect();
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  hero.dispatchEvent(pe('pointerdown', cx + 220, cy));
  w.dispatchEvent(pe('pointermove', cx + 220, cy + 60));
  await wait(16);
  const beforeC = angle(wheel);
  await wait(4600);
  const duringC = +(angle(wheel) - beforeC).toFixed(3);
  w.dispatchEvent(new w.PointerEvent('pointerup', { pointerId: 7, pointerType: 'mouse',
    clientX: cx + 220, clientY: cy + 60, bubbles: true }));

  // Phase D - a hidden tab. The pointerup re-armed the clock, so a tooth is
  // due at +4.2s - but the release also left the wheel coasting, and the
  // coast is the hand's momentum rather than the clock: it decays for about
  // 2.5s and would contaminate any count that opened at the release. The
  // window therefore opens once the coast has died, and a tooth is still
  // due inside it, so the visibility guard is the only thing that can hold
  // it. (`hidden` is an accessor on Document.prototype rather than an own
  // property of the instance, so it is shadowed on the instance, and the
  // shadow is deleted afterwards.)
  Object.defineProperty(d, 'hidden', { get: () => true, configurable: true });
  // The window opens on DEMONSTRATED stillness rather than on a guess about
  // the coast: the release flung the wheel with the hand's capped velocity,
  // and its decay length is the momentum constants' to decide, not this
  // scenario's. 1500ms with no mark at all means the rAF loop has stopped -
  // the coast's own threshold - so everything the window sees from here is
  // the clock's, or nothing is. Capped at 8s so a pathological coast cannot
  // stall the audit.
  const dStart = performance.now();
  let stillFor = 0, lastCount = marks.length;
  while (stillFor < 1500 && performance.now() - dStart < 8000) {
    await wait(100);
    if (marks.length === lastCount) stillFor += 100;
    else { stillFor = 0; lastCount = marks.length; }
  }
  const lenD0 = marks.length;
  await wait(4800);
  const ticksD = marks.length - lenD0;
  delete d.hidden;   // the prototype's accessor again
  clearInterval(poll);
  return {
    phaseA, newB, bFirst, duringC, ticksD,
    firstTooth: marks.length ? marks[0].a : null,
    firstPinion: marks.length ? marks[0].pa : null,
    finalRatio: angle(wheel) ? +(angle(pinion) / angle(wheel)).toFixed(4) : null,
    marks: marks.slice(0, 8)
  };
})(d, w)
"""


DWELL_CLAIMS = [
    "stillness steps the wheel one tooth at a time",
    "the pinion answers the tick through the mesh",
    "three teeth, then the mechanism rests",
    "a scroll re-arms the clock, restarted and past the settle window",
    "the hand defers the clock",
    "a hidden tab holds the tick",
]


def check_dwell(doc: dict, failures: list) -> None:
    """M22's behaviour, asserted. The tooth is 360/223 and the interlock is
    3.3s: both are held here against the page, not against a note."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the dwell scenario ran", False, doc["error"])
        return
    tooth = 360 / 223
    ok("stillness steps the wheel one tooth at a time",
       doc.get("firstTooth") is not None
       and abs(abs(doc["firstTooth"]) - tooth) <= 0.11,
       "%.2f degrees at the first mark, and 360/223 = %.3f (the writer rounds "
       "to a tenth)" % (doc.get("firstTooth") or 0, tooth))
    pa = doc.get("firstPinion") or 0
    fa = doc.get("firstTooth") or 0
    ok("the pinion answers the tick through the mesh",
       abs(abs(pa) - abs(fa) * RATIO) <= 0.15
       and doc.get("finalRatio") is not None
       and abs(abs(doc["finalRatio"]) - RATIO) <= 0.06,
       "pinion stepped %.2f against %.2f owed, end ratio %.4f against %.4f"
       % (abs(pa), abs(fa * RATIO), abs(doc.get("finalRatio") or 0), RATIO))
    ok("three teeth, then the mechanism rests", doc.get("phaseA") == 3,
       "%d wheel marks in the 13.4s stillness window (marks: %s)"
       % (doc.get("phaseA") or 0, doc.get("marks")))
    ok("a scroll re-arms the clock, restarted and past the settle window",
       doc.get("newB") == 1 and doc.get("bFirst") is not None
       and 3800 <= doc["bFirst"] <= 5200,
       "%d tick(s) after the scroll, the first %s ms after it - the momentum "
       "audit's windows end at 3300, which is why the clock waits 4200"
       % (doc.get("newB") or 0, doc.get("bFirst")))
    dc = doc.get("duringC")
    ok("the hand defers the clock", dc is not None and abs(dc) <= DRIFT_MAX,
       "%.3f degrees during a 4.6s hold, with a live timer in flight - zero "
       "is the success this claim describes, so a falsy-or fallback would "
       "read it as missing" % (0.0 if dc is None else dc))
    ok("a hidden tab holds the tick", doc.get("ticksD") == 0,
       "%d tick(s) while the tab was hidden and a tooth was due"
       % (doc.get("ticksD") or 0))



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
       "read (the gesture ended %spx down, inside the %spx hero)"
       % (v["charged"], abs(v["notched"]), v["gestureEnd"], v["heroBottom"]))
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

    ok("a flick below the hero does not charge the wheel",
       v["belowHero"] > v["heroBottom"] + 400 and abs(v["belowHeroCharged"]) <= DRIFT_MAX,
       "%dpx down, %.3f degrees of free rotation from the same gesture that charges "
       "%.1f at the hero" % (v["belowHero"], v["belowHeroCharged"], v["charged"]))

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


# M20 asks a different question again, and it needs two page loads because a reveal
# fires once and a block is unobserved afterwards: the SAME block is approached
# slowly in one load and fast in the other, and the two are compared. The block is
# the reading log's, which has the longest authored chain anywhere in the family
# (four rows, four ticks and a counter), so a clock change cannot hide in it.
#
# What is measured is deliberately split between behaviour and computed style. The
# behaviour - does the same content arrive either way, and does the counter keep the
# rows' clock - is driven and observed. The ORDER claim is read off computed
# delays instead, because order is what multiplication cannot change and asserting
# it by watching a 2s sequence race would be a test of the machine's frame rate
# rather than of the page. The static half of that claim (every timing in the
# family, including the plate's scribe, is written against the same property) is
# verify-links.py's job, where it costs nothing to check.
PACE_SCENARIO = r"""
(async (d, w) => {
  const WIN = d.querySelector('.win-readlog');
  if (!WIN) return { error: 'no reading-log block in this document' };
  const block = WIN.closest('.reveal') || WIN;
  const rows = Array.from(WIN.querySelectorAll('.readlog li'));
  const ticks = Array.from(WIN.querySelectorAll('.readlog-tick'));
  const count = WIN.querySelector('.win-count');
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  d.documentElement.style.scrollBehavior = 'auto';

  // Park it just below the fold and let the sample window go quiet, so the
  // approach below is the only motion in the measurement.
  const top = block.getBoundingClientRect().top + w.scrollY;
  w.scrollTo({ top: top - w.innerHeight - 40, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(900);

  const authored = count ? count.textContent.trim() : null;
  const t0 = performance.now();
  const countChanges = [];
  let seen = authored;
  const poll = setInterval(function () {
    if (!count) return;
    const now = count.textContent.trim();
    if (now !== seen) {
      seen = now;
      countChanges.push(Math.round(performance.now() - t0));
    }
  }, 10);

  __APPROACH__
  await wait(2400);
  clearInterval(poll);

  const cs = getComputedStyle(block);
  const row1 = getComputedStyle(rows[0]);
  const out = {
    quick: block.classList.contains('is-quick'),
    stillCold: block.classList.contains('is-cold'),
    arrive: cs.getPropertyValue('--arrive').trim(),
    rowDurationMs: row1.transitionDuration,
    rowDelaysMs: rows.map((r) => getComputedStyle(r).transitionDelay),
    countChangesMs: countChanges,
    authoredCount: authored,
    count: count ? count.textContent.trim() : null,
    rowsOpacity: rows.map((r) => getComputedStyle(r).opacity).join(','),
    ticksOpacity: ticks.map((t) => getComputedStyle(t).opacity).join(','),
    rowsDelayApplied: rows.map((r) => r.style.transitionDelay).join(','),
    approach: '__HOW__'
  };
  return out;
})(d, w)
"""

PACE_CALM = PACE_SCENARIO.replace("__HOW__", "slow").replace(
    "__APPROACH__", "for (let i = 0; i < 16; i++) { step(60); await wait(80); }")
PACE_FAST = PACE_SCENARIO.replace("__HOW__", "fast").replace(
    "__APPROACH__", "for (let i = 0; i < 12; i++) { step(220); await wait(16); }")


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
    # The boundary the session probe earned: without it the wheel is charged from
    # anywhere on the page, and the rotation it accumulates below the hero is
    # invisible and unexplainable when the reader scrolls back up to it.
    ("the flywheel charged below the hero as well",
     [("active !== heroTurnable && window.scrollY < heroBottom",
       "active !== heroTurnable")],
     "a flick below the hero does not charge the wheel"),
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
    # M20's four, each the failure of one of the pacing claims. The first is the
    # bug this feature actually shipped for one build: px per millisecond divided
    # by 1000 as if it were px per second, so the inequality was never true and
    # the whole thing was dead code that looked alive.
    ("the pacing test divided by 1000, so it can never fire",
     [("pace * ARRIVE_MS > window.innerHeight",
       "pace * ARRIVE_MS / 1000 > window.innerHeight")],
     "a fast arrival gets the arrival's own clock"),
    ("the quick clock declared but not applied",
     [("--arrive: 0.3", "--arrive: 1")],
     "a fast arrival gets the arrival's own clock"),
    ("the counter left on a clock of its own",
     [("steps[s] * scale", "steps[s]")],
     "the counter keeps the rows' clock"),
    ("the fast path dropping the chain's last step",
     [("for (var s = 0; s < steps.length; s++)",
       "for (var s = 0; s < steps.length - (quick ? 1 : 0); s++)")],
     "the same content arrives either way"),
    # M21's five, each the failure of one of the library's claims. The patches name
    # their own file and URL, because these live in the SHARED `/theme.js` and
    # `/styles.css` that every library document loads rather than in the landing's
    # inlined pair - so a patch here is a patch of what the library actually runs.
    #
    # The second is worth naming: the landing's pacing shipped for one build with
    # `px per millisecond` divided by 1000 as if it were `px per second`, and the
    # library's copy of the same inequality could repeat that bug without any landing
    # claim moving, which is precisely why the library needs its own claims.
    ("the library marked every block cold, including the one being read",
     [("if (el.getBoundingClientRect().top < window.innerHeight) continue;", "")],
     "the library hides only what is below the fold", ("theme.js", "/library/")),
    ("the library's pacing test divided by 1000, so it can never fire",
     [("pace * ARRIVE_MS > window.innerHeight) {",
       "pace * ARRIVE_MS / 1000 > window.innerHeight) {")],
     "a fast arrival gets the library's own clock", ("theme.js", "/library/")),
    ("the library's quick clock declared but not applied",
     [(".reveal.is-quick { --arrive: 0.3; }", ".reveal.is-quick { --arrive: 1; }")],
     "a fast arrival gets the library's own clock", ("styles.css", "/library/")),
    # The class and the rule are two copies of one fact, so the interesting failure is
    # the class arriving on a block the stylesheet no longer hides: everything looks
    # correct in the markup and the page simply never shows an arrival.
    ("the library's hidden state dropped, so a waiting block is visible",
     [(".reveal.is-cold { opacity: 0; transform: translateY(14px); }",
       ".reveal.is-cold { transform: translateY(14px); }")],
     "a block that waits is hidden while it waits", ("styles.css", "/library/")),
    ("the library marked and observed a page with motion reduced",
     [("if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: "
       "reduce)').matches) return;", "")],
     "in the reduced world the library marks nothing", ("theme.js", "/library/")),
    # M22's five, each the failure of one of the dwell's claims. The clock is
    # three constants, a guard and two call sites; each patch removes exactly
    # one of the things a reader can catch.
    ("the dwell's tooth stopped being the drawing's pitch",
     [("var DWELL_TOOTH = 360 / 223;", "var DWELL_TOOTH = 360 / 48;")],
     "stillness steps the wheel one tooth at a time"),
    ("the dwell never rested",
     [("DWELL_TICKS = 3;", "DWELL_TICKS = 99;")],
     "three teeth, then the mechanism rests"),
    ("a scroll no longer re-armed the dwell clock",
     [('dwellArm();\n      if (paintPoster) paintPoster();',
       'if (paintPoster) paintPoster();')],
     "a scroll re-arms the clock, restarted and past the settle window"),
    ("a grip stopped deferring the dwell clock",
     [('stopSpin(t);\n        dwellStop();   // M22 · a grip is not stillness; the clock defers',
       "stopSpin(t);"),
      ("heroTurnable && !active && !document.hidden",
       "heroTurnable && !document.hidden")],
     "the hand defers the clock"),
    ("the dwell ticked to a hidden tab",
     [("heroTurnable && !active && !document.hidden",
       "heroTurnable && !active")],
     "a hidden tab holds the tick"),
]

# The claims that need the pacing pair of page loads, so the self-test knows which
# patches have to pay for them.
PACE_CLAIMS = ("a slow arrival gets the authored clock",
               "a fast arrival gets the arrival's own clock",
               "the delays scale with the durations, so the order cannot move",
               "the same content arrives either way",
               "the counter keeps the rows' clock")


def check_pace(calm: dict, fast: dict, failures: list) -> None:
    """The arrival's clock, and the one thing pacing must never touch."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    for name, doc in (("slow", calm), ("fast", fast)):
        if "error" in doc:
            ok("the %s approach ran" % name, False, doc["error"])
            return

    # The decision itself, on both sides of it. The slow path is not decoration:
    # without it, a page that always arrived at speed would pass the fast claim.
    ok("a slow arrival gets the authored clock",
       not calm["quick"] and calm["arrive"] == "1",
       "--arrive = %s after a %s approach" % (calm["arrive"], calm["approach"]))
    ok("a fast arrival gets the arrival's own clock",
       fast["quick"] and fast["arrive"] != "1",
       "--arrive = %s after a %s approach" % (fast["arrive"], fast["approach"]))

    # The clock is one number multiplied through the family, so a delay cannot
    # scale without the durations scaling with it, and the ORDER of the delays
    # cannot move: multiplication is monotonic. Both halves are checked, because
    # a stylesheet that scaled the durations and left the delays authored would
    # keep every row arriving 140ms apart inside a 144ms transition.
    try:
        factor = float(fast["arrive"]) / float(calm["arrive"])
    except (TypeError, ValueError, ZeroDivisionError):
        factor = 0
    # A computed timing carries one value per transitioned property ("0s, 0s" for
    # opacity and transform), so only the first of each is read: they are written
    # from one expression here, and a rule that gave them different delays would be
    # a different claim than this one.
    def first_time(v):
        return float(v.split(",")[0].strip().rstrip("s"))

    calm_d = [first_time(v) for v in calm["rowDelaysMs"]]
    fast_d = [first_time(v) for v in fast["rowDelaysMs"]]
    scaled = factor > 0 and all(abs(c * factor - f) < 0.001 for f, c in zip(fast_d, calm_d))
    ordered = all(b > a for a, b in zip(calm_d, calm_d[1:])) if len(calm_d) > 1 else False
    ok("the delays scale with the durations, so the order cannot move",
       scaled and ordered and factor < 1,
       "factor %.2f, delays %s -> %s, still increasing"
       % (factor, [round(v * 1000) for v in calm_d], [round(v * 1000) for v in fast_d]))

    # The claim the whole feature has to earn: the CLOCK moved, nothing else did.
    same = (calm["count"] == fast["count"] and calm["rowsOpacity"] == fast["rowsOpacity"]
            and calm["ticksOpacity"] == fast["ticksOpacity"]
            and calm["stillCold"] is False and fast["stillCold"] is False)
    ok("the same content arrives either way",
       same,
       "count %r vs %r, rows %s vs %s, ticks %s vs %s"
       % (calm["count"], fast["count"], calm["rowsOpacity"], fast["rowsOpacity"],
          calm["ticksOpacity"], fast["ticksOpacity"]))

    # And the counter is on the same clock rather than one of its own, which is the
    # failure a second copy of the constant would produce: rows that land on time
    # with a count that does not.
    # The counter's own gaps, not its offset: the moment its chain starts depends on
    # when the browser delivered the intersection, which is the instrument's timing
    # rather than the page's, while the SPACING between its four writes is the
    # clock's and nothing else's.
    def gaps(doc):
        ts = doc.get("countChangesMs") or []
        return [b - a for a, b in zip(ts, ts[1:])]

    cg, fg = gaps(calm), gaps(fast)
    gap_ok = (len(cg) >= 3 and len(fg) == len(cg)
              and sum(fg) / 3.0 < sum(cg) / 3.0 * 0.6)
    ok("the counter keeps the rows' clock",
       gap_ok,
       "its %d writes came %s ms apart when slow and %s ms apart when fast (scale %.2f)"
       % (len(cg) + 1, cg, fg, factor))


# M21 is the library's arrivals, and this is a different question rather than a
# second run of M20. The library is a set of documents sharing one stylesheet and one
# script (`/styles.css` and `/theme.js`) while the landing inlines both, so what has to
# hold here is three facts a shared file makes easy to lose: the fold test decides what
# gets hidden, the reader's pace picks the clock, and a reader who asked for less
# motion gets a page that was never marked at all.
#
# The library index is the page used, because its seven blocks come from a generator
# rather than from hand-authored markup, and the block measured is the first one that
# was COLD AT LOAD - found rather than fixed, so the run does not depend on which group
# happens to sit below the fold at the width it is given. It is also required to be
# taller than one fast step: a block shorter than a step can be entered and left
# between two frames, which would make the fast claim a measurement of this machine's
# frame rate instead of the page's behaviour.
LIB_SCENARIO = r"""
(async (d, w) => {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const groups = Array.from(d.querySelectorAll('.reveal'));
  if (!groups.length) return { error: 'no .reveal blocks on this page' };
  const at = groups.map((el) => {
    const r = el.getBoundingClientRect();
    return { top: Math.round(r.top), h: Math.round(r.height),
             cold: el.classList.contains('is-cold') };
  });
  const target = groups.find((el) => el.classList.contains('is-cold'));
  if (!target) return { error: 'nothing was cold at load, so this run would measure nothing' };
  if (target.getBoundingClientRect().height < 260)
    return { error: 'the block below the fold is shorter than one fast step, so the ' +
                    'fast approach could pass it without a frame in between' };
  d.documentElement.style.scrollBehavior = 'auto';
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  const top = target.getBoundingClientRect().top + w.scrollY;
  w.scrollTo({ top: top - w.innerHeight - 40, behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(900);
  const p = getComputedStyle(target);
  const parked = { cold: target.classList.contains('is-cold'), opacity: p.opacity,
                   transform: p.transform, duration: p.transitionDuration,
                   arrive: p.getPropertyValue('--arrive').trim() };
  const items = Array.from(target.querySelectorAll('li'));
  const atRest = items.slice(0, 3).map((l) => getComputedStyle(l).opacity).join(',');
  __APPROACH__
  await wait(1400);
  const cs = getComputedStyle(target);
  return {
    approach: '__HOW__', vh: w.innerHeight, groups: at, parked: parked,
    quick: target.classList.contains('is-quick'),
    stillCold: target.classList.contains('is-cold'),
    arrive: cs.getPropertyValue('--arrive').trim(),
    duration: cs.transitionDuration, opacity: cs.opacity, transform: cs.transform,
    items: items.length,
    itemsOpacity: items.slice(0, 3).map((l) => getComputedStyle(l).opacity).join(','),
    itemOpacityAtRest: atRest,
    y: Math.round(w.scrollY)
  };
})(d, w)
"""

LIB_CALM = LIB_SCENARIO.replace("__HOW__", "slow").replace(
    "__APPROACH__", "for (let i = 0; i < 16; i++) { step(60); await wait(80); }")
LIB_FAST = LIB_SCENARIO.replace("__HOW__", "fast").replace(
    "__APPROACH__", "for (let i = 0; i < 12; i++) { step(220); await wait(16); }")

# The reduced-motion question, asked of the library's own blocks. There is no gesture
# to drive here: the claim is that the script's guard returns before anything is
# marked, so the authored page is the finished page and the reader who asked for less
# motion is never shown a page with pieces of it missing.
LIB_REDUCED_SCENARIO = r"""
(async (d, w) => {
  const groups = Array.from(d.querySelectorAll('.reveal'));
  if (!groups.length) return { error: 'no .reveal blocks on this page' };
  const ops = groups.map((el) => getComputedStyle(el).opacity);
  return {
    blocks: groups.length,
    cold: groups.filter((el) => el.classList.contains('is-cold')).length,
    quick: groups.filter((el) => el.classList.contains('is-quick')).length,
    hidden: ops.filter((o) => parseFloat(o) < 0.99).length,
    arrive: getComputedStyle(groups[0]).getPropertyValue('--arrive').trim(),
    reduce: w.matchMedia('(prefers-reduced-motion: reduce)').matches
  };
})(d, w)
"""

# The claims the reduced-motion load is the only one that can carry. A world claim is
# not evidence about the reduced page and the reverse, so the self-test pays for the
# load that can catch its patch and no other: a self-test that loads two browsers per
# patch to prove one thing is a self-test nobody runs.
REDUCED_CLAIMS = ("in the reduced world nothing is written",)

# The claims that need the library's pair of page loads.
LIB_CLAIMS = ("the library hides only what is below the fold",
              "a block that waits is hidden while it waits",
              "a slow arrival gets the library's authored clock",
              "a fast arrival gets the library's own clock",
              "the same content arrives either way the reader came")
LIB_REDUCED_CLAIMS = ("in the reduced world the library marks nothing",)


def check_library(calm: dict, fast: dict, failures: list) -> None:
    """What the library hides, on whose clock it arrives, and that it arrives at all."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    for name, doc in (("slow", calm), ("fast", fast)):
        if "error" in doc:
            ok("the library's %s approach ran" % name, False, doc["error"])
            return

    # The fold test is what makes this safe for a reader whose script runs at all:
    # marking everything would hide the block they are already looking at, and marking
    # nothing would leave the library as it was - a page of text with no arrivals.
    # Both directions are read off the same list, because a run that hid nothing and a
    # run that hid everything are the two ways this can be wrong.
    vh = calm["vh"]
    below = [g for g in calm["groups"] if g["top"] >= vh]
    above = [g for g in calm["groups"] if g["top"] < vh]
    wrong = [g for g in below if not g["cold"]] + [g for g in above if g["cold"]]
    ok("the library hides only what is below the fold",
       bool(below) and not wrong,
       "%d of %d blocks sit below the fold and are cold, %d sit above it and are not%s"
       % (len(below), len(calm["groups"]), len(above),
          "" if above else " - nothing sat above the fold at this width, so that half "
                           "of the claim was not exercised"))

    # Cold has to mean hidden. The class and the rule are written twice on purpose (the
    # script for pages that load it, the stylesheet for pages that do not), which is
    # exactly the shape in which one of the two copies goes missing.
    ok("a block that waits is hidden while it waits",
       calm["parked"]["cold"] and float(calm["parked"]["opacity"]) < 0.5,
       "parked 40px below the fold it is cold %s at opacity %s, %s"
       % (calm["parked"]["cold"], calm["parked"]["opacity"],
          calm["parked"]["transform"]))

    def first_time(v):
        return float(v.split(",")[0].strip().rstrip("s"))

    ok("a slow arrival gets the library's authored clock",
       not calm["quick"] and calm["arrive"] == "1"
       and not calm["stillCold"] and float(calm["opacity"]) > 0.99,
       "--arrive = %s, %s, arrived at opacity %s"
       % (calm["arrive"], calm["duration"], calm["opacity"]))

    # The inequality is the whole feature, and it is checked from both sides: the fast
    # path has to be quicker AND has to finish, since an arrival that outran itself
    # would leave the block half-drawn at the bottom of the screen.
    ok("a fast arrival gets the library's own clock",
       fast["quick"] and fast["arrive"] != "1"
       and first_time(fast["duration"]) < first_time(calm["duration"]) * 0.6
       and not fast["stillCold"] and float(fast["opacity"]) > 0.99,
       "--arrive = %s, %s against the authored %s, arrived at opacity %s"
       % (fast["arrive"], fast["duration"], calm["duration"], fast["opacity"]))

    same = (calm["items"] == fast["items"]
            and calm["itemsOpacity"] == fast["itemsOpacity"]
            and calm["transform"] == "none" and fast["transform"] == "none")
    ok("the same content arrives either way the reader came",
       same,
       "%d links either way, opacity %s against %s, transform %s against %s"
       % (calm["items"], calm["itemsOpacity"], fast["itemsOpacity"],
          calm["transform"], fast["transform"]))


def check_library_reduced(doc: dict, failures: list) -> None:
    """The library under `prefers-reduced-motion`, where the arrivals do not exist."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the library's reduced run ran", False, doc["error"])
        return
    if not doc.get("reduce"):
        ok("the reduced world was forced", False,
           "the media query did not match, so the forced switch did not take and "
           "nothing here was measured")
        return
    ok("in the reduced world the library marks nothing",
       doc["cold"] == 0 and doc["quick"] == 0 and doc["hidden"] == 0
       and doc["blocks"] > 0 and doc["arrive"] == "1",
       "%d blocks, %d cold, %d quick, %d hidden, --arrive = %s"
       % (doc["blocks"], doc["cold"], doc["quick"], doc["hidden"], doc["arrive"]))


def self_test(chrome, site, width, height, tmp, family="all") -> int:
    print("self-test: %d doctored pages, each of which must fail one named claim"
          % len(SELF_TESTS))
    worst = 0
    # Which family of page loads a patch has to pay for, so this can be run a third at
    # a time: it grew past ten minutes otherwise, and a self-test nobody runs because
    # it takes a quarter of an hour is a self-test that stops being evidence. The
    # family is read off the claim the patch is declared to break, so a new patch
    # cannot forget to declare one.
    lib_claims = LIB_CLAIMS + LIB_REDUCED_CLAIMS
    skip = 0
    for i, entry in enumerate(SELF_TESTS):
        what, edits, expected = entry[0], entry[1], entry[2]
        # A patch names the built file it doctors and the page to drive, because they
        # are not always the landing's: the library's behaviour lives in the shared
        # `/theme.js` and `/styles.css`, and its claims are about `/library/`.
        rel, url = entry[3] if len(entry) > 3 else ("index.html", "/")
        in_lib = expected in lib_claims
        in_pace = expected in PACE_CLAIMS
        in_dwell = expected in DWELL_CLAIMS
        if ((family == "lib" and not in_lib) or (family == "pace" and not in_pace)
                or (family == "dwell" and not in_dwell)
                or (family == "land" and (in_lib or in_pace or in_dwell))):
            skip += 1
            continue
        broken = os.path.join(tmp, "broken-%d" % i)
        if os.path.isdir(broken):
            shutil.rmtree(broken)
        shutil.copytree(site, broken)
        patched = os.path.join(broken, rel)
        if not os.path.isfile(patched):
            print("  FAIL  %s: %s is not a file in the built site, so the self-test "
                  "is checking nothing" % (what, rel))
            worst = 1
            continue
        html = open(patched, encoding="utf-8").read()
        missing = [old for old, _ in edits if old not in html]
        if missing:
            print("  FAIL  %s: the text it patches is not in %s (%r), so the "
                  "self-test is checking nothing" % (what, rel, missing[0]))
            worst = 1
            continue
        for old, new in edits:
            html = html.replace(old, new, 1)
        AC.write(patched, html)

        # Each patch is checked by the family its claim belongs to and no other; a
        # self-test that loads four browsers per patch to prove one thing is a
        # self-test nobody runs. A patch aimed at the wheel is not evidence about
        # the arrivals, and the reverse.
        failures: list = []
        reduced_failures: list = []
        if in_lib:
            if expected in LIB_REDUCED_CLAIMS:
                rlib = run(chrome, broken, tmp, url, width, height,
                           LIB_REDUCED_SCENARIO,
                           extra=["--force-prefers-reduced-motion"],
                           tag="st%d-lib-red" % i)
                check_library_reduced(rlib, failures)
            else:
                cdoc = run(chrome, broken, tmp, url, width, height, LIB_CALM,
                           extra=None, tag="st%d-lib-calm" % i)
                fdoc = run(chrome, broken, tmp, url, width, height, LIB_FAST,
                           extra=None, tag="st%d-lib-fast" % i)
                check_library(cdoc, fdoc, failures)
        elif in_pace:
            cdoc = run(chrome, broken, tmp, "/", width, height, PACE_CALM,
                       extra=None, tag="st%d-calm" % i)
            fdoc = run(chrome, broken, tmp, "/", width, height, PACE_FAST,
                       extra=None, tag="st%d-fast" % i)
            check_pace(cdoc, fdoc, failures)
        elif in_dwell:
            ddoc = run(chrome, broken, tmp, "/", width, height, DWELL_SCENARIO,
                       extra=None, tag="st%d-dwell" % i)
            check_dwell(ddoc, failures)
        elif expected in REDUCED_CLAIMS:
            # Only the reduced page can carry this claim, so only it is driven: the
            # world run would cost a browser and could never report this failure.
            rdoc = run(chrome, broken, tmp, "/", width, height, REDUCED_SCENARIO,
                       extra=["--force-prefers-reduced-motion"], tag="st%d-reduced" % i)
            check_reduced(rdoc, reduced_failures)
        else:
            doc = run(chrome, broken, tmp, "/", width, height, SCENARIO,
                      extra=None, tag="st%d" % i)
            check(doc, failures)
        named = expected in failures or expected in reduced_failures
        print("  %s  %s -> %s" % ("ok  " if named else "FAIL", what,
                                  (", ".join(failures + reduced_failures) or "nothing failed")))
        if not named:
            worst = 1
    if worst == 0:
        print("self-test ok - every doctored page is caught by the claim it breaks"
              + (" (%d outside the %s family were skipped)" % (skip, family)
                 if skip else ""))
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
    ap.add_argument("--family", default="all", choices=("all", "land", "pace", "lib", "dwell"),
                    help="with --self-test, doctor only one family's pages: the landing's "
                         "world and reduced claims, the arrivals' pacing pair, or the "
                         "library's fold test and clock")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.site):
        print("error: %s is not a directory - run build-site.py first" % a.site,
              file=sys.stderr)
        return 1
    chrome = AC.find_chrome()
    tmp = tempfile.mkdtemp(prefix="istor-motion-")
    try:
        if a.self_test:
            return self_test(chrome, a.site, a.width, a.height, tmp, a.family)

        print("the mechanism, driven: %s at %dpx" % (a.site, a.width))
        failures: list = []
        doc = run(chrome, a.site, tmp, "/", a.width, a.height, SCENARIO)
        check(doc, failures)
        rdoc = run(chrome, a.site, tmp, "/", a.width, a.height, REDUCED_SCENARIO,
                   extra=["--force-prefers-reduced-motion"], tag="reduced")
        check_reduced(rdoc, failures)
        cdoc = run(chrome, a.site, tmp, "/", a.width, a.height, PACE_CALM,
                   extra=None, tag="pace-calm")
        fdoc = run(chrome, a.site, tmp, "/", a.width, a.height, PACE_FAST,
                   extra=None, tag="pace-fast")
        check_pace(cdoc, fdoc, failures)
        # M22 - stillness, driven. A 28s scenario of mostly waiting, which is
        # the honest cost of measuring patience.
        wdoc = run(chrome, a.site, tmp, "/", a.width, a.height, DWELL_SCENARIO,
                   extra=None, tag="dwell")
        check_dwell(wdoc, failures)
        # The library is a different page on a different pair of shared files, so it is
        # driven rather than inferred from the landing's behaviour: nothing about the
        # landing's arrivals would move if `/theme.js` lost its fold test.
        lcalm = run(chrome, a.site, tmp, "/library/", a.width, a.height, LIB_CALM,
                    extra=None, tag="lib-calm")
        lfast = run(chrome, a.site, tmp, "/library/", a.width, a.height, LIB_FAST,
                    extra=None, tag="lib-fast")
        check_library(lcalm, lfast, failures)
        lred = run(chrome, a.site, tmp, "/library/", a.width, a.height,
                   LIB_REDUCED_SCENARIO,
                   extra=["--force-prefers-reduced-motion"], tag="lib-reduced")
        check_library_reduced(lred, failures)

        if a.json:
            with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"motion": doc, "reduced": rdoc, "calm": cdoc, "fast": fdoc,
                           "dwell": wdoc,
                           "library": lcalm, "libraryFast": lfast,
                           "libraryReduced": lred, "failures": failures}, fh, indent=1)
            print("\nfindings written to %s" % a.json)

        print()
        if failures:
            print("FAILED - %d of %d claims are not true of the page:\n  %s"
                  % (len(failures), CHECKED[0], "\n  ".join(failures)))
            return 1
        band = "%dpx" % doc["heroBottom"] if isinstance(doc.get("heroBottom"), int) else "not measured"
        print("motion ok - %d claims about the two worlds, the landing's arrivals, "
              "the dwell and the library's, verified by driving the pages rather "
              "than by reading them (hero band %s of %s)"
              % (CHECKED[0], band, doc.get("viewport", "?")))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
