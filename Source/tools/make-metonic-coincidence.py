#!/usr/bin/env python3
"""Generate the metonic-coincidence plate: the founding arithmetic of the
rear face, drawn as the two counts on one dial.

    python Source/tools/make-metonic-coincidence.py [--self-test]

Writes Source/figures/metonic-coincidence-wide.svg and
Source/figures/metonic-coincidence-tall.svg. Run from anywhere; paths are
anchored to this file.

WHY THIS EXISTS. The page's captured answer states the coincidence every
rear-face plate stands on, and no plate drew it: "The Metonic cycle is an
astronomical period of 19 tropical years, almost exactly equal to 235
synodic lunar months ... 19 solar years and 235 lunar months differ by only
about two hours" (source 1). The rear dials plate draws where the spiral
sits, the exeligmos draws the correction its error demands, the callippic
draws the refinement 4 x 19 = 76 - and the coincidence itself, the reason
ANY of them exist, was prose only. This plate is the relation first, the
dial that embodies it second: 235 lunar months as beads on the outer ring,
19 tropical years as the divisions of the inner dial, one anchor at 12
o'clock where both counts start together.

THE DRAWING IS THE COUNT. The month beads' dash pitch is 2*pi*r/235, the
year strokes stand at 360/19 degrees, and the self-test demands both
reproduce to four decimals - a drawing whose counts were decorative would
be a lie told with geometry, the two-rings plate's own rule.

WHAT IS DELIBERATELY ABSENT. No month names (the rear-dials plate carries
the recovered ones; this plate draws the COUNTS, not the calendar). No
month numbers on the beads - 235 marks would label themselves into noise.
No drift arrow, no second rotation state: the prose prints the gap as a
TIME ("about two hours"), and the hub carries that phrase as the plate's
one claim; nothing multiplies it into a position the page does not state.

SELF-TEST. Demands the 235-pitch arithmetic, the 19 strokes at 360/19 with
the first at 12 o'clock, the one anchor, the four strings verbatim (all
printed prose, from the captured answer), MEASURED covering every string
at both render scales, token inks only, and both variants asserting the
same dial.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

MONTHS = 235
YEARS = 19

# The four drawn strings, all from the captured answer's Metonic paragraph
# (source 1), verbatim. The hub carries the gap as the page prints it: a
# time, not a position.
HUB_LEAD = "differ by only"
HUB_CLAIM = "about two hours"
YEARS_LABEL = "19 tropical years"
MONTHS_LABEL = "235 synodic lunar months"

# Measured in the browser off the built page (Inter 600, canvas
# measureText), following the family's scale arithmetic: the wide plate
# renders at 0.944 in the field's 700px inset, so its hub lines are 11.9
# units (11.2px rendered, above the floor) and its labels 14 (13.2px); the
# tall plate renders at 0.729 at a 320px phone, so its hub lines are 15.2
# units (11.1px) and its labels 16.5 (12.0px).
MEASURED = {
    (HUB_LEAD, 11.9): 75.7, (HUB_CLAIM, 11.9): 93.5,
    (HUB_LEAD, 15.2): 96.7, (HUB_CLAIM, 15.2): 119.5,
    (YEARS_LABEL, 14.0): 110.7, (MONTHS_LABEL, 14.0): 175.7,
    (YEARS_LABEL, 16.5): 130.5, (MONTHS_LABEL, 16.5): 207.1,
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


def month_ring(cx, cy, r, count):
    """The lunar months as beads: the calendar-ring family's own language,
    stroke-width 2.4 with round caps, dash 0.02, the gap the rest of a
    pitch of 2*pi*r/count, the whole circle rotated so bead 0 sits at 12
    o'clock. Returns the element and the pitch, for the self-test."""
    pitch = 2 * math.pi * r / count
    gap = pitch - 0.02
    el = ('    <circle class="mtc-months-ring" cx="%.1f" cy="%.1f" r="%.1f" '
          'stroke-dasharray="0.02 %.6f" transform="rotate(-90 %.1f %.1f)"/>'
          % (cx, cy, r, gap, cx, cy))
    return el, pitch


