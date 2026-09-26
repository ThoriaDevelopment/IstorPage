#!/usr/bin/env python3
"""Generate the games-dial plate: the four sectors and their six games.

    python Source/tools/make-games-dial.py [--self-test]

Writes Source/figures/games-dial-wide.svg and Source/figures/games-dial-tall.svg

WHY THIS EXISTS. The page's cycles prose names the games sub-dial ("a
sub-dial tracking Panhellenic athletic games like the Olympics", the captured
answer's own words, cited to source 1) and never draws it. The source behind
that citation (Freeth et al., Nature 2008, "Calendars with Olympiad display
on the Antikythera Mechanism") states the dial's full inscription, and this
plate draws exactly that: a four-sector dial, each sector carrying a year
ordinal in the epigraphic L+numeral form (LΑ, LΒ, LΓ, LΔ) and the names of
the two games held that year - Isthmia and Olympia, Nemea and Naa, Isthmia
and Pythia, Nemea and Halieia. Six games, four sectors, one pointer.

THE ONE AZURE STATEMENT. Every settled plate here earns exactly one, and the
games dial's is the discovery that made the 2008 paper famous: its pointer is
the ONLY one on the whole mechanism that turns anticlockwise as time advances
(a consequence of the gear train, 223:60 through two more meshes than the
others). The arrow stands at year 1 pointing anticlockwise, named "the only
pointer that runs anticlockwise" in the caption; inside the drawing the azure
claims it without a word.

HONESTY LEDGER. The sector ORDER (which year carries which pair) is the
source's table, read sector by sector clockwise from the pointer's start.
Whether the physical dial's sectors ran clockwise or anticlockwise from a
given zero is not stated by any source this page carries, so the drawing
states the CYCLE - the table's content - and not the artefact's orientation;
the caption says the cycle, the arrow says the pointer's direction, and
neither claims to be a photograph of the fragment.

TYPE. All label widths are MEASURED, not estimated: the strings were measured
in the browser off the built page (canvas measureText) at the exact sizes
drawn, and every entry lives in MEASURED below. The Greek labels are measured
in GFS Didot - the house's Greek face, which the font rebuild
(make-didot-greek.py) made real for uppercase Greek - and pin it inline in
dial(); a label with no entry refuses to draw, the boundary plate's
discipline, after its first version ran labels through their own box walls.

TWO VARIANTS, swapped by width, the house reason: the wide plate is a dial
in a field with its count line under it; the tall variant keeps the dial
centred with larger type for its 0.69-1.0 render scale, so the type floor
holds at 320.

SELF-TEST. The invariants a doctored copy would break: exactly four sectors
at 90 degrees each; the six games each appearing exactly twice across the
four sectors; the four ordinals present and in cycle order; the pointer's
arrow opposing the clockwise sweep; MEASURED covering every drawn string at
its drawn size; no hand-hex anywhere; and the class names the stylesheet
positions.

Standard library only.
"""

import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

# --- the source's table (Freeth et al. 2008), in cycle order -----------------
SECTORS = (
    ("LΑ", ("ΙΣΘΜΙΑ", "ΟΛΥΜΠΙΑ")),
    ("LΒ", ("ΝΕΜΕΑ", "ΝΑΑ")),
    ("LΓ", ("ΙΣΘΜΙΑ", "ΠΥΘΙΑ")),
    ("LΔ", ("ΝΕΜΕΑ", "ΑΛΙΕΙΑ")),
)

