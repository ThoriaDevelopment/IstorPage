#!/usr/bin/env python3
"""Generate the questions act's plate: what stays inside your machine.

    python Source/tools/make-boundary.py

Writes Source/figures/boundary-wide.svg and boundary-tall.svg

WHY THIS ACT. `#questions` is the only act on the page with no illustration at
all: seven disclosures, 323 words, and nothing to look at. It is also where a
reader asks the page's own hardest questions, and four of the seven answers are
the same answer from four directions — what runs locally, what does not leave,
what it needs installed, and what it cannot do yet. A diagram of the boundary
shows that in one look; the prose then has somewhere to point instead of
somewhere to repeat itself.

EVERY LABEL IS A PHRASE THAT IS ALREADY ON THE PAGE. Nothing here is new copy
and nothing is a claim the act does not make in words a reader can check: "your
library", "ollama or llama.cpp", "the model you choose", "web research", "off
until you turn it on", "no account, no key". That is the rule this project
applies to its generated plates — the drawing is arithmetic on what the page
says, not illustration on top of it — and it is why this figure can be a picture
of the argument without becoming a second place the argument lives.

THE BOUNDARY IS THE FIGURE. A hairline rounded rectangle labelled "your machine",
with the three things that run inside it in a row (or a column, on a phone), and
one wire leaving it: web research, crossed out in `--azure`, the figure's single
accent and its single assertion. Everything else is `--rule` for the frame and
`--ink`/`--ink-2` for what is named, so the eye reads the crossing first and the
contents second, in that order, which is the order the act answers in.

THREE VARIANTS, and each one is a different diagram rather than a squashed copy:
WIDE puts the stack beside the wall, MID keeps the row and moves the stack above
it, TALL reads the three nodes downward with the wire leaving the top. They exist
because the plate's type is in user units and therefore scales with the figure,
which the 2026-09-20 type sweep measured: the wide drawing is 704 units across, so
at a 641px viewport its glosses rendered at 9.4px and at 768, a tablet in
portrait, at 10.8. The site's floor is 11. Same reason the etymology plate and
the exhibits art-direct their phone crops: a diagram is not exempt from the width
it is read at.
"""

import math
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

# The three things that run on the machine, in the order the page introduces them,
# and the one thing that does not.
INSIDE = [
    ("your library", "the documents you gave it"),
    ("istor", "search, reading and answers"),
    ("ollama or llama.cpp", "the model you choose"),
]
OUTSIDE = "web research"
CROSS = "off until you turn it on"
NOTE = "no account, no key"
BOUNDARY = "your machine"

# EVERY STRING'S RENDERED WIDTH, in user units, keyed by the string and the size it
# is drawn at. Measured in the browser off the rendered page -- ink extents through
# `camera.py measure` with .improvement/tools/q-qsvg.js -- and not estimated from a
# character table, because the whole layout below is built out of these numbers.
#
# Why they are a hard requirement rather than a comment: this figure's boxes are
# sized by their labels, and the first version of it drew every label from the box's
# centre with an anchor the stylesheet never set, so the widest label in each pair
# ran out through the right wall of its own box -- by 60 units in the tall variant,
# and 59 in the wide one. It was shipped for two passes because it reads as a style
# at a glance: a figure whose text does not line up looks loosely typeset, not
# broken. A label with no entry here has no measured width, so tw() refuses it, and
# the refusal is the reminder to spend one command re-measuring.
MEASURED = {
    ("your library", 15.0): 81.3,
    ("the documents you gave it", 11.5): 144.8,
    ("istor", 15.0): 31.3,
    ("search, reading and answers", 11.5): 156.9,
    ("ollama or llama.cpp", 15.0): 137.8,
    ("the model you choose", 11.5): 121.6,
    ("web research", 15.0): 96.4,
    ("off until you turn it on", 11.5): 116.3,
    ("no account, no key", 11.5): 103.8,
    ("your machine", 12.5): 83.7,
    # The tall plate's own step, measured at the sizes T_TALL_* below. The phone
    # column is narrower than the drawing, so this variant's type has to be bigger
    # in user units to land at the same pixels -- which is why the tall plate's
    # boxes are wider than the wide plate's for the same words.
    ("your library", 17.0): 91.9,
    ("istor", 17.0): 35.7,
    ("ollama or llama.cpp", 17.0): 156.2,
    ("web research", 17.0): 109.2,
    # 2026-09-23: the tall subs stepped 13.5 -> 14.5. The earlier note measured
    # the plate's 320px render at 0.824 of its units; the real floor is lower -
    # a 17px scrollbar (the audit's own iframe shows one) takes the content to
    # 303, the clamp keeps the gutter at 20 a side, and the tall svg rendered
    # 263 wide: scale 0.774, where 13.5-unit subs landed at 10.45px, UNDER the
    # 11px type floor the contrast audit now asserts. 14.5 lands at 11.2 there
    # and at 14.5px from 390 up. The five widths below are measured live in the
    # rendered page (wide variant at 11.5, scaled per unit), not estimated.
    ("the documents you gave it", 14.5): 177.0,
    ("search, reading and answers", 14.5): 191.8,
    ("the model you choose", 14.5): 148.2,
    ("off until you turn it on", 14.5): 142.0,
    ("no account, no key", 14.5): 126.4,
}

