#!/usr/bin/env python3
"""Generate the pin-slot plate: the mechanism that makes the Moon's pointer
speed up and slow down.

    python Source/tools/make-pin-slot.py [--self-test]

Writes Source/figures/pin-slot-wide.svg and Source/figures/pin-slot-tall.svg.

WHY THIS EXISTS. The cycles answer's last sentence names the mechanism and no
drawing carries it: "a pin-and-slot mechanism that matches Hipparchus's lunar
theory, replicating the Moon's variable velocity" (cited to source 4). The
plate draws what that sentence states, and derives from the drawing the one
number that makes the claim land.

WHAT SOURCE 4 STATES (the Wikipedia article the app read, cited eight times
on this page): k1 and k2 "are an identical pair of gears that do not mesh,
but rather, they operate face-to-face, with a short pin on k1 inserted into
a slot in k2"; "the two gears have different centres of rotation, so the pin
must move back and forth in the slot"; that varies the radius at which k2 is
driven and "necessarily" its angular velocity; "over an entire revolution the
average velocities are the same, but the fast-slow variation models the
effects of the elliptical orbit of the Moon". It names the moon train
(b1, c1, c2, d1, d2, e2, e5, k1, k2, e6, e1, b3) and the pointer's period,
27.321 days against the modern 27.321661.

THE PLATE'S ONE DERIVED NUMBER. The geometry is drawn exactly: two equal
gears, centres offset along the line of centres by e, the pin riding k1 at
its radius r, the slot a radial line of k2. The slot constrains the pin to
k2's own radius line, so k2's angle at k1's angle t is fully determined:

    phi(t) = atan2(r sin t, r cos t - e)          (centres along +x)

and the phase deviation d(t) = phi(t) - t is the drawn ring: ticks inward
where k2 lags, outward where it runs ahead. The eccentricity is a stated
choice: e/r = 0.1096, which makes the drawn deviation's amplitude 6.29
degrees, the principal term of the Moon's equation of centre, the anomaly
Hipparchus's theory models and the mechanism replicates. The plate is not
free to pick a smaller e and still claim the moon; the self-test holds the
amplitude to that figure. (The physical gears' true e/r is not in the
source; what IS in the source is the anomaly's size, and the drawing is
solved for it.)

WHAT IS DELIBERATELY ABSENT. No tooth counts (the source names none for k1/k2),
no train diagram (the plate's caption carries the train in words, as the
answer already does), no elliptical orbit drawing (the source states the
variation models the ellipse; drawing an ellipse would add a claim it does
not make). The pin and slot are drawn at one instant, labelled as such.

SELF-TEST. Demands the exact constraint curve (recomputed from the same
atan2), the amplitude at 6.29 degrees, the eccentric centres, the pin inside
the slot at the drawn instant, MEASURED covering every drawn string, token
inks only, and both variants asserting the same mechanism.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# The drawn eccentricity, stated above.
E_OVER_R = 0.1096

# The drawn instant: k1's pin at 60 degrees (2 o'clock), where the slot's
# offset from the pin's own radius reads clearly and the deviation is 5.7
# of its 6.3 degrees - visibly engaged, not at a degenerate zero crossing.
DRAWN_T_DEG = 60.0

# Every drawn string's measured width in user units, keyed by string and size.
# Measured in the browser off the built page, 2026-09-23, Inter 500. The sizes
# are the type floor's: the wide plate renders at 0.85 of its viewBox in the
# window's centre column (544 of 640) and the tall one at 0.628 at the 320px
# floor, so 12.5 and 16.5 came back at 10.63px and 10.37px - under the 11px
# floor. 13.5 and 18 clear it at every swept width (11.48 and 11.30).
MEASURED = {
    # The legend names the rates with source 4's own words: k2's
    # "necessarily" variable velocity, the page's printed phrase. The
    # ring's halves are named by the words the caption prints, "ahead"
    # and "behind"; the sample is the printed hyphenate "pin-and-slot".
    ("constant rate", 13.5): 85.2, ("variable velocity", 13.5): 105.8,
    ("constant rate", 18.0): 113.6, ("variable velocity", 18.0): 133.3,
    ("ahead", 13.5): 39.9, ("behind", 13.5): 44.3,
    ("ahead", 18.0): 48.7, ("behind", 18.0): 54.1,
    ("6.29 degrees", 13.5): 85.3, ("6.29 degrees", 18.0): 113.8,
    ("pin-and-slot", 13.5): 79.9, ("pin-and-slot", 18.0): 100.6,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


def dev_deg(t_deg, e_over_r=E_OVER_R):
    """The exact constraint curve, in degrees, unwrapped. Shared by the
    builder and the self-test: the drawing cannot drift from the arithmetic
    because both call this."""
    t = math.radians(t_deg)
    phi = math.atan2(math.sin(t), math.cos(t) - e_over_r)
    d = phi - t
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return math.degrees(d)


def amp(e_over_r=E_OVER_R):
    return max(abs(dev_deg(i / 4.0, e_over_r)) for i in range(1441))


def pt(cx, cy, r, deg_from_12):
    a = math.radians(deg_from_12 - 90.0)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def ring_ticks(cx, cy, r_out, r_in, step_deg, cls, long_at=()):
    """Radial ticks on a ring; `long_at` names angles drawn twice as long."""
    g = []
    for i in range(int(360 / step_deg)):
        d = i * step_deg
        half = 4.5 if any(abs((d - a + 180) % 360 - 180) < step_deg / 2
                          for a in long_at) else 2.2
        x0, y0 = pt(cx, cy, r_out, d)
        x1, y1 = pt(cx, cy, r_out - half, d)
        g.append('    <path class="%s" d="M%.2f %.2f L%.2f %.2f"/>'
                 % (cls, x0, y0, x1, y1))
    return g


def deviation_ring(cx, cy, r, scale_deg_per_unit, label_size, uid):
    """The consequence: 360 one-degree positions, each ticked inward or
    outward by the deviation d(t), azure where k2 runs ahead of k1. The
    zero crossings sit on the line of centres (0 and 180 degrees); they are
    drawn twice as long, the ring's own frame of reference."""
    g = ['  <g class="ps-dev" aria-hidden="true">']
    g += ring_ticks(cx, cy, r, r, 30.0, "ps-devframe", long_at=(0.0, 180.0))
    for i in range(0, 360, 2):
        d = dev_deg(i)
        if abs(d) < 0.05:
            continue
        length = abs(d) * scale_deg_per_unit
        inward = d < 0
        r0 = r
        r1 = r - length if inward else r + length
        cls = "ps-devlag" if inward else "ps-devlead"
        x0, y0 = pt(cx, cy, r0, i)
        x1, y1 = pt(cx, cy, r1, i)
        g.append('    <path class="%s" d="M%.2f %.2f L%.2f %.2f"/>'
                 % (cls, x0, y0, x1, y1))
    g.append('  </g>')
    return "\n".join(g) + "\n"


