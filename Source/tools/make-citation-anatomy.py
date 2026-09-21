#!/usr/bin/env python3
"""Generate the library's second figure: a citation, and a sentence shaped like one.

    python Source/tools/make-citation-anatomy.py [--self-test]

Writes Source/figures/citation-anatomy-wide.svg and citation-anatomy-tall.svg

WHY THIS EXISTS. Four of the library's pages carry a figure and 74 do not, so the
missing ones are chosen by what a drawing can say that a sentence cannot. This
page's own prose ends on the claim: "the fluency is real, only the referent is
missing". That is a shape, not a fact, and it is the shape of the site's whole
subject - an answer that carries its sources against one that only looks like it.

WHAT THE DRAWING ARGUES, in one glance. Two citations, and NOTHING about the two
boxes differs: same height, same three lines, same field positions, the same red
on the one field that matters. That identity is the argument, so it is not left to
care: ROW_GEOMETRY is one dictionary, both rows are drawn from it, and the
self-test parses the emitted SVG and fails if any field's x differs between the
rows. A figure that quietly laid the two out differently would be making the
opposite point, and it would look fine.

The difference is only what each locator CONNECTS to. The real citation's line is
solid and lands on a document. The invented one's is dashed and runs off the
bottom of the frame, which is the same honesty marker the GGUF figure uses for
the tensor band: the drawing refuses to end the thing that is not there. The two
verdicts are the page's own words, not new ones: "found" and "not found".

THE REAL ONE IS REAL. Vaswani et al., "Attention Is All You Need", NeurIPS 30,
5998-6008 is a record that exists and can be opened; a figure arguing that
citations must resolve cannot make its own example up. The second is a
fabrication and the caption says so in as many words - a drawing that blurs the
two is exactly the problem it is about.

TOKENS, NOT COLORS, as the GGUF figure established: every fill and stroke is one
of the library's own variables (--ink, --mist, --hairline, --subtle, --canvas) so
the figure themes with the page, and the single --witness is the locator, in both
rows, because the locator is what the figure is about. The self-test fails the
figure if a hex color appears.

TWO VARIANTS, the same rule as the etymology plate and the GGUF anatomy. A
560-wide drawing in a 272px phone column is a 0.49 scale, which turns a 20-unit
line into 10px; the tall variant is a different composition, not a smaller one -
the box grows, the verdicts move under their connectors, and the type floor holds
at the width it actually ships at.

ACCESSIBILITY. role="img" with an aria-label that states the argument rather than
describing the marks, since a screen reader loses the composition and should not
lose the point.
"""

import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"
FONTS_DISPLAY = "Fraunces, Georgia, serif"

# The text floor discipline: the smallest thing in either variant must survive
# that variant's narrowest real display at >= 11px. Tall ships at 272-342px wide
# (scale 0.80-1.0 of 340), so 14 units is the floor there; wide ships at 1:1 in a
# ~640 column, so 16 is already generous.
FLOOR_WIDE = 16
FLOOR_TALL = 14

# Per-character advance estimates, at font size, for the fit assertions. JetBrains
# Mono is exactly 0.6em; the sans and display numbers are measured against the
# page's own labels the way the GGUF figure's were.
ADV_MONO = 0.60
ADV_SANS = 0.53
ADV_DISPLAY = 0.55

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_HAIR = "var(--hairline)"
TOK_SUBTLE = "var(--subtle)"
TOK_CANVAS = "var(--canvas)"
TOK_WITNESS = "var(--witness)"

# The two records. ROW 1 exists and can be opened; ROW 2 does not, and the caption
# says so. Field by field, so the drawing can place each one.
REAL = {"index": "[1]", "author": "Vaswani et al.", "year": "(2017)",
        "title": "Attention Is All You Need", "venue": "NeurIPS 30",
        "locator": "5998-6008", "verdict": "found"}
# The venue is abbreviated because a citation abbreviates it, and because the same
# string has to fit the narrow variant: the two variants may not show different
# records, so the field widths bend to the text and never the other way round.
INVENTED = {"index": "[2]", "author": "Aldrich & Povey", "year": "(2021)",
            "title": "Retrieval Gates for Local Corpora",
            "venue": "J. Doc. Analysis", "locator": "331-349",
            "verdict": "not found"}

LABEL = ("A real citation on top, an invented one below: the same three lines, the "
         "same fields in the same places. The locator is the only field that can be "
         "checked, and the only thing the drawing lets differ is where it leads.")

