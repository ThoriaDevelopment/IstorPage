#!/usr/bin/env python3
"""Draw the page's own instrument: the reading bar, on one axis, in tok/s.

    python Source/tools/make-reading-bar.py [--self-test]

Writes Source/figures/reading-bar-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues entirely in thresholds on one axis - a person
reads "somewhere near five to ten tokens per second", "below roughly ten, long
answers start to drag; below five, the tool feels broken", "a model sustaining
twenty or thirty is streaming faster than you can read", and it names the
instrument "the reading bar" three times without ever drawing it. Four speeds
against that bar is the page's whole first section: an entry-level GPU's four
feels usable because it clears the bar, not because it is fast; a datacenter
number is faster than the eye can spend. The second panel is the page's other
shape, "As an answer grows, the rate usually drifts down" - a line that starts
at a flagship speed, sags with every piece written, and must still finish above
the bar, because that is what "usable" means here.

THE BAR IS A VERTICAL LINE AT SIX, not a rule under the numbers: it divides the
axis into the speeds a reader can spend and the speeds they cannot, which is
what "clearing the reading bar" means. It runs through both panels at the same
x, because the drift is the same axis while one answer is being written. Six
sits inside the five-to-ten yardstick the prose gives, and it is the number
every check holds the claims against. The four example speeds are labelled as
examples: what is not illustrative is the RELATION, and that is what the
self-test holds.

PLANNED, THEN DRAWN, like every plate here: every string is placed by plan()
before any of it is rendered, so "does a label sit inside the plate" and "does
any label sit on another" are questions about data rather than arithmetic
buried in text calls. The feel labels are staggered onto two rows and clamped
to the band, because the four speeds are not equally spaced on their own axis
and two of them sit too close for stacked centred labels - the same lesson the
token plate's brace label taught, applied before the render instead of after.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the
drawing themes with the page, and no hex value appears in it. The witness marks
the bar itself, in both panels, because the bar is the one object the reader
follows across the plate - it is the page's subject.
"""

import re
import sys
import tempfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

ADV_MONO = 0.60
ADV_SANS = 0.53

INK = "var(--ink)"
MIST = "var(--mist)"
SUBTLE = "var(--subtle)"
WITNESS = "var(--witness)"

TITLE = "the axis is the page's own: pieces per second"

# The bar, at six: inside the five-to-ten yardstick the prose gives, and the
# number every check holds the claims against.
BAR = 6.0

# The four example speeds, in pieces per second, and what each feels like. They
# are labelled as examples: the relation to the bar is the claim, the numbers
# are props. 4 is under the bar - the page's "below five, the tool feels
# broken" - 12 clears it, 25 is faster than reading, 90 is a datacenter number
# the eye cannot spend.
SPEEDS = ((4.0, "under the bar"),
          (12.0, "clears the bar"),
          (25.0, "faster than reading"),
          (90.0, "a datacenter number"))

FEEL_ROWS = (1, 0, 2, 0)

# The drift, as (answer length in pieces, rate in pieces per second): a line
# that starts at a flagship speed, sags because each new piece attends to
# everything written so far, and must finish above the bar - "usable" is the
# page's own word for what that means.
DRIFT = ((0, 30.0), (120, 27.0), (240, 24.0), (360, 22.0), (480, 20.0),
         (600, 19.0), (720, 18.0))

# The drift panel's own scale: its x is ANSWER PROGRESS - the whole band is the
# answer being written - and its y is the rate, topped a little above the
# drift's start so the sag has air. The bar is horizontal here, at its own
# value through this scale: one threshold, each panel reading it on the axis it
# lives on.
DRIFT_Y_MAX = 32.0

PANELS = (("speeds", "four example speeds, one bar"),
          ("drift", "the rate while one answer is written"))

NOTES = ("Speeds are examples, not measurements.",
         "The bar sits in the five-to-ten band.")

# The feel labels' rows, as data: the four speeds are not equally spaced on
# their own axis - three of them cluster on the left third - and their labels
# are wider than the gaps, so they share rows by assignment rather than by
# parity. Row 0 sits nearest the axis, row 2 furthest; the assignment is a
# claim the overlap check holds.

