#!/usr/bin/env python3
"""Draw the embedding page's claim: meaning maps to position.

    python Source/tools/make-embedding-map.py [--self-test]

Writes Source/figures/embedding-map-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues in geometry and shows nothing: "meaning maps to
position: two passages about the same finding land near each other even if one says
efficacy and the other says how well it worked", while "keyword search... cannot see
a paraphrase. Ask about drug safety while a paper says adverse events, and keywords
return nothing while the meaning sits right there." Both sentences are shapes. The
plate is one panel of a library's passages as positions, the question placed among
them, and the two ways a search can reach: the keyword ray, which stops at the
wording wall, and the near-neighbour circle, which reaches across it.

THE POINTS ARE A DRAWING, NOT A DATASET, and both the plate and the caption say so.
What is not illustrative is the RELATION the page asserts, and that is what the
self-test holds: the two phrasings of one finding are each other's nearest neighbour
among everything drawn, the question is nearer to them than to any keyword-aligned
passage, and the keyword ray's first hit is a passage the near-neighbour circle does
not reach - because "keywords for the terms you actually used, embeddings for the
ones you did not" is the page's conclusion, not a decoration on it.

LABELLED, NOT ANNOTATED. Four points carry their own words, because an unlabelled
scatter proves nothing: the reader has to SEE that the two passages about one finding
sit together while saying different words. The labels are placed by plan() before
anything is drawn, so "does a label sit inside the plate" and "does a label sit on
another" are questions about data, and the first composition failed both in one
place - the paired passage's label sat on its twin's point.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the
drawing themes with the page, and no hex value appears in it. The witness marks the
pair the page is about, and the dashed circle is the near-neighbour reach - the only
dashed stroke on the plate, as the token row's hole was the only dashed box.
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

TITLE = "one library, two ways to reach it"

# The library, as positions. Units are the plate's own; the relation is the content.
# Six passages a research library actually holds, of which two are the same finding
# in different words - the page's own example pair, efficacy / how well it worked -
# and one shares the question's keyword without sharing its subject, which is the
# honest weakness of the keyword half: it returns something. The question sits in the
# pair's neighbourhood: the meaning it is about is what is NEAR it, and the keyword
# hit is deliberately farther, which is the page's point - the wording you share is
# not where the subject you want lives. The field keeps every point inside the wide
# plate with a label's room to its right.
POINTS = (
    # name, x, y, label (None = unlabelled), group
    ("efficacy",   168.0, 118.0, "a paper: efficacy", "pair"),
    ("worked",     200.0, 142.0, "a thesis: how well it worked", "pair"),
    ("safety",      43.1, 173.9, "a paper: adverse events", "topic"),
    ("keyworded",   64.2, 262.8, "a note: drug safety", "keyword"),
    ("methods",    256.8, 292.7, None, "other"),
    ("archive",    348.7, 296.2, None, "other"),
)

# The question, and which point is which. It sits high in the field, clear of the
# pair's labels below-left of it, and its label reads to the RIGHT on the wide plate
# and to the LEFT on the tall one, because 380 units cannot hold a 27-character label
# hung off a point in the right half. The side is chosen by the same rule the point
# labels use.
QUESTION = (352.0, 96.0, "the question: drug safety")

# The keyword ray stops at the passage that shares its words. The wording wall is the
# gap between the question and the meaning it is about.
RAY_TO = "keyworded"

# The near-neighbour circle: centred on the question, drawn to just include the pair.
# Its radius is DERIVED - the distance to the farther of the two paired passages - so
# the circle cannot drift away from the relation it asserts.
CIRCLE_PAD = 14.0

PAIR = ("efficacy", "worked")

LINE_KW = "keywords reach the wording, not the subject"
LINE_EM = "nearness reaches across the wording"
NOTES = ("The positions are the argument,",
         "not a model's own coordinates.")

WITNESS_LABEL = None  # the points label themselves

# The text floors, DERIVED like every plate here: the tall plate is 380 units wide
# and renders at 280px in a 320px viewport, a 0.737 scale, so 15 units lands at
# 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

FACTS = ((TITLE, "the title"), (LINE_KW, "the keyword line"),
         (LINE_EM, "the nearness line")) + \
        tuple((note, "a footnote line") for note in NOTES) + \
        tuple((label, "a point's label") for _n, _x, _y, label, _g in POINTS if label) + \
        ((QUESTION[2], "the question's label"),)


WIDE = {
    "w": 640, "h": 420, "name": "wide",
    "x0": 0.0, "y0": 0.0,
    "title_x": 24.0, "title_y": 30.0, "label": 16.0, "foot": 16.0,
    "line1_y": 376.0, "line2_y": 396.0,
    "foot_x": 24.0,
}

TALL = {
    "w": 380, "h": 452, "name": "tall",
    "x0": 0.0, "y0": 0.0,
    "title_x": 22.0, "title_y": 26.0, "label": 15.0, "foot": 15.0,
    "line1_y": 404.0, "line2_y": 424.0,
    "foot_x": 22.0,
}

# Scale the field of points to each plate: the coordinates above are drawn for the
# wide plate; the tall one compresses x by its band ratio so nothing runs off.
def _field(spec: dict) -> tuple:
    sx = (spec["w"] - 2 * 24) / (640 - 2 * 24)
    sy = 1.0 if spec["name"] == "wide" else (spec["h"] - 170) / (420 - 148)
    return sx, sy


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float, adv: float) -> float:
    return len(s) * size * adv


def pt(spec: dict, name: str) -> tuple:
    sx, sy = _field(spec)
    for n, x, y, *_rest in POINTS:
        if n == name:
            return 24 + x * sx, 60 + y * sy
    raise KeyError(name)


def qpos(spec: dict) -> tuple:
    sx, sy = _field(spec)
    return 24 + QUESTION[0] * sx, 60 + QUESTION[1] * sy


# The two numbered lines, and the room the tall variant gives them: its band is 332
# units wide, so a 37-character line at 15 units is what fits. The lines are the
# plate's conclusion and they are CHECKED against the drawn geometry in check_lines.


def circle(spec: dict) -> tuple:
    """Centre, radius: the question to the farther paired passage, plus pad."""
    qx, qy = qpos(spec)
    rs = [pow(pow(qx - pt(spec, n)[0], 2) + pow(qy - pt(spec, n)[1], 2), 0.5)
          for n in PAIR]
    return qx, qy, max(rs) + CIRCLE_PAD


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font, colour,
    anchor). Drawing reads this and the checks read this, so neither can drift."""
    out = [("title", TITLE, spec["title_x"], spec["title_y"], spec["label"],
            FONTS_SANS, MIST, "start")]
    for name, _x, _y, label, _g in POINTS:
        if label:
            px, py = pt(spec, name)
            # Labels read to the LEFT of their point when the point is in the right
            # half of the field, so a label never has to cross the question's own.
            anchor = "end" if px > spec["w"] * 0.52 else "start"
            dx = -10 if anchor == "end" else 10
            out.append(("pt-%s" % name, label, px + dx, py + 4, spec["label"],
                        FONTS_SANS, INK, anchor))
    qx, qy = qpos(spec)
    q_anchor = "end" if qx > spec["w"] * 0.52 else "start"
    out.append(("question", QUESTION[2], qx + (-10 if q_anchor == "end" else 10),
                qy - 14, spec["label"], FONTS_SANS, WITNESS, q_anchor))
    out.append(("line-kw", LINE_KW, spec["foot_x"], spec["line1_y"], spec["label"],
                FONTS_SANS, MIST, "start"))
    out.append(("line-em", LINE_EM, spec["foot_x"], spec["line2_y"], spec["label"],
                FONTS_SANS, INK, "start"))
    return out


