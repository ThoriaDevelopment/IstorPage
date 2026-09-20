#!/usr/bin/env python3
"""Generate the mechanism icon masters: the site's crown, small.

    python Source/tools/make-mechanism-icon.py [--self-test]

Writes (both committed; these are MASTERS, not the favicon outputs themselves):

    Assets/brand/istor-gear.svg      the small-slot master (<=32px), var() contract
    Assets/brand/istor-gear-lg.svg   the large-slot master (>=48px), var() contract

WHY THIS EXISTS. The tab icon is the last brand surface that predates the
mechanism: the eye and the witnessed page are the app's marks, and the site
that argues from the Antikythera mechanism shows a *document* in a browser tab.
The mechanism now opens the page, runs through it, closes it, and draws the
share card; the icon set is the one surface it never reached.

THE MARK IS THE SITE'S OWN CROWN, not a generic gear. A gear clip-art would be
any project's icon; this one is the wheel the page argues from, with the tooth
count that means something: 223 teeth would be invisible at 16px (0.45 degrees
of pitch), so the master carries the count that READS - 24 teeth, the calendar
ring's own count per quadrant of the page's plate figure - and records the
compromise here, as the figure files record theirs. The ARITHMETIC is still the
mechanism's: one module, teeth as radial intervals on the pitch circle, and a
pinion of 8 biting it externally - the hero's own 223:48 relation reduced to
counts that survive rasterisation. The self-test asserts the mesh at the
contact point, because an icon of gears that do not mesh is worse than no icon.

TWO MASTERS, ONE GEOMETRY, the same split the eye/page pair makes: <=32px gets
a fat single wheel with a bold hub (a pinion at 16px is 4px of noise); >=48px
gets the wheel AND the pinion, because there the bite is the subject - two
wheels turning is "it shows you what it saw" at icon scale.

THE CONTRACT IS THE EYE/PAGE CONTRACT: `var(--mark-ink, ...)`,
`var(--mark-paper, ...)`, `var(--mark-accent, ...)` with the same fallbacks the
other masters carry, so make-favicons.py's literalize() and dark block work
verbatim. Accent takes the iris slot's meaning: the one colour the mark is
allowed, spent on the pinion - the moving part.

Ink weights: the page's plate draws its ring in 1.5-2.4/64 stroke; an icon
needs 4.5/64 at <=32 (2.5px rendered at 16 - the floor for a tab icon on
Windows' 125% scaling) and 3.2/64 at >=48. Measured against the existing
masters' 6.7/64 eye outline and 3.6/64 page outline.
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BRAND = ROOT / "Assets" / "brand"

OUT_SMALL = BRAND / "istor-gear.svg"
OUT_LARGE = BRAND / "istor-gear-lg.svg"

# Counts that survive rasterisation, from the mechanism's own relations:
# 16 teeth on the small master (24 pitched the teeth 1.9 user units apart and
# they merged into a solid ring at 16px - measured on the raster, not guessed),
# 24 on the large one where there is room; 8 is the same 3:1 step the hero's
# 223:48 drive is, rounded to a count that renders. The REAL counts (223/48)
# are recorded in the SVG comment so the compromise lives where the art is.
N_WHEEL = 16
N_PINION = 8

VB = 64.0            # both masters share the eye/page 64-unit box
STROKE_S = 4.5       # small master: survives 16px
STROKE_L = 3.2       # large master: the page outline's own weight

# Geometry: the wheel's pitch circle at R=23 centred slightly low-left; the
# pinion bites it externally at the upper-right bearing, the composition the
# hero's band uses. Pinion radius from the SHARED MODULE.
R_WHEEL = 23.0
PITCH = 2 * math.pi * R_WHEEL / N_WHEEL
R_PINION = N_PINION * PITCH / (2 * math.pi)
THETA = math.radians(42.0)          # the bite's bearing from the wheel's centre
CENTRE_DIST = R_WHEEL + R_PINION    # external mesh


def centres():
    cx, cy = VB / 2 - 2.0, VB / 2 + 2.0
    px = cx + CENTRE_DIST * math.sin(THETA)
    py = cy - CENTRE_DIST * math.cos(THETA)
    return (cx, cy), (px, py)


def teeth(centre, radius, n, phase_deg=0.0, length=2.2):
    """Tooth marks as short radial strokes ON the pitch circle.

    A tick CENTRED on the pitch circle is half inside it - at 16px that half
    vanishes into the rim's own stroke and the teeth melt away. The hero's
    generator fixes this by putting the dash's FULL depth outside the pitch
    (stroke-width centred on the circle), so the tick runs from the rim
    outward: r to r+length, not r-length to r+length.
    """
    cx, cy = centre
    out = []
    step = 360.0 / n
    for i in range(n):
        a = math.radians(phase_deg + i * step)
        r0, r1 = radius - 1.0, radius + length
        out.append(
            f"M{cx + r0 * math.cos(a):.2f} {cy + r0 * math.sin(a):.2f}"
            f"L{cx + r1 * math.cos(a):.2f} {cy + r1 * math.sin(a):.2f}")
    return " ".join(out)


def spokes(centre, inner, angles):
    """Lines from the hub circle out to the rim's inner edge.

    The hero's figure: three on a pinion, four on a wheel, and the reason is
    the same at both scales - a plain ring rotated by a few degrees reads as
    nothing, spokes give the eye something that moves.
    """
    cx, cy = centre
    out = []
    for a_deg in angles:
        a = math.radians(a_deg)
        r0 = 5.2
        out.append(
            f"M{cx + r0 * math.cos(a):.2f} {cy + r0 * math.sin(a):.2f}"
            f"L{cx + inner * math.cos(a):.2f} {cy + inner * math.sin(a):.2f}")
    return " ".join(out)


def phase_for(centre, radius, mesh, want_tooth, n):
    """The phase (in degrees) putting a tooth CENTRE on the mesh bearing.

    `want_tooth` is which tooth of the pattern lands there; the wheel uses
    tooth 0, the pinion then needs a GAP at the same world bearing, which is
    half a step around its own pitch circle from any tooth - solved here as
    the pinion's phase, not nudged.
    """
    dx, dy = mesh[0] - centre[0], mesh[1] - centre[1]
    brg = math.degrees(math.atan2(dy, dx))
    return brg - want_tooth * (360.0 / n)


def svg_master(large: bool) -> str:
    n_wheel = N_WHEEL if large else 16
    stroke = STROKE_L if large else STROKE_S
    # tick length scales with the stroke so teeth stay teeth at both slots
    tick = 2.6 if large else 3.4
    (cx, cy), (px, py) = centres()
    mesh = (cx + R_WHEEL * math.sin(THETA), cy - R_WHEEL * math.cos(THETA))
    wheel_phase = phase_for((cx, cy), R_WHEEL, mesh, 0, n_wheel)
    # The pinion needs a GAP centre at the mesh bearing: its tooth pattern
    # must sit half a step off the bearing, which is 180/N_PINION degrees.
    pinion_phase = phase_for((px, py), R_PINION, mesh, 0, N_PINION) + 180.0 / N_PINION

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="512" height="512">',
        '  <!-- Istor · the mechanism ({} slot)'.format('large, >= 48 px' if large else 'small, <= 32 px'),
        '       The site\'s crown: the wheel the page opens, closes and argues from.',
        f'       Counts are the ones that READ at raster size ({n_wheel} and {N_PINION}: the',
        '       calendar ring\'s family and the hero drive\'s 3:1 step, stepped down to',
        '       what survives 16px - 24 pitched the teeth 1.9 units apart and they',
        '       merged into a solid ring, measured on the raster). The REAL drive is',
        '       223:48. One module: the pinion\'s radius is N*P/2pi from the',
        '       wheel\'s own, the centre distance is the sum, and the phases are solved',
        '       so a wheel tooth meets a pinion gap at the contact. Same var() contract',
        '       as istor-page.svg; mark-accent takes the iris slot\'s meaning and is',
        '       spent on the pinion, the moving part. -->',
        '  <g fill="none" stroke="var(--mark-ink, #171717)"',
        f'     stroke-width="{stroke}" stroke-linecap="round">',
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R_WHEEL:.2f}"/>',
        # the hub: 4 spokes from a small hub out to the rim - the hero's idiom,
        # and what tells a turning wheel from a stamped O at a glance
        f'    <path d="{spokes((cx, cy), R_WHEEL - 2.0, [45, 135, 225, 315])}"/>',
        f'    <path d="{teeth((cx, cy), R_WHEEL, n_wheel, wheel_phase, tick)}"/>',
    ]
    if large:
        parts += [
            '    <g stroke="var(--mark-accent, #F2726F)">',
            f'      <circle cx="{px:.2f}" cy="{py:.2f}" r="{R_PINION:.2f}"/>',
            f'      <path d="{teeth((px, py), R_PINION, N_PINION, pinion_phase, tick * 0.8)}"/>',
            f'      <circle cx="{px:.2f}" cy="{py:.2f}" r="2.6" fill="var(--mark-accent, #F2726F)" stroke="none"/>',
            '    </g>',
        ]
    else:
        # <=32px: one wheel, bold hub. The pinion is 4px of noise at 16.
        parts += [
            f'    <path d="{spokes((cx, cy), R_WHEEL - 2.0, [45, 135, 225, 315])}"/>',
            f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.6" fill="var(--mark-accent, #F2726F)" stroke="none"/>',
        ]
    parts.append('  </g>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main():
    if "--self-test" in sys.argv:
        (cx, cy), (px, py) = centres()
        d = math.hypot(px - cx, py - cy)
        assert abs(d - CENTRE_DIST) < 1e-9, "centre distance is not R1+R2: not a mesh"
        # module shared: R2 from the wheel's own pitch
        assert abs(R_PINION - N_PINION * PITCH / (2 * math.pi)) < 1e-9
        # counts that render, recorded against the real drive
        assert N_WHEEL == 16 and N_PINION == 8
        assert 16 <= N_WHEEL <= 64 and N_WHEEL % 8 == 0, "wheel count drifted"
        print(f"self-test ok - external mesh at distance {CENTRE_DIST:.2f}, "
              f"module {PITCH:.3f}, pinion R {R_PINION:.2f}")
    OUT_SMALL.write_bytes(svg_master(large=False).encode("utf-8"))
    OUT_LARGE.write_bytes(svg_master(large=True).encode("utf-8"))
    print(f"{OUT_SMALL.relative_to(ROOT)} written: {OUT_SMALL.stat().st_size:,} B")
    print(f"{OUT_LARGE.relative_to(ROOT)} written: {OUT_LARGE.stat().st_size:,} B")


if __name__ == "__main__":
    main()