# The bar's own word on the plate, beside the line it names.
BAR_WORD = "the reading bar"

# The drift's printed ends, computed once from the drift itself so a retuned
# drift retunes the numbers.
DRIFT_START = "starts at %g" % DRIFT[0][1]
DRIFT_END = "ends at %g" % DRIFT[-1][1]

# The axis's top: a hundred, so the datacenter number lands far enough past the
# bar to read as a different order of speed.
AXIS_MAX = 100.0


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * size * adv


def bar_x(spec: dict) -> float:
    return scale_x(spec, BAR)


def deepest_over(pts: list, x_from: float, x_to: float) -> float:
    """The deepest y the drift line reaches over a span, interpolating the
    segments rather than sampling the vertices: the line between two points is
    exactly what a reader sees cross a label, so placement and check share this
    one arithmetic rather than each keeping its own."""
    worst = None
    for (ax, ay), (bx2, by2) in zip(pts, pts[1:]):
        lo, hi = max(ax, x_from), min(bx2, x_to)
        if lo > hi:
            continue
        for x in (lo, hi):
            f = (x - ax) / (bx2 - ax) if bx2 > ax else 0.0
            y = ay + (by2 - ay) * f
            worst = y if worst is None else max(worst, y)
    return worst if worst is not None else pts[0][1]


def axis_y(spec: dict) -> float:
    return spec["speed_top"] + spec["speed_h"]


def fmt_v(v: float) -> str:
    """A speed as the plate prints it: whole numbers, no trailing zero."""
    return "%g" % v


def scale_x(spec: dict, v: float) -> float:
    """A speed in pieces per second to a plate x, linear from zero."""
    return spec["x0"] + spec["band"] * v / AXIS_MAX


def drift_y(spec: dict, rate: float) -> float:
    """A rate to a plate y in the drift panel: the top of the panel is the
    scale's top, the bottom is zero."""
    return spec["drift_top"] + spec["drift_h"] * (1 - rate / DRIFT_Y_MAX)


def drift_pts(spec: dict) -> list:
    """The drift line as (x, y) in plate units: x is answer progress across the
    whole band, y is the rate through the panel's own scale."""
    out = []
    for length, rate in DRIFT:
        out.append((spec["x0"] + spec["band"] * length / DRIFT[-1][0],
                    drift_y(spec, rate)))
    return out


# The text floors, DERIVED like every plate here: the tall plate is 380 units
# wide and renders at 280px in a 320px viewport, a 0.737 scale, so 15 units
# lands at 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

# Two lines, set by the narrow plate: at 15 units the tall variant has room for
# 42 characters a line, which is why the notes are this short.
FACTS = ((TITLE, "the title"), (BAR_WORD, "the bar's own label"),
         (DRIFT_START, "the drift's start speed"),
         (DRIFT_END, "the drift's end speed")) + \
        tuple((note, "a footnote line") for note in NOTES) + \
        tuple((label, "a panel label") for _k, label in PANELS) + \
        tuple((what, "a speed's feel") for _v, what in SPEEDS)

WIDE = {
    "w": 640, "h": 424, "name": "wide",
    "x0": 24.0, "band": 546.0,
    "title_y": 30.0, "first_label_y": 64.0, "speed_top": 82.0,
    "speed_h": 104.0, "feel_dy": 20.0, "feel_step": 24.0,
    "drift_label_y": 276.0, "drift_top": 294.0, "drift_h": 76.0,
    "label": 16.0, "foot": 16.0,
    "foot_y": 398.0, "foot_step": 19.0,
}

