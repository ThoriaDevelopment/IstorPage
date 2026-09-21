#!/usr/bin/env python3
"""Draw one sentence three ways: by letter, by token, by word.

    python Source/tools/make-token-rows.py [--self-test]

Writes Source/figures/token-rows-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues a position rather than reporting a fact: tokens sit
between two failed extremes. "Splitting on whole words leaves holes a research tool
cannot afford... Splitting on single characters goes the other way, stretching every
sentence into long sequences." A sentence can state that. Only a drawing can show it,
because the argument IS a shape: the same text cut at three granularities, the cuts
getting finer one way and coarser the other, and the middle one - the pieces a model
actually reads - the only row where nothing is unknown.

So the plate is three bands of the same sentence, aligned to the same width, with the
cuts marked where they fall: 35 for the letters, 9 for the tokens, 6 for the words.
The counts are in mono at the right of each band, and the word row's rare name is that
row's whole problem drawn: a dashed box where a word-level scheme has no entry, against
the two solid pieces the same name costs in the row above.

THE ROWS ARE THE SAME TEXT, and that is the invariant the self-test holds: every row
carries the literal string in TEXT, in order, checked by joining its pieces, and every
row spans EXACTLY the band width, because a row whose pieces did not add up to the same
line would be a different sentence. Each piece carries its own leading space - the
first version of this file did not, and the self-test said so, because a cut whose
pieces are just the words leaves the spaces in no piece at all.

THE COUNTS ARE DERIVED, THE ORDER IS ASSERTED. The number under each row is the number
of pieces drawn rather than a second copy of it, and the order letters > tokens > words
is asserted, because "the middle is the compromise" is the claim and a plate whose
middle was an extreme would be arguing against itself.

PLANNED, THEN DRAWN. Every string in the plate is placed by `plan()` before any of it
is rendered, so the checks can ask the questions a reader would: does every label sit
inside the plate, and does any label sit on top of another? The first version drew
straight from the geometry and passed its self-test while doing two of the things those
questions catch - a title running off the tall plate and a brace label sitting on the
row below it - which is why the layout is data here rather than arithmetic inside text
calls.

THE SPLIT IS AN ILLUSTRATION, NOT A MEASUREMENT, and both the drawing and the caption
say so. The page's own prose says the mapping is fixed per model; a real model's scheme
decides where the pieces fall, and this plate demonstrates the principle on a sentence
a research tool would actually meet - a name that is not in an English word list, and a
figure with a comma in it.

TOKENS, NOT COLORS, as every other plate here: fills and strokes are the library's own
variables, so the drawing themes with the page, and no hex value appears in it.
"""

import re
import sys
import tempfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

# The text, and the three cuts of it. The token split is a plausible one rather than
# any model's own: the name costs two pieces because its first letter is not in an
# English word list, and the figure costs four because a tokenizer has no reason to
# keep "4,096" whole.
TEXT = "the \u00c6gir dataset costs 4,096 tokens"
WORDS = ("the", " \u00c6gir", " dataset", " costs", " 4,096", " tokens")
TOKENS = ("the", " \u00c6", "gir", " dataset", " costs", " 4", ",", "096", " tokens")
LETTERS = tuple(TEXT)

# The word a word-level scheme has no entry for, and the label that says so. The dashed
# box is the only place --witness appears, since it marks the thing being pointed at.
HOLE = "\u00c6gir"
HOLE_LABEL = "no entry"
# The caption for the brace under the marked row. It is 37 characters because of the
# NARROW plate: centred on a brace it would run off the left edge (the first version
# did, and `check_inside` said so), and at 15 units the tall plate has room for 42.
PAIR_LABEL = "a name in two pieces, nothing unknown"

# The text floors, DERIVED rather than picked: the tall plate is 380 units wide and
# renders at 280px in a 320px viewport, a 0.737 scale, so 15 units lands at 11.05px and
# 14 at 10.3px, under the floor every plate here holds. The wide plate renders at 600
# of 640 units at 640px, so 16 units is 15.0px at its worst.
FLOOR_WIDE = 16
FLOOR_TALL = 15

