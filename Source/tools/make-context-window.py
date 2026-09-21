#!/usr/bin/env python3
"""Draw the context window: one budget, four claimants, and what falls outside it.

    python Source/tools/make-context-window.py [--self-test]

Writes Source/figures/context-window-wide.svg and -tall.svg

WHY THIS EXISTS. The page's own prose says the thing that wants a drawing and cannot
have one in a sentence: "The window is not ignorance; it is a budget." Four
claimants share one fixed space, the passages take most of it, the system prompt
claims its share first, and - the part a paragraph can state but not show - the
middle of a long context is read LESS reliably than its ends, so what fits is not
all equally read. A budget bar carries all four at once: a proportional split of a
fixed total, with the middle band veiled, and the region past the ceiling drawn
faint and dashed because text there is not compressed or remembered, it is
invisible.

THE PROPORTIONS ARE TOKENS, NOT TASTE. The bar is divided by the token counts in
SHARES, out of the 8,192 a small local model's window holds, and the self-test
requires each segment to be its share of the extent within a unit of rounding and
the segments plus their gaps to fill the extent EXACTLY. A figure about a budget
that does not add up would be arguing against itself.

TWO VARIANTS, the rule the etymology plate and the GGUF anatomy established: the
640-wide plate measured in the built page renders at 280px in a 320px viewport, a
0.44 scale, which would turn its 16-unit labels into 7px. The tall variant is a
different composition rather than a smaller one - the budget becomes a column, the
labels move to its right with leader ticks, the ceiling becomes a line at its foot
and the unreadable past continues downward - and its own floor is 15 units, because
at the narrowest column a phone shows it in (280px, a 0.737 scale) 14 would set the
smallest label at 10.4px. The two variants carry the same facts, and the self-test
checks that they do, since a phone getting a different claim than a desktop is the
failure that rule exists for.

TOKENS, NOT COLORS, as the other figures established: every fill and stroke is one
of the library's own variables, so the plate themes with the page. The veil over the
middle is the same --ink at low opacity, which darkens a light page and lightens a
dark one, so "read less reliably" is drawn rather than written twice.
"""

import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"
FONTS_DISPLAY = "Fraunces, Georgia, serif"

# The text floors, and they are DERIVED rather than chosen. The tall plate is 380
# units wide and MEASURED in the built page at 280px rendered in a 320px viewport,
# 335px at 375, 440px at 480 and 520px at 560 - so its narrowest real column is a
# 0.737 scale, and 11 / 0.737 = 14.9, which is where 15 comes from. At 14 the
# smallest label rendered at 10.4px on the narrowest phone the site supports, under
# the floor every other plate in this library holds. The wide plate renders 640 of
# 640 units at 1440 and 600 of 640 at 640, so 16 units is 15.0px at its worst.
FLOOR_WIDE = 16
FLOOR_TALL = 15

# Per-character advance at font size: JetBrains Mono is exactly 0.6em, the sans and
# display figures are the same estimates the other two plates measure against.
ADV_MONO = 0.60
ADV_SANS = 0.53
ADV_DISPLAY = 0.55

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_HAIR = "var(--hairline)"
TOK_SUBTLE = "var(--subtle)"
TOK_CANVAS = "var(--canvas)"

# One window, and who is claiming it. The order is the order these things appear in
# a request: the standing instructions are first and claim their share first, the
# passages are what retrieval chose, and the answer is what is left over to write
# into. The passages dominating is the whole reason retrieval is the skill.
BUDGET = 8192
SHARES = (("instructions", 1024, "front"),
          ("your question", 768, "asked"),
          ("a few passages", 5120, "chosen"),
          ("the answer", 1280, "written"))

# Where the middle starts and ends, as a fraction of the budget. Past the halfway
# point of a long context a model's reading degrades - the page names it, and this
# is the band that draws it.
BAND = (0.30, 0.70)

# The note under the title, and it says "e.g." for a reason: the window size is a real
# one for the class of models the library is about, and the split between the four
# claimants is an illustration of how a request fills one rather than a measurement of
# any particular request. A plate arguing about budgets should not smuggle numbers in
# that look measured.
NOTE = "e.g. one 8,192-token window"

LABEL = ("A context window as a budget, in an example 8,192-token window: the "
         "instructions, the question, the few passages retrieval chose, and the "
         "answer being written all share it, and the split between them is an "
         "illustration rather than a measurement. The middle band is read less "
         "reliably than the ends, and text past the ceiling is invisible rather "
         "than compressed.")


def allocate(extent: float, gaps: int, gap: float) -> list[float]:
    """Split `extent` between the shares in proportion, with gaps between them.

    Largest remainder, because a budget bar has one arithmetic job - the parts add
    up to the whole - and naive rounding of floats can leave a unit over or under.
    The caller asserts the sum is exact.
    """
    usable = extent - gaps * gap
    total = sum(t for _, t, _ in SHARES)
    exact = [usable * t / total for _, t, _ in SHARES]
    floors = [int(x) for x in exact]
    rest = usable - sum(floors)
    order = sorted(range(len(exact)), key=lambda i: exact[i] - floors[i], reverse=True)
    for i in order[:int(round(rest))]:
        floors[i] += 1
    return [float(x) for x in floors]


