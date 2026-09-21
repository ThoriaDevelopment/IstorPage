#!/usr/bin/env python3
"""Draw the page's own claim about attention: it is a weighting, not a recording.

    python Source/tools/make-attention-profile.py [--self-test]

Writes Source/figures/attention-profile-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues in geometry and shows nothing: "its attention is not
uniform across that text: in very long inputs, the start and the middle get less
reliable attention than the end", and the fix is retrieval, which places "only the
handful that bear on it... in front of the model, where attention is sharpest". Both
sentences are shapes. The first is a weight profile over the document - not equal, low
in the middle, strongest at the end. The second is the same profile over a window
short enough that every passage sits in the strong zone. A reader who sees the two
strips one above the other has the whole page: the detail was in the window both
times; what changed is the weight it gets.

THE SHAPE IS THE ARGUMENT, NOT A MEASUREMENT. No model's attention is drawn here, and
both the plate and the caption say so. What is not illustrative is the RELATION the
page asserts, and that is what the self-test holds: the end bar is the maximum of its
panel, the middle third holds the trough, and the early detail's bar sits below a
third of the end's weight in the whole-document window and above four fifths of the
best in the retrieval window. The percentages printed under the bands are computed
from the same weights that draw the bars, and the check reads them back off the
drawing, so the plate cannot print a number its bars do not show.

THE TWO BANDS SHARE ONE BAR PITCH, and the retrieval band is left-aligned rather than
centred, because the point is that its window is literally shorter: four of the same
twenty-four slots filled. A centred band would be prettier and would say something
else - that retrieval is a different kind of thing, when it is the same document read
less.

PLANNED, THEN DRAWN, like every plate here: every string is placed by plan() before
any of it is rendered, so "does a label sit inside the plate" and "does any label sit
on another" are questions about data rather than arithmetic buried in text calls.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the drawing
themes with the page, and no hex value appears in it. The witness marks the one
passage the reader is following, in both bands, because "the same detail, read
better" is the argument and the reader should be able to follow one bar across the
plate and watch it rise.
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

TITLE = "one document, two ways to read it"

# The document, cut into passages - the count a long report actually yields after
# chunking, and the count is what makes "the whole document" concrete. The window
# below it is the handful the page's own prose names.
N_DOC = 24
N_WINDOW = 4

# Where the detail the reader is following sits: an early chapter's passage, which is
# the page's own failure case ("filling an early chapter's detail with a confident
# guess"). In the retrieval window it is the second passage - retrieved passages are
# ordered by bearing, not by position in the source.
DETAIL_DOC = 2
DETAIL_WIN = 1

# The weight profile over a whole-document window, drawn through named anchors rather
# than a formula, because the anchors ARE the page's claims and each one is checkable:
# a start that is merely middling, the detail - an early chapter's passage - under a
# third of the end, a trough that is the global minimum sitting in the middle third
# ("the middle of the text tends to be read least reliably"), and the end strongest,
# because it sits nearest the answer being written. Linear between anchors; the shape
# is an argument a reader can check, not a curve nobody can ask questions of.
ANCHORS = {0: 0.46, 2: 0.31, 9: 0.29, 16: 0.42, 23: 1.0}

# The retrieval window's weights: every passage is one the question bears on, so every
# one sits where attention is sharp. Still a window, so still not flat - the end is
# strongest here too - but the floor is the whole point: nothing in this band is
# effectively unread.
WEIGHTS_WIN = (0.84, 0.90, 0.87, 0.92)


NOTES = ("The shape is the argument, not a measurement",
         "of any one model; the counts are the bars.")


def weight_doc(i: int, n: int = N_DOC) -> float:
    """The weight passage i gets when the whole document is in the window: linear
    between the anchors, which are the page's claims in numbers."""
    at = sorted(ANCHORS)
    if i <= at[0]:
        return ANCHORS[at[0]]
    if i >= at[-1]:
        return ANCHORS[at[-1]]
    for a, b in zip(at, at[1:]):
        if a <= i <= b:
            f = (i - a) / (b - a)
            return ANCHORS[a] + f * (ANCHORS[b] - ANCHORS[a])
    return ANCHORS[at[-1]]