# Per-character advance at font size: JetBrains Mono is exactly 0.6em, Inter is the
# same 0.53 estimate the other plates measure their labels against.
ADV_MONO = 0.60
ADV_SANS = 0.53

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_HAIR = "var(--hairline)"
TOK_SUBTLE = "var(--subtle)"
TOK_WITNESS = "var(--witness)"

# The bracket under the marked row: how far its arms turn up at the ends, and how far
# the pointer at its middle drops toward the label. Both are in plate units like every
# other measurement here, so the tall plate's bracket is the same shape at its scale.
ARM = 5.0
POINT = 4.0

# The title has to fit the narrow plate, which is what makes it a title rather than a
# sentence: 34 characters at 16 units is 288 of the tall plate's 336.
TITLE = "one sentence, three cuts, in pieces"

ROW_WORDS = (("letters", "by letter", ""),
             ("tokens", "by token", "the pieces a model reads"),
             ("words", "by word", ""))

# TWO short lines, and the shorter footnote is the improvement: the plate's first
# version carried the caveat here in five lines while the caption below the figure said
# the same thing in five more. The caveat belongs to the caption, because page text is
# read by the search index and the copy gate and text inside an SVG is read by neither,
# and what is left here is the one number a reader can use. The line breaks are set by
# the narrow plate: at 15 units the tall variant has room for 42 characters a line, and
# a footnote that ran off the edge would be a fact only a desktop reader gets.
NOTES = ("Rule of thumb: 1,000 words of English",
         "cost about 1,300 tokens.")

def cut(kind: str) -> tuple:
    """The pieces of one row, in order."""
    return {"letters": LETTERS, "tokens": TOKENS, "words": WORDS}[kind]


# What both variants must carry, whatever their composition. The counts are derived
# from the cuts, so a cut that changes changes the check with it.
FACTS = ((TITLE, "the title"), (HOLE_LABEL, "the word row's hole"),
         (PAIR_LABEL, "the pair under the marked row"),
         ("the pieces a model reads", "the marked row's note")) + \
        tuple((note, "a footnote line") for note in NOTES) + \
        tuple((name, "a row label") for _kind, name, _note in ROW_WORDS) + \
        tuple((str(len(cut(kind))), "the %s count" % kind)
              for kind, _name, _note in ROW_WORDS)


# Each variant: the plate, the band, the sizes, and where the rows sit. The composition
# is the same in both because the drawing is a LINE OF TEXT, which does not reflow into
# columns; what changes is the scale and where the counts sit - beside each band on the
# wide plate, at the end of each label line on the tall one, which has no column to
# spare. The row step is set by the brace under the marked band: it carries a label of
# its own, and the row below it needs to clear that label.
WIDE = {
    "w": 640, "h": 400, "name": "wide",
    "x0": 24.0, "band": 546.0, "mono": 26.0,
    "title_y": 30.0, "first_label_y": 62.0, "row_step": 96.0,
    "band_h": 44.0, "label": 16.0, "foot": 16.0,
    "foot_y": 360.0, "foot_step": 19.0,
    "count_beside_band": True,
}

TALL = {
    "w": 380, "h": 366, "name": "tall",
    "x0": 22.0, "band": 336.0, "mono": 16.0,
    "title_y": 26.0, "first_label_y": 54.0, "row_step": 92.0,
    "band_h": 36.0, "label": 15.0, "foot": 15.0,
    "foot_y": 328.0, "foot_step": 18.0,
    "count_beside_band": False,
}


# --------------------------------------------------------------------------
# The layout, as data
# --------------------------------------------------------------------------

def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * size * adv


def row_cuts(spec: dict, kind: str) -> list:
    """Where each piece of one row starts and ends, in plate units.

    The widths are the pieces' own characters times the mono advance, so every row adds
    up to the band width by construction - the same text is the same width whatever it
    is cut into, which is why the three bands line up."""
    xs, at = [], spec["x0"]
    for piece in cut(kind):
        w = width_of(piece, spec["mono"], ADV_MONO)
        xs.append((at, at + w, piece))
        at += w
    return xs


