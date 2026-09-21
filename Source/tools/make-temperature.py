#!/usr/bin/env python3
"""Generate the temperature plate: one list of odds, three settings.

    python Source/tools/make-temperature.py [--self-test]

Writes Source/figures/temperature-wide.svg and Source/figures/temperature-tall.svg

WHY THIS EXISTS. `/what-is-temperature/` says the thing plainly - "Raised, the odds
flatten, and less likely candidates start winning slots" - and then has nothing to show
for it. That sentence is a picture: four candidates, the same four at every setting, with
their shares sliding off the likeliest one as the dial turns. The page's own section
heading is "A dial over the odds", so the plate is that heading drawn.

THE PLATE COMPUTES. Every other figure in this repository is a diagram of something the
prose asserts; this one runs the arithmetic the prose describes, softmax over four logits
with the temperature dividing first, and draws the answer. That is what makes its claims
checkable rather than decorative: a segment's width is its share of the free width, the
printed percentage is that segment's own width, and the top share falls from row to row
because softmax says it does. The CHECK recomputes all of it from LOGITS and TEMPERATURES
and compares the two, so the drawing and the maths cannot drift apart.

WHAT IT DOES NOT CLAIM. The four candidates and the gaps between their logits are made
up, and the note inside the plate says so. A real model's next-word odds depend on the
prompt and on everything it learned; the shape of the reshaping is the part that does not.
A made-up list is also the honest way to show one thing only: the CANDIDATES DO NOT CHANGE,
which is the page's answer to "is temperature a creativity switch".

TWO VARIANTS, and this plate is where the two-variant rule earns its keep differently from
the token plate. Here the composition survives at both widths, so what changes is only the
scale and where the share sits: beside the band on the wide plate, inside the band's width
on the narrow one, which has no column to spare. Both carry the same four words, the same
three settings, the same three percentages and the same notes, and that is asserted.

TOKENS, NOT COLORS: every fill is `var(--ink)` at a step of `fill-opacity`, so the ramp
themes with the page, and the faintest step is checked against the 3:1 a filled mark that
carries meaning needs - on both grounds, because half the visitors read the dark theme.
"""

import re
import sys
import tempfile
from pathlib import Path

# THE ODDS ARE IMPORTED, NOT DECLARED HERE. The page this plate sits on also carries a
# control the reader can drag, and the control reads a table computed from the same four
# numbers; two copies of a number are two numbers waiting to differ, so `odds.py` holds
# them and this file draws them. `verify-links.py` imports the same module for the same
# reason.
from odds import (CANDIDATES, DIAL_BAND, DIAL_GAP, DIAL_HEIGHT, LOGITS, SETTINGS,
                  STOP_STEP, STOPS, shares, softmax, table, widths)
# Aliased because this file has a plate-shaped `free_width(spec)`: the dial's band is one
# number, the plate's is a row of them.
from odds import free_width as free_of_band

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

WORDS = CANDIDATES
TEMPERATURES = SETTINGS

# One colour at four opacities. Not four colours: the point of the ramp is that the four
# segments are the same kind of thing, and steps of one ink theme with the page.
RAMP = (1.0, 0.80, 0.62, 0.46)

# The narrow plate's floor for a segment: 8 units of a 296 unit band is 2.7%, so a share
# smaller than that would be drawn as a sliver nobody could measure. The check holds the
# drawing to it, which is what makes "the last candidate climbs from 5% to 18%" visible
# rather than asserted.
VISIBLE_MIN = 8.0

GAP = 2.0            # the paper between two segments, which is what divides them
CHIP = 10.0          # the legend's swatch, which has to be the same fill as its segment

TITLE = "one list of odds, three temperatures"

# Three short lines, each inside the narrow plate's 42 characters at 15 units. The first
# states the mechanism, because "temperature" is the only thing here a reader cannot see.
NOTES = ("The same odds, divided by the setting",
         "and normalised back to 100 percent.",
         "The candidate list is made up.")

# The label a row carries. The number is drawn in mono and the word in sans, so the two
# settings can be read down the left edge without reading the sentence on each line.
TEMP_WORD = "temperature"

FLOOR_WIDE = 16
FLOOR_TALL = 15

# Per-character advance at font size, the same constants the other plates measure with.
ADV_MONO = 0.60
ADV_SANS = 0.53

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"

# The two grounds a segment is drawn on, and the ink it is drawn in, taken from the
# library's own token blocks. The check recomputes the faintest step against both.
THEMES = {"light": {"canvas": "#FFFFFF", "ink": "#171717"},
          "dark": {"canvas": "#0A0A0A", "ink": "#EDEDED"}}
GRAPHIC_MIN = 3.0    # a filled mark that carries meaning, per the cuts on the token plate


# --------------------------------------------------------------------------
# The composition, as data
# --------------------------------------------------------------------------