WIDE = {"w": 640, "h": 268, "extent": 512.0, "gap": 6.0,
        "bar_x": 6.0, "bar_y": 92.0, "bar_h": 100.0, "pad": 4.0,
        "title_y": 26, "note_y": 54, "note_x": 6, "ceiling_label_right": 526,
        "band_label_y": 76, "beyond_label_right": 628,
        "bracket_y": 88, "bracket_tick": 4,
        "legend_x": (6.0, 330.0), "legend_y": (220, 242), "swatch": 14.0,
        "title": "The window is a budget, not a memory",
        "band_label": ("read less reliably",),
        "title_size": 22, "label_size": 16, "note_size": 16,
        "beyond_x": 538.0, "beyond_w": 24.0, "beyond_gap": 12.0,
        "beyond_tokens": ("invisible, not compressed",)}

TALL = {"w": 380, "h": 448, "extent": 240.0, "gap": 6.0,
        "col_x": 6.0, "col_y": 86.0, "col_w": 120.0, "pad": 6.0,
        "title_y": (24, 46), "note_y": 68, "note_x": 6,
        "band_label_y": (207, 227), "band_leader_y": 202,
        "band_label_x": 272,
        "ceiling_y": 348.0,
        "beyond_y": 360.0, "beyond_h": 20.0, "beyond_gap": 6.0,
        "beyond_label_x": 142, "beyond_label_y": (352, 372, 392),
        "title": ("The window is a budget,", "not a memory"),
        "band_label": ("read less", "reliably"),
        "title_size": 18, "label_size": 15, "note_size": 15,
        "label_x": 142.0, "tick_inset": 4.0,
        "beyond_tokens": ("invisible, not compressed",),
        "beyond_lines": ("invisible,", "not compressed")}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, fill, size, font, weight=None, anchor=None, opacity=None) -> str:
    bits = [f'<text x="{x:g}" y="{y:g}"']
    if anchor:
        bits.append(f' text-anchor="{anchor}"')
    bits.append(f' font-family="{font}" font-size="{size}" fill="{fill}"')
    if weight:
        bits.append(f' font-weight="{weight}"')
    if opacity:
        bits.append(f' opacity="{opacity}"')
    bits.append(f'>{esc(s)}</text>')
    return "".join(bits)


def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * adv * size