def hole_span(spec: dict) -> tuple:
    """Where the word's own letters are, and the point the box and its label are about.

    The piece carries its leading space, because that is what makes the three rows the
    same line; the BOX does not, because a dashed box drawn around the gap before a
    word would be pointing at the gap. The first drawing did exactly that."""
    for start, end, piece in row_cuts(spec, "words"):
        if piece.strip() == HOLE:
            return start + width_of(" ", spec["mono"], ADV_MONO), end
    return None


def row_y(spec: dict, i: int) -> tuple[float, float]:
    label_y = spec["first_label_y"] + i * spec["row_step"]
    return label_y, label_y + 8


def pair_pieces(spec: dict) -> list:
    """The two pieces of the marked row that are one name, and where the name's own
    letters begin and end.

    The pieces carry their leading space, because that is what makes the three rows the
    same line. The BRACKET does not, for the reason the dashed box does not: a bracket
    that began under the gap would be pointing at the gap, and the second version of
    this plate did exactly that, one character cell wide of the name.
    """
    out = []
    for start, end, piece in row_cuts(spec, "tokens"):
        if piece.strip() in ("\u00c6", "gir"):
            lead = piece[:len(piece) - len(piece.lstrip())]
            out.append((start + width_of(lead, spec["mono"], ADV_MONO), end))
    return out