# The narrow plate is the constraint that set every number here. Its band is 296 units of
# a 380 unit plate, so the share column has to live on the label line; 296 units split four
# ways leaves the smallest share 15 units at the low setting, which is legible.
WIDE = {
    "w": 640, "h": 402, "name": "wide",
    "x0": 24.0, "band": 500.0, "share_x": 616.0,
    "mono": 22.0, "sans": 16.0,
    "title_y": 30.0, "key_y": 62.0, "first_label_y": 100.0, "row_step": 92.0,
    "bar_h": 40.0, "note_y": 352.0, "note_step": 19.0, "key_gap": 22.0,
}

TALL = {
    "w": 380, "h": 352, "name": "tall",
    "x0": 22.0, "band": 296.0, "share_x": 356.0,
    "mono": 16.0, "sans": 15.0,
    "title_y": 26.0, "key_y": 54.0, "first_label_y": 88.0, "row_step": 80.0,
    "bar_h": 32.0, "note_y": 312.0, "note_step": 18.0, "key_gap": 18.0,
}

VARIANTS = (WIDE, TALL)


def free_width(spec: dict) -> float:
    """The band minus the paper between its segments, which is what the shares divide."""
    return spec["band"] - GAP * (len(LOGITS) - 1)


def row_y(spec: dict, i: int) -> tuple:
    """The label line's baseline and the bar's top edge for one setting."""
    label_y = spec["first_label_y"] + i * spec["row_step"]
    return label_y, label_y + 8


def segments(spec: dict, i: int) -> list:
    """One bar's segments, in order, as (x, width, opacity).

    Cumulative from the band's left edge: the first segment is the likeliest candidate and
    the bar reads left to right, which is asserted rather than assumed.
    """
    ys = row_y(spec, i)[1]
    free = free_width(spec)
    at, out = spec["x0"], []
    for j, p in enumerate(shares(TEMPERATURES[i])):
        w = p * free
        out.append((at, w, RAMP[j], ys))
        at += w + GAP
    return out


def legend(spec: dict) -> list:
    """The key under the title: one swatch and one word per candidate, in order."""
    x, y = spec["x0"], spec["key_y"]
    out = []
    for j, word in enumerate(WORDS):
        out.append((x, y - CHIP, j))
        x += CHIP + 6 + len(word) * spec["sans"] * ADV_SANS + spec["key_gap"]
    return out


def share_text(i: int) -> str:
    """The percentage printed on a row: the top candidate's own share, to one decimal."""
    return "%.1f%%" % (shares(TEMPERATURES[i])[0] * 100)


