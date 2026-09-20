#!/usr/bin/env python3
"""Generate the close's horizon: the calendar ring, seen from far enough away.

    python Source/tools/make-poster-horizon.py

Writes Source/figures/poster-horizon.svg

WHY THIS EXISTS. The close had a flat field and nothing else, so the wordmark sat
on a colour rather than in a place. Both reference sites that end on a giant
wordmark give theirs a horizon and put the scene in front of it: Tempo's is a
luminous limb rising across the lower third with the footer links standing on its
face, Freebuff's is a ridgeline crossing the letters' feet. This is that idea in
Istor's own material rather than a borrowed landscape.

THE MATERIAL IS THE RING, NOT A HILL. The viewport's one drawn figure is already
the calendar ring at `where-it-stops`: 355 holes on a 4.602px pitch, and the
section's whole argument is that 354 and 355 are a difference the eye cannot
settle. So the horizon is the SAME circle at a radius twelve times larger, where
only its upper edge is in frame. Nothing is invented: same centre, same hole
count, same one dashed circle rather than 355 elements, and the disputed 355th
hole is marked at the apex exactly as it is marked on the plate. The motif
returns at the end of the page, and if a reader notices, it is because it is
meant to be noticed.

WHY THE RADIUS IS 1000 AND NOT 260. A limb reads as a limb only if it is much
larger than the frame, so the arc drops 306px across the half-width instead of
curving visibly like an arch. Not proportional to the plate: at 260 the beads
would be nearly four times their on-screen size on the plate and the horizon
would look like a necklace. The COUNT is the figure's content and it is
preserved; the pitch and the bead size are composition and they are not.

WHY THE APEX IS AT y=0. The stylesheet has to place this band so its apex meets
the wordmark, and the only place it can read the mark's height is in CSS, where
the wordmark's size is a clamp() and the SVG's height is a fraction of the
viewport. So the arithmetic that positions the apex is CSS's job and the
drawing's job is to put the apex on its own top edge, where the answer is zero at
every width. The halo above the arc is then the one thing the frame would crop,
which is why .poster-horizon sets overflow:visible and lets the glow sit over the
letters' feet. See the note in styles.css.

WHY EVERY EDGE FADES TO NOTHING. A stroked edge and a radial wash both end
somewhere, and a gradient that reaches the frame still opaque leaves a straight
line where the frame is. Every stop below finishes at zero inside the viewBox, so
the horizon dissolves rather than being cropped.

Inks are palette tokens, so this costs no new colour. Regenerate rather than
hand-edit: the console output below is the check that the arithmetic still holds.
"""

import gzip
import math
from pathlib import Path

VB_W, VB_H = 1440, 520      # the frame the poster spans; full width, one band
R = 1000.0                  # the limb. Much larger than the frame, hence a limb
APEX_Y = 0.0                # the arc crosses the vertical centre at the top edge
CX = VB_W / 2.0
CY = APEX_Y + R             # the circle of which we see only the top

HOLES = 355                 # the plate's count, carried over unchanged
DOT = 7.0                   # bead diameter; see the note above on proportions
PITCH = 2 * math.pi * R / HOLES
GAP = PITCH - 0.02

# Same rule as the plate: a circle path starts at 3 o'clock and the dashes run
# clockwise, so this rotation lands the LAST hole at 12 o'clock. That hole is the
# disputed one, and here it is the apex.
ALPHA = math.degrees((HOLES - 0.5) * PITCH / R)
THETA = -90.0 - ALPHA

# How far it falls from the apex to the left and right edges, which is the whole
# difference between a limb and an arch.
half = VB_W / 2.0
EDGE_Y = CY - math.sqrt(R * R - half * half)

# The wash, and why it is an ellipse centred BELOW the apex. A radial gradient
# centred on the apex is still at its brightest where it meets the frame's top
# edge, so the frame crops it mid-glow and leaves a straight line across the sky.
# Every shape here therefore has to finish at zero INSIDE the viewBox, and the
# nearest edge to the apex is only APEX_Y away. Pushing the centre down to the
# middle of the band and squashing the radius vertically buys the margin: the
# glow now ends 22px above the top edge and 22px above the bottom one, and 40px
# inside each side. Nothing is cropped, so nothing has an edge to see.
GLOW_CY = 260.0
GLOW_R = 680.0
GLOW_SQUASH = 0.35

# The depth layers: the mechanism's plates, sinking below the ring the visitor
# reads as the horizon. Concentric with the limb but smaller, so each apex sits
# lower (apex y = R minus its own radius), and each is fainter, so the eye
# stacks them as distance. Each carries the 355 holes at its own pitch, one
# dashed circle again, because the count is the figure's content at every depth.
# Freebuff's close stacks cloud behind cloud; Tempo's stacks atmosphere against
# the limb; this is the same depth cue in Istor's own material. Layers are
# (radius offset, stroke opacity, hole opacity): derived positions, tuned ink.
LAYERS = ((38, 0.30, 0.16), (90, 0.18, 0.09), (160, 0.10, 0.045))


def layer_arcs():
    out = []
    for off, line_op, dot_op in LAYERS:
        r = R - off
        pitch = 2 * math.pi * r / HOLES
        gap = pitch - 0.02
        # The arc, thin, and its row of holes under it: one dashed circle each.
        out.append('  <g class="horizon-layer">')
        out.append(f'    <circle cx="{CX:g}" cy="{CY:.1f}" r="{r:g}" fill="none" '
                   f'stroke="var(--field-ink)" stroke-width="1.4" '
                   f'stroke-opacity="{line_op:g}"/>')
        out.append(f'    <circle cx="{CX:g}" cy="{CY:.1f}" r="{r - 9:g}" fill="none" '
                   f'stroke="var(--field-ink)" stroke-width="4.2" '
                   f'stroke-opacity="{dot_op:g}" stroke-linecap="round" '
                   f'stroke-dasharray="0.02 {gap:.5f}" '
                   f'transform="rotate({THETA:.5f} {CX:g} {CY:.1f})"/>')
        out.append('  </g>')
    return "\n".join(out)


