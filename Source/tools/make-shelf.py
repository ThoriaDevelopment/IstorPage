#!/usr/bin/env python3
"""Generate the shelf plate: the ten documents the library act talks about,
drawn as the objects they are.

    python Source/tools/make-shelf.py [--self-test]

Writes Source/figures/shelf-wide.svg and Source/figures/shelf-tall.svg.

WHY THIS EXISTS. The library act's claim is "everything Istor knows is a
document you put there, and everything it says can be traced back to one",
and until now the only picture of that library was the exhibit capture: a
bitmap of a rail, at image resolution. This plate draws the ten documents
as the objects the act says they are - the rail's own rows, one document
per row, each with the status dot the app prints at its right.

WHERE THE NAMES COME FROM, exactly. The notes capture's caption states
"Ten notes, one for each source it read", and the page's notes rail lists
all ten note titles. Notes are named after their sources, so this list is
the page's own attested set of documents; the plate adds none and renames
none. Every title below is transcribed from Source/index.html's notes rail
(ul.rail-notes), punctuation included.

THE LAYOUT IS THE RAIL'S OWN GRAMMAR, scaled up to a plate: a filter-free
list of ten rows, title left at the rail's title weight, the azure dot at
the right end (the capture's "a status dot at its right"), and the app's
own zebra band on alternating rows --fill-row, sampled off the exhibit
capture exactly as the dispute table's was. The longest title measures
582.8 units at the tall plate's 15.5; the row gives it 594, so nothing
truncates. The wide plate runs the same list at 11.5 units, where the
longest title is 432.3 in a 594-unit row - the list is the one layout
that holds every name without abbreviating any.

WHAT IS DELIBERATELY ABSENT. No file types, sizes or dates (the page states
none). No green/amber status colours - the plate does not guess which
status each row carried in the capture; the dots are the structure the rail
prints (one per document), drawn in the plate's single azure, the colour
this page already uses for "the machine's own statement". No counts beyond
ten, which is the number the act states.

SELF-TEST. Demands exactly ten rows, the ten titles verbatim in the rail's
order, one dot per row, MEASURED covering every title at both sizes, no
title wider than its row's text box, token inks only, and both variants
carrying the same shelf.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import re
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

# The ten documents, verbatim from the page's notes rail, in its order.
TITLES = (
    "ancient astronomical computer",
    "The National Archaeological Museum in Athens",
    "The Saros cycle",
    "The Metonic cycle",
    "X-ray data from the Antikythera mechanism’s broken calendar ring",
    "Fragment C of the Antikythera mechanism",
    "Reconstruction of the missing front dial gearing of the Antikythera mechanism.",
    "Antikythera mechanism",
    "Antikythera wreck",
    "Decoding Antikythera mechanism",
)

# Measured widths per title at the two label sizes (Inter 500, browser,
# 2026-09-23). The generator refuses an unmeasured string: a guessed width
# would be a row that clips its own title.
MEASURED = {
    ("ancient astronomical computer", 12.5): 185.3,
    ("The National Archaeological Museum in Athens", 12.5): 282.5,
    ("The Saros cycle", 12.5): 95.3,
    ("The Metonic cycle", 12.5): 109.6,
    ("X-ray data from the Antikythera mechanism’s broken calendar ring", 12.5): 396.7,
    ("Fragment C of the Antikythera mechanism", 12.5): 252.0,
    ("Reconstruction of the missing front dial gearing of the Antikythera mechanism.", 12.5): 469.9,
    ("Antikythera mechanism", 12.5): 141.3,
    ("Antikythera wreck", 12.5): 109.0,
    ("Decoding Antikythera mechanism", 12.5): 201.9,
    ("ancient astronomical computer", 15.5): 229.7,
    ("The National Archaeological Museum in Athens", 15.5): 350.3,
    ("The Saros cycle", 15.5): 118.2,
    ("The Metonic cycle", 15.5): 135.9,
    ("X-ray data from the Antikythera mechanism’s broken calendar ring", 15.5): 492.0,
    ("Fragment C of the Antikythera mechanism", 15.5): 312.5,
    ("Reconstruction of the missing front dial gearing of the Antikythera mechanism.", 15.5): 582.8,
    ("Antikythera mechanism", 15.5): 175.2,
    ("Antikythera wreck", 15.5): 135.2,
    ("Decoding Antikythera mechanism", 15.5): 250.3,
    ("ancient astronomical computer", 16.5): 244.6,
    ("The National Archaeological Museum in Athens", 16.5): 372.9,
    ("The Saros cycle", 16.5): 125.9,
    ("The Metonic cycle", 16.5): 144.7,
    ("X-ray data from the Antikythera mechanism’s broken calendar ring", 16.5): 523.7,
    ("Fragment C of the Antikythera mechanism", 16.5): 332.7,
    ("Reconstruction of the missing front dial gearing of the Antikythera mechanism.", 16.5): 620.4,
    ("Antikythera mechanism", 16.5): 186.5,
    ("Antikythera wreck", 16.5): 143.9,
    ("Decoding Antikythera mechanism", 16.5): 266.5,
    # The head, the tall wrap lines and the footer, measured for the extents
    # gate: the gate recomputes every drawn label's extent from these
    # numbers, so every string the plate can draw needs its width at the
    # size it draws at - including the tall wrap lines (the titles' 16.5)
    # and the tall head's 17.82 (16.5 x 1.08).
    ("10 sources", 13.5): 69.4, ("10 sources", 17.82): 91.6, ("10 sources", 18.0): 92.6,
    ("The National Archaeological Museum", 16.5): 294.7,
    ("in Athens", 16.5): 73.9,
    ("X-ray data from the Antikythera", 16.5): 249.3,
    ("mechanism’s broken calendar ring", 16.5): 270.2,
    ("Fragment C of the Antikythera", 16.5): 237.6,
    ("mechanism", 16.5): 90.8,
    ("Reconstruction of the missing front", 16.5): 277.4,
    ("dial gearing of the Antikythera", 16.5): 238.6,
    ("mechanism.", 16.5): 95.8,
    ("every one of them a document on this machine", 12.5): 280.2,
    ("every one of them a document", 16.5): 240.9,
    ("on this machine", 16.5): 124.5,
}

# Row geometry. TEXT_X is the title's left edge; DOT_X the dot's centre, at
# the row's right end (the capture: "a status dot at its right"). The text
# box runs from TEXT_X to DOT_X - 14: every title must fit inside it, and
# the self-test measures that rather than trusting the layout.
#
# THE TALL PLATE WRAPS, and the wrap points are measured, not guessed: at
# the plate's own 16.5 units in a 340-wide row, five of the rail's ten
# titles cannot hold one line (the longest, "Reconstruction of the missing
# front dial gearing of the Antikythera mechanism.", needs 620.4 of a
# 296-unit text box). The app's own rail wraps its rows, so the plate wraps
# too: a title that does not fit breaks at the last space whose prefix fits,
# word widths from WORDS (same browser measurement as MEASURED). A wrapped
# row grows to hold its lines; the zebra band follows the row's real height.
WIDE_W, WIDE_H = 640.0, 372.0
TALL_W, TALL_H = 340.0, 500.0
ROW_H_WIDE, ROW_H_TALL = 30.0, 36.0
TEXT_X = 16.0
DOT_INSET = 14.0
TITLE_DY = 0.32   # baseline factor: title sits centred in its row

# Word widths at 16.5, Inter 500, browser-measured 2026-09-23, and the
# apostrophe word re-measured 2026-09-24 when the rail's titles moved to the
# curly form: `mechanism's` was 104.7 straight and is 102.7 curly, which
# changes the drawn glyph and not the wrap points (the longest line still
# ends at "ring", 270.2 of the 296-unit box). Only the titles that can wrap
# on the tall plate need their words here, and the table is keyed by the
# title's own spelling: a title whose punctuation moves must move here too,
# or the generator refuses the string rather than guessing a width.
WORDS = {
    "The": 30.4, "National": 65.0, "Archaeological": 117.9, "Museum": 68.1,
    "in": 14.1, "Athens": 55.4, "Saros": 44.9, "cycle": 41.8,
    "Metonic": 63.8, "X-ray": 43.5, "data": 34.6, "from": 36.9, "the": 25.3,
    "Antikythera": 91.3, "mechanism’s": 102.7, "broken": 54.7,
    "calendar": 68.8, "ring": 30.8, "Fragment": 75.1, "C": 12.1, "of": 16.2,
    "mechanism": 90.8, "Reconstruction": 119.6, "missing": 60.9,
    "front": 37.8, "dial": 27.9, "gearing": 60.3, "mechanism.": 95.8,
    "wreck": 48.2, "Decoding": 75.6, "ancient": 58.2,
    "astronomical": 101.8, "computer": 75.8,
}
SPACE = 4.4   # the space's advance at 16.5, measured with the words


def wrap_title(title, max_w, size):
    """The app's own wrap: break at the last space that fits. Returns the
    lines. The wide plate never calls this (every title fits there); the
    tall plate wraps only what its self-test proves needs wrapping."""
    factor = size / 16.5
    words = title.split(" ")
    lines, cur, cur_w = [], [], 0.0
    for w in words:
        ww = WORDS[w] * factor
        add = ww if not cur else ww + SPACE * factor
        if cur and cur_w + add > max_w:
            lines.append(" ".join(cur))
            cur, cur_w = [w], ww
        else:
            cur.append(w)
            cur_w += add
    if cur:
        lines.append(" ".join(cur))
    return lines


def rows(wide):
    """The layout: per title, (y_top, height, lines). Single-line rows keep
    the plate's row height; wrapped rows grow by a line. The plate height
    is derived from the rows, so wrapping changes the drawing, not a
    hand-tuned number. The base sizes are the type floor's own arithmetic:
    the tall plate renders 0.729 at 320 (16.5 -> 12.03px) and the wide one
    0.944 in its 700px field (12.5 -> 11.80px) - the earlier 11.5 rendered
    10.85px there, under."""
    size = 12.5 if wide else 16.5
    W = WIDE_W if wide else TALL_W
    row_h = ROW_H_WIDE if wide else ROW_H_TALL
    max_w = W - DOT_INSET - 14.0 - TEXT_X
    out = []
    y = 40.0 if wide else 46.0
    for t in TITLES:
        if wide or MEASURED[(t, size)] <= max_w:
            out.append((y, row_h, [t]))
            y += row_h
        else:
            lines = wrap_title(t, max_w, size)
            h = row_h + (len(lines) - 1) * size * 1.3
            out.append((y, h, lines))
            y += h
    return out, W, (y + (12.0 if wide else 14.0)), row_h, size


def plate(wide):
    layout, W, H, row_h, size = rows(wide)
    dot_x = W - DOT_INSET
    g = []
    g.append('  <g class="shelf-rows">')
    for i, (ry, rh, lines) in enumerate(layout):
        if i % 2 == 1:
            g.append('    <rect class="shelf-band" x="0" y="%.1f" '
                     'width="%g" height="%g"/>' % (ry, W, rh))
        if len(lines) == 1:
            ty = ry + rh * TITLE_DY + size * 0.34
            g.append('    <text class="shelf-title" x="%.1f" y="%.1f" '
                     'font-size="%g" font-family="%s">%s</text>'
                     % (TEXT_X, ty, size, INTER, lines[0]))
        else:
            lh = size * 1.3
            ty0 = ry + (rh - len(lines) * lh) / 2.0 + size * 0.34
            for j, line in enumerate(lines):
                g.append('    <text class="shelf-title" x="%.1f" y="%.1f" '
                         'font-size="%g" font-family="%s">%s</text>'
                         % (TEXT_X, ty0 + j * lh, size, INTER, line))
        g.append('    <circle class="shelf-dot" cx="%.1f" cy="%.1f" r="3.4"/>'
                 % (dot_x, ry + rh / 2.0))
        # the row's hairline, the rail's own separator
        if i:
            g.append('    <path class="shelf-rule" d="M0 %.1f H%g"/>'
                     % (ry, W))
    g.append('  </g>')

    head = ('  <text class="shelf-head" x="%.1f" y="%.1f" font-size="%g" '
            'font-family="%s">10 sources</text>'
            % (TEXT_X, (28.0 if wide else 32.0), size * 1.08, INTER))
    # The footer is the library caption's own sentence, verbatim - the
    # verbatim census in verify-figures.py holds every drawn string to the
    # page's prose, so the old compression ("every one a document on this
    # machine") fails the gate. The tall plate's width cannot hold it on one
    # line at 16.5 units, so it wraps the way the rows wrap: measured halves,
    # at the rail's line height - BOTH lines end-anchored at the dot column
    # like the wide plate's, after the cold read caught the first draft
    # drawing them start-anchored from x=dot_x, off the plate's clipped edge.
    foot_lines = ["every one of them a document", "on this machine"] \
        if not wide else ["every one of them a document on this machine"]
    foot = "".join(
        '  <text class="shelf-foot" x="%.1f" y="%.1f" font-size="%g" '
        'font-family="%s" text-anchor="end">%s</text>\n'
        % (dot_x, H - 10.0 - i * size * 1.3, size, INTER, line)
        for i, line in enumerate(foot_lines))

    variant = "wide" if wide else "tall"
    title = (
        "The library’s ten sources, drawn as the rows the app prints them "
        "as: one document per row, its title, and its status dot at the "
        "right. The titles are the page’s own transcription of the notes "
        "rail - ten notes, one for each source it read." if wide else
        "The library’s ten sources as the app’s rows: one document per "
        "row, title and status dot.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}"
     class="shelf-plate shelf-{variant}" role="img" focusable="false"
     aria-labelledby="shelf-{variant}-title">
  <title id="shelf-{variant}-title">{title}</title>
{head}
{chr(10).join(g)}
{foot}</svg>
'''
    return svg


def build_wide():
    return plate(True)


def build_tall():
    return plate(False)


def self_test():
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" - " + detail) if detail else ""))
        if not good:
            worst = 1

    for name, svg, wide in (("wide", build_wide(), True),
                            ("tall", build_tall(), False)):
        size = 12.5 if wide else 16.5
        W = WIDE_W if wide else TALL_W
        dot_x = W - DOT_INSET
        check(name + ": ten rows",
              svg.count('class="shelf-dot"') == 10)
        # no drawn line wider than its text box; the tall plate's wraps are
        # re-measured line by line, so the plate cannot clip a title and the
        # wrap cannot leave a line the measurement does not cover
        overflow = []
        for t in re.findall(r'class="shelf-title"[^>]*>([^<]+)</text>', svg):
            w = MEASURED.get((t, size))
            if w is None:
                # a wrapped line: rebuild its width from WORDS
                factor = size / 16.5
                w = sum(WORDS[wd] for wd in t.split(" ")) + \
                    SPACE * factor * (len(t.split(" ")) - 1)
            if TEXT_X + w > dot_x - 14:
                overflow.append((t[:30], round(TEXT_X + w - (dot_x - 14), 1)))
        check(name + ": every drawn line inside its row", not overflow,
              str(overflow[:2]))
        check(name + ": zebra on the odd rows",
              svg.count('class="shelf-band"') == 5)
        # the ten titles, reassembled row by row (a row's <text> elements all
        # precede its dot, so the dots partition the lines), are the rail's
        # ten in its order - the wrap changes the drawing, never the words
        rows_split = re.split(r'<circle class="shelf-dot"[^>]*/>', svg)
        reassembled = []
        for block in rows_split[:-1]:
            lines = re.findall(r'class="shelf-title"[^>]*>([^<]+)</text>', block)
            lines = [l for l in lines if l != "10 sources"]
            if lines:
                reassembled.append(" ".join(lines))
        check(name + ": reassembled titles are the rail's ten",
              reassembled == list(TITLES), str(reassembled[:2]))
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        check(name + ": label sizes are the plate's scale family",
              sizes <= {"%g" % round(size * f, 2) for f in
                        (1.0, 1.08, 0.92, 0.99, 1.1664)}, str(sizes))
        check(name + ": every title measured",
              all((t, size) in MEASURED for t in TITLES))
        # the floor: the smallest drawn size must clear 11.0px at the tall
        # plate's worst render scale (0.68 at a 320px phone); the wide plate
        # renders at 0.944 in its 700px field
        worst_scale = 0.729 if not wide else 0.944
        min_u = min(float(s) for s in sizes)
        check(name + ": smallest label clears the 11px floor",
              min_u * worst_scale >= 11.0,
              "min %g units -> %.2fpx" % (min_u, min_u * worst_scale))

    if worst == 0:
        print("shelf self-test ok: ten rows verbatim, dots, bands, fits, "
              "token inks, both variants")
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, svg in (("shelf-wide.svg", build_wide()),
                       ("shelf-tall.svg", build_tall())):
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