def temp_text(i: int) -> str:
    t = TEMPERATURES[i]
    return "%g" % t


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font, colour,
    anchor). Drawing reads this and the checks read it, so labels cannot drift from the
    questions asked about them - which is the lesson the token plate wrote down.
    """
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["sans"], FONTS_SANS,
            TOK_MIST, "start")]
    for j, word in enumerate(WORDS):
        x = legend(spec)[j][0] + CHIP + 6
        out.append(("key%d" % j, word, x, spec["key_y"], spec["sans"], FONTS_SANS,
                    TOK_INK if j == 0 else TOK_MIST, "start"))
    for i in range(len(TEMPERATURES)):
        label_y, _bar_y = row_y(spec, i)
        out.append(("temp%d" % i, TEMP_WORD, spec["x0"], label_y, spec["sans"],
                    FONTS_SANS, TOK_MIST, "start"))
        out.append(("tempv%d" % i, temp_text(i),
                    spec["x0"] + len(TEMP_WORD) * spec["sans"] * ADV_SANS + 8,
                    label_y, spec["mono"], FONTS_MONO, TOK_INK, "start"))
        out.append(("share%d" % i, share_text(i), spec["share_x"], label_y,
                    spec["mono"], FONTS_MONO, TOK_INK, "end"))
    for k, note in enumerate(NOTES):
        out.append(("note%d" % k, note, spec["x0"],
                    spec["note_y"] + k * spec["note_step"], spec["sans"], FONTS_SANS,
                    TOK_MIST, "start"))
    return out


def boxes(spec: dict) -> list:
    """The placed labels as rectangles, so the checks can ask what a reader sees."""
    out = []
    for name, s, x, y, size, font, _colour, anchor in plan(spec):
        w = len(s) * size * (ADV_MONO if font == FONTS_MONO else ADV_SANS)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        out.append((name, x, x + w, y - size * 0.78, y + size * 0.22))
    return out


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_text(x, y, s, fill, size, font, weight=None, anchor=None) -> str:
    bits = ['<text x="%g" y="%g" font-family="%s" font-size="%g" fill="%s"'
            % (x, y, font, size, fill)]
    if weight:
        bits.append(' font-weight="%s"' % weight)
    if anchor:
        bits.append(' text-anchor="%s"' % anchor)
    bits.append(">%s</text>" % esc(s))
    return "".join(bits)


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" '
           'height="%g" role="img" aria-label="%s" focusable="false" data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("The same four next-word candidates at three temperatures. The "
                  "likeliest word takes %s of the picks at %s and %s at %s, while the "
                  "least likely climbs from %s to %s, so raising the setting flattens "
                  "the odds without changing the candidates."
                  % (share_text(0), temp_text(0), share_text(2), temp_text(2),
                     "%.1f%%" % (shares(TEMPERATURES[0])[-1] * 100),
                     "%.1f%%" % (shares(TEMPERATURES[2])[-1] * 100))),
              spec["name"])]

    for j, (x, y, _j) in enumerate(legend(spec)):
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" '
                   'fill-opacity="%g" data-k="key"/>'
                   % (x, y, CHIP, CHIP, TOK_INK, RAMP[j]))

    # The bars, one per setting, under the label line that belongs to it.
    for i in range(len(TEMPERATURES)):
        for sx, sw, op, sy in segments(spec, i):
            out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" '
                       'fill-opacity="%g" data-k="seg"/>'
                       % (sx, sy, sw, spec["bar_h"], TOK_INK, op))

    for name, s, x, y, size, font, colour, anchor in plan(spec):
        bold = "600" if name.startswith(("temp", "share")) else None
        out.append(svg_text(x, y, s, colour, size, font, weight=bold,
                            anchor=None if anchor == "start" else anchor))
    out.append("</svg>")
    return "".join(out)


DIAL = Path(__file__).resolve().parent.parent / "temperature-dial.partial"


def dial_markup() -> str:
    """The control's markup, with every number in it computed here.

    WHY THE MARKUP IS GENERATED. `/what-is-temperature/` now carries a slider the reader
    can drag, and the bar under it has to agree with the plate above it at every position
    on the slider. The script that drives it therefore does NO ARITHMETIC: this file bakes
    the widths for every position into `data-stops`, and the script looks a row up and
    writes it out. One implementation of softmax, three callers - the plate draws from it,
    this table is computed from it, and `verify-links.py` recomputes it against what
    shipped - which is the only way a reader cannot find a position where the drawing and
    the prose disagree.

    `hidden` IS AUTHORED RATHER THAN ADDED, and the direction matters: a reader without
    scripting sees the plate and its caption, which is the whole argument, and never sees a
    control that would not move. The script is what puts it on the page, and verify-links
    holds the page to both halves.
    """
    import json
    default = SETTINGS[1]
    rows = table()
    segs = ""
    at = 0.0
    for j, w in enumerate(widths(default)):
        segs += ('\n        <rect data-seg="%d" x="%g" y="0" width="%g" height="%g" '
                 'fill="var(--ink)" fill-opacity="%g" />'
                 % (j, at, w, DIAL_HEIGHT, RAMP[j]))
        at += w + DIAL_GAP
    row = [r for r in rows if abs(r["t"] - default) < 1e-9][0]
    stops = " ".join('<option value="%g"></option>' % t for t in SETTINGS)
    return (
        '<div class="temperature-dial" data-temperature-dial hidden>\n'
        '  <label class="temperature-dial-head" for="temperature-setting">'
        'Another setting</label>\n'
        '  <input id="temperature-setting" type="range" min="%g" max="%g" step="%g" '
        'value="%g" list="temperature-stops" />\n'
        '  <datalist id="temperature-stops">%s</datalist>\n'
        '  <svg class="temperature-dial-bar" viewBox="0 0 %g %g" width="%g" height="%g" '
        'aria-hidden="true" data-free="%g" data-gap="%g" data-stops=\'%s\'>%s\n'
        '  </svg>\n'
        '  <p class="temperature-dial-readout" id="temperature-readout">Setting '
        '<span data-readout="setting">%s</span>: %s takes '
        '<span data-readout="top">%.1f%%</span> of the picks, and %s '
        '<span data-readout="last">%.1f%%</span>.</p>\n'
        '</div>'
        % (STOPS[0], STOPS[-1], STOP_STEP, default, stops,
           DIAL_BAND, DIAL_HEIGHT, DIAL_BAND, DIAL_HEIGHT,
           free_of_band(), DIAL_GAP, json.dumps(rows, separators=(",", ":")), segs,
           "%g" % default, CANDIDATES[0], row["top"], CANDIDATES[-1], row["last"]))


def write(out: Path = OUT) -> list:
    """Both variants, drawn and written, into `out`.

    THE DIRECTORY IS A PARAMETER and the self-test uses another one, because the probes
    that prove this plate can fail doctor its drawing, and a check that can overwrite what
    it checks is worse than no check. That lesson cost a shipped figure on the token plate.
    """
    written = []
    for spec in VARIANTS:
        svg = draw(spec)
        path = out / ("temperature-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


def write_dial() -> str:
    """The control's markup, written where LIBRARY_INCLUDES looks for it."""
    markup = dial_markup()
    DIAL.write_bytes(markup.encode("utf-8"))
    return markup


# --------------------------------------------------------------------------
# The claims
# --------------------------------------------------------------------------

SEG_RE = re.compile(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" '
                    r'height="([0-9.]+)" fill="([^"]+)" fill-opacity="([0-9.]+)" '
                    r'data-k="(seg|key)"/>')


def rects(svg: str, kind: str) -> list:
    return [(float(x), float(y), float(w), float(h), fill, float(op))
            for x, y, w, h, fill, op, k in SEG_RE.findall(svg) if k == kind]


