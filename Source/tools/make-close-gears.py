#!/usr/bin/env python3
"""Generate the close's world: the train that enters the poster from off-page.

    python Source/tools/make-close-gears.py [--self-test]

Writes Source/figures/close-gears.svg

WHY THIS EXISTS. The close ends flat: wordmark, window, copy, footer, over. The
reference closes land on a world (Freebuff's trees over their wordmark, Tempo's
planet limb) and this page opened on a world of its own, the mechanism, which
then never returns. The reader walks down a page that argues the machine's case
for twelve acts and ends on bare paint.

So the machine returns, arriving rather than standing: the hero's band runs
UNDER the product; the close's enters from OFF-PAGE. The great wheel's crown
sinks from above the poster's top edge (the apex is exactly on the band's top
edge, so the wheel is cut by the page's own frame, which is what says the world
is larger than it), and a second wheel rides inside the crown near the apex so
the one place the teeth bite is fully in frame, right of centre, clear of the
wordmark's mass. The FIELD ends below this band while the world is still
running: the machine goes on past the bottom of the page.

WHY TWO WHEELS. The mechanism's published reconstruction has a second wheel
riding inside the great one, which the hero's figure does not show and this one
does. 223 teeth for the crown, again, because it is the same machine: the wheel
the hero opens with closes the page. 60 is the count the reconstruction names
for the large slot wheel. Nothing on the page states a 60; the figure is
decorative (`aria-hidden`), carries no title and no caption, so no reader is
told anything by it that the prose has not said about its own numbers. The mesh
arithmetic, not the tooth story, is the claim the self-test owns.

THE PAINT IS THE ENDING'S POINT. The band hangs below the field's bottom edge,
but nothing in it is drawn with the dark's own colours: every stroke is the
field's ink, exactly as bright on the dark as in the field, because the reader
is looking at the machine, not the ground. The hero's world is drawn IN the
ground; the close's is drawn IN the machine.

THE GEOMETRY IS ARITHMETIC, so nothing is cropped by accident and the two
numbers that must agree are one:

    W, H           = 640 x 560            one train wide: the pinion wholly in
                                           frame, the crown bleeding off three
                                           sides, its right limb leaving through
                                           the bottom
    apex           = (150, 0)             the great wheel's crown, exactly on
                                           the band's top edge, off-centre left
    great wheel R1 = 720                  (pitch), centre C1 = (150, 720)
    inner wheel R2 = N2*P/(2*pi) = 193.72 (pitch)
    fall to x=640  = 720 - sqrt(720^2 - 490^2) = 193.4

That last line is the limb test, the same one the poster's horizon is held to:
a crown that falls ~193px across the band reads as a world much larger than
the frame. The 150 is composition, and it is recorded as composition: it puts
the crown's apex left of centre so the mesh point and the pinion sit in the
band's right half, clear of the wordmark's optical mass, which sits centre.

WHY THE PINION MUST FIT AND THE CROWN MUST NOT. The crown is the world: cut by
the frame on three sides, it reads as continuing past the page, which is the
whole point of the ending. The pinion is the subject: small enough to fit
entirely, and a straight chord across it would read as a drawing that did not
know where its own edge was - the exact defect the hero's generator notes and
avoids. The first draft's viewBox was 420 wide and cut the pinion at x=420;
the shot caught it and the width moved to 640.

EXTERNAL OR INTERNAL? INTERNAL, and the word matters. The pinion rides INSIDE
the crown: its pitch circle lies within the great wheel's, the crown acting as
the annulus, so the centre distance is R1 - R2 (not R1 + R2, which would put
the pinion outside the wheel entirely, nor R1, which is no mesh at all - the
first draft's bug, caught by its own assertion before the figure shipped). The
contact point sits at R1 from the wheel's centre, beyond the pinion's centre,
and the pinion turns the SAME way as the wheel, at N1/N2 the rate. The dash
phases are solved so a tooth CENTRE of the crown meets a GAP CENTRE of the
pinion at that contact point, and the drive relation preserves it through any
rotation because arc length is what meshing conserves. The self-test asserts
both the invariant and its failure under the flipped rate - a check that
cannot fail is not a check.

THE TEETH ARE A DASH PATTERN, exactly as the hero's are, for the same byte
argument and the same mechanical truth: a dash is a radial interval on the
pitch circle, which is what a cut tooth is, and the shared module P is the
shared pattern.
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "close-gears.svg"

W, H = 640.0, 560.0           # one train wide, deep enough to sink

N1 = 223                      # the mechanism's largest gear, as in the hero
N2 = 60                       # the reconstruction's large slot wheel
R1 = 720.0                    # the great wheel's pitch radius
P = 2 * math.pi * R1 / N1     # the shared module
R2 = N2 * P / (2 * math.pi)   # 193.72: the inner wheel

TOOTH = P * 0.5               # half the pitch, square-cut, as in the hero
DEPTH = P * 0.75              # radial tooth height

# Rims, in the hero's proportions: the hero's 505-pitch great wheel carries a
# 24 rim, so this 720 carries 34, and the 194 pinion carries 9 - each the same
# fraction of the wheel it belongs to, which is what keeps the two drawings
# cousins. The hub radius is shared idiom too.
RIM1 = 34.0
RIM2 = 9.0
ARBOR = 26.0

APEX_X = 150.0                # composition: crown apex left of centre, mesh right
C1 = (APEX_X, R1)             # so the apex is exactly on the band's top edge

# The pinion's bearing, measured from 12 o'clock (straight up from C1),
# positive clockwise. 18.5 degrees puts the contact point at bearing x =
# 150 + 720*sin(18.5) = 378.5, y = 720 - 720*cos(18.5) = 37.2: upper right,
# the bite just right of the apex. The pinion's centre then hangs
# D = R1-R2 = 526.28 along the same bearing, at (317.0, 220.9) - wholly
# inside the 640-wide frame (right edge 510.7 < 640), which is the rule:
# the crown may bleed, the pinion may not.
THETA_DEG = 18.5


def pinion_centre():
    """The pinion's centre: distance R1-R2 from C1, the internal-mesh distance."""
    t = math.radians(THETA_DEG)
    d = R1 - R2
    return (C1[0] + d * math.sin(t), C1[1] - d * math.cos(t))


