#!/usr/bin/env python3
"""Draw a mark for each of the library's seven groups.

    python Source/tools/make-group-marks.py [--self-test]

Writes Source/figures/group-mark-<anchor>.svg, one per group.

WHY THIS EXISTS. The library's front door is a list of 75 links under seven plain
headings, and the seven headings are the only structure a reader gets. The landing
argues in drawings and the library's pages now carry six generated plates, but the
directory itself says nothing about what a group IS until the reader has read its
blurb. A mark per group gives the structure a shape before the reading starts, and
gives every page a family it visibly belongs to (the same seven anchors key the
groups, so a page's mark is the mark of the group its slug classifies into).

THE MARK LANGUAGE IS THE BRAND'S, not a new one. The site's mark is a page with an
eye, drawn as open strokes in `currentColor` at a 2.4-3.6 unit weight, and it themes
because it inherits the text colour. These marks inherit both facts: 48-unit boxes,
one stroke weight, `currentColor` only, no fills except where a shape needs a solid
(a dot is a dot), and no text of any kind. Decorative by construction: each one sits
beside a heading that already names the group, so they are `aria-hidden` where they
are used and the generator emits no title or description to announce twice.

WHAT THE SEVEN ARE, and each is about its group rather than about the site:
`what-it-is` a card with a margin rule and shorter lines (definitions), `how-it-works`
two interlocking rings (mechanism), `how-to-do-it` three chevrons (a sequence of
steps), `whether-it-can` a lens with four rays (the capability question), `using-it-
for-your-own-work` a ruled notebook, `compared-with-other-tools` three bars of
different heights, `the-project-log` a line with three dots on it.

WHAT THE SELF-TEST IS FOR. Seven marks that are the same shape seven times would be
worse than none, so the check that matters most is that the seven are DISTINGUISHABLE:
their path data is reduced to a signature and the signatures must all differ. The rest
is the family's usual discipline - one box size, one stroke weight, nothing outside the
box, no colour that cannot theme, no text - which is what keeps seven drawings looking
like one set rather than seven.
"""

import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

BOX = 48.0
STROKE = 2.6

# The anchors are the library index's own group anchors, so the mapping from a
# heading to its mark is the heading's own name run through the index's rule. The
# index generator looks its mark up with the same rule, and its self-test fails if a
# group has no mark, which is the drift this coupling would otherwise invite.
GROUPS = ("what-it-is",
          "how-it-works-and-why-it-behaves-that-way",
          "how-to-do-it",
          "whether-it-can",
          "using-it-for-your-own-work",
          "compared-with-other-tools",
          "the-project-log")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def stroke(d: str, fill: str = "none", width: float = STROKE) -> str:
    return (f'<path d="{d}" fill="{fill}" stroke="currentColor" '
            f'stroke-width="{width:g}" stroke-linecap="round" stroke-linejoin="round"/>')


def circle(cx: float, cy: float, r: float, fill: str = "none") -> str:
    return (f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" '
            f'stroke="currentColor" stroke-width="{STROKE:g}"/>')


def element(tag: str, **attrs) -> str:
    bits = [f"<{tag}"]
    for k, v in attrs.items():
        bits.append(f' {k.replace("_", "-")}="{v}"' if not isinstance(v, float)
                    else f' {k.replace("_", "-")}="{v:g}"')
    return "".join(bits) + "/>"


def body(anchor: str) -> str:
    """The strokes of one mark. Geometry only: no colours, no text, nothing outside."""
    if anchor == "what-it-is":
        # A card with a margin rule and lines that get shorter: a definition.
        return "\n".join([
            element("rect", x=9.0, y=8.0, width=30.0, height=32.0, rx=4.5, ry=4.5,
                    fill="none", stroke="currentColor", stroke_width=STROKE),
            stroke("M16 14 V36"),
            stroke("M22 18 H32"),
            stroke("M22 24 H30"),
            stroke("M22 30 H28"),
        ])
    if anchor == "how-it-works-and-why-it-behaves-that-way":
        # Two interlocking rings: a mechanism, and one part moving another.
        return "\n".join([circle(18.5, 24, 9.5), circle(29.5, 24, 9.5)])
    if anchor == "how-to-do-it":
        # Three chevrons: a sequence of steps, read left to right.
        return "\n".join([stroke("M11 16 L18 24 L11 32"),
                          stroke("M21 16 L28 24 L21 32"),
                          stroke("M31 16 L38 24 L31 32")])
    if anchor == "whether-it-can":
        # A lens with four rays: the question every page in the group asks.
        return "\n".join([
            circle(24, 24, 10.5), circle(24, 24, 4.2),
            stroke("M24 6.5 V13.5"), stroke("M24 34.5 V41.5"),
            stroke("M6.5 24 H13.5"), stroke("M34.5 24 H41.5"),
        ])
    if anchor == "using-it-for-your-own-work":
        # A ruled notebook: a cover edge, a margin, and three lines to write on.
        return "\n".join([
            element("rect", x=11.0, y=8.0, width=26.0, height=32.0, rx=3.5, ry=3.5,
                    fill="none", stroke="currentColor", stroke_width=STROKE),
            stroke("M18 8 V40"),
            stroke("M23 17 H32"), stroke("M23 24 H32"), stroke("M23 31 H29"),
        ])
    if anchor == "compared-with-other-tools":
        # Three bars of different heights: a comparison, without a chart's clutter.
        return "\n".join([
            stroke("M13 20 V36"), stroke("M24 13 V36"), stroke("M35 26 V36"),
        ])
    if anchor == "the-project-log":
        # A line with three dots on it, the last one filled: entries over time.
        return "\n".join([
            stroke("M9 24 H39"),
            circle(14, 24, 2.8, "currentColor"),
            circle(24, 24, 2.8),
            circle(34, 24, 2.8),
        ])
    raise SystemExit("make-group-marks: no mark is defined for %r" % anchor)


