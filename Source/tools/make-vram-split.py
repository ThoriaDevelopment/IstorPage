#!/usr/bin/env python3
"""Draw the page's own decision: one model, one card, two bit-widths.

    python Source/tools/make-vram-split.py [--self-test]

Writes Source/figures/vram-split-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues in arithmetic and shows none: "fewer bits per
weight squeezes a larger model into the same 4 GB" - quantization and VRAM as
"two halves of one decision" - and when the model does not fit, "the layers
that fit go to the GPU, the rest run on the CPU... quality is identical; only
the speed changes, because the split adds a trip through the slower memory on
every token". The plate is that paragraph as one drawing: the same 32-layer
model against the same 4 GB card, twice - at 8 bits, where 16 of the 32 layers
fit and the rest spill to system RAM, and at 4 bits, where the same 32 layers
fit with room left for the conversation. Both memory bars are drawn at one
scale, so a gigabyte is the same width everywhere and nothing is resized to
look better.

THE SPLIT IS A COUNT, NOT A GRADIENT, and the checks read the drawn segments:
16 plus 16 is 32 in the first state, 32 plus nothing in the second; the card's
bar is the same width in both states, because the card did not change; an
8-bit layer is exactly two and a half times the width of a 4-bit one, because
that ratio is what bits per weight means; and the second state's fill is under
nine tenths of the card, which is the headroom the page's tenancy paragraph
needs - the weights are "the biggest tenant, not the only one".

PLANNED, THEN DRAWN, like every plate here: every string is placed by plan()
before any of it is rendered, so "does a label sit inside the plate" and "does
any label sit on another" are questions about data rather than arithmetic
buried in text calls.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the
drawing themes with the page, and no hex value appears in it. The model's
layers are the witness colour in both rows and both states - the model is the
subject everywhere it sits.
"""

import re
import sys
import tempfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

ADV_SANS = 0.53

INK = "var(--ink)"
MIST = "var(--mist)"
SUBTLE = "var(--subtle)"
WITNESS = "var(--witness)"

TITLE = "one model, one card, two bit-widths"

# The model and the card. 32 layers; a layer is 0.25 GB at 8 bits and 0.1 GB
# at 4 bits (the 2.5:1 ratio is 8/3.2, and it is what "fewer bits per weight"
# means in pixels). The card is 4 GB; system RAM in the drawing is 16 GB, and
# BOTH bars are drawn at that one scale.
N_LAYERS = 32
CARD_GB = 4.0
RAM_GB = 16.0
GB_8BIT = 0.25
GB_4BIT = 0.10

PANELS = (("at 8 bits", 16, "16 of 32 layers fit",
           "the rest run on the CPU", "every token pays the trip"),
          ("at 4 bits", 32, "the same 32 layers fit",
           "nothing of the model", "every layer read at full speed"))

NOTES = ("Quality is identical; only the speed changes.",
         "Fewer bits per weight is the other half.")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float) -> float:
    return len(s) * size * ADV_SANS


def gb_px(spec: dict, gb: float) -> float:
    """The one scale: a gigabyte is the same width in every bar."""
    return spec["bar_w"] * gb / RAM_GB


def vram_w(spec: dict) -> float:
    return gb_px(spec, CARD_GB)


def panel_bits(i: int) -> float:
    """The bit-width is a property of the PANEL, not the variant: every plate
    draws both states side by side, because the argument is the same model at
    two widths."""
    return GB_8BIT if i == 0 else GB_4BIT


def fit_count(i: int) -> int:
    """How many layers the card holds in panel i, from the arithmetic and not
    from the panel table: the card's gigabytes over a layer's, floored, and
    never more than the model has - at 4 bits the arithmetic would happily
    fit 40."""
    return min(N_LAYERS, int(CARD_GB / panel_bits(i)))


# The text floors, DERIVED like every plate here: the tall plate is 380 units
# wide and renders at 280px in a 320px viewport, a 0.737 scale, so 15 units
# lands at 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

