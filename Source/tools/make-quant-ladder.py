#!/usr/bin/env python3
"""Generate the quantization page's ladder: one model, three precisions.

    python Source/tools/make-quant-ladder.py [--self-test]

Writes Source/figures/quant-ladder-wide.svg and Source/figures/quant-ladder-tall.svg

WHY THIS EXISTS. The quantization page's middle section is a chart written as
a paragraph: the same 4-billion-parameter model, 8 GB at full precision,
4 GB at 8-bit, about 2.5 GB at 4-bit. A ladder says "every step down halves
the file" in one glance, and the paragraph it sits with keeps the sentences.

THE BARS ARE HONEST, which is the whole point of this figure. The anatomy
plate's bands are declared not-to-scale because file layout has no natural
length; file SIZE does, so these bars carry their exact proportion and the
self-test asserts it: width_i / width_fp16 == gb_i / gb_fp16 to within
0.5%. A bar chart that lies about its ratios is the one drawing this site's
own captions warn about, so the assertion is arithmetic, not a promise.

THE NUMBERS ARE THE PAGE'S. 8 GB is the page's "roughly 8 GB" for a 4B model
at full precision; ~2.5 GB is the page's own 4-bit figure; 4 GB at Q8 is the
byte arithmetic both imply (8 bits = one byte per parameter, 4 billion
parameters). The tilde travels with the approximations and not with the
exact one, because a tilde is a claim too.

ONE ACCENT. The witness red marks Q4_K_M's row - the rung the whole library
assumes you downloaded, the one the GGUF page calls the file that fits your
memory budget. Everything else is ink, mist and hairline.

TWO VARIANTS, same rule as the anatomy plate: the tall one is not a scaled
wide one. Wide runs label | bits | bar | value; tall stacks each rung as a
label line, a full-width bar under it, and the value carried at the bar's
end, because a 340-wide drawing has no room for four columns.
"""

import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

# (name, bits, gigabytes, approx, note) - the page's own numbers
RUNGS = [
    ("FP16", "16 bit", 8.0, False, "full precision"),
    ("Q8_0", "8 bit", 4.0, False, "one byte per parameter"),
    ("Q4_K_M", "4 bit", 2.5, True, "the rung that fits"),
]
MODEL = "a 4B model"
UNIT = "GB"

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_RULE = "var(--hairline)"
TOK_SUBTLE = "var(--subtle)"
TOK_CANVAS = "var(--canvas)"
TOK_WITNESS = "var(--witness)"

FLOOR_WIDE = 16
FLOOR_TALL = 14
ADV_SANS = 0.53
ADV_MONO = 0.60

INK_OPACITY = 0.22   # the bars: --ink at this opacity on --canvas


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, fill, content, font, anchor="start", weight=None, opacity=None):
    w = f' font-weight="{weight}"' if weight else ""
    o = f' fill-opacity="{opacity}"' if opacity else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}"'
            f' fill="{fill}" text-anchor="{anchor}"{w}{o}>{esc(content)}</text>')


def gb_label(gb, approx):
    return ("~" if approx else "") + (f"{gb:g}")


def wide():
    """560 units: name | bits | bar | value, one row per rung."""
    W, H = 560, 232
    X0 = 6
    NAME_X, BITS_X, BAR_X = 20, 116, 210
    BAR_SPAN = 280.0          # the FP16 bar's length; the scale's 100%
    ROWS_Y = 64.0
    PITCH = 56.0
    BAR_H = 34.0
    rows = [
        text(X0, 34, 16, TOK_MIST, f"{MODEL}, one file per rung", FONTS_SANS),
    ]
    for i, (name, bits, gb, approx, note) in enumerate(RUNGS):
        y = ROWS_Y + i * PITCH
        w = BAR_SPAN * gb / RUNGS[0][2]
        accent = name == "Q4_K_M"
        rows.append(text(NAME_X, y + BAR_H / 2 + 6, 19,
                         TOK_WITNESS if accent else TOK_INK, name, FONTS_MONO,
                         weight="600"))
        rows.append(text(BITS_X, y + BAR_H / 2 + 6, 19, TOK_MIST, bits, FONTS_SANS))
        rows.append(f'<rect x="{BAR_X}" y="{y}" width="{w:.1f}" height="{BAR_H}" '
                    f'fill="{TOK_INK}" fill-opacity="{INK_OPACITY}" '
                    f'stroke="{TOK_RULE}" stroke-width="1"/>')
        vx = BAR_X + w + 14
        rows.append(text(vx, y + BAR_H / 2 + 6, 19,
                         TOK_WITNESS if accent else TOK_INK,
                         gb_label(gb, approx) + " " + UNIT, FONTS_SANS, weight="600"))
    rows.append(text(X0, H - 8, 16, TOK_MIST,
                     "bar lengths are the files’ true proportions", FONTS_SANS))
    return svg(W, H, rows, "wide")


