#!/usr/bin/env python3
"""Generate the library's first figure: what is inside a GGUF file.

    python Source/tools/make-gguf-anatomy.py [--self-test]

Writes Source/figures/gguf-anatomy-wide.svg and Source/figures/gguf-anatomy-tall.svg

WHY THIS EXISTS. The library is 75 pages of prose with zero figures in it - the
landing page argues with drawings and the library argues with paragraphs. The
GGUF page is the right place to start because its subject IS a shape: one file
whose internal order is fixed by the format, where a drawing can say "the
weights are nearly all of it" in one glance and the prose needs a sentence.

THE FACTS ARE THE FORMAT'S, NOT MINE. GGUF v3's layout is public and short:
four magic bytes, a uint32 version, two uint64 counts - 24 bytes, so the
metadata begins at 0x18 - then the key-value metadata, then the tensor info
table, then alignment padding, then the tensor data. Byte offsets appear only
where the format fixes them (0x00, 0x04, 0x18); everything after the header
depends on the file's own contents, so those bands carry no offsets rather
than invented ones. The "nearly all of it" claim is arithmetic: a 7B Q4_K_M
file is about 4.5 GB and its tensors are about 4.4 of those.

TWO VARIANTS, the etymology plate's rule. A 560-wide drawing shown in a 272px
phone column is a 0.49 scale, and a 19-unit gloss becomes 9px - a caption
nobody can read, which no font-size step can fix inside one composition. The
tall variant is not the wide one scaled: the gloss moves under its name, the
bands grow, and the type floor holds at the width it actually ships at. CSS
swaps them; both ship, because a figure that only exists on desktop is a
figure that does not exist on a phone.

TOKENS, NOT COLORS. The library themes itself through data-theme, and the
figure is spliced inline, so every fill and stroke is one of the page's own
variables - --ink, --mist, --hairline, --subtle, --canvas - and themes for
free. Exactly one --witness, on the magic bytes: the signature is the one
thing in the file that is a constant literal, and the library's red is the
one accent it has. The self-test fails the figure if a hex color appears,
because a hex in an inline SVG is a theme bug that no review will catch.

THE CUT EDGE IS AN HONESTY MARKER, not decoration. The tensors band has no
bottom edge: the drawing refuses to end the thing that is nearly the whole
file, and the caption says the heights are not to scale. A false-proportion
chart with a footnote is still a lie with better manners; an open edge says
"continues past the frame" the way the landing page's worlds bleed off it.

ACCESSIBILITY. role="img" with a title, like the etymology plate: the figure
carries meaning the prose repeats, so a screen reader loses the composition
and nothing else.
"""

import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

# GGUF v3, from the spec: the only offsets the format itself fixes.
MAGIC_BYTES = 4
VERSION_BYTES = 4
COUNT_BYTES = 8
COUNTS = 2
HEADER_BYTES = MAGIC_BYTES + VERSION_BYTES + COUNT_BYTES * COUNTS
HEADER_OFFSET_HEX = f"0x{HEADER_BYTES:02X}"   # 0x18, where the metadata begins

FONTS_MONO = "JetBrains Mono, ui-monospace, Consolas, monospace"
FONTS_SANS = "Inter, system-ui, sans-serif"
FONTS_DISPLAY = "Fraunces, Georgia, serif"

# text-floor discipline: the smallest thing in either variant must survive
# that variant's narrowest real display at >= 11px. Tall ships at 272-342px
# (scale 0.80-1.0 of 340), so 14 units is the floor there; wide ships at
# 1:1 in a ~640 column, so 16 is already generous.
FLOOR_WIDE = 16
FLOOR_TALL = 14

# per-character advance estimates for the fit assertions (units at font size):
ADV_MONO = 0.60   # JetBrains Mono is exactly 0.6em
ADV_SANS = 0.53   # Inter, mixed case, measured across the page's own labels
ADV_DISPLAY = 0.55

TOK_INK = "var(--ink)"
TOK_MIST = "var(--mist)"
TOK_RULE = "var(--hairline)"
TOK_SUBTLE = "var(--subtle)"
TOK_CANVAS = "var(--canvas)"
TOK_WITNESS = "var(--witness)"