FACTS = ((TITLE, "the title"),
         ("16 of 32 layers fit", "the first state's count"),
         ("the same 32 layers fit", "the second state's count"),
         ("every token pays the trip", "the first state's speed"),
         ("every layer read at full speed", "the second state's speed")) + \
        tuple((note, "a footnote line") for note in NOTES) + \
        tuple((label, "a panel label") for label, *_ in PANELS) + \
        (("VRAM 4 GB", "the card's label"), ("system RAM 16 GB", "the RAM's label"))

WIDE = {
    "w": 640, "h": 400, "name": "wide",
    "x0": 24.0, "bar_w": 546.0,
    "title_y": 30.0,
    "p1_label": 64.0, "p2_label": 204.0,
    "label": 16.0, "foot": 16.0,
    "foot_y": 368.0, "foot_step": 19.0,
}

TALL = {
    "w": 380, "h": 396, "name": "tall",
    "x0": 22.0, "bar_w": 336.0,
    "title_y": 26.0,
    "p1_label": 58.0, "p2_label": 198.0,
    "label": 15.0, "foot": 15.0,
    "foot_y": 364.0, "foot_step": 18.0,
}

BAR_H = 20.0
ROW_STEP = 44.0


def panel_y(spec: dict, i: int) -> float:
    return spec["p1_label"] if i == 0 else spec["p2_label"]


def vram_row_y(spec: dict, i: int) -> float:
    return panel_y(spec, i) + 28.0


def ram_row_y(spec: dict, i: int) -> float:
    return vram_row_y(spec, i) + ROW_STEP


