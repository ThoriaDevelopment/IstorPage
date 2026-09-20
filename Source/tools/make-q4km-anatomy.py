#!/usr/bin/env python3
"""Generate the Q4_K_M page's name anatomy: the code, decoded in place.

    python Source/tools/make-q4km-anatomy.py [--self-test]

Writes Source/figures/q4km-anatomy-wide.svg and Source/figures/q4km-anatomy-tall.svg

WHY THIS EXISTS. The page's first section reads the code piece by piece -
"Q4_K_M therefore reads as: four bits, K-style block scales, the medium
variant of the two" - and a code read is a POINTING job: the eye needs to
be told which characters carry which meaning.

HOW IT POINTS, and why not with brackets. The first draft drew brackets
from each piece down to three gloss columns, with x positions computed
from a 0.60em mono advance. The raster look caught it three ways: the
pieces overlapped (the rasterizer's fallback mono is not 0.60em - manual
glyph advance math is a bet on a font metric nobody controls), the gloss
columns collided, and the brackets pointed between them. The fix removes
every bet: the code is ONE <text> with tspans, so the renderer spaces it
however its font actually is, and the pointing is done by COLOR - each
piece and the row that decodes it share an ink, Q4 and its row in the
witness red, the rest in the page's ink. A color link survives any font;
a bracket computed from a guessed advance does not.

THE PIECES ARE THE PAGE'S. "four bits per weight", "K-style block
scales", "the medium variant" are the page's own phrases, and the
self-test asserts they appear, in order, with the code pieces - so the
figure cannot quietly teach a different story than the paragraphs.

NO FAKE PROPORTION. Nothing in a NAME has a quantity to draw: no bars,
nothing to scale, pure pointing. The one accent is Q4 - "the main dial on
file size", the piece a reader must take away.

TWO VARIANTS, one composition at two scales: the name is short enough
that both a 560 column and a 340 phone column carry the same code-line-
plus-rows shape, and a figure that is a list should not pretend a phone
needs a different invention - the etymology plate earned its two shapes
because a descent is spatial; a decode is not.
"""

import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_RULE = "var(--hairline)"
TOK_CANVAS = "var(--canvas)"
TOK_WITNESS = "var(--witness)"

FLOOR_WIDE = 16
FLOOR_TALL = 14

# (piece, gloss, note, accent) - glosses are the page's own phrases
PIECES = [
    ("Q4", "four bits per weight", "the main dial on file size", True),
    ("_K_", "K-style block scales", "precision kept where it is needed", False),
    ("M", "the medium variant", "of the two grades", False),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, fill, content, font, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}"'
            f' fill="{fill}" text-anchor="{anchor}"{w}>{esc(content)}</text>')


def code_line(x, y, size, centered=False):
    """The code as ONE text element with tspans - the renderer's own spacing."""
    tspans = "".join(
        f'<tspan fill="{TOK_WITNESS if a else TOK_INK}">{esc(p)}</tspan>'
        for p, g, n, a in PIECES)
    anchor = ' text-anchor="middle"' if centered else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONTS_MONO}" font-size="{size}"'
            f'{anchor} font-weight="600">{tspans}</text>')


def rows(y0, pitch, chip_x, gloss_x, rule_end, name_size, note_size):
    out = []
    for i, (piece, gloss, note, accent) in enumerate(PIECES):
        y = y0 + i * pitch
        color = TOK_WITNESS if accent else TOK_INK
        out.append(f'<line x1="{chip_x}" y1="{y}" x2="{rule_end}" y2="{y}" '
                   f'stroke="{TOK_RULE}" stroke-width="1"/>')
        out.append(text(chip_x, y + name_size + 8, name_size, color, piece,
                        FONTS_MONO, weight="600"))
        out.append(text(gloss_x, y + name_size + 8, name_size, color, gloss, FONTS_SANS, weight="600"))
        out.append(text(gloss_x, y + name_size + 30 + (name_size - 16), note_size,
                        TOK_MIST, note, FONTS_SANS))
    return out