def brace(spec: dict) -> tuple:
    """The bracket under the marked row, as a path and the span it points at.

    A BRACKET RATHER THAN A RULE, and the second version is the correction: a plain
    horizontal line five units under a band reads as an underline, which on a page of
    links means something else entirely. Arms turned up at the ends and a short pointer
    dropped at the middle read as an annotation, which is what this is - the label below
    belongs to these two pieces and to nothing else on the plate. The arms stop exactly
    at the band's lower edge, so the bracket hangs off the row rather than floating.
    """
    pair = pair_pieces(spec)
    if len(pair) != 2:
        return None
    a, b = pair[0][0], pair[1][1]
    _label_y, band_y = row_y(spec, 1)
    y2 = band_y + spec["band_h"] + 5
    mid = (a + b) / 2
    return ("M%g %g V%g H%g V%g M%g %g V%g"
            % (a, y2 - ARM, y2, b, y2 - ARM, mid, y2, y2 + POINT), (a, b), mid)


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font, colour,
    anchor). Drawing reads this and the checks read this, so neither can drift."""
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["label"], FONTS_SANS,
            TOK_MIST, "start")]
    for i, (kind, label, note) in enumerate(ROW_WORDS):
        label_y, band_y = row_y(spec, i)
        marked = kind == "tokens"
        colour = TOK_INK if marked else TOK_MIST
        out.append(("%s-label" % kind, label, spec["x0"], label_y, spec["label"],
                    FONTS_SANS, colour, "start"))
        if note:
            out.append(("%s-note" % kind, note,
                        spec["x0"] + width_of(label, spec["label"], ADV_SANS) + 14,
                        label_y, spec["label"], FONTS_SANS, colour, "start"))
        count = str(len(cut(kind)))
        cx = (spec["x0"] + spec["band"] + 22 if spec["count_beside_band"]
              else spec["x0"] + spec["band"] - 1)
        out.append(("%s-count" % kind, count, cx, label_y, spec["mono"], FONTS_MONO,
                    colour, "end" if not spec["count_beside_band"] else "start"))
        if marked:
            # The label under the brace, which is about the two pieces the word row's
            # hole is the alternative to, so the two rows can be read against each
            # other. It is anchored at the margin rather than centred on the brace: the
            # first version centred it, and a 37 character label centred on a 47 unit
            # brace runs off the left edge of the narrow plate.
            drawn = brace(spec)
            if drawn:
                y2 = row_y(spec, 1)[1] + spec["band_h"] + 5
                out.append(("pair", PAIR_LABEL, spec["x0"],
                            y2 + spec["label"] + 2, spec["label"], FONTS_SANS,
                            TOK_INK, "start"))
    hole = hole_span(spec)
    if hole:
        start, end = hole
        _label_y, band_y = row_y(spec, 2)
        out.append(("hole", HOLE_LABEL, (start + end) / 2,
                    band_y + spec["band_h"] + spec["label"] + 8, spec["label"],
                    FONTS_SANS, TOK_WITNESS, "middle"))
    for i, note in enumerate(NOTES):
        out.append(("note%d" % i, note, spec["x0"],
                    spec["foot_y"] + i * spec["foot_step"], spec["foot"], FONTS_SANS,
                    TOK_MIST, "start"))
    return out


def boxes(spec: dict) -> list:
    """The placed labels as rectangles, so the checks can ask what a reader sees."""
    out = []
    for name, s, x, y, size, _font, _colour, anchor in plan(spec):
        w = width_of(s, size, ADV_MONO if _font == FONTS_MONO else ADV_SANS)
        if anchor == "middle":
            x = x - w / 2
        elif anchor == "end":
            x = x - w
        out.append((name, x, x + w, y - size * 0.78, y + size * 0.22))
    return out


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def draw_band(spec: dict, kind: str, y: float) -> str:
    """One row: its wash, its text, its cuts, and - for the word row - the dashed box
    where a word-level scheme has no entry."""
    out = []
    x0, band, h = spec["x0"], spec["band"], spec["band_h"]
    cuts = row_cuts(spec, kind)
    if kind == "tokens":
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                   % (x0, y, band, h, TOK_SUBTLE))
    out.append(svg_text(x0, y + h * 0.68, TEXT, TOK_INK, spec["mono"], FONTS_MONO))

    # The cuts, as ticks on the band's edges rather than rules through the text: a 1px
    # line through 26-unit letterforms is noise, and the count is what is being read.
    # ALL THREE ROWS ARE CUT IN THE SAME COLOUR and differ in tick LENGTH, and that is
    # a correction rather than a preference: the first version drew the coarser cuts in
    # --hairline, which is 1.6:1 on the dark ground, and these ticks are not decoration
    # - they are the drawing's whole meaning, so they have to be visible in both themes.
    # Length carries the hierarchy instead, and ±0.01 of a band is not a difference any
    # reader has to be told about.
    tick = h * {"letters": 0.14, "tokens": 0.26, "words": 0.19}[kind]
    for _start, end, _piece in cuts[:-1]:
        out.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" '
                   'stroke-width="1"/>' % (end, y, end, y + tick, TOK_MIST))
        out.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" '
                   'stroke-width="1"/>' % (end, y + h - tick, end, y + h, TOK_MIST))

    if kind == "words":
        hole = hole_span(spec)
        if hole:
            start, end = hole
            out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="none" '
                       'stroke="%s" stroke-width="1.5" stroke-dasharray="5 4"/>'
                       % (start, y, end - start, h, TOK_WITNESS))
    return "".join(out)


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


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" '
           'height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("The same sentence cut three ways: %d pieces by letter, %d by token, "
                  "%d by word. A word-level scheme has no entry for %s, which costs two "
                  "tokens." % (len(LETTERS), len(TOKENS), len(WORDS), HOLE)),
              spec["name"])]

    for i, (kind, _label, _note) in enumerate(ROW_WORDS):
        _label_y, band_y = row_y(spec, i)
        if kind == "tokens":
            drawn = brace(spec)
            if drawn:
                out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" '
                           'stroke-linecap="round"/>' % (drawn[0], TOK_INK))
        out.append(draw_band(spec, kind, band_y))

    for name, s, x, y, size, font, colour, anchor in plan(spec):
        marked = name.startswith("tokens")
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if marked else None,
                            anchor=None if anchor == "start" else anchor))
    out.append("</svg>")
    return "".join(out)


def write(out: Path = OUT) -> list:
    """Both variants, drawn and written, into `out`.

    THE DIRECTORY IS A PARAMETER AND THE SELF-TEST USES ANOTHER ONE, which is a fix
    rather than a tidy-up. This plate's claims are proved by DOCTORING it - a token split
    with no seam, a bracket that has drifted off its pair - and the first version of
    those probes ran the drawing's own writer, so a check aimed at a broken plate wrote
    the broken plate into `Source/figures/` and left it there. The build then served it,
    and `verify-figures.py` reported it stale exactly as it should. A check that can
    overwrite what it checks is worse than no check, so the self-test draws into a
    temporary directory and the shipped drawing is only ever written by a plain run.
    """
    written = []
    for spec in (WIDE, TALL):
        svg = draw(spec)
        path = out / ("token-rows-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def check_same_text(spec: dict, name: str) -> list:
    """The three rows are the same sentence, and each spans the same width."""
    bad = []
    for row, _label, _note in ROW_WORDS:
        joined = "".join(cut(row))
        if joined != TEXT:
            bad.append("%s: the %s row reads %r, which is not the sentence in TEXT"
                       % (name, row, joined))
        cuts = row_cuts(spec, row)
        span = cuts[-1][1] - cuts[0][0]
        if abs(span - spec["band"]) > 0.01:
            bad.append("%s: the %s row spans %.2f units and the band is %.2f, so the "
                       "rows are not the same line" % (name, row, span, spec["band"]))
    return bad


def check_counts(spec: dict, name: str, svg: str) -> list:
    """The numbers drawn are the pieces drawn, and the middle one is between them."""
    bad = []
    for row, _label, _note in ROW_WORDS:
        n = str(len(cut(row)))
        if not re.search(r">%s</text>" % re.escape(n), svg):
            bad.append("%s: the %s row draws %d pieces and the number %s is not in the "
                       "drawing" % (name, row, len(cut(row)), n))
    order = [len(cut(row)) for row, _l, _n in ROW_WORDS]
    if not (order[0] > order[1] > order[2]):
        bad.append("%s: the cuts are %s, so tokens are not between letters and words - "
                   "which is the claim" % (name, order))
    # The marks drawn are the cuts claimed: each internal boundary is two ticks, top and
    # bottom, so the count of lines is arithmetic a reader could do rather than a
    # second number typed into the file. 94 for the wide plate, which is 2 x (34 + 8 + 5).
    want = 2 * sum(len(cut(row)) - 1 for row, _l, _n in ROW_WORDS)
    drawn = len(re.findall(r"<line ", svg))
    if drawn != want:
        bad.append("%s: %d cut ticks are drawn and the pieces imply %d, so the marks "
                   "and the counts disagree" % (name, drawn, want))
    return bad


def check_hole(spec: dict, name: str, svg: str) -> list:
    """The word row's hole is drawn where the hole is, and nothing else is dashed."""
    bad = []
    cuts = row_cuts(spec, "words")
    if len([c for c in cuts if c[2].strip() == HOLE]) != 1:
        bad.append("%s: %s is not one word of the word row (%r)"
                   % (name, HOLE, [c[2].strip() for c in cuts]))
    boxes_ = re.findall(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" '
                        r'height="([0-9.]+)" fill="none" stroke="var\(--witness\)"', svg)
    hole = hole_span(spec)
    if len(boxes_) != 1:
        bad.append("%s: %d dashed boxes are drawn, and only the word row has a hole"
                   % (name, len(boxes_)))
    elif hole:
        start, end = hole
        bx, _by, bw, _bh = [float(v) for v in boxes_[0]]
        if abs(bx - start) > 0.01 or abs(bw - (end - start)) > 0.01:
            bad.append("%s: the dashed box sits at %.1f and is %.1f wide, and %s spans "
                       "%.1f to %.1f - the box would point at the wrong word"
                       % (name, bx, bw, HOLE, start, end))
    # The token row splits the same name and knows nothing about it: a dashed box there
    # would mean the drawing had stopped making the argument.
    return bad