# What the layout is allowed to assume: how much air a label keeps inside its box,
# the gap between boxes, and how much room the widest outside string needs from the
# right edge of the plate.
# The row's air. PAD is what a label keeps inside its own box and GAP is between
# boxes; both came DOWN on 2026-09-20 (12 and 22 to 10 and 18) for a measured
# reason rather than a taste one: the plate's type is in user units, so the whole
# figure's legibility is set by how wide it is in those units, and the wide
# composition could not be read at 1:1 in any column narrower than ~630px. Ten
# units of air around a label is not tight -- the box is 62 tall and the type is
# 15 -- and it buys the mid variant its 1:1 width.
PAD, GAP, EDGE = 10.0, 18.0, 8.0
PAD_ROW = 14.0        # air between the boundary's walls and the first/last box
LABEL_GAP = 10.0      # between the wire's head and the label stack beside it

# Type. The wide plate is read at 1:1 in a 736px column, the tall one in a 340px
# one, so the tall variant steps its type UP in user units to land at the same
# pixels. Sizes are the site's own label/body scale, not new steps.
T_NODE = 15.0
T_SUB = 11.5
T_LABEL = 12.5
T_NOTE = 11.5
TALL_BW = 328.0  # the tall boundary's width, quoted here so self_test() can use it
# The tall plate's type, one step up from the wide plate's. The 2026-09-20
# measurement had the 320px render at 0.824 of user units; the real floor is
# 0.774 (a 17px scrollbar plus the gutter clamp's 20px floor), so the subs were
# stepped again on 2026-09-23 - see the note in MEASURED. Node 17 lands at
# 13.2px at that floor and 17px from 390 up; sub 14.5 lands at 11.2 and 14.5.
T_TALL_NODE = 17.0
T_TALL_SUB = 14.5


def tw(s, size):
    """The measured width of a string at a size, or a loud refusal.

    Called for every string that is drawn, so the layout cannot be built from a
    guess: a missing entry names the string, the size, and the command that
    measures it.
    """
    try:
        return MEASURED[(s, float(size))]
    except KeyError:
        raise SystemExit(
            f"make-boundary: {s!r} at {size} has no measured width.\n"
            "  Measure it before shipping it: python .improvement/tools/camera.py "
            "measure --width 1440 --expr-file .improvement/tools/q-qsvg.js")


def fits(s, size, box_w):
    """Whether a label keeps PAD inside a box of this width, on both sides."""
    return tw(s, size) + PAD * 2 <= box_w + 1e-9


def fits_width(s, size, width, slack=8.0):
    """Whether a centred string keeps `slack` clear of both edges of `width`."""
    return tw(s, size) <= width - slack + 1e-9


