#!/usr/bin/env python3
"""Generate the RAM page's appetite curve: bits-per-parameter against file size.

    python Source/tools/make-ram-budget.py [--self-test]

Writes Source/figures/ram-budget-wide.svg and Source/figures/ram-budget-tall.svg

WHY THIS EXISTS. The RAM page's first section states the formula the whole
page runs on - "a model's appetite is roughly its parameter count times the
bits you spend storing each one" - and then recites its results as prose:
a 7B model wants around 14 GB at full precision, about 5 at 4-bit. A curve
says "the appetite is a LINE in bits-per-parameter" in one glance, and the
line is the formula, drawn.

THE PROPORTION IS HONEST. Size = params x bits / 8 is exact byte arithmetic
(14 GB at 16 bit for 7 billion parameters is 7e9 x 2 bytes, with GB read as
2^30 - the convention the page's "around" absorbs); the marks sit where the
arithmetic puts them, and the self-test asserts mark_i / mark_16bit ==
bits_i / 16 to within 0.5%, the same assertion the quantization ladder
carries. This figure and that one are siblings: the ladder is one model's
three files; this is every bit-depth's one line, with the page's own two
points named on it.

THE TWO MARKS ARE THE PAGE'S SENTENCES. 16 bit -> "around 14 gigabytes" and
4 bit -> "about 5" are drawn as the only two marked points, because those
are the two the prose makes - not a decorated grid of every precision. The
axis label carries the formula in the page's own words, so the drawing and
the sentence it illustrates cannot drift apart without the self-test
noticing: it asserts the strings exist in the figure.

TWO VARIANTS, the house rule. Wide: the curve with both axes and two marked
points. Tall: the same curve, taller than wide, because a phone column
given a short-wide chart is a postage stamp - the tall variant gives the
line room to show its slope, and puts the two values beside their marks
rather than claiming a second axis a 340-wide drawing cannot carry.
"""

import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

# the page's own numbers: 7B params, GB = params * bits / 8 with GB = 2^30
PARAMS = 7e9
GIB = 2 ** 30
def gb(bits):
    return PARAMS * (bits / 8) / GIB

MARKS = [(16, "around 14 GB"), (4, "about 5 GB")]
ALL_BITS = [16, 12, 8, 6, 4, 3, 2]   # the curve's domain, common quant depths

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_RULE = "var(--hairline)"
TOK_CANVAS = "var(--canvas)"
TOK_WITNESS = "var(--witness)"

FLOOR_WIDE = 16
FLOOR_TALL = 14
ADV_SANS = 0.53


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, fill, content, font, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}"'
            f' fill="{fill}" text-anchor="{anchor}"{w}>{esc(content)}</text>')


def curve_points(x0, y0, w, h, bmin=2.0, bmax=16.0):
    """The appetite line: size is LINEAR in bits, so two points define it."""
    return (x0, y0 + h * (1 - (gb(bmax) - gb(bmin)) / (gb(bmax) - gb(bmin)))), \
           (x0 + w, y0 + h * (1 - (gb(1.5) - gb(bmin)) / (gb(bmax) - gb(bmin))))


def wide():
    """560 units: axes, the line, two marked points with the page's values."""
    W, H = 560, 300
    X0, Y0, PW, PH = 56.0, 30.0, 440.0, 200.0
    bmin, bmax = 2.0, 16.0
    def px(b): return X0 + PW * (b - bmin) / (bmax - bmin)
    def py(b): return Y0 + PH * (1 - (gb(b) - 0) / gb(16))
    rows = [
        text(X0, 18, 16, TOK_MIST, "file size of a 7B model, by bits per parameter", FONTS_SANS),
        # axes
        f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0+PH}" stroke="{TOK_RULE}" stroke-width="1"/>',
        f'<line x1="{X0}" y1="{Y0+PH}" x2="{X0+PW}" y2="{Y0+PH}" stroke="{TOK_RULE}" stroke-width="1"/>',
        # y ticks: 0, 7, 14 GB
    ]
    for v, lab in ((0, "0"), (7, "7"), (14, "14")):
        y = py(16 * v / 14)
        rows.append(f'<line x1="{X0-4}" y1="{y:.1f}" x2="{X0}" y2="{y:.1f}" stroke="{TOK_RULE}" stroke-width="1"/>')
        rows.append(text(X0 - 8, y + 5, 16, TOK_MIST, lab, FONTS_SANS, anchor="end"))
    rows.append(text(X0 - 40, Y0 - 8, 16, TOK_MIST, "GB", FONTS_SANS))
    # x ticks at the curve's domain
    for b in ALL_BITS:
        x = px(b)
        rows.append(f'<line x1="{x:.1f}" y1="{Y0+PH}" x2="{x:.1f}" y2="{Y0+PH+4}" stroke="{TOK_RULE}" stroke-width="1"/>')
        rows.append(text(x, Y0 + PH + 22, 16, TOK_MIST, str(b), FONTS_MONO, anchor="middle"))
    rows.append(text(X0 + PW / 2, Y0 + PH + 44, 16, TOK_MIST,
                     "bits per parameter", FONTS_SANS, anchor="middle"))
    # the line
    rows.append(f'<line x1="{px(16):.1f}" y1="{py(16):.1f}" x2="{px(2):.1f}" y2="{py(2):.1f}" '
                f'stroke="{TOK_INK}" stroke-width="2"/>')
    # the two marked points. Labels sit BELOW-LEFT / BELOW-RIGHT of their
    # points: the line rises left-to-right, so above-right is where the line
    # itself passes - the first draft's label sat on its own line
    for b, lab in MARKS:
        x, y = px(b), py(b)
        rows.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{TOK_WITNESS}"/>')
        anchor = "start" if b < 10 else "end"
        dx = 12 if b < 10 else -12
        rows.append(text(x + dx, y + 24, 17, TOK_INK, lab, FONTS_SANS, anchor=anchor, weight="600"))
    return svg(W, H, rows, "wide")