def check_marked(spec: dict, name: str, svg: str) -> list:
    """The row a model reads is the marked one, in ink, and the others are not."""
    bad = []
    ink = re.findall(r'fill="var\(--ink\)"[^>]*>([^<]*)</text>', svg)
    for _row, label, _note in ROW_WORDS:
        want = label == "by token"
        if want and label not in ink:
            bad.append("%s: %r is not drawn in ink, so the marked row is not marked"
                       % (name, label))
        if not want and label in ink:
            bad.append("%s: %r is drawn in ink too, so nothing is marked"
                       % (name, label))
    return bad


def check_brace(spec: dict, name: str, svg: str) -> list:
    """The bracket points at the two pieces the label under it is about, and at them only.

    The label is a sentence about a pair of pieces, so the bracket is the sentence's
    subject, and this is where the drawing and the claim are wired together: the path is
    compared to the span the pieces actually occupy, so a change to the token split
    moves the bracket or fails here. Nothing else in this plate is a path, which is what
    makes the count meaningful rather than decorative.
    """
    bad = []
    drawn = re.findall(r'<path d="([^"]+)" fill="none" stroke="([^"]+)"', svg)
    want = brace(spec)
    if want is None:
        bad.append("%s: the marked row does not split %s into two pieces, so the label "
                   "under it has no subject" % (name, HOLE))
        return bad
    path, (a, b), mid = want
    if len(drawn) != 1:
        bad.append("%s: %d brackets are drawn and the marked row has one pair of "
                   "pieces" % (name, len(drawn)))
    elif drawn[0][0] != path:
        bad.append("%s: the bracket is drawn as %r, and the pair %s to %s wants %r"
                   % (name, drawn[0][0], a, b, path))
    elif drawn[0][1] != TOK_INK:
        bad.append("%s: the bracket is stroked in %s, and it marks the row that is drawn "
                   "in ink" % (name, drawn[0][1]))
    if not a < mid < b:
        bad.append("%s: the pointer sits at %.1f, outside the pair's own span %.1f to "
                   "%.1f" % (name, mid, a, b))
    # THE TWO ROWS MARK THE SAME NAME, and this is the plate's argument written as
    # arithmetic: the word row's dashed box is where a word list fails, the bracket is
    # what a model does instead, and if they did not cover the same four cells the two
    # rows would be talking about different words.
    hole = hole_span(spec)
    if hole and (abs(hole[0] - a) > 0.01 or abs(hole[1] - b) > 0.01):
        bad.append("%s: the bracket spans %.1f to %.1f and the word row's box spans %.1f "
                   "to %.1f, so the two rows are not marking the same name"
                   % (name, a, b, hole[0], hole[1]))
    return bad