def check_model(spec: dict, name: str, svg: str) -> list:
    """Every segment is its share of the free width, recomputed here from the odds.

    This is the plate's whole claim as arithmetic. The drawing divides by the setting and
    normalises; so does `softmax()`, from the same two constants, and the two answers are
    compared segment by segment. A doctored width, a doctored setting and a doctored logit
    all land here.
    """
    bad = []
    segs = rects(svg, "seg")
    want = len(LOGITS) * len(TEMPERATURES)
    if len(segs) != want:
        return ["%s: %d segments are drawn and %d settings over %d candidates need %d"
                % (name, len(segs), len(TEMPERATURES), len(LOGITS), want)]
    free = free_width(spec)
    for i in range(len(TEMPERATURES)):
        p = shares(TEMPERATURES[i])
        row = segs[i * len(LOGITS):(i + 1) * len(LOGITS)]
        for j, (x, y, w, h, _fill, _op) in enumerate(row):
            if abs(w - p[j] * free) > 0.05:
                bad.append("%s, %s: segment %d is %.2f units wide and its share is %.2f%% "
                           "of %.0f, which is %.2f units"
                           % (name, temp_text(i), j, w, p[j] * 100, free, p[j] * free))
            if abs(h - spec["bar_h"]) > 0.01:
                bad.append("%s, %s: segment %d is %.1f units tall and the bars are %.1f, "
                           "so the rows are not the same chart"
                           % (name, temp_text(i), j, h, spec["bar_h"]))
        # The bar reads left to right, with one gap of paper between segments.
        at = spec["x0"]
        for j, (x, y, w, _h, _f, _o) in enumerate(row):
            if abs(x - at) > 0.05:
                bad.append("%s, %s: segment %d starts at %.2f and the bar has reached "
                           "%.2f, so the segments overlap or float"
                           % (name, temp_text(i), j, x, at))
            at += w + GAP
        if abs(at - GAP - (spec["x0"] + spec["band"])) > 0.05:
            bad.append("%s, %s: the bar ends at %.2f and the band ends at %.2f"
                       % (name, temp_text(i), at - GAP, spec["x0"] + spec["band"]))
        if abs(row[0][1] - row_y(spec, i)[1]) > 0.01:
            bad.append("%s, %s: the bar is drawn at y %.1f and its label line is at %.1f"
                       % (name, temp_text(i), row[0][1], row_y(spec, i)[1]))
    return bad


def check_printed(spec: dict, name: str, svg: str) -> list:
    """The printed percentage is the drawn segment's own width, not a second calculation.

    A percentage typed into the file would agree with the drawing on the day it was typed
    and with nothing after that, so the number is read back off the geometry it labels.
    """
    bad = []
    free = free_width(spec)
    for i in range(len(TEMPERATURES)):
        path, _t = share_text(i), None
        if path not in svg:
            bad.append("%s: the share %s is not in the drawing" % (name, path))
            continue
        top = rects(svg, "seg")[i * len(LOGITS)][2]
        drawn = "%.1f%%" % (top / free * 100)
        if drawn != path:
            bad.append("%s: %s is printed and the drawn segment is %s of the bar"
                       % (name, path, drawn))
        printed = "%.1f%%" % (shares(TEMPERATURES[i])[0] * 100)
        if printed != path:
            bad.append("%s: %s is printed and the odds make it %s"
                       % (name, path, printed))
    return bad


def check_flattens(spec: dict, name: str, svg: str) -> list:
    """Raising the setting moves share off the first word and onto the others.

    The page's sentence, and it is checked against the DRAWN WIDTHS rather than against the
    odds, because a reader reads widths: the top segment has to lose at least a quarter of
    its length from the first row to the last, and the last segment has to more than
    double, on the narrow plate, which is the harder of the two. A plate where the top
    share fell and nothing gained would be a shrinking pie rather than flattened odds.
    """
    bad = []
    free = free_width(spec)
    tops = [rects(svg, "seg")[i * len(LOGITS)][2] for i in range(len(TEMPERATURES))]
    tails = [rects(svg, "seg")[i * len(LOGITS) + len(LOGITS) - 1][2]
             for i in range(len(TEMPERATURES))]
    for i in range(len(TEMPERATURES) - 1):
        if not tops[i] > tops[i + 1]:
            bad.append("%s: the top segment is %.1f units at %s and %.1f at %s, so "
                       "raising the setting did not flatten the odds"
                       % (name, tops[i], temp_text(i), tops[i + 1], temp_text(i + 1)))
        if not tails[i] < tails[i + 1]:
            bad.append("%s: the last segment is %.1f units at %s and %.1f at %s, so no "
                       "candidate climbed"
                       % (name, tails[i], temp_text(i), tails[i + 1], temp_text(i + 1)))
    if tops[-1] > tops[0] * 0.75:
        bad.append("%s: the top segment goes %.1f to %.1f units, a change too small to "
                   "read" % (name, tops[0], tops[-1]))
    if tails[-1] < tails[0] * 2:
        bad.append("%s: the last segment goes %.1f to %.1f units, which is not the climb "
                   "the caption claims" % (name, tails[0], tails[-1]))
    # The bar is a share of something: whatever the setting, a row is a hundred percent.
    for i in range(len(TEMPERATURES)):
        row = rects(svg, "seg")[i * len(LOGITS):(i + 1) * len(LOGITS)]
        if abs(sum(w for _x, _y, w, _h, _f, _o in row) - free) > 0.05:
            bad.append("%s, %s: the segments add up to %.2f units and the band has %.2f "
                       "for them" % (name, temp_text(i),
                                     sum(w for _x, _y, w, _h, _f, _o in row), free))
        if abs(sum(shares(TEMPERATURES[i])) - 1.0) > 1e-9:
            bad.append("the shares at %s do not add up to one" % temp_text(i))
    # THE CANDIDATES DO NOT CHANGE, which is the page's answer to "is temperature a
    # creativity switch": the odds are sorted once and every bar keeps that order, so the
    # only thing the setting moves is share.
    if not LOGITS[0] > LOGITS[-1]:
        bad.append("the odds are not sorted, so the bars are not ranked")
    spread = [LOGITS[0] / t - LOGITS[-1] / t for t in TEMPERATURES]
    if not spread[0] > spread[-1]:
        bad.append("the gap between the top and bottom odds is %s across the settings, "
                   "so the settings are not in the order they are drawn" % spread)
    return bad


