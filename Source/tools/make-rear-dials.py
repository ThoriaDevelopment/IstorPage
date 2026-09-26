"""Generate the rear-dials plate: the Metonic and Saros spirals.

    python Source/tools/make-rear-dials.py [--self-test]

Writes Source/figures/rear-dials-wide.svg and Source/figures/rear-dials-tall.svg

WHY THIS EXISTS. The evidence act is four numbers the app printed about the
calendar ring, and the two dials those numbers were read against are named all
over the page and never drawn: the Metonic cycle ("a five-turn spiral dial on
the upper rear plate", the page's own captured answer) and the Saros dial ("223
lunar months ... a 54-year Exeligmos sub-dial"). The calendar-ring figure exists
because the ring's count is DISPUTED; these two dials are the SETTLED geometry,
and a page that argues in drawings should draw them. Everything here is
arithmetic from counts the page itself prints - 235 months in five turns, 223
in four, 19 tropical years - and nothing that would be scholarship drawn from
memory. No month names, no eclipse letters: the prose says those ring the real
dials, and this plate does not invent which.

TWO HONEST SIMPLIFICATIONS, stated where a reader of this file can weigh them:

  * The slots divide each spiral's angle evenly over its whole length. The
    physical Metonic dial holds exactly 47 months per turn (235 / 5 is whole),
    so for it even division is also the physical one; the Saros dial's 223
    months do not divide by 4, and the real dial's per-turn counts are lopsided
    in a way no source on this page states. The plate asserts the TOTAL, which
    is the number the page's prose asserts, and the self-test demands it.

  * The month marks are radial ticks crossing the spiral line, the way the
    real dial divides months, not beads along it: at 235 slots the arc spacing
    at the inner turn is 1.1 user units and any tangential mark long enough to
    see would merge into a solid line.

The azure statement carries no token in this file: the dot and its name are
classes (dials-start, dials-startlabel), and the stylesheet picks the token per
ground, --azure on paper and --azure-lift in the field, the same division the
etymology plate runs. A plate hanged on a new ground inherits the right blue
instead of carrying a wrong one inside itself.

TWO VARIANTS, swapped by width, for the reason every art-directed figure on
this page carries: a phone column at 320px renders the wide plate's labels as
glosses. The wide plate sets the spirals side by side with their counts in the
gutter between them - the one band of empty paper the composition owns. The
tall plate stacks them, carries larger type for its 0.76 render scale, and puts
each dial's count below it.

INKS. Structure is --ink-3 (the drawing, not text), the counts are Inter at
--ink with --ink-2 glosses, and each spiral gets exactly one azure statement:
the dot where its count ENDS - the spiral's inner terminus, named "one month"
in the spiral's free eye. The azure claim is the slot arithmetic itself - one
mark standing for 235, and one for 223 - not a reading direction or a month
name the page does not have. Both variants carry a <title> and role="img":
these plates carry their act's meaning, so a screen reader gets the composition
the prose already states.

ENCODING. The paths are written M absolute once, then relative integer steps,
the house standard the calendar ring sets (355 holes as one dashed circle in
1.7KB) and the gears run. First written at absolute %.1f, these two plates
cost 46.9KB of the document - the biggest single reason the document crossed
its budget ceiling. The same geometry, relative integers, is a quarter of
that, and nothing a reader can see changes: the widest render of either plate
is one to one, where a half-unit lattice is finer than one screen pixel, and
the self-test still decodes the paths back to points and measures the same
turns and slots it demanded before. Geometry lives at the lattice the
rendering cannot resolve past; bytes are part of the design too.

SELF-TEST. The invariants a doctored copy would break: turn counts measured by
accumulating the spiral path's swept angle, month-slot counts counted inside
the slots path only, the count labels present, exactly one azure statement per
spiral (dot plus its name), no hand-hex anywhere, and both variants asserting
the same two dials.
"""

import gzip
import math
import re
import sys
from pathlib import Path

# --- shared geometry ---------------------------------------------------------

METONIC_TURNS, METONIC_MONTHS = 5, 235
SAROS_TURNS, SAROS_MONTHS = 4, 223

