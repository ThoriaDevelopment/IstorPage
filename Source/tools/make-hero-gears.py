#!/usr/bin/env python3
"""Generate the hero's world: the mechanism the product window stands on.

    python Source/tools/make-hero-gears.py

Writes Source/figures/hero-gears.svg

WHY THIS EXISTS. Every reference hero stands on a world. Tempo's product floats
over a planet limb, Freebuff's over an illustrated landscape, and both crop the
world so it reads as larger than the frame. Istor's hero stood on a gradient:
the page's most expensive real estate carried type and a window and nothing the
reader could look at.

The world this site owns is the Antikythera mechanism, because the page already
argues from it: the hero's own answer opens on the Saros cycle, the evidence act
prints the calendar ring it was fitted from, and the name act descends from the
word for a witness. What the page had never once shown is the part that makes it
a machine rather than a dial: the gearing.

THE COUNTS ARE THE MECHANISM'S, NOT INVENTED FOR THE DRAWING. 223 is its
largest gear, "about 13 cm in diameter and originally had 223 teeth" (the
fragment A wheel, measured); 48 is the count of the wheel that drives it in the
published reconstruction. Both are in the literature the page's library is built
from, and the page's own text already prints 223 as the Saros cycle's length in
months, so the artwork's numbers came from the same place its prose did.

TWO PINIONS RIDE THE ONE WHEEL, AND THAT IS THE DRAWING'S CHOICE, NOT A CLAIM
ABOUT THE TRAIN. The band wants a balanced composition, and a second 48-tooth
wheel on the other flank gives it one. Nothing in the page says which wheel
drives which, and the figure is decorative: it carries no title, no caption, and
`aria-hidden`, so no reader is told anything by it that the page has not said in
words it can check. THIS IS THE ONE PLACE THE ARTWORK IS ARRANGED RATHER THAN
OBSERVED, and it is recorded here because the file's own rule is that choices
get written down.

THE COMPOSITION IS ARITHMETIC, so that nothing is cropped by accident. The
viewBox is 1440x420. The great wheel's CROWN is placed exactly at y = 40, which
is where the window's bottom edge lands: 40 is `--world-overlap` in
styles.css, and this file READS THAT TOKEN rather than repeating it, because two
numbers that must agree can only be one. Tangent is the point: the wheel's top
meets the plate's edge, so the product touches the world without either one
cutting the other, and the wheel then runs off the page's own bottom edge, which
is where a world should end.

    crown            = OVERLAP                        = 40  (the plate's edge)
    pitch        P   = 2*pi*R1/N1 = 2*pi*505/223      = 14.2289
    pinion       R2  = N2*P/(2*pi) = 48*P/(2*pi)      = 108.71
    centre           = C1.y - R1 = 545 - 505          = 545, i.e. R1 + OVERLAP
    centre distance  = R1 + R2                        = 613.71
    exits bottom at  x = 720 +/- sqrt(505^2 - 125^2)  = 230.7 and 1209.3

The pinions are placed by requiring their centres to sit at y = 240: high enough
that a 108.71 radius is fully inside the band (no straight chord cut across a
wheel, which is what a layer's own box does to anything that overflows it), and
low enough that they meet the great wheel on its flanks rather than at its
crown, where a meshing wheel would have to sit above the band. Solving for that
y gives sin(theta) = (545-240)/613.71, so:

    theta = 29.81 deg,  C2 = (720 -/+ 532.6, 240) = (187.4, 240) and (1252.6, 240)
    mesh points          (281.8, 294.0) and (1158.2, 294.0)

THE TEETH ARE A DASH PATTERN, AND THAT IS THE WHOLE BYTE ARGUMENT. 223 teeth as
223 <path> elements is about 9 KB of coordinates for one wheel; the same teeth as
a circle stroked at the tooth's depth with `stroke-dasharray: tooth gap` is 90
bytes, and it is a truer drawing: the dashes are radial rectangles on the pitch
circle, which is what a cut tooth is. The dash pattern is the shared module P, so
both wheels carry the same one, and the phase of each is solved rather than
nudged: a tooth CENTRE of the great wheel must meet a GAP CENTRE of the pinion at
each mesh point, which is what `dashoffset` below computes from the arc length
between each circle's start and its mesh point.

That phase is also why the two wheels can turn and stay meshed. Arc length is
what meshing preserves, so a rotation of the great wheel by psi moves the pattern
at the mesh point by R1*psi and the pinion by R2*(R1/R2)*psi in the other
direction: the difference is invariant, and the teeth interleave at every angle.
The script drives exactly that relation, so this is a geared drawing and not a
drawing of gears.

Ink comes from the field's own tokens in styles.css, not from this file, so the
figure switches with the page's grounds like every other generated plate.
"""