def rounded(x, y, w, h, r, cls):
    return (f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="{r:.1f}"/>')


def node(cx, cy, w, h, title, sub, t_node, t_sub):
    """A named box: the term in --ink, the gloss in --ink-2 under it.

    text-anchor is an ATTRIBUTE here, not something the page's stylesheet is asked
    for, because it is geometry: the box is centred on cx and the label has to be
    centred on cx too. Left to the stylesheet, a rule that is missing or renamed
    turns into text standing outside its own box, which is what shipped first.
    """
    for label, size in ((title, t_node), (sub, t_sub)):
        if label and not fits(label, size, w):
            raise SystemExit(f"make-boundary: {label!r} is {tw(label, size):.1f} wide "
                             f"and the box around it is {w:.1f}. Widen the box or "
                             "shorten the label -- do not ship it overlapping.")
    out = [rounded(cx - w / 2, cy - h / 2, w, h, 10, "bnd-box"),
           f'<text class="bnd-name" x="{cx:.1f}" y="{cy - (3 if sub else -4):.1f}" '
           f'text-anchor="middle" font-size="{t_node}">{title}</text>']
    if sub:
        out.append(f'<text class="bnd-sub" x="{cx:.1f}" y="{cy + 15:.1f}" '
                   f'text-anchor="middle" font-size="{t_sub}">{sub}</text>')
    return out


def arrow(x1, y1, x2, y2):
    """A hairline with a head at the far end, as ONE path.

    One path and not a line plus a triangle: two elements can be nudged apart by a
    later edit and a wire whose head has drifted off the wire is the kind of thing
    that survives review, because it still looks deliberate. The head is two short
    strokes back from the tip at +/- 2.6 radians, which is a 30-degree barb.
    """
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 6.0
    left = (x2 + head * math.cos(ang + 2.6), y2 + head * math.sin(ang + 2.6))
    right = (x2 + head * math.cos(ang - 2.6), y2 + head * math.sin(ang - 2.6))
    return (f'<path class="bnd-wire" d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} '
            f'M{left[0]:.1f} {left[1]:.1f} L{x2:.1f} {y2:.1f} '
            f'L{right[0]:.1f} {right[1]:.1f}"/>')


def elbow(pts, last_to=None):
    """A wire that turns. `pts` are the corners; the head lands on the last one.

    The wire leaves the app's TOP edge rather than its right edge, because the
    right edge already carries the arrow to the runtime and two wires sharing a
    line reads as one wire with a mistake on it.
    """
    d = [f'M{pts[0][0]:.1f} {pts[0][1]:.1f}']
    for x, y in pts[1:]:
        d.append(f'L{x:.1f} {y:.1f}')
    head = _head(pts[-2], pts[-1])
    return f'<path class="bnd-wire" d="{" ".join(d)} {head}"/>'


def _head(a, b):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    size = 6.0
    left = (b[0] + size * math.cos(ang + 2.6), b[1] + size * math.sin(ang + 2.6))
    right = (b[0] + size * math.cos(ang - 2.6), b[1] + size * math.sin(ang - 2.6))
    return (f'M{left[0]:.1f} {left[1]:.1f} L{b[0]:.1f} {b[1]:.1f} '
            f'L{right[0]:.1f} {right[1]:.1f}')


def cross(cx, cy, size=7.0):
    """The figure's one assertion: the wire that is not connected."""
    return (f'<path class="bnd-cross" d="M{cx - size:.1f} {cy - size:.1f} '
            f'L{cx + size:.1f} {cy + size:.1f} '
            f'M{cx + size:.1f} {cy - size:.1f} L{cx - size:.1f} {cy + size:.1f}"/>')


def row_widths():
    """The three box widths, and the boundary that holds them with its own air.

    The wall is the row plus PAD_ROW at each end, and the boxes are the measured
    labels plus PAD: the figure's width is arithmetic on its text, which is why a
    third variant is a rearrangement rather than a rescale.
    """
    widths = [max(tw(title, T_NODE), tw(sub, T_SUB)) + PAD * 2
              for title, sub in INSIDE]
    return widths, sum(widths) + GAP * 2 + PAD_ROW * 2


def wide_width():
    """Everything the wide plate needs: wall, wire, stack beside it, and edge."""
    _, bw = row_widths()
    return 6.0 + bw + LABEL_GAP + max(tw(OUTSIDE, T_NODE), tw(CROSS, T_SUB)) + EDGE


def wide(W=None, H=250.0):
    """The three nodes in a row, the wire leaving the top, the stack beside it.

    Every x in here is derived from the measured text widths above, so the figure
    is sized by its labels rather than the labels being squeezed into a guess, and
    W defaults to the width the content actually needs: a viewBox with slack in it
    is a figure that scales down for no reason, and scaling down is what makes a
    diagram's type unreadable. W is a parameter only so self_test() can ask for a
    plate that has to be refused.
    """
    W = wide_width() if W is None else W
    bx, by, bh = 6.0, 40.0, 150.0
    widths, row = row_widths()
    # The row keeps PAD_ROW from the walls rather than the PAD a label keeps from
    # its box: the boundary's own label sits in the header band above the row, so
    # nothing here needs to clear it, and every unit spent on that air is a unit the
    # labels outside the wall do not have.
    bw = row + PAD_ROW * 2
    cy = by + bh / 2 + 6
    body = [rounded(bx, by, bw, bh, 18, "bnd-line"),
            f'<text class="bnd-label" x="{bx + 18:.1f}" y="{by + 22:.1f}">{BOUNDARY}</text>']
    xs = [bx + PAD_ROW + widths[0] / 2]
    for i in range(1, 3):
        xs.append(xs[-1] + widths[i - 1] / 2 + GAP + widths[i] / 2)
    for (title, sub), x, w in zip(INSIDE, xs, widths):
        body += node(x, cy, w, 62.0, title, sub, T_NODE, T_SUB)
    for i in range(2):
        body.append(arrow(xs[i] + widths[i] / 2 + 6, cy, xs[i + 1] - widths[i + 1] / 2 - 6, cy))
    # The wire: out of the app's top edge, right, over the boundary's edge and off
    # to the node outside. The cross sits ON the boundary, where the wire leaves the
    # machine, which is the claim: this is the crossing that does not happen.
    wy = 18.0
    # The stop is set by the label stack, and the wire takes the space that is left:
    # the plate is the width of its longest string, so the wire yields rather than the
    # copy running off the plate. On this text it ends 17.3 units past the wall, which
    # is enough for the head to read as pointing at what is outside.
    stack = max(tw(OUTSIDE, T_NODE), tw(CROSS, T_SUB))
    wire_end = min(bx + bw + 22.0, W - EDGE - LABEL_GAP - stack)
    label_x = wire_end + LABEL_GAP
    # The one thing that can genuinely break here, and the one check worth having:
    # if the row grows, the wire can end up with no run outside the boxes and the
    # head becomes a mark ON the runtime box, which reads as a different sentence.
    # A guard for the label stack would be decoration: `wire_end` is a minimum that
    # keeps the labels inside the plate by construction, whichever term wins.
    if wire_end <= xs[2] + widths[2] / 2 + 8.0:
        raise SystemExit(
            f"make-boundary: the wire ends at {wire_end:.1f} but the last box ends at "
            f"{xs[2] + widths[2] / 2:.1f}. The row has grown out of the plate; "
            "shorten a label or widen the viewBox.")
    body.append(elbow([(xs[1], cy - 31.0), (xs[1], wy), (wire_end, wy)]))
    body.append(cross(xs[1], by))
    body.append(f'<text class="bnd-outside" x="{label_x:.1f}" y="{wy + 5:.1f}" '
                f'font-size="{T_NODE}">{OUTSIDE}</text>')
    body.append(f'<text class="bnd-sub" x="{label_x:.1f}" y="{wy + 24:.1f}" '
                f'font-size="{T_SUB}">{CROSS}</text>')
    body.append(f'<text class="bnd-claim" x="{bx:.1f}" y="{H - 16:.1f}" '
                f'font-size="{T_NOTE}">{NOTE}</text>')
    return W, H, body


def mid():
    """The three nodes in a row, the stack ABOVE the wall. Why a third one:

    Measured, not assumed. The wide plate is 704 units of drawing, so in a column
    narrower than that it scales down and its type scales with it: at a 641px
    viewport its 15px names render at 12.3 and its 11.5px glosses at 9.4, and at
    768, which is a tablet in portrait, 10.8. The page's floor for anything a
    reader has to read is 11. The tall plate is legible at those widths but it is
    the COLUMN composition, and a 340-wide column drawing in a 720-wide one is a
    stamp in a field, so the row stays a row and the one part that needed the wall's
    flank moves above it. The wire could not follow it up and then turn: it leaves
    the app's top edge and rises, which is the tall plate's arrangement borrowed
    whole, and the cross stays on the wall where the wire pierces it.
    """
    _, bw = row_widths()
    W, H = 6.0 + bw + 6.0, 300.0
    widths, _ = row_widths()
    bx, by, bh = 6.0, 96.0, 150.0
    cy = by + bh / 2 + 6
    stack_x = bx + PAD_ROW + widths[0] / 2 + GAP + widths[1] / 2
    stack = max(tw(OUTSIDE, T_NODE), tw(CROSS, T_SUB))
    for label, size in ((OUTSIDE, T_NODE), (CROSS, T_SUB), (NOTE, T_NOTE)):
        if not fits_width(label, size, bw):
            raise SystemExit(f"make-boundary: {label!r} is {tw(label, size):.1f} wide on "
                             f"a {bw:.0f} boundary; the mid plate cannot hold it.")
    body = [rounded(bx, by, bw, bh, 18, "bnd-line"),
            f'<text class="bnd-label" x="{bx + 18:.1f}" y="{by + 22:.1f}">{BOUNDARY}</text>']
    xs = [bx + PAD_ROW + widths[0] / 2]
    for i in range(1, 3):
        xs.append(xs[-1] + widths[i - 1] / 2 + GAP + widths[i] / 2)
    for (title, sub), x, w in zip(INSIDE, xs, widths):
        body += node(x, cy, w, 62.0, title, sub, T_NODE, T_SUB)
    for i in range(2):
        body.append(arrow(xs[i] + widths[i] / 2 + 6, cy, xs[i + 1] - widths[i + 1] / 2 - 6, cy))
    # The stack sits above the wire's head, which is above the wall's top edge, so
    # outside is still outside at every width -- the one relationship the figure has.
    body.append(arrow(xs[1], cy - 31.0, xs[1], 52.0))
    body.append(cross(xs[1], by))
    body.append(f'<text class="bnd-outside" x="{stack_x:.1f}" y="16.0" '
                f'text-anchor="middle" font-size="{T_NODE}">{OUTSIDE}</text>')
    body.append(f'<text class="bnd-sub" x="{stack_x:.1f}" y="35.0" '
                f'text-anchor="middle" font-size="{T_SUB}">{CROSS}</text>')
    body.append(f'<text class="bnd-claim" x="{bx:.1f}" y="{H - 16:.1f}" '
                f'font-size="{T_NOTE}">{NOTE}</text>')
    return W, H, body


def tall():
    """340x430: the same three nodes downward, the wire leaving the top."""
    W, H = 340.0, 430.0
    bx, by, bw, bh = 6.0, 92.0, TALL_BW, 320.0
    body = [rounded(bx, by, bw, bh, 18, "bnd-line"),
            f'<text class="bnd-label" x="{bx + 16:.1f}" y="{by + 24:.1f}">{BOUNDARY}</text>']
    rows = [by + 74.0, by + 168.0, by + 262.0]
    for (title, sub), y in zip(INSIDE, rows):
        w = min(bw - 36.0, max(tw(title, T_TALL_NODE), tw(sub, T_TALL_SUB)) + PAD * 2)
        body += node(bx + bw / 2, y, w, 62.0, title, sub, T_TALL_NODE, T_TALL_SUB)
    for i in range(2):
        body.append(arrow(bx + bw / 2, rows[i] + 31.0, bx + bw / 2, rows[i + 1] - 33.0))
    # The wire leaves the boundary's TOP: outside is above, inside is below, which
    # is the one relationship the figure has to keep at every width. Its labels are
    # centred on the same axis as the boxes, so everything here shares one centre.
    for label, size in ((OUTSIDE, T_TALL_NODE), (CROSS, T_TALL_SUB), (NOTE, T_TALL_SUB)):
        if not fits_width(label, size, bw):
            raise SystemExit(f"make-boundary: {label!r} is {tw(label, size):.1f} wide on "
                             f"a {bw:.0f} boundary; the tall plate cannot hold it.")
    body.append(arrow(bx + bw / 2, by - 4.0, bx + bw / 2, 56.0))
    body.append(cross(bx + bw / 2, by))
    body.append(f'<text class="bnd-outside" x="{bx + bw / 2:.1f}" y="26.0" '
                f'text-anchor="middle" font-size="{T_TALL_NODE}">{OUTSIDE}</text>')
    body.append(f'<text class="bnd-sub" x="{bx + bw / 2:.1f}" y="46.0" '
                f'text-anchor="middle" font-size="{T_TALL_SUB}">{CROSS}</text>')
    body.append(f'<text class="bnd-claim" x="{bx + bw / 2:.1f}" y="{H - 12:.1f}" '
                f'text-anchor="middle" font-size="{T_TALL_SUB}">{NOTE}</text>')
    return W, H, body


def write(name, W, H, body, title):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}"\n'
           f'     class="bnd bnd-{name}" role="img" focusable="false"\n'
           f'     aria-labelledby="bnd-{name}-title">\n'
           f'  <title id="bnd-{name}-title">{title}</title>\n'
           '  <!-- Generated by Source/tools/make-boundary.py -- do not hand-edit.\n'
           '       Every label in it is a phrase the act already uses in words. -->\n'
           + "\n".join("  " + line for line in body) + "\n</svg>\n")
    (FIG / f"boundary-{name}.svg").write_bytes(svg.encode("utf-8"))
    print(f"  boundary-{name}.svg  {len(svg)} B  ({W:.0f}x{H:.0f})")