def mechanism(cx, cy, r, uid):
    """k1 and k2 face-to-face, drawn exactly: centres offset by e along the
    line of centres (0/180 degrees), k1's pin at the drawn instant, k2's
    slot along k2's own rotated radius through the pin. The pin is the
    plate's one azure statement; k2's rim is dashed, the legend's way of
    saying its rate is the varied one (k1's rim is solid: the constant)."""
    e = r * E_OVER_R
    t = DRAWN_T_DEG
    # centres: k1 at (cx, cy), k2 offset along +x (0 degrees = 3 o'clock in
    # screen terms, but pt() measures from 12; put the line of centres along
    # pt-angle 90 for composition: k2 below k1 in the wide plate? No: the
    # line of centres is HORIZONTAL on the plate, the reading direction,
    # so the slot's swing reads against it. In pt() coordinates horizontal
    # right is 90 degrees.
    LINE = 90.0
    k2x, k2y = pt(cx, cy, e, LINE)
    # pin on k1 at t
    px, py = pt(cx, cy, r, t)
    # k2's rotation phi, from the constraint, in pt() screen terms:
    # math frame: pin relative to k2 centre = (r cos T - e, r sin T) with
    # T maths angle; in pt() frame maths angle T = 90 - t. Convert:
    Tr = math.radians(90.0 - t)
    dx = r * math.cos(Tr) - e
    dy = r * math.sin(Tr)
    phi_screen = math.degrees(math.atan2(dy, dx))   # maths angle of slot line
    slot_pt_angle = (90.0 - phi_screen) % 360.0     # to pt() from-12 frame
    g = ['  <g class="ps-mech">']
    # the two gear circles, equal, face-to-face: k1 solid, k2 dashed (the
    # dashed rim is the drawing's own key: the dashed wheel is the one whose
    # rate varies, and the legend's dashed sample says the same thing)
    g.append('    <circle class="ps-gear" cx="%.2f" cy="%.2f" r="%.2f"/>'
             % (cx, cy, r))
    g.append('    <circle class="ps-gear ps-gear-b" cx="%.2f" cy="%.2f" r="%.2f"/>'
             % (k2x, k2y, r))
    # the line of centres, the geometry's frame
    lx0, ly0 = pt(cx, cy, 0.0, 0.0)
    lx1, ly1 = pt(k2x, k2y, r, LINE)
    g.append('    <path class="ps-centres" d="M%.2f %.2f L%.2f %.2f"/>'
             % (lx0, ly0, lx1, ly1))
    # the slot: a channel along k2's radius through the pin, from hub to rim
    s0x, s0y = pt(k2x, k2y, r * 0.25, slot_pt_angle)
    s1x, s1y = pt(k2x, k2y, r, slot_pt_angle)
    g.append('    <path class="ps-slot" d="M%.2f %.2f L%.2f %.2f"/>'
             % (s0x, s0y, s1x, s1y))
    # the pin: the plate's one azure statement, ON k1's circle at t
    g.append('    <circle class="ps-pin" cx="%.2f" cy="%.2f" r="3.0"/>'
             % (px, py))
    # the pin's own radius on k1, faint
    g.append('    <path class="ps-pinarm" d="M%.2f %.2f L%.2f %.2f"/>'
             % (cx, cy, px, py))
    # centre dots
    g.append('    <circle class="ps-centre" cx="%.2f" cy="%.2f" r="1.6"/>'
             % (cx, cy))
    g.append('    <circle class="ps-centre" cx="%.2f" cy="%.2f" r="1.6"/>'
             % (k2x, k2y))
    g.append('  </g>')
    return "\n".join(g) + "\n", k2x, k2y