def check_lines(spec: dict, name: str) -> list:
    """The two conclusion lines are inside the plate they conclude, which is the
    constraint their wording is sized to."""
    bad = []
    for lname, x0, x1, _t, _b in boxes(spec):
        if lname.startswith("line-") and x1 > spec["w"]:
            bad.append("%s: %s runs to %g of %g, and a conclusion that is cut off "
                       "concludes nothing" % (name, lname, x1, spec["w"]))
    return bad


def boxes(spec: dict) -> list:
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


def draw(spec: dict) -> str:
    qx, qy, r = circle(spec)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" '
           'height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("A library’s passages as positions. The two phrasings of one "
                  "finding sit nearest each other; keywords reach the note that "
                  "shares the words, and the near-neighbour circle reaches the "
                  "subject across the wording."),
              spec["name"])]
    # the field's ground
    out.append('<rect x="%g" y="52" width="%g" height="%g" fill="%s"/>'
               % (12, spec["w"] - 24, spec["h"] - 134, SUBTLE))
    # the near-neighbour circle: the only dashed stroke on the plate
    out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" '
               'stroke-width="1.5" stroke-dasharray="5 4"/>'
               % (qx, qy, r, WITNESS))
    # the keyword ray: solid, mist, from the question to the point that shares its
    # words, stopping at the wording wall
    kx, ky = pt(spec, RAY_TO)
    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
               'stroke-width="1.5"/>' % (qx, qy, kx, ky, MIST))
    # the passages
    for name, _x, _y, _label, group in POINTS:
        px, py = pt(spec, name)
        if group == "pair":
            out.append('<circle cx="%.2f" cy="%.2f" r="5" fill="%s"/>'
                       % (px, py, WITNESS))
        else:
            out.append('<circle cx="%.2f" cy="%.2f" r="4.4" fill="%s"/>'
                       % (px, py, MIST))
    # the question
    out.append('<path d="M%g %g l7 -12 h-14 z" fill="%s"/>'
               % (qx, qy + 4, WITNESS))
    for name, s, x, y, size, font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size, font,
                            weight="600" if name in ("question", "line-em") else None,
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
        path = out / ("embedding-map-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def dist(spec: dict, a: tuple, b: tuple) -> float:
    return pow(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2), 0.5)