def phase_for(centre, radius, mesh, want):
    """`stroke-dashoffset` putting `want` of the pattern at the mesh point.

    Same arithmetic as the hero's generator, stated locally because the two
    files agree by construction and not by import: a circle's path starts at
    3 o'clock and runs clockwise (increasing angle here, y-down), arc length
    from the start is r*phi, and a dash begins where (s + offset) hits a
    multiple of the pattern - a tooth centre at half a tooth, a gap centre at
    one and a half. Returns a value in [0, P) because the pattern repeats.
    """
    dx, dy = mesh[0] - centre[0], mesh[1] - centre[1]
    phi = math.atan2(dy, dx) % (2 * math.pi)
    s = radius * phi
    return ((want * P) - s) % P


def mesh_geometry():
    """The contact point and both wheels' dashoffsets.

    Internal mesh: the contact sits on the line of centres at R1 from the
    wheel's centre - which is R2 beyond the pinion's centre, since the
    centres are R1-R2 apart. Asserted, because the first draft put the
    centre distance at R1 and the contact landed on the pinion's centre,
    which is a drawing of nothing.
    """
    cx, cy = pinion_centre()
    d = math.hypot(cx - C1[0], cy - C1[1])
    assert abs(d - (R1 - R2)) < 1e-9, f"centre distance {d} is not R1-R2: not an internal mesh"
    t = math.radians(THETA_DEG)
    mesh = (C1[0] + R1 * math.sin(t), C1[1] - R1 * math.cos(t))
    a = phase_for(C1, R1, mesh, 0.5)    # a tooth CENTRE of the crown
    b = phase_for((cx, cy), R2, mesh, 1.5)   # meets a GAP CENTRE of the pinion
    return mesh, a, b


def internal_check(turn_deg, sense=1.0):
    """Do the teeth still interleave after the train turns?

    Internal gearing: the pinion turns the SAME way as the wheel, at N1/N2
    the rate (`sense` is the sign of that rate). In pattern coordinates
    u = R*(phi - turn) + offset, meshing conserves arc length, so the
    DIFFERENCE of the two wheels' pattern coordinates at the contact point is
    invariant - the internal-mesh invariant, where the hero's external wheels
    hold a sum. `sense` exists to make the check falsifiable: flipped, the
    invariant breaks, and the assertion fails.
    """
    mesh, a_off, b_off = mesh_geometry()
    cx, cy = pinion_centre()
    phi_a = math.atan2(mesh[1] - C1[1], mesh[0] - C1[0]) % (2 * math.pi)
    phi_b = math.atan2(mesh[1] - cy, mesh[0] - cx) % (2 * math.pi)
    psi = math.radians(turn_deg)
    u_a = (R1 * phi_a - R1 * psi + a_off) % P
    u_b = (R2 * phi_b - sense * R1 * psi + b_off) % P
    return (u_a - u_b) % P


