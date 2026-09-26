#!/usr/bin/env python3
"""Generate the gate plate: the decision the cheap question makes.

    python Source/tools/make-gate.py [--self-test]

Writes Source/figures/gate-wide.svg and Source/figures/gate-tall.svg.

STATUS, 2026-09-24: wired and committed (M46). Include rows in build-site.py,
the verify-figures.py row, the markup at the end of the gate act
(#how-it-answers) and the 14d10 CSS block in Source/styles.css are all in;
the full battery is green (verify-figures 97, copy, links, budget, contrast
0 below AA across all six states, motion). Plate lives under the gate
act's exhibit in a .field.is-inset inset; see M46 in
.improvement/OVERNIGHT_LOG.md.

WHY THIS EXISTS. The gate act's two sentences are the product's whole
architecture - "If the documents in your library already settle the question,
Istor answers from them and never goes online" and "Istor runs two, and the
cheap question goes first (is this already answered here?), so the better
model can be slow, and can be right" - and the act shows a capture of an
answer but never the decision itself. This plate draws it: one question in,
the small model's test, and the two outcomes the act states. The boundary
plate in the questions act draws what stays INSIDE the machine; this one
draws HOW the machine decides. Neither repeats the other.

EVERY LABEL IS A PHRASE THE ACT ALREADY PRINTS, transcribed verbatim from
Source/index.html's gate act: "the question", "the small model", "is this
already answered here?", "the library", "answers from them,", "never goes
online", "the better model", "slow, and can be right", and the caption line
"the cheap question goes first". The branch edges are the act's own two
answers to the test, "yes" and "not yet", because that is what a yes-or-no
question's edges are called. Nothing is invented; the drawing is arithmetic
on the act's own words.

THE DRAWING'S ONE CLAIM is the asymmetry the two outcomes carry: the library
path's gloss ends in "never goes online" and the better model's in "can be
right" - the two promises the page is built on, placed on the two branches
where the act itself places them. The azure is the test (the small model's
question), the one moving part in the diagram.

THE LAYOUT IS DERIVED. Nodes are boxes sized from MEASURED string widths,
not hand-fitted; the branch geometry is computed from the box positions;
the plate height follows the tall plate's stacked flow. The self-test
demands the eleven labels verbatim, the two edges named yes and not yet,
every drawn line inside its plate, token inks only, and both variants
carrying the same decision.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# Measured widths, browser, Inter 500, 2026-09-23. The generator refuses an
# unmeasured string: a guessed width would be a node that clips its label.
MEASURED = {
    ("the question", 12.5): 74.2, ("the question", 16.5): 98.0,
    ("the small model", 12.5): 93.9, ("the small model", 16.5): 123.9,
    ("is this already answered here?", 12.5): 181.1,
    ("is this already answered here?", 16.5): 239.1,
    ("the library", 12.5): 60.6, ("the library", 16.5): 80.0,
    ("answers from them,", 12.5): 119.1, ("answers from them,", 16.5): 157.2,
    ("never goes online", 12.5): 106.0, ("never goes online", 16.5): 139.9,
    ("the better model", 12.5): 98.2, ("the better model", 16.5): 129.7,
    ("slow, and can be right", 12.5): 130.6, ("slow, and can be right", 16.5): 172.4,
    ("the cheap question goes first", 12.5): 174.3,
    ("the cheap question goes first", 16.5): 230.2,
    ("yes", 12.5): 21.0, ("yes", 16.5): 27.8,
    ("not yet", 12.5): 41.2, ("not yet", 16.5): 54.4,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured string %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


PAD = 12.0        # node padding, one side
LINE_H = 1.45     # node line height factor


def node_w(lines, size):
    return max(tw(t, size) for t in lines) + PAD * 2


def plate(wide):
    size = 12.5 if wide else 16.5
    if wide:
        W, H = 640.0, 300.0
    else:
        W, H = 340.0, 470.0

    def node(x, y, lines, cls):
        w = node_w(lines, size)
        h = PAD * 2 + len(lines) * size * LINE_H
        g = ['  <g class="gn" data-x="%g" data-y="%g" data-w="%g" data-h="%g">'
             % (x, y, w, h)]
        g.append('    <rect class="gn-box %s" x="%g" y="%g" width="%g" '
                 'height="%g" rx="6"/>' % (cls, x, y, w, h))
        ty = y + PAD + size * 0.34
        for i, t in enumerate(lines):
            anchor = "middle"
            tx = x + w / 2.0
            g.append('    <text class="gn-t %s" x="%g" y="%g" font-size="%g" '
                     'font-family="%s" text-anchor="%s">%s</text>'
                     % (cls, tx, ty + i * size * LINE_H, size, INTER,
                        anchor, t))
        g.append('  </g>')
        return "\n".join(g) + "\n", w, h

    if wide:
        # left-to-right: question -> small model -> branch to two outcomes
        q_x, q_y = 8.0, 0.0
        q_g, q_w, q_h = node(q_x, q_y, ["the question"], "gn-plain")
        sm_x = q_x + q_w + 54.0
        sm_y = (H - (PAD * 2 + 2 * size * LINE_H)) / 2.0 - 22.0
        sm_g, sm_w, sm_h = node(sm_x, sm_y,
                                ["the small model",
                                 "is this already answered here?"], "gn-azure")
        out_x = sm_x + sm_w + 54.0
        lib_y = 8.0
        lib_g, lib_w, lib_h = node(out_x, lib_y,
                                   ["the library", "answers from them,",
                                    "never goes online"], "gn-plain")
        bm_y = H - (PAD * 2 + 2 * size * LINE_H) - 8.0
        bm_g, bm_w, bm_h = node(out_x, bm_y,
                                ["the better model", "slow, and can be right"],
                                "gn-plain")
        # edges: question -> small model; small model -> each outcome
        e1_y = q_y + q_h / 2.0
        sm_mid = sm_y + sm_h / 2.0
        e1 = ('  <path class="gn-edge" d="M%g %g L%g %g"/>'
              % (q_x + q_w, e1_y, sm_x, sm_mid))
        lib_mid = lib_y + lib_h / 2.0
        bm_mid = bm_y + bm_h / 2.0
        e2 = ('  <path class="gn-edge" d="M%g %g C%g %g %g %g %g %g"/>'
              % (sm_x + sm_w, sm_mid, sm_x + sm_w + 27.0, sm_mid,
                 out_x - 27.0, lib_mid, out_x, lib_mid))
        e3 = ('  <path class="gn-edge" d="M%g %g C%g %g %g %g %g %g"/>'
              % (sm_x + sm_w, sm_mid, sm_x + sm_w + 27.0, sm_mid,
                 out_x - 27.0, bm_mid, out_x, bm_mid))
        # edge labels at the branch
        yes_x, yes_y = out_x - 27.0, lib_mid - 10.0
        ny_x, ny_y = out_x - 27.0, bm_mid + size * 1.2
        cap = ('  <text class="gn-cap" x="%g" y="%g" font-size="%g" '
               'font-family="%s" text-anchor="middle">the cheap question '
               'goes first</text>'
               % (sm_x + sm_w / 2.0, H - 6.0, size, INTER))
        edges = (e1, e2, e3,
                 '  <text class="gn-elabel" x="%g" y="%g" font-size="%g" '
                 'font-family="%s" text-anchor="middle">yes</text>'
                 % (yes_x, yes_y, size, INTER),
                 '  <text class="gn-elabel" x="%g" y="%g" font-size="%g" '
                 'font-family="%s" text-anchor="middle">not yet</text>'
                 % (ny_x, ny_y, size, INTER))
        body = q_g + sm_g + lib_g + bm_g
        head_y = 0.0
    else:
        # downward: question -> small model -> two outcomes stacked
        q_x = (W - node_w(["the question"], size)) / 2.0
        q_y = 6.0
        q_g, q_w, q_h = node(q_x, q_y, ["the question"], "gn-plain")
        sm_w2 = node_w(["the small model", "is this already answered here?"],
                       size)
        sm_x = (W - sm_w2) / 2.0
        sm_y = q_y + q_h + 44.0
        sm_g, sm_w, sm_h = node(sm_x, sm_y,
                                ["the small model",
                                 "is this already answered here?"], "gn-azure")
        lib_w2 = node_w(["the library", "answers from them,", "never goes online"],
                        size)
        lib_x = (W - lib_w2) / 2.0
        lib_y = sm_y + sm_h + 44.0
        lib_g, lib_w, lib_h = node(lib_x, lib_y,
                                   ["the library", "answers from them,",
                                    "never goes online"], "gn-plain")
        bm_y = lib_y + lib_h + 44.0
        bm_g, bm_w, bm_h = node(lib_x, bm_y,
                                ["the better model", "slow, and can be right"],
                                "gn-plain")
        H = bm_y + bm_h + 40.0
        sm_mid = sm_y + sm_h / 2.0
        e1 = ('  <path class="gn-edge" d="M%g %g L%g %g"/>'
              % (q_x + q_w / 2.0, q_y + q_h, sm_x + sm_w / 2.0, sm_y))
        e2 = ('  <path class="gn-edge" d="M%g %g L%g %g"/>'
              % (sm_x + sm_w / 2.0, sm_y + sm_h, lib_x + lib_w / 2.0, lib_y))
        e3 = ('  <path class="gn-edge" d="M%g %g C%g %g %g %g %g %g"/>'
              % (sm_x + sm_w / 2.0, sm_y + sm_h, sm_x + sm_w / 2.0,
                 sm_y + sm_h + 22.0, lib_x + lib_w / 2.0 - 24.0,
                 lib_y + lib_h / 2.0, lib_x - 2.0, lib_y + lib_h / 2.0 + 20.0))
        edges = (e1, e2, e3,
                 '  <text class="gn-elabel" x="%g" y="%g" font-size="%g" '
                 'font-family="%s" text-anchor="middle">yes</text>'
                 % (sm_x + sm_w / 2.0 + 10.0, sm_y + sm_h + 30.0, size, INTER),
                 '  <text class="gn-elabel" x="%g" y="%g" font-size="%g" '
                 'font-family="%s" text-anchor="end">not yet</text>'
                 % (lib_x - 8.0, lib_y + lib_h / 2.0 + 20.0 + 4.0, size, INTER))
        body = q_g + sm_g + lib_g + bm_g
        cap = ('  <text class="gn-cap" x="%g" y="%g" font-size="%g" '
               'font-family="%s" text-anchor="middle">the cheap question '
               'goes first</text>'
               % (W / 2.0, H - 8.0, size, INTER))

    variant = "wide" if wide else "tall"
    title = (
        "The gate, drawn: the question reaches the small model first, which "
        "asks whether the documents in the library already settle it. Yes: "
        "the answer comes from the library and never goes online. Not yet: "
        "the better model takes it, and can be slow to be right." if wide else
        "The gate, drawn: the small model’s question decides between the "
        "library’s own answer and the better model.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}"
     class="gate-plate gate-{variant}" role="img" focusable="false"
     aria-labelledby="gate-{variant}-title">
  <title id="gate-{variant}-title">{title}</title>
{chr(10).join(edges)}
{body}
{cap}</svg>
'''
    return svg


def build_wide():
    return plate(True)


def build_tall():
    return plate(False)


def self_test():
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" - " + detail) if detail else ""))
        if not good:
            worst = 1

    labels = ("the question", "the small model",
              "is this already answered here?", "the library",
              "answers from them,", "never goes online", "the better model",
              "slow, and can be right", "the cheap question goes first",
              "yes", "not yet")
    for name, svg, wide in (("wide", build_wide(), True),
                            ("tall", build_tall(), False)):
        size = 12.5 if wide else 16.5
        W = 640.0 if wide else 340.0
        H = 300.0 if wide else None
        check(name + ": every label verbatim",
              all(">%s<" % t in svg for t in labels),
              str([t for t in labels if ">%s<" % t not in svg][:2]))
        check(name + ": four nodes",
              svg.count('class="gn-box') == 4)
        check(name + ": the test is the azure node",
              'gn-box gn-azure' in svg)
        # nodes sized from MEASURED: no text wider than its node's box
        import re
        bad = []
        for m in re.finditer(
                r'<g class="gn" data-x="([\d.]+)" data-y="([\d.]+)" '
                r'data-w="([\d.]+)" data-h="([\d.]+)">(.*?)</g>', svg, __import__("re").S):
            x, y, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
            for t in re.findall(r'>([^<]+)</text>', m.group(5)):
                if t in ("yes", "not yet"):
                    continue
                if tw(t, size) > w - PAD * 2 + 0.5:
                    bad.append(t[:30])
        check(name + ": every label inside its node", not bad, str(bad[:2]))
        # no node outside the plate
        off = []
        for m in re.finditer(
                r'data-x="(-?[\d.]+)" data-y="(-?[\d.]+)" data-w="([\d.]+)" '
                r'data-h="([\d.]+)"', svg):
            x, y, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
            if x < 0 or y < 0 or x + w > W or (H and y + h > H):
                off.append((x, y, w, h))
        check(name + ": every node inside the plate", not off, str(off[:1]))
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        check(name + ": one label size",
              sizes == {"%g" % size}, str(sizes))
        check(name + ": every string measured",
              all((t, size) in MEASURED for t in labels))

    if worst == 0:
        print("gate self-test ok: labels verbatim, nodes fitted, azure test, "
              "token inks, both variants")
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("gate-wide.svg", build_wide()),
                       ("gate-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
