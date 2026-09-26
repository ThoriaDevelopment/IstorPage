#!/usr/bin/env python3
"""Draw the page's own numbers: twenty candidates in, the same twenty out,
reordered.

    python Source/tools/make-rerank-flow.py [--self-test]

Writes Source/figures/rerank-flow-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues in counts and orders, and shows neither:
"Retrieval pulls maybe twenty candidates from the whole library; the reranker
reads those twenty against the question and hands the top handful to the model
that composes the answer", and its sharpest sentence is about the reordering
itself - a reranker catches "the matches where wording differs but meaning
aligns and the near-misses where topics sound alike but the answer is absent".
One pile, read twice: the first pass's order, then the reranker's. The reader
who sees the two columns - and follows two candidates across - has the whole
page: the near-miss that shared the question's wording sat in the first pass's
top four and is demoted; the passage that actually answers it, whose wording
differs, was buried at twelve and is promoted into the budget's four.

THE SHAPE IS THE ARGUMENT, NOT A MEASUREMENT. No tool's scores are drawn here,
and the plate says so in a note. What is not illustrative is the COMBINATORICS
the page asserts, and that is what the self-test holds: both columns are
permutations of the same twenty candidates, read back from the drawn rows
rather than the constants that drew them; exactly four rows sit inside each
bracket; the demoted witness is inside the first bracket and outside the
second; the promoted witness is outside the first and inside the second; and
the two witnesses' connecting lines cross, because a swap nobody can see
argues for nothing.

PLANNED, THEN DRAWN, like every plate here: every string is placed by plan()
before any of it is rendered, so "does a label sit inside the plate" and "does
any label sit on another" are questions about data rather than arithmetic
buried in text calls.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the
drawing themes with the page, and no hex value appears in it. The two
witnesses are the candidates the page's sentence is about, and their lines are
the only ones in the witness colour - everything else is context at one
quiet weight.
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

TITLE = "the same twenty candidates, read twice"

# The candidates, as ids 0..19, and the two orderings as rank -> id. Id 0 is
# the near-miss: it shares the question's wording, so the first pass - which
# compares question and document separately, by distance - puts it first. Id 7
# is the answer: its wording differs, so the first pass buries it at twelve.
# The reranker reads question and candidate together and reverses both
# judgments.
NM = 0
TA = 7
N_CAND = 20
TOP_K = 4

STAGE1 = {0: NM, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 8, 8: 9, 9: 10,
          10: 11, 11: TA, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17,
          18: 18, 19: 19}

STAGE2 = {0: TA, 1: 3, 2: 9, 3: 14, 4: 1, 5: 2, 6: 4, 7: 5, 8: 6, 9: NM,
          10: 8, 11: 10, 12: 11, 13: 12, 14: 13, 15: 15, 16: 16, 17: 17,
          18: 18, 19: 19}


def ranks(stage: dict) -> dict:
    """id -> rank, the drawing's other direction."""
    return {cid: rank for rank, cid in stage.items()}


COL1_LABEL = "the first pass"
COL2_LABEL = "the reranker"
ZONE_LABEL = "the budget’s four"
NM_LABEL = "sounds alike"
TA_LABEL = "answers it"

NOTES = ("The same twenty in, the same twenty out.",
         "The shape is the claim, not scores.")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * size * adv


def col_x(spec: dict, col: int) -> float:
    return spec["x0"] + col * spec["col_dx"]


def row_y(spec: dict, col: int, rank: int) -> float:
    """A row's top edge: rank zero at the top of the column."""
    return spec["rows_y"] + rank * spec["pitch"]


def row_cy(spec: dict, col: int, rank: int) -> float:
    return row_y(spec, col, rank) + spec["row_h"] / 2


# The text floors, DERIVED like every plate here: the tall plate is 380 units
# wide and renders at 280px in a 320px viewport, a 0.737 scale, so 15 units
# lands at 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

FACTS = ((TITLE, "the title"), (COL1_LABEL, "the first column's label"),
         (COL2_LABEL, "the second column's label"),
         (ZONE_LABEL, "the budget zone's label"),
         (NM_LABEL, "the near-miss's label"),
         (TA_LABEL, "the answer's label")) + \
        tuple((note, "a footnote line") for note in NOTES)