# ONE layout for both rows WITHIN a variant: the figure's claim is geometric
# identity, so each row is drawn from this dict and the self-test parses the
# output to confirm no field moved. The two VARIANTS lay out differently, which is
# the etymology plate's rule (a phone gets a different composition, not a smaller
# one) and not a contradiction: one reader sees one of them.
#
# The locator is right-aligned in both rows so the two connectors leave from one
# x, and that alignment is the figure rather than a preference: lines that started
# at different places would suggest the rows differ somewhere.
WIDE = {"w": 560, "h": 452, "row_h": 104, "gap": 104, "top": 6,
        "box_w": 548, "index_x": 22, "author_x": 78, "year_x": 268,
        "line2_x": 78, "line3_x": 78, "locator_right": 534, "pad": 8,
        "line1_dy": 36, "line2_dy": 68, "line2_step": 24, "line3_dy": 94,
        "index_size": 16, "author_size": 21, "year_size": 19, "title_size": 22,
        "venue_size": 16, "locator_size": 16, "verdict_size": 16,
        "drop": 34, "doc_w": 44, "doc_h": 48, "dash": "7 6",
        "wrap": 34, "verdict_side": "left", "connector_inset": 20}

TALL = {"w": 340, "h": 470, "row_h": 144, "gap": 120, "top": 6,
        "box_w": 328, "index_x": 22, "author_x": 74, "year_x": 248,
        "line2_x": 22, "line3_x": 22, "locator_right": 318, "pad": 8,
        "line1_dy": 40, "line2_dy": 74, "line2_step": 24, "line3_dy": 126,
        "index_size": 14, "author_size": 17, "year_size": 15, "title_size": 18,
        "venue_size": 14, "locator_size": 14, "verdict_size": 14,
        "drop": 30, "doc_w": 40, "doc_h": 44, "dash": "6 5",
        "wrap": 24, "verdict_side": "under", "connector_inset": 34}

# The tall row is taller than the wide one, so its connector and document glyph have
# MORE room to cross on the way to the second citation, not less: the gap has to hold
# `drop + doc_h` with clearance over. The first version of the tall variant put the
# glyph inside row 2, which is a layout bug a picture shows and a fit assertion does
# not; check_fits now does.


def title_lines(spec: dict, title: str) -> list:
    """Break a title at spaces to fit the variant's column.

    A real citation runs onto a second line in a narrow column, so the wrap is
    what a citation does rather than a compromise: the alternative is shrinking
    the type under the floor, which is the thing that rule exists to prevent. The
    function is shared with the fit assertion, so what is checked is what is drawn.
    """
    words, lines, cur = title.split(), [], ""
    for word in words:
        candidate = (cur + " " + word).strip()
        if len(candidate) <= spec["wrap"] or not cur:
            cur = candidate
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, fill, size, font, weight=None, anchor=None, extra="") -> str:
    bits = [f'<text x="{x}" y="{y}"']
    if anchor:
        bits.append(f' text-anchor="{anchor}"')
    bits.append(f' font-family="{font}" font-size="{size}" fill="{fill}"')
    if weight:
        bits.append(f' font-weight="{weight}"')
    if extra:
        bits.append(" " + extra)
    bits.append(f">{esc(s)}</text>")
    return "".join(bits)


def narrow(text_s: str, limit: int) -> bool:
    """Would this string pass the fit assertion at the given limit?"""
    return len(text_s) * ADV_SANS * 1.0 <= limit