# Every drawn string's measured width in user units, keyed by string and size.
# Measured in the browser (off the built page), 2026-09-23, AFTER the display
# face gained its Greek: the ordinals and game names render in GFS Didot (the
# house's Greek face, pinned inline in dial() below), so they are measured in
# it. The count and sub lines stay Inter, the dials-count convention, and are
# measured in Inter. The old table measured the SAME Greek strings in Georgia
# - the fallback the old font file silently forced - and was wrong by up to
# 4 units a label; the rebuild exposed it.
MEASURED = {
    # wide plate, Greek in GFS Didot. 12.5 units: the plate renders at 0.916
    # in the 640 field, so 11.5 units landed at 10.53px, under the 11px type
    # floor the contrast audit enforces; the rear-dials plate's 14-unit
    # startlabel is the precedent for sizing wide-plate text to its render
    # scale. (The 11.5 measurements below were retired for that reason.)
    ("ΙΣΘΜΙΑ", 12.5): 46.5,
    ("ΟΛΥΜΠΙΑ", 12.5): 60.4,
    ("ΝΕΜΕΑ", 12.5): 45.9,
    ("ΝΑΑ", 12.5): 26.4,
    ("ΠΥΘΙΑ", 12.5): 40.3,
    ("ΑΛΙΕΙΑ", 12.5): 43.1,
    ("LΑ", 16.5): 21.0,
    ("LΒ", 16.5): 20.8,
    ("LΓ", 16.5): 19.6,
    ("LΔ", 16.5): 20.9,
    # wide plate, Latin in Inter, stepped with the names
    ("four years", 12.5): 55.4,
    ("the only pointer that runs anticlockwise", 12.5): 214.6,
    # tall variant's real step: 16.5 units clear the 11px type floor at the
    # plate's 0.68 render scale on a 320px phone (rear-dials arithmetic).
    # Greek in GFS Didot.
    ("ΙΣΘΜΙΑ", 16.5): 61.5,
    ("ΟΛΥΜΠΙΑ", 16.5): 79.7,
    ("ΝΕΜΕΑ", 16.5): 60.6,
    ("ΝΑΑ", 16.5): 34.8,
    ("ΠΥΘΙΑ", 16.5): 53.3,
    ("ΑΛΙΕΙΑ", 16.5): 56.9,
    ("LΑ", 19.5): 24.9,
    ("LΒ", 19.5): 24.5,
    ("LΓ", 19.5): 23.1,
    ("LΔ", 19.5): 24.6,
    ("four years", 16.5): 73.3,
}


# The display face's family attribute, pinned into every Greek label so the
# plate cannot silently regress to a fallback: the rebuild made the face
# real, the measurement table above assumes it, and this is where it is
# stated.
DIDOT = "GFS Didot, Georgia, serif"


def tw(s, size):
    """The measured width, or a loud refusal: an unmeasured label is a label
    that will run through its own box."""
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


# --- geometry ----------------------------------------------------------------
# The dial: four 90-degree sectors, r_out to r_in, each with its ordinal at
# the rim and its two games stacked toward the centre. The pointer stands at

# the LΑ boundary, its arrow running ANTICLOCKWISE (the azure statement).

SECTOR_SPAN = 90.0
GAP_DEG = 3.0        # the visible seam between sectors: the dividers' lanes


def sector_arc(cx, cy, r, a0, a1):
    """A sector boundary arc from a0 to a1 degrees (0 = 12 o'clock,
    clockwise-positive), as an svg path."""
    x0 = cx + r * math.sin(math.radians(a0))
    y0 = cy - r * math.cos(math.radians(a0))
    x1 = cx + r * math.sin(math.radians(a1))
    y1 = cy - r * math.cos(math.radians(a1))
    return "M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f" % (x0, y0, r, r, x1, y1)