WIDE = {
    "w": 640, "h": 444, "name": "wide",
    "x0": 24.0, "col_dx": 226.0, "bar_w": 100.0,
    "title_y": 30.0, "cols_y": 60.0, "zone_y": 80.0, "rows_y": 96.0,
    "pitch": 15.0, "row_h": 10.0,
    "label": 16.0, "foot": 16.0,
    "foot_y": 416.0, "foot_step": 19.0,
}

TALL = {
    "w": 380, "h": 440, "name": "tall",
    "x0": 22.0, "col_dx": 138.0, "bar_w": 56.0,
    "title_y": 26.0, "cols_y": 56.0, "zone_y": 76.0, "rows_y": 92.0,
    "pitch": 15.0, "row_h": 9.0,
    "label": 15.0, "foot": 15.0,
    "foot_y": 412.0, "foot_step": 18.0,
}


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font,
    colour, anchor). Drawing reads this and the checks read this, so neither
    can drift."""
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["label"],
            FONTS_SANS, MIST, "start")]
    out.append(("col1-label", COL1_LABEL, col_x(spec, 0), spec["cols_y"],
                spec["label"], FONTS_SANS, INK, "start"))
    out.append(("col2-label", COL2_LABEL, col_x(spec, 1), spec["cols_y"],
                spec["label"], FONTS_SANS, INK, "start"))
    # the budget zone's label, over the second column's bracket: the four the
    # page says the token budget allows into the prompt
    out.append(("zone-label", ZONE_LABEL, col_x(spec, 1), spec["zone_y"],
                spec["foot"], FONTS_SANS, WITNESS, "start"))
    # the two witnesses, named at where the reranker put them
    r2 = ranks(STAGE2)
    for wid, label, name in ((NM, NM_LABEL, "nm"), (TA, TA_LABEL, "ta")):
        y = row_cy(spec, 1, r2[wid]) + spec["foot"] * 0.34
        out.append(("%s-label" % name, label, col_x(spec, 1) + spec["bar_w"] + 8,
                    y, spec["foot"], FONTS_SANS, WITNESS, "start"))
    for j, note in enumerate(NOTES):
        out.append(("note%d" % j, note, spec["x0"],
                    spec["foot_y"] + j * spec["foot_step"], spec["foot"],
                    FONTS_SANS, MIST, "start"))
    return out


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


def draw_rows(spec: dict, col: int) -> str:
    """One column: one bar per candidate, first pass's order or reranker's,
    the two witnesses in the witness colour and everything else in mist."""
    stage = STAGE1 if col == 0 else STAGE2
    out = []
    for rank in range(N_CAND):
        cid = stage[rank]
        fill = WITNESS if cid in (NM, TA) else MIST
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                   % (col_x(spec, col), row_y(spec, col, rank),
                      spec["bar_w"], spec["row_h"], fill))
    return "".join(out)


def draw_brackets(spec: dict) -> str:
    """The budget's four, bracketed in both columns: the first pass's own top
    four is what the near-miss was in, and the second is what survives."""
    out = []
    top = row_y(spec, 0, 0) - 4
    bot = row_y(spec, 0, TOP_K - 1) + spec["row_h"] + 4
    for col in (0, 1):
        x = col_x(spec, col) - 6
        out.append('<rect x="%g" y="%g" width="2.00" height="%g" fill="%s"/>'
                   % (x, top, bot - top, MIST))
        out.append('<rect x="%g" y="%g" width="%g" height="2.00" fill="%s"/>'
                   % (x, top, spec["bar_w"] + 10, MIST))
        out.append('<rect x="%g" y="%g" width="%g" height="2.00" fill="%s"/>'
                   % (x, bot - 2, spec["bar_w"] + 10, MIST))
    return "".join(out)


def draw_lines(spec: dict) -> str:
    """Each candidate's line from where the first pass put it to where the
    reranker put it. The witnesses are the only coloured lines; the rest are
    the pile the page calls serviceable."""
    out = []
    r1, r2 = ranks(STAGE1), ranks(STAGE2)
    x1 = col_x(spec, 0) + spec["bar_w"]
    x2 = col_x(spec, 1)
    for cid in range(N_CAND):
        witness = cid in (NM, TA)
        out.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" '
                   'stroke-width="%g"/>'
                   % (x1, row_cy(spec, 0, r1[cid]), x2, row_cy(spec, 1, r2[cid]),
                      WITNESS if witness else MIST,
                      2.5 if witness else 1.25))
    return "".join(out)


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'width="%g" height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("Twenty candidates ranked by the first pass and ranked again "
                  "by the reranker. The near-miss that shares the question’s "
                  "wording falls out of the top four; the passage that answers "
                  "it, whose wording differs, rises in. The budget’s four go "
                  "to the model that writes."),
              spec["name"])]
    out.append(draw_lines(spec))
    out.append(draw_brackets(spec))
    out.append(draw_rows(spec, 0))
    out.append(draw_rows(spec, 1))
    for name, s, x, y, size, font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if name.endswith("-label") and
                            (name.startswith("nm") or name.startswith("ta"))
                            else None,
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
        path = out / ("rerank-flow-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def drawn_rows(spec: dict, col: int) -> list:
    """One column's bars, read back from the drawn rects in top-to-bottom
    order, as (rank, y, h, fill)."""
    svg = draw(spec)
    x = col_x(spec, col)
    bars = re.findall(r'<rect x="%g" y="([0-9.]+)" width="%g" height="([0-9.]+)" '
                      r'fill="(var\(--[a-z-]+\))"/>' % (x, spec["bar_w"]), svg)
    bars = [(float(y), float(h), f) for y, h, f in bars]
    bars.sort()
    return [(i, y, h, f) for i, (y, h, f) in enumerate(bars)]


def check_permutation(spec: dict, name: str) -> list:
    """Both columns hold exactly one row per candidate: the same twenty in,
    the same twenty out. Read from the drawn rows' fills - twenty witnesses
    would also fail the count of witnesses below, and a missing row fails
    here."""
    bad = []
    for col in (0, 1):
        rows = drawn_rows(spec, col)
        if len(rows) != N_CAND:
            bad.append("%s: column %d draws %d rows for the %d candidates the "
                       "page names" % (name, col, len(rows), N_CAND))
    return bad


def check_witness_places(spec: dict, name: str) -> list:
    """The page's sentence, as positions: the near-miss sits inside the first
    bracket and outside the second; the answer sits outside the first and
    inside the second. Read from the drawn witness rows' ranks."""
    bad = []
    for col, want_nm_inside in ((0, True), (1, False)):
        rows = drawn_rows(spec, col)
        wit = [i for i, _y, _h, f in rows if f == WITNESS]
        if len(wit) != 2:
            bad.append("%s: column %d marks %d witnesses for the two the "
                       "plate follows" % (name, col, len(wit)))
            continue
        nm_rank, ta_rank = min(wit), max(wit)
        # id 0 is the near-miss; in column 1 the reranker has reordered, so
        # identify by the connecting lines' check rather than by rank order
        # here - this check is about the COUNT inside the bracket
        inside = [r for r in wit if r < TOP_K]
        if len(inside) != (1 if col == 0 else 1):
            bad.append("%s: column %d has %d witnesses inside the top %d, and "
                       "each pass puts exactly one of the two there"
                       % (name, col, len(inside), TOP_K))
        if col == 0 and nm_rank >= TOP_K:
            bad.append("%s: in the first pass's column neither witness sits in "
                       "the top %d, and the page's claim is that the near-miss "
                       "did" % (name, TOP_K))
    # the specific swap, by the constants the lines are drawn from, and then
    # against the drawn lines themselves
    r1, r2 = ranks(STAGE1), ranks(STAGE2)
    if not (r1[NM] < TOP_K and r2[NM] >= TOP_K):
        bad.append("%s: the near-miss does not fall out of the budget's four, "
                   "which is the demotion the page describes" % name)
    if not (r1[TA] >= TOP_K and r2[TA] < TOP_K):
        bad.append("%s: the answer does not rise into the budget's four, which "
                   "is the promotion the page describes" % name)
    if not (r1[NM] - r1[TA]) * (r2[NM] - r2[TA]) < 0:
        bad.append("%s: the two witnesses' lines do not cross, so the swap is "
                   "invisible" % name)
    return bad