def check_pair(spec: dict, name: str) -> list:
    """The two phrasings of one finding are each other's nearest neighbour among
    everything drawn, and the question is nearer to them than to any keyword-aligned
    passage."""
    bad = []
    for a, b in (PAIR, (PAIR[1], PAIR[0])):
        da = dist(spec, pt(spec, a), pt(spec, b))
        for other, _x, _y, _l, _g in POINTS:
            if other in PAIR:
                continue
            if dist(spec, pt(spec, a), pt(spec, other)) <= da:
                bad.append("%s: %s is as near to %s as its own pair, and the pair "
                           "being nearest is the page's claim"
                           % (name, a, other))
    qx = qpos(spec)
    d_pair = min(dist(spec, qx, pt(spec, n)) for n in PAIR)
    d_kw = dist(spec, qx, pt(spec, RAY_TO))
    if d_kw <= d_pair:
        bad.append("%s: the question sits no nearer the meaning than the wording, "
                   "and nearness across the wording is what the plate argues"
                   % name)
    return bad


def check_circle(spec: dict, name: str, svg: str) -> list:
    """The circle includes the pair and excludes the keyword hit - the page's
    conclusion, drawn."""
    bad = []
    qx, qy, r = circle(spec)
    for n in PAIR:
        if dist(spec, (qx, qy), pt(spec, n)) > r:
            bad.append("%s: the circle does not reach %s, and reaching the pair is "
                       "what it is drawn for" % (name, n))
    for n, _x, _y, _l, group in POINTS:
        if group in ("pair",):
            continue
        if dist(spec, (qx, qy), pt(spec, n)) <= r:
            bad.append("%s: the circle also reaches %s, and a near-neighbour circle "
                       "that sweeps up bystanders is not the instrument the page "
                       "describes" % (name, n))
    if dist(spec, (qx, qy), pt(spec, RAY_TO)) <= r:
        bad.append("%s: the circle reaches the keyword hit, and keywords-for-the-"
                   "terms-you-used being a DIFFERENT reach is the page's conclusion"
                   % name)
    dashes = re.findall(r'stroke-dasharray="([^"]+)"', svg)
    if len(dashes) != 1:
        bad.append("%s: %d dashed strokes are drawn, and the near-neighbour circle "
                   "is meant to be the only one" % (name, len(dashes)))
    return bad