def check_fits(spec: dict, name: str) -> list:
    """Facts the drawing claims that arithmetic can check."""
    bad = []
    pad = spec["pad"]
    right = 6 + spec["box_w"] - pad          # the usable right edge inside a row
    for which, row in (("real", REAL), ("invented", INVENTED)):
        locator_w = len(row["locator"]) * ADV_MONO * spec["locator_size"]
        fits = (
            ("index", len(row["index"]) * ADV_MONO * spec["index_size"],
             spec["author_x"] - spec["index_x"] - pad),
            ("author", len(row["author"]) * ADV_SANS * spec["author_size"],
             spec["year_x"] - spec["author_x"] - pad),
            ("year", len(row["year"]) * ADV_SANS * spec["year_size"],
             right - spec["year_x"]),
            ("venue", len(row["venue"]) * ADV_MONO * spec["venue_size"],
             (spec["locator_right"] - locator_w) - spec["line3_x"] - pad),
            ("locator", locator_w, spec["locator_right"] - spec["line3_x"]),
        )
        for field, need, have in fits:
            if need > have:
                bad.append(f"{name}: the {which} row's {field} needs {need:.0f} "
                           f"units and the geometry gives it {have:.0f}")
        # The title is measured per LINE, because the wrap is what the drawing
        # does: checking the unwrapped string would fail a figure that fits.
        for line in title_lines(spec, row["title"]):
            need = len(line) * ADV_DISPLAY * spec["title_size"]
            have = right - spec["line2_x"]
            if need > have:
                bad.append(f"{name}: the {which} row's title line {line!r} needs "
                           f"{need:.0f} units and has {have:.0f}")
    if 6 + spec["box_w"] > spec["w"]:
        bad.append(f"{name}: the row box is wider than the drawing")
    if spec["top"] + spec["row_h"] * 2 + spec["gap"] > spec["h"]:
        bad.append(f"{name}: two rows and the gap do not fit the drawing")
    # The connector and the document glyph belong in the gap between the rows, not
    # inside the second one: the two boxes have to stay unambiguous, since reading
    # one citation's evidence into the other would invert the figure.
    clearance = spec["gap"] - spec["drop"] - spec["doc_h"]
    if clearance < 10:
        bad.append(f"{name}: the document ends {clearance} units above the second "
                   "citation, which is close enough to read as part of it - the two "
                   "rows have to stay unambiguous")
    # The verdicts have to fit INSIDE the drawing. The first version put them to
    # the right of the connector, which is the one place the drawing has run out of
    # room: "not found" ended 54 units past the viewBox and was silently clipped,
    # and a clipped label is worse than no label because the figure still looks
    # finished. The wide variant puts them on the open side of the line instead.
    cx = spec["locator_right"] - spec["connector_inset"]
    for row in (REAL, INVENTED):
        w = len(row["verdict"]) * ADV_MONO * spec["verdict_size"]
        if spec["verdict_side"] == "left":
            # Left of the GLYPH, not left of the connector: 12 units from the line
            # put the label's right end inside the document it was labelling.
            start = cx - spec["doc_w"] / 2 - 12 - w
            if start < 6 + spec["pad"]:
                bad.append(f"{name}: the verdict {row['verdict']!r} starts at "
                           f"{start:.0f}, outside the drawing")
        else:
            if cx - w / 2 < 6 + spec["pad"] or cx + w / 2 > 6 + spec["box_w"] - spec["pad"]:
                bad.append(f"{name}: the verdict {row['verdict']!r} centred under the "
                           f"connector at x={cx:g} runs past the row it labels")
    return bad


def check_titles_whole(svg: str, spec: dict, name: str) -> list:
    """A wrapped title must still BE the title, word for word.

    The wrap is the one place where a drawing could lose content quietly: a title
    broken at the wrong boundary ships a truncated reference that reads perfectly,
    and the field is on the page to be checked. So the lines are read back out of
    the output at the title's own column and rejoined, per row.
    """
    bad = []
    halves = svg.split('<rect x="6"')[1:]
    for half, row in zip(halves, (REAL, INVENTED)):
        drawn = re.findall(r'<text x="%s" y="[\d.]+"[^>]*font-family="Fraunces[^"]*"'
                           r'[^>]*>([^<]*)</text>' % spec["line2_x"], half)
        if " ".join(drawn) != row["title"]:
            bad.append(f"{name}: the title drawn in the row is {' '.join(drawn)!r} "
                       f"and the record's is {row['title']!r}")
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


def check_rows_identical(svg: str) -> list:
    """The figure's argument, checked on its own output rather than assumed.

    Every field x in the second row must equal the first row's. This is the claim
    the drawing makes - the box is where a citation's shape stops being evidence -
    and a layout that drifted apart by four units would still look deliberate
    while arguing the opposite. The edit point is the second row's own rect, so the
    halves are compared as SETS of x positions: a wrapped title adds an element at
    an x the other row already uses, and that is the wrap working, not a drift.
    """
    bodies = svg.split('<rect x="6"')
    if len(bodies) != 3:
        return [f"the drawing has {len(bodies) - 1} rows, not two"]
    sets = []
    for half in bodies[1:]:
        sets.append(sorted({float(m) for m in re.findall(r'<text x="([\d.]+)"', half)}))
    if sets[0] != sets[1]:
        only_first = [x for x in sets[0] if x not in sets[1]]
        only_second = [x for x in sets[1] if x not in sets[0]]
        return [f"the two rows do not share one geometry: x={only_first} appears only "
                f"in the first and x={only_second} only in the second, and the "
                "point of the figure is that a citation's shape gives nothing away"]
    if not sets[0]:
        return ["the drawing emitted no fields at all"]
    return []