def self_test():
    """Prove that each refusal refuses, and that the shipped layout passes them.

    Every check in this file is called here once with an input that has to fail and
    once with the real one, because a guard that fires on everything is as useless
    as a guard that fires on nothing, and only one of the two is easy to notice.
    """
    checks = []

    def refuses(label, fn):
        try:
            fn()
        except SystemExit:
            checks.append((label, True))
        else:
            checks.append((label, False))

    def allows(label, fn):
        try:
            fn()
        except SystemExit as exc:
            checks.append((f"{label} -- refused: {exc}", False))
        else:
            checks.append((label, True))

    tight = tw("your library", T_NODE) + PAD * 2
    refuses("tw() refuses a string nobody has measured",
            lambda: tw("a phrase no one has measured", T_NODE))
    refuses("node() refuses a label that runs out of its box",
            lambda: node(100.0, 100.0, tight - 1.0, 62.0, "your library", "",
                         T_NODE, T_SUB))
    allows("node() allows a label exactly PAD inside its box",
           lambda: node(100.0, 100.0, tight, 62.0, "your library", "",
                        T_NODE, T_SUB))
    refuses("fits_width() refuses a string wider than the plate it sits on",
            lambda: fits_width("your library", T_NODE, 60.0) or _raise("it fit"))
    allows("fits_width() allows the outside stack on the tall plate",
           lambda: fits_width(OUTSIDE, T_TALL_NODE, TALL_BW) or _raise("it did not fit"))
    refuses("wide() refuses a plate too narrow to run the wire outside the row",
            lambda: wide(W=560.0))
    allows("wide() builds the shipped plate", lambda: wide())
    allows("mid() builds the shipped plate", lambda: mid())
    allows("tall() builds the shipped plate", lambda: tall())

    bad = [name for name, ok in checks if not ok]
    for name in bad:
        print(f"  FAIL  {name}")
    print(f"  self-test: {len(checks) - len(bad)}/{len(checks)}")
    return 1 if bad else 0


def _raise(why):
    """Turn a boolean check into the SystemExit shape the other guards use."""
    raise SystemExit(why)


def main():
    W, H, body = wide()
    write("wide", W, H, body,
          "A diagram of one machine: your library, istor, and ollama or llama.cpp run "
          "inside a boundary labelled your machine, and the only wire leaving it, web "
          "research, is crossed out and marked off until you turn it on. No account, "
          "no key.")
    W, H, body = mid()
    write("mid", W, H, body,
          "The same diagram for a narrower column: your library, istor, and ollama or "
          "llama.cpp inside a boundary labelled your machine, and web research above "
          "it as the only wire leaving, crossed out and marked off until you turn it "
          "on. No account, no key.")
    W, H, body = tall()
    write("tall", W, H, body,
          "The same diagram read downward: your library, istor, and ollama or llama.cpp "
          "inside a boundary labelled your machine, and web research as the only wire "
          "leaving it, crossed out and marked off until you turn it on.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    main()