def check_ray(spec: dict, name: str, svg: str) -> list:
    """The ray runs from the question to the passage that shares its words, and stops
    there."""
    bad = []
    qx, qy = qpos(spec)
    kx, ky = pt(spec, RAY_TO)
    m = re.search(r'<line x1="([0-9.]+)" y1="([0-9.]+)" x2="([0-9.]+)" '
                  r'y2="([0-9.]+)" stroke="%s"' % re.escape(MIST), svg)
    if not m:
        bad.append("%s: the keyword ray is not drawn in the mist ink" % name)
        return bad
    got = tuple(float(v) for v in m.groups())
    want = (round(qx, 2), round(qy, 2), round(kx, 2), round(ky, 2))
    if got != want:
        bad.append("%s: the ray runs %s and the question to %s is %s"
                   % (name, got, RAY_TO, want))
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
    """No label sits on another, and no label sits on a point."""
    bad = []
    bx = boxes(spec)
    for i, (a, ax0, ax1, ay0, ay1) in enumerate(bx):
        for b, bx0, bx1, by0, by1 in bx[i + 1:]:
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                bad.append("%s: %s sits on %s" % (name, a, b))
    for lname, x0, x1, t, b in bx:
        for pname, _x, _y, _l, _g in POINTS:
            px, py = pt(spec, pname)
            if x0 - 3 < px < x1 + 3 and t - 3 < py < b + 3:
                bad.append("%s: %s sits on the point %s" % (name, lname, pname))
        qx, qy = qpos(spec)
        if x0 - 3 < qx < x1 + 3 and t - 3 < qy < b + 3 and lname != "question":
            bad.append("%s: %s sits on the question" % (name, lname))
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


def check_fills(svg: str, name: str) -> list:
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {SUBTLE, MIST, WITNESS, INK}:
        bad = "%s: the plate fills with %s, and only the library's own tokens may " \
              "appear" % (name, sorted(fills))
        return [bad]
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

    Points and strokes carry the plate's meaning, so they are held to the 3:1 a
    graphic needs; every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "the points and the ray, graphics"),
                             ("witness", "the pair, the circle, a graphic")):
            for ground in ("canvas", "subtle"):
                ratio = contrast(t[colour], t[ground])
                if ratio < 3.0:
                    bad.append("%s theme, %s on %s: %.2f:1, under 3:1, and %s"
                               % (theme, colour, ground, ratio, what))
        for colour, what in (("ink", "the labels"), ("mist", "the title and the "
                                                    "keyword line"),
                             ("witness", "the question's label")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s on canvas: %.2f:1, under 4.5, and %s is text"
                           % (theme, colour, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "embedding-map-wide.svg",
                         OUT / "embedding-map-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_pair(spec, name)
        bad += check_circle(spec, name, svg)
        bad += check_ray(spec, name, svg)
        bad += check_inside(spec, name)
        bad += check_no_overlap(spec, name)
        bad += check_text_floor(svg, floor, name)
        bad += check_no_hex(svg, name)
        bad += check_fills(svg, name)
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
        print("embedding-map self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("embedding-map self-test ok: the paired phrasings are each other's nearest "
          "neighbour and the question is nearer them than the wording, the circle "
          "reaches the pair and excludes the keyword hit and is the only dashed "
          "stroke, the ray runs from the question to the passage that shares its "
          "words and stops, every label sits inside the plate and none sits on "
          "another or on a point, both variants make the same claims, no hex colour, "
          "and every colour clears its bar in both themes")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