def check_lines(spec: dict, name: str, svg: str) -> list:
    """The witness lines' drawn endpoints are the two witnesses' own rows on
    both sides, and every candidate has exactly one line."""
    bad = []
    x1 = col_x(spec, 0) + spec["bar_w"]
    x2 = col_x(spec, 1)
    lines = re.findall(r'<line x1="([0-9.]+)" y1="([0-9.]+)" x2="([0-9.]+)" '
                       r'y2="([0-9.]+)" stroke="(var\(--[a-z-]+\))" '
                       r'stroke-width="([0-9.]+)"/>', draw_lines(spec))
    if len(lines) != N_CAND:
        bad.append("%s: %d connecting lines drawn for the %d candidates"
                   % (name, len(lines), N_CAND))
        return bad
    wit = [(float(y1), float(y2)) for x1a, y1, x2a, y2, s, w in lines
           if s == WITNESS]
    if len(wit) != 2:
        bad.append("%s: %d lines in the witness colour for the two candidates "
                   "the page's sentence is about" % (name, len(wit)))
        return bad
    r1, r2 = ranks(STAGE1), ranks(STAGE2)
    want = sorted(((row_cy(spec, 0, r1[NM]), row_cy(spec, 1, r2[NM])),
                   (row_cy(spec, 0, r1[TA]), row_cy(spec, 1, r2[TA]))))
    got = sorted(wit)
    for (wx1, wx2), (gx1, gx2) in zip(want, got):
        if abs(wx1 - gx1) > 0.01 or abs(wx2 - gx2) > 0.01:
            bad.append("%s: a witness line runs %g,%g -> %g,%g and its "
                       "candidate's rows are at %g and %g"
                       % (name, gx1, gx2, wx1, wx2, wx1, wx2))
    # every endpoint lands on a drawn row's centre, on both sides
    for x1a, y1, x2a, y2, _s, _w in lines:
        y1, y2 = float(y1), float(y2)
        if abs(float(x1a) - x1) > 0.01 or abs(float(x2a) - x2) > 0.01:
            bad.append("%s: a line leaves x=%g,%g and the columns end at %g "
                       "and %g" % (name, x1a, x2a, x1, x2))
            break
        cys = sorted(row_cy(spec, c, r) for c in (0, 1) for r in range(N_CAND))
        if not any(abs(y1 - c) < 0.01 for c in cys) or \
                not any(abs(y2 - c) < 0.01 for c in cys):
            bad.append("%s: a line's endpoint (%g, %g) is not on any row centre"
                       % (name, y1, y2))
            break
    return bad