def weights(kind: str) -> tuple:
    return WEIGHTS_WIN if kind == "window" else \
        tuple(weight_doc(i) for i in range(N_DOC))



def pct_of(kind: str, at: int, of: str) -> int:
    """The printed number: the detail's weight as a percent of a panel's own best.

    "Of the end" in the document band, where the end is the best; "of this window's
    best" in the retrieval band, where the same sentence has to stay true however the
    weights are tuned."""
    ws = weights(kind)
    best = ws[-1] if of == "end" else max(ws)
    return round(100 * ws[at] / best)


PANELS = (("document", "the whole document, one window", "of the end's weight"),
          ("window", "the handful that bear on the question", "of this window's best"))

LINE_DOC = "the early detail: %d%% of the end's weight"
LINE_WIN = "the same detail: %d%% of this window's best"
LINE_DOC %= pct_of("document", DETAIL_DOC, "end")
LINE_WIN %= pct_of("window", DETAIL_WIN, "best")

WITNESS_LABEL = "the early detail"

# The text floors, DERIVED like every plate here: the tall plate is 380 units wide and
# renders at 280px in a 320px viewport, a 0.737 scale, so 15 units lands at 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

# Two lines, set by the narrow plate: at 15 units the tall variant has room for 42
# characters a line.
FACTS = ((TITLE, "the title"), (WITNESS_LABEL, "the detail's label"),
         (LINE_DOC, "the document band's number"),
         (LINE_WIN, "the window band's number")) + \
        tuple((note, "a footnote line") for note in NOTES) + \
        tuple((label, "a panel label") for _k, label, _s in PANELS) + \
        (("24", "the document's passage count"), ("4", "the window's passage count"))


WIDE = {
    "w": 640, "h": 384, "name": "wide",
    "x0": 24.0, "band": 546.0,
    "title_y": 30.0, "first_label_y": 64.0, "panel_step": 150.0,
    "band_h": 56.0, "label": 16.0, "foot": 16.0,
    "foot_y": 356.0, "foot_step": 19.0,
    "count_beside": True,
}