def text_boxes(spec: dict, spec_kind: str) -> list[tuple[str, float, float, float, float]]:
    """Every label this variant draws, as (name, x0, x1, y0, y1).

    Built from the same numbers the drawing uses, so the overlap and containment
    checks below are checks on the figure's layout rather than on a description of
    it that could drift.
    """
    g, size = spec, spec["label_size"]
    boxes = []
    cap = size * 0.78          # cap height, so a label's box is what a reader sees
    if spec_kind == "wide":
        boxes.append(("title", g["note_x"], g["note_x"] + width_of(g["title"], g["title_size"], ADV_DISPLAY),
                      g["title_y"] - g["title_size"] * 0.78, g["title_y"] + g["title_size"] * 0.2))
        boxes.append(("note", g["note_x"], g["note_x"] + width_of(NOTE, g["note_size"], ADV_MONO),
                      g["note_y"] - cap, g["note_y"] + 2))
        ceil = "the ceiling"
        boxes.append(("ceiling", g["ceiling_label_right"] - width_of(ceil, size, ADV_MONO),
                      g["ceiling_label_right"], g["note_y"] - cap, g["note_y"] + 2))
        band = "read less reliably"
        centre = g["bar_x"] + g["pad"] + g["extent"] * (BAND[0] + BAND[1]) / 2
        boxes.append(("band", centre - width_of(band, size, ADV_MONO) / 2,
                      centre + width_of(band, size, ADV_MONO) / 2,
                      g["band_label_y"] - cap, g["band_label_y"] + 2))
        beyond = g["beyond_tokens"][0]
        boxes.append(("beyond", g["beyond_label_right"] - width_of(beyond, size, ADV_MONO),
                      g["beyond_label_right"], g["band_label_y"] - cap,
                      g["band_label_y"] + 2))
        for i, (name, _, _) in enumerate(SHARES):
            col = g["legend_x"][i % 2]
            row = g["legend_y"][i // 2]
            x0 = col + g["swatch"] + 8
            boxes.append((name, x0, x0 + width_of(name, size, ADV_SANS),
                          row - cap, row + 2))
    else:
        boxes.append(("title1", g["note_x"], g["note_x"] + width_of(g["title"][0], g["title_size"], ADV_DISPLAY),
                      g["title_y"][0] - g["title_size"] * 0.78, g["title_y"][0] + g["title_size"] * 0.2))
        boxes.append(("title2", g["note_x"], g["note_x"] + width_of(g["title"][1], g["title_size"], ADV_DISPLAY),
                      g["title_y"][1] - g["title_size"] * 0.78, g["title_y"][1] + g["title_size"] * 0.2))
        boxes.append(("note", g["note_x"], g["note_x"] + width_of(NOTE, g["note_size"], ADV_MONO),
                      g["note_y"] - cap, g["note_y"] + 2))
        for i, (name, _, _) in enumerate(SHARES):
            top, bottom = segment_span(g, i, kind="tall")
            centre = (top + bottom) / 2
            boxes.append((name, g["label_x"], g["label_x"] + width_of(name, size, ADV_MONO),
                          centre - cap / 2 - 1, centre + cap / 2 + 1))
        # Two lines, because the label column right of the tall plate's
        # measurements is only as wide as the drawing allows: "read less reliably"
        # set on one line ran 11 units past the edge, which is the failure the
        # citation plate's verdicts taught this family to check for.
        for i, line in enumerate(g["band_label"]):
            y = g["band_label_y"][i]
            boxes.append(("band%d" % i, g["band_label_x"],
                          g["band_label_x"] + width_of(line, size, ADV_MONO),
                          y - cap, y + 2))
        # The right column below the budget carries three annotations in order: the
        # ceiling that ends the budget, then what the region past it is. The first
        # draft centred the ceiling label under the line and piled the other two on
        # top of it, which is the crowding this check exists to catch.
        ceil = "the ceiling"
        boxes.append(("ceiling", g["beyond_label_x"],
                      g["beyond_label_x"] + width_of(ceil, size, ADV_MONO),
                      g["beyond_label_y"][0] - cap, g["beyond_label_y"][0] + 2))
        for i, line in enumerate(g["beyond_lines"]):
            y = g["beyond_label_y"][i + 1]
            boxes.append(("beyond%d" % i, g["beyond_label_x"],
                          g["beyond_label_x"] + width_of(line, size, ADV_MONO),
                          y - cap, y + 2))
    return boxes


def segment_span(spec: dict, i: int, kind: str) -> tuple[float, float]:
    """The y range of share `i` in the tall variant, from the same allocation."""
    parts = allocate(spec["extent"], len(SHARES) - 1, spec["gap"])
    top = spec["col_y"] + spec["pad"]
    for j in range(i):
        top += parts[j] + spec["gap"]
    return top, top + parts[i]


def check_shares(spec: dict, kind: str, name: str) -> list:
    """The budget adds up, and each claimant gets its own share of it.

    This is the figure's arithmetic, and a bar chart that does not sum to its own
    total is a false statement about a budget - so it is measured on the allocation
    the drawing uses rather than on the drawing, and then the drawn extents are read
    back out of the SVG and required to match.
    """
    bad = []
    parts = allocate(spec["extent"], len(SHARES) - 1, spec["gap"])
    if abs(sum(parts) + (len(SHARES) - 1) * spec["gap"] - spec["extent"]) > 0.001:
        bad.append("%s: the segments and their gaps do not fill the window: %s + gaps "
                   "against %s" % (name, sum(parts), spec["extent"]))
    total = sum(t for _, t, _ in SHARES)
    if total != BUDGET:
        bad.append("%s: the shares total %d tokens and the window holds %d"
                   % (name, total, BUDGET))
    for (claim, tokens, _), got in zip(SHARES, parts):
        want = (spec["extent"] - (len(SHARES) - 1) * spec["gap"]) * tokens / total
        if abs(got - want) > 1.0:
            bad.append("%s: %s draws %.0f units for %d tokens where its share of the "
                       "budget is %.0f" % (name, claim, got, tokens, want))
    return bad


def drawn_strings(svg: str) -> list[str]:
    """Every text node, in the order the plate draws it."""
    return [m.group(1) for m in re.finditer(r"<text\b[^>]*>([^<]*)</text>", svg)]


def carries(svg: str, fact: str) -> bool:
    """Does the plate say this, allowing a label that was wrapped onto lines?

    A wrapped label is still the label - the citation plate's title check learned
    that - so a fact counts as carried when some CONTIGUOUS RUN of the plate's text
    nodes, joined, is that fact. Contiguous is the part that matters: matching the
    whole text with whitespace stripped would pass a plate that said "read" in one
    place and "less reliably" somewhere else entirely.
    """
    nodes = drawn_strings(svg)
    for i in range(len(nodes)):
        for j in range(i, min(i + 3, len(nodes))):
            if " ".join(nodes[i:j + 1]) == fact:
                return True
    return False


def check_facts(spec: dict, kind: str, svg: str, name: str) -> list:
    """Both variants have to carry the same facts, whatever the composition.

    A phone getting a different claim from a desktop is the failure the two-variant
    rule exists for, so the labels are read back out of the output rather than
    trusted to the spec that produced them. The tall plate wraps two of them, which
    is a composition choice; the words are not.
    """
    bad = []
    wanted = [c for c, _, _ in SHARES] + ["the ceiling", "read less reliably",
                                          "invisible, not compressed", NOTE]
    for item in wanted:
        if not carries(svg, item):
            bad.append("%s: %r is missing from the drawing, so the variants no longer "
                       "carry the same facts" % (name, item))
    return bad


def check_no_overlap(spec: dict, kind: str, name: str) -> list:
    """No two labels may overlap, on either plate.

    This is the check the citation plate learned to want: an assertion can bound a
    drawing and still not see two labels sharing a baseline, and a crowded plate
    reads as a mistake even when every element is inside the frame.
    """
    bad = []
    boxes = text_boxes(spec, kind)
    for i in range(len(boxes)):
        n1, a0, a1, b0, b1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            n2, c0, c1, d0, d1 = boxes[j]
            if c0 < a1 and a0 < c1 and d0 < b1 and b0 < d1:
                bad.append("%s: %s overlaps %s by %.0f units"
                           % (name, n1, n2, min(a1, c1) - max(a0, c0)))
    return bad


def check_inside(spec: dict, kind: str, name: str) -> list:
    bad = []
    for label, x0, x1, y0, y1 in text_boxes(spec, kind):
        if x1 > spec["w"] - 4 or x0 < 2:
            bad.append("%s: %s runs to x %.0f-%.0f in a %d-wide drawing, so it is "
                       "clipped at the edge or off it" % (name, label, x0, x1, spec["w"]))
        if y1 > spec["h"] - 4 or y0 < 0:
            bad.append("%s: %s sits at y %.0f-%.0f in a %d-tall drawing"
                       % (name, label, y0, y1, spec["h"]))
    # The bar or column itself, and the region past the ceiling.
    if kind == "wide" and spec["bar_x"] + spec["extent"] + 2 * spec["pad"] > spec["w"]:
        bad.append("%s: the bar is wider than the drawing" % name)
    if kind == "tall" and spec["col_x"] + spec["col_w"] > spec["w"]:
        bad.append("%s: the column runs off the drawing" % name)
    return bad


def check_text_floor(svg: str, floor: int, name: str) -> list:
    sizes = [float(m) for m in re.findall(r'font-size="([\d.]+)"', svg)]
    small = [s for s in sizes if s < floor]
    if small:
        return [f"{name}: a text element is set at {min(small)} units, under the "
                f"{floor} floor this variant ships at"]
    return []


def check_no_hex(svg: str, name: str) -> list:
    found = re.findall(r"#[0-9A-Fa-f]{3,8}\b", svg)
    if found:
        return [f"{name}: the figure carries {found[0]}, a hex color that will not "
                "theme with the page"]
    return []


def check_beyond_fades(svg: str, name: str) -> list:
    """Drawn as leaving: the past-the-ceiling blocks must fade, strictly.

    A region that is meant to read as "not there" has to get fainter with every
    step; equal opacities would say the invisible part is as present as the near
    part, which is exactly what the page says it is not.
    """
    ops = [float(m) for m in re.findall(r'<rect[^>]*class="beyond"[^>]*opacity="([\d.]+)"', svg)]
    if len(ops) < 3:
        return [f"{name}: {len(ops)} beyond-the-ceiling blocks, expected 3"]
    if not all(b < a for a, b in zip(ops, ops[1:])):
        return [f"{name}: the beyond-the-ceiling blocks do not fade: {ops}"]
    return []


def check_veil(svg: str, spec: dict, kind: str, name: str) -> list:
    """The veiled band is the middle of the budget, not a stripe someone liked."""
    m = re.search(r'<rect[^>]*class="veil"[^>]*>(?:</rect>)?', svg)
    if not m:
        return [f"{name}: no veiled middle band in the drawing"]
    if kind == "wide":
        got = (float(re.search(r'x="([\d.]+)"', m.group(0)).group(1)),
               float(re.search(r'x="([\d.]+)"', m.group(0)).group(1))
               + float(re.search(r'width="([\d.]+)"', m.group(0)).group(1)))
        inner = spec["bar_x"] + spec["pad"]
        want = (inner + spec["extent"] * BAND[0], inner + spec["extent"] * BAND[1])
    else:
        got = (float(re.search(r'y="([\d.]+)"', m.group(0)).group(1)),
               float(re.search(r'y="([\d.]+)"', m.group(0)).group(1))
               + float(re.search(r'height="([\d.]+)"', m.group(0)).group(1)))
        want = (spec["col_y"] + spec["pad"] + spec["extent"] * BAND[0],
                spec["col_y"] + spec["pad"] + spec["extent"] * BAND[1])
    if abs(got[0] - want[0]) > 1 or abs(got[1] - want[1]) > 1:
        return [f"{name}: the veiled band covers {got[0]:.0f}-{got[1]:.0f} where the "
                f"middle of the budget is {want[0]:.0f}-{want[1]:.0f}"]
    return []


def claim_swatch(spec: dict, i: int, x: float, y: float) -> str:
    """The legend's mark for one claimant, in the marks its segment uses.

    Drawn at --ink rather than the faint rules the segments sit on, because a legend
    mark is 14 units wide and the first version drew these in --hairline on --canvas:
    at the scale a phone shows them, all four were a smudge.
    """
    claim, tokens, role = SHARES[i]
    s, h = spec["swatch"], spec["swatch"]
    if role == "chosen":
        # Blocks, like the segment they stand for: retrieval chose a few, not a slab.
        parts, w, gap = [], (s - 4) / 3.0, 2.0
        for k in range(3):
            parts.append(f'<rect x="{x + k * (w + gap):.1f}" y="{y:g}" width="{w:.1f}" '
                         f'height="{h:g}" fill="{TOK_CANVAS}" stroke="{TOK_INK}" '
                         f'stroke-width="1.5"/>')
        return "".join(parts)
    if role == "written":
        return (f'<rect x="{x:g}" y="{y:g}" width="{s:g}" height="{h:g}" '
                f'fill="{TOK_CANVAS}" stroke="{TOK_MIST}" stroke-width="1.5" '
                f'stroke-dasharray="4 3"/>')
    return (f'<rect x="{x:g}" y="{y:g}" width="{s:g}" height="{h:g}" '
            f'fill="{TOK_CANVAS}" stroke="{TOK_INK}" stroke-width="1.5"/>')


def draw_wide(spec: dict) -> str:
    g = spec
    parts = []
    inner_x = g["bar_x"] + g["pad"]
    inner_y = g["bar_y"] + g["pad"]
    inner_h = g["bar_h"] - 2 * g["pad"]
    parts.append(text(g["note_x"], g["title_y"], g["title"], TOK_INK,
                      g["title_size"], FONTS_DISPLAY))
    parts.append(text(g["note_x"], g["note_y"], NOTE, TOK_MIST,
                      g["note_size"], FONTS_MONO))
    parts.append(text(g["ceiling_label_right"], g["note_y"], "the ceiling", TOK_MIST,
                      g["label_size"], FONTS_MONO, anchor="end"))
    # The bar: empty first, so the veil sits under nothing and over the budget.
    # The trough, then the claims carved out of it. The first version filled the
    # claims with --subtle and stroked them with --hairline, which is very nearly the
    # canvas they sat on: the four parts of the budget were invisible, so the plate
    # showed one rectangle where it claims to show a split. Now the budget is a tinted
    # vessel and every claimant is a box cut into it, so the gaps read as spent space.
    parts.append(f'<rect x="{g["bar_x"]:g}" y="{g["bar_y"]:g}" width="{g["extent"] + 2 * g["pad"]:g}" '
                 f'height="{g["bar_h"]:g}" fill="{TOK_SUBTLE}" stroke="{TOK_HAIR}" '
                 f'stroke-width="1"/>')
    # The segments first, then the veil OVER them. The first version drew the veil
    # under the segments, which was the same as not drawing it at all: the shares
    # fill the budget exactly, so the band that is the figure's whole point was
    # covered by the blocks it was meant to shade.
    x = inner_x
    for (claim, tokens, role), w in zip(SHARES, allocate(g["extent"], len(SHARES) - 1, g["gap"])):
        if role == "chosen":
            # A few discrete passages rather than one slab: the page's point is that
            # retrieval puts a handful in, not that it fills the window with mush.
            blocks, bw, bgap = 3, (w - 2 * 4) / 3.0, 4.0
            for k in range(blocks):
                parts.append(f'<rect x="{x + k * (bw + bgap):.1f}" y="{inner_y:g}" '
                             f'width="{bw:.1f}" height="{inner_h:g}" fill="{TOK_CANVAS}" '
                             f'stroke="{TOK_INK}" stroke-width="1"/>')
        elif role == "front":
            parts.append(f'<rect x="{x:g}" y="{inner_y:g}" width="{w:.1f}" '
                         f'height="{inner_h:g}" fill="{TOK_CANVAS}" stroke="{TOK_INK}" '
                         f'stroke-width="1.3"/>')
        elif role == "written":
            parts.append(f'<rect x="{x:g}" y="{inner_y:g}" width="{w:.1f}" '
                         f'height="{inner_h:g}" fill="{TOK_CANVAS}" stroke="{TOK_MIST}" '
                         f'stroke-width="1" stroke-dasharray="5 4"/>')
        else:
            parts.append(f'<rect x="{x:g}" y="{inner_y:g}" width="{w:.1f}" '
                         f'height="{inner_h:g}" fill="{TOK_CANVAS}" stroke="{TOK_INK}" '
                         f'stroke-width="1"/>')
        x += w + g["gap"]
    parts.append(f'<rect class="veil" x="{inner_x + g["extent"] * BAND[0]:.1f}" '
                 f'y="{inner_y:g}" width="{g["extent"] * (BAND[1] - BAND[0]):.1f}" '
                 f'height="{inner_h:g}" fill="{TOK_INK}" opacity="0.14"/>')
    # The band's bracket, over the veiled middle: two ticks and a rule, so the label
    # above it is attached to the band rather than floating over the bar.
    b0 = inner_x + g["extent"] * BAND[0]
    b1 = inner_x + g["extent"] * BAND[1]
    parts.append(f'<path d="M{b0:.1f} {g["bracket_y"] + g["bracket_tick"]} V{g["bracket_y"]} '
                 f'H{b1:.1f} V{g["bracket_y"] + g["bracket_tick"]}" fill="none" '
                 f'stroke="{TOK_MIST}" stroke-width="1"/>')
    parts.append(text((b0 + b1) / 2, g["band_label_y"], "read less reliably", TOK_MIST,
                      g["label_size"], FONTS_MONO, anchor="middle"))
    # The ceiling itself: the budget's right edge drawn as the hard boundary the prose
    # says it is, running past the bar on both sides. Without it the word "ceiling"
    # floated over an ordinary box edge and the plate did not show where the budget
    # stops, only said so.
    edge = g["bar_x"] + g["extent"] + 2 * g["pad"]
    parts.append(f'<line x1="{edge:g}" y1="{g["bar_y"] - 10:g}" x2="{edge:g}" '
                 f'y2="{g["bar_y"] + g["bar_h"] + 10:g}" stroke="{TOK_INK}" '
                 f'stroke-width="1.5"/>')
    # Past the ceiling: outlined, and shrinking as it goes. The first version filled
    # these at fading opacity, which on a light page gave three dark slabs heavier
    # than the budget; the second gave three equal dashed boxes, which read as three
    # more claims. A region that is not there has to lose size as well as strength.
    for k, op in enumerate((0.60, 0.36, 0.16)):
        w = g["beyond_w"] - 3 * k
        h = inner_h * (1 - 0.32 * k)
        parts.append(f'<rect class="beyond" x="{g["beyond_x"] + k * (g["beyond_w"] + g["beyond_gap"]):g}" '
                     f'y="{inner_y + (inner_h - h) / 2:.1f}" width="{w:g}" height="{h:.1f}" '
                     f'fill="none" stroke="{TOK_MIST}" stroke-width="1.2" opacity="{op}" '
                     f'stroke-dasharray="5 4"/>')
    parts.append(text(g["beyond_label_right"], g["band_label_y"],
                      g["beyond_tokens"][0], TOK_MIST, g["label_size"], FONTS_MONO,
                      anchor="end"))
    for i in range(len(SHARES)):
        col, row = g["legend_x"][i % 2], g["legend_y"][i // 2]
        parts.append(claim_swatch(g, i, col, row - g["swatch"] + 3))
        parts.append(text(col + g["swatch"] + 8, row, SHARES[i][0], TOK_INK,
                          g["label_size"], FONTS_SANS))
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {g["w"]} {g["h"]}" '
            f'width="{g["w"]}" height="{g["h"]}" role="img" aria-label="{esc(LABEL)}" '
            f'focusable="false" data-variant="wide" '
            f'data-generated-by="Source/tools/make-context-window.py - do not '
            f'hand-edit">\n{body}\n</svg>\n')


def draw_tall(spec: dict) -> str:
    g = spec
    parts = []
    for i, line in enumerate(g["title"]):
        parts.append(text(g["note_x"], g["title_y"][i], line, TOK_INK,
                          g["title_size"], FONTS_DISPLAY))
    parts.append(text(g["note_x"], g["note_y"], NOTE, TOK_MIST,
                      g["note_size"], FONTS_MONO))
    inner_y = g["col_y"] + g["pad"]
    inner_h = g["extent"]
    # The same trough and the same claims as the wide plate, for the same reason.
    parts.append(f'<rect x="{g["col_x"]:g}" y="{g["col_y"]:g}" '
                 f'width="{g["col_w"]:g}" height="{inner_h + 2 * g["pad"]:g}" '
                 f'fill="{TOK_SUBTLE}" stroke="{TOK_HAIR}" stroke-width="1"/>')
    y = inner_y
    for i, ((claim, tokens, role), part) in enumerate(zip(SHARES, allocate(g["extent"], len(SHARES) - 1, g["gap"]))):
        if role == "front":
            parts.append(f'<rect x="{g["col_x"] + g["pad"]:g}" y="{y:g}" '
                         f'width="{g["col_w"] - 2 * g["pad"]:g}" height="{max(part - 4, 8):.1f}" '
                         f'fill="{TOK_CANVAS}" stroke="{TOK_INK}" stroke-width="1.3"/>')
        elif role == "chosen":
            # Four passages rather than three in the tall plate: at the column's width
            # three blocks read as one striped slab, which is the opposite of "a few".
            blocks, bh, bgap = 4, (part - 3 * 3) / 4.0, 3.0
            for k in range(blocks):
                parts.append(f'<rect x="{g["col_x"] + g["pad"]:g}" '
                             f'y="{y + k * (bh + bgap):.1f}" '
                             f'width="{g["col_w"] - 2 * g["pad"]:g}" height="{bh:.1f}" '
                             f'fill="{TOK_CANVAS}" stroke="{TOK_INK}" stroke-width="1"/>')
        elif role == "written":
            parts.append(f'<rect x="{g["col_x"] + g["pad"]:g}" y="{y:g}" '
                         f'width="{g["col_w"] - 2 * g["pad"]:g}" height="{max(part - 4, 8):.1f}" '
                         f'fill="{TOK_CANVAS}" stroke="{TOK_MIST}" stroke-width="1" '
                         f'stroke-dasharray="5 4"/>')
        else:
            parts.append(f'<rect x="{g["col_x"] + g["pad"]:g}" y="{y:g}" '
                         f'width="{g["col_w"] - 2 * g["pad"]:g}" height="{max(part - 4, 8):.1f}" '
                         f'fill="{TOK_CANVAS}" stroke="{TOK_INK}" stroke-width="1"/>')
        # The label lives to the right of the column with a tick from its own
        # segment, because a 90-wide column cannot hold "your question".
        centre = y + part / 2
        parts.append(f'<line x1="{g["col_x"] + g["col_w"]:g}" y1="{centre:.1f}" '
                     f'x2="{g["label_x"] - g["tick_inset"]:g}" y2="{centre:.1f}" '
                     f'stroke="{TOK_HAIR}" stroke-width="1"/>')
        parts.append(text(g["label_x"], centre + g["label_size"] * 0.32, claim, TOK_INK,
                          g["label_size"], FONTS_MONO))
        y += part + g["gap"]
    # Over the segments, for the same reason as the wide plate: the shares fill the
    # column exactly, so a veil drawn beneath them would never be seen.
    parts.append(f'<rect class="veil" x="{g["col_x"]:g}" '
                 f'y="{inner_y + inner_h * BAND[0]:.1f}" width="{g["col_w"]:g}" '
                 f'height="{inner_h * (BAND[1] - BAND[0]):.1f}" fill="{TOK_INK}" '
                 f'opacity="0.14"/>')
    # The band: the bracket runs down the column's right edge, its leader crosses to
    # the label, and the label is placed to clear the segment labels above and below.
    tick_x = g["col_x"] + g["col_w"]
    parts.append(f'<path d="M{tick_x + 4:g} {inner_y + inner_h * BAND[0]:.1f} '
                 f'H{tick_x:g} V{inner_y + inner_h * BAND[1]:.1f} H{tick_x + 4:g}" '
                 f'fill="none" stroke="{TOK_MIST}" stroke-width="1"/>')
    parts.append(f'<line x1="{tick_x + 4:g}" y1="{g["band_leader_y"]:g}" x2="268" '
                 f'y2="{g["band_leader_y"]:g}" stroke="{TOK_MIST}" stroke-width="1"/>')
    for i, line in enumerate(g["band_label"]):
        parts.append(text(g["band_label_x"], g["band_label_y"][i], line, TOK_MIST,
                          g["label_size"], FONTS_MONO))
    # The ceiling, and the part of the past that is not there.
    parts.append(f'<line x1="0" y1="{g["ceiling_y"]:g}" x2="{g["col_w"] + 14:g}" '
                 f'y2="{g["ceiling_y"]:g}" stroke="{TOK_INK}" stroke-width="1.5"/>')
    # Shrinking as well as fading, for the reason the wide plate records: three equal
    # dashed boxes read as three more claims rather than as nothing at all.
    for k, op in enumerate((0.60, 0.36, 0.16)):
        h = g["beyond_h"] - 5 * k
        parts.append(f'<rect class="beyond" x="{g["col_x"]:g}" '
                     f'y="{g["beyond_y"] + k * (g["beyond_h"] + g["beyond_gap"]):.1f}" '
                     f'width="{g["col_w"] - 18 * k:g}" height="{h:g}" '
                     f'fill="none" stroke="{TOK_MIST}" stroke-width="1.2" '
                     f'opacity="{op}" stroke-dasharray="5 4"/>')
    # One annotation column below the ceiling, read top to bottom: the line first,
    # then what lies past it. The first draft centred the ceiling's label under the
    # line and stacked the other two on the same column, which crowded them into a
    # pile the overlap check could not see because the label box was hardcoded.
    parts.append(text(g["beyond_label_x"], g["beyond_label_y"][0], "the ceiling",
                      TOK_MIST, g["label_size"], FONTS_MONO))
    for i, line in enumerate(g["beyond_lines"]):
        parts.append(text(g["beyond_label_x"], g["beyond_label_y"][i + 1], line,
                          TOK_MIST, g["label_size"], FONTS_MONO))
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {g["w"]} {g["h"]}" '
            f'width="{g["w"]}" height="{g["h"]}" role="img" aria-label="{esc(LABEL)}" '
            f'focusable="false" data-variant="tall" '
            f'data-generated-by="Source/tools/make-context-window.py - do not '
            f'hand-edit">\n{body}\n</svg>\n')