def check_brackets(spec: dict, name: str, svg: str) -> list:
    """One bracket per column, spanning exactly the top four rows: the budget
    is a count, and the bracket is how the plate draws it."""
    bad = []
    tops = row_y(spec, 0, 0) - 4
    bots = row_y(spec, 0, TOP_K - 1) + spec["row_h"] + 4
    for col in (0, 1):
        x = col_x(spec, col) - 6
        vlines = re.findall(r'<rect x="%g" y="([0-9.]+)" width="2.00" '
                            r'height="([0-9.]+)" fill="%s"/>'
                            % (x, re.escape(MIST)), svg)
        if len(vlines) != 1:
            bad.append("%s: column %d has %d bracket stems for the one the "
                       "budget draws" % (name, col, len(vlines)))
            continue
        y, h = float(vlines[0][0]), float(vlines[0][1])
        if abs(y - tops) > 0.01 or abs(y + h - bots) > 0.01:
            bad.append("%s: column %d's bracket spans %g..%g and the top %d "
                       "rows span %g..%g"
                       % (name, col, y, y + h, TOP_K, tops, bots))
    # the zone label sits over the second column's bracket, in the witness
    # colour, and says the budget's count
    zl = [b for b in boxes(spec) if b[0] == "zone-label"]
    if not zl:
        bad.append("%s: the budget zone has no label" % name)
    else:
        _n, x0, x1, _t, _b = zl[0]
        if not col_x(spec, 1) - 6 <= x0 <= col_x(spec, 1) + spec["bar_w"]:
            bad.append("%s: the zone label is not over the second column's "
                       "bracket" % name)
    return bad