def wide():
    W, H = 560, 402
    return svg(W, H, [
        code_line(280, 76, 60, centered=True),
        text(280, 104, 16, TOK_MIST, "the code on the file, piece by piece",
             FONTS_SANS, anchor="middle"),
        ] + rows(136, 72, 24, 130, 536, 19, 16) + [
        # the page's own reading, closing the figure the way the page's
        # section closes: the pieces assembled back into the sentence
        text(280, 378, 19, TOK_INK,
             "four bits, K-style block scales, the medium variant of the two",
             FONTS_SANS, anchor="middle"),
        ], "wide")


def tall():
    W, H = 340, 386
    return svg(W, H, [
        code_line(170, 62, 42, centered=True),
        text(170, 86, 14, TOK_MIST, "the code, piece by piece", FONTS_SANS, anchor="middle"),
        ] + rows(112, 72, 16, 96, 324, 16, 14) + [
        text(170, 368, 14, TOK_INK,
             "four bits, K-style block scales,", FONTS_SANS, anchor="middle"),
        text(170, 384 - 4, 14, TOK_INK,
             "the medium variant of the two", FONTS_SANS, anchor="middle"),
        ], "tall")


def svg(w, h, rows_, variant):
    body = "\n".join(rows_)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="The code Q4_K_M decoded: Q4 means four bits per weight, the main dial on file size; K means K-style block scales, precision kept where it is needed; M means the medium variant of the two grades." focusable="false" data-variant="{variant}" data-generated-by="Source/tools/make-q4km-anatomy.py - do not hand-edit">
{body}
</svg>'''


def self_test():
    import re
    fails = []
    for name, doc in (("wide", wide()), ("tall", tall())):
        for m in re.finditer(r'(?:fill|stroke)="(#[0-9a-fA-F]{3,8}|rgb)', doc):
            fails.append(f"{name}: literal color {m.group(1)}")
        for v in set(re.findall(r"var\((--[a-z-]+)\)", doc)):
            if v not in {"--ink", "--mist", "--hairline", "--canvas", "--witness"}:
                fails.append(f"{name}: unknown token {v}")
        floor = FLOOR_WIDE if name == "wide" else FLOOR_TALL
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', doc)]
        below = [s for s in sizes if s < floor]
        if below:
            fails.append(f"{name}: text below {floor}: {below}")
        # the page's glosses are present, in order
        pos = [doc.find(esc(g)) for g in ("four bits per weight",
                "K-style block scales", "the medium variant")]
        if any(p < 0 for p in pos) or pos != sorted(pos):
            fails.append(f"{name}: glosses missing or out of order: {pos}")
        # the code is ONE text element whose tspans spell Q4_K_M in order
        m = re.search(r'<text[^>]*font-family="JetBrains[^>]*>(.*?)</text>', doc, re.S)
        if not m or "".join(re.findall(r'<tspan[^>]*>([^<]*)</tspan>', m.group(1))) != "Q4_K_M":
            fails.append(f"{name}: the code line is not one tspan-spelled Q4_K_M")
        # the accent color appears exactly on the Q4 tspan and its row's two
        # texts (chip + gloss) - three, and nowhere else
        if doc.count(f'fill="{TOK_WITNESS}"') != 3:
            fails.append(f"{name}: witness red used {doc.count(TOK_WITNESS)} times, want 3")
    for f in fails:
        print("FAIL", f)
    return len(fails)


def main(argv):
    if "--self-test" in argv:
        n = self_test()
        if n:
            return 1
        print("self-test ok - code spelled by tspans in one text, glosses in "
              "order, accent exactly twice, token-only inks, floors held")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "q4km-anatomy-wide.svg").write_text(wide(), encoding="utf-8", newline="\n")
    (OUT / "q4km-anatomy-tall.svg").write_text(tall(), encoding="utf-8", newline="\n")
    print("wrote", OUT / "q4km-anatomy-wide.svg")
    print("wrote", OUT / "q4km-anatomy-tall.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