def check_inside(spec: dict, name: str) -> list:
    """Every label sits inside the plate. The tall variant's first version failed this
    at both ends: a title wider than the plate and footnote lines 40 units past it."""
    bad = []
    for label, x0, x1, top, bottom in boxes(spec):
        if x0 < 2 or x1 > spec["w"] - 2:
            bad.append("%s: %s runs %.1f to %.1f and the plate is 0 to %g"
                       % (name, label, x0, x1, spec["w"]))
        if top < 0 or bottom > spec["h"]:
            bad.append("%s: %s sits %.1f to %.1f and the plate is 0 to %g"
                       % (name, label, top, bottom, spec["h"]))
    return bad


def check_no_overlap(spec: dict, name: str) -> list:
    """No label sits on another. The first version put the brace label, which belongs
    to the marked row, on top of the word row's label line."""
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


def check_facts(svg: str, name: str) -> list:
    bad = []
    for fact, what in FACTS:
        if fact and fact not in svg:
            bad.append("%s: %r (%s) is not in the drawing" % (name, fact, what or "fact"))
    return bad


def check_text_floor(svg: str, floor: int, name: str) -> list:
    sizes = [float(s) for s in re.findall(r'font-size="([0-9.]+)"', svg)]
    if not sizes:
        return ["%s: no text in the drawing at all" % name]
    if min(sizes) + 1e-9 < floor:
        return ["%s: the smallest text is %g units, under the %g floor this variant "
                "ships at" % (name, min(sizes), floor)]
    return []