def tall():
    """340 units: each rung is a label line with its bar under it."""
    W, H = 340, 292
    X0 = 6
    BAR_X = 20
    BAR_SPAN = 232.0
    ROWS_Y = 40.0
    PITCH = 82.0
    BAR_H = 30.0
    rows = [
        text(X0, 26, 14, TOK_MIST, f"{MODEL}, one file per rung", FONTS_SANS),
    ]
    for i, (name, bits, gb, approx, note) in enumerate(RUNGS):
        y = ROWS_Y + i * PITCH
        w = BAR_SPAN * gb / RUNGS[0][2]
        accent = name == "Q4_K_M"
        rows.append(text(BAR_X, y + 4, 16,
                         TOK_WITNESS if accent else TOK_INK, name, FONTS_MONO,
                         weight="600"))
        rows.append(text(X1_END if (X1_END := 320) else 320, y + 4, 14, TOK_MIST,
                         bits, FONTS_SANS, anchor="end"))
        rows.append(f'<rect x="{BAR_X}" y="{y + 12}" width="{w:.1f}" height="{BAR_H}" '
                    f'fill="{TOK_INK}" fill-opacity="{INK_OPACITY}" '
                    f'stroke="{TOK_RULE}" stroke-width="1"/>')
        rows.append(text(BAR_X + w + 10, y + 12 + BAR_H / 2 + 5, 16,
                         TOK_WITNESS if accent else TOK_INK,
                         gb_label(gb, approx) + " " + UNIT, FONTS_SANS, weight="600"))
    rows.append(text(X0, H - 8, 14, TOK_MIST,
                     "bar lengths are the files’ true proportions", FONTS_SANS))
    return svg(W, H, rows, "tall")


def svg(w, h, rows, variant):
    body = "\n".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="The same 4-billion-parameter model at three precisions: 8 gigabytes at full precision, 4 at Q8, about 2.5 at Q4. Bar lengths are the true proportions." focusable="false" data-variant="{variant}" data-generated-by="Source/tools/make-quant-ladder.py - do not hand-edit">
{body}
</svg>'''


def self_test():
    import re
    fails = []
    for name, doc in (("wide", wide()), ("tall", tall())):
        # tokens only
        for m in re.finditer(r'(?:fill|stroke)="(#[0-9a-fA-F]{3,8}|rgb)', doc):
            fails.append(f"{name}: literal color {m.group(1)}")
        for v in set(re.findall(r"var\((--[a-z-]+)\)", doc)):
            if v not in {"--ink", "--mist", "--hairline", "--subtle",
                         "--canvas", "--witness"}:
                fails.append(f"{name}: unknown token {v}")
        # text floor
        floor = FLOOR_WIDE if name == "wide" else FLOOR_TALL
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', doc)]
        below = [s for s in sizes if s < floor]
        if below:
            fails.append(f"{name}: text below {floor}: {below}")
        # PROPORTIONALITY: every bar's width over its gigabytes is one constant
        widths = [float(w) for w in
                  re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="[\d.]+"', doc)]
        if len(widths) != 3:
            fails.append(f"{name}: expected 3 bars, drew {len(widths)}")
            continue
        ratios = [w / r[2] for w, r in zip(widths, RUNGS)]
        for r in ratios[1:]:
            if abs(r - ratios[0]) / ratios[0] > 0.005:
                fails.append(f"{name}: bars not proportional: {ratios}")
                break
        # the values the page states are the values drawn
        for s in ("8 GB", "4 GB", "~2.5 GB"):
            if s not in doc:
                fails.append(f"{name}: missing value {s}")
        if "bar lengths are the files’ true proportions" not in doc:
            fails.append(f"{name}: missing the honesty caption")
    # column fits (wide): name at 116, bar starts 210, span 280, value after
    if 116 + len("Q4_K_M") * 19 * ADV_MONO > 210 - 8:
        fails.append("wide: rung name reaches the bits column")
    for rung in RUNGS:
        w = 280.0 * rung[2] / RUNGS[0][2]
        label = gb_label(rung[2], rung[3]) + " " + UNIT
        if 210 + w + 14 + len(label) * 19 * ADV_SANS > 560 - 8:
            fails.append(f"wide: {label!r} overruns the frame at its own bar")
    for f in fails:
        print("FAIL", f)
    return len(fails)


def main(argv):
    if "--self-test" in argv:
        n = self_test()
        if n:
            return 1
        print("self-test ok - bars exactly proportional to 8:4:2.5, token-only "
              "inks, no text below the floor, the page's own values drawn")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "quant-ladder-wide.svg").write_text(wide(), encoding="utf-8", newline="\n")
    (OUT / "quant-ladder-tall.svg").write_text(tall(), encoding="utf-8", newline="\n")
    print("wrote", OUT / "quant-ladder-wide.svg")
    print("wrote", OUT / "quant-ladder-tall.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