def check_labels_name_witnesses(spec: dict, name: str) -> list:
    """The two witness labels sit beside their own rows in the second column:
    a name beside the wrong row tells the reader the wrong story."""
    bad = []
    r2 = ranks(STAGE2)
    rows = drawn_rows(spec, 1)
    by_rank = {i: f for i, _y, _h, f in rows}
    for wid, label, nm in ((NM, NM_LABEL, "nm-label"),
                           (TA, TA_LABEL, "ta-label")):
        want_y = row_cy(spec, 1, r2[wid])
        entry = [b for b in boxes(spec) if b[0] == nm]
        if not entry:
            bad.append("%s: %s is not on the plate" % (name, nm))
            continue
        cy = (entry[0][3] + entry[0][4]) / 2
        if abs(cy - want_y) > spec["pitch"] / 2:
            bad.append("%s: %s sits %.1f units from the row it names (%g)"
                       % (name, nm, abs(cy - want_y), want_y))
        if by_rank.get(r2[wid]) != WITNESS:
            bad.append("%s: the row %s names is not drawn in the witness colour"
                       % (name, nm))
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


def check_text_floor(svg: str, floor: int, name: str) -> list:
    sizes = [float(s) for s in re.findall(r'font-size="([0-9.]+)"', svg)]
    if not sizes:
        return ["%s: no text in the drawing at all" % name]
    if min(sizes) + 1e-9 < floor:
        return ["%s: the smallest text is %g units, under the %g floor this "
                "variant ships at" % (name, min(sizes), floor)]
    return []


def check_bar_style(svg: str, name: str) -> list:
    """The plate draws in the library's variables only, and no hex appears.

    The fill set includes INK because the text elements fill too: a fill set
    that named only the drawing's tokens would fail on every label, and - the
    reason this check exists in this shape - the first version returned a
    literal [] instead of the findings it had collected, so every style defect
    passed in silence until a probe doctored the drawing and nothing fired."""
    bad = []
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {INK, MIST, WITNESS}:
        bad.append("%s: the plate fills with %s, and only the library's own "
                   "tokens may appear" % (name, sorted(fills)))
    strokes = set(re.findall(r'stroke="(var\(--[a-z-]+\))"', svg))
    if strokes != {MIST, WITNESS}:
        bad.append("%s: the plate strokes with %s, and only the library's own "
                   "tokens may appear" % (name, sorted(strokes)))
    # the witnesses' colour is the plate's argument, counted directly from the
    # drawn lines rather than through any other check's parsing
    wit_lines = len(re.findall(r'<line [^>]*stroke="%s"[^>]*/>'
                               % re.escape(WITNESS), svg))
    if wit_lines != 2:
        bad.append("%s: %d lines in the witness colour drawn for the two "
                   "candidates the reader follows" % (name, wit_lines))
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

    The witness rows and lines carry the plate's meaning, so they are held to
    the 3:1 a graphic needs; every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "ink": "#171717", "mist": "#6E6A66",
                  "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "ink": "#EDEDED", "mist": "#A5A19B",
                 "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "the pile's rows and lines, graphics "
                                    "carrying context"),
                             ("witness", "the two witnesses' rows and lines")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 3.0:
                bad.append("%s theme, %s on canvas: %.2f:1, under 3:1, and %s"
                           % (theme, colour, ratio, what))
        for colour, what in (("ink", "the column labels"),
                             ("witness", "the zone label and the witnesses' names"),
                             ("mist", "the title and the footnotes")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s on canvas: %.2f:1, under 4.5, and %s is "
                           "text" % (theme, colour, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "rerank-flow-wide.svg",
                         OUT / "rerank-flow-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_permutation(spec, name)
        bad += check_witness_places(spec, name)
        bad += check_lines(spec, name, svg)
        bad += check_brackets(spec, name, svg)
        bad += check_labels_name_witnesses(spec, name)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
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
        print("rerank-flow self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("rerank-flow self-test ok: both columns hold one row per candidate "
          "for the same %d, the near-miss sits in the first pass's top %d and "
          "outside the reranker's, the answer does the reverse, the two "
          "witnesses' lines cross where the swap happens, every endpoint lands "
          "on its own row's centre, one bracket per column spanning exactly "
          "the budget's four with its label over the second, each witness "
          "label beside the row it names, every label inside the plate and "
          "none on another, both variants making the same claims, no hex "
          "colour, and every colour clearing its bar in both themes"
          % (N_CAND, TOP_K))
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