# Radial pitch: user units between a spiral's turns. The wide plate renders at
# or above one to one, so 9 keeps the turns as airy as the ring plate's marks;
# the tall plate renders between 0.68 (a 320px phone) and 1.0 (its 340px cap),
# so 8 units there still read as open channels.
WIDE_PITCH, TALL_PITCH = 9.0, 8.0

# The month tick: a radial stroke centred on the spiral line, half-length 1.6,
# so the whole tick is 3.2 units against a 5.3-to-11.5-unit arc spacing between
# neighbouring slots. Long enough to see at both render scales, short enough
# that no two ticks touch.
TICK_HALF = 1.6

# The start label lives in the spiral's free eye - the disc inside the first
# turn, which no stroke enters - and ONLY on the wide plate: its eye is 41
# units and a 14-unit label measures 58.9 wide, half 29.4, which clears. The
# tall plate's eye is 8 units tighter at the size its labels must be to clear
# the type floor at 320 (see below), so there the dot speaks alone and the
# caption - real HTML, floor-safe - carries the meaning. This is the etymology
# plate's own move: its tall ledger carries 16-unit glosses for the same
# reason.
START_LABEL_WIDE_PX = 14

# Every drawn string's measured width, browser (Inter 500), for the extents
# gate: the gate recomputes each label's extent from these numbers and the
# anchor, and holds it inside the viewBox. The wide plate's "one month" sits
# at the spiral's start (14px); the gutter counts are 16.5 and their glosses
# 14; the tall plate draws all four count lines at 16.5 centred on its axis.
MEASURED = {
    ("one month", 13.0): 66.2, ("one month", 14.0): 71.3,
    ("235 months", 16.5): 93.9, ("223 months", 16.5): 94.1,
    ("5 turns · 19 years", 14.0): 114.0, ("4 turns · eclipses", 14.0): 114.7,
    ("5 turns · 19 years", 16.5): 134.4, ("4 turns · eclipses", 16.5): 135.2,
}

WIDE_W, WIDE_H = 640, 300
TALL_W, TALL_H = 340, 560

WIDE_MET_X, WIDE_SAR_X = 168.0, 470.0
WIDE_CY = 132.0
# Tall: 340-wide viewBox, so a 320px phone (svg 231.6 after the wrap's and the
# field's padding) renders it at 0.68 - and the 16.5-unit labels the floor
# demands there land at 11.2px, the same arithmetic the etymology ledger runs.
# The spirals come in to r_out 74/70 so each keeps 22 units of side margin.
TALL_MET_CY, TALL_SAR_CY = 128.0, 408.0

# Wide plate: the counts sit in the gutter between the spirals - 254 to 388 is
# empty paper from top to bottom - as one hinge of four lines. x is the
# gutter's centre; the longest line ("4 turns · eclipses") measures about 110
# units at 13px, so its half-width 55 clears both spirals with 15 to spare.
WIDE_GUTTER_X = 321.0


def spiral_points(cx, cy, r_out, pitch, turns, samples_per_turn=72):
    """The spiral as (x, y) samples: r = r_out - pitch * turns * (t/total).
    72 samples a turn: the chord's sagitta at the innermost radius (26 units)
    is 0.008 user units, invisible at one to one where a unit is a pixel."""
    r_in = r_out - pitch * turns
    total = turns * 2 * math.pi
    n = turns * samples_per_turn
    pts = []
    for i in range(n + 1):
        t = total * i / n
        r = r_out - (r_out - r_in) * (t / total)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts, r_in


def _rel(pts):
    """The house encoding: M absolute once, then relative integer steps. The
    lattice is half a user unit (rounding to integers on a cumulative sum),
    finer than any pixel either plate is ever rendered at, so the drawn curve
    does not move. Returned with the points, so the caller names the azure dot
    from the same lattice rather than inventing a second one."""
    out = ["M%d %d" % (round(pts[0][0]), round(pts[0][1]))]
    lat = [pts[0]]
    px, py = pts[0]
    for x, y in pts[1:]:
        gx, gy = round(x), round(y)
        if (gx, gy) == (round(lat[-1][0]), round(lat[-1][1])):
            continue
        out.append("l%d %d" % (gx - round(lat[-1][0]), gy - round(lat[-1][1])))
        lat.append((float(gx), float(gy)))
        px, py = gx, gy
    return "".join(out), lat