def circle(r, width, opacity, **extra):
    a = "".join(f' {k}="{v}"' for k, v in extra.items())
    return (f'<circle cx="{CX:g}" cy="{CY:.1f}" r="{r:g}" fill="none" '
            f'stroke="var(--field-ink)" stroke-width="{width:g}" '
            f'stroke-opacity="{opacity:g}"{a}/>')


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}"
     class="poster-horizon" aria-hidden="true" focusable="false">
  <!-- The calendar ring's 355 holes, at a radius that turns its arc into the
       close's horizon. Generated by Source/tools/make-poster-horizon.py — do not
       hand-edit; the geometry is arithmetic and the script prints its own check. -->
  <defs>
    <radialGradient id="poster-glow" gradientUnits="userSpaceOnUse"
                    cx="0" cy="0" r="{GLOW_R:g}"
                    gradientTransform="translate({CX:g} {GLOW_CY:g}) scale(1 {GLOW_SQUASH:g})">
      <stop offset="0" stop-color="var(--field-ink)" stop-opacity="0.09"/>
      <stop offset="0.45" stop-color="var(--field-ink)" stop-opacity="0.034"/>
      <stop offset="1" stop-color="var(--field-ink)" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- The wash: the face of the limb. Its centre is deliberately below the apex,
       so the glow arrives at neither edge of this viewBox and is never cropped
       into a straight line. See the note in make-poster-horizon.py. -->
  <rect width="{VB_W}" height="{VB_H}" fill="url(#poster-glow)"/>

  <!-- The mechanism's plates under the ring: concentric hole rows, each lower
       and fainter than the one above, which is how the eye reads depth in a
       stacked machine. See LAYERS in make-poster-horizon.py. -->
{layer_arcs()}

  <!-- The limb itself: four strokes of one circle, widest and faintest first. A
       stacked stroke rather than a blur filter, because a filter's cost and its
       result both vary by renderer and this has to look identical everywhere. -->
  <g>
    {circle(R, 58, 0.035)}
    {circle(R, 30, 0.055)}
    {circle(R, 14, 0.095)}
    {circle(R, 3.2, 0.3)}
  </g>

  <!-- All 355 holes along that edge, as one dashed circle. pathLength is not used
       so the dash arithmetic stays literal and cannot drift between renderers. -->
  <circle cx="{CX:g}" cy="{CY:.1f}" r="{R:g}" fill="none"
          stroke="var(--field-ink)" stroke-width="{DOT:g}" stroke-linecap="round"
          stroke-opacity="0.5" stroke-dasharray="0.02 {GAP:.5f}"
          transform="rotate({THETA:.5f} {CX:g} {CY:.1f})"/>

  <!-- The disputed hole, at the apex, in the plate's own --azure. The figure's
       single piece of information, as it is on the plate. -->
  <circle cx="{CX:g}" cy="{APEX_Y:g}" r="{DOT * 0.72:.2f}" fill="var(--azure)"/>
</svg>
'''

# Resolved from this file rather than from the shell's cwd, so the command in the
# docstring works from the repo root and from Source/tools alike. The ring
# generator next door is cwd-relative and needs `cd Source/tools` first.
out = Path(__file__).resolve().parent.parent / "figures" / "poster-horizon.svg"
out.write_text(svg, encoding="utf-8", newline="\n")

# The visible arc: the beads that fall inside the frame. Only the top of the
# circle is in shot, so this is what the visitor actually counts.
visible = 0
for k in range(HOLES):
    a = math.radians(THETA + 90.0 + math.degrees((k + 0.5) * PITCH / R))
    x, y = CX + R * math.cos(a), CY + R * math.sin(a)
    if 0 <= x <= VB_W and 0 <= y <= VB_H:
        visible += 1

n = len(svg.encode())
print(f"limb          R={R:g}  apex y={APEX_Y:g}  falls to y={EDGE_Y:.1f} at the edges")
print(f"              {EDGE_Y - APEX_Y:.1f}px of drop across {half:g}px half-width")
gl_top = GLOW_CY - GLOW_R * GLOW_SQUASH
gl_bot = GLOW_CY + GLOW_R * GLOW_SQUASH
print(f"wash          ends y={gl_top:.0f} to y={gl_bot:.0f}, x={CX - GLOW_R:.0f} to "
      f"{CX + GLOW_R:.0f} — inside the frame on every side")
print(f"              top margin {gl_top:.0f}px, bottom {VB_H - gl_bot:.0f}px, "
      f"sides {CX - GLOW_R:.0f}px")
print(f"holes         {HOLES} on the full circle, {visible} of them in frame")
print(f"layers        {len(LAYERS)} plates under the limb, apices at "
      f"{', '.join(f'y={off}' for off, _, _ in LAYERS)}")
print(f"pitch         {PITCH:.4f} px   ({360 / HOLES:.4f} deg per slot)")
print(f"svg           {n:,} bytes")
print(f"svg gzipped   {len(gzip.compress(svg.encode(), 9)):,} bytes")
print(f"written       Source/figures/{out.name}")