def check_visible(spec: dict, name: str, svg: str) -> list:
    """Every segment is wide enough to measure, on the plate a phone gets.

    A share drawn as a two-unit sliver is not evidence of anything, so the smallest one is
    held to a floor. It clears it by 7 units at the low setting and by more as the odds
    flatten, which is the direction this plate wants to be tight in.
    """
    bad = []
    for i in range(len(TEMPERATURES)):
        for j, (x, _y, w, _h, _f, _o) in enumerate(
                rects(svg, "seg")[i * len(LOGITS):(i + 1) * len(LOGITS)]):
            if w < VISIBLE_MIN - 0.01:
                bad.append("%s, %s: segment %d is %.1f units wide, under the %.0f a share "
                           "needs to be read" % (name, temp_text(i), j, w, VISIBLE_MIN))
    return bad


def _lin(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour: str) -> float:
    i = int(hex_colour.lstrip("#"), 16)
    return 0.2126 * _lin(i >> 16) + 0.7152 * _lin((i >> 8) & 255) + 0.0722 * _lin(i & 255)


def contrast(fg: str, bg: str) -> float:
    la, lb = _luminance(fg), _luminance(bg)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def blend(ink: str, ground: str, opacity: float) -> str:
    """What a step of the ramp actually looks like: ink at opacity over the paper."""
    a = int(ink.lstrip("#"), 16)
    b = int(ground.lstrip("#"), 16)
    out = 0
    for shift in (16, 8, 0):
        v = ((a >> shift) & 255) * opacity + ((b >> shift) & 255) * (1 - opacity)
        out |= int(round(v)) << shift
    return "#%06X" % out


def check_ramp(name: str, svg: str) -> list:
    """One ink, four steps, and every step visible on both grounds.

    The ramp is how a reader tells the four candidates apart, so it is checked the way the
    token plate checks its cuts: the faintest step is measured against the paper it is
    drawn on, in both themes, because a filled mark that carries meaning needs 3:1 and half
    the readers are in the dark theme.
    """
    bad = []
    segs = rects(svg, "seg")
    if not segs:
        return ["%s: no segments to check" % name]
    fills = {f for _x, _y, _w, _h, f, _o in segs}
    if fills != {TOK_INK}:
        bad.append("%s: the segments are filled with %s, so the ramp is a second colour "
                   "rather than one ink at four steps" % (name, sorted(fills)))
    ops = sorted({round(o, 3) for _x, _y, _w, _h, _f, o in segs}, reverse=True)
    if [round(o, 3) for o in RAMP] != ops:
        bad.append("%s: the steps drawn are %s and the ramp is %s"
                   % (name, ops, [round(o, 3) for o in RAMP]))
    for i in range(len(ops) - 1):
        if ops[i] - ops[i + 1] < 0.12:
            bad.append("%s: steps %.2f and %.2f are too close to tell apart"
                       % (name, ops[i], ops[i + 1]))
    faint = min(ops)
    for theme, t in THEMES.items():
        ratio = contrast(blend(t["ink"], t["canvas"], faint), t["canvas"])
        if ratio < GRAPHIC_MIN:
            bad.append("%s: the faintest step is %.2f:1 on the %s ground, under the %.1f "
                       "a filled mark needs" % (name, ratio, theme, GRAPHIC_MIN))
    return bad