def line_path(pts):
    d, _ = _rel(pts)
    return d


def slot_path(cx, cy, r_out, pitch, turns, months):
    """The month marks: one path element whose subpaths are radial ticks, each
    centred on its slot's point on the spiral line. One element per spiral,
    not one per month. First tick M absolute; every tick after rides an m
    relative step from the previous tick's end, so a tick costs its two
    integer deltas and nothing else."""
    r_in = r_out - pitch * turns
    total = turns * 2 * math.pi
    parts = []
    pe = None  # previous tick's end, absolute
    for i in range(months):
        t = total * i / months
        r = r_out - (r_out - r_in) * (t / total)
        ux, uy = math.cos(t), math.sin(t)
        x1, y1 = round(cx + (r - TICK_HALF) * ux), round(cy + (r - TICK_HALF) * uy)
        x2, y2 = round(cx + (r + TICK_HALF) * ux), round(cy + (r + TICK_HALF) * uy)
        if pe is None:
            parts.append("M%d %d" % (x1, y1))
        else:
            parts.append("m%d %d" % (x1 - pe[0], y1 - pe[1]))
        parts.append("l%d %d" % (x2 - x1, y2 - y1))
        pe = (x2, y2)
    return "".join(parts)


def first_slot(cx, cy, r_out, pitch, turns, months):
    """The first month slot's centre: each spiral's one azure dot."""
    r_in = r_out - pitch * turns
    return cx + r_in, cy


def spiral_block(cx, cy, r_out, pitch, turns, months, count, sub, start_px,
                 labeled=True):
    """One dial. `labeled=False` (the wide plate) omits the count lines: there
    they stand once, in the gutter between the dials, rather than twice.
    text-anchor is inline because it is geometry: every label here is centred
    on the axis it names, and the default `start` would run each one rightward
    off its spiral."""
    pts, r_in = spiral_points(cx, cy, r_out, pitch, turns)
    _, lat = _rel(pts)
    fx, fy = lat[0]  # the lattice's first point IS the inner terminus
    g = []
    g.append('  <g class="dials-spiral" data-dial="%s">'
             % ("metonic" if months == METONIC_MONTHS else "saros"))
    g.append('    <path class="dials-line" d="%s"/>' % line_path(pts))
    g.append('    <path class="dials-slots" d="%s"/>'
             % slot_path(cx, cy, r_out, pitch, turns, months))
    g.append('    <circle class="dials-start" cx="%.1f" cy="%.1f" r="3.2"/>'
             % (fx, fy))
    if start_px:
        g.append('    <text class="dials-startlabel" x="%.1f" y="%.1f" '
                 'font-size="%d" text-anchor="middle">one month</text>'
                 % (cx, cy + 3, start_px))
    if labeled:
        g.append('    <text class="dials-count" x="%.1f" y="%.1f" '
                 'font-size="16.5" text-anchor="middle">%s</text>'
                 % (cx, cy + r_out + 26, count))
        g.append('    <text class="dials-sub" x="%.1f" y="%.1f" '
                 'font-size="16.5" text-anchor="middle">%s</text>'
                 % (cx, cy + r_out + 26 + 22, sub))
    g.append('  </g>')
    return "\n".join(g)


def gutter_line(x, y, text, cls):
    """The wide plate's count block. Sizes are inline like every other label:
    16.5 for the datum, 14 for its gloss, both sized for the print world's
    0.809 scale (13.3px and 11.3px there) where the wide plate still shows."""
    size = 16.5 if "count" in cls else 14
    return ('  <text class="%s" x="%.1f" y="%.1f" font-size="%s" '
            'text-anchor="middle">%s</text>' % (cls, x, y, size, text))


# --- wide plate ---------------------------------------------------------------