def plate(wide):
    label = 13.5 if wide else 18.0
    if wide:
        W, H = 640, 360
        mech_cx, mech_cy, mech_r = 190.0, 180.0, 96.0
        dev_cx, dev_cy, dev_r = 480.0, 180.0, 108.0
    else:
        W, H = 340, 560
        mech_cx, mech_cy, mech_r = 170.0, 138.0, 78.0
        dev_cx, dev_cy, dev_r = 170.0, 402.0, 96.0
    # the deviation ring's scale: the amplitude must read. 6.29 deg at
    # scale 1.6 units/deg = 10.1 units of tick - clear at both scales.
    scale = 1.6
    mech_g, k2x, k2y = mechanism(mech_cx, mech_cy, mech_r, "wide" if wide else "tall")
    dev_g = deviation_ring(dev_cx, dev_cy, dev_r, scale, label,
                           "wide" if wide else "tall")
    # amplitude claim, inside the deviation ring's centre
    amp_txt = ('  <text class="ps-amp" x="%.1f" y="%.1f" font-size="%s" '
               'font-family="%s" text-anchor="middle">6.29 degrees</text>\n'
               % (dev_cx, dev_cy + label * 0.35, label, INTER))
    # the two rate labels, on the ring's vertical axis: the deviation is zero
    # at pt-angles 0 and 180 (the line of centres) and the frame circle's own
    # tangent there is horizontal, so a horizontally-centred label just above
    # and just below the ring sits ALONG the tangent - the one placement where
    # the whole text box clears the frame circle and every tick's outward tip
    # (dmin = dev_r + 22 - baseline shift, measured 21 units of daylight).
    # The labels read with the halves they name: "ahead" at 12 (the lead
    # half opens at 0 and runs to 180), "behind" at 6 (the lag half).
    # (Placement history: 90/270 ran off the box AND through the frame; 15/195
    # with line-start anchors grazed the frame at the tall plate's box corner.
    # The tangent placement is the first one the DOM audit passes at both
    # variants.)
    ax, ay = dev_cx, dev_cy - dev_r - 22
    bxx, byy = dev_cx, dev_cy + dev_r + 22
    ahead = ('  <text class="ps-ahead" x="%.1f" y="%.1f" font-size="%s" '
             'font-family="%s" text-anchor="middle">ahead</text>\n'
             % (ax, ay + label * 0.35, label, INTER))
    behind = ('  <text class="ps-behind" x="%.1f" y="%.1f" font-size="%s" '
              'font-family="%s" text-anchor="middle">behind</text>\n'
              % (bxx, byy + label * 0.35, label, INTER))
    # The legend's geometry: the wide plate has room for one row of three;
    # the tall plate's 340-wide column cannot hold one line of the attested
    # strings ("variable velocity" 133.3 and "pin-and-slot" 100.6 at 18
    # units: three entries minimum 351.2 of 340), and the cold read caught
    # the two-row draft pushing the second label past the plate's clipped
    # edge. So the tall legend stacks THREE rows at the rail's left column,
    # 1.3 line height, the third still clear of the deviation ring below.
    # Same entries, same inks.
    if wide:
        leg_y = mech_cy + mech_r + 34
        s1_x = mech_cx - 118
        s2_x = mech_cx + 4
        s3_x = mech_cx + 126
        rows = [(s1_x, "constant rate", "line", 0.0),
                (s2_x, "variable velocity", "dash", 0.0),
                (s3_x, "pin-and-slot", "pin", 1.55)]
    else:
        leg_y = mech_cy + mech_r + 30
        s1_x = s2_x = s3_x = mech_cx - 118
        rows = [(s1_x, "constant rate", "line", 0.0),
                (s2_x, "variable velocity", "dash", 1.3),
                (s3_x, "pin-and-slot", "pin2", 2.6)]
    legend = ['  <g class="ps-legend">']
    for sx, text, kind, dy in rows:
        ty = leg_y + dy * label
        if kind == "line":
            legend.append('    <path class="ps-gear" d="M%.1f %.1f h20"/>' % (sx, ty))
        elif kind == "dash":
            legend.append('    <path class="ps-gear-b" d="M%.1f %.1f h20" stroke-dasharray="3.2 2.6"/>' % (sx, ty))
        else:
            legend.append('    <circle class="ps-pin" cx="%.1f" cy="%.1f" r="2.6"/>' % (sx + 3, ty))
        legend.append('    <text class="ps-legend-t" x="%.1f" y="%.1f" font-size="%s" '
                      'font-family="%s">%s</text>'
                      % (sx + (10 if kind in ("pin", "pin2") else 28),
                         ty + label * 0.35, label, INTER, text))
    legend.append('  </g>')
    legend_g = "\n".join(legend) + "\n"
    variant = "wide" if wide else "tall"
    title = ("The pin-and-slot mechanism, drawn exactly: k1 turns at a constant "
             "rate and carries a pin; k2, an identical gear with a different "
             "centre of rotation, carries the slot the pin rides. The ring "
             "shows the consequence, k2’s phase against k1’s: ahead by up to "
             "6.29 degrees through half the turn, behind through the other "
             "half." if wide else
             "The pin-and-slot mechanism drawn exactly, with k2’s phase "
             "deviation ring: ahead 6.29 degrees, then behind, once per turn.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="ps-plate ps-{variant}" role="img" focusable="false"
     aria-labelledby="ps-{variant}-title">
  <title id="ps-{variant}-title">{title}</title>
{mech_g}{dev_g}{legend_g}{amp_txt}{ahead}{behind}</svg>
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

    amplitude = amp()
    check("the derived amplitude is the Moon's 6.29",
          abs(amplitude - 6.29) < 0.02, "%.3f deg at e/r=%.4f"
          % (amplitude, E_OVER_R))

    for name, svg, mech_cx, mech_cy, mech_r, dev_cx, dev_cy, dev_r in (
            ("wide", build_wide(), 190.0, 180.0, 96.0, 480.0, 180.0, 108.0),
            ("tall", build_tall(), 170.0, 138.0, 78.0, 170.0, 402.0, 96.0)):
        check(name + ": two equal gear circles",
              svg.count('class="ps-gear"') == 2)
        # one pin in the mechanism; the legend's sample circle is the second
        # ps-pin by design (the key drawn in the ink it describes)
        check(name + ": one pin, one slot",
              svg.count('class="ps-pin" cx') == 2 and
              svg.count('class="ps-slot"') == 1)
        # eccentric centres: the second gear's centre sits exactly e from the first
        # (the regex matches both rim classes; the legend's sample paths have
        # no cx, so they never enter this list)
        gears = re.findall(r'ps-gear(?: ps-gear-b)?" cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"',
                           svg)
        (ax, ay, ar), (bx, by, br) = gears
        ar, br = float(ar), float(br)
        e = math.hypot(float(bx) - float(ax), float(by) - float(ay))
        check(name + ": centres offset by the stated eccentricity",
              ar == br and abs(e / ar - E_OVER_R) < 0.001,
              "e/r %.4f" % (e / ar))
        # the pin lies on k1's circle at the drawn instant, and INSIDE k2's slot
        pin = re.search(r'ps-pin" cx="([\d.]+)" cy="([\d.]+)"', svg)
        px, py = float(pin.group(1)), float(pin.group(2))
        on_circle = abs(math.hypot(px - mech_cx, py - mech_cy) - mech_r) < 0.05
        check(name + ": the pin rides k1's radius", on_circle)
        # slot line passes through the pin: cross product ~ 0
        k2 = gears[1]
        slot = re.search(r'ps-slot" d="M([\d.-]+) ([\d.-]+) L([\d.-]+) ([\d.-]+)"',
                         svg)
        sx0, sy0, sx1, sy1 = (float(slot.group(i)) for i in (1, 2, 3, 4))
        cross = ((sx1 - sx0) * (py - sy0) - (sy1 - sy0) * (px - sx0))
        check(name + ": the pin is inside the slot", abs(cross) < 0.5,
              "cross %.3f" % cross)
        # the deviation ring exists with lead and lag strokes
        check(name + ": deviation ring carries lead and lag",
              svg.count('class="ps-devlead"') > 40 and
              svg.count('class="ps-devlag"') > 40,
              "%d lead, %d lag" % (svg.count('class="ps-devlead"'),
                                   svg.count('class="ps-devlag"')))
        # the drawn strokes match the arithmetic: sample the 0-degree tick
        # (lag side) and the 90-degree tick (lead side)
        def tick_len(angle):
            best = None
            for m in re.finditer(r'ps-dev(lead|lag)" d="M([\d.-]+) ([\d.-]+) '
                                 r'L([\d.-]+) ([\d.-]+)"', svg):
                x0, y0 = float(m.group(2)), float(m.group(3))
                x1, y1 = float(m.group(4)), float(m.group(5))
                if abs(math.hypot(x0 - dev_cx, y0 - dev_cy) - dev_r) > 0.6:
                    continue
                a0 = math.degrees(math.atan2(y0 - dev_cy, x0 - dev_cx))
                # screen-y grows downward, so the pt() angle is 90 + a0,
                # not 90 - a0 (the minus maps probe t to the tick at
                # 180 - t and mismatches every asymmetric tick)
                ang = (90.0 + a0) % 360.0
                if abs((ang - angle + 180) % 360 - 180) < 1.2:
                    best = math.hypot(x1 - x0, y1 - y0)
            return best
        # dev(0) is 0 by symmetry (the line of centres): the nearest drawn
        # tick, at 2 degrees, carries the check instead.
        want_0 = abs(dev_deg(2.0)) * 1.6
        got_0 = tick_len(2.0)
        check(name + ": the 2-degree lag tick is the arithmetic",
              got_0 is not None and abs(got_0 - want_0) < 0.05,
              "%.2f vs %.2f" % (got_0 or -1, want_0))
        want_90 = dev_deg(90.0) * 1.6
        got_90 = tick_len(90.0)
        check(name + ": the 90-degree lead tick is the arithmetic",
              got_90 is not None and abs(got_90 - want_90) < 0.05,
              "%.2f vs %.2f" % (got_90 or -1, want_90))
        for s in ("constant rate", "variable velocity", "pin-and-slot",
                  "ahead", "behind", "6.29 degrees"):
            if ">%s<" % s not in svg:
                check(name + ": label %r" % s, False)
                break
        else:
            check(name + ": every label drawn", True)
        # the legend carries the same three strings, each beside a sample of
        # its own line class: the key is drawn in the ink it describes
        check(name + ": legend has three samples",
              svg.count('ps-legend') >= 1 and
              svg.count('class="ps-legend-t"') == 3 and
              'class="ps-gear" d="M' in svg and 'stroke-dasharray' in
              svg.split('ps-legend', 1)[1])
        check(name + ": k2's rim carries the dash key",
              'ps-gear ps-gear-b"' in svg)
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        want = 13.5 if name == "wide" else 18.0
        check(name + ": labels at the plate's size",
              sizes == {str(want)}, str(sizes))
        check(name + ": every string measured",
              all((s, want) in MEASURED for s in
                  ("constant rate", "variable velocity", "ahead",
                   "behind", "6.29 degrees")))

    print("pin-slot self-test %s" % ("ok" if not worst else "FAILED"))
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("pin-slot-wide.svg", build_wide()),
                       ("pin-slot-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