TALL = {
    "w": 380, "h": 404, "name": "tall",
    "x0": 22.0, "band": 336.0,
    "title_y": 26.0, "first_label_y": 56.0, "speed_top": 76.0,
    "speed_h": 96.0, "feel_dy": 19.0, "feel_step": 22.0,
    "drift_label_y": 256.0, "drift_top": 272.0, "drift_h": 72.0,
    "label": 15.0, "foot": 15.0,
    "foot_y": 368.0, "foot_step": 18.0,
}


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font,
    colour, anchor). Drawing reads this and the checks read this, so neither
    can drift."""
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["label"],
            FONTS_SANS, MIST, "start")]

    # Panel one: the four speeds as numbers at their own places on the axis,
    # each with its feel under the axis - staggered onto two rows, because two
    # of the speeds sit too close together for one row of centred labels.
    out.append(("speeds-label", PANELS[0][1], spec["x0"], spec["first_label_y"],
                spec["label"], FONTS_SANS, INK, "start"))
    ay = axis_y(spec)
    for i, (v, what) in enumerate(SPEEDS):
        x = scale_x(spec, v)
        out.append(("speed%d" % i, fmt_v(v), x,
                    spec["speed_top"] + spec["speed_h"] * 0.42,
                    spec["label"], FONTS_MONO, INK, "middle"))
        row = spec["feel_dy"] + FEEL_ROWS[i] * spec["feel_step"]
        out.append(("speed%d-what" % i, what, x, ay + row,
                    spec["foot"], FONTS_SANS, MIST, "middle"))
    # The bar's own label, at the panel's top, beside the line it names.
    out.append(("bar-word", BAR_WORD, bar_x(spec) + 10, spec["speed_top"] + 18,
                spec["label"], FONTS_SANS, WITNESS, "start"))

    # Panel two: the drift line's two ends, named where the line starts and
    # where it finishes, and the same bar running through this panel too -
    # horizontal here, at its own value, because this panel's rate axis is y.
    out.append(("drift-label", PANELS[1][1], spec["x0"], spec["drift_label_y"],
                spec["label"], FONTS_SANS, INK, "start"))
    pts = drift_pts(spec)
    first, last = pts[0], pts[-1]
    # The start label sits UNDER the line's first stretch, so its baseline is
    # computed from the line's own descent across the label's width: the text
    # must clear the deepest point of the line over the span the text occupies.
    # A fixed offset grazed on the tall variant, where the same drop happens
    # over less width.
    sw = width_of(DRIFT_START, spec["label"], ADV_MONO)
    deep = deepest_over(pts, spec["x0"] + 2, spec["x0"] + 2 + sw)
    out.append(("drift-start", DRIFT_START, spec["x0"] + 2,
                deep + spec["label"] * 0.78 + 4.0,
                spec["label"], FONTS_MONO, INK, "start"))
    out.append(("drift-end", DRIFT_END, spec["x0"] + spec["band"] - 2,
                last[1] - 16, spec["label"], FONTS_MONO, INK, "end"))
    out.append(("drift-bar-word", BAR_WORD, spec["x0"], drift_y(spec, BAR) - 8,
                spec["foot"], FONTS_SANS, WITNESS, "start"))

    for j, note in enumerate(NOTES):
        out.append(("note%d" % j, note, spec["x0"],
                    spec["foot_y"] + j * spec["foot_step"], spec["foot"],
                    FONTS_SANS, MIST, "start"))

    # The feel labels were centred on their ticks; where that would run them
    # past the band's edge, clamp them inside it. Their x is data, so the check
    # for the speed NUMBERS is unaffected: those stay exactly on the scale.
    clamped = []
    for name, s, x, y, size, font, colour, anchor in out:
        if anchor == "middle" and name.endswith("-what"):
            w = width_of(s, size, ADV_SANS)
            if x - w / 2 < spec["x0"]:
                anchor, x = "start", spec["x0"]
            elif x + w / 2 > spec["x0"] + spec["band"]:
                anchor, x = "end", spec["x0"] + spec["band"]
        clamped.append((name, s, x, y, size, font, colour, anchor))
    return clamped


def boxes(spec: dict) -> list:
    """The placed labels as rectangles, so the checks can ask what a reader
    sees."""
    out = []
    for name, s, x, y, size, font, _colour, anchor in plan(spec):
        w = width_of(s, size, ADV_MONO if font == FONTS_MONO else ADV_SANS)
        if anchor == "middle":
            x = x - w / 2
        elif anchor == "end":
            x = x - w
        out.append((name, x, x + w, y - size * 0.78, y + size * 0.22))
    return out


def svg_text(x: float, y: float, s: str, fill: str, size: float, font: str,
             weight=None, anchor=None) -> str:
    bits = ['<text x="%g" y="%g" font-family="%s" font-size="%g" fill="%s"'
            % (x, y, font, size, fill)]
    if weight:
        bits.append(' font-weight="%s"' % weight)
    if anchor:
        bits.append(' text-anchor="%s"' % anchor)
    bits.append(">%s</text>" % esc(s))
    return "".join(bits)


def draw_axis(spec: dict) -> str:
    """The speeds panel's ground line and its scale marks - the axis the four
    numbers sit on."""
    y = axis_y(spec)
    out = ['<rect x="%g" y="%g" width="%g" height="2" fill="%s"/>'
           % (spec["x0"], y, spec["band"], SUBTLE)]
    for v in (0, 25, 50, 75, 100):
        out.append('<rect x="%.2f" y="%.2f" width="2.00" height="14.00" fill="%s"/>'
                   % (scale_x(spec, v) - 1, y - 6, MIST))
    return "".join(out)


def draw_bars(spec: dict) -> str:
    """The reading bar, twice: vertical through the speeds panel, where the
    axis is speed, horizontal through the drift panel, where the axis is
    progress and the rate is y. One threshold, read on each panel's own axes."""
    out = ['<rect x="%.2f" y="%g" width="2.00" height="%g" fill="%s"/>'
           % (bar_x(spec) - 1, spec["speed_top"], spec["speed_h"], WITNESS)]
    out.append('<rect x="%g" y="%.2f" width="%g" height="2.00" fill="%s"/>'
               % (spec["x0"], drift_y(spec, BAR) - 1, spec["band"], WITNESS))
    return "".join(out)