def verdict_label(spec: dict, cx: float, top: float, doc_h: float, verdict: str) -> str:
    """One placement for both rows' verdicts, and the same one in both branches.

    `top` is where the connector starts and `doc_h` the document's height below it;
    the invented row passes 0 there because it has no document - the label still
    lands at the height the other row's label occupies, so the two verdicts sit level
    and can be read against each other.
    """
    y = top + spec["drop"] + (doc_h or spec["doc_h"]) / 2 + 5
    if spec["verdict_side"] == "under":
        return text(cx, top + spec["drop"] + (doc_h or spec["doc_h"]) + 22, verdict,
                    TOK_MIST, spec["verdict_size"], FONTS_MONO, anchor="middle")
    return text(cx - spec["doc_w"] / 2 - 12, y, verdict, TOK_MIST,
                spec["verdict_size"], FONTS_MONO, anchor="end")


def draw(spec: dict, name: str) -> str:
    """One variant. Both rows are drawn from `spec`, field for field, identically."""
    g = spec
    box_x, box_w = 6, g["box_w"]
    y1 = spec["top"]
    y2 = y1 + spec["row_h"] + spec["gap"]
    parts = []
    for i, row in enumerate((REAL, INVENTED)):
        top = y1 if i == 0 else y2
        real = i == 0
        parts.append(f'<rect x="{box_x}" y="{top}" width="{box_w}" '
                     f'height="{spec["row_h"]}" fill="{TOK_CANVAS}" '
                     f'stroke="{TOK_HAIR}" stroke-width="1"/>')
        parts.append(text(g["index_x"], top + spec["line1_dy"], row["index"],
                          TOK_MIST, spec["index_size"], FONTS_MONO))
        parts.append(text(g["author_x"], top + spec["line1_dy"], row["author"],
                          TOK_INK, spec["author_size"], FONTS_SANS, weight="600"))
        parts.append(text(g["year_x"], top + spec["line1_dy"], row["year"],
                          TOK_MIST, spec["year_size"], FONTS_SANS))
        for k, line in enumerate(title_lines(spec, row["title"])):
            parts.append(text(g["line2_x"], top + spec["line2_dy"] + k * spec["line2_step"],
                              line, TOK_INK, spec["title_size"], FONTS_DISPLAY))
        parts.append(text(g["line3_x"], top + spec["line3_dy"], row["venue"],
                          TOK_MIST, spec["venue_size"], FONTS_MONO))
        # The one red in the figure, on the one field the figure is about, in both
        # rows: the locator is what can be checked, whoever wrote it.
        parts.append(text(g["locator_right"], top + spec["line3_dy"], row["locator"],
                          TOK_WITNESS, spec["locator_size"], FONTS_MONO,
                          weight="600", anchor="end"))

        # The connector. It leaves from the locator's own column, which is why the
        # locator is right-aligned in both rows: the two lines start at one x.
        cx = g["locator_right"] - g["connector_inset"]
        bottom = top + spec["row_h"]
        end = bottom + spec["drop"]
        if real:
            parts.append(f'<line x1="{cx}" y1="{bottom}" x2="{cx}" y2="{end}" '
                         f'stroke="{TOK_INK}" stroke-width="1.5"/>')
            # A document: a page with a folded corner, in the library's own mark
            # language. This is what "found" means, so it is drawn, not labelled.
            # A document, in the page's own mark language: a sheet with a folded
            # corner and three rules of text. The first version drew it in
            # --hairline on --subtle, which is what the boxes are, so the one thing
            # the drawing is FOR arrived as a pale square. It is the payoff of the
            # figure, so it is drawn in ink.
            dx = cx - spec["doc_w"] / 2
            dw, dh = spec["doc_w"], spec["doc_h"]
            fold = dw * 0.36
            parts.append(
                f'<path d="M{dx} {end} h{dw - fold} l{fold} {fold} v{dh - fold} '
                f'h{-dw} z" fill="{TOK_SUBTLE}" stroke="{TOK_INK}" '
                f'stroke-width="1.3"/>')
            parts.append(
                f'<path d="M{dx + dw - fold} {end} v{fold} h{fold}" fill="none" '
                f'stroke="{TOK_INK}" stroke-width="1.3"/>')
            rule_x0, rule_x1 = dx + dw * 0.18, dx + dw * 0.82
            for r in range(3):
                ty = end + dh * 0.42 + r * dh * 0.16
                parts.append(f'<line x1="{rule_x0:.1f}" y1="{ty:.1f}" '
                             f'x2="{rule_x1:.1f}" y2="{ty:.1f}" '
                             f'stroke="{TOK_MIST}" stroke-width="1"/>')
            parts.append(verdict_label(spec, cx, end, dh, row["verdict"]))
        else:
            # Dashed, and it leaves the drawing: the invented citation's line has
            # nothing to arrive at, and an open edge says that without a label.
            parts.append(f'<line x1="{cx}" y1="{bottom}" x2="{cx}" y2="{spec["h"]}" '
                         f'stroke="{TOK_MIST}" stroke-width="1.5" '
                         f'stroke-dasharray="{spec["dash"]}"/>')
            verdict = row["verdict"]
            # The SAME placement as the found row's: a label that moved would be a
            # second difference between the two citations, and this figure exists
            # because there is only one that matters.
            parts.append(verdict_label(spec, cx, bottom, 0, row["verdict"]))
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {spec["w"]} '
            f'{spec["h"]}" width="{spec["w"]}" height="{spec["h"]}" role="img" '
            f'aria-label="{esc(LABEL)}" focusable="false" data-variant="{name}" '
            f'data-generated-by="Source/tools/make-citation-anatomy.py - do not '
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
    """The figure's own colors, held against the tokens it borrows.

    A generated figure cannot judge its own legibility, but it can read the values
    it points at: every text fill here is a library token, so the contrast of that
    token against the fill is arithmetic. The rule is the WCAG one for NORMAL text
    (4.5:1), applied to the shipping scale: the tall variant's 14-unit labels are
    11-14px on the phones that get them, which is not large text, and a figure that
    fails here is unreadable on a phone while looking perfectly fine in a desktop
    screenshot. It is checked against the stylesheet rather than a copy of its
    values, because a copy is the thing that stops agreeing.
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
                        re.findall(r"--(canvas|ink|mist|witness):\s*(#[0-9A-Fa-f]{6})", block)}
    for name, toks in themes.items():
        if "canvas" not in toks:
            bad.append(f"the {name} theme has no --canvas to measure against")
            continue
        for token in ("ink", "mist", "witness"):
            if token not in toks:
                bad.append(f"the {name} theme has no --{token}")
                continue
            ratio = contrast(toks[token], toks["canvas"])
            if ratio < 4.5:
                bad.append(f"--{token} on --canvas is {ratio:.2f}:1 in the {name} "
                           f"theme ({toks[token]} on {toks['canvas']}), under the 4.5 "
                           "normal text needs, and this figure sets every label in "
                           "those two tokens")
    return bad


def write() -> list:
    written = []
    for spec, name in ((WIDE, "wide"), (TALL, "tall")):
        svg = draw(spec, name)
        path = OUT / f"citation-anatomy-{name}.svg"
        path.write_bytes(svg.encode("utf-8"))
        written.append((name, svg, path))
    return written


def self_test() -> int:
    bad = []
    written = write()
    for spec, (name, svg, path) in zip((WIDE, TALL), written):
        bad += check_fits(spec, name)
        bad += check_text_floor(svg, FLOOR_TALL if name == "tall" else FLOOR_WIDE, name)
        bad += check_no_hex(svg, name)
        bad += check_rows_identical(svg)
        bad += check_titles_whole(svg, spec, name)
        # Both variants must carry the same facts, or the phone gets a different
        # claim than the desktop (the GGUF figure's rule, and its reason). The
        # title is checked by check_titles_whole, which can see a wrapped one.
        for row in (REAL, INVENTED):
            for field in ("author", "year", "venue", "locator", "verdict"):
                if esc(row[field]) not in svg:
                    bad.append(f"{name}: the {field} {row[field]!r} is missing, so "
                               "the two variants do not show the same records")
        if not path.is_file():
            bad.append(f"{name}: nothing was written to {path}")
    # Once, not per variant: the tokens are the page's, and both variants draw with
    # the same three of them.
    bad += check_contrast()
    if bad:
        print("citation-anatomy self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("citation-anatomy self-test ok: both rows share one geometry, every field "
          "fits, no hex color, both variants carry the same two records, and the "
          "tokens it draws with clear 4.5:1 in both themes")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    for name, svg, path in write():
        print(f"{path.name}  {len(svg.encode('utf-8')):,} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