def check_legend(spec: dict, name: str, svg: str) -> list:
    """The key is the chart: one swatch per candidate, same fills, same order, same words.

    A legend that drifted from the ramp would leave a reader matching the wrong word to the
    wrong segment, and nothing else in the plate would notice.
    """
    bad = []
    keys = rects(svg, "key")
    if len(keys) != len(WORDS):
        bad.append("%s: %d swatches are drawn for %d candidates"
                   % (name, len(keys), len(WORDS)))
        return bad
    for j, (x, y, w, h, fill, op) in enumerate(keys):
        if abs(w - CHIP) > 0.01 or abs(h - CHIP) > 0.01:
            bad.append("%s: swatch %d is %.1f by %.1f and the key is %.0f square"
                       % (name, j, w, h, CHIP))
        if fill != TOK_INK or abs(op - RAMP[j]) > 0.001:
            bad.append("%s: swatch %d is %s at %.2f and its segment is %s at %.2f"
                       % (name, j, fill, op, TOK_INK, RAMP[j]))
        word = WORDS[j]
        if word not in svg:
            bad.append("%s: %s has a swatch and no word" % (name, word))
        seg = rects(svg, "seg")[j]
        if abs(seg[5] - op) > 0.001:
            bad.append("%s: %s is swatched at %.2f and drawn at %.2f in the first bar"
                       % (name, word, op, seg[5]))
    for _x, _y, _w, _h, _f, op in keys:
        if op not in [round(o, 3) for o in RAMP]:
            bad.append("%s: a swatch uses %.2f, which is not a step of the ramp" % (name, op))
    return bad


def check_dial(markup: str) -> list:
    """The control's markup is the odds, drawn at the setting it starts on.

    Everything here is a comparison between what shipped and what `odds.py` computes, in
    the file the PLATE is drawn from: the table the script reads, the four widths the
    page shows before any script runs, and the two percentages in the sentence under the
    bar. A table that drifted from the plate would leave a reader able to find a position
    where the two disagree, which is the one thing this control must not do.
    """
    import json
    bad = []
    default = SETTINGS[1]
    rows = [r for r in table() if abs(r["t"] - default) < 1e-9][0]

    # The table the script reads.
    m = re.search(r"data-stops='([^']+)'", markup)
    if not m:
        return ["the control carries no table for the script to read"]
    try:
        drawn = json.loads(m.group(1))
    except ValueError as exc:
        return ["the control's table is not readable: %s" % exc]
    if drawn != table():
        bad.append("the control's table is not what odds.py computes: %d rows on the "
                   "page and %d in the table" % (len(drawn), len(table())))
    else:
        for row in drawn:
            if abs(sum(row["w"]) - free_of_band()) > 0.05:
                bad.append("at %s the table's widths add up to %.2f and the band has "
                           "%.2f for them" % (row["t"], sum(row["w"]), free_of_band()))

    # The bar the page shows before the script runs, which has to be the default row.
    segs = re.findall(r'<rect data-seg="(\d+)" x="([0-9.]+)" y="0" width="([0-9.]+)" '
                      r'height="([0-9.]+)" fill="([^"]+)" fill-opacity="([0-9.]+)"',
                      markup)
    if len(segs) != len(CANDIDATES):
        bad.append("the control draws %d segments and there are %d candidates"
                   % (len(segs), len(CANDIDATES)))
    else:
        at = 0.0
        for j, (_idx, x, w, h, fill, op) in enumerate(segs):
            if abs(float(w) - rows["w"][j]) > 0.01:
                bad.append("the drawn segment %d is %s units wide and the table at %s "
                           "says %.2f" % (j, w, default, rows["w"][j]))
            if abs(float(x) - at) > 0.01:
                bad.append("the drawn segment %d starts at %s and the bar has reached "
                           "%.2f" % (j, x, at))
            if fill != TOK_INK or abs(float(op) - RAMP[j]) > 0.001:
                bad.append("the drawn segment %d is %s at %s and the plate's ramp is %s "
                           "at %.2f" % (j, fill, op, TOK_INK, RAMP[j]))
            if abs(float(h) - DIAL_HEIGHT) > 0.01:
                bad.append("the drawn segment %d is %s units tall" % (j, h))
            at += float(w) + DIAL_GAP

    # The sentence under the bar, which is the control's accessible read-out.
    for key, want in (("setting", "%g" % default),
                      ("top", "%.1f%%" % rows["top"]),
                      ("last", "%.1f%%" % rows["last"])):
        span = re.search(r'data-readout="%s">([^<]*)<' % key, markup)
        if not span:
            bad.append("the sentence under the bar has no %s in it" % key)
        elif span.group(1) != want:
            bad.append("the sentence says %s is %r and the table says %r"
                       % (key, span.group(1), want))
    for word, what in ((CANDIDATES[0], "the first candidate"),
                       (CANDIDATES[-1], "the last candidate")):
        if word not in markup:
            bad.append("the sentence under the bar does not name %s" % what)

    # And the things that make it a control rather than a picture: reachable settings, and
    # hidden until a script is there to move it.
    rng = re.search(r'type="range" min="([0-9.]+)" max="([0-9.]+)" step="([0-9.]+)" '
                    r'value="([0-9.]+)"', markup)
    if not rng:
        bad.append("the control's slider has no range on it")
    else:
        lo, hi, step, value = (float(v) for v in rng.groups())
        if lo > min(SETTINGS) or hi < max(SETTINGS):
            bad.append("the slider runs %g to %g and the plate draws settings out to %g "
                       "to %g" % (lo, hi, min(SETTINGS), max(SETTINGS)))
        if abs(step - STOP_STEP) > 1e-9:
            bad.append("the slider steps by %g and the table is every %g"
                       % (step, STOP_STEP))
        if abs(value - default) > 1e-9:
            bad.append("the slider starts at %g and the drawn bar is the table's %g"
                       % (value, default))
    if 'data-temperature-dial hidden' not in markup:
        bad.append("the control is not authored hidden, so a reader without a script "
                   "would meet a control that cannot move")
    m = re.search(r'data-free="([0-9.]+)"', markup)
    if not m or abs(float(m.group(1)) - free_of_band()) > 0.01:
        bad.append("the bar declares %s units of free width and the table divides %g"
                   % (m.group(1) if m else "no", free_of_band()))
    return bad