def draw_drift(spec: dict) -> str:
    """The drift as one polyline through the measured points."""
    pts = drift_pts(spec)
    d = " ".join("%s%g %g" % ("M" if i == 0 else "L", x, y)
                 for i, (x, y) in enumerate(pts))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, MIST)


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'width="%g" height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("Four example speeds against the reading bar at six pieces per "
                  "second: 4 under it, 12 clearing it, 25 faster than reading, "
                  "90 a datacenter number. While one answer is written the rate "
                  "drifts from 30 to 18 and finishes above the bar."),
              spec["name"])]
    out.append(draw_axis(spec))
    out.append(draw_bars(spec))
    out.append(draw_drift(spec))
    for name, s, x, y, size, font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if name == "bar-word" else None,
                            anchor=None if anchor == "start" else anchor))
    out.append("</svg>")
    return "".join(out)


def write(out: Path = OUT) -> list:
    """Both variants, drawn and written, into `out`.

    THE DIRECTORY IS A PARAMETER AND THE SELF-TEST USES ANOTHER ONE, for the
    reason token-rows.py records: the claims here are proved by doctoring this
    file, and a doctored run must not be able to leave a doctored plate in
    Source/figures/.
    """
    written = []
    for spec in (WIDE, TALL):
        svg = draw(spec)
        path = out / ("reading-bar-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def drawn_speed_xs(spec: dict) -> list:
    """The speed numbers' x positions, read back from the drawn text elements
    rather than from plan(): the plate's geometry is checked the way a renderer
    sees it."""
    return [float(x) for x in re.findall(
        r'<text x="([0-9.]+)" y="%g" font-family="%s" font-size="[0-9.]+" '
        r'fill="%s" text-anchor="middle">'
        % (spec["speed_top"] + spec["speed_h"] * 0.42, re.escape(FONTS_MONO),
           re.escape(INK)), draw(spec))]


def check_axis(spec: dict, name: str, svg: str) -> list:
    """The speeds sit where the axis says: each number's drawn x is its own
    value through the same scale the marks use, the four are in rising order,
    and the relations to the bar hold in the drawing - under, clearing, and far
    past it."""
    bad = []
    marks = re.findall(r'<rect x="[0-9.]+" y="[0-9.]+" width="2.00" '
                       r'height="14.00" fill="%s"/>' % re.escape(MIST),
                       draw_axis(spec))
    if len(marks) != 5:
        bad.append("%s: %d scale marks drawn for the five the axis claims"
                   % (name, len(marks)))
    xs = drawn_speed_xs(spec)
    if len(xs) != len(SPEEDS):
        bad.append("%s: %d speed numbers read back for the %d the plate claims"
                   % (name, len(xs), len(SPEEDS)))
        return bad
    for (v, _what), x in zip(SPEEDS, xs):
        if abs(x - scale_x(spec, v)) > 0.01:
            bad.append("%s: the %g tok/s number is drawn at x=%g and the axis "
                       "puts it at %g" % (name, v, x, scale_x(spec, v)))
    if xs != sorted(xs):
        bad.append("%s: the speeds are not drawn in rising order, so the axis "
                   "reads backwards" % name)
    barx = bar_x(spec)
    if not xs[0] < barx < xs[1] < xs[3]:
        bad.append("%s: the drawn order does not say under/clearing/faster "
                   "against the bar" % name)
    if not xs[3] - barx > 2.5 * (barx - xs[0]):
        bad.append("%s: the datacenter number is not far enough past the bar to "
                   "read as a different order of speed" % name)
    return bad


def check_drift(spec: dict, name: str, svg: str) -> list:
    """The drift spans the answer being written - first point at the band's
    left edge, last at its right - sags monotonically as the rate falls, and
    finishes above the bar's line, which is the page's claim about usable.
    Read from the drawn path's own points."""
    bad = []
    m = re.search(r'<path d="([^"]+)"', svg)
    if not m:
        return ["%s: the drift line is not in the drawing" % name]
    pts = [(float(x), float(y)) for _m, x, y in
           re.findall(r"([ML])([0-9.]+) ([0-9.]+)", m.group(1))]
    if len(pts) != len(DRIFT):
        bad.append("%s: the path holds %d points for the %d the drift claims"
                   % (name, len(pts), len(DRIFT)))
        return bad
    if abs(pts[0][0] - spec["x0"]) > 0.01 or \
            abs(pts[-1][0] - (spec["x0"] + spec["band"])) > 0.01:
        bad.append("%s: the drift line does not span the answer being written "
                   "(%g to %g of %g)" % (name, pts[0][0], pts[-1][0],
                                          spec["x0"] + spec["band"]))
    if any(b < a - 1e-9 for a, b in zip([p[1] for p in pts],
                                         [p[1] for p in pts][1:])):
        bad.append("%s: the drift line rises somewhere, and the page's claim is "
                   "that the rate only drifts down as the answer grows" % name)
    if pts[-1][1] <= pts[0][1] + 0.01:
        bad.append("%s: the drift line ends where it started, so no sag is "
                   "visible" % name)
    by = drift_y(spec, BAR)
    if not pts[0][1] < by:
        bad.append("%s: the drift starts at or below the bar, so there is "
                   "nothing to drift from" % name)
    if not pts[-1][1] < by:
        bad.append("%s: the drift finishes at y=%g, on or below the bar at %g, "
                   "and the page's claim is that it stays readable"
                   % (name, pts[-1][1], by))
    for (x, y) in pts:
        if not spec["drift_top"] - 0.01 <= y <= spec["drift_top"] + spec["drift_h"] + 0.01:
            bad.append("%s: a drift point sits at y=%g, outside its own panel"
                       % (name, y))
    return bad


def check_bar(spec: dict, name: str, svg: str) -> list:
    """One witness line per panel: vertical through the speeds panel at the
    bar's own value on the speed axis, horizontal through the drift panel at
    the same value on the rate axis. One threshold, read on each panel's own
    axes, and both must span their panel."""
    bad = []
    vert = re.findall(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="2.00" '
                      r'height="([0-9.]+)" fill="%s"/>' % re.escape(WITNESS), svg)
    horiz = re.findall(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" '
                       r'height="2.00" fill="%s"/>' % re.escape(WITNESS), svg)
    if len(vert) != 1 or len(horiz) != 1:
        bad.append("%s: %d vertical and %d horizontal witness lines drawn for "
                   "the one-per-panel the plate claims"
                   % (name, len(vert), len(horiz)))
        return bad
    vx, vy, vh = (float(a) for a in vert[0])
    if abs(vx + 1 - bar_x(spec)) > 0.01:
        bad.append("%s: the vertical bar sits at x=%g and the axis puts %g at %g"
                   % (name, vx + 1, BAR, bar_x(spec)))
    if abs(vy - spec["speed_top"]) > 0.01 or abs(vh - spec["speed_h"]) > 0.01:
        bad.append("%s: the vertical bar does not span the speeds panel "
                   "(y=%g h=%g of %g..%g)" % (name, vy, vh, spec["speed_top"],
                                               spec["speed_top"] + spec["speed_h"]))
    hx, hy, hw = (float(a) for a in horiz[0])
    if abs(hy + 1 - drift_y(spec, BAR)) > 0.01:
        bad.append("%s: the horizontal bar sits at y=%g and the rate axis puts "
                   "%g at %g" % (name, hy + 1, BAR, drift_y(spec, BAR)))
    if abs(hx - spec["x0"]) > 0.01 or abs(hw - spec["band"]) > 0.01:
        bad.append("%s: the horizontal bar does not span the drift panel's band"
                   % name)
    return bad


def check_numbers(spec: dict, name: str, svg: str) -> list:
    """The printed drift ends are the drawn line's own ends."""
    bad = []
    for text, want, what in ((DRIFT_START, DRIFT[0][1], "start"),
                             (DRIFT_END, DRIFT[-1][1], "end")):
        if text not in svg:
            bad.append("%s: the drift's %s speed %r is not printed on the plate"
                       % (name, what, text))
        elif "%g" % want not in text:
            bad.append("%s: the drift's %s prints %r and the line ends at %g"
                       % (name, what, text, want))
    return bad


def check_inside(spec: dict, name: str) -> list:
    """Every label sits inside the plate, horizontally AND vertically."""
    bad = []
    for lname, x0, x1, t, b in boxes(spec):
        if x0 < 0 or x1 > spec["w"]:
            bad.append("%s: %s runs off the plate sideways (%g to %g of %g)"
                       % (name, lname, x0, x1, spec["w"]))
        if t < 0 or b > spec["h"]:
            bad.append("%s: %s runs off the plate vertically (%g to %g of %g)"
                       % (name, lname, t, b, spec["h"]))
    return bad


def check_no_overlap(spec: dict, name: str) -> list:
    """No label sits on another."""
    bad = []
    bx = boxes(spec)
    for i, (a, ax0, ax1, ay0, ay1) in enumerate(bx):
        for b, bx0, bx1, by0, by1 in bx[i + 1:]:
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                bad.append("%s: %s sits on %s" % (name, a, b))
    return bad


def check_path_clearance(spec: dict, name: str) -> list:
    """No label sits on the drift line. The line is the panel's data, and a
    baseline crossing a descender is exactly the kind of defect a label-only
    overlap check cannot see: the path is not in boxes(), so it is checked
    here, segment by segment, against every label rectangle."""
    bad = []
    pts = drift_pts(spec)
    CLEAR = 3.0
    for lname, x0, x1, t, b in boxes(spec):
        for (ax, ay), (bx2, by2) in zip(pts, pts[1:]):
            # clamp the segment to the label's x-span, then measure the gap at
            # both ends of the overlap - the line between vertices is what a
            # reader sees cross the text, not the vertices themselves
            lo, hi = max(ax, x0), min(bx2, x1)
            if lo > hi:
                continue
            f0 = (lo - ax) / (bx2 - ax) if bx2 > ax else 0.0
            f1 = (hi - ax) / (bx2 - ax) if bx2 > ax else 1.0
            y_at = [ay + (by2 - ay) * f for f in (f0, f1)]
            if any(y < t for y in y_at):
                gap = min(abs(y - t) for y in y_at if y < t)
            else:
                gap = min(abs(y - b) for y in y_at)
            if gap < CLEAR:
                bad.append("%s: %s sits %g units off the drift line, under the %g "
                           "a label needs" % (name, lname, gap, CLEAR))
                break
    return bad


def check_text_floor(svg: str, floor: int, name: str) -> list:
    sizes = [float(s) for s in re.findall(r'font-size="([0-9.]+)"', svg)]
    if not sizes:
        return ["%s: no text in the drawing at all" % name]
    if min(sizes) + 1e-9 < floor:
        return ["%s: the smallest text is %g units, under the %g floor this "
                "variant ships at" % (name, min(sizes), floor)]
    return []


def check_bar_style(svg: str, name: str) -> list:
    """The plate fills with the library's variables only, and no hex appears."""
    bad = []
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {SUBTLE, MIST, WITNESS, INK}:
        bad.append("%s: the plate fills with %s, and only the library's own "
                   "tokens may appear" % (name, sorted(fills)))
    if re.search(r"#[0-9A-Fa-f]{3,6}\b", svg):
        bad.append("%s: a literal hex color is in the drawing, so it will not "
                   "theme" % name)
    return bad


def _lin(c: int) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(colour: str) -> float:
    i = int(colour.lstrip("#"), 16)
    return 0.2126 * _lin(i >> 16) + 0.7152 * _lin((i >> 8) & 255) + 0.0722 * _lin(i & 255)


def contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_contrast() -> list:
    """Every colour this plate draws in, against the grounds it draws it on.

    The bar and the drift line carry the plate's meaning, so they are held to
    the 3:1 a graphic needs; every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "the axis marks and the drift line, "
                                    "graphics carrying meaning"),):
            for ground in ("canvas", "subtle"):
                ratio = contrast(t[colour], t[ground])
                if ratio < 3.0:
                    bad.append("%s theme, %s on %s: %.2f:1, under 3:1, and %s"
                               % (theme, colour, ground, ratio, what))
        for colour, what in (("ink", "the labels and speed numbers"),
                             ("witness", "the bar and its label"),
                             ("mist", "the feels and the footnotes")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s on canvas: %.2f:1, under 4.5, and %s is "
                           "text" % (theme, colour, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "reading-bar-wide.svg",
                         OUT / "reading-bar-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_axis(spec, name, svg)
        bad += check_drift(spec, name, svg)
        bad += check_bar(spec, name, svg)
        bad += check_numbers(spec, name, svg)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
        bad += check_path_clearance(spec, name)
        bad += check_text_floor(svg, floor, name)
        bad += check_bar_style(svg, name)
        if not path.is_file():
            bad.append("%s: nothing was written to %s" % (name, path))
    scratch.cleanup()
    for path, was in shipped.items():
        now = path.read_bytes() if path.is_file() else None
        if now != was:
            bad.append("the self-test changed %s, so proving the plate can fail "
                       "is a way to ship the plate that failed" % path.name)
    if len(rendered) == 2:
        for fact, what in FACTS:
            if fact and fact in rendered["wide"] and fact not in rendered["tall"]:
                bad.append("the variants disagree: %r (%s) is in the wide plate "
                           "and not the tall one" % (fact, what or "fact"))
    bad += check_contrast()
    if bad:
        print("reading-bar self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("reading-bar self-test ok: the four speeds sit at their own places on "
          "the axis in rising order with the datacenter number in another order "
          "of speed past the bar, the drift sags from its start without ending "
          "at its own floor and stays inside its panel, one witness line per "
          "panel at the bar's own value, the printed ends are the drawn line's "
          "own, every label sits inside the plate and none sits on another, "
          "both variants make the same claims, no hex colour, and every colour "
          "clears its bar in both themes")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