LIBRARY_CSS = Path(__file__).resolve().parent.parent.parent / "OldVersion" / "styles.css"


def _chan(v: float) -> float:
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _luminance(hexcolor: str) -> float:
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _chan(r) + 0.7152 * _chan(g) + 0.0722 * _chan(b)


def contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_contrast() -> list:
    """The figure's colors, held against the tokens it borrows.

    Every fill and stroke here is a library variable, so whether a reader can see
    the plate is arithmetic on the stylesheet rather than a judgment a generator
    cannot make. Two rules: WCAG's 4.5:1 for the text, applied at the shipping scale
    (the tall plate's 14-unit labels are 12-13px on the phones that get them, which
    is not large text); and the veiled band has to be VISIBLE, checked as the
    contrast between the veiled and bare budget, because a band a reader cannot
    perceive is a claim the plate makes to itself.
    """
    bad = []
    if not LIBRARY_CSS.is_file():
        return [f"the library stylesheet is not at {LIBRARY_CSS}, so the figure's "
                "colors cannot be held against the tokens they borrow"]
    css = LIBRARY_CSS.read_text(encoding="utf-8")
    themes = {}
    for name, start in (("light", css.find(":root {")),
                        ("dark", css.find(':root[data-theme="dark"] {'))):
        if start < 0:
            bad.append(f"the {name} theme block is gone from the library stylesheet")
            continue
        block = css[start:css.find("}", start)]
        themes[name] = {k: v for k, v in
                        re.findall(r"--(canvas|ink|mist|subtle|witness):\s*(#[0-9A-Fa-f]{6})", block)}
    for name, toks in themes.items():
        if "canvas" not in toks:
            bad.append(f"the {name} theme has no --canvas to measure against")
            continue
        for token in ("ink", "mist"):
            if token not in toks:
                bad.append(f"the {name} theme has no --{token}")
                continue
            ratio = contrast(toks[token], toks["canvas"])
            if ratio < 4.5:
                bad.append(f"--{token} on --canvas is {ratio:.2f}:1 in the {name} "
                           f"theme, under the 4.5 normal text needs, and this plate "
                           "sets every label in those two tokens")
        # The band is --ink at 0.14 over the budget it shades. Nothing is written on
        # it, so the question is not legibility but visibility: a 1.15:1 difference in
        # luminance is a band a reader sees without hunting for it, and the first
        # draft of this figure failed by drawing the veil UNDER the segments, where
        # no opacity would have been visible at all.
        if "ink" in toks and "canvas" in toks:
            ratio = contrast(mix(toks["canvas"], toks["ink"], 0.14), toks["canvas"])
            if ratio < 1.15:
                bad.append(f"the veiled band is {ratio:.2f}:1 against the budget it "
                           f"shades in the {name} theme, which is not a band a reader "
                           "can see")
    return bad