def draw(anchor: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
            'width="%g" height="%g" aria-hidden="true" focusable="false" '
            'class="group-mark" data-group="%s" '
            'data-generated-by="Source/tools/make-group-marks.py - do not hand-edit">\n'
            "%s\n</svg>\n" % (BOX, BOX, BOX, BOX, anchor, body(anchor)))


def numbers(svg: str) -> list:
    return [float(m) for m in re.findall(r'="(-?[\d.]+)"', svg)]


def check_shape(svg: str, anchor: str) -> list:
    """Nothing may leave the box, and the box is the box.

    A mark that overflows is clipped silently, which is the failure the plates keep
    finding in their own labels: the drawing still looks finished.
    """
    bad = []
    if f'viewBox="0 0 48 48"' not in svg or 'width="48"' not in svg:
        bad.append(f"{anchor}: the mark is not in a 48-unit box")
    for cx in re.findall(r'cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', svg):
        x, y, r = (float(v) for v in cx)
        if x - r < 0 or y - r < 0 or x + r > BOX or y + r > BOX:
            bad.append(f"{anchor}: a circle at ({x:g}, {y:g}) r={r:g} leaves the box")
    for m in re.finditer(r'<path d="([^"]+)"', svg):
        for xy in re.findall(r"(-?[\d.]+)", m.group(1)):
            v = float(xy)
            if v < 0 or v > BOX:
                bad.append(f"{anchor}: a path coordinate at {v:g} leaves the box")
    for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" '
                         r'height="([\d.]+)"', svg):
        x, y, w, h = (float(v) for v in m.groups())
        if x < 0 or y < 0 or x + w > BOX or y + h > BOX:
            bad.append(f"{anchor}: the rect at ({x:g}, {y:g}) {w:g}x{h:g} leaves the box")
    return bad


def check_language(svg: str, anchor: str) -> list:
    """One colour that themes, one weight, no text and nothing to announce."""
    bad = []
    if re.search(r"#[0-9A-Fa-f]{3,8}\b", svg):
        bad.append(f"{anchor}: carries a hex colour, so it cannot theme with the page")
    if "var(--" in svg:
        bad.append(f"{anchor}: points at a library token; a mark beside a heading in "
                   "the page head has no plate's stylesheet to resolve it")
    if "currentColor" not in svg:
        bad.append(f"{anchor}: does not draw in currentColor, so it would not follow "
                   "the text it sits beside")
    if re.search(r"<text", svg):
        bad.append(f"{anchor}: contains text; a mark that spells something is a label")
    if "aria-hidden" not in svg:
        bad.append(f"{anchor}: is not hidden from assistive technology, and the heading "
                   "beside it already names the group")
    for w in set(re.findall(r'stroke-width="([\d.]+)"', svg)):
        if abs(float(w) - STROKE) > 0.001:
            bad.append(f"{anchor}: a stroke at weight {w} against the set's {STROKE:g}")
    return bad


def signature(svg: str) -> str:
    """The mark's shape, reduced to something two drawings can be compared by.

    The first version dropped every number and every tag, which left the empty string
    for all seven: a signature that says nothing matches everything, and the self-test
    reported all seven marks as duplicates of each other. What is kept is the element
    list, the path command sequence, and the coordinates coarsely rounded - coarse
    because two marks whose geometry differs by less than 6 units are the same drawing
    at the size these are shown at, and that is the case worth failing.
    """
    paths = re.findall(r'd="([^"]+)"', svg)
    tags = re.findall(r"<(\w+)", svg)
    cmds = re.findall(r"[MHVLZmlhvz]", " ".join(paths))
    coarse = [round(float(n) / 6) for n in re.findall(r"-?[\d.]+", " ".join(paths))]
    circles = re.findall(r'cx="(-?[\d.]+)" cy="(-?[\d.]+)" r="(-?[\d.]+)"', svg)
    rounding = [round(float(v) / 6) for triple in circles for v in triple]
    return "%s#%s#%s#%s" % (tags, "".join(cmds), coarse, rounding)


def write() -> list:
    written = []
    for anchor in GROUPS:
        svg = draw(anchor)
        path = OUT / f"group-mark-{anchor}.svg"
        path.write_bytes(svg.encode("utf-8"))
        written.append((anchor, svg, path))
    return written


def self_test() -> int:
    bad = []
    written = write()
    seen = {}
    for anchor, svg, path in written:
        bad += check_shape(svg, anchor)
        bad += check_language(svg, anchor)
        if not path.is_file():
            bad.append(f"{anchor}: nothing was written to {path}")
        sig = signature(svg)
        if sig in seen:
            bad.append(f"{anchor}: draws the same shape as {seen[sig]}, so two groups "
                       "would look the same at a glance")
        seen[sig] = anchor
    if len(written) != len(GROUPS):
        bad.append(f"the set has {len(written)} marks for {len(GROUPS)} groups")
    if bad:
        print("group-marks self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("group-marks self-test ok: %d marks, all seven distinguishable, all inside "
          "their box, one stroke weight, currentColor only, no text, no colour that "
          "cannot theme" % len(written))
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    for anchor, svg, path in write():
        print(f"{path.name}  {len(svg.encode('utf-8')):,} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
