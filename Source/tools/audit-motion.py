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
  // The wait after the jumps is the coast claim's 1,200ms, not 600: the flywheel's
  // decay is still in flight at 600ms, and the residue sat ON the DRIFT_MAX
  // boundary across runs (-0.2, -0.2, -0.1) - a gate that fails on jitter is a
  // gate that lies. Give the decay the same window the coast gets and the
  // residue converges to the writer's rounding step.
  await home();
  before = angle(wheel); pos = position();
  for (let i = 0; i < 3; i++) { step(700); await wait(400); }
  await wait(1200);
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
  // M25 · the sun, read at home: rest, then the pointer's lean, then the
  // depth term the scroll writes. Read off the hero's computed background,
  // which is the only honest reading - a custom property round-trips as a
  // string and would pass even if the gradient ignored it.
  const sunBG = () => getComputedStyle(hero).backgroundImage;
  // The reader's return is TWO moves: the pointer back to centre and the
  // scroll back to the top. The hand's drag and the lean read both left the
  // pointer away from centre, and the sun keeps the LAST lean it was given,
  // so bg0 and bgBack read without this would be two different residues
  // compared - the claim would fail on a correct page forever.
  const readerHome = async () => {
    w.dispatchEvent(new w.PointerEvent('pointermove', { pointerId: 3,
      pointerType: 'mouse', clientX: Math.round(w.innerWidth / 2),
      clientY: 100, bubbles: true }));
    w.scrollTo({ top: 0, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
    // 1700ms, not the 400ms home() gives: the ease runs at 0.08/frame, so
    // the trip home crosses its own 0.002 stop slack ~1.3s after the target
    // moves - a 400ms window reads the return MID-FLIGHT and calls a correct
    // rest a failure. A measuring window waits out the coast it measures.
    await wait(1700);
  };
  await readerHome();
  const bg0 = sunBG();
  // Lean: a pointer far right of centre must move the origin right.
  w.dispatchEvent(new w.PointerEvent('pointermove', { pointerId: 3,
    pointerType: 'mouse', clientX: w.innerWidth - 20, clientY: 100,
    bubbles: true }));
  await wait(700);
  const bgRight = sunBG();
  // Sink: the depth term rides the scroll's own event, so no pointer needed.
  w.scrollTo({ top: Math.round(heroBottom / 2), behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  await wait(700);
  const bgMid = sunBG();
  await readerHome();
  const bgBack = sunBG();
  out.sun = { bg0, bgRight, bgMid, bgBack };
  // M26 · the bearing, read mid-flight is useless - the claim is about WHERE
  // it settles - so every read waits out the 340ms glide it measures. The
  // transform's ty is the honest reading: a custom property round-trips as a
  // string, and the dots' aria-current is the state the ring must agree with,
  // so the ring's index is compared to the RAIL's named act, not to itself.
  const rail = d.querySelector('.act-index');
  // M30 · the header's three links, read as the list of hrefs that currently
  // carry aria-current (null where they do not). Declared here, before either
  // read, so both stops answer with the same instrument.
  const headerRead = () => Array.from(d.querySelectorAll('.nav-links a'))
    .map((a) => a.hasAttribute('aria-current') ? a.getAttribute('href') : null);
  const ringRead = async () => {
    await wait(700);
    const cs = getComputedStyle(rail, '::before');
    const m = cs.transform.match(/matrix\(([^)]+)\)/);
    const named = Array.from(rail.querySelectorAll('a'))
      .findIndex((a) => a.hasAttribute('aria-current'));
    return { ty: m ? parseFloat(m[1].split(',')[5]) : null,
             op: parseFloat(cs.opacity),
             i: rail.style.getPropertyValue('--i'), named: named };
  };
  const ring0 = await ringRead();
  // A deep act, far enough that the slot difference is unambiguous.
  const machineAct = d.getElementById('on-your-machine');
  w.scrollTo({ top: machineAct.getBoundingClientRect().top + w.scrollY - 200,
               behavior: 'instant' });
  w.dispatchEvent(new Event('scroll'));
  const ringMid = await ringRead();
  const headerMid = headerRead();
  await readerHome();
  const ringBack = await ringRead();
  // M30 · the header's answer, read on the same two stops: at the top, where
  // the hero is the act and no header link names it, and deep in "On your
  // machine", whose header link is the one of the three that names the act
  // the rail has already promoted. The rail's own named act is the truth this
  // is compared against - the header agrees with the rail or the claim fails.
  const headerTop = headerRead();
  out.bearing = { ring0: ring0, ringMid: ringMid, ringBack: ringBack,
                  headerTop: headerTop, headerMid: headerMid };
  // M33 · the two whole-SVG reveals. Their is-cold selectors were the one
  // thing the stylesheet did not answer (the M3 list names a .win or an
  // .exhibit img, and these figures are neither), so both sat fully drawn
  // through their own waiting state. The read is the family's own shape:
  // arm-check at cold (opacity 0), release, wait out the 700ms window, and
  // the settled state must be the authored one.
  //
  // THREE THINGS THE PROBE HAD TO LEARN, and each cost a false failure.
  //
  // THE SCROLL LANDS HIGH, NOT CENTRED. Centring a plate puts its whole
  // neighbourhood in view, and the four plates are neighbours: the gallery
  // stacks the parapegma, the rear dials and the games dial within 1,600px of
  // each other. Centring the rear dials (12664..13016 on the built page at
  // 1440x900) puts the viewport at 12390..13290, and the parapegma's own box
  // (11930..12612) crosses it - so centring the dials fired the parapegma,
  // which then read armed false on its own turn, through no fault of the page.
  // The read now puts its plate's top 24px under the viewport's top edge. That
  // is the one placement that is inside the observer's band whether or not the
  // containing frame clips it, and it can only ever fire plates BELOW the one
  // being read, which the order below makes harmless.
  //
  // THE CONTAINING FRAME IS SHORTER THAN THE PAGE'S OWN BAND. The harness sizes
  // the iframe to the viewport being claimed (1440x900) but opens Chrome at its
  // default window, so the iframe is clipped to the window's 600px, and an
  // IntersectionObserver reaches no further than its frame's visible part. The
  // observer's own `rootMargin` (`0px 0px -12% 0px`, so a line at 792 of 900)
  // is therefore NOT the line the page is judged against here: the real line is
  // 600. A plate scrolled to the middle of the iframe (top at 630 of 900) sits
  // below that line and its arrival never happens at all. Measured in that
  // frame, on the parapegma: with its top placed 109px down the iframe it
  // releases to opacity 1, at 24px it releases to opacity 1, and at 630px it
  // stays at opacity 0 through the whole 1,500ms window. 24px is the placement
  // that holds whichever of the two lines applies.
  //
  // THE ORDER. The plates are read top to bottom, in document order, because
  // that is the only order in which each one is still armed when its own read
  // arrives - a block unobserves after it fires, so a read that scrolls past a
  // plate spends it for every read after it. Reading downward means anything a
  // read fires out of turn is a plate below it, whose own read has not happened
  // yet. Reading the parapegma last could never be honest, whatever scroll it
  // used: it sits above the dials and the games dial, and the scroll that
  // reaches either of them passes it.
  //
  // The page fact was checked by hand while this was fixed, before the probe
  // was touched: on a fresh load at 1440x900 the parapegma reads cold true at
  // opacity 0 and matrix(0.97, 0, 0, 0.97, 0, 24), and 1,500ms after it is
  // scrolled into its band it reads cold false at opacity 1 and transform
  // none - the authored pair. What failed was the instrument's geometry, not
  // the arrival.
  const plateRead = async (sel) => {
    const fig = d.querySelector(sel);
    if (!fig) return { error: 'no ' + sel };
    const svg = fig.querySelector('svg');
    const top = fig.getBoundingClientRect().top + w.scrollY;
    // 'instant', not the stylesheet's global smooth: a smooth scroll from the
    // act above passes every plate between here and there through the band on
    // the way, which spends them for their own reads. A jump is one position
    // and the observer judges that position.
    w.scrollTo({ top: Math.max(0, top - 24), behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
    const cold = fig.classList.contains('is-cold');
    const coldOp = cold ? getComputedStyle(svg).opacity : null;
    await wait(1600);
    const cs = getComputedStyle(svg);
    return { cold: cold, coldOp: coldOp, restOp: parseFloat(cs.opacity),
             restTransform: cs.transform, armed: cold };
  };
  // Every plate sits below the fold, so a fresh load has them cold; if the
  // run arrived here already-released (a scenario reorder, or a short
  // viewport that fired them on the way down), the claim records that
  // honestly rather than passing on a state nobody drove.
  out.parapegmaPlate = await plateRead('.parapegma-fig');
  out.dialsPlate = await plateRead('.rear-dials');
  out.gamesPlate = await plateRead('.games-dial-fig');
  out.boundaryPlate = await plateRead('.boundary');
  await home();
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
  const line = d.querySelector('.hero .h1-reveal .h1-line');
  // M25 · under reduce the sun's writer is never armed (the arm requires
  // !reduced), so the hero's inline style must carry neither sun property.
  const heroStyle = hero.getAttribute('style') || '';
  const sunArmed = /--sun-(x|d)\s*:/.test(heroStyle);
  // M26 · under reduce the ring still renders at its right slot; what must be
  // absent is the glide. Read the transform, not the custom property alone: a
  // property round-trips as a string and would pass even if nothing rendered.
  const railR = d.querySelector('.act-index');
  let ringArmed = false;
  if (railR) {
    await wait(400);
    const stepTo = d.getElementById('on-your-machine');
    w.scrollTo({ top: stepTo.getBoundingClientRect().top + w.scrollY - 200,
                 behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
    await wait(500);
    const csR = getComputedStyle(railR, '::before');
    const mR = csR.transform.match(/matrix\(([^)]+)\)/);
    const namedR = Array.from(railR.querySelectorAll('a'))
      .findIndex((a) => a.hasAttribute('aria-current'));
    ringArmed = mR ? Math.abs((parseFloat(mR[1].split(',')[5]) + 12)
                   - namedR * 26) < 0.5 : false;
  }
  return { reduced: w.matchMedia('(prefers-reduced-motion: reduce)').matches,
           worldPresent: true,
           sunArmed: sunArmed,
           ringArmed: ringArmed,
           wroteTransform: wheel.hasAttribute('transform'),
           scrolled: Math.round(w.scrollY),
           heroColdArmed: hero.classList.contains('is-cold'),
           lineAtRest: line ? String(getComputedStyle(line).transform) : 'absent' };
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
    """One run's answer box. This used to be a class-global shared by every run,
    which was fine while runs were serial but made the tool unable to run two
    pages at once: two concurrent runs would read each other's answers and half
    the claims would be checked against the wrong page's evidence. Each run()
    now owns one box, the handler factory closes over it, and two runs on two
    ports on two profiles share nothing at all. SLOW RUNS ARE STILL SERIAL
    INSIDE THEMSELVES - one box, one page, one answer - so every claim's
    semantics are exactly what they were; only the WAITING overlaps."""

    def __init__(self) -> None:
        self.answer: dict | None = None

    def post_result(self, body: bytes) -> None:
        try:
            self.answer = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            self.answer = {"error": "the harness posted something unreadable: %s" % exc}


def make_handler(site: str, harness: str, rig: Rig):
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
            rig.post_result(self.rfile.read(n))
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
    rig = Rig()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(site, harness, rig))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    cmd = [chrome, "--headless", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--hide-scrollbars",
           "--user-data-dir=" + profile] + list(extra or []) + [base + "/_motion.html"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")
    deadline = time.time() + timeout
    try:
        while time.time() < deadline and rig.answer is None:
            time.sleep(0.1)
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
        srv.shutdown()
    if rig.answer is None:
        return {"error": "no answer in %ds; the browser was killed. A page that keeps "
                         "requesting animation frames can hold a headless renderer "
                         "open, so this is reported rather than waited on forever" % timeout}
    doc = rig.answer
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




# M23 asks the question first paint asks: what does the page's OPENING look
# like, and can it be broken silently? The window's sequence (M2) was always
# verified implicitly by the world runs; the hero's words were never verified at
# all, because before M23 they did not move. The scenario runs in real time like
# every other one: it reads the arrived state off the words, records the order
# they first become visible in, measures the mask's room around the line, then
# re-arms the cold state and demands the arrival happen a second time - a class
# the page itself re-adds must not be a one-way door.
HERO_SCENARIO = r"""
(async (d, w) => {
  const hero = d.querySelector('.hero');
  const lines = Array.from(d.querySelectorAll('.hero .h1-reveal .h1-line'));
  const lede = d.querySelector('.hero .lede');
  const cta = d.querySelector('.hero .cta');
  const cue = d.querySelector('.hero .scroll-cue');
  const world = d.querySelector('.hero-world');
  if (!hero || !lines.length || !lede || !cta || !cue || !world) {
    return { error: 'the arrival scenario needs the hero\'s words: hero=' + !!hero +
                    ' lines=' + lines.length + ' lede=' + !!lede + ' cta=' + !!cta +
                    ' cue=' + !!cue + ' world=' + !!world };
  }
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const state = () => {
    const s = (el) => {
      const cs = getComputedStyle(el);
      return { op: cs.opacity, tf: cs.transform };
    };
    return { line1: s(lines[0]), line2: s(lines[1]), lede: s(lede),
             cta: s(cta), cue: s(cue), world: s(world) };
  };
  const ty = (st) => {
    if (st.tf === 'none') return 0;
    const m = /matrix\(([^)]+)\)/.exec(st.tf);
    return m ? parseFloat(m[1].split(',')[5]) : 999;
  };
  const atRest = (st) => parseFloat(st.op) >= 0.95 && Math.abs(ty(st)) < 2;
  // Both measures mean the same thing: essentially arrived. An element is
  // marked at 90% opacity just as a line is marked within 3px of rest -
  // comparing a line's 97% point against a fade's 50% point would interleave
  // two performers whose designed order is strict.
  const visible = (st) => parseFloat(st.op) >= 0.9 && Math.abs(ty(st)) < 3;
  const lineVisible = visible; // the mask holds a line's opacity at 1, so the
                               // opacity half is vacuous for it - one shared
                               // predicate so the measure cannot drift apart

  // The harness has already waited out its settle (700ms), so the entrance is
  // in flight NOW. Record when each performer first becomes visible; the mask
  // hides the line's opacity (always 1), so its visibility is the transform.
  const t0 = performance.now();
  const firsts = {};
  let seen = { line1: false, line2: false, lede: false, cta: false, cue: false };
  const poll = setInterval(() => {
    const s = state();
    const mark = (k, ok) => {
      if (!seen[k] && ok) { seen[k] = true; firsts[k] = Math.round(performance.now() - t0); }
    };
    mark('line1', lineVisible(s.line1));
    mark('line2', lineVisible(s.line2));
    mark('lede', visible(s.lede));
    mark('cta', visible(s.cta));
    mark('cue', visible(s.cue));
  }, 40);

  await wait(1700);
  clearInterval(poll);
  const arrived = state();
  const mask = d.querySelector('.hero .h1-reveal');
  const mr = mask.getBoundingClientRect();
  const room = (el) => {
    const lr = el.getBoundingClientRect();
    return { top: Math.round((lr.top - mr.top) * 10) / 10,
             bottom: Math.round((mr.bottom - lr.bottom) * 10) / 10 };
  };
  const result = {
    arrived: {
      line1: atRest(arrived.line1), line2: atRest(arrived.line2),
      lede: atRest(arrived.lede), cta: atRest(arrived.cta), cue: atRest(arrived.cue),
      world: atRest(arrived.world),
    },
    firsts: firsts,
    maskRoom: { line1: room(lines[0]), line2: room(lines[1]) },
  };
  // M43 · the answer's seventh child. The cycles answer gained a drawn plate
  // (the pin-and-slot, the sentence that names it made visible), and M2's
  // sequence gained a seventh slot for it. The claim reads the COMPUTED
  // animation-delay, not a wall-clock race: by the time this scenario polls,
  // the sequence may already have finished, and two settled elements cannot
  // be ordered by their timestamps. The delay is the authored slot (the
  // sixth child's 1260ms plus the family's 100ms step, read as a computed
  // value the doctor's removal zeroes), and the plate must be at rest.
  const answer = d.querySelector('.hero .answer#ans-cycles') ||
                 d.querySelector('.hero .answer');
  const kids = answer ? answer.children : [];
  if (kids.length >= 7) {
    const fig = kids[6];
    const prev = kids[5];
    const delayOf = (el) => getComputedStyle(el).animationDelay;
    const fs = (() => { const cs = getComputedStyle(fig);
      return { op: parseFloat(cs.opacity), tf: cs.transform }; })();
    result.answerPlate = {
      seventhChild: fig.tagName.toLowerCase() + '.' + (fig.className || ''),
      atRest: fs.op >= 0.95 && (fs.tf === 'none' ||
               Math.abs(parseFloat(/matrix\(([^)]+)\)/.exec(fs.tf)[1].split(',')[5] || 0)) < 2),
      figDelay: delayOf(fig),
      prevDelay: delayOf(prev),
      ordered: parseFloat(delayOf(fig)) > parseFloat(delayOf(prev)),
    };
  }

  // Re-arm the cold state and hold it long enough for the hiding to finish
  // (the lede's own clock is 560ms of delay plus 560ms of travel; the cue's is
  // 1360ms), then release and demand the arrival again.
  hero.classList.add('is-cold');
  // M27 · one scroll, so the depth term can speak in the cold state: both the
  // hold and the cold class are read inside the scroll handler, and a state
  // that never produces an event is a state the page cannot answer in. The
  // 1450ms is the ease's own coast (74 frames of 0.92 to cross its stop slack)
  // plus margin, so the read is the settled pose, not the flight.
  w.dispatchEvent(new Event('scroll'));
  await wait(1450);
  const cold = state();
  // The origin is authored through calc(), but the computed serialization
  // differs between Chromium builds: some keep calc(78%), some simplify it
  // to 78%. Parsing must accept both, or a correct dawn reads as no pose -
  // which is exactly the false failure the first run produced.
  const sunOrigin = (bg) => {
    const m = /at\s+(?:calc\(([^)]*)\)|([^\s,()]+))\s+(?:calc\(([^)]*)\)|([^\s,()]+))/.exec(bg);
    return m ? { x: m[1] || m[2], y: m[3] || m[4] } : null;
  };
  const coldPose = sunOrigin(getComputedStyle(hero).backgroundImage);
  result.coldDawn = {
    originY: coldPose ? parseFloat(coldPose.y) : null,
    styleD: ((hero.getAttribute('style') || '').match(/--sun-d:\s*([\d.]+)/) || [])[1] || null,
    bg: getComputedStyle(hero).backgroundImage.slice(0, 160),
  };
  result.cold = {
    line1Down: Math.abs(ty(cold.line1)) > 20,
    line2Down: Math.abs(ty(cold.line2)) > 20,
    ledeHidden: parseFloat(cold.lede.op) < 0.05,
    ctaHidden: parseFloat(cold.cta.op) < 0.05,
    cueHidden: parseFloat(cold.cue.op) < 0.05,
    worldHidden: parseFloat(cold.world.op) < 0.05,
  };
  hero.classList.remove('is-cold');
  // M27 · the same one scroll on release, so the pose the reader gets is the
  // one the page's own handler targets rather than wherever the ease coasts.
  w.dispatchEvent(new Event('scroll'));
  await wait(1500);
  const back = state();
  const backPose = sunOrigin(getComputedStyle(hero).backgroundImage);
  result.restoredDawn = { originY: backPose ? parseFloat(backPose.y) : null,
                          bg: getComputedStyle(hero).backgroundImage.slice(0, 160) };
  result.restored = {
    line1: atRest(back.line1), line2: atRest(back.line2), lede: atRest(back.lede),
    cta: atRest(back.cta), cue: atRest(back.cue),
  };
  return result;
})(d, w)
"""


# M24 asks the question the close asks at the page's END, and the hero now
# answers at its START: what does this moment look like when it arrives? M6
# re-inked the mark and M14b swept the gears, but the window, the heading, the
# paragraph and the CTA sat there already printed - the close was a poster with
# a theatre whose cast refused to enter. The scenario arrives like a reader
# (parks above the mark's threshold, lets the park's own pace go stale, then
# approaches on steps that make the pace the quick test reads), records the
# order the cast first becomes visible in, and reads the arrived state off
# every member. The same "essentially arrived" predicate M23's order claim
# learned to use: one shared reading, opacity >= 0.9 and transform within 3px,
# so no performer is measured by a different ruler than another.
CLOSE_SCENARIO = r"""
(async (d, w) => {
  const poster = d.querySelector('.poster');
  const mark = d.getElementById('close-mark');
  const win = poster ? poster.querySelector('.win') : null;
  const h2 = poster ? poster.querySelector('.body h2') : null;
  const p = poster ? poster.querySelector('.body > p') : null;
  const cta = poster ? poster.querySelector('.body .cta') : null;
  if (!poster || !mark || !win || !h2 || !p || !cta) {
    return { error: 'the close scenario needs its cast: poster=' + !!poster +
                    ' mark=' + !!mark + ' win=' + !!win + ' h2=' + !!h2 +
                    ' p=' + !!p + ' cta=' + !!cta };
  }
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const step = (dy) => {
    w.scrollTo({ top: w.scrollY + dy, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
  };
  const ty = (el) => {
    const m = /matrix\(([^)]+)\)/.exec(getComputedStyle(el).transform);
    return m ? parseFloat(m[1].split(',')[5]) : 0;
  };
  const arrived = (el) => parseFloat(getComputedStyle(el).opacity) >= 0.9
                       && Math.abs(ty(el)) < 3;
  // The window is the one cast member measured by OPACITY ALONE. M6's parallax
  // writes an inline transform on it every scroll, so a transform reading there
  // measures M6, not M24 - and the stylesheet arrives it by opacity alone for
  // exactly that reason. One documented exception, not a second ruler by stealth.

  const wasCold = mark.classList.contains('is-cold');
  const below = mark.getBoundingClientRect().top >= w.innerHeight;
  if (wasCold) {
    // Park just above the mark's threshold and let the park's own pace go
    // stale (the quick test wants the approach, not the positioning), then
    // arrive like a reader: the approach below is the only motion measured.
    const top = mark.getBoundingClientRect().top + w.scrollY;
    w.scrollTo({ top: top - w.innerHeight - 100, behavior: 'instant' });
    w.dispatchEvent(new Event('scroll'));
    await wait(500);
  }

  __APPROACH__
  const t0 = performance.now();
  const firsts = {};
  let seen = { mark: false, win: false, h2: false, p: false, cta: false };
  const mark2 = (k, ok) => {
    if (!seen[k] && ok) { seen[k] = true;
                          firsts[k] = Math.round(performance.now() - t0); }
  };
  const poll = setInterval(() => {
    mark2('mark', !mark.classList.contains('is-cold'));
    mark2('win', parseFloat(getComputedStyle(win).opacity) >= 0.9);
    mark2('h2', arrived(h2));
    mark2('p', arrived(p));
    mark2('cta', arrived(cta));
  }, 40);

  await wait(2600);
  clearInterval(poll);
  return {
    armed: wasCold, belowFoldOnLoad: below,
    firsts: firsts,
    quick: poster.classList.contains('is-quick'),
    arrive: getComputedStyle(poster).getPropertyValue('--arrive').trim(),
    atRest: {
      mark: !mark.classList.contains('is-cold'),
      win: parseFloat(getComputedStyle(win).opacity) >= 0.9,
      h2: arrived(h2), p: arrived(p), cta: arrived(cta),
    },
  };
})(d, w)
"""

CLOSE_CALM = CLOSE_SCENARIO.replace("__APPROACH__",
    "for (let i = 0; i < 8; i++) { step(60); await wait(80); }")
CLOSE_FAST = CLOSE_SCENARIO.replace("__APPROACH__",
    "for (let i = 0; i < 8; i++) { step(220); await wait(16); }")


def check_close(doc: dict, failures: list, fast: bool = False,
                reduced: bool = False) -> None:
    """M24's claims, read off the close the way a reader meets it: as a state.

    The reduced run asserts only the reduced claim - the cold state never
    existed there, so the arrival claims would be checking nothing. The fast
    run adds the clock claim: the compressed arrival must still end at rest.
    """
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the close's arrival scenario ran", False, doc["error"])
        return
    if reduced:
        r = doc.get("atRest", {})
        keys = ("mark", "win", "h2", "p", "cta")
        ok("in the reduced world the close's cast is simply there",
           doc.get("armed") is False and all(r.get(k) for k in keys),
           "no cold state on the close (armed=%s), all five readable at rest"
           % doc.get("armed"))
        return
    r = doc.get("atRest", {})
    keys = ("mark", "win", "h2", "p", "cta")
    ok("the close's cast arrives with the mark",
       doc.get("armed") is True and all(r.get(k) for k in keys),
       "armed on load: %s, at rest: " % doc.get("armed")
       + ", ".join("%s %s" % (k, "yes" if r.get(k) else "NO") for k in keys))
    f = doc.get("firsts", {})
    order = [f.get(k) for k in ("mark", "win", "h2", "p", "cta")]
    ok("the cast arrives in order: mark, window, h2, paragraph, CTA",
       all(t is not None for t in order)
       and all(order[i] <= order[i + 1] + 40 for i in range(4)),
       "first visible at %s ms on the scenario's own clock (40ms poll grace)"
       % order)
    if fast:
        ok("a fast approach to the close compresses the clock, not the cast",
           doc.get("quick") is True and doc.get("arrive") == "0.3"
           and all(r.get(k) for k in keys),
           "quick=%s, --arrive=%s, all five at rest"
           % (doc.get("quick"), doc.get("arrive")))




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




# M23's claims, and the tuple the doctors read their family from. The reduced
# world's claim lives in REDUCED_CLAIMS, where the reduced scenario can carry it.
HERO_CLAIMS = (
    "the hero's words arrive with the page",
    "the arrival is ordered: line1, line2, lede, CTA, cue",
    "the mask leaves the lines room to breathe",
    "is-cold hides the hero's arrival again",
    "released, the hero arrives a second time",
    "the dawn holds the light sunk in the cold state",
    "and releases it on the cast's own clock",
    "the cycles answer's plate arrives last, at rest",
)


def check_hero(doc: dict, failures: list) -> None:
    """M23's claims, read off the hero the way a reader meets it: as a state."""
    def ok(label, good, detail=""):
        CHECKED[0] += 1
        print("  %s  %-58s %s" % ("ok  " if good else "FAIL", label, detail))
        if not good:
            failures.append(label)

    if "error" in doc:
        ok("the arrival scenario ran", False, doc["error"])
        return
    a = doc.get("arrived", {})
    keys = ("line1", "line2", "lede", "cta", "cue", "world")
    ok("the hero's words arrive with the page",
       all(a.get(k) for k in keys),
       "at rest: " + ", ".join("%s %s" % (k, "yes" if a.get(k) else "NO") for k in keys))
    f = doc.get("firsts", {})
    order = [f.get(k) for k in ("line1", "line2", "lede", "cta", "cue")]
    ok("the arrival is ordered: line1, line2, lede, CTA, cue",
       all(t is not None for t in order)
       and all(order[i] <= order[i + 1] + 40 for i in range(4)),
       "first visible at %s ms on the scenario's own clock (40ms poll grace)" % order)
    m = doc.get("maskRoom", {})
    tops = [(m.get(k) or {}).get("top", -1) for k in ("line1", "line2")]
    bottoms = [(m.get(k) or {}).get("bottom", -1) for k in ("line1", "line2")]
    ok("the mask leaves the lines room to breathe",
       min(tops) >= 2 and min(bottoms) >= 2,
       "the lines clear their mask by %s/%s px above and %s/%s px below at rest - "
       "the y in 'you' paints past the 1.06 line box, so the clip window is "
       "padded 0.14em for it" % (tops[0], tops[1], bottoms[0], bottoms[1]))
    c = doc.get("cold", {})
    ckeys = ("line1Down", "line2Down", "ledeHidden", "ctaHidden", "cueHidden",
             "worldHidden")
    ok("is-cold hides the hero's arrival again",
       all(c.get(k) for k in ckeys),
       "re-armed: " + ", ".join("%s %s" % (k, "hidden" if c.get(k) else "VISIBLE")
                                for k in ckeys))
    r = doc.get("restored", {})
    ok("released, the hero arrives a second time",
       all(r.get(k) for k in ("line1", "line2", "lede", "cta", "cue")),
       "the same words at rest again - is-cold must not be a one-way door")

    # M43 · the answer's drawn plate. The computed animation-delay is the
    # authored slot (1.36s of the family's clock); the doctor's removal
    # reads 0s, which orders the plate with the prose instead of after it.
    # At rest the plate is the authored state, fully painted.
    ap = doc.get("answerPlate") or {}
    if ap:
        ok("the cycles answer's plate arrives last, at rest",
           ap.get("atRest") is True and ap.get("ordered") is True,
           "child %s delay %s (prev %s), at rest %s"
           % (ap.get("seventhChild", "?"), ap.get("figDelay"),
              ap.get("prevDelay"), ap.get("atRest")))
    else:
        ok("the cycles answer's plate arrives last, at rest", False,
           "the scenario found no seventh child to read")

    # M27 · the dawn's two claims, read off the rendered gradient the way the
    # sun's are: the computed background is the only honest reading of a
    # custom property, and the style attribute is what separates a pose the
    # page wrote from one the stylesheet defaulted. Sunk is d = 1, which
    # renders as origin 28%; authored rest is d = 0, origin 14%. The cold
    # state must hold the sunk pose and the released state must be back on
    # the authored one, or the opening the page performs is not the opening
    # it authored.
    dc = doc.get("coldDawn") or {}
    dr = doc.get("restoredDawn") or {}
    ok("the dawn holds the light sunk in the cold state",
       dc.get("originY") is not None and dc["originY"] > 25
       and dc.get("styleD") is not None and float(dc["styleD"]) > 0.9,
       "sunk is origin 28%% with --sun-d 1: the cold state reads %.1f%% (style %s) bg=%s"
       % (dc.get("originY") if dc.get("originY") is not None else -1, dc.get("styleD"),
          (dc.get("bg") or "")[:90]))
    ok("and releases it on the cast's own clock",
       dr.get("originY") is not None and dr["originY"] < 17,
       "released, the origin is back on the authored 14%%: %.1f%% bg=%s"
       % (dr.get("originY") if dr.get("originY") is not None else -1,
          (dr.get("bg") or "")[:90]))


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
        # The teleport's residue is QUANTIZED: the writer rounds the wheel's
        # angle to 0.1 degrees, so the harness cannot read finer than one
        # quantum, and under a loaded machine the honest residue is two
        # (-0.2, -0.2, -0.1, -0.1 across four runs - and a real gesture
        # charges 2 degrees, ten times the bound). DRIFT_MAX's one quantum
        # sat inside the quantization noise and the gate failed on jitter;
        # the bound for the teleport is two quanta, stated where the
        # measurement can actually resolve it.
        JUMPS_MAX = 0.25
        ok(label, v[key] is not None and abs(v[key]) <= JUMPS_MAX,
           "%s degrees of free rotation (the writer rounds to %.1f)" % (v[key], SETTLE_MAX))

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
       v["ratioAtRelease"] is not None and abs(abs(v["ratioAtRelease"]) - RATIO) < 0.001,
       "pinion/wheel = %s, and 223/48 = %.4f" % (v["ratioAtRelease"], RATIO))
    ok("the wheel coasts after the gesture ends",
       v["coasted"] is not None and v["coasted"] >= 3,
       "%s degrees after the reader stopped, on top of the %s already charged"
       % (v["coasted"], v["charged"]))
    ok("the mesh ratio holds through the coast",
       v["ratioInCoast"] is not None and abs(abs(v["ratioInCoast"]) - RATIO) < 0.001,
       "pinion/wheel = %s" % v["ratioInCoast"])
    ok("and then it stops", v["settledDelta"] is not None
       and abs(v["settledDelta"]) <= SETTLE_MAX,
       "%s degrees in the 600ms after the coast was given 1.5s to finish"
       % v["settledDelta"])

    ok("a flick below the hero does not charge the wheel",
       v["belowHero"] > v["heroBottom"] + 400 and v["belowHeroCharged"] is not None
       and abs(v["belowHeroCharged"]) <= DRIFT_MAX,
       "%dpx down, %.3f degrees of free rotation from the same gesture that charges "
       "%.1f at the hero" % (v["belowHero"], v["belowHeroCharged"], v["charged"]))

    ok("the hand turns the wheel", v["handTurned"] is not None
       and abs(v["handTurned"]) >= 0.5,
       "%s degrees from a 120px drag" % v["handTurned"])
    ok("the mesh ratio holds under the hand",
       v["ratioUnderHand"] is not None and abs(abs(v["ratioUnderHand"]) - RATIO) < 0.001,
       "pinion/wheel = %s" % v["ratioUnderHand"])

    ok("a control keeps its own pointer", not v["controlStartsATurn"],
       "the pointer was over %s" % v["controlTarget"])
    ok("a touch is never taken", not v["touchStartsATurn"],
       "a touch drag is the reader scrolling")

    # M25 · the sun's three claims, read off computed backgrounds. The lean
    # and the sink must both MOVE the origin (the gradient string differs);
    # returning home must return the authored gradient exactly, or the lamp
    # would be a lamp that never turns off. A browser without registered
    # properties keeps bg0 == bgRight == bgMid, so the claims fail loudly
    # rather than silently measuring a static gradient that never moved.
    s = v.get("sun") or {}
    ok("the field's light leans with the pointer",
       bool(s) and s["bg0"] != s["bgRight"],
       "the computed origin differs from rest when the pointer sits far right"
       if s else "no sun reading in this document")
    ok("the field's light sinks as the reader descends",
       bool(s) and s["bgRight"] != s["bgMid"],
       "the computed origin at half the hero band differs from the leaned one"
       if s else "no sun reading in this document")
    ok("and returns when the reader does",
       bool(s) and s["bgBack"] == s["bg0"],
       "home again, the gradient is the authored one to the string"
       if s else "no sun reading in this document")

    # M26 · the bearing's three claims. The ring must appear (the dots' aria-
    # current already carries the state; the ring is its visual half), must sit
    # on the SAME act the rail names - the ring's --i against the rail's own
    # aria-current, not against itself - and must return to the first dot when
    # the reader returns home. `--i` reads back as "0", "1", ...; the transform
    # is the render of it, which is what the eye actually sees.
    b = v.get("bearing") or {}
    r0, rm, rb = b.get("ring0") or {}, b.get("ringMid") or {}, b.get("ringBack") or {}
    PITCH = 26
    def ring_ty(r):
        # ty is the render of -50% + i*26px on a 24px ring: -12 + i*26.
        return None if r.get("ty") is None else r["ty"] + 12
    ok("the bearing rides the rail it marks",
       bool(b) and r0.get("op") == 1.0 and rm.get("op") == 1.0,
       "the ring is present whenever its rail is: op %s at rest, %s in act %s"
       % (r0.get("op"), rm.get("op"), rm.get("named")))
    ok("the bearing settles on the act the rail names",
       bool(b) and ring_ty(rm) is not None
       and abs(ring_ty(rm) - rm.get("named", -9) * PITCH) < 0.5
       and rm.get("i") == str(rm.get("named")),
       "the ring's travel index (%s) and its rendered slot (%.1f) both name the act the rail's aria-current names (%s)"
       % (rm.get("i"), ring_ty(rm) if ring_ty(rm) is not None else -99, rm.get("named")))
    ok("and hands back to the first act on the return",
       bool(b) and rb.get("i") == "0" and ring_ty(rb) is not None and abs(ring_ty(rb)) < 0.5,
       "home again, the ring sits on the first dot: --i %s, render %.1f"
       % (rb.get("i"), ring_ty(rb) if ring_ty(rb) is not None else -99))
    # M30 · the header's answer. At the top no header link may claim the act
    # (the hero is not one of the three), and in "On your machine" exactly the
    # link whose href names the rail's act carries it: the header agrees with
    # the rail or the wayfinding is lying somewhere.
    ht = (b.get("headerTop") or []) if isinstance(b.get("headerTop"), list) else []
    hm = (b.get("headerMid") or []) if isinstance(b.get("headerMid"), list) else []
    mid_named = None
    if rm.get("named") is not None:
        rail_acts = ["#what-it-is", "#how-it-answers", "#the-passage",
                     "#on-your-machine", "#where-it-stops", "#the-evidence",
                     "#questions", "#the-name"]
        mid_named = rail_acts[rm["named"]] if rm["named"] < len(rail_acts) else None
    current_mid = [h for h in hm if h]
    ok("the header's links answer for the act they name",
       ht is not None and all(h is None for h in ht)
       and current_mid == ([mid_named] if mid_named in (
           "#how-it-answers", "#on-your-machine", "#questions") else []),
       "at rest %s; in act %s the header carries %s"
       % (ht, rm.get("named"), current_mid or "nothing"))

    # M33 · the two whole-SVG reveals arrive. The claims are the family's own:
    # the block was armed cold (so the arrival is real), the stylesheet answered
    # it (the plate was actually hidden while it waited - the bug this exists
    # for is the class arriving with no rule behind it), and the released state
    # is the authored one (opaque, untransformed). A plate that reads armed
    # false was fired before the probe got there - an environment fact, not a
    # page fact - so the claim records it and fails loudly rather than passing
    # on a state nobody drove.
    for key, label in (("boundaryPlate", "the boundary plate arrives from its own cold state"),
                       ("dialsPlate", "the rear dials arrive from their own cold state"),
                       ("gamesPlate", "the games dial arrives from its own cold state"),
                       ("parapegmaPlate", "the parapegma arrives from its own cold state")):
        p = v.get(key) or {}
        if p.get("error"):
            ok(label, False, p["error"])
            continue
        ok(label,
           p.get("armed") is True
           and p.get("coldOp") == "0"
           and p.get("restOp") == 1.0
           and p.get("restTransform") in ("none", "matrix(1, 0, 0, 1, 0, 0)"),
           "cold %s (opacity %s), released to opacity %s, transform %s"
           % (p.get("armed"), p.get("coldOp"), p.get("restOp"),
              (p.get("restTransform") or "?")[:28]))



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
    ok("in the reduced world the hero never arms its arrival",
       not doc.get("heroColdArmed")
       and doc.get("lineAtRest") in ("none", "matrix(1, 0, 0, 1, 0, 0)"),
       "no cold state on the field, the headline at rest: %s" % doc.get("lineAtRest"))
    ok("in the reduced world the field keeps its authored light",
       not doc.get("sunArmed"),
       "the sun's writer was never armed: %s" % doc.get("sunArmed"))
    ok("in the reduced world the bearing still finds its slot",
       doc.get("ringArmed"),
       "the ring renders on the act the rail names, with no glide: %s" % doc.get("ringArmed"))


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
  // The writes are observed, not polled. The first instrument was a 10ms
  // setInterval comparing text, and under load - four browsers at once, or any
  // busy machine - the interval can slip past one of the fast clock's 40ms
  // steps, so two writes landed between two polls and read as ONE. A shortened
  // gap list failed the length equality the claim needs, on a page that was
  // behaving. A MutationObserver queues one record per mutation no matter how
  // long delivery waits - delivery is deferred, coalescing is not - so the
  // write COUNT is exact and contention can only bunch the timestamps, never
  // lose a write. Same claim, an instrument that cannot drop what it measures.
  const mo = new MutationObserver(function () {
    countChanges.push(Math.round(performance.now() - t0));
  });
  if (count) mo.observe(count, { characterData: true, childList: true, subtree: true });

  __APPROACH__
  await wait(2400);
  mo.disconnect();

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

# The M23 doctors' anchors, quoted from the page itself (Source/index.html and
# Source/styles.css). They are module constants rather than inline literals so a
# doctor's edit is reviewable against the exact text it patches; if the page's
# wording drifts, the doctor FAILS LOUDLY at self-test time (the patch's `old`
# text is not in the built file) rather than passing on stale anchors - which is
# the same contract the other families' doctors keep by declaring their page.
# M27 moved the dawn into the release callback, so the release is no longer the
# one-liner it was; the anchor is the remove line itself, which is the statement
# both M23 doctors mean to kill.
PAGE_RELEASE = "        heroField.classList.remove('is-cold');"
PAGE_COLD_LINE = "  .hero.is-cold .h1-reveal .h1-line { transform: translateY(118%); }"
PAGE_ARM_COND = "  if (heroField && !reduced) {"
PAGE_MASK_PAD = ("                   padding-block: 0.14em; margin-block: -0.14em; }")
PAGE_LEDE_D = "  .hero .lede        { transition-delay: calc(var(--arrive) * 560ms),"
PAGE_ANS7 = "  .hero .win .answer > *:nth-child(7) { animation: rise 520ms 1360ms var(--ease) both; }"

# M24's claim family and its doctors' anchors, quoted from the page itself, on
# the same contract as M23's: if the page's wording drifts, the doctor FAILS
# LOUDLY at self-test time rather than passing on a stale anchor. The reduced
# claim is spelled out so the self-test can drive only the reduced page for it.
CLOSE_CLAIMS = (
    "the close's cast arrives with the mark",
    "the cast arrives in order: mark, window, h2, paragraph, CTA",
    "a fast approach to the close compresses the clock, not the cast",
    "in the reduced world the close's cast is simply there",
)
CLOSE_REDUCED_CLAIMS = ("in the reduced world the close's cast is simply there",)
PAGE_CLOSE_RELEASE = ("      mark.classList.remove('is-cold');\n"
                      "      section.classList.remove('is-cold');")
PAGE_CLOSE_CAST = ("var cast = [mark, section.querySelector('.win'), section.querySelector('.body h2'),\n"
                   "                section.querySelector('.body p'), section.querySelector('.body .cta')];")
PAGE_CLOSE_QUICK = ("        mark.classList.add('is-quick');\n"
                    "        section.classList.add('is-quick');")
PAGE_CLOSE_ARM = ("  if (mark && !reduced && mark.getBoundingClientRect().top "
                  ">= window.innerHeight) {")

# M25's doctors' anchors, quoted from the page itself, on the same contract as
# M23's and M24's: a page whose wording drifts makes the doctor fail loudly at
# self-test time rather than passing on a stale anchor.
PAGE_SUN_ARM = ("if (!reduced && window.CSS && "
                "'registerProperty' in window.CSS) {")
PAGE_SUN_TX = "if (sun.s) sun.tx = (e.clientX / window.innerWidth) - 0.5;"

# M26's anchors, quoted from the page like every doctor's: a page whose script
# or stylesheet drifts fails loudly here rather than passing on a stale string.
PAGE_BEARING_WRITE = "if (k >= 0) actIndex.style.setProperty('--i', String(k));"
PAGE_BEARING_RING = "transform: translate(-50%, calc(-50% + var(--i, 0) * var(--pitch)));"
# M30 · the header's write, anchored the way the bearing's is: the whole loop
# the page uses to answer the header, so removing it removes the answer.
PAGE_HEADER_WRITE = """navLinks.forEach(function (a) {
          if (here && a.getAttribute('href') === here) a.setAttribute('aria-current', 'location');
          else a.removeAttribute('aria-current');
        });"""

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
    # M33 · the class without the rule, on the landing this time: the same
    # failure the library doctor above holds, in the place it had actually
    # shipped - the whole-SVG reveals sat fully drawn through their own cold
    # state because the M3 selectors named a .win or an .exhibit img and these
    # figures are neither. The patch drops the boundary selector; the dials'
    # claim still passes (its rule remains), so the doctor pins exactly the
    # rule that failed and nothing else.
    ("the landing's whole-SVG cold state dropped, so a waiting plate is visible",
     [(".boundary.is-cold .bnd,", "")],
     "the boundary plate arrives from its own cold state", ("index.html", "/")),
    ("the games dial's cold rule dropped, so the waiting plate is visible",
     [(".games-dial-fig.is-cold .games-plate,", "")],
     "the games dial arrives from its own cold state", ("index.html", "/")),
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
     [('dwellArm();\n      if (sun.s) {',
       'if (sun.s) {')],
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
    ("M23 · the release never happens",
     [(PAGE_RELEASE, "      /* doctor: the cold state is never released, so the words "
                "never arrive */")],
     "the hero's words arrive with the page"),
    ("M23 · a mask that shaves the descender",
     [(PAGE_MASK_PAD, "                   padding-block: 0em; margin-block: 0em; }")],
     "the mask leaves the lines room to breathe", ("index.html", "/")),
    ("M23 · a lede that arrives out of order",
     [(PAGE_LEDE_D, "  .hero .lede        { transition-delay: calc(var(--arrive) * 5000ms),")],
     "the arrival is ordered: line1, line2, lede, CTA, cue", ("index.html", "/")),
    # M43's own doctor: the plate's sequence slot dropped means the seventh
    # child sits painted from the first frame while the prose rises - exactly
    # the seam M2 closes. The claim reads the first-visible timestamp, which
    # the slotless page produces before the prose finishes.
    ("M43 · the answer plate lost its sequence slot",
     [(PAGE_ANS7, "")],
     "the cycles answer's plate arrives last, at rest", ("index.html", "/")),
    ("M23 · a cold state that never hides the line",
     [(PAGE_COLD_LINE, "  .hero.is-cold .h1-reveal .h1-line { transform: translateY(0%); }")],
     "is-cold hides the hero's arrival again"),
    ("M23 · the arm ignores reduced motion",
     [(PAGE_ARM_COND, "  if (heroField) {"), (PAGE_RELEASE, "        /* doctor: no release */")],
     "in the reduced world the hero never arms its arrival"),
    # M27's two. A hold that never releases dawns forever - the cold state's
    # light stays sunk on a page the reader is reading - and a depth term that
    # ignores the hold means the first scroll paints daylight before the cast
    # has arrived, which is the dawn silently not existing.
    ("M27 · the dawn never releases the hold",
     [("        sun.hold = false;", "        sun.hold = true;")],
     "and releases it on the cast's own clock"),
    ("M27 · the depth term ignores the hold",
     [("        sun.td = (sun.hold || heroField.classList.contains('is-cold'))",
       "        sun.td = false ?")],
     "the dawn holds the light sunk in the cold state"),
    # M24's four, each the failure of one of the close's claims. The cold class
    # goes on the section AND the mark, so the release that forgets the section
    # leaves the cast hidden forever, and the patch below removes both - the
    # mark's own ink claim is what catches a partial release the next time the
    # two classes drift apart.
    ("M24 · the close's cast is never released",
     [(PAGE_CLOSE_RELEASE, "          /* doctor: the cast is never released */")],
     CLOSE_CLAIMS[0]),
    ("M24 · a cast that arrives out of order",
     # Two slots of displacement minimum: a one-slot swap lands inside the
     # order claim's 40ms poll grace half the time, which makes a doctor that
     # only sometimes catches its claim worse than no doctor at all. win and
     # cta are three slots apart in the cast, so the swap is unmissable.
     [(PAGE_CLOSE_CAST,
       "var cast = [mark, section.querySelector('.body .cta'), "
       "section.querySelector('.body h2'),\n"
       "                section.querySelector('.body p'), "
       "section.querySelector('.win')];")],
     CLOSE_CLAIMS[1]),
    ("M24 · the quick clock never reaches the close",
     [(PAGE_CLOSE_QUICK,
       "            /* doctor: the quick clock is never applied on the close */")],
     CLOSE_CLAIMS[2]),
    ("M24 · the close arms in the reduced world",
     [(PAGE_CLOSE_ARM, "  if (mark) {")],
     CLOSE_REDUCED_CLAIMS[0]),
    # M25's two, each the failure of one of the sun's claims. The arm ignored
    # under reduce is the reduced claim's own failure; the lean that never
    # follows the pointer is the lean claim's.
    ("M25 · the sun's writer armed in the reduced world",
     [(PAGE_SUN_ARM, "if (window.CSS && 'registerProperty' in window.CSS) {")],
     "in the reduced world the field keeps its authored light"),
    ("M25 · the sun ignores the pointer",
     [(PAGE_SUN_TX, "if (sun.s) sun.tx = 0;")],
     "the field's light leans with the pointer"),
    # M26's two. A writer that never fires leaves the ring parked on the first
    # dot forever; a ring that ignores --i decorates the column without ever
    # following the reader. Each is the failure of one of the bearing's claims.
    ("M26 · the bearing never writes its index",
     [(PAGE_BEARING_WRITE, "if (k >= 0) actIndex.style.setProperty('--i', '0');")],
     "the bearing settles on the act the rail names"),
    ("M26 · the ring ignores the index it is given",
     [(PAGE_BEARING_RING, "transform: translate(-50%, -50%);")],
     "the bearing settles on the act the rail names"),
    # The reduced world's own doctor: a ring that no longer renders at its slot
    # is the one failure the reduced claim can see, and it is checked against
    # the reduced page, which costs its own browser load.
    ("M26 · the reduced ring stops rendering its slot",
     [(PAGE_BEARING_RING, "opacity: 0;")],
     "in the reduced world the bearing still finds its slot"),
    ("M30 · the header stops answering",
     [(PAGE_HEADER_WRITE, "/* the header no longer answers */")],
     "the header's links answer for the act they name"),
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
# The sun's reduced claim belongs here with the others: without it its doctor
# routed to the ordinary scenario, which cannot carry a reduced-world claim, and
# the doctored page passed the one run it was given. Found by the self-test's
# own verdict line, which is what the verdict line is for.
REDUCED_CLAIMS = ("in the reduced world nothing is written",
                  "in the reduced world the hero never arms its arrival",
                  "in the reduced world the field keeps its authored light",
                  "in the reduced world the bearing still finds its slot",)

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


def self_test(chrome, site, width, height, tmp, family="all", jobs=1) -> int:
    print("self-test: %d doctored pages, each of which must fail one named claim"
          % len(SELF_TESTS))
    worst = 0
    # Which family of page loads a patch has to pay for, so this can be run a third at
    # a time: it grew past ten minutes otherwise, and a self-test nobody runs because
    # it takes a quarter of an hour is a self-test that stops being evidence. The
    # family is read off the claim the patch is declared to break, so a new patch
    # cannot forget to declare one.
    lib_claims = LIB_CLAIMS + LIB_REDUCED_CLAIMS

    # JOBS. A doctor's cost is almost entirely the real-time wait inside its run()
    # call; the copy, the patch and the check are noise. And since every run() now
    # owns its Rig, its port, its profile and its broken copy, two doctors share
    # nothing - so the waits overlap freely at N concurrent browsers. The CHECKS
    # still run on the main thread, in the self-test's own order, so the output is
    # byte-for-byte what the serial run printed: parallel evidence, serial verdicts.
    # Caveat worth naming: the scenarios measure REAL time, so a machine that
    # cannot comfortably render N animations at once can make a timing claim flake.
    # A flake under --jobs reruns serial before it is believed.
    def prepare(i, entry):
        """Do everything up to and including the browser waits; return the check."""
        what, edits, expected = entry[0], entry[1], entry[2]
        rel, url = entry[3] if len(entry) > 3 else ("index.html", "/")
        in_lib = expected in lib_claims
        in_pace = expected in PACE_CLAIMS
        in_dwell = expected in DWELL_CLAIMS
        in_hero = expected in HERO_CLAIMS
        in_close = expected in CLOSE_CLAIMS
        in_sun_land = expected in ("the field's light leans with the pointer",
                                   "the field's light sinks as the reader descends",
                                   "and returns when the reader does")
        in_bearing_land = expected in ("the bearing rides the rail it marks",
                                       "the bearing settles on the act the rail names",
                                       "and hands back to the first act on the return")
        broken = os.path.join(tmp, "broken-%d" % i)
        if os.path.isdir(broken):
            shutil.rmtree(broken)
        shutil.copytree(site, broken)
        patched = os.path.join(broken, rel)
        if not os.path.isfile(patched):
            return ("fail", "%s: %s is not a file in the built site, so the self-test "
                    "is checking nothing" % (what, rel))
        html = open(patched, encoding="utf-8").read()
        missing = [old for old, _ in edits if old not in html]
        if missing:
            return ("fail", "%s: the text it patches is not in %s (%r), so the "
                    "self-test is checking nothing" % (what, rel, missing[0]))
        for old, new in edits:
            html = html.replace(old, new, 1)
        AC.write(patched, html)

        # Each patch is checked by the family its claim belongs to and no other; a
        # self-test that loads four browsers per patch to prove one thing is a
        # self-test nobody runs. A patch aimed at the wheel is not evidence about
        # the arrivals, and the reverse.
        if in_lib:
            if expected in LIB_REDUCED_CLAIMS:
                rlib = run(chrome, broken, tmp, url, width, height,
                           LIB_REDUCED_SCENARIO,
                           extra=["--force-prefers-reduced-motion"],
                           tag="st%d-lib-red" % i)
                return ("check", lambda f, rf: check_library_reduced(rlib, f))
            cdoc = run(chrome, broken, tmp, url, width, height, LIB_CALM,
                       extra=None, tag="st%d-lib-calm" % i)
            fdoc = run(chrome, broken, tmp, url, width, height, LIB_FAST,
                       extra=None, tag="st%d-lib-fast" % i)
            return ("check", lambda f, rf: check_library(cdoc, fdoc, f))
        if in_pace:
            cdoc = run(chrome, broken, tmp, "/", width, height, PACE_CALM,
                       extra=None, tag="st%d-calm" % i)
            fdoc = run(chrome, broken, tmp, "/", width, height, PACE_FAST,
                       extra=None, tag="st%d-fast" % i)
            return ("check", lambda f, rf: check_pace(cdoc, fdoc, f))
        if in_dwell:
            ddoc = run(chrome, broken, tmp, "/", width, height, DWELL_SCENARIO,
                       extra=None, tag="st%d-dwell" % i)
            return ("check", lambda f, rf: check_dwell(ddoc, f))
        if in_hero:
            hdoc = run(chrome, broken, tmp, "/", width, height, HERO_SCENARIO,
                       extra=None, tag="st%d-hero" % i)
            return ("check", lambda f, rf: check_hero(hdoc, f))
        if in_sun_land:
            sdoc = run(chrome, broken, tmp, "/", width, height, SCENARIO,
                       extra=None, tag="st%d-sun" % i)
            return ("check", lambda f, rf: check(sdoc, f))
        if in_bearing_land:
            bdoc = run(chrome, broken, tmp, "/", width, height, SCENARIO,
                       extra=None, tag="st%d-bearing" % i)
            return ("check", lambda f, rf: check(bdoc, f))
        if expected in CLOSE_REDUCED_CLAIMS:
            xred = run(chrome, broken, tmp, "/", width, height, CLOSE_CALM,
                       extra=["--force-prefers-reduced-motion"],
                       tag="st%d-close-red" % i)
            return ("check", lambda f, rf: check_close(xred, f, reduced=True))
        if in_close:
            xdoc = run(chrome, broken, tmp, "/", width, height, CLOSE_FAST,
                       extra=None, tag="st%d-close" % i)
            return ("check", lambda f, rf: check_close(xdoc, f, fast=True))
        if expected in REDUCED_CLAIMS:
            # Only the reduced page can carry this claim, so only it is driven: the
            # world run would cost a browser and could never report this failure.
            rdoc = run(chrome, broken, tmp, "/", width, height, REDUCED_SCENARIO,
                       extra=["--force-prefers-reduced-motion"], tag="st%d-reduced" % i)
            return ("check", lambda f, rf: check_reduced(rdoc, rf))
        doc = run(chrome, broken, tmp, "/", width, height, SCENARIO,
                  extra=None, tag="st%d" % i)
        return ("check", lambda f, rf: check(doc, f))

    live = [e for i, e in enumerate(SELF_TESTS)
            if not ((family == "lib" and e[2] not in lib_claims)
                    or (family == "pace" and e[2] not in PACE_CLAIMS)
                    or (family == "dwell" and e[2] not in DWELL_CLAIMS)
                    or (family == "hero" and e[2] not in HERO_CLAIMS)
                    or (family == "close" and e[2] not in CLOSE_CLAIMS
                        and e[2] not in CLOSE_REDUCED_CLAIMS)
                    or (family == "land" and (e[2] in lib_claims
                                              or e[2] in PACE_CLAIMS
                                              or e[2] in DWELL_CLAIMS
                                              or e[2] in HERO_CLAIMS
                                              or e[2] in CLOSE_CLAIMS
                                              or e[2] in CLOSE_REDUCED_CLAIMS)))]
    skip = len(SELF_TESTS) - len(live)
    indices = [i for i, e in enumerate(SELF_TESTS) if e in live]
    if jobs > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(lambda pair: prepare(pair[0], pair[1]),
                                    list(zip(indices, live))))
    else:
        results = [prepare(i, e) for i, e in zip(indices, live)]
    for entry, (kind, payload) in zip(live, results):
        what, expected = entry[0], entry[2]
        failures: list = []
        reduced_failures: list = []
        if kind == "fail":
            print("  FAIL  %s" % payload)
            worst = 1
            continue
        payload(failures, reduced_failures)
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
    ap.add_argument("--family", default="all",
                    choices=("all", "land", "hero", "close", "pace", "lib", "dwell"),
                    help="with --self-test, doctor only one family's pages: the landing's "
                         "world and reduced claims, the hero's arrival, the arrivals' "
                         "pacing pair, or the library's fold test and clock")
    ap.add_argument("--jobs", type=int, default=1,
                    help="how many pages to drive at once. Each run owns its own port, "
                         "browser profile and answer box, so the real-time waits overlap "
                         "freely; the checks stay on the main thread in the tool's own "
                         "order, so the output reads exactly as the serial run's. Every "
                         "scenario measures REAL time, so a flaky result under N>1 is "
                         "rerun serial before it is believed. 1 keeps the old behaviour.")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.site):
        print("error: %s is not a directory - run build-site.py first" % a.site,
              file=sys.stderr)
        return 1
    chrome = AC.find_chrome()
    tmp = tempfile.mkdtemp(prefix="istor-motion-")
    try:
        if a.self_test:
            return self_test(chrome, a.site, a.width, a.height, tmp, a.family, a.jobs)

        print("the mechanism, driven: %s at %dpx%s"
              % (a.site, a.width, "" if a.jobs == 1 else " (%d at a time)" % a.jobs))
        failures: list = []
        # With jobs > 1 the drives overlap: every run owns its port, profile and
        # answer box, so N browsers render N pages without sharing anything, and
        # the longest scenario - the 28s dwell - no longer gates the total. The
        # checks stay here, on the main thread, in this order, so the printed
        # claims and the failure list are exactly the serial run's.
        specs = [
            ("hdoc", "/", HERO_SCENARIO, None, "hero-arrival"),
            ("xdoc", "/", CLOSE_CALM, None, "close-calm"),
            ("xfd", "/", CLOSE_FAST, None, "close-fast"),
            ("xred", "/", CLOSE_CALM, ["--force-prefers-reduced-motion"], "close-reduced"),
            ("doc", "/", SCENARIO, None, "world"),
            ("rdoc", "/", REDUCED_SCENARIO, ["--force-prefers-reduced-motion"], "reduced"),
            ("cdoc", "/", PACE_CALM, None, "pace-calm"),
            ("fdoc", "/", PACE_FAST, None, "pace-fast"),
            ("wdoc", "/", DWELL_SCENARIO, None, "dwell"),
            ("lcalm", "/library/", LIB_CALM, None, "lib-calm"),
            ("lfast", "/library/", LIB_FAST, None, "lib-fast"),
            ("lred", "/library/", LIB_REDUCED_SCENARIO,
             ["--force-prefers-reduced-motion"], "lib-reduced"),
        ]
        docs: dict = {}
        if a.jobs > 1:
            from concurrent.futures import ThreadPoolExecutor
            def drive(spec):
                name, page, scenario, extra, tag = spec
                return name, run(chrome, a.site, tmp, page, a.width, a.height,
                                 scenario, extra=extra, tag=tag)
            with ThreadPoolExecutor(max_workers=a.jobs) as pool:
                for name, d in pool.map(drive, specs):
                    docs[name] = d
        else:
            for name, page, scenario, extra, tag in specs:
                docs[name] = run(chrome, a.site, tmp, page, a.width, a.height,
                                 scenario, extra=extra, tag=tag)
        hdoc, xdoc, xfd, xred = (docs[k] for k in ("hdoc", "xdoc", "xfd", "xred"))
        doc, rdoc, cdoc, fdoc, wdoc = (docs[k] for k in ("doc", "rdoc", "cdoc", "fdoc", "wdoc"))
        lcalm, lfast, lred = (docs[k] for k in ("lcalm", "lfast", "lred"))

        # M23 - the opening moment, driven. ~5.4s of real time, most of it the
        # courtesy of letting a re-armed cold state finish hiding.
        check_hero(hdoc, failures)
        # M24 - the close's arrival, driven on both clocks like the pacing pair,
        # plus its reduced run: the mark, the window, the prose and the CTA.
        check_close(xdoc, failures)
        check_close(xfd, failures, fast=True)
        check_close(xred, failures, reduced=True)
        check(doc, failures)
        check_reduced(rdoc, failures)
        check_pace(cdoc, fdoc, failures)
        # M22 - stillness, driven. A 28s scenario of mostly waiting, which is
        # the honest cost of measuring patience.
        check_dwell(wdoc, failures)
        # The library is a different page on a different pair of shared files, so it is
        # driven rather than inferred from the landing's behaviour: nothing about the
        # landing's arrivals would move if `/theme.js` lost its fold test.
        check_library(lcalm, lfast, failures)
        check_library_reduced(lred, failures)

        if a.json:
            with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"motion": doc, "reduced": rdoc, "calm": cdoc, "fast": fdoc,
                           "dwell": wdoc, "close": xdoc, "closeFast": xfd,
                           "closeReduced": xred,
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
              "the close's, the dwell and the library's, verified by driving the "
              "pages rather than by reading them (hero band %s of %s)"
              % (CHECKED[0], band, doc.get("viewport", "?")))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