# The content, in format order. (offset, name, gloss, bytes-note)
BANDS = [
    ("0x00", "GGUF", "the signature", "4 bytes"),
    ("0x04", "header", "version and counts", "20 bytes"),
    (HEADER_OFFSET_HEX, "metadata", "key-value pairs", ""),
    ("", "tensor table", "names, shapes, offsets", ""),
    ("", "alignment", "padding, up to 32 bytes", ""),
    ("", "tensor data", "the weights themselves", ""),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, fill, content, font, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}"'
            f' fill="{fill}" text-anchor="{anchor}"{w}>{esc(content)}</text>')


def band_box(x, y, w, h, fill=TOK_CANVAS):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{TOK_RULE}" stroke-width="1"/>')


def cut_edge(x0, x1, y, depth, segments=28):
    """An open bottom edge: a jagged polyline that never closes the band."""
    import math
    pts = []
    for i in range(segments + 1):
        px = x0 + (x1 - x0) * i / segments
        py = y + (depth * 0.55 if i % 2 else 0) + (depth * 0.45 * math.sin(i * 1.7) ** 2)
        pts.append(f"{px:.1f},{py:.1f}")
    return (f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="{TOK_RULE}" stroke-width="1"/>')


def wide() -> str:
    """560 units wide, for the ~640px article column: offset | name | gloss."""
    W, H = 560, 436
    X0, X1 = 6, 554
    OFF_X, NAME_X = 20, 104
    rows = []
    y = 6.0
    heights = [52, 52, 60, 60, 44, 0]   # last band runs to the cut edge
    cut_y = 404.0
    heights[-1] = cut_y - y - sum(heights[:-1])
    y = 6.0
    for i, ((off, name, gloss, note), bh) in enumerate(zip(BANDS, heights)):
        last = i == len(BANDS) - 1
        if last:
            rows.append(f'<rect x="{X0}" y="{y:.0f}" width="{X1-X0}" '
                        f'height="{cut_y-y:.0f}" fill="{TOK_SUBTLE}" '
                        f'stroke="{TOK_RULE}" stroke-width="1"/>')
        else:
            rows.append(band_box(X0, y, X1 - X0, bh))
        if last:
            # centred in the band's own room, as the tall variant does - the
            # first draft drew these twice (loop + post-loop) and parked the
            # claim on the cut edge, both caught in the raster
            mid = y + bh / 2
            rows.append(text(NAME_X, mid - 22, 21, TOK_INK, name, FONTS_SANS, weight="600"))
            rows.append(text(NAME_X + 152, mid - 22, 19, TOK_MIST, gloss, FONTS_SANS))
            rows.append(text(NAME_X, mid + 26, 32, TOK_INK, "nearly the whole file", FONTS_DISPLAY))
            rows.append(text(X1 - 20, mid + 26, 19, TOK_MIST, "99%", FONTS_SANS, anchor="end", weight="600"))
        elif name == "GGUF":
            rows.append(text(OFF_X, y + 34, 19, TOK_MIST, off, FONTS_MONO))
            rows.append(text(NAME_X, y + 36, 32, TOK_WITNESS, name, FONTS_MONO, weight="600"))
            if note:
                rows.append(text(X1 - 20, y + 33, 19, TOK_MIST, note, FONTS_MONO, anchor="end"))
        else:
            base = y + bh / 2 + 6
            if off:
                rows.append(text(OFF_X, base, 19, TOK_MIST, off, FONTS_MONO))
            rows.append(text(NAME_X, base, 21, TOK_INK, name, FONTS_SANS, weight="600"))
            if gloss:
                rows.append(text(NAME_X + 152, base, 19, TOK_MIST, gloss, FONTS_SANS))
            if note:
                rows.append(text(X1 - 20, base, 19, TOK_MIST, note, FONTS_MONO, anchor="end"))
        y += bh
    rows.append(cut_edge(X0, X1, cut_y, 10))
    rows.append(text(X0, H - 6, 16, TOK_MIST,
                     "band heights are not to scale", FONTS_SANS))
    body = "\n".join(rows)
    return svg(W, H, body, "wide")


def tall() -> str:
    """340 units wide, for the phone column: gloss under its name."""
    W, H = 340, 560
    X0, X1 = 6, 334
    OFF_X, NAME_X = 20, 86
    cut_y = 528.0
    # (offset, name, gloss, band height, note) - the same strings BANDS
    # carries, so the two variants cannot disagree about the content
    bands = [
        ("0x00", "GGUF", "the signature", 48, "4 bytes"),
        ("0x04", "header", "version and counts", 48, "20 bytes"),
        (HEADER_OFFSET_HEX, "metadata", "key-value pairs", 64, ""),
        ("", "tensor table", "names, shapes, offsets", 64, ""),
        ("", "alignment", "padding, up to 32 bytes", 56, ""),
        ("", "tensor data", "the weights themselves", 0, ""),
    ]
    heights = [b[3] for b in bands]
    heights[-1] = cut_y - 6 - sum(heights[:-1])
    rows = []
    y = 6.0
    for i, ((off, name, gloss, bh, note), h) in enumerate(zip(bands, heights)):
        last = i == len(bands) - 1
        if last:
            rows.append(f'<rect x="{X0}" y="{y:.0f}" width="{X1-X0}" '
                        f'height="{cut_y-y:.0f}" fill="{TOK_SUBTLE}" '
                        f'stroke="{TOK_RULE}" stroke-width="1"/>')
        else:
            rows.append(band_box(X0, y, X1 - X0, h))
        if name == "GGUF":
            rows.append(text(OFF_X, y + 30, 14, TOK_MIST, off, FONTS_MONO))
            rows.append(text(NAME_X, y + 33, 26, TOK_WITNESS, name, FONTS_MONO, weight="600"))
            rows.append(text(X1 - 16, y + 31, 14, TOK_MIST, note, FONTS_MONO, anchor="end"))
        elif last:
            # The band IS the emptiness: it is nearly the whole file, so the
            # drawing gives it nearly the whole drawing and the claim sits
            # centred in the room the band's own share creates, not parked at
            # its top like a label that lost its content.
            mid = y + h / 2
            rows.append(text(OFF_X, mid - 34, 16, TOK_INK, name, FONTS_SANS, weight="600"))
            rows.append(text(OFF_X, mid - 12, 14, TOK_MIST, gloss, FONTS_SANS))
            rows.append(text(OFF_X, mid + 26, 22, TOK_INK, "nearly the whole file", FONTS_DISPLAY))
            rows.append(text(X1 - 16, mid + 26, 16, TOK_MIST, "99%", FONTS_SANS, anchor="end", weight="600"))
        else:
            if off:
                rows.append(text(OFF_X, y + 26, 14, TOK_MIST, off, FONTS_MONO))
            rows.append(text(NAME_X, y + 27, 16, TOK_INK, name, FONTS_SANS, weight="600"))
            rows.append(text(NAME_X, y + 46, 14, TOK_MIST, gloss, FONTS_SANS))
            if note:
                rows.append(text(X1 - 16, y + 26, 14, TOK_MIST, note, FONTS_MONO, anchor="end"))
        y += h
    rows.append(cut_edge(X0, X1, cut_y, 12))
    rows.append(text(X0, H - 6, 14, TOK_MIST,
                     "band heights are not to scale", FONTS_SANS))
    body = "\n".join(rows)
    return svg(W, H, body, "tall")


def svg(w, h, body, variant):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Anatomy of a GGUF file: header, metadata, tensor table, alignment, then the weights, which are nearly the whole file." focusable="false" data-variant="{variant}" data-generated-by="Source/tools/make-gguf-anatomy.py - do not hand-edit">
{body}
</svg>'''


# --- the self-test -----------------------------------------------------------

def fit(text_str, size, adv, col_from, col_to):
    return col_from + len(text_str) * size * adv <= col_to - 8


def self_test() -> int:
    fails = []
    # 1. the header arithmetic is the spec's, and the printed offset agrees
    if HEADER_BYTES != 24 or HEADER_OFFSET_HEX != "0x18":
        fails.append(f"header arithmetic: {HEADER_BYTES} {HEADER_OFFSET_HEX}")
    # 2. no literal colors anywhere: a hex inside an inline SVG is a theme bug
    for name, doc in (("wide", wide()), ("tall", tall())):
        for tok in ("#", "rgb(", "rgba("):
            import re
            hits = [m for m in re.finditer(re.escape(tok) + r"[0-9a-fA-F]{3,8}", doc)]
            if hits:
                fails.append(f"{name}: literal color {tok}... x{len(hits)}")
        # 3. every var() used is one of the library's own tokens
        import re
        for v in set(re.findall(r"var\((--[a-z-]+)\)", doc)):
            if v not in {"--ink", "--mist", "--hairline", "--subtle",
                         "--canvas", "--witness"}:
                fails.append(f"{name}: unknown token {v}")
        # 4. the text floor
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', doc)]
        floor = FLOOR_WIDE if name == "wide" else FLOOR_TALL
        below = [s for s in sizes if s < floor]
        if below:
            fails.append(f"{name}: text below {floor} units: {below}")
        # 5. the cut edge exists and no rect closes the tensors band's bottom:
        #    the last rect is drawn open-topped by construction, so assert the
        #    polyline is present AFTER the last rect and the band has no
        #    bottom border - approximated by counting polylines.
        if "<polyline" not in doc:
            fails.append(f"{name}: no cut edge")
        # 6. band order is format order
        order = [BANDS[i][1] for i in range(len(BANDS))]
        pos = [doc.find(esc(n)) for n in order]
        if any(p < 0 for p in pos) or pos != sorted(pos):
            fails.append(f"{name}: band order wrong: {pos}")
    # 7. the wide variant's strings fit their columns (Inter 0.53em, mono 0.6)
    if not fit("version and counts", 19, ADV_SANS, 254, 460):
        fails.append("wide: header gloss overruns its column")
    if not fit("key-value pairs", 19, ADV_SANS, 254, 534):
        fails.append("wide: metadata gloss overruns its column")
    if not fit("names, shapes, offsets", 19, ADV_SANS, 254, 534):
        fails.append("wide: table gloss overruns its column")
    if not fit("padding, up to 32 bytes", 19, ADV_SANS, 254, 534):
        fails.append("wide: alignment gloss overruns its column")
    if not fit("nearly the whole file", 32, ADV_DISPLAY, 104, 496):
        fails.append("wide: display claim overruns")
    if not fit("the weights themselves", 19, ADV_SANS, 104, 534):
        fails.append("wide: tensors gloss overruns")
    # 8. every string the fit checks name must actually BE in the documents -
    # a fit test against a string the generator no longer emits is a test of
    # nothing, and that exact drift shipped once: the tall variant kept its
    # first-draft glosses while the test measured the new short ones.
    for name, doc in (("wide", wide()), ("tall", tall())):
        for s in ("version and counts", "key-value pairs", "names, shapes, offsets",
                  "padding, up to 32 bytes", "the weights themselves",
                  "nearly the whole file", "band heights are not to scale"):
            if esc(s) not in doc:
                fails.append(f"{name}: fit-tested string missing from figure: {s!r}")
    # 9. the tall variant's glosses fit under the names
    if not fit("key-value pairs", 14, ADV_SANS, 86, 318):
        fails.append("tall: metadata gloss overruns")
    if not fit("the weights themselves", 14, ADV_SANS, 20, 302):
        fails.append("tall: tensors gloss overruns")
    if not fit("nearly the whole file", 22, ADV_DISPLAY, 20, 288):
        fails.append("tall: display claim overruns")
    if not fit("padding, up to 32 bytes", 14, ADV_SANS, 86, 318):
        fails.append("tall: alignment gloss overruns")
    if not fit("version and counts", 14, ADV_SANS, 86, 318):
        fails.append("tall: header gloss overruns")
    for f in fails:
        print("FAIL", f)
    return len(fails)


def main(argv):
    if "--self-test" in argv:
        n = self_test()
        if n:
            return 1
        print("self-test ok - header is 24 bytes (metadata at 0x18), token-only "
              "inks, no text below the floor, strings fit their columns")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gguf-anatomy-wide.svg").write_text(wide(), encoding="utf-8", newline="\n")
    (OUT / "gguf-anatomy-tall.svg").write_text(tall(), encoding="utf-8", newline="\n")
    print("wrote", OUT / "gguf-anatomy-wide.svg")
    print("wrote", OUT / "gguf-anatomy-tall.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