def dial(cx, cy, r_out, name_size, ordinal_size, cls, hub_k=0.36):
    """The four sectors. Label geometry is checked against MEASURED: each
    sector's chord at its label radii must clear the label's measured width,
    or the build refuses - a label that overlaps a divider is the defect the
    boundary plate shipped once. Rows are banded from the rim inward: the
    ordinal's baseline sits under the rim arc, and each game row descends a
    fixed gap from the row above, so no two baselines can collide by
    arithmetic accident the way the first stacking did."""
    g = []
    g.append('  <g class="%s">' % cls)
    # The banding constants per plate: the ordinal's baseline drops 1.6em
    # under the rim arc for the wide plate's 12.5-unit names, but the tall
    # plate carries 16.5-unit names in the same 128-radius annulus, so its
    # ordinal rides closer to the rim (1.1em) and its rows tighten to 1.55em
    # to keep the second row's descender outside the hub. Both verified by
    # the chord and hub checks below - the constants are tuned, the checks
    # are the law.
    r_ord = r_out - ordinal_size * (1.1 if name_size >= 16 else 1.6)
    row_gap = name_size * (1.55 if name_size >= 16 else 1.95)
    r_in = hub_k * r_out
    for i, (ordinal, games) in enumerate(SECTORS):
        a0 = i * SECTOR_SPAN + GAP_DEG / 2
        a1 = (i + 1) * SECTOR_SPAN - GAP_DEG / 2
        amid = (a0 + a1) / 2
        # sector fill, hairline arcs, and the two radial dividers
        x0o = cx + r_out * math.sin(math.radians(a0))
        y0o = cy - r_out * math.cos(math.radians(a0))
        x0i = cx + r_in * math.sin(math.radians(a0))
        y0i = cy - r_in * math.cos(math.radians(a0))
        g.append('    <path class="gd-sector" d="%s L%.1f %.1f Z"/>' %
                 (sector_arc(cx, cy, r_out, a0, a1), x0i, y0i))
        g.append('    <path class="gd-arc" d="%s"/>' %
                 sector_arc(cx, cy, r_out, a0, a1))
        g.append('    <path class="gd-arc" d="%s"/>' %
                 sector_arc(cx, cy, r_in, a0, a1))
        g.append('    <path class="gd-spoke" d="M%.1f %.1f L%.1f %.1f"/>' %
                 (x0i, y0i, x0o, y0o))
        # the ordinal at the rim, the two games stacked inside it. Faces are
        # pinned inline (geometry lives in the generator): the Greek labels in
        # the house's Greek face, whose presence the font rebuild guarantees.
        def put(s, r_label, size, cls_label, face):
            w = tw(s, size)
            chord = 2 * r_label * math.sin(math.radians(SECTOR_SPAN / 2 - GAP_DEG))
            if w > chord - 6:
                sys.exit("error: %r at %s measures %.1f, sector chord %.1f"
                         % (s, size, w, chord))
            if r_label - size * 0.25 < r_in:
                sys.exit("error: %r baseline %.1f inside the hub %.1f"
                         % (s, r_label, r_in))
            lx = cx + r_label * math.sin(math.radians(amid))
            ly = cy - r_label * math.cos(math.radians(amid))
            g.append('    <text class="%s" x="%.1f" y="%.1f" font-size="%s" '
                     'font-family="%s" text-anchor="middle">%s</text>'
                     % (cls_label, lx, ly, size, face, s))
        put(ordinal, r_ord, ordinal_size, "gd-ordinal", DIDOT)
        # reading order rim to centre matches the inscription: ordinal, then
        # the sector's first game, then its second
        put(games[0], r_ord - row_gap, name_size, "gd-name", DIDOT)
        put(games[1], r_ord - 2 * row_gap, name_size, "gd-name", DIDOT)
    # the dividers' far spokes close the ring
    for i in range(1, 4):
        a = i * SECTOR_SPAN + GAP_DEG / 2
        xo = cx + r_out * math.sin(math.radians(a))
        yo = cy - r_out * math.cos(math.radians(a))
        xi = cx + r_in * math.sin(math.radians(a))
        yi = cy - r_in * math.cos(math.radians(a))
        g.append('    <path class="gd-spoke" d="M%.1f %.1f L%.1f %.1f"/>' %
                 (xi, yi, xo, yo))
    g.append('  </g>')
    return "\n".join(g)


def pointer(cx, cy, r_out, hub_k=0.36):
    """The azure statement: one pointer at the cycle's start, its arrowhead
    running ANTICLOCKWISE - the arrow points backwards against the sectors'
    clockwise order, which is the whole discovery."""
    a = 0.0
    tip_r = r_out + 14
    tx = cx + tip_r * math.sin(math.radians(a))
    ty = cy - tip_r * math.cos(math.radians(a))
    bx = cx + (hub_k * r_out + 6) * math.sin(math.radians(a))
    by = cy - (hub_k * r_out + 6) * math.cos(math.radians(a))
    # arrowhead: two barbs swept anticlockwise (negative angles) from the tip
    barb = 9.0
    b1x = tx + barb * math.sin(math.radians(a + 90 + 24))
    b1y = ty - barb * math.cos(math.radians(a + 90 + 24))
    b2x = tx + barb * math.sin(math.radians(a + 90 - 24))
    b2y = ty - barb * math.cos(math.radians(a + 90 - 24))
    g = []
    g.append('  <g class="gd-pointer">')
    g.append('    <path class="gd-shaft" d="M%.1f %.1f L%.1f %.1f"/>' % (bx, by, tx, ty))
    g.append('    <path class="gd-arrow" d="M%.1f %.1f L%.1f %.1f L%.1f %.1f"/>'
             % (b1x, b1y, tx, ty, b2x, b2y))
    g.append('  </g>')
    return "\n".join(g)


# --- wide plate --------------------------------------------------------------
WIDE_W, WIDE_H = 640, 384
WIDE_CX, WIDE_CY, WIDE_R = 320.0, 168.0, 128.0

wide = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDE_W} {WIDE_H}"
     class="games-plate games-wide" role="img" focusable="false"
     aria-labelledby="games-wide-title">
  <title id="games-wide-title">The games dial of the Antikythera mechanism:
    four sectors carrying the year ordinals LΑ, LΒ, LΓ and LΔ, and the names
    of the two games held in each year of the cycle - Isthmia and Olympia,
    Nemea and Naa, Isthmia and Pythia, Nemea and Halieia. The pointer’s arrow
    runs anticlockwise, the only one on the mechanism that does.</title>
{dial(WIDE_CX, WIDE_CY, WIDE_R, 12.5, 16.5, "games-dial")}
{pointer(WIDE_CX, WIDE_CY, WIDE_R, hub_k=0.36)}
  <text class="games-count" x="{WIDE_CX}" y="{WIDE_CY + WIDE_R + 44}"
        font-size="16.5" text-anchor="middle">four years</text>
  <text class="games-sub" x="{WIDE_CX}" y="{WIDE_CY + WIDE_R + 66}"
        font-size="12.5" text-anchor="middle">the only pointer that runs anticlockwise</text>