def check_inside(spec: dict, name: str) -> list:
    bad = []
    for label, x0, x1, top, bottom in boxes(spec):
        if x0 < 2 or x1 > spec["w"] - 2:
            bad.append("%s: %s runs %.1f to %.1f and the plate is 0 to %g"
                       % (name, label, x0, x1, spec["w"]))
        if top < 0 or bottom > spec["h"]:
            bad.append("%s: %s sits %.1f to %.1f and the plate is 0 to %g"
                       % (name, label, top, bottom, spec["h"]))
    for i in range(len(TEMPERATURES)):
        bar_y = row_y(spec, i)[1]
        if bar_y + spec["bar_h"] > spec["h"] - 2:
            bad.append("%s: the bar at %s ends at %.1f, past the plate's %g"
                       % (name, temp_text(i), bar_y + spec["bar_h"], spec["h"]))
    return bad


def check_no_overlap(spec: dict, name: str) -> list:
    bad = []
    bs = boxes(spec)
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, b = bs[i], bs[j]
            if a[1] < b[2] - 0.5 and b[1] < a[2] - 0.5 and a[3] < b[4] - 0.5 \
                    and b[3] < a[4] - 0.5:
                bad.append("%s: %s and %s overlap (%.1f-%.1f against %.1f-%.1f)"
                           % (name, a[0], b[0], a[1], a[2], b[1], b[2]))
    return bad


def facts() -> tuple:
    """What both variants must carry, derived from the odds rather than typed in.

    The counts a reader is asked to trust are computed here from the same two constants the
    drawing uses, so a change to either moves the claim with the plate.
    """
    out = [(TITLE, "the title")] + [(w, "a candidate") for w in WORDS] + \
          [(TEMP_WORD, "the setting's label")] + \
          [(temp_text(i), "a setting") for i in range(len(TEMPERATURES))] + \
          [(share_text(i), "a printed share") for i in range(len(TEMPERATURES))] + \
          [(n, "a note line") for n in NOTES]
    return tuple(out)


def check_facts(svg: str, name: str) -> list:
    bad = []
    for fact, what in facts():
        if fact and fact not in svg:
            bad.append("%s: %r (%s) is not in the drawing" % (name, fact, what))
    return bad


def check_text_floor(svg: str, floor: float, name: str) -> list:
    sizes = [float(s) for s in re.findall(r'font-size="([0-9.]+)"', svg)]
    if not sizes:
        return ["%s: no text in the drawing at all" % name]
    if min(sizes) + 1e-9 < floor:
        return ["%s: the smallest text is %g units, under the %g floor this variant "
                "ships at" % (name, min(sizes), floor)]
    return []


def check_no_hex(svg: str, name: str) -> list:
    if re.search(r"#[0-9A-Fa-f]{3,6}\b", svg):
        return ["%s: a literal hex colour is in the drawing, so it will not theme" % name]
    return []


def check_contrast() -> list:
    """The plate's text, against the grounds it is drawn on, in both themes."""
    drawn = (("ink", "the settings, the shares, the first candidate"),
             ("mist", "the title, the other candidates, the notes"))
    bad = []
    for theme, t in THEMES.items():
        for token, what in drawn:
            colour = {"light": {"ink": "#171717", "mist": "#6E6A66"},
                      "dark": {"ink": "#EDEDED", "mist": "#A5A19B"}}[theme][token]
            ratio = contrast(colour, t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s: %.2f:1, under 4.5, and %s is text"
                           % (theme, token, ratio, what))
    return bad


# --------------------------------------------------------------------------
# The self-test, including the proofs that it can fail
# --------------------------------------------------------------------------