import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "figures" / "hero-gears.svg"
CSS = HERE.parent / "styles.css"

W, H = 1440.0, 420.0          # the band, in SVG units; matches --world-h's ceiling

N1 = 223                      # the mechanism's largest gear
N2 = 48                       # the wheel that drives it in the reconstruction
R1 = 505.0                    # pitch radius, from the crown's placement below
P = 2 * math.pi * R1 / N1     # the module: every wheel shares it
R2 = N2 * P / (2 * math.pi)
PINION_Y = 240.0              # pinion centres, so neither wheel is cut by the box


def world_overlap():
    """`--world-overlap` out of styles.css, in pixels.

    The crown is placed against this number, so the file reads it instead of
    repeating it. A hardcoded 40 here would be a second copy of a token that
    moves: the failure mode is a wheel hanging three pixels off the plate's edge,
    which looks like a drawing that was eyeballed, because it would have been.
    """
    text = CSS.read_text(encoding="utf-8")
    m = re.search(r"--world-overlap:\s*(\d+(?:\.\d+)?)px", text)
    if not m:
        raise SystemExit(f"no --world-overlap found in {CSS}")
    return float(m.group(1))


OVERLAP = world_overlap()
C1 = (720.0, R1 + OVERLAP)    # so the crown's top is the window's bottom edge

TOOTH = P * 0.5               # half the pitch: square-cut, and the gap is the rest
DEPTH = P * 0.75              # radial tooth height, under the pitch, as cut bronze is
# The rim is drawn three ways: a faint band for the metal, then its two edges as
# hairlines. A band alone reads as a pipe; edges alone leave the metal empty and
# the teeth looking like ticks on a wire. Both, at these weights, read as bronze.
RIM = 24.0                    # the solid rim under the roots
FACE = 18.0                   # the pinion's inner rim
ARBOR = 16.0                  # the pinion's hub
SPOKES = [210, 240, 270, 300, 330]   # the great wheel's, every 30 deg, all upward


def mesh_phase(centre, radius, mesh, want):
    """`stroke-dashoffset` that puts `want` of the pattern at the mesh point.

    A circle's path starts at (cx + r, cy) and runs clockwise, which is
    increasing angle in this file's y-down coordinates, so the arc length from
    the start to a point is r * phi. A dash starts where (s + offset) is a
    multiple of the pattern, a tooth CENTRE at half the tooth, a GAP CENTRE at
    one and a half: `want` is that fraction of the pattern, and the offset is
    solved from it. Returns a value in [0, pitch) because the pattern repeats.
    """
    dx, dy = mesh[0] - centre[0], mesh[1] - centre[1]
    phi = math.atan2(dy, dx) % (2 * math.pi)
    s = radius * phi
    return ((want * P) - s) % P


def spokes(centre, inner, angles):
    """Lines from the hub out to a rim's inner edge.

    Three of these on a pinion are what make its rotation readable at a glance;
    five of them on the great wheel are what make the arcs read as a WHEEL and
    not as a hill. Both are structural, and both are drawn from the hub rather
    than floating: the great wheel's hub is 300 units below the band, so its
    spokes enter the band from its bottom edge, which is the drawing saying that
    the machine continues past the page.
    """
    out = []
    for a_deg in angles:
        a = math.radians(a_deg)
        x1, y1 = centre[0] + ARBOR * math.cos(a), centre[1] + ARBOR * math.sin(a)
        x2, y2 = centre[0] + inner * math.cos(a), centre[1] + inner * math.sin(a)
        out.append(f'M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}')
    return " ".join(out)


