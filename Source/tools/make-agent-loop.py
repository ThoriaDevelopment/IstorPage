#!/usr/bin/env python3
"""Draw the page's own heading: a loop, not a single answer.

    python Source/tools/make-agent-loop.py [--self-test]

Writes Source/figures/agent-loop-wide.svg and -tall.svg

WHY THIS EXISTS. The page argues in paths and shows none: "Ordinary chat is
one pass of inference: question in, answer out, done. An agent inserts a
middle... the model's output can name an action, a piece of software notices,
runs it, and hands the result back as more text for the model to read. The
model then decides whether the job is finished or another step is needed." The
plate is that paragraph as one drawing: two paths that share their start and
their end - the question and the answer - of which chat's is a single straight
pass and the agent's bends through a tool and back into the model, twice drawn
as one loop. The agency itself is drawn as what the page says it is: the
branch at the model, which has exactly two ways out - call a tool, or decide
it is done.

THE FIRST FLOWCHART HERE, and its checks are topological rather than
numerical: every arrow tip lands on a node's boundary; the tool is touched by
exactly two witness segments, one in and one out; the model by four, two in
and two out, which is what makes it a loop through a revisited box rather than
a sequence of boxes; the chat path touches no node between its endpoints; and
the model has exactly two outgoing segments, because a model with one way out
is a pipe and a model with three is not what the page describes. No scores,
no timings - the plate's note says so.

PLANNED, THEN DRAWN, like every plate here: every string is placed by plan()
before any of it is rendered, and the labels are checked against the drawn
segments the way reading-bar's are, segment by segment, because a flowchart
whose labels sit on its own arrows is not a flowchart.

TOKENS, NOT COLOURS: fills and strokes are the library's own variables, so the
drawing themes with the page, and no hex value appears in it. The agent's path
is the witness colour - it is the subject - and chat's one pass is mist: the
context the page improves on.
"""

import math
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

TITLE = "a loop, not a single answer"

NODE_TEXTS = (("question", "question"), ("model", "model"),
              ("tool", "tool"), ("answer", "answer"))

CHAT_LABEL = "ordinary chat: one pass"
CALL_LABEL = "names an action"
BACK_LABEL = "result, as text"
DONE_LABEL = "decides it is done"

NOTES = ("Chat is one pass. The agent bends it.",
         "Each turn is still ordinary inference.")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def width_of(s: str, size: float) -> float:
    return len(s) * size * ADV_SANS


def seg_len(a: tuple, b: tuple) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def arrow_head(a: tuple, b: tuple, colour: str, size: float = 7.0) -> str:
    """A triangle at b, pointing along a->b, tip exactly on the node edge."""
    L = seg_len(a, b) or 1.0
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    px, py = -uy, ux
    bx, by = b[0] - ux * size, b[1] - uy * size
    pts = [(b[0], b[1]),
           (bx + px * size * 0.45, by + py * size * 0.45),
           (bx - px * size * 0.45, by - py * size * 0.45)]
    return '<polygon points="%s" fill="%s"/>' % (
        " ".join("%g,%g" % p for p in pts), colour)


def arrow_line(a: tuple, b: tuple, colour: str, width: float) -> str:
    """The shaft, stopped short so the triangle's tip is the contact point."""
    L = seg_len(a, b) or 1.0
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    ex, ey = b[0] - ux * 5.6, b[1] - uy * 5.6
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" '
            'stroke-width="%g"/>' % (a[0], a[1], ex, ey, colour, width))


def agent_segs(spec: dict) -> list:
    """The agent's path, as four (start, end) pairs between node edges: into
    the model, out to the tool, back into the model, out to the answer. Two
    visits to one box is the loop; the two ways out of it are the branch."""
    q, m, t, a = (spec["nodes"][k] for k in ("question", "model", "tool",
                                              "answer"))
    return [((q[0] + q[2], q[1] + q[3] / 2), (m[0], m[1] + m[3] * 0.34)),
            ((m[0] + m[2] / 2, m[1] + m[3]), (t[0] + t[2] / 2, t[1])),
            ((t[0] + t[2], t[1] + t[3] / 2), (m[0] + m[2], m[1] + m[3] * 0.78)),
            ((m[0] + m[2] * 0.7, m[1]), (a[0] + a[2] * 0.4, a[1] + a[3]))]