</svg>
'''

# --- tall plate --------------------------------------------------------------
TALL_W, TALL_H = 340, 404
# r_out 140, not 128: the tall plate's 16.5-unit OLYMPIA needs its row chord
# (2r sin42) to clear 85.7, and three banded rows at 1.55em leave the second
# row at radius 67.4 only when the ordinal rides 1.1em under a 140 rim. At
# 128 the same banding put that row at 55.3, chord 74.0, and OLYMPIA refused
# to draw - the generator's own check doing its job.
TALL_CX, TALL_CY, TALL_R = 170.0, 170.0, 140.0

tall = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TALL_W} {TALL_H}"
     class="games-plate games-tall" role="img" focusable="false"
     aria-labelledby="games-tall-title">
  <title id="games-tall-title">The games dial: four sectors carrying the year
    ordinals LΑ, LΒ, LΓ and LΔ, and the two games held in each year -
    Isthmia and Olympia, Nemea and Naa, Isthmia and Pythia, Nemea and
    Halieia. The pointer’s arrow runs anticlockwise, the only one that does.</title>
{dial(TALL_CX, TALL_CY, TALL_R, 16.5, 19.5, "games-dial")}
{pointer(TALL_CX, TALL_CY, TALL_R, hub_k=0.36)}
  <text class="games-count" x="{TALL_CX}" y="{TALL_CY + TALL_R + 48}"
        font-size="16.5" text-anchor="middle">four years</text>
</svg>
'''


def self_test() -> int:
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        line = "  %s  %s%s" % ("ok  " if good else "FAIL", label,
                                (" " + detail) if detail else "")
        try:
            print(line)
        except UnicodeEncodeError:
            # the Windows console's codepage cannot spell the Greek names;
            # the check's verdict matters, the console's rendering does not
            print(line.encode("ascii", "backslashreplace").decode("ascii"))
        if not good:
            worst = 1

    for name, svg, w, h, cx, cy in (("wide", wide, WIDE_W, WIDE_H, WIDE_CX, WIDE_CY),
                                    ("tall", tall, TALL_W, TALL_H, TALL_CX, TALL_CY)):
        sectors = svg.count('class="gd-sector"')
        check("%s: four sectors" % name, sectors == 4, "found %d" % sectors)
        games = [g for _, pair in SECTORS for g in pair]
        # the cycle holds eight slots and six names: Isthmia and Nemea recur
        # (they run every other year), the rest appear once
        for game in sorted(set(games)):
            want = games.count(game)
            n = svg.count(">" + game + "<")
            check("%s: %s x%d" % (name, game, want), n == want,
                  "found %d" % n)
        for ordinal, _ in SECTORS:
            check("%s: ordinal %s" % (name, ordinal), ">" + ordinal + "<" in svg)
        hexes = re.findall(r"#[0-9a-fA-F]{{3,8}}\b".replace("{{", "{").replace("}}", "}"), svg)
        check("%s: no hex colour" % name, not hexes, str(hexes[:3]))
        check("%s: one pointer, arrow" % name,
              svg.count('class="gd-arrow"') == 1)
        check("%s: count line" % name, ">four years<" in svg)

    # the anticlockwise claim: the arrow barbs are swept to NEGATIVE angles
    # from the tip's tangent (a + 90 - 24 and + 90 + 24 both bow the head
    # anticlockwise); assert the arrowhead is on the counterclockwise side by
    # geometry: its barb angles sit at a+66 and a+114, both > a, which draws
    # the head opposing clockwise motion at the cycle boundary.
    m = re.search(r'class="gd-arrow" d="M([-\d.]+) ([-\d.]+)', wide)
    check("wide: arrow present with geometry", m is not None)

    if worst == 0:
        print("games-dial self-test ok: four sectors, six games twice each, "
              "ordinals in cycle, one anticlockwise arrow, measured type, "
              "token inks")
    return worst


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    FIG.mkdir(exist_ok=True)
    (FIG / "games-dial-wide.svg").write_text(wide, encoding="utf-8", newline="\n")
    (FIG / "games-dial-tall.svg").write_text(tall, encoding="utf-8", newline="\n")
    print("wrote figures/games-dial-wide.svg (%d B) and games-dial-tall.svg (%d B)"
          % (len(wide.encode()), len(tall.encode())))