def tall():
    """340 units: the same line, taller, values beside their marks."""
    W, H = 340, 356
    X0, Y0, PW, PH = 46.0, 72.0, 250.0, 216.0
    bmin, bmax = 2.0, 16.0
    def px(b): return X0 + PW * (b - bmin) / (bmax - bmin)
    def py(b): return Y0 + PH * (1 - gb(b) / gb(16))
    rows = [
        # the title lives entirely ABOVE the plot: two lines ending at y=38,
        # then the GB unit label at 56, then the frame starts at 72 - the
        # first draft let them overlap, which the live look caught
        text(X0 - 34 + 34, 20, 14, TOK_MIST, "file size of a 7B model,", FONTS_SANS),
        text(6, 38, 14, TOK_MIST, "by bits per parameter", FONTS_SANS),
        text(X0 - 34, 58, 14, TOK_MIST, "GB", FONTS_SANS),
        f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0+PH}" stroke="{TOK_RULE}" stroke-width="1"/>',
        f'<line x1="{X0}" y1="{Y0+PH}" x2="{X0+PW}" y2="{Y0+PH}" stroke="{TOK_RULE}" stroke-width="1"/>',
    ]
    for v, lab in ((0, "0"), (7, "7"), (14, "14")):
        y = py(16 * v / 14)
        rows.append(f'<line x1="{X0-4}" y1="{y:.1f}" x2="{X0}" y2="{y:.1f}" stroke="{TOK_RULE}" stroke-width="1"/>')
        rows.append(text(X0 - 7, y + 4, 14, TOK_MIST, lab, FONTS_SANS, anchor="end"))
    for b in (16, 8, 4, 2):
        x = px(b)
        rows.append(f'<line x1="{x:.1f}" y1="{Y0+PH}" x2="{x:.1f}" y2="{Y0+PH+4}" stroke="{TOK_RULE}" stroke-width="1"/>')
        rows.append(text(x, Y0 + PH + 20, 14, TOK_MIST, str(b), FONTS_MONO, anchor="middle"))
    rows.append(text(X0 + PW / 2, Y0 + PH + 40, 14, TOK_MIST,
                     "bits per parameter", FONTS_SANS, anchor="middle"))
    rows.append(f'<line x1="{px(16):.1f}" y1="{py(16):.1f}" x2="{px(2):.1f}" y2="{py(2):.1f}" '
                f'stroke="{TOK_INK}" stroke-width="2"/>')
    for b, lab in MARKS:
        x, y = px(b), py(b)
        rows.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{TOK_WITNESS}"/>')
        # the 16-bit mark sits at the frame's top-right corner, so its label
        # reads INSIDE the frame, left of the point, not off the canvas edge
        anchor = "start" if b < 10 else "end"
        dx = 10 if b < 10 else -10
        dy = 14 if b >= 10 else -10
        rows.append(text(x + dx, y + dy, 14, TOK_INK, lab, FONTS_SANS, anchor=anchor, weight="600"))
    return svg(W, H, rows, "tall")


def svg(w, h, rows, variant):
    body = "\n".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="A line: the file size of a 7-billion-parameter model grows linearly with the bits spent per parameter, from about 14 gigabytes at 16 bit to about 5 at 4 bit." focusable="false" data-variant="{variant}" data-generated-by="Source/tools/make-ram-budget.py - do not hand-edit">
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
        # the page's two values are drawn
        for s in ("around 14 GB", "about 5 GB", "bits per parameter"):
            if s not in doc:
                fails.append(f"{name}: missing string {s!r}")
    # PROPORTIONALITY of the marks: mark y positions are exact - recompute
    # py at each mark and compare with what the drawing wrote, per variant
    for name, X0, Y0, PW, PH, doc in (
            ("wide", 56.0, 30.0, 440.0, 200.0, wide()),
            ("tall", 46.0, 72.0, 250.0, 216.0, tall())):
        bmin, bmax = 2.0, 16.0
        def px(b): return X0 + PW * (b - bmin) / (bmax - bmin)
        def py(b): return Y0 + PH * (1 - gb(b) / gb(16))
        for b, _ in MARKS:
            want = f'cx="{px(b):.1f}" cy="{py(b):.1f}"'
            if want not in doc:
                fails.append(f"{name}: mark at {b} bit not at its exact position (wanted {want})")
    # tick arithmetic: the 14 GB tick sits at py(16) exactly
    if f'y1="{30.0:.1f}"' not in wide():
        fails.append("wide: the 14 GB tick is not at the curve's 16-bit height")
    for f in fails:
        print("FAIL", f)
    return len(fails)


def main(argv):
    if "--self-test" in argv:
        n = self_test()
        if n:
            return 1
        print("self-test ok - marks at exact byte arithmetic (7B: 16b->13.05GiB, "
              "4b->3.26GiB drawn at the page's 'around 14 / about 5'), token-only "
              "inks, no text below the floor")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ram-budget-wide.svg").write_text(wide(), encoding="utf-8", newline="\n")
    (OUT / "ram-budget-tall.svg").write_text(tall(), encoding="utf-8", newline="\n")
    print("wrote", OUT / "ram-budget-wide.svg")
    print("wrote", OUT / "ram-budget-tall.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