def pinion(centre, offset, name):
    """One 48-tooth wheel: teeth, rim, hub and three spokes.

    The spokes are not decoration: a plain toothed ring rotated by a few degrees
    reads as nothing at all. Spokes give the eye something that moves.
    """
    cx, cy = centre
    root = R2 - DEPTH / 2
    inner = root - FACE
    arms = spokes(centre, inner, [30, 150, 270])
    return (
        f'  <g data-gear-b="{name}" data-gear-cx="{cx:.2f}" data-gear-cy="{cy:.2f}">\n'
        f'    <circle class="gear-tooth" cx="{cx:.2f}" cy="{cy:.2f}" r="{R2:.2f}"\n'
        f'            stroke-width="{DEPTH:.2f}" stroke-dasharray="{TOOTH:.2f} {TOOTH:.2f}"\n'
        f'            stroke-dashoffset="{offset:.2f}"/>\n'
        f'    <circle class="gear-band" cx="{cx:.2f}" cy="{cy:.2f}" r="{inner + FACE / 2:.2f}"\n'
        f'            stroke-width="{FACE:.2f}"/>\n'
        f'    <circle class="gear-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{root:.2f}"/>\n'
        f'    <circle class="gear-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{inner:.2f}"/>\n'
        f'    <path class="gear-face" d="{arms}"/>\n'
        f'    <circle class="gear-rim" cx="{cx:.2f}" cy="{cy:.2f}" r="{ARBOR:.2f}"/>\n'
        f'  </g>\n'
    )


def mesh_check(turn_deg, sense=-1.0):
    """Do the teeth still interleave after the wheels turn?

    The script rotates the great wheel by psi and the pinion by psi*N1/N2 the
    OTHER way, which is what external gearing is; `sense` is the sign of that
    rotation. What this checks is that the dash phases hold through it.

    A tooth is a MATERIAL interval of the pitch circle, so what matters is which
    material sits at the mesh point after the turn. The pattern is rigid with the
    wheel, so the pattern coordinate at a screen angle phi is R*(phi - turn) plus
    the wheel's own dashoffset, and the two wheels' coordinates add up: the turn
    cancels, so the sum is invariant and the phase relationship at the mesh point
    never changes. That sum is what the caller asserts on.

    `sense` exists to make the check falsifiable. Pass +1 and the pinion turns the
    way a wheel meshing from the INSIDE would: the sum stops being invariant and
    the assertion fails. A check that cannot fail is not a check.
    """
    sin_t = (C1[1] - PINION_Y) / (R1 + R2)
    theta = math.asin(sin_t)
    off = (R1 + R2) * math.cos(theta)
    left_c = (C1[0] - off, PINION_Y)
    left_m = (C1[0] - R1 * math.cos(theta), C1[1] - R1 * sin_t)
    a_off = mesh_phase(C1, R1, left_m, 0.5)
    b_off = mesh_phase(left_c, R2, left_m, 1.5)

    phi_a = math.atan2(left_m[1] - C1[1], left_m[0] - C1[0]) % (2 * math.pi)
    phi_b = math.atan2(left_m[1] - left_c[1], left_m[0] - left_c[0]) % (2 * math.pi)
    psi = math.radians(turn_deg)
    u_a = (R1 * phi_a - R1 * psi + a_off) % P
    u_b = (R2 * phi_b - sense * R1 * psi + b_off) % P
    return u_a, u_b, (u_a + u_b) % P


