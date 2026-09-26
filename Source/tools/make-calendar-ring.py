"""Generate the page's one drawn figure: the calendar ring, 355 holes.

    python Source/tools/make-calendar-ring.py

Writes Source/figures/calendar-ring.svg

Everything is arithmetic taken from the app's own captured answer — the disputed
hole count, 354 or 355, and nothing else. No plate layout, no gear positions,
nothing that would be scholarship rather than arithmetic, because a reader who
knows the mechanism would catch a drawing made up from memory.

The figure is a ground, not a diagram. It sits behind the opening of "Where it
stops", so the ring's interior holds the section's copy instead of 500px of
nothing, and the only loud thing in it is its single piece of information: the
three hundred and fifty-fifth hole.

Two inks, and the split is between what the figure asserts and what it frames.
The rim circles are `--rule`, the page's hairline, and they stay a whisper: they
are the plate's edge and nothing depends on them. The 355 holes are `--ink-3`,
because they are the subject and because at `--rule` they measured 1.20:1
against the page's `--paper` — invisible on a normal screen, while every caption
in the act talks about them. Two tokens, both already in the palette, so this
costs no new colour.

354 and 355 holes are 1.0141 degrees apart end to end, so the two rings are
visually identical — the disagreement that overturned a hundred years of work is
a difference the eye cannot settle. That is the caption, and it is why this is a
ring of 355 with one hole marked rather than two rings drawn side by side.
"""

import gzip
import math
from pathlib import Path

VB_W, VB_H = 594, 440    # the reading column's measure, and the header block's height
CX, CY = 297.0, 360.0    # centre pushed below the frame so only the upper plate shows
R_BAND_OUT, R_BAND_IN = 272.0, 248.0
R_HOLES = (R_BAND_OUT + R_BAND_IN) / 2      # 260 — beads run mid-band
HOLES = 355
DOT = 2.8                # stroke-width; with linecap:round this is the hole diameter

C = 2 * math.pi * R_HOLES
PITCH = C / HOLES        # 4.602 px per hole slot
GAP = PITCH - 0.02       # 0.02 is the dash; round caps draw the bead

# Put the disputed hole — the last of the 355 — at 12 o'clock. A circle path starts
# at 3 o'clock and runs clockwise, so the ring turns by whatever that takes.
ALPHA = math.degrees((HOLES - 0.5) * PITCH / R_HOLES)
THETA = -90.0 - ALPHA


def pt(r, deg):
    a = math.radians(deg)
    return CX + r * math.cos(a), CY + r * math.sin(a)


mx, my = pt(R_HOLES, -90.0)
t1 = pt(R_BAND_OUT, -90.0)
t2 = pt(R_BAND_OUT + 14, -90.0)
lx, ly = pt(R_BAND_OUT + 27, -90.0)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}"
     class="ring-plate" aria-hidden="true" focusable="false">
  <!-- The calendar ring, 355 holes. Geometry is arithmetic from the app's own
       answer; the count in dispute is the only thing marked. Regenerate with
       Source/tools/make-calendar-ring.py — do not hand-edit. -->

  <g fill="none" stroke="var(--rule)" stroke-width="1">
    <circle class="ring-frame" cx="{CX:g}" cy="{CY:g}" r="{R_BAND_OUT:g}"/>
    <circle class="ring-frame" cx="{CX:g}" cy="{CY:g}" r="{R_BAND_IN:g}"/>
  </g>

  <!-- 355 holes in one dashed circle rather than 355 elements. pathLength is not
       used, so the dash arithmetic is literal and cannot drift between renderers.
       ink-3 because the holes are the subject, not the frame: at rule they
       measured 1.20:1 on paper. Why, in full, is in make-calendar-ring.py.
       class=ring-holes: M12's roll, one dash period, styles.css motion block. -->
  <circle class="ring-holes" cx="{CX:g}" cy="{CY:g}" r="{R_HOLES:g}" fill="none"
          stroke="var(--ink-3)" stroke-width="{DOT:g}" stroke-linecap="round"
          stroke-dasharray="0.02 {GAP:.6f}"
          transform="rotate({THETA:.4f} {CX:g} {CY:g})"/>

  <!-- The hole in question: the figure's only azure, and the one thing in it that
       is a claim rather than a measure. class=ring-claim: lands last in M12. -->
  <g class="ring-claim">
    <circle cx="{mx:.4f}" cy="{my:.4f}" r="{DOT / 2:.2f}" fill="var(--azure)"/>
    <path d="M{t1[0]:.3f} {t1[1]:.3f} L{t2[0]:.3f} {t2[1]:.3f}"
          stroke="var(--azure)" stroke-width="1" fill="none"/>
    <text x="{lx:.3f}" y="{ly:.3f}" fill="var(--azure)" font-size="13"
          font-family="Inter, sans-serif" text-anchor="middle"
          dominant-baseline="middle">355</text>
  </g>
</svg>
'''

# Anchored to this file rather than to the shell's directory. This wrote to
# "../figures/" until 2026-09-20, which resolves correctly only when the tool is
# run from Source/tools and, from the repository root the docstring names, lands in
# the repository's PARENT: outside the project, on a path nobody would look at.
OUT = Path(__file__).resolve().parent.parent / "figures" / "calendar-ring.svg"
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)

n = len(svg.encode())
print(f"holes         {HOLES}")
print(f"pitch         {PITCH:.4f} px   ({360 / HOLES:.4f} deg per slot)")
per_354, per_355 = 360 / 354, 360 / 355
print(f"354 vs 355    {per_354:.4f} deg per hole vs {per_355:.4f} "
      f"— {per_354 - per_355:.4f} deg apart")
print(f"rotation      {THETA:.4f} deg to bring hole {HOLES} to 12 o'clock")
print(f"svg           {n:,} bytes")
print(f"svg gzipped   {len(gzip.compress(svg.encode(), 9)):,} bytes")
print(f"written       {OUT.relative_to(OUT.parents[2])}")