TALL = {
    "w": 380, "h": 380, "name": "tall",
    "x0": 22.0, "band": 336.0,
    "title_y": 26.0, "first_label_y": 56.0, "panel_step": 148.0,
    "band_h": 58.0, "label": 15.0, "foot": 15.0,
    "foot_y": 352.0, "foot_step": 18.0,
    "count_beside": False,
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * size * adv


def bar_pitch(spec: dict) -> tuple:
    """The bar width and gap for one panel's band, from the count it holds."""
    def pitch(n: int, gap: float) -> tuple:
        return (spec["band"] - (n - 1) * gap) / n, gap
    return pitch(N_DOC, 2.2), pitch(N_WINDOW, 6.0)


def panel_y(spec: dict, i: int) -> tuple:
    label_y = spec["first_label_y"] + i * spec["panel_step"]
    return label_y, label_y + 14


def band_x(spec: dict, kind: str, i: int) -> tuple:
    """The bar's left and right edges. The window band shares the document's pitch
    and starts at the same margin, so four filled slots read as four of the same
    twenty-four rather than as a second, different chart."""
    (bw_doc, gap_doc), (_bw2, _g2) = bar_pitch(spec)
    if kind == "document":
        bw, gap = bw_doc, gap_doc
    else:
        bw, gap = bw_doc, gap_doc
    x = spec["x0"] + i * (bw + gap)
    return x, x + bw


def detail_x(spec: dict, kind: str) -> float:
    i = DETAIL_DOC if kind == "document" else DETAIL_WIN
    a, b = band_x(spec, kind, i)
    return (a + b) / 2


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font, colour,
    anchor). Drawing reads this and the checks read this, so neither can drift."""
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["label"], FONTS_SANS,
            MIST, "start")]
    for i, (kind, label, _suffix) in enumerate(PANELS):
        label_y, _band_y = panel_y(spec, i)
        out.append(("%s-label" % kind, label, spec["x0"], label_y, spec["label"],
                    FONTS_SANS, INK, "start"))
        count = str(N_WINDOW if kind == "window" else N_DOC)
        cx = (spec["x0"] + spec["band"] + 22 if spec["count_beside"]
              else spec["x0"] + spec["band"])
        out.append(("%s-count" % kind, count, cx, label_y, spec["label"],
                    FONTS_MONO, INK, "end" if not spec["count_beside"] else "start"))
        # The detail's label sits under its own bar, in the witness colour, so the
        # reader can follow one passage across both bands. Anchored at the band's
        # left margin rather than centred on the bar: a 17-character label centred on
        # one narrow bar runs off the plate's left edge on the tall variant, the same
        # defect token-rows' brace label taught.
        dx = spec["x0"] if kind == "document" else spec["x0"]
        out.append(("%s-detail" % kind, WITNESS_LABEL, dx,
                    _band_y + spec["band_h"] + spec["label"] + 6, spec["label"],
                    FONTS_SANS, WITNESS, "start"))
        # The band's number: the weight the detail gets here, as a percent of the
        # band's own best. Computed from the same weights that drew the bars.
        line = LINE_DOC if kind == "document" else LINE_WIN
        out.append(("%s-line" % kind, line, spec["x0"],
                    _band_y + spec["band_h"] + spec["label"] + 6 + spec["label"] + 8,
                    spec["label"], FONTS_SANS, MIST, "start"))
    for j, note in enumerate(NOTES):
        out.append(("note%d" % j, note, spec["x0"],
                    spec["foot_y"] + j * spec["foot_step"], spec["foot"], FONTS_SANS,
                    MIST, "start"))
    return out


def boxes(spec: dict) -> list:
    """The placed labels as rectangles, so the checks can ask what a reader sees."""
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


def draw_band(spec: dict, kind: str, y: float) -> str:
    """One panel: its wash, its bars - one per passage in the window - and the detail's
    bar in the witness colour. The bar geometry is exposed to the checks as data, so
    the checks read the drawing's own arithmetic rather than parsing it back."""
    out = ['<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
           % (spec["x0"], y, spec["band"], spec["band_h"], SUBTLE)]
    ws = weights(kind)
    detail = DETAIL_DOC if kind == "document" else DETAIL_WIN
    for i, w in enumerate(ws):
        a, b = band_x(spec, kind, i)
        h = w * spec["band_h"]
        fill = WITNESS if i == detail else MIST
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                   % (a, y + spec["band_h"] - h, b - a, h, fill))
    return "".join(out)


def bar_heights(spec: dict, kind: str) -> list:
    """The drawn bar heights, in passage order, read back from the band's own string.
    The detail's bar is in the witness colour and is read with them."""
    band = draw_band(spec, kind, 0)
    bars = re.findall(r'<rect x="([0-9.]+)" y="[0-9.]+" width="[0-9.]+" '
                      r'height="([0-9.]+)" fill="(?:%s|%s)"/>'
                      % (re.escape(MIST), re.escape(WITNESS)), band)
    return [float(h) for _x, h in sorted(bars, key=lambda p: float(p[0]))]


def draw(spec: dict) -> str:
    ws_doc = weights("document")
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" '
           'height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("Attention across a %d-passage window: the early detail gets %d%% "
                  "of the weight the end gets. A retrieval window of %d passages "
                  "reads the same detail at %d%% of its best."
                  % (N_DOC, pct_of("document", DETAIL_DOC, "end"), N_WINDOW,
                     pct_of("window", DETAIL_WIN, "best"))),
              spec["name"])]
    for i, (kind, _label, _suffix) in enumerate(PANELS):
        _label_y, band_y = panel_y(spec, i)
        out.append(draw_band(spec, kind, band_y))
    for name, s, x, y, size, font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if name.endswith(("-detail", "-count"))
                            else None,
                            anchor=None if anchor == "start" else anchor))
    out.append("</svg>")
    return "".join(out)