def chat_seg(spec: dict) -> tuple:
    q, a = spec["nodes"]["question"], spec["nodes"]["answer"]
    return ((q[0] + q[2], q[1] + q[3] / 2), (a[0], a[1] + a[3] / 2))


# The text floors, DERIVED like every plate here: the tall plate is 380 units
# wide and renders at 280px in a 320px viewport, a 0.737 scale, so 15 units
# lands at 11.05px.
FLOOR_WIDE = 16
FLOOR_TALL = 15

FACTS = ((TITLE, "the title"), (CHAT_LABEL, "the chat path's label"),
         (CALL_LABEL, "the call label"), (BACK_LABEL, "the return label"),
         (DONE_LABEL, "the done label")) + \
        tuple((txt, "a node's text") for _k, txt in NODE_TEXTS) + \
        tuple((note, "a footnote line") for note in NOTES)

WIDE = {
    "w": 640, "h": 344, "name": "wide",
    "title_y": 30.0,
    "nodes": {"question": (24.0, 78.0, 116.0, 32.0),
              "answer": (500.0, 78.0, 116.0, 32.0),
              "model": (242.0, 170.0, 156.0, 36.0),
              "tool": (272.0, 262.0, 100.0, 30.0)},
    "chat_label_y": 86.0,
    "call_label": (312.0, 232.0, "end"),
    "back_label": (404.0, 250.0, "start"),
    "done_label": (496.0, 116.0, "end"),
    "node_text": 16.0, "label": 16.0, "foot": 16.0,
    "foot_y": 318.0, "foot_step": 19.0,
}

TALL = {
    "w": 380, "h": 368, "name": "tall",
    "title_y": 26.0,
    "nodes": {"question": (22.0, 72.0, 80.0, 28.0),
              "answer": (298.0, 72.0, 80.0, 28.0),
              "model": (110.0, 158.0, 160.0, 34.0),
              "tool": (142.0, 268.0, 96.0, 28.0)},
    "chat_label_y": 78.0,
    "call_label": (182.0, 232.0, "end"),
    "back_label": (244.0, 302.0, "start"),
    "done_label": (292.0, 112.0, "end"),
    "node_text": 15.0, "label": 15.0, "foot": 15.0,
    "foot_y": 336.0, "foot_step": 18.0,
}


def plan(spec: dict) -> list:
    """Every string the plate draws, as (name, text, x, baseline, size, font,
    colour, anchor). Node texts sit centred in their boxes; the four path
    labels sit where the empty space is."""
    size, foot = spec["node_text"], spec["foot"]
    out = [("title", TITLE, spec["nodes"]["question"][0], spec["title_y"],
            spec["label"], FONTS_SANS, MIST, "start")]
    for key, txt in NODE_TEXTS:
        x, y, w, h = spec["nodes"][key]
        out.append(("node-%s" % key, txt, x + w / 2, y + h / 2 + size * 0.34,
                    size, FONTS_SANS, INK, "middle"))
    out.append(("chat-label", CHAT_LABEL,
                (spec["nodes"]["question"][0] + spec["nodes"]["question"][2]
                 + spec["nodes"]["answer"][0]) / 2,
                spec["chat_label_y"], foot, FONTS_SANS, MIST, "middle"))
    for name, (x, y, anchor) in (("call-label", spec["call_label"]),
                                 ("back-label", spec["back_label"]),
                                 ("done-label", spec["done_label"])):
        txt = {"call-label": CALL_LABEL, "back-label": BACK_LABEL,
               "done-label": DONE_LABEL}[name]
        out.append((name, txt, x, y, foot, FONTS_SANS, MIST, anchor))
    for j, note in enumerate(NOTES):
        out.append(("note%d" % j, note, spec["nodes"]["question"][0],
                    spec["foot_y"] + j * spec["foot_step"], foot,
                    FONTS_SANS, MIST, "start"))
    return out


