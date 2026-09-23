#!/usr/bin/env python3
"""Generate the mark's gear as a sprite symbol for the page's brand rows.

    python Source/tools/make-win-mark.py [--self-test]

Writes Source/win-mark.partial, spliced by build-site.py into the sprite at
<!--#include win-mark-->. Register the include there and the figure row in
verify-figures.py when you touch this.

WHY THIS EXISTS. The page's five brand rows (the header mark and the four
window bars) carried a text-only wordmark, and a brand mark that is only text
reads unfinished next to the same page's drawn windows, plates and gears. The
mark's gear already exists as the crown every tab carries: the favicon and the
icon are drawn from Assets/brand/istor-gear.svg, whose comment records the
raster-tuned counts (24 teeth at 16px, the pinion at 8) and the honest lie
(the real drive is 223:48). This script does NOT redraw any of that. It reads
the master and lifts its geometry into a <symbol>, the same discipline
make-icon-sprite.py runs for Lucide: one geometry, every slot.

TWO DELIBERATE SUBSTITUTIONS, both recorded here rather than hidden:

  * The master strokes on var(--mark-ink, #171717). The symbol strokes on
    currentColor instead, so the gear re-inks with the row it sits in - the
    nav's over-field state already flips .nav-mark to --field-ink, and the
    gear now follows it with no extra rule. A var() with a fallback would
    freeze the gear to one ink and lie the first time a row changes ground.

  * The master's pinion on var(--mark-accent, #F2726F). The symbol classes it
    (.mark-pinion) and the stylesheet fills it --coral, the palette's token
    for the mark's artwork, lifted to --coral-lift inside the field and poster
    worlds by the same rule that lifts every other mark there. Artwork, not
    text, so the contrast audit's text floor does not apply to it; it is the
    same red the favicon has always spent.

USERS. The header mark and the four window bars: one <svg class="i-mark"> per
row, aria-hidden, ahead of the wordmark text. The close's giant mark is NOT a
user of this symbol; it composes with the horizon by design and is handled in
its own figure.

SELF-TEST. The invariants a doctored copy would break: the symbol is the only
element, strokes are currentColor with no hex anywhere, the tooth and spoke
subpath counts equal the master's, the pinion survives with its class, and the
stroke width is the master's 4.5 (the raster-tuned weight, not a guess).

Standard library only.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
ROOT = HERE.parents[1]
MASTER = ROOT / "Assets" / "brand" / "istor-gear.svg"
OUT = SOURCE / "win-mark.partial"

STROKE_W = "4.5"


def build() -> str:
    master = MASTER.read_text(encoding="utf-8")
    g = re.search(r"<g\b.*?</g>", master, re.S)
    if not g:
        sys.exit("error: the gear master has no <g> block")
    body = g.group(0)

    paths = re.findall(r"<path\b[^>]*d=\"([^\"]+)\"", body)
    circles = re.findall(r"<circle\b([^>]*)/>", body)
    # Three paths: the spokes are drawn twice on the master (once under the
    # teeth, once over), which is how their joints read full-weight where the
    # tooth ring crosses them. The repetition is lifted as-is.
    if len(paths) != 3 or len(circles) != 2:
        sys.exit("error: master shape drift - expected 3 paths and 2 circles, "
                 "found %d and %d" % (len(paths), len(circles)))

    # The wheel circle: r=23 on the master. Stroked currentColor, no fill.
    wheel = [c for c in circles if "fill" not in c]
    pinion = [c for c in circles if "fill" in c]
    if len(wheel) != 1 or len(pinion) != 1:
        sys.exit("error: master circles drifted - expected one stroked wheel "
                 "and one filled pinion")

    pinion_attrs = pinion[0]
    pinion_xy = re.search(r"cx=\"([\d.]+)\" cy=\"([\d.]+)\" r=\"([\d.]+)\"", pinion_attrs)
    if not pinion_xy:
        sys.exit("error: the pinion lost its geometry")

    lines = []
    lines.append('<symbol id="i-mark" viewBox="0 0 64 64" aria-hidden="true"')
    lines.append('          focusable="false">')
    lines.append("  <!-- The brand gear, lifted from Assets/brand/istor-gear.svg")
    lines.append("       by Source/tools/make-win-mark.py - do not hand-edit.")
    lines.append("       Strokes are currentColor so the gear re-inks with its")
    lines.append("       row; the pinion is .mark-pinion, coral by default and")
    lines.append("       --coral-lift in the field and poster worlds. -->")
    lines.append('  <g fill="none" stroke="currentColor" stroke-width="%s"'
                 % STROKE_W)
    lines.append('     stroke-linecap="round">')
    lines.append('    <circle cx="30.00" cy="34.00" r="23.00"/>')
    for d in paths:
        lines.append('    <path d="%s"/>' % d)
    lines.append('    <circle class="mark-pinion" cx="%s" cy="%s" r="%s"'
                 % pinion_xy.groups())
    lines.append('          fill="var(--coral)" stroke="none"/>')
    lines.append("  </g>")
    lines.append("</symbol>")
    return "\n".join(lines) + "\n"


def self_test() -> int:
    worst = 0
    out = OUT.read_text(encoding="utf-8")
    master = MASTER.read_text(encoding="utf-8")

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" " + detail) if detail else ""))
        if not good:
            worst = 1

    check("one symbol, nothing else",
          out.count("<symbol") == 1 and out.count("</symbol>") == 1
          and out.strip().startswith("<symbol"))
    check("id is i-mark", 'id="i-mark"' in out)
    check("strokes currentColor", 'stroke="currentColor"' in out)
    hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", out)
    check("no hex anywhere", not hexes, str(hexes[:3]))

    master_teeth = re.findall(r"<path\b[^>]*d=\"([^\"]+)\"", master)
    out_teeth = re.findall(r"<path\b[^>]*d=\"([^\"]+)\"", out)
    check("three path elements as the master has",
          len(master_teeth) == 3 and len(out_teeth) == 3)
    check("tooth geometry byte-identical to the master",
          out_teeth == master_teeth)

    m_subpaths = sum(d.count("M") for d in master_teeth)
    o_subpaths = sum(d.count("M") for d in out_teeth)
    check("%d tooth+spoke subpaths, as the master" % m_subpaths,
          o_subpaths == m_subpaths, "found %d" % o_subpaths)

    check("pinion survives, classed",
          'class="mark-pinion"' in out and "r=\"4.6\"" in out)
    check("pinion on the palette's coral", 'fill="var(--coral)"' in out)
    check("stroke width is the master's %s" % STROKE_W,
          'stroke-width="%s"' % STROKE_W in out)
    check("viewBox is the master's 64",
          'viewBox="0 0 64 64"' in out)

    if worst == 0:
        print("win-mark self-test ok: one symbol, currentColor strokes, "
              "master geometry byte-identical, pinion classed and tokened")
    return worst


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    OUT.write_text(build(), encoding="utf-8", newline="\n")
    print("wrote %s (%d bytes) from %s"
          % (OUT.relative_to(OUT.parents[2]), len(OUT.read_text(encoding="utf-8")),
             MASTER.relative_to(ROOT)))