def write(out: Path = OUT) -> list:
    """Both variants, drawn and written, into `out`.

    THE DIRECTORY IS A PARAMETER AND THE SELF-TEST USES ANOTHER ONE, for the reason
    token-rows.py records: the claims here are proved by doctoring this file, and a
    doctored run must not be able to leave a doctored plate in Source/figures/.
    """
    written = []
    for spec in (WIDE, TALL):
        svg = draw(spec)
        path = out / ("attention-profile-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def check_counts(spec: dict, name: str, svg: str) -> list:
    """The bands hold one bar per passage they claim, witness bar included."""
    bad = []
    for kind in ("document", "window"):
        n = N_DOC if kind == "document" else N_WINDOW
        bars = re.findall(r'<rect x="[0-9.]+" y="[0-9.]+" width="[0-9.]+" '
                          r'height="[0-9.]+" fill="(?:%s|%s)"/>'
                          % (re.escape(MIST), re.escape(WITNESS)),
                          draw_band(spec, kind, 0))
        if len(bars) != n:
            bad.append("%s: %s draws %d bars for %d passages"
                       % (name, kind, len(bars), n))
    return bad


def check_shape(spec: dict, name: str) -> list:
    """The relations the page asserts, measured on the drawn heights.

    The bars are the profile. Reading them back rather than the weights they came
    from is what makes this a check on the drawing rather than on the arithmetic that
    drew it: a bar drawn at the wrong height fails here even though the weights are
    untouched."""
    bad = []
    for kind in ("document", "window"):
        heights = bar_heights(spec, kind)
        n = N_DOC if kind == "document" else N_WINDOW
        if len(heights) != n:
            bad.append("%s: %s: %d bar heights read back for %d passages"
                       % (name, kind, len(heights), n))
            continue
        detail_i = DETAIL_DOC if kind == "document" else DETAIL_WIN
        if kind == "document":
            # the end is the maximum, the trough is in the middle third, and the
            # detail - an early chapter's passage - sits under a third of the end
            if max(range(n), key=lambda i: heights[i]) != n - 1:
                bad.append("%s: the end is not the strongest passage in the document "
                           "band, and that is the page's own sentence" % name)
            mid = heights[n // 3:2 * n // 3]
            if min(heights) not in mid:
                bad.append("%s: the trough is not in the middle third of the document "
                           "band" % name)
            if heights[detail_i] > heights[n - 1] / 3:
                bad.append("%s: the early detail's bar is %.0f%% of the end's, and the "
                           "plate's number says it is under a third"
                           % (name, 100 * heights[detail_i] / heights[n - 1]))
        else:
            # every passage in the window sits where attention is sharp: nothing
            # below four fifths of the band's best, and the detail above what the
            # whole-document window gave it
            if min(heights) < 0.8 * max(heights):
                bad.append("%s: a passage in the retrieval window sits at %.0f%% of "
                           "the band's best, under the four fifths that makes "
                           "'where attention is sharpest' true"
                           % (name, 100 * min(heights) / max(heights)))
            doc_h = bar_heights(spec, "document")
            if len(doc_h) == N_DOC and \
                    heights[detail_i] * spec["band_h"] <= doc_h[DETAIL_DOC]:
                bad.append("%s: the same detail reads no better in the retrieval "
                           "window than in the whole document, which argues against "
                           "the page" % name)
    return bad


def check_witness(spec: dict, name: str, svg: str) -> list:
    """One witness bar per band, at the passage the label names, and the label
    anchored at the band margin, where the label was placed."""
    bad = []
    for kind, detail_i in (("document", DETAIL_DOC), ("window", DETAIL_WIN)):
        band = draw_band(spec, kind, 0)
        wit = re.findall(r'<rect x="([0-9.]+)" y="[0-9.]+" width="[0-9.]+" '
                         r'height="[0-9.]+" fill="%s"/>' % re.escape(WITNESS), band)
        if len(wit) != 1:
            bad.append("%s: %s marks %d bars in the witness colour, and the reader "
                       "follows exactly one" % (name, kind, len(wit)))
            continue
        a, b = band_x(spec, kind, detail_i)
        x = float(wit[0])
        if not a - 0.01 <= x <= b + 0.01:
            bad.append("%s: the witness bar sits at x=%g and %s's detail is at %g"
                       % (name, x, kind, a))
    for entry in plan(spec):
        if entry[0].endswith("-detail"):
            if abs(entry[2] - spec["x0"]) > 0.01:
                bad.append("%s: the detail's label was moved from the band margin "
                           "without moving its anchor rule" % name)
    return bad


def check_numbers(spec: dict, name: str, svg: str) -> list:
    """The printed percentages are the drawn bars', computed from the same weights."""
    bad = []
    want = {"document": pct_of("document", DETAIL_DOC, "end"),
            "window": pct_of("window", DETAIL_WIN, "best")}
    for kind, n in want.items():
        line = LINE_DOC if kind == "document" else LINE_WIN
        m = re.search(r"(\d+)%", line)
        if not m or int(m.group(1)) != n:
            bad.append("%s: %s's printed line says %s and its weights say %d%%"
                       % (name, kind, m.group(1) if m else "nothing", n))
    return bad


def check_inside(spec: dict, name: str) -> list:
    """Every label sits inside the plate, horizontally AND vertically. The vertical
    half is not decoration: a plate whose last panel's labels run past the bottom
    edge is clipped in every renderer, and a horizontal-only check passes it."""
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
        return ["%s: the smallest text is %g units, under the %g floor this variant "
                "ships at" % (name, min(sizes), floor)]
    return []


def check_no_hex(svg: str, name: str) -> list:
    if re.search(r"#[0-9A-Fa-f]{3,6}\b", svg):
        return ["%s: a literal hex color is in the drawing, so it will not theme"
                % name]
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
    """Every colour this plate draws in, against the grounds it draws it on.

    The bars carry the plate's meaning, so they are held to the 3:1 a graphic needs;
    every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "the bars, a graphic carrying meaning"),):
            for ground in ("canvas", "subtle"):
                ratio = contrast(t[colour], t[ground])
                if ratio < 3.0:
                    bad.append("%s theme, %s on %s: %.2f:1, under 3:1, and %s"
                               % (theme, colour, ground, ratio, what))
        for colour, what in (("ink", "the labels and counts"),
                             ("witness", "the detail's bar and its label"),
                             ("mist", "the band's number line and the footnotes")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s on canvas: %.2f:1, under 4.5, and %s is text"
                           % (theme, colour, ratio, what))
    return bad


def check_bar_style(svg: str, name: str) -> list:
    """The bars are fills of the library's variables, and the wash is the only other
    filled rect."""
    bad = []
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {SUBTLE, MIST, WITNESS, INK}:
        bad.append("%s: the plate fills with %s, and only the library's own tokens "
                   "may appear" % (name, sorted(fills)))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "attention-profile-wide.svg",
                         OUT / "attention-profile-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_counts(spec, name, svg)
        bad += check_shape(spec, name)
        bad += check_witness(spec, name, svg)
        bad += check_numbers(spec, name, svg)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
        bad += check_text_floor(svg, floor, name)
        bad += check_no_hex(svg, name)
        bad += check_bar_style(svg, name)
        if not path.is_file():
            bad.append("%s: nothing was written to %s" % (name, path))
    scratch.cleanup()
    for path, was in shipped.items():
        now = path.read_bytes() if path.is_file() else None
        if now != was:
            bad.append("the self-test changed %s, so proving the plate can fail is a "
                       "way to ship the plate that failed" % path.name)
    if len(rendered) == 2:
        for fact, what in FACTS:
            if fact and fact in rendered["wide"] and fact not in rendered["tall"]:
                bad.append("the variants disagree: %r (%s) is in the wide plate and "
                           "not the tall one" % (fact, what or "fact"))
    bad += check_contrast()
    if bad:
        print("attention-profile self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("attention-profile self-test ok: the bands hold %d and %d bars for the "
          "passages they claim, the end is the document band's maximum with the "
          "trough in its middle third, the early detail sits under a third of the "
          "end's weight there and above four fifths of the retrieval window's best, "
          "the printed percentages are the drawn bars' own, one witness bar per band "
          "with its label centred on it, every label sits inside the plate and none "
          "sits on another, both variants make the same claims, no hex colour, and "
          "every colour clears its bar in both themes" % (N_DOC, N_WINDOW))
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