def check_cuts_visible(svg: str, name: str) -> list:
    """Every cut tick is drawn in a colour a reader can see in both themes.

    This check exists because the first drawing used --hairline here, which is 1.6:1 on
    the dark ground: invisible, in the theme half the visitors use, on the marks that
    carry the plate's meaning. A graphic needs 3:1, so the cuts are held to it."""
    bad = []
    strokes = set(re.findall(r'<line [^>]*stroke="([^"]+)"', svg))
    if strokes != {TOK_MIST}:
        bad.append("%s: the cut ticks are drawn in %s, and they carry the drawing's "
                   "meaning" % (name, sorted(strokes)))
    for theme, ground in (("light", "#FFFFFF"), ("dark", "#0A0A0A")):
        colour = {"light": "#6E6A66", "dark": "#A5A19B"}[theme]
        ratio = contrast(colour, ground)
        if ratio < 3.0:
            bad.append("%s: the cuts measure %.2f:1 on the %s ground, under the 3:1 a "
                       "meaningful graphic needs" % (name, ratio, theme))
    return bad


def check_no_hex(svg: str, name: str) -> list:
    if re.search(r"#[0-9A-Fa-f]{3,6}\b", svg):
        return ["%s: a literal hex color is in the drawing, so it will not theme" % name]
    return []


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
    """Every colour this plate draws text in, against every ground it draws it on.

    The witness is the interesting one: it labels the word row's hole, which is a
    sentence and not a graphic, so it has to clear 4.5:1 on the canvas in both themes -
    and it clears the light one by 0.05, which is worth a check rather than a memory."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    # (colour, the grounds it is actually drawn on, what it is for). The witness is not
    # tested against the washed band, because the plate never draws it there: the wash
    # belongs to the token row and the hole to the word row, and a check failing on a
    # combination the drawing does not contain would be the check drifting from the
    # plate rather than the plate being wrong.
    drawn = (("ink", ("canvas", "subtle"), "the row text, the counts, the marked row"),
             ("mist", ("canvas",), "the labels and the footnotes"),
             ("witness", ("canvas",), "the hole's box and its label"))
    for theme, t in themes.items():
        for colour, grounds, what in drawn:
            for ground in grounds:
                ratio = contrast(t[colour], t[ground])
                if ratio < 4.5:
                    bad.append("%s theme, %s on %s: %.2f:1, under 4.5, and %s is text"
                               % (theme, colour, ground, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    # What the tree held before anything was drawn, so the claim at the end of this
    # function can be checked rather than believed.
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "token-rows-wide.svg", OUT / "token-rows-tall.svg")}
    # Somewhere throwaway, for the reason `write()` gives: a doctored run of this file
    # must not be able to leave a doctored plate behind in Source/figures/.
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_same_text(spec, name)
        bad += check_counts(spec, name, svg)
        bad += check_hole(spec, name, svg)
        bad += check_brace(spec, name, svg)
        bad += check_marked(spec, name, svg)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
        bad += check_facts(svg, name)
        bad += check_text_floor(svg, floor, name)
        bad += check_no_hex(svg, name)
        bad += check_cuts_visible(svg, name)
        if not path.is_file():
            bad.append("%s: nothing was written to %s" % (name, path))
    scratch.cleanup()
    # THE SELF-TEST WROTE NOTHING INTO THE TREE, which is the failure it made once: the
    # probes for this plate doctor it, and a doctored probe wrote a doctored plate over
    # the shipped one. Read the bytes back rather than trust the scratch directory.
    for path, was in shipped.items():
        now = path.read_bytes() if path.is_file() else None
        if now != was:
            bad.append("the self-test changed %s, so proving the plate can fail is a way "
                       "to ship the plate that failed" % path.name)
    # The two variants make the same claims: a phone that got a different argument than
    # a desktop is the failure the two-variant rule exists for.
    if len(rendered) == 2:
        for fact, what in FACTS:
            if fact and fact in rendered["wide"] and fact not in rendered["tall"]:
                bad.append("the variants disagree: %r (%s) is in the wide plate and not "
                           "the tall one" % (fact, what or "fact"))
    bad += check_contrast()
    if bad:
        print("token-rows self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("token-rows self-test ok: all three rows are the same sentence and the same "
          "width, the counts are the pieces drawn and so are the cut marks, the middle "
          "cut is between the two, the word row's hole is the only dashed box and the "
          "bracket spans the pair the label under it names, every label sits inside the "
          "plate and none sits on another, both variants make the same claims, no hex "
          "colour, the cuts clear 3:1 as a graphic, and every colour clears 4.5:1 in "
          "both themes")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
