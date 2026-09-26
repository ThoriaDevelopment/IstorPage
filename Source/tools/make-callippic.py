#!/usr/bin/env python3
"""Generate the callippic plate: the sub-dial that keeps the calendar
from drifting, drawn as the page's own arithmetic.

    python Source/tools/make-callippic.py [--self-test]

Writes Source/figures/callippic-wide.svg and Source/figures/callippic-tall.svg.
Run from anywhere; paths are anchored to this file.

WHY THIS EXISTS. The page's cycles act names five cycles. Four of them are
drawn (Metonic spiral, games sub-dial, Saros spiral, exeligmos); the Callippic
is the one the prose names and no plate carried: "The Callippic cycle is a
76-year sub-dial on the upper rear dial of the Antikythera mechanism" (the
page's captured answer, source 4). The plate exists so a reader who has just
been shown the Metonic spiral's five turns can see what the fourth named cycle
adds, in the same grammar as its siblings.

THE ARITHMETIC, ALL FROM NUMBERS THE PAGE PRINTS. The Metonic paragraph says
19 tropical years; the captured answer says the Callippic is 76 years. 4 x 19
is 76 - four Metonic cycles are one Callippic - and that product is the
drawing: four turns of the Metonic, drawn at exact quarters (90 degrees each,
the dial's own geometry), with the product standing in the centre as the
plate's one claim, the way the exeligmos hub carries 8 + 8 + 8 = 24.

WHAT IS DELIBERATELY ABSENT. No reconstruction of the physical sub-dial's
appearance (no source on this page states what it looked like; the plate is
the cycle's arithmetic, not the dial's archaeology). No pointer position. No
month counts on the ring - the page prints 235 synodic lunar months for ONE
Metonic cycle, and the plate does not multiply a printed number into a
claim the page does not make.

SELF-TEST. Demands four exact 90-degree sectors (measured from the drawn
boundaries), the four-turn arithmetic verbatim ("one Metonic", "x 4",
"= 76 years"), the cycle line ("76 years · 4 turns of the Metonic"),
MEASURED covering every string, token inks only, and both variants asserting
the same dial.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# The cycle, from the page's printed numbers: the captured answer says
# "a 76-year sub-dial"; the Metonic paragraph says 19 tropical years.
# 4 x 19 = 76, and 4 is the number of turns the drawing makes.
YEARS = 76
TURNS = 4
SECTOR_DEG = 90.0

# The four-turn arithmetic, declared as the census reads it: the drawn
# strings. "one Metonic" is diagram grammar for the printed "Metonic cycle";
# "x 4" and "= 76 years" are the plate's derived arithmetic (76-year is
# printed prose; 4 is the number of turns the drawing itself makes).
ARITHMETIC = (("one Metonic", "cl-arith"), ("x 4", "cl-arith"),
              ("= 76 years", "cl-claim"))

# The cycle line, one drawn string, from the printed "76-year sub-dial" and
# the four turns the plate draws.
CYCLE_LINE = "76 years · 4 turns of the Metonic"

# Every drawn string's measured width in user units, keyed by string and
# size. Measured in the browser off the built page (Inter 500, canvas
# measureText), following the exeligmos plate's scale arithmetic: the wide
# plate renders at 0.944 in the field's 700px inset, so labels are 14 units
# (13.2px rendered, above the floor); the tall plate renders at 0.729 at a
# 320px phone, so its labels are 16.5 units to land at 12.0px.
MEASURED = {
    ("one Metonic", 14.0): 82.9, ("x 4", 14.0): 20.7,
    ("= 76 years", 14.0): 70.5,
    ("one Metonic", 16.5): 97.8, ("x 4", 16.5): 24.4,
    ("= 76 years", 16.5): 83.0,
    ("76 years · 4 turns of the Metonic", 14.0): 217.3,
    ("76 years · 4 turns of the Metonic", 16.5): 256.0,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


def pt(cx, cy, r, deg):
    """A point at `deg` from 12 o'clock, clockwise (the dial's own reading
    direction)."""
    a = math.radians(deg - 90.0)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def sector_path(cx, cy, r, a0, a1, inset=0.0):
    """One sector's boundary: two radii and the arc between them. `inset`
    pulls the radii's outer end back so the arc reads as divided rather
    than cut."""
    x0, y0 = pt(cx, cy, inset, a0)
    x1, y1 = pt(cx, cy, r, a0)
    x2, y2 = pt(cx, cy, r, a1)
    x3, y3 = pt(cx, cy, inset, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return ("M%.2f %.2f L%.2f %.2f A%.2f %.2f 0 %d 1 %.2f %.2f L%.2f %.2f"
            % (x0, y0, x1, y1, r, r, large, x2, y2, x3, y3))


def plate(wide):
    label_size = 14.0 if wide else 16.5
    if wide:
        W, H = 640, 320
        cx, cy, r_out = 300.0, 158.0, 112.0
    else:
        W, H = 340, 430
        cx, cy, r_out = 170.0, 142.0, 100.0
    # The hub holds the three arithmetic rows; the exeligmos plate's measured
    # ratios apply (its hub text carries the same three-row shape), scaled to
    # this plate: 0.41 wide / 0.53 tall put the ring clear of the contrast
    # audit's probe band and give the claim air.
    r_in = r_out * (0.53 if not wide else 0.41)
    r_label = (r_in + r_out) / 2.0

    g = []
    g.append('  <g class="cl-sectors">')
    for i in range(TURNS):
        a0 = i * SECTOR_DEG
        a1 = (i + 1) * SECTOR_DEG
        g.append('    <path class="cl-sector" d="%s"/>' %
                 sector_path(cx, cy, r_out, a0 + 1.5, a1 - 1.5, inset=r_in))
        # each turn's ordinal, mid-sector mid-radius: I II III IV, the dial's
        # own reading order - diagram grammar, declared in the self-test
        lx, ly = pt(cx, cy, r_label, a0 + SECTOR_DEG / 2.0)
        g.append('    <text class="cl-turn" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" text-anchor="middle">%s</text>'
                 % (lx, ly + label_size * 0.35, label_size, INTER,
                    ("I", "II", "III", "IV")[i]))
    g.append('    <circle class="cl-hub" cx="%.1f" cy="%.1f" r="%.1f"/>'
             % (cx, cy, r_in))
    g.append('  </g>')

    # the product, in the hub: the plate's one claim
    sub_factor = 0.85 if wide else 0.92
    hub_g = ['  <g class="cl-hubtext">']
    hy = cy - label_size * 1.1
    for text, cls in ARITHMETIC:
        size = label_size if cls == "cl-claim" else round(label_size * 0.85, 1)
        hub_g.append('    <text class="%s" x="%.1f" y="%.1f" font-size="%g" '
                     'font-family="%s" text-anchor="middle">%s</text>'
                     % (cls, cx, hy, size, INTER, text))
        hy += label_size * 1.25
    hub_g.append('  </g>')
    g.append("\n".join(hub_g))

    # the cycle line under the dial, from the printed "76-year sub-dial"
    cycle = ('  <text class="cl-cycle" x="%.1f" y="%.1f" font-size="%g" '
             'font-family="%s" text-anchor="middle">%s</text>'
             % (cx, cy + r_out + 30, label_size, INTER, CYCLE_LINE))
    g.append(cycle)

    variant = "wide" if wide else "tall"
    title = (
        "The Callippic sub-dial: four turns of the Metonic cycle are 76 "
        "years, the dial the prose names on the upper rear plate. Each turn "
        "is one Metonic cycle of 19 tropical years; the plate draws the "
        "four quarters and the product." if wide else
        "The Callippic sub-dial: four turns of the Metonic cycle are 76 "
        "years. Each quarter is one Metonic cycle.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="cl-plate cl-{variant}" role="img" focusable="false"
     aria-labelledby="cl-{variant}-title">
  <title id="cl-{variant}-title">{title}</title>
{chr(10).join(g)}</svg>
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

    for name, svg, cx, cy, r_out in (
            ("wide", build_wide(), 300.0, 158.0, 112.0),
            ("tall", build_tall(), 170.0, 142.0, 100.0)):
        check(name + ": four sectors",
              svg.count('class="cl-sector"') == 4)
        # sector boundaries: decode the arc endpoints, measure each sector's
        # angular span - exact quarters or the drawing lies about the cycle
        spans = []
        for m in re.finditer(r'cl-sector" d="M([\d.-]+) ([\d.-]+) '
                             r'L([\d.-]+) ([\d.-]+) A[\d.]+ [\d.]+ 0 (\d) 1 '
                             r'([\d.-]+) ([\d.-]+)', svg):
            x1, y1, x2, y2 = (float(m.group(i)) for i in (3, 4, 6, 7))
            a0 = math.degrees(math.atan2(y1 - cy, x1 - cx))
            a1 = math.degrees(math.atan2(y2 - cy, x2 - cx))
            spans.append((a1 - a0) % 360)
        check(name + ": sectors are exact quarters",
              len(spans) == 4 and all(abs(s - 87.0) < 0.6 for s in spans),
              "spans %s (87 = 90 minus the 1.5-degree gaps either side)"
              % [round(s, 1) for s in spans])
        # the four turn ordinals, verbatim, in the dial's order
        turns = re.findall(r'cl-turn" x="[\d.]+" y="[\d.]+" '
                           r'font-size="[\d.]+" font-family="[^"]*"[^>]*>'
                           r'([^<]+)</text>', svg)
        check(name + ": turn ordinals verbatim in order",
              turns == ["I", "II", "III", "IV"], str(turns))
        check(name + ": the four-turn product stands in the hub",
              all(t in svg for t in ("one Metonic", "x 4", "= 76 years")))
        check(name + ": the cycle line",
              "76 years" in svg and "4 turns of the Metonic" in svg)
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        want = {"11.9", "14"} if name == "wide" else {"14", "16.5"}
        check(name + ": labels at the plate's sizes",
              sizes == want, str(sizes))
        check(name + ": every string measured",
              all((s, sz) in MEASURED for s in
                  ("one Metonic", "x 4", "= 76 years")
                  for sz in (14.0, 16.5)))
        # no hex anywhere
        check(name + ": no hex colour",
              not re.findall(r"#[0-9a-fA-F]{3,8}\b", svg))

    if worst == 0:
        print("callippic self-test ok: quarters measured, ordinals verbatim, "
              "hub product, cycle line, token inks, both variants")
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("callippic-wide.svg", build_wide()),
                       ("callippic-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