wide = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDE_W} {WIDE_H}"
     class="dials-plate dials-wide" role="img" focusable="false"
     aria-labelledby="dials-wide-title">
  <title id="dials-wide-title">The two settled rear dials of the Antikythera
    mechanism: the Metonic spiral, five turns holding 235 lunar months, and the
    Saros spiral, four turns holding 223 months, the counts this page’s own
    answer prints. Each radial tick is one month; the azure dot sits where each
    dial’s count ends.</title>
  <!-- The Metonic and Saros spirals as arithmetic: 5 turns / 235 slots and
       4 turns / 223 slots. The counts stand in the gutter between the dials,
       the one band of empty paper the composition owns. Regenerate with
       Source/tools/make-rear-dials.py - do not hand-edit. -->
{spiral_block(WIDE_MET_X, WIDE_CY, 86, WIDE_PITCH, METONIC_TURNS, METONIC_MONTHS,
              "235 months", "5 turns · 19 years", START_LABEL_WIDE_PX,
              labeled=False)}
{gutter_line(WIDE_GUTTER_X, 118, "235 months", "dials-count dials-gutter")}
{gutter_line(WIDE_GUTTER_X, 138, "5 turns · 19 years", "dials-sub dials-gutter")}
{gutter_line(WIDE_GUTTER_X, 168, "223 months", "dials-count dials-gutter")}
{gutter_line(WIDE_GUTTER_X, 188, "4 turns · eclipses", "dials-sub dials-gutter")}
{spiral_block(WIDE_SAR_X, WIDE_CY, 82, WIDE_PITCH, SAROS_TURNS, SAROS_MONTHS,
              "223 months", "4 turns · eclipses", START_LABEL_WIDE_PX,
              labeled=False)}
</svg>
'''

# --- tall plate ---------------------------------------------------------------

tall = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TALL_W} {TALL_H}"
     class="dials-plate dials-tall" role="img" focusable="false"
     aria-labelledby="dials-tall-title">
  <title id="dials-tall-title">The two settled rear dials of the Antikythera
    mechanism, read downward: the Metonic spiral, five turns holding 235 lunar
    months, and the Saros spiral, four turns holding 223 months, the counts
    this page’s own answer prints. Each radial tick is one month; the azure dot
    sits where each dial’s count ends.</title>
  <!-- The same two dials as the wide plate, stacked for a phone column, with
       type sized for this plate's 0.76 render scale. Regenerate with
       Source/tools/make-rear-dials.py - do not hand-edit. -->
{spiral_block(TALL_W / 2, TALL_MET_CY, 74, TALL_PITCH, METONIC_TURNS, METONIC_MONTHS,
              "235 months", "5 turns · 19 years", None)}
{spiral_block(TALL_W / 2, TALL_SAR_CY, 70, TALL_PITCH, SAROS_TURNS, SAROS_MONTHS,
              "223 months", "4 turns · eclipses", None)}
</svg>
'''

# --- write --------------------------------------------------------------------

FIG = Path(__file__).resolve().parent.parent / "figures"
for name, svg in (("rear-dials-wide", wide), ("rear-dials-tall", tall)):
    out = FIG / ("%s.svg" % name)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("%-18s %5d bytes  (%d gzipped)  -> %s"
          % (name, len(svg.encode()), len(gzip.compress(svg.encode(), 9)),
             out.relative_to(out.parents[2])))


# --- self-test ----------------------------------------------------------------

def decode_path(d):
    """Decode the house encoding - M/m absolute-or-relative moves, l relative
    lines, integer pairs - back to absolute points. The only three commands
    this generator emits, so a decoder that knows exactly those three is not a
    shortcut, it is the file's own contract: a doctored path with anything
    else in it decodes to junk and fails the turns test downstream."""
    pts = []
    x = y = 0.0
    for cmd, a, b in re.findall(r"([Mml])(-?\d+) (-?\d+)", d):
        a, b = float(a), float(b)
        if cmd == "M":
            x, y = a, b
        else:
            x, y = x + a, y + b
        pts.append((x, y))
    return pts