def speed_y(spec: dict, i: int) -> float:
    return ram_row_y(spec, i) + BAR_H + 26.0


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font,
    colour, anchor). Drawing reads this and the checks read this, so neither
    can drift."""
    out = [("title", TITLE, spec["x0"], spec["title_y"], spec["label"],
            FONTS_SANS, MIST, "start")]
    for i, (label, _n, vram_txt, ram_txt, speed_txt) in enumerate(PANELS):
        py = panel_y(spec, i)
        bits = panel_bits(i)
        n_fit = fit_count(i)
        out.append(("p%d-label" % i, label, spec["x0"], py, spec["label"],
                    FONTS_SANS, INK, "start"))
        out.append(("p%d-vram-row" % i, "VRAM 4 GB", spec["x0"],
                    vram_row_y(spec, i) - 6, spec["foot"], FONTS_SANS, MIST,
                    "start"))
        out.append(("p%d-ram-row" % i, "system RAM 16 GB", spec["x0"],
                    ram_row_y(spec, i) - 6, spec["foot"], FONTS_SANS, MIST,
                    "start"))
        out.append(("p%d-vram-count" % i, vram_txt, spec["x0"] + vram_w(spec) + 10,
                    vram_row_y(spec, i) + BAR_H - 5, spec["foot"], FONTS_SANS,
                    INK, "start"))
        out.append(("p%d-ram-count" % i, ram_txt,
                    spec["x0"] + (gb_px(spec, (N_LAYERS - n_fit) * bits) + 10
                                  if i == 0 else 8.0),
                    ram_row_y(spec, i) + BAR_H - 5, spec["foot"], FONTS_SANS,
                    MIST, "start"))
        out.append(("p%d-speed" % i, speed_txt, spec["x0"], speed_y(spec, i),
                    spec["foot"], FONTS_SANS, MIST, "start"))
    for j, note in enumerate(NOTES):
        out.append(("note%d" % j, note, spec["x0"],
                    spec["foot_y"] + j * spec["foot_step"], spec["foot"],
                    FONTS_SANS, MIST, "start"))
    return out


def boxes(spec: dict) -> list:
    """The placed labels as rectangles, so the checks can ask what a reader
    sees."""
    out = []
    for name, s, x, y, size, _font, _colour, anchor in plan(spec):
        w = width_of(s, size)
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


def draw_bar(spec: dict, y: float, width: float) -> str:
    """The ground a memory's occupancy is read against: SUBTLE, with its own
    outline so an empty bar is still visible."""
    return ('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" '
            'stroke="%s" stroke-width="1"/>'
            % (spec["x0"], y, width, BAR_H, SUBTLE, MIST))


def draw_layers(spec: dict, y: float, count: int, first: int,
                bits: float) -> str:
    """`count` layer segments from layer `first`, at `bits` per weight, at the
    one scale. Each segment carries its layer index as data so the checks can
    read the split back."""
    lw = gb_px(spec, bits)
    # The gap is a fraction of the segment, not a constant: a constant gap
    # would make the drawn 8-bit-to-4-bit width ratio wrong, and that ratio is
    # what "fewer bits per weight" means in pixels.
    gap = 0.07 * lw
    out = []
    for k in range(count):
        x = spec["x0"] + k * lw
        out.append('<rect x="%.2f" y="%g" width="%.2f" height="%g" '
                   'fill="%s" data-layer="%d"/>'
                   % (x, y, lw - gap, BAR_H, WITNESS, first + k))
    return "".join(out)


def draw_panel(spec: dict, i: int) -> str:
    bits = panel_bits(i)
    n_fit = fit_count(i)
    spilled = (N_LAYERS - n_fit) if bits == GB_8BIT else 0
    in_vram = n_fit if bits == GB_8BIT else N_LAYERS
    out = [draw_bar(spec, vram_row_y(spec, i), vram_w(spec)),
           draw_bar(spec, ram_row_y(spec, i), spec["bar_w"])]
    out.append(draw_layers(spec, vram_row_y(spec, i), in_vram, 0, bits))
    if spilled:
        out.append(draw_layers(spec, ram_row_y(spec, i), spilled, n_fit, bits))
    return "".join(out)


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'width="%g" height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("The same 32-layer model against the same 4 GB card, twice. "
                  "At 8 bits, 16 of the 32 layers fit and the rest run on the "
                  "CPU, so every token pays the trip through the slower "
                  "memory. At 4 bits, the same 32 layers fit with room left "
                  "for the conversation."),
              spec["name"])]
    for i in (0, 1):
        out.append(draw_panel(spec, i))
    for name, s, x, y, size, font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if name.endswith("-label") else None,
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
        path = out / ("vram-split-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def drawn_model_rects(spec: dict, y: float) -> list:
    """The model's segments in one row, read back from the drawn rects as
    (x, w, layer-index)."""
    svg = draw(spec)
    out = []
    for x, w, idx in re.findall(
            r'<rect x="([0-9.]+)" y="%g" width="([0-9.]+)" height="%g" '
            r'fill="%s" data-layer="([0-9]+)"/>'
            % (y, BAR_H, re.escape(WITNESS)), svg):
        out.append((float(x), float(w), int(idx)))
    out.sort()
    return out


def check_split(spec: dict, name: str) -> list:
    """The split is the page's arithmetic, read from the drawn segments: at 8
    bits, 16 layers in the card and the other 16 in RAM; at 4 bits, all 32 in
    the card and none in RAM. Both states hold one segment per layer, so a
    layer that moved was not drawn twice."""
    bad = []
    n_fit = fit_count(0)
    vram = drawn_model_rects(spec, vram_row_y(spec, 0))
    if len(vram) != n_fit:
        bad.append("%s: %d segments drawn in the card at 8 bits for the %d its "
                   "gigabytes hold" % (name, len(vram), n_fit))
    ram = drawn_model_rects(spec, ram_row_y(spec, 0))
    if len(ram) != N_LAYERS - n_fit:
        bad.append("%s: %d segments drawn in RAM at 8 bits for the %d that do "
                   "not fit" % (name, len(ram), N_LAYERS - n_fit))
    ids = sorted(i for _x, _w, i in vram + ram)
    if ids != list(range(N_LAYERS)):
        bad.append("%s: the two rows hold %d distinct layers for the %d "
                   "the model has" % (name, len(ids), N_LAYERS))
    vram4 = drawn_model_rects(spec, vram_row_y(spec, 1))
    if len(vram4) != N_LAYERS:
        bad.append("%s: %d segments drawn in the card at 4 bits for the %d "
                   "the model has" % (name, len(vram4), N_LAYERS))
    ram4 = drawn_model_rects(spec, ram_row_y(spec, 1))
    if ram4:
        bad.append("%s: %d segments drawn in RAM at 4 bits, and the "
                   "page's claim is that the model fits"
                   % (name, len(ram4)))
    return bad


def check_scale(spec: dict, name: str) -> list:
    """One scale everywhere: the card's bar is a quarter of the RAM bar's,
    because 4 GB against 16 GB is that ratio, and the card's bar is the same
    width in both states, because the card did not change."""
    bad = []
    svg = draw(spec)
    grounds = [tuple(float(v) for v in m) for m in re.findall(
        r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" height="%g" '
        r'fill="%s" stroke="%s" stroke-width="1"/>'
        % (BAR_H, re.escape(SUBTLE), re.escape(MIST)), svg)]
    vrams = [g for g in grounds if abs(g[2] - vram_w(spec)) < 0.01]
    rams = [g for g in grounds if abs(g[2] - spec["bar_w"]) < 0.01]
    if len(vrams) != 2 or len(rams) != 2:
        bad.append("%s: %d card grounds and %d RAM grounds drawn for the two "
                   "states" % (name, len(vrams), len(rams)))
        return bad
    if abs(vrams[0][2] - vrams[1][2]) > 0.01:
        bad.append("%s: the card's bar changed width between states, and the "
                   "card did not change" % name)
    if abs(rams[0][2] / vrams[0][2] - RAM_GB / CARD_GB) > 0.01:
        bad.append("%s: the two bars are not at one scale - %g GB over %g GB "
                   "is not the drawn ratio" % (name, RAM_GB, CARD_GB))
    return bad


def check_bits_ratio(spec: dict, name: str) -> list:
    """An 8-bit layer is exactly 8/3.2 times the width of a 4-bit one: that
    ratio is what 'fewer bits per weight' means in pixels. Both panels are in
    this plate, so the ratio is read across them - each as a fraction of the
    same card bar, since both states draw on the same bar in one figure."""
    bad = []
    a = drawn_model_rects(spec, vram_row_y(spec, 0))
    b = drawn_model_rects(spec, vram_row_y(spec, 1))
    if not a or not b:
        bad.append("%s: a panel drew no card segments to compare" % name)
        return bad
    if abs((a[0][1] / b[0][1]) - GB_8BIT / GB_4BIT) > 0.01:
        bad.append("%s: the bit-width ratio in drawn pixels is %.3f and %g "
                   "over %g is %.3f" % (name, a[0][1] / b[0][1], GB_8BIT,
                                         GB_4BIT, GB_8BIT / GB_4BIT))
    return bad


def check_headroom(spec: dict, name: str) -> list:
    """At 4 bits the model fills under nine tenths of the card, which is the
    headroom the tenancy paragraph needs - the weights are the biggest tenant,
    not the only one."""
    bad = []
    fill = fit_count(1) * panel_bits(1)
    if not fill <= 0.9 * CARD_GB:
        bad.append("%s: the 4-bit model fills %.1f of %.1f GB, past the nine "
                   "tenths that leaves room for the conversation"
                   % (name, fill, CARD_GB))
    return bad


def check_labels(spec: dict, name: str) -> list:
    """Each panel's label names the bit-width whose arithmetic the panel
    drew: the plate's two states are distinguished by their labels, so a
    swapped or stale label mislabels the whole argument."""
    bad = []
    placed = {n: s for n, s, _x, _y, _sz, _f, _c, _a in plan(spec)}
    for i, (label, _n, _v, _r, _s) in enumerate(PANELS):
        drawn = fit_count(i)
        want = "8 bits" if panel_bits(i) == GB_8BIT else "4 bits"
        if placed["p%d-label" % i] != label:
            bad.append("%s: panel %d draws %s but its placed label text was "
                       "changed away from the panel table" % (name, i, want))
        if want not in label:
            bad.append("%s: panel %d draws the %d-layer split that %g bits per "
                       "weight gives, and its label does not say %s"
                       % (name, i, drawn, panel_bits(i), want))
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
    """No label sits on another, no label sits on a bar it does not describe,
    and no label sits on the model - the segments are the plate's subject."""
    bad = []
    bx = boxes(spec)
    for i, (a, ax0, ax1, ay0, ay1) in enumerate(bx):
        for b, bx0, bx1, by0, by1 in bx[i + 1:]:
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                bad.append("%s: %s sits on %s" % (name, a, b))
    model_rows = [(drawn_model_rects(spec, vram_row_y(spec, 0)), "at 8 bits",
                   vram_row_y(spec, 0)),
                  (drawn_model_rects(spec, ram_row_y(spec, 0)), "at 8 bits",
                   ram_row_y(spec, 0)),
                  (drawn_model_rects(spec, vram_row_y(spec, 1)), "at 4 bits",
                   vram_row_y(spec, 1)),
                  (drawn_model_rects(spec, ram_row_y(spec, 1)), "at 4 bits",
                   ram_row_y(spec, 1))]
    for segs, which, ry in model_rows:
        if not segs:
            continue
        # The model's extent is its drawn segments, not the bar's ground: a
        # count label may sit in the space the split leaves empty - that is
        # what "the rest" means drawn - but never on a segment itself.
        mx0 = min(x for x, _w, _i in segs)
        mx1 = max(x + w for x, w, _i in segs)
        for lname, lx0, lx1, ly0, ly1 in bx:
            if lx0 < mx1 and mx0 < lx1 and ly0 < ry + BAR_H and ry < ly1:
                bad.append("%s: %s sits on the model's segments (%s row)"
                           % (name, lname, which))
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

    The fill set includes INK because text fills too, and this check returns
    what it finds - the first version of this check on another plate returned
    a literal [] and every style defect passed in silence."""
    bad = []
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {INK, MIST, SUBTLE, WITNESS}:
        bad.append("%s: the plate fills with %s, and only the library's own "
                   "tokens may appear" % (name, sorted(fills)))
    strokes = set(re.findall(r'stroke="(var\(--[a-z-]+\))"', svg))
    if strokes != {MIST}:
        bad.append("%s: the plate strokes with %s, and the bars' outline is "
                   "the only stroke an empty memory needs"
                   % (name, sorted(strokes)))
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

    The model's segments carry the plate's meaning, so they are held to the
    3:1 a graphic needs against both grounds; every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "the bars' outline, a graphic"),
                             ("witness", "the model's segments")):
            for ground in ("canvas", "subtle"):
                ratio = contrast(t[colour], t[ground])
                if ratio < 3.0:
                    bad.append("%s theme, %s on %s: %.2f:1, under 3:1, and %s"
                               % (theme, colour, ground, ratio, what))
        for colour, what in (("ink", "the panel labels and counts"),
                             ("mist", "the row labels, speeds and notes")):
            for ground, gname in (("canvas", "canvas"), ("subtle", "the bars' ground")):
                ratio = contrast(t[colour], t[ground])
                if ratio < 4.5:
                    bad.append("%s theme, %s on %s: %.2f:1, under 4.5, and %s "
                               "is text" % (theme, colour, gname, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "vram-split-wide.svg",
                         OUT / "vram-split-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_split(spec, name)
        bad += check_scale(spec, name)
        bad += check_bits_ratio(spec, name)
        bad += check_headroom(spec, name)
        bad += check_labels(spec, name)
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
        print("vram-split self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("vram-split self-test ok: the card holds %d of %d layers at 8 bits "
          "with the other %d in RAM and every layer accounted for once, all "
          "%d at 4 bits with none in RAM, the card's bar the same width in "
          "both states and one scale across both bars, an 8-bit layer exactly "
          "the %g-to-%g ratio of a 4-bit one, the 4-bit fill under nine "
          "tenths of the card, every label inside the plate and none on "
          "another, both variants making the same claims, no hex colour, and "
          "every colour clearing its bar in both themes"
          % (fit_count(0), N_LAYERS, N_LAYERS - fit_count(0), N_LAYERS,
             GB_8BIT, GB_4BIT))
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