def plate(wide):
    if wide:
        W, H = 640, 320
        cx, cy, r_out = 320.0, 150.0, 118.0
        r_in = 49.5          # hub ratio 0.42, callippic's precedent range
        hub_lines = ((HUB_LEAD, 11.9, -15.0), (HUB_CLAIM, 11.9, 3.0))
        label_size = 14.0
        lab_y1, lab_y2 = cy + r_out + 24, cy + r_out + 40
        side_labels = True
    else:
        W, H = 340, 430
        cx, cy, r_out = 170.0, 138.0, 96.0
        r_in = 51.0          # hub ratio 0.53, the callippic tall plate's own
        hub_lines = ((HUB_LEAD, 15.2, -15.0), (HUB_CLAIM, 15.2, 3.0))
        label_size = 16.5
        lab_y1, lab_y2 = cy + r_out + 34, cy + r_out + 54
        side_labels = False

    r_year_out = r_in + 20.0 if wide else r_in + 18.0
    year_deg = 360.0 / YEARS

    g = []
    # the lunar months: 235 beads, the outer ring
    ring, pitch = month_ring(cx, cy, r_out, MONTHS)
    g.append('  <g class="mtc-moons">')
    g.append(ring)
    g.append('  </g>')

    # the tropical years: 19 divisions of the inner dial, the first at 12
    g.append('  <g class="mtc-years">')
    for i in range(YEARS):
        x0, y0 = pt(cx, cy, r_in + 4.0, i * year_deg)
        x1, y1 = pt(cx, cy, r_year_out, i * year_deg)
        g.append('    <line class="mtc-year" x1="%.2f" y1="%.2f" '
                 'x2="%.2f" y2="%.2f"/>' % (x0, y0, x1, y1))
    g.append('  </g>')

    # the one anchor: a radial hairline through both counts at 12 o'clock,
    # where month 0 and year 0 start together
    ax0, ay0 = pt(cx, cy, r_in + 2.0, 0.0)
    ax1, ay1 = pt(cx, cy, r_out + 6.0, 0.0)
    dotx, doty = pt(cx, cy, r_out, 0.0)
    g.append('  <g class="mtc-anchor">')
    g.append('    <line class="mtc-anchor-line" x1="%.2f" y1="%.2f" '
             'x2="%.2f" y2="%.2f"/>' % (ax0, ay0, ax1, ay1))
    g.append('    <circle class="mtc-anchor-dot" cx="%.2f" cy="%.2f" '
             'r="1.6"/>' % (dotx, doty))
    g.append('  </g>')

    # the hub: the gap as the page prints it, a time - the plate's one claim
    g.append('  <g class="mtc-hubtext">')
    g.append('    <circle class="mtc-hub" cx="%.1f" cy="%.1f" r="%.1f"/>'
             % (cx, cy, r_in))
    for text, size, dy in hub_lines:
        cls = "mtc-claim" if text == HUB_CLAIM else "mtc-hub-lead"
        g.append('    <text class="%s" x="%.1f" y="%.1f" font-size="%g" '
                 'font-family="%s" font-weight="600" text-anchor="middle">'
                 '%s</text>' % (cls, cx, cy + dy + size * 0.35, size, INTER,
                                text))
    g.append('  </g>')

    # the two counts, named: side by side at the ring's foot on the wide
    # plate, stacked and centred on the tall (the wide row cannot fit the
    # months label at the tall plate's width; the tall column cannot spare
    # the wide row's diameter)
    g.append('  <g class="mtc-labels">')
    if side_labels:
        g.append('    <text class="mtc-years-label" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" font-weight="600" '
                 'text-anchor="end">%s</text>'
                 % (cx - 8, lab_y1, label_size, INTER, YEARS_LABEL))
        g.append('    <text class="mtc-months-label" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" font-weight="600" '
                 'text-anchor="start">%s</text>'
                 % (cx + 8, lab_y1, label_size, INTER, MONTHS_LABEL))
    else:
        g.append('    <text class="mtc-years-label" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" font-weight="600" '
                 'text-anchor="middle">%s</text>'
                 % (cx, lab_y1, label_size, INTER, YEARS_LABEL))
        g.append('    <text class="mtc-months-label" x="%.1f" y="%.1f" '
                 'font-size="%g" font-family="%s" font-weight="600" '
                 'text-anchor="middle">%s</text>'
                 % (cx, lab_y2, label_size, INTER, MONTHS_LABEL))
    g.append('  </g>')

    variant = "wide" if wide else "tall"
    title = (
        "The Metonic coincidence: 235 synodic lunar months fit almost "
        "exactly into 19 tropical years. The two counts on one dial, "
        "anchored together at 12 o'clock; after nineteen years the lunar "
        "count is about two hours ahead." if wide else
        "The Metonic coincidence: 235 lunar months in 19 tropical years, "
        "about two hours apart.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="mtc-plate mtc-{variant}" role="img" focusable="false"
     aria-labelledby="mtc-{variant}-title">
  <title id="mtc-{variant}-title">{title}</title>
{chr(10).join(g)}
</svg>
'''
    return svg, pitch


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

    for name, (svg, pitch), r_out, r_in, wide in (
            ("wide", build_wide(), 118.0, 49.5, True),
            ("tall", build_tall(), 96.0, 51.0, False)):
        # the count IS the drawing: the bead pitch must be the 235th of the
        # circle, to four decimals
        check(name + ": the month ring carries 235 beads",
              abs(pitch - 2 * math.pi * r_out / MONTHS) < 0.0001,
              "pitch %.4f units" % pitch)
        strokes = re.findall(r'mtc-year" x1="([\d.-]+)" y1="([\d.-]+)" '
                             r'x2="([\d.-]+)" y2="([\d.-]+)"', svg)
        check(name + ": nineteen year divisions",
              len(strokes) == YEARS, str(len(strokes)))
        if strokes:
            cx = 320.0 if wide else 170.0
            cy = 150.0 if wide else 138.0
            # stroke 0 stands at 12 o'clock: both ends on the vertical
            x0, y0, x1, y1 = (float(v) for v in strokes[0])
            check(name + ": the first year starts at 12 o'clock",
                  abs(x0 - cx) < 0.02 and abs(x1 - cx) < 0.02
                  and y0 < cy and y1 < cy)
            # the strokes are evenly divided: decode every inner angle
            angs = sorted(
                (math.degrees(math.atan2(float(y0) - cy, float(x0) - cx))
                 % 360) for x0, y0, x1, y1 in strokes)
            steps = [(b - a) % 360 for a, b in zip(angs, angs[1:])]
            check(name + ": the years divide the circle exactly",
                  all(abs(s - year_deg_expect(wide)) < 0.05 for s in steps),
                  "step %.3f expected %.3f" % (steps[0], year_deg_expect(wide)))
        check(name + ": one anchor at 12 o'clock",
              svg.count('class="mtc-anchor-line"') == 1 and
              svg.count('class="mtc-anchor-dot"') == 1)
        check(name + ": the gap stands in the hub as the page prints it",
              ">%s<" % HUB_LEAD in svg and ">%s<" % HUB_CLAIM in svg)
        for s in (YEARS_LABEL, MONTHS_LABEL):
            if ">%s<" % s not in svg:
                check(name + ": label %r" % s, False)
                break
        else:
            check(name + ": both counts named", True)
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        want = {"11.9", "14"} if wide else {"15.2", "16.5"}
        check(name + ": labels at the plate's sizes", sizes == want,
              str(sizes))
        hub_size = 11.9 if wide else 15.2
        lab_size = 14.0 if wide else 16.5
        check(name + ": every string measured at its drawn size",
              all((s, sz) in MEASURED for s, sz in
                  ((HUB_LEAD, hub_size), (HUB_CLAIM, hub_size),
                   (YEARS_LABEL, lab_size), (MONTHS_LABEL, lab_size))))
        check(name + ": no hex colour",
              not re.findall(r"#[0-9a-fA-F]{3,8}\b", svg))

    if worst == 0:
        print("metonic-coincidence self-test ok: 235 beads, 19 divisions, "
              "one anchor, the gap verbatim, token inks, both variants")
    return worst


def year_deg_expect(wide):
    return 360.0 / YEARS


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, (svg, _) in (("metonic-coincidence-wide.svg", build_wide()),
                            ("metonic-coincidence-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