def swept_turns(d, cx, cy):
    """Turns measured the only honest way: decode the path and accumulate the
    angle it sweeps around the spiral's centre. A first-and-last-points test
    would measure nothing - both ends sit on the same ray by construction."""
    pts = decode_path(d)
    swept = 0.0
    prev = math.atan2(pts[0][1] - cy, pts[0][0] - cx)
    for x, y in pts[1:]:
        a = math.atan2(y - cy, x - cx)
        delta = a - prev
        if delta > math.pi:
            delta -= 2 * math.pi
        if delta < -math.pi:
            delta += 2 * math.pi
        swept += delta
        prev = a
    return abs(swept) / (2 * math.pi)


def self_test() -> int:
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" " + detail) if detail else ""))
        if not good:
            worst = 1

    centres = {
        ("wide", "metonic"): (WIDE_MET_X, WIDE_CY),
        ("wide", "saros"): (WIDE_SAR_X, WIDE_CY),
        ("tall", "metonic"): (TALL_W / 2, TALL_MET_CY),
        ("tall", "saros"): (TALL_W / 2, TALL_SAR_CY),
    }
    for variant, svg in (("wide", wide), ("tall", tall)):
        blocks = svg.split('<g class="dials-spiral"')[1:]
        check("%s: two spirals" % variant, len(blocks) == 2, "found %d" % len(blocks))
        if len(blocks) != 2:
            continue
        for which, months, turns, count, sub in (
                ("metonic", METONIC_MONTHS, METONIC_TURNS, "235 months", "5 turns · 19 years"),
                ("saros", SAROS_MONTHS, SAROS_TURNS, "223 months", "4 turns · eclipses")):
            blob = blocks[0 if which == "metonic" else 1]
            cx, cy = centres[(variant, which)]
            # the spiral group is the one it claims to be
            check("%s/%s: group named" % (variant, which),
                  ('data-dial="%s"' % which) in blob)
            # slots: count subpaths inside the slots path ONLY - a whole-block
            # count would also meet the M in the labels
            m = re.search(r'class="dials-slots" d="([^"]+)"', blob)
            check("%s/%s: slots path present" % (variant, which), m is not None)
            if m:
                # one move per tick: M on the first, m relative on every tick
                # after - so moves, not Ms, count the slots
                dd = m.group(1)
                n_slots = dd.count("M") + dd.count("m")
                check("%s/%s: %d month slots" % (variant, which, months),
                      n_slots == months, "found %d" % n_slots)
            m = re.search(r'class="dials-line" d="([^"]+)"', blob)
            if m:
                got = swept_turns(m.group(1), cx, cy)
                check("%s/%s: %d turns" % (variant, which, turns),
                      abs(got - turns) < 0.02, "measured %.3f" % got)
            if variant == "tall":
                # stacked plate: each count sits under its own dial
                check("%s/%s: count label %r" % (variant, which, count),
                      (">%s<" % count) in blob)
                check("%s/%s: sub label %r" % (variant, which, sub),
                      (">%s<" % sub) in blob)
            # the wide spiral's azure is the dot AND its name; the tall
            # spiral's is the dot alone (the caption carries the meaning there,
            # real HTML at the type floor rather than plate text under it)
            n_azure = blob.count('class="dials-start"') + \
                blob.count('class="dials-startlabel"')
            want = 2 if variant == "wide" else 1
            check("%s/%s: one azure statement" % (variant, which),
                  n_azure == want, "found %d" % n_azure)
        if variant == "wide":
            # side-by-side plate: the counts stand ONCE, in the gutter between
            # the dials, so a reader meets them once rather than four times
            for count, sub in (("235 months", "5 turns · 19 years"),
                               ("223 months", "4 turns · eclipses")):
                check("wide/gutter: %r once" % count,
                      svg.count(">%s<" % count) == 1)
                check("wide/gutter: %r once" % sub, svg.count(">%s<" % sub) == 1)

    for name, svg in (("wide", wide), ("tall", tall)):
        hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", svg)
        check("%s: no hex colour" % name, not hexes, str(hexes[:3]))
        check("%s: both dials asserted" % name,
              "Metonic" in svg and "Saros" in svg and "235" in svg and "223" in svg)

    if worst == 0:
        print("rear-dials self-test ok: turns swept, slots counted, labels, "
              "azure discipline, token inks, both variants")
    return worst


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
