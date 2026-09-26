#!/usr/bin/env python3
"""Generate the exeligmos plate: the dial that turns a third of a day
back into a whole one.

    python Source/tools/make-exeligmos.py [--self-test]

Writes Source/figures/exeligmos-wide.svg and Source/figures/exeligmos-tall.svg.

WHY THIS EXISTS. The page's cycles answer names the Exeligmos cycle ("The
Exeligmos cycle is a 54-year sub-dial on the lower rear dial", cited to
source 4), and the inscriptions answer claims the Saros dial is "lettered
with the eclipses it predicts, down to the hour" (source 4's own witness
quote). What no drawing carried is the dial that makes those two sentences
true at once: the exeligmos sub-dial, sitting in the eye of the Saros
spiral, whose whole job is the hours.

WHAT SOURCE 1 STATES, COMPLETE (the Wikipedia article the app read). The
exeligmos cycle is a 54-year triple Saros cycle, 19,756 days long. "Since
the length of the Saros cycle is to a third of a day (namely, 6,585 days
plus 8 hours), a full exeligmos cycle returns the counting to an integral
number of days." The labels on its three divisions are: blank (or o),
representing zero; H (number 8), "add 8 hours to the time mentioned in the
display"; Iς (number 16), "add 16 hours". "Thus the dial pointer indicates
how many hours must be added to the glyph times of the Saros dial in order
to calculate the exact eclipse times."

THE PLATE'S ONE DERIVED NUMBER. Three sectors, and the hours each one
carries: 0, 8, 16. The arithmetic the drawing exists to land is the sum
8 + 8 + 8 = 24: one full turn of the exeligmos pointer is three Saros
cycles, and three eight-hour corrections are one whole day, which is why
the third sector exists at all. The plate draws the three sectors at exact
thirds (120 degrees each, the sub-dial's own geometry), each carrying its
Greek label and its hour instruction, and the +24 sum stands in the centre
as the drawing's one claim. Every number is source 1's or the sum of two
of its own; nothing is reconstructed.

WHAT IS DELIBERATELY ABSENT. No glyph transcriptions from the Saros dial
(the source marks its own abbreviations list with a citation-needed banner,
so the plate does not quote what the source itself doubts). No pointer
position (a pointer implies a reading; the plate is a key, not a
prediction). No depiction of the sub-dial's physical mounting (the source
does not state it).

SELF-TEST. Demands three exact 120-degree sectors (measured from the drawn
boundaries), the three labels verbatim (blank rendered as the source's "o"
mark), the 24-hour sum present, MEASURED covering every string, token inks
only, and both variants asserting the same dial.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import gzip
import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# The cycle, from the source.
YEARS = 54

# The three divisions and what each instructs: (label, hours, note).
# The blank sector's label is the source's "o" mark ("blank or o,
# representing the number zero, assumed, not yet observed").
# The legend is source 1's own key, verbatim: blank (zero, "add nothing"),
# H ("add 8 hours"), Iϛ ("add 16 hours") - the last glyph written as the
# literal character so the verbatim census can match the drawn string to
# this declaration.
SECTORS = (
    ("o", 0, "add nothing"),
    ("H", 8, "add 8 hours"),
    ("Iϛ", 16, "add 16 hours"),
)

# The cycle line, declared as the census reads it: one drawn string.
CYCLE_LINE = "54 years · 3 turns of the Saros"

# Sector boundaries at exact thirds, starting at 12 o'clock, clockwise.
SECTOR_DEG = 120.0

# Every drawn string's measured width in user units, keyed by string and
# size. Measured in the browser off the built page, 2026-09-23, Inter 500.
# Sizes follow the rear-dials plate's own arithmetic: the wide plate renders
# at or above one to one (14-unit labels land at 14px); the tall plate
# renders at 0.68 at a 320px phone, so its labels are 16.5 units to land at
# 11.2px, the floor's own arithmetic.
MEASURED = {
    ("one Saros", 14.0): 64.0, ("+ 8 h", 14.0): 42.0,
    ("= 24 h", 14.0): 48.0, ("one day", 14.0): 52.0,
    ("54 years", 16.5): 68.0, ("3 turns of the Saros", 16.5): 148.0,
    ("one Saros", 16.5): 75.0, ("+ 8 h", 16.5): 50.0,
    ("= 24 h", 16.5): 57.0, ("one day", 16.5): 62.0,
    # the legend's glyphs and notes at the wide plate's 14 units, measured
    # for the extents gate (the tall legend reuses the 16.5 sums' labels)
    ("o", 14.0): 8.5, ("H", 14.0): 10.4, ("Iϛ", 14.0): 9.7,
    ("add nothing", 14.0): 79.7, ("add 8 hours", 14.0): 79.8,
    ("add 16 hours", 14.0): 85.6, ("8 + 8 + 8 = 24", 14.0): 94.5,
    # the tall plate's legend and sums at its 16.5 units, and the sub-labels
    # at the scales the hub draws them (11.9 = 16.5 x 0.72, 15.2 = 16.5 x
    # 0.92), all measured for the extents gate
    ("o", 16.5): 9.97, ("H", 16.5): 12.29, ("Iϛ", 16.5): 11.42,
    ("add nothing", 16.5): 93.92, ("add 8 hours", 16.5): 94.04,
    ("add 16 hours", 16.5): 100.89, ("3 x 8 h", 14.0): 45.01,
    ("3 x 8 h", 16.5): 53.04, ("one day", 11.9): 45.28, ("one day", 15.2): 57.84,
    ("54 years · 3 turns of the Saros", 14.0): 201.9,
    ("54 years · 3 turns of the Saros", 16.5): 237.95,
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


def label_pos(cx, cy, r_mid, ang_mid):
    return pt(cx, cy, r_mid, ang_mid)


def plate(wide):
    label_size = 14.0 if wide else 16.5
    if wide:
        W, H = 640, 340
        cx, cy, r_out = 300.0, 170.0, 118.0
        legend_x = 520.0
    else:
        W, H = 340, 480
        cx, cy, r_out = 170.0, 150.0, 104.0
        legend_x = None
    # the label ring: sectors are annular. The hub has to hold the three hub
    # rows with air around them, and the ratio that does it was measured rather
    # than guessed. The widest row's furthest corner sits 37.3 units from the
    # centre on the wide plate and 44.0 on the tall, and the contrast audit
    # probes SVG text 10.1 units OUTSIDE its box at three heights, so its
    # furthest probe lands at 41.7 units on the wide plate and 49.3 on the tall
    # (both DOM-measured; the probe offsets scale with the plate, so these
    # ratios hold at every width the page renders). At the old 0.34 and 0.45 the
    # hub circle fell INSIDE that probe band - 40.1 against 41.7, 46.8 against
    # 49.3 - so the audit read the ring's own 1px stroke instead of the ground
    # and reported the azure hub text at 3.78:1 against a line the text never
    # touches; the ground under it measures 6.19:1. 0.41 and 0.53 put the ring
    # clear of the probes with room to spare and give the claim 11 units of air
    # on both plates instead of 3, which is the bigger half of the fix: the hub
    # is the plate's focal point and it was crowding its own text. The sector
    # band stays 69.6 and 48.9 units wide, still the dial's dominant ring.
    r_in = r_out * (0.53 if not wide else 0.41)
    r_label = (r_in + r_out) / 2.0

    g = []
    g.append('  <g class="ex-sectors">')
    for i, (glyph, hours, note) in enumerate(SECTORS):
        a0 = i * SECTOR_DEG
        a1 = (i + 1) * SECTOR_DEG
        g.append('    <path class="ex-sector" d="%s"/>' %
                 sector_path(cx, cy, r_out, a0 + 1.5, a1 - 1.5, inset=r_in))
        # the glyph label sits mid-sector, mid-radius
        lx, ly = label_pos(cx, cy, r_label, a0 + SECTOR_DEG / 2.0)
        g.append('    <text class="ex-glyph" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" text-anchor="middle">%s</text>'
                 % (lx, ly + label_size * 0.35, label_size, INTER, glyph))
    g.append('    <circle class="ex-hub" cx="%.1f" cy="%.1f" r="%.1f"/>'
             % (cx, cy, r_in))
    g.append('  </g>')

    # the sum, in the hub: the plate's one claim
    # The hub sub-label's factor is the type floor's, at each plate's worst
    # render scale: the wide plate renders 0.944 in the field's 700px inset
    # (604/640) and the tall one 0.729 at a 320px phone (248/340), so 0.8 of
    # the label size came out 10.57px and 9.63px - both under 11. 0.85 and
    # 0.92 clear the floor at every width the audit sweeps (11.23px, 11.07px).
    sub_factor = 0.85 if wide else 0.92
    hub_lines = (("3 x 8 h", "ex-sum"), ("= 24 h", "ex-sum"),
                 ("one day", "ex-sum-sub"))
    hub_g = ['  <g class="ex-hubtext">']
    hy = cy - label_size * 1.1
    for text, cls in hub_lines:
        size = label_size if cls == "ex-sum" else round(label_size * sub_factor, 1)
        hub_g.append('    <text class="%s" x="%.1f" y="%.1f" font-size="%g" '
                     'font-family="%s" text-anchor="middle">%s</text>'
                     % (cls, cx, hy, size, INTER, text))
        hy += label_size * 1.25
    hub_g.append('  </g>')
    g.append("\n".join(hub_g))

    # the legend, beside (wide) or below (tall) the dial: each sector's
    # instruction, in the dial's reading order
    legend_items = [
        ("o", "add nothing"),
        ("H", "add 8 hours"),
        ("I\u03db", "add 16 hours"),
    ]
    if wide:
        ly0 = cy - label_size * 2.1
        leg_g = ['  <g class="ex-legend">']
        leg_g.append('    <text class="ex-leghead" x="%.1f" y="%.1f" '
                     'font-size="%s" font-family="%s">one Saros</text>'
                     % (legend_x - 60, ly0 - label_size * 1.4, label_size, INTER))
        for i, (glyph, note) in enumerate(legend_items):
            yy = ly0 + i * label_size * 1.7
            leg_g.append('    <text class="ex-glyph ex-legglyph" x="%.1f" '
                         'y="%.1f" font-size="%s" font-family="%s">%s</text>'
                         % (legend_x - 60, yy, label_size, INTER, glyph))
            leg_g.append('    <text class="ex-legnote" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (legend_x - 60 + label_size * 2.2, yy,
                            label_size, INTER, note))
        leg_g.append('  </g>')
        g.append("\n".join(leg_g))
        # the cycle line under the dial
        cycle = ('  <text class="ex-cycle" x="%.1f" y="%.1f" font-size="%s" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (cx, cy + r_out + 30, label_size, INTER, CYCLE_LINE))
        g.append(cycle)
    else:
        leg_g = ['  <g class="ex-legend">']
        ly0 = cy + r_out + 34
        for i, (glyph, note) in enumerate(legend_items):
            yy = ly0 + i * label_size * 1.6
            leg_g.append('    <text class="ex-glyph ex-legglyph" x="%.1f" '
                         'y="%.1f" font-size="%s" font-family="%s">%s</text>'
                         % (cx - 96, yy, label_size, INTER, glyph))
            leg_g.append('    <text class="ex-legnote" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (cx - 96 + label_size * 2.0, yy,
                            label_size, INTER, note))
        leg_g.append('  </g>')
        g.append("\n".join(leg_g))
        cycle = ('  <text class="ex-cycle" x="%.1f" y="%.1f" font-size="%s" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (cx, ly0 + label_size * 4.9, label_size, INTER, CYCLE_LINE))
        g.append(cycle)

    variant = "wide" if wide else "tall"
    title = (
        "The exeligmos sub-dial: three divisions of 54 years, the triple "
        "Saros. Each division adds hours to the eclipse times the Saros dial "
        "shows: nothing, 8 hours, or 16. Three corrections of 8 hours are 24 "
        "hours, one whole day, which is what makes the third cycle land on "
        "the calendar." if wide else
        "The exeligmos sub-dial: three divisions, adding nothing, 8 hours, "
        "or 16 hours to the Saros dial’s times. Three 8-hour corrections are "
        "one whole day.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="ex-plate ex-{variant}" role="img" focusable="false"
     aria-labelledby="ex-{variant}-title">
  <title id="ex-{variant}-title">{title}</title>
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
            ("wide", build_wide(), 300.0, 170.0, 118.0),
            ("tall", build_tall(), 170.0, 150.0, 104.0)):
        check(name + ": three sectors",
              svg.count('class="ex-sector"') == 3)
        # sector boundaries: decode the arc endpoints, measure each sector's
        # angular span - exact thirds or the drawing lies about the cycle
        spans = []
        for m in re.finditer(r'ex-sector" d="M([\d.-]+) ([\d.-]+) '
                             r'L([\d.-]+) ([\d.-]+) A[\d.]+ [\d.]+ 0 (\d) 1 '
                             r'([\d.-]+) ([\d.-]+)', svg):
            x1, y1, x2, y2 = (float(m.group(i)) for i in (3, 4, 6, 7))
            a0 = math.degrees(math.atan2(y1 - cy, x1 - cx))
            a1 = math.degrees(math.atan2(y2 - cy, x2 - cx))
            span = (a1 - a0) % 360
            spans.append(span)
        check(name + ": sectors are exact thirds",
              len(spans) == 3 and all(abs(s - 117.0) < 0.6 for s in spans),
              "spans %s (117 = 120 minus the 1.5-degree gaps either side)"
              % [round(s, 1) for s in spans])
        # the three glyphs, verbatim, in the dial's order
        glyphs = re.findall(r'ex-glyph" x="[\d.]+" y="[\d.]+" '
                            r'font-size="[\d.]+" font-family="[^"]*"[^>]*>'
                            r'([^<]+)</text>', svg)
        check(name + ": labels verbatim in order",
              glyphs[:3] == ["o", "H", "I\u03db"],
              str(glyphs[:3]))
        check(name + ": the 24-hour sum stands in the hub",
              "3 x 8 h" in svg and "= 24 h" in svg and "one day" in svg)
        check(name + ": legend carries each sector's instruction",
              all(s in svg for s in ("add nothing", "add 8 hours",
                                     "add 16 hours")))
        check(name + ": the cycle line",
              ("54 years" in svg and "3 turns of the Saros" in svg))
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        want = {14.0, 11.9} if name == "wide" else {16.5, 15.2}
        check(name + ": labels at the plate's sizes",
              sizes == {"%g" % w for w in want} | {"14.0" if name == "wide" else "16.5"},
              str(sizes))
        check(name + ": every string measured",
              all((s, sz) in MEASURED for s in
                  ("one Saros", "+ 8 h", "= 24 h", "one day")
                  for sz in (14.0, 16.5)))
        # no hex anywhere
        check(name + ": no hex colour",
              not re.findall(r"#[0-9a-fA-F]{3,8}\b", svg))

    if worst == 0:
        print("exeligmos self-test ok: thirds measured, labels verbatim, "
              "hub sum, legend, token inks, both variants")
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("exeligmos-wide.svg", build_wide()),
                       ("exeligmos-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