def node_label_names() -> set:
    return {"node-%s" % k for k, _t in NODE_TEXTS}


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


def svg_text(x: float, y: float, s: str, fill: str, size: float, weight=None,
             anchor=None) -> str:
    bits = ['<text x="%g" y="%g" font-family="%s" font-size="%g" fill="%s"'
            % (x, y, FONTS_SANS, size, fill)]
    if weight:
        bits.append(' font-weight="%s"' % weight)
    if anchor:
        bits.append(' text-anchor="%s"' % anchor)
    bits.append(">%s</text>" % esc(s))
    return "".join(bits)


def draw_nodes(spec: dict) -> str:
    out = []
    for key, txt in NODE_TEXTS:
        x, y, w, h = spec["nodes"][key]
        out.append('<rect x="%g" y="%g" width="%g" height="%g" rx="6" '
                   'fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x, y, w, h, SUBTLE, MIST))
    return "".join(out)


def draw_paths(spec: dict) -> str:
    out = [arrow_line(*chat_seg(spec), MIST, 2.0),
           arrow_head(*chat_seg(spec), MIST)]
    for a, b in agent_segs(spec):
        out.append(arrow_line(a, b, WITNESS, 2.5))
        out.append(arrow_head(a, b, WITNESS))
    return "".join(out)


def draw(spec: dict) -> str:
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'width="%g" height="%g" role="img" aria-label="%s" focusable="false" '
           'data-variant="%s">'
           % (spec["w"], spec["h"], spec["w"], spec["h"],
              esc("Ordinary chat is one pass from question to answer. An agent "
                  "bends that pass through a tool and back into the model, and "
                  "at the model decides: call a tool, or it is done."),
              spec["name"])]
    out.append(draw_nodes(spec))
    out.append(draw_paths(spec))
    for name, s, x, y, size, _font, colour, anchor in plan(spec):
        out.append(svg_text(x, y, s, colour, size,
                            weight="600" if name.startswith("node-") else None,
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
        path = out / ("agent-loop-%s.svg" % spec["name"])
        path.write_bytes(svg.encode("utf-8"))
        written.append((spec, spec["name"], svg, path))
    return written


# --------------------------------------------------------------------------
# The claims. Each is a sentence this plate is making, and each can fail.
# --------------------------------------------------------------------------

def node_rects(spec: dict) -> dict:
    return spec["nodes"]


def on_boundary(spec: dict, pt: tuple, key: str, tol: float = 1.5) -> bool:
    x, y, w, h = node_rects(spec)[key]
    px, py = pt
    on_v = (abs(px - x) <= tol or abs(px - (x + w)) <= tol) and y - tol <= py <= y + h + tol
    on_h = (abs(py - y) <= tol or abs(py - (y + h)) <= tol) and x - tol <= px <= x + w + tol
    return on_v or on_h


def which_node(spec: dict, pt: tuple, tol: float = 1.5) -> str:
    for key in node_rects(spec):
        if on_boundary(spec, pt, key, tol):
            return key
    return ""


def drawn_tris(svg: str, colour: str) -> list:
    """The arrowheads in one colour, as (tip, p1, p2)."""
    out = []
    for body in re.findall(r'<polygon points="([^"]+)" fill="%s"/>'
                           % re.escape(colour), svg):
        pts = [tuple(float(v) for v in p.split(",")) for p in body.split()]
        out.append(pts)
    return out


def drawn_lines(svg: str, colour: str) -> list:
    return [((float(x1), float(y1)), (float(x2), float(y2)))
            for x1, y1, x2, y2 in re.findall(
                r'<line x1="([0-9.]+)" y1="([0-9.]+)" x2="([0-9.]+)" '
                r'y2="([0-9.]+)" stroke="%s"' % re.escape(colour), svg)]


def check_nodes(spec: dict, name: str, svg: str) -> list:
    """Four node boxes drawn, each box's own text inside it: a label that
    escapes its box is a label about nothing."""
    bad = []
    rects = re.findall(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" '
                       r'height="([0-9.]+)" rx="6" fill="%s" stroke="%s" '
                       r'stroke-width="1.5"/>' % (re.escape(SUBTLE),
                                                  re.escape(MIST)), svg)
    if len(rects) != len(NODE_TEXTS):
        bad.append("%s: %d node boxes drawn for the %d the loop needs"
                   % (name, len(rects), len(NODE_TEXTS)))
    for lname, x0, x1, t, b in boxes(spec):
        if not lname.startswith("node-"):
            continue
        key = lname[5:]
        x, y, w, h = node_rects(spec)[key]
        if not (x - 0.01 <= x0 and x1 <= x + w + 0.01 and y - 0.01 <= t
                and b <= y + h + 0.01):
            bad.append("%s: the %s text is not inside its own box" % (name, key))
    return bad


def check_chat(spec: dict, name: str, svg: str) -> list:
    """Chat is one pass: exactly one mist arrow, whose drawn shaft and head
    agree with the one logical segment the plate's geometry declares, from the
    question's edge to the answer's edge, touching no node between - that is
    the whole claim. The shaft is drawn short of its tip, so the boundaries
    are read off the segment function the drawing came from and the drawn
    elements are checked to be that segment's."""
    bad = []
    lines = drawn_lines(svg, MIST)
    if len(lines) != 1:
        bad.append("%s: %d mist lines drawn for chat's one pass"
                   % (name, len(lines)))
        return bad
    tris = drawn_tris(svg, MIST)
    if len(tris) != 1:
        bad.append("%s: %d mist arrowheads drawn for chat's one pass"
                   % (name, len(tris)))
    a, b = chat_seg(spec)
    if not on_boundary(spec, a, "question"):
        bad.append("%s: chat's pass does not leave the question's edge" % name)
    if not on_boundary(spec, b, "answer"):
        bad.append("%s: chat's pass does not arrive at the answer's edge" % name)
    if abs(lines[0][0][0] - a[0]) > 0.01 or abs(lines[0][0][1] - a[1]) > 0.01:
        bad.append("%s: the drawn shaft does not start where the segment does"
                   % name)
    if tris and (abs(tris[0][0][0] - b[0]) > 0.01
                 or abs(tris[0][0][1] - b[1]) > 0.01):
        bad.append("%s: the drawn arrowhead's tip is not the segment's end"
                   % name)
    # no node between: sample the segment's interior against every box
    for f in (0.25, 0.5, 0.75):
        px, py = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        for key, (x, y, w, h) in node_rects(spec).items():
            if x <= px <= x + w and y <= py <= y + h:
                bad.append("%s: chat's pass runs through the %s, and one pass "
                           "is the claim" % (name, key))
    return bad


def check_loop(spec: dict, name: str, svg: str) -> list:
    """The agent's path: four witness segments, each drawn where its segment
    function says; every start on a node edge, every tip on a node edge; the
    tool touched once in and once out; the model touched four times; exactly
    two ways OUT of the model, which is the branch the page calls agency.
    Topology is read from the segment functions the drawing came from, and
    the drawn shafts and heads are required to be those segments'."""
    bad = []
    lines = drawn_lines(svg, WITNESS)
    tris = drawn_tris(svg, WITNESS)
    segs = agent_segs(spec)
    if len(lines) != 4 or len(tris) != 4:
        bad.append("%s: %d witness segments and %d heads drawn for the four "
                   "the loop needs" % (name, len(lines), len(tris)))
        return bad
    for (sa, _sb), (ax, ay) in zip(lines, [a for a, _b in segs]):
        if abs(sa[0] - ax) > 0.01 or abs(sa[1] - ay) > 0.01:
            bad.append("%s: a drawn shaft starts at %g,%g and its segment "
                       "starts at %g,%g" % (name, sa[0], sa[1], ax, ay))
            break
    for tri, (_a, b) in zip(tris, segs):
        if abs(tri[0][0] - b[0]) > 0.01 or abs(tri[0][1] - b[1]) > 0.01:
            bad.append("%s: a drawn tip lands at %g,%g and its segment ends "
                       "at %g,%g" % (name, tri[0][0], tri[0][1], b[0], b[1]))
            break
    touches = {"question": 0, "model": 0, "tool": 0, "answer": 0}
    outs_from_model = 0
    for a, b in segs:
        ka, kb = which_node(spec, a), which_node(spec, b)
        if not ka:
            bad.append("%s: a segment starts at %g,%g, on no node's edge"
                       % (name, a[0], a[1]))
        if not kb:
            bad.append("%s: a segment's tip lands at %g,%g, on no node's edge"
                       % (name, b[0], b[1]))
            continue
        # a box is touched wherever a path meets it, at either end: the model
        # is entered twice and left twice, and that is the count that makes it
        # a revisited box rather than a sequence
        touches[ka] = touches.get(ka, 0) + 1
        touches[kb] = touches.get(kb, 0) + 1
        if ka == "model":
            outs_from_model += 1
    for key in ("question", "answer"):
        if touches[key] != 1:
            bad.append("%s: the %s is touched %d times by the agent's path, "
                       "and both paths share its one edge"
                       % (name, key, touches[key]))
    if touches["tool"] != 2:
        bad.append("%s: the tool is touched %d times for the two the loop "
                   "needs, one in and one out" % (name, touches["tool"]))
    if touches["model"] != 4:
        bad.append("%s: the model is touched %d times for the four that make "
                   "it a revisited box rather than a sequence"
                   % (name, touches["model"]))
    if outs_from_model != 2:
        bad.append("%s: the model has %d ways out for the two the branch "
                   "needs - call a tool, or decide it is done"
                   % (name, outs_from_model))
    return bad


def seg_label_clearance(spec: dict, name: str, svg: str) -> list:
    """No label sits on a path. The arrows are the plate's data, and a
    baseline crossing a shaft is what a label-only overlap check cannot see."""
    bad = []
    segs = [chat_seg(spec)] + agent_segs(spec)
    CLEAR = 3.0
    for lname, x0, x1, t, b in boxes(spec):
        if lname in node_label_names() or lname.startswith("note") \
                or lname == "title":
            continue
        for (ax, ay), (bx, by) in segs:
            lo, hi = min(ax, bx), max(ax, bx)
            if hi < x0 or lo > x1:
                continue
            for fx in (max(lo, x0), min(hi, x1), (max(lo, x0) + min(hi, x1)) / 2):
                if bx == ax:
                    continue
                y = ay + (by - ay) * (fx - ax) / (bx - ax)
                if t - CLEAR <= y <= b + CLEAR:
                    bad.append("%s: %s sits on a path near x=%g"
                               % (name, lname, fx))
                    break
            else:
                continue
            break
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
    """No label sits on another, and no label sits on a node box it does not
    belong to."""
    bad = []
    bx = boxes(spec)
    for i, (a, ax0, ax1, ay0, ay1) in enumerate(bx):
        for b, bx0, bx1, by0, by1 in bx[i + 1:]:
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                bad.append("%s: %s sits on %s" % (name, a, b))
    for lname, x0, x1, t, b in bx:
        if lname.startswith("node-") or lname.startswith("note") \
                or lname == "title":
            continue
        for key, (x, y, w, h) in node_rects(spec).items():
            if x0 < x + w and x < x0 + (x1 - x0) and t < y + h and y < t + (b - t):
                if not (x1 <= x + 0.01 or x0 >= x + w - 0.01
                        or b <= y + 0.01 or t >= y + h - 0.01):
                    bad.append("%s: %s sits on the %s box" % (name, lname, key))
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

    The first version of this check on another plate returned a literal []
    instead of the findings it had collected, so every style defect passed in
    silence until a probe doctored the drawing and nothing fired; this one
    returns what it finds, and the fill set includes INK because text fills
    too."""
    bad = []
    fills = set(re.findall(r'fill="(var\(--[a-z-]+\))"', svg))
    if fills != {INK, MIST, SUBTLE, WITNESS}:
        bad.append("%s: the plate fills with %s, and only the library's own "
                   "tokens may appear" % (name, sorted(fills)))
    strokes = set(re.findall(r'stroke="(var\(--[a-z-]+\))"', svg))
    if strokes != {MIST, WITNESS}:
        bad.append("%s: the plate strokes with %s, and only the nodes' "
                   "outline and the two paths may stroke"
                   % (name, sorted(strokes)))
    wit_lines = len(re.findall(r'<line [^>]*stroke="%s"' % re.escape(WITNESS),
                               svg))
    if wit_lines != 4:
        bad.append("%s: %d witness lines drawn for the four segments the "
                   "agent's path needs" % (name, wit_lines))
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

    The agent's path carries the plate's meaning, so it is held to the 3:1 a
    graphic needs; every text clears 4.5:1."""
    bad = []
    themes = {
        "light": {"canvas": "#FFFFFF", "subtle": "#FAFAFA", "ink": "#171717",
                  "mist": "#6E6A66", "witness": "#D93A3A"},
        "dark": {"canvas": "#0A0A0A", "subtle": "#141414", "ink": "#EDEDED",
                 "mist": "#A5A19B", "witness": "#4DA3FF"},
    }
    for theme, t in themes.items():
        for colour, what in (("mist", "chat's pass and the nodes' outline, "
                                    "graphics carrying context"),
                             ("witness", "the agent's path")):
            for ground in ("canvas", "subtle"):
                ratio = contrast(t[colour], t[ground])
                if ratio < 3.0:
                    bad.append("%s theme, %s on %s: %.2f:1, under 3:1, and %s"
                               % (theme, colour, ground, ratio, what))
        for colour, what in (("ink", "the nodes' text"),
                             ("mist", "the path labels and the footnotes")):
            ratio = contrast(t[colour], t["canvas"])
            if ratio < 4.5:
                bad.append("%s theme, %s on canvas: %.2f:1, under 4.5, and %s "
                           "is text" % (theme, colour, ratio, what))
    return bad


def self_test() -> int:
    bad = []
    rendered = {}
    shipped = {p: (p.read_bytes() if p.is_file() else None)
               for p in (OUT / "agent-loop-wide.svg",
                         OUT / "agent-loop-tall.svg")}
    scratch = tempfile.TemporaryDirectory()
    for spec, name, svg, path in write(Path(scratch.name)):
        rendered[name] = svg
        floor = FLOOR_TALL if name == "tall" else FLOOR_WIDE
        bad += check_nodes(spec, name, svg)
        bad += check_chat(spec, name, svg)
        bad += check_loop(spec, name, svg)
        bad += seg_label_clearance(spec, name, svg)
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
        print("agent-loop self-test FAILED:")
        for line in bad:
            print("  " + line)
        return 1
    print("agent-loop self-test ok: four node boxes with their own text "
          "inside them, chat's single pass from the question's edge to the "
          "answer's touching nothing between, the agent's path of four "
          "segments with every start and tip on a node's edge, the tool "
          "touched once in and once out, the model touched four times with "
          "exactly two ways out - the branch that is the agency - no label on "
          "a path or a box, both variants making the same claims, no hex "
          "colour, and every colour clearing its bar in both themes")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    for _spec, _name, svg, path in write():
        print("%s  %s B" % (path.name, format(len(svg.encode("utf-8")), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
