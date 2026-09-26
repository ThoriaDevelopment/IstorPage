#!/usr/bin/env python3
"""Generate the unverified-mark plate: what the answer does with a fitted citation.

    python Source/tools/make-unverified.py [--self-test]

Writes Source/figures/unverified-wide.svg and Source/figures/unverified-tall.svg.

STATUS, 2026-09-26: wired and committed (M47). Include rows in build-site.py
(unverified-wide / unverified-tall), the verify-figures.py row, the markup at
the end of act 3 (#the-passage) as a .field.is-inset inset after the exhibit,
and the 14d11 CSS block in Source/styles.css. See M47 in
.improvement/OVERNIGHT_LOG.md.

WHY THIS EXISTS. The survey that picked this plate read every act of the main
page against its drawings: hero (gears, ring, pin-and-slot), gate act (gate),
passage act (NOTHING but the exhibit capture), reading log (DOM), dispute
(DOM), privacy (captures), library (captures, shelf), stop (ring), evidence
(six plates), questions (boundary), name (etymology). Act 3's prose names an
object no capture shows and no plate draws: "Istor sends the small model to
fit a citation quickly, and marks what it fitted: Unverified, check the
source." The citation chip and the passage card are drawn (the citation
anatomy on the library pages, the exhibit-11 capture here); the MARK - the
app's honest label for work it has not finished - is named twice and drawn
nowhere. This plate draws it.

THE DRAWING'S ONE CLAIM is stated by the act itself: "That word is not a
guess about truth." So the mark is not drawn as a stamp or a verdict; it is
drawn as a node in the same flow grammar as the gate plate, carrying the
page's exact two words, and the line that leaves it is the one thing drawn
dashed: the citation it fitted, open until "the passage behind the claim"
closes it. The mark does not end the answer's claim; it points past it.

EVERY LABEL IS A PHRASE THE PAGE ALREADY PRINTS, transcribed verbatim:
"the small model" (gate act and here: "sends the small model"),
"fit a citation" (the act's "to fit a citation quickly"),
"Unverified," and "check the source." (the act's own mark, comma and
full stop included, exactly as the strong element prints it),
"a good answer" (the act's own phrase, the answer whose citation is
fitted: "Sometimes the model writes a good answer and forgets to cite as
it goes"),
"the passage behind the claim" (act 3's caption: "the passage behind the
claim"), "does not end" (the drawing's dashed-edge label - the act's figure
of speech: the plate draws what the prose says is open as open), and the
caption line "That word is not a guess about truth." (the act, verbatim).
Nothing is invented; the drawing is arithmetic on the act's own words.

INKS. The rear-dials family, like the gate: structure --ink-3 on paper, text
--ink/--ink-2, and the mark's node and label in --coral - the page's
unverified ink elsewhere (the citation anatomy draws the invented locator's
field in red; the mark here is that red given its node). The coral is the
plate's single accent, on the one thing the act is about. The dashed edge is
NOT coral: the open citation is structure, not alarm - the mark is the
alarm, and it is already red.

TWO VARIANTS, the house rule. Wide 640 units in a 700px field (~0.944
scale), tall 340 units at phone width (0.729 scale at 320px), so the base
sizes are 12.5 / 16.5 units and the rendered floor holds at 11px+ at the
worst widths of each. The tall variant is a different composition (the flow
stacks downward), not a scaled one. The caption and the act's verbatim
sentence set the tall plate's minimum width; the self-test proves the fit.

THE LAYOUT IS DERIVED. Nodes are boxes sized from MEASURED string widths
(browser, Inter 500); the plate height follows the tall plate's stacked
flow; the dashed edge is the gap after the mark, so the drawing cannot
accidentally end the line it says does not end.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# Measured widths, browser, Inter 500, 2026-09-26 (localhost:8123 canvas,
# variable Inter loaded from the page's own woff2). The generator refuses an
# unmeasured string: a guessed width would be a node that clips its label.
MEASURED = {
    ("the small model", 12.5): 93.9, ("the small model", 16.5): 123.9,
    ("fit a citation", 12.5): 70.2, ("fit a citation", 16.5): 92.7,
    ("Unverified,", 12.5): 65.7, ("Unverified,", 16.5): 86.8,
    ("check the source.", 12.5): 106.8, ("check the source.", 16.5): 141.0,
    ("a good answer", 12.5): 88.0, ("a good answer", 16.5): 116.2,
    ("the passage behind the claim", 12.5): 174.9,
    ("the passage behind the claim", 16.5): 230.8,
    ("does not end", 12.5): 77.9, ("does not end", 16.5): 102.9,
    ("That word is not a guess about truth.", 12.5): 219.1,
    ("That word is not a guess about truth.", 16.5): 289.2,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured string %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


PAD = 12.0        # node padding, one side
LINE_H = 1.45     # node line height factor
GAP_W = 32.0      # wide: horizontal gap between nodes
GAP_H = 44.0      # tall: vertical gap between nodes


def node_w(lines, size):
    return max(tw(t, size) for t in lines) + PAD * 2


def node_h(lines, size):
    return PAD * 2 + len(lines) * size * LINE_H


def box(x, y, lines, cls, size):
    w = node_w(lines, size)
    h = node_h(lines, size)
    g = ['  <g class="uv" data-x="%g" data-y="%g" data-w="%g" data-h="%g">'
         % (x, y, w, h)]
    g.append('    <rect class="uv-box %s" x="%g" y="%g" width="%g" '
             'height="%g" rx="6"/>' % (cls, x, y, w, h))
    ty = y + PAD + size * 0.34
    for i, t in enumerate(lines):
        g.append('    <text class="uv-t %s" x="%g" y="%g" font-size="%g" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (cls, x + w / 2.0, ty + i * size * LINE_H, size, INTER, t))
    g.append('  </g>')
    return "\n".join(g) + "\n", w, h


def edge(x1, y1, x2, y2, dashed=False):
    cls = "uv-edge uv-dashed" if dashed else "uv-edge"
    return '  <path class="%s" d="M%g %g L%g %g"/>' % (cls, x1, y1, x2, y2)


def plate(wide):
    size = 12.5 if wide else 16.5
    W = 640.0 if wide else 340.0

    if wide:
        # Row one, left to right: the small model -> the mark -> the answer's
        # claim, the mark sitting ON the claim as it does in the app. Row two,
        # centred: the passage behind the claim, reached by the plate's one
        # dashed edge - the fitted citation, drawn open between the two places
        # the act says it joins. The wide plate is a different composition,
        # not a scaled row: "the passage behind the claim" is the plate's
        # widest string and would not fit four boxes on one 640-unit line.
        H = 252.0
        n1 = ["the small model", "fit a citation"]
        mk = ["Unverified,", "check the source."]
        n3 = ["a good answer"]
        n4 = ["the passage behind the claim"]
        widths = [node_w(n, size) for n in (n1, mk, n3)]
        x = (W - sum(widths) - GAP_W * 2) / 2.0
        mid_y = 12.0
        g1, w1, h1 = box(x, mid_y, n1, "uv-plain", size)
        n1_end = x + w1
        mark_x = x + w1 + GAP_W
        gm, wm, hm = box(mark_x, mid_y, mk, "uv-coral", size)
        n3_x = mark_x + wm + GAP_W
        h3 = node_h(n3, size)
        y3 = mid_y + (hm - h3) / 2.0
        g3, w3, _ = box(n3_x, y3, n3, "uv-plain", size)
        n3_end = n3_x + w3
        n4_x = (W - node_w(n4, size)) / 2.0
        y4 = mid_y + hm + GAP_H
        h4 = node_h(n4, size)
        g4, w4, _ = box(n4_x, y4, n4, "uv-plain", size)
        H = y4 + h4 + 52.0
        e_mid = mid_y + hm / 2.0
        # the dashed edge: out of the claim's foot, over to the passage's
        # top - two different places, the same line the citation is
        edges = (
            edge(n1_end, e_mid, mark_x, e_mid),
            edge(mark_x + wm, e_mid, n3_x, e_mid),
            '  <path class="uv-edge uv-dashed" d="M%g %g C%g %g %g %g %g %g"'
            % (n3_x + w3 / 2.0, y3 + h3,
               n3_x + w3 / 2.0, y3 + h3 + 22.0,
               n4_x + w4 / 2.0 + 24.0, y4 - 22.0,
               n4_x + w4 / 2.0, y4),
        )
        # "does not end" rides to the right of the dashed bend, clear of
        # both boxes
        elabel = ('  <text class="uv-elabel" x="%g" y="%g" font-size="%g" '
                  'font-family="%s" text-anchor="start">does not end</text>'
                  % (n4_x + w4 + 10.0, (mid_y + hm + y4) / 2.0 + size * 0.35,
                     size, INTER))
        body = g1 + gm + g3 + g4
    else:
        n1 = ["the small model", "fit a citation"]
        mk = ["Unverified,", "check the source."]
        n3 = ["a good answer"]
        n4 = ["the passage behind the claim"]
        x1 = (W - node_w(n1, size)) / 2.0
        y1 = 6.0
        g1, w1, h1 = box(x1, y1, n1, "uv-plain", size)
        xm = (W - node_w(mk, size)) / 2.0
        ym = y1 + h1 + GAP_H
        gm, wm, hm = box(xm, ym, mk, "uv-coral", size)
        x3 = (W - node_w(n3, size)) / 2.0
        y3 = ym + hm + GAP_H
        g3, w3, h3 = box(x3, y3, n3, "uv-plain", size)
        x4 = (W - node_w(n4, size)) / 2.0
        y4 = y3 + h3 + GAP_H
        g4, w4, h4 = box(x4, y4, n4, "uv-plain", size)
        H = y4 + h4 + 78.0
        e_mid1 = y1 + h1 / 2.0
        e_midm = ym + hm / 2.0
        e_mid3 = y3 + h3 / 2.0
        edges = (
            edge(x1 + w1, e_mid1, xm, e_midm),
            edge(xm + wm / 2.0, ym + hm, x3 + w3 / 2.0, y3),
            edge(x3 + w3 / 2.0, y3 + h3, x4 + w4 / 2.0, y4, dashed=True),
        )
        # beside the dashed edge, to its right where nothing is drawn
        elabel = ('  <text class="uv-elabel" x="%g" y="%g" font-size="%g" '
                  'font-family="%s" text-anchor="start">does not end</text>'
                  % (W / 2.0 + 12.0, (y3 + h3 + y4) / 2.0 + size * 0.35,
                     size, INTER))
        body = g1 + gm + g3 + g4

    cap = ('  <text class="uv-cap" x="%g" y="%g" font-size="%g" '
           'font-family="%s" text-anchor="middle">'
           'That word is not a guess about truth.</text>'
           % (W / 2.0, H - 10.0, size, INTER))

    variant = "wide" if wide else "tall"
    title = (
        "The unverified mark, drawn: the small model fits a citation, the "
        "answer carries the mark, and the dotted line from the claim does "
        "not end until the passage behind the claim closes it." if wide else
        "The unverified mark, drawn: the small model fits a citation, and "
        "the answer carries the mark until the passage closes it.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}"
     class="uv-plate uv-{variant}" role="img" focusable="false"
     aria-labelledby="uv-{variant}-title">
  <title id="uv-{variant}-title">{title}</title>
{chr(10).join(edges)}
{elabel}
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

    labels = ("the small model", "fit a citation", "Unverified,",
              "check the source.", "a good answer",
              "the passage behind the claim", "does not end",
              "That word is not a guess about truth.")
    for name, svg, wide in (("wide", build_wide(), True),
                            ("tall", build_tall(), False)):
        size = 12.5 if wide else 16.5
        W = 640.0 if wide else 340.0
        H = 250.0 if wide else None
        check(name + ": every label verbatim",
              all(">%s<" % t in svg for t in labels),
              str([t for t in labels if ">%s<" % t not in svg][:2]))
        check(name + ": four nodes",
              svg.count('class="uv-box') == 4)
        check(name + ": the mark is the one coral node",
              svg.count('uv-box uv-coral') == 1)
        check(name + ": exactly one dashed edge, after the mark",
              svg.count('class="uv-edge uv-dashed"') == 1
              and svg.count('class="uv-edge"') == 2)
        # nodes sized from MEASURED: no text wider than its node's box
        bad = []
        for m in re.finditer(
                r'<g class="uv" data-x="(-?[\d.]+)" data-y="(-?[\d.]+)" '
                r'data-w="([\d.]+)" data-h="([\d.]+)">(.*?)</g>', svg, re.S):
            x, y, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
            for t in re.findall(r'>([^<]+)</text>', m.group(5)):
                if tw(t, size) > w - PAD * 2 + 0.5:
                    bad.append(t[:30])
        check(name + ": every label inside its node", not bad, str(bad[:2]))
        # no node outside the plate; the caption fits its width
        off = []
        for m in re.finditer(
                r'data-x="(-?[\d.]+)" data-y="(-?[\d.]+)" data-w="([\d.]+)" '
                r'data-h="([\d.]+)"', svg):
            x, y, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
            if x < 0 or y < 0 or x + w > W or (H and y + h > H):
                off.append((x, y, w, h))
        cap_w = tw("That word is not a guess about truth.", size)
        if cap_w > W - 8:
            off.append(("caption", cap_w, W))
        check(name + ": every node and the caption inside the plate",
              not off, str(off[:1]))
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        check(name + ": one label size", sizes == {"%g" % size}, str(sizes))
        check(name + ": every string measured",
              all((t, size) in MEASURED for t in labels))
        check(name + ": titled for the reader",
              'aria-labelledby="uv-%s-title"' % name in svg
              and "<title" in svg)

    if worst == 0:
        print("unverified self-test ok: labels verbatim, mark coral and one, "
              "one dashed edge after it, nodes fitted, token inks, both "
              "variants")
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("unverified-wide.svg", build_wide()),
                       ("unverified-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