def main():
    sin_t = (C1[1] - PINION_Y) / (R1 + R2)
    theta = math.asin(sin_t)
    off = (R1 + R2) * math.cos(theta)
    left_c = (C1[0] - off, PINION_Y)
    right_c = (C1[0] + off, PINION_Y)
    left_m = (C1[0] - R1 * math.cos(theta), C1[1] - R1 * sin_t)
    right_m = (C1[0] + R1 * math.cos(theta), C1[1] - R1 * sin_t)

    # The great wheel: a tooth centre at the LEFT mesh point (the right one gets
    # its own phase from the same wheel, so the pinion is solved to match it).
    a_off = mesh_phase(C1, R1, left_m, 0.5)
    bl_off = mesh_phase(left_c, R2, left_m, 1.5)   # a gap centre meets that tooth
    br_off = mesh_phase(right_c, R2, right_m, 1.5)

    root1 = R1 - DEPTH / 2
    inner1 = root1 - RIM
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 420"\n'
        '     class="hero-gears" preserveAspectRatio="xMinYMid slice"\n'
        '     focusable="false" aria-hidden="true">\n'
        '  <!-- Generated by Source/tools/make-hero-gears.py -- do not hand-edit.\n'
        '       223 teeth and 48: the mechanism\'s largest gear and the wheel that\n'
        '       drives it. The band is 1440x420 and the geometry is in that file,\n'
        '       including why the pinions sit at y = %.0f. -->\n' % PINION_Y
        + f'  <g data-gear-a="223" data-gear-cx="{C1[0]:.2f}" data-gear-cy="{C1[1]:.2f}">\n'
        + f'    <circle class="gear-tooth" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{R1:.2f}"\n'
        + f'            stroke-width="{DEPTH:.2f}" stroke-dasharray="{TOOTH:.2f} {TOOTH:.2f}"\n'
        + f'            stroke-dashoffset="{a_off:.2f}"/>\n'
        + f'    <circle class="gear-band" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{inner1 + RIM / 2:.2f}"\n'
        + f'            stroke-width="{RIM:.2f}"/>\n'
        + f'    <circle class="gear-rim" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{root1:.2f}"/>\n'
        + f'    <circle class="gear-rim" cx="{C1[0]:.2f}" cy="{C1[1]:.2f}" r="{inner1:.2f}"/>\n'
        + f'    <path class="gear-face" d="{spokes(C1, inner1, SPOKES)}"/>\n'
        + '  </g>\n'
        + pinion(left_c, bl_off, "48-left")
        + pinion(right_c, br_off, "48-right")
        + '</svg>\n'
    )
    if "--self-test" in sys.argv:
        # The sum must be the same at every angle, because that is the alignment
        # the teeth interleave on. The second run flips the pinion's sense and
        # must move it, or the first run is measuring nothing.
        # Compared modulo the pitch, because the sum lives on a circle: two
        # phases a hair either side of 0/one full pitch are the same alignment,
        # and a bare `set()` calls them different. That is the same trap as
        # reading a clock's 11:59 and 12:01 as two hours apart.
        def drift(values):
            return max(abs(((v - values[0] + P / 2) % P) - P / 2) for v in values)

        angles = (0, 2, 4, 8)
        base = [mesh_check(t)[2] for t in angles]
        wrong = [mesh_check(t, sense=1.0)[2] for t in angles]
        assert drift(base) < 1e-9, f"mesh phase drifts across rotation: {base}"
        assert drift(wrong) > 0.1, "the flipped rotation did not move the phase"
        print(f"self-test ok - mesh sum held to {drift(base):.2e} of a pitch at "
              f"0/2/4/8 deg, and the wrong sense moved it to {wrong[-1]:.2f}")

    OUT.write_bytes(svg.encode("utf-8"))
    print(f"{OUT.relative_to(OUT.parents[2])} written: {len(svg)} B")
    print(f"  module {P:.4f}  R2 {R2:.2f}  theta {math.degrees(theta):.2f} deg")
    print(f"  mesh points ({left_m[0]:.1f}, {left_m[1]:.1f}) and ({right_m[0]:.1f}, {right_m[1]:.1f})")
    print(f"  phases {a_off:.2f} / {bl_off:.2f} / {br_off:.2f}")


if __name__ == "__main__":
    main()