def _doctor(svg: str, kind: str) -> str:
    """One deliberate break, for each claim that has to be able to notice it."""
    if kind == "width":            # a segment five units wider than its share
        m = re.search(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" '
                      r'height="([0-9.]+)" fill="var\(--ink\)" fill-opacity="1" '
                      r'data-k="seg"/>', svg)
        return svg[:m.start()] + m.group(0).replace('width="%s"' % m.group(3),
                                                    'width="%g"' % (float(m.group(3)) + 5)) \
            + svg[m.end():]
    if kind == "printed":          # a percentage a hair off the geometry it labels
        return svg.replace(share_text(0), "%.1f%%" % (shares(TEMPERATURES[0])[0] * 100 + 0.5))
    if kind == "sliver":           # a share drawn too thin to measure
        return re.sub(r'fill-opacity="0\.46" data-k="seg"',
                      'fill-opacity="0.46" data-k="seg"', svg).replace(
            'width="%g"' % (shares(TEMPERATURES[-1])[-1] * free_width(WIDE)),
            'width="2"', 1)
    if kind == "ramp":             # the faintest step, made invisible
        return svg.replace('fill-opacity="0.46"', 'fill-opacity="0.12"')
    if kind == "key":              # a swatch that is not its segment's fill
        return svg.replace('fill-opacity="0.62" data-k="key"',
                           'fill-opacity="0.8" data-k="key"')
    if kind == "order":            # the candidates re-ranked per row
        return svg.replace(share_text(2), "%.1f%%" % (shares(TEMPERATURES[-1])[-1] * 100))
    raise ValueError(kind)


DOCTORS = (("width", check_model, "a segment wider than its share"),
           ("printed", check_printed, "a printed percentage off its own segment"),
           ("sliver", check_visible, "a share drawn too thin to measure"),
           ("ramp", check_ramp, "a ramp step made invisible"),
           ("key", check_legend, "a swatch that is not its segment's fill"),
           ("order", check_printed, "a percentage that belongs to another candidate"))


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "temperature-wide.svg", OUT / "temperature-tall.svg",
                         DIAL)}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_model(spec, name, svg)
        bad += check_printed(spec, name, svg)
        bad += check_visible(spec, name, svg)
        bad += check_ramp(name, svg)
        bad += check_legend(spec, name, svg)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
        bad += check_flattens(spec, name, svg)
        bad += check_facts(svg, name)
        bad += check_text_floor(svg, floor, name)
        bad += check_no_hex(svg, name)
        if not path.is_file():
            bad.append("%s: nothing was written to %s" % (name, path))
    scratch.cleanup()
    # The control's markup is checked against the odds rather than against the drawing: it
    # is the second thing made of these numbers, and the page ships it every night.
    markup = dial_markup()
    bad += check_dial(markup)
    # The two variants make the same claims: a phone that got a different chart than a
    # desktop is the failure the two-variant rule exists for.
    if len(rendered) == 2:
        for fact, what in facts():
            if fact and fact in rendered["wide"] and fact not in rendered["tall"]:
                bad.append("the variants disagree: %r (%s) is in the wide plate and not "
                           "the tall one" % (fact, what))
    bad += check_contrast()
    # And the plate can fail. Each doctor breaks one thing and names the check that has to
    # see it; a claim nobody has watched fail is a claim nobody has tested.
    for kind, check, what in DOCTORS:
        spec = WIDE
        doctored = _doctor(draw(spec), kind)
        caught = check(spec, "doctored", doctored) if check in (
            check_model, check_printed, check_visible, check_legend) \
            else check("doctored", doctored)
        if not caught:
            bad.append("the self-test cannot catch %s: %s passed on a doctored plate"
                       % (what, check.__name__))
    # The control gets the same treatment: a table a hair off the widths the page shows, a
    # control that is not hidden, and a slider that cannot reach a setting the plate draws.
    for what, doctored in (
            ("a table that does not match the page's own bar",
             markup.replace('"w":[121.45,81.41,54.57,36.58]', '"w":[121.45,81.41,54.57,30]')),
            ("a control a reader without a script would meet",
             markup.replace('data-temperature-dial hidden', 'data-temperature-dial')),
            ("a slider that cannot reach the plate's high setting",
             markup.replace('max="2"', 'max="1.5"'))):
        if not check_dial(doctored):
            bad.append("the self-test cannot catch %s" % what)
    # THE SELF-TEST WROTE NOTHING INTO THE TREE, which is the failure the token plate made:
    # read the bytes back rather than trust the scratch directory.
    for path, was in shipped.items():
        now = path.read_bytes() if path.is_file() else None
        if now != was:
            bad.append("the self-test changed %s, so proving the plate can fail is a way "
                       "to ship the plate that failed" % path.name)
    if bad:
        print("temperature self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("temperature self-test ok: every segment is the share of the bar that softmax "
          "gives it, every printed percentage is read back off its own segment, the bar "
          "reads left to right with paper between its parts and ends where the band ends, "
          "raising the setting flattens the odds in both directions, the ramp is one ink "
          "at four steps and the faintest clears 3:1 on both grounds, the key is the "
          "chart, every label is inside the plate and none sits on another, both variants "
          "make the same claims, no hex colour, the control's table and its own bar are "
          "the odds at the setting it starts on and its slider reaches every setting the "
          "plate draws, and each of the nine doctors is caught by the claim it breaks")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    markup = write_dial()
    print("%s  %s B" % (DIAL.name, format(len(markup.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