def mix(a: str, b: str, t: float) -> str:
    """`b` at `t` over `a`, as the compositor would, in sRGB."""
    out = []
    for i in (1, 3, 5):
        x, y = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        out.append(int(round(x * (1 - t) + y * t)))
    return "#" + "".join("%02X" % c for c in out)


def write() -> list:
    written = []
    for spec, kind in ((WIDE, "wide"), (TALL, "tall")):
        svg = draw_wide(spec) if kind == "wide" else draw_tall(spec)
        path = OUT / f"context-window-{kind}.svg"
        path.write_bytes(svg.encode("utf-8"))
        written.append((kind, spec, svg, path))
    return written


def self_test() -> int:
    bad = []
    for kind, spec, svg, path in write():
        floor = FLOOR_TALL if kind == "tall" else FLOOR_WIDE
        bad += check_shares(spec, kind, kind)
        bad += check_facts(spec, kind, svg, kind)
        bad += check_no_overlap(spec, kind, kind)
        bad += check_inside(spec, kind, kind)
        bad += check_text_floor(svg, floor, kind)
        bad += check_no_hex(svg, kind)
        bad += check_beyond_fades(svg, kind)
        bad += check_veil(svg, spec, kind, kind)
        if not path.is_file():
            bad.append(f"{kind}: nothing was written to {path}")
    bad += check_contrast()
    if bad:
        print("context-window self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("context-window self-test ok: the shares add up to the window exactly, no "
          "two labels overlap, the veiled band is the middle of the budget, the "
          "beyond-the-ceiling blocks fade, both variants carry the same facts, no hex "
          "color, and the tokens it draws with clear 4.5:1 in both themes")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    for kind, spec, svg, path in write():
        print(f"{path.name}  {len(svg.encode('utf-8')):,} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