def main():
    mesh, a_off, b_off = mesh_geometry()
    cx, cy = pinion_centre()
    root1 = R1 - DEPTH / 2
    inner1 = root1 - RIM1
    root2 = R2 - DEPTH / 2
    inner2 = root2 - RIM2

    # Spokes, in the hero's idiom: a plain rotating ring reads as nothing;
    # spokes give the eye a count that moves. Five on the crown, three on the
    # pinion, all from the hub out to the rim's inner edge.
    def spokes(centre, inner, angles):
        out = []
        for a_deg in angles:
            a = math.radians(a_deg)
            x1, y1 = centre[0] + ARBOR * math.cos(a), centre[1] + ARBOR * math.sin(a)
            x2, y2 = centre[0] + inner * math.cos(a), centre[1] + inner * math.sin(a)
            out.append(f"M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}")
        return " ".join(out)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 560"\n'
        '     class="close-gears"\n'
        '     focusable="false" aria-hidden="true">\n'
        '  <!-- Generated by Source/tools/make-close-gears.py - do not hand-edit.\n'
        '       223 and 60: the hero\'s crown again, driving the reconstruction\'s\n'
        '       large slot wheel - internal gearing, the pinion riding inside the\n'
        '       crown, turning the same way at N1/N2 the rate. The crown is\n'
        '       cut by the band\'s top edge (the world arrives from off-page) and\n'
        '       the band hangs below the field\'s end; the ink is the field\'s, so\n'
        '       the machine reads against the dark. Phases are solved for the\n'
        '       mesh just right of the apex. -->\n'
        # The great wheel first, so the pinion paints over it at the bite.
        + f'  <g data-close-a="223" data-close-cx="{C1[0]:.2f}" data-close-cy="{C1[1]:.2f}">\n'
        + f'    <circle class="cg-tooth" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{R1:.2f}"\n'
        + f'            stroke-width="{DEPTH:.2f}" stroke-dasharray="{TOOTH:.2f} {TOOTH:.2f}"\n'
        + f'            stroke-dashoffset="{a_off:.2f}"/>\n'
        + f'    <circle class="cg-band" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{inner1 + RIM1 / 2:.2f}"\n'
        + f'            stroke-width="{RIM1:.2f}"/>\n'
        + f'    <circle class="cg-rim" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{root1:.2f}"/>\n'
        + f'    <circle class="cg-rim" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{inner1:.2f}"/>\n'
        + f'    <path class="cg-face" d="{spokes(C1, inner1, [195, 225, 255, 285, 315])}"/>\n'
        + f'    <circle class="cg-rim" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{ARBOR:.2f}"/>\n'
        + '  </g>\n'
        + f'  <g data-close-b="60" data-close-cx="{cx:.2f}" data-close-cy="{cy:.2f}">\n'
        + f'    <circle class="cg-tooth" cx="{cx:.2f}" cy="{cy:.2f}" r="{R2:.2f}"\n'
        + f'            stroke-width="{DEPTH:.2f}" stroke-dasharray="{TOOTH:.2f} {TOOTH:.2f}"\n'
        + f'            stroke-dashoffset="{b_off:.2f}"/>\n'
        + f'    <circle class="cg-band" cx="{cx:.2f}" cy="{cy:.2f}" r="{inner2 + RIM2 / 2:.2f}"\n'
        + f'            stroke-width="{RIM2:.2f}"/>\n'
        + f'    <circle class="cg-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{root2:.2f}"/>\n'
        + f'    <circle class="cg-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{inner2:.2f}"/>\n'
        + f'    <path class="cg-face" d="{spokes((cx, cy), inner2, [30, 150, 270])}"/>\n'
        + f'    <circle class="cg-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{ARBOR:.2f}"/>\n'
        + '  </g>\n'
        + '</svg>\n'
    )

    if "--self-test" in sys.argv:
        # The sum must be the same at every angle, because that is the
        # alignment the teeth interleave on. The flipped sense must move it.
        # Compared on the circle, as the hero's check is: two values a hair
        # either side of a whole pitch are the same alignment, and a bare
        # max() would call them different.
        def drift(values):
            return max(abs(((v - values[0] + P / 2) % P) - P / 2) for v in values)

        angles = (0, 2, 4, 8)
        base = [internal_check(t) for t in angles]
        wrong = [internal_check(t, sense=-1.0) for t in angles]
        assert drift(base) < 1e-9, f"mesh drifts across rotation: {base}"
        assert drift(wrong) > 0.1, f"the flipped rate did not move the phase: {wrong}"
        print(f"self-test ok - internal mesh held to {drift(base):.2e} of a pitch "
              f"at 0/2/4/8 deg; the wrong rate moved it to {wrong[-1]:.2f}")

    OUT.write_bytes(svg.encode("utf-8"))
    print(f"{OUT.relative_to(OUT.parents[2])} written: {len(svg)} B")
    print(f"  module {P:.4f}  R2 {R2:.2f}  C1 {C1}  C2 ({cx:.2f}, {cy:.2f})")
    print(f"  mesh at ({mesh[0]:.2f}, {mesh[1]:.2f}), phases {a_off:.2f} / {b_off:.2f}")


if __name__ == "__main__":
    main()
