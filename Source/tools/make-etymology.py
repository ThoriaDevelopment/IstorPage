"""Generate the name act's plate: one root, three descendants.

    python Source/tools/make-etymology.py

Writes Source/figures/etymology.svg and Source/figures/etymology-tall.svg

WHY THIS EXISTS. "ἵστωρ" is the act where the page says what it is named after, and
until now it was the one content act with no visual at all: two paragraphs and a
word. The paragraph it replaces already told this story in prose, and prose is the
wrong instrument for a descent. Four words in a line, one of them Greek, is
something the eye can take in at once, and it is the page's most ownable fact: the
tool is named after the person who was there, and the same root that named the
witness also named "wit".

TWO VARIANTS, and the swap is by width rather than by density, because the tall one
is not a scaled-down copy of the wide one. The wide plate is a bracket: a rail with
three branches, words stacked in a column, because a desktop column has height to
spend. A phone does not, and a 40%-scale diagram with 5px glosses in it is not that
variant, it is a photograph of it. So the tall plate is a LEDGER: the same four words
and the same descent, with each gloss set beside its word instead of under it, which
is the shape that fits a narrow column at full size. The site art-directs its bitmaps
for exactly this reason, and an SVG does not escape the reason by being scalable.

THE BOX IS THE SIZE OF THE THING. The wide plate is 540 units across because that is
where its content ends, and it is displayed at about one to one: the act's text column
is 66ch, so a word set at 26 units arrives at 26px next to a 15px paragraph, which is
the hierarchy this act wants. The first draft was 780 units with the same content in
it, which left 40% of the figure empty and read as a diagram that had lost its right
half rather than as a plate. A figure's viewBox is a measurement, not a canvas size.

ARITHMETIC AND INK. Every position below is a number derived from the row pitch, not
a hand-placed nudge, so a change to the pitch moves the nodes with it. Two inks for
text and two for structure, all four already in the palette:

  * words --ink, the page's own text ink, and the Greek at 46px against the Latin
    and English at 26px, because it is the destination;
  * glosses --ink-2 at the page's own label size (13px), which the token list
    documents as ">= 4.5:1 on --paper" and which the plate needs: a gloss is TEXT,
    and --ink-3 (the graphic ink, 3.12:1) would be a caption nobody can read. The
    ring figure uses --ink-3 for its 355 holes because those are a drawing;
    nothing here is. Lowercase with the page's middot separator, because this site
    does not letter-space capitals anywhere and a diagram is not the place to
    start: the window chips it already ships read "10 sources · 10 notes";
  * the rail and its stubs --rule, the page's hairline, because the descent is
    structure and the eye should read the words first;
  * exactly one --azure, the short rule under the Greek word. Sites mark their
    claims with their accent, and this figure makes exactly one.

The root is written with its asterisk, which is the convention for a reconstructed
form, and it is the same asterisk the prose uses. That is not decoration: it is the
honest mark for a word nobody wrote down.

ACCESSIBILITY. Unlike the ring plate this figure is not aria-hidden: it carries the
act's meaning rather than sitting behind it. It is a `role="img"` with a <title>,
and the act's prose still says the same thing in sentences, so a reader with a
screen reader loses the composition and nothing else.
"""

import gzip
from pathlib import Path

# --- the wide plate, read left to right -------------------------------------

W, H = 540, 330          # tight to its own content: see the note on dead space
RAIL_X = 250.0            # the stem everything branches from
ROOT_X = 24.0             # the root block, left of it
CONNECT_X = 168.0         # where the root's rule meets the stem
BRANCH_X = 310.0          # where each branch rule ends and its word begins
ROW1, ROW3 = 72.0, 248.0  # first and last branch
ROW_PITCH = (ROW3 - ROW1) / 2
NODE_R = 3.0

WORD_X = BRANCH_X + 30.0
ROOT_BASE = 172.0         # root baseline: its optical centre sits on the middle row
GLOSS_LIFT = 28.0


def rows():
    return [ROW1 + i * ROW_PITCH for i in range(3)]


wide = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="etym etym-wide" role="img" focusable="false"
     aria-labelledby="etym-wide-title">
  <title id="etym-wide-title">One root, *weyd-, to see, and three words that came
    from it: Latin videre, English wit, and the Greek word for a witness, which is
    the name of this tool.</title>
  <!-- One root, three descendants. Regenerate with Source/tools/make-etymology.py
       -- do not hand-edit. Positions are derived from the row pitch above; the
       ink/contrast argument is in that file's docstring. -->

  <g stroke="var(--rule)" stroke-width="1" fill="none">
    <path class="etym-rail" d="M{RAIL_X:g} {rows()[0]:g} V{rows()[2]:g}"/>
    <path class="etym-root-rule" d="M{CONNECT_X:g} {rows()[1]:g} H{RAIL_X:g}"/>
'''
for i, y in enumerate(rows()):
    wide += (f'    <path class="etym-branch" d="M{RAIL_X:g} {y:g} H{BRANCH_X:g}"/>\n')
wide += '  </g>\n\n  <g fill="var(--ink-3)">\n'
for i, y in enumerate(rows()):
    wide += (f'    <circle class="etym-node" cx="{RAIL_X:g}" cy="{y:g}" '
             f'r="{NODE_R:g}"/>\n')
wide += ('  </g>\n\n'
         '  <text class="etym-root" x="%g" y="%g">*weyd-</text>\n'
         '  <text class="etym-gloss" x="%g" y="%g">root · to see</text>\n'
         % (ROOT_X, ROOT_BASE, ROOT_X, ROOT_BASE + GLOSS_LIFT))


def wide_entry(y, word, gloss, cls="etym-word", size=26, lift=9, rule=False):
    out = (f'  <text class="{cls}" x="{WORD_X:g}" y="{y + lift:g}"'
           f' font-size="{size:g}">{word}</text>\n'
           f'  <text class="etym-gloss" x="{WORD_X:g}" y="{y + lift + GLOSS_LIFT:g}">'
           f'{gloss}</text>\n')
    if rule:
        out = (f'  <path class="etym-claim" d="M{WORD_X:g} {y + lift + 8:g} '
               f'H{WORD_X + 132:g}"/>\n') + out
    return out


wide += wide_entry(rows()[0], "videre", "latin · to see")
wide += wide_entry(rows()[1], "wit", "english · to know")
wide += wide_entry(rows()[2], "ἵστωρ", "greek · a witness", cls="etym-name",
                   size=46, lift=16, rule=True)
wide += '</svg>\n'

# --- the tall plate: the same descent as a ledger ----------------------------

TW, TH = 320, 430
T_RAIL_X = 16.0
T_STUB_END = 42.0
T_WORD_X = 52.0           # the words, in a column
T_GLOSS_X = 176.0         # the glosses, in a column of their own. Measured, not
# guessed: at 168 the Greek row's 44px name ran to 1.7px PAST the gloss column's
# left edge, so the tool's own name touched the words that gloss it. The column
# moved 8 units right and the name came down to 40, which leaves that row a 16px
# gap and the widest gloss a 24px right margin, both of them measured again
# afterwards rather than assumed.
T_ROOT_BASE = 60.0
T_TOP = 92.0              # the rail starts below the root row
T_ROWS = [120.0, 220.0, 320.0]


def tall_entry(y, word, gloss, cls="etym-word", size=28, lift=9, rule=False):
    """One row of the ledger: word in the left column, gloss in the right, both
    sitting on the row's line so the two columns read across."""
    out = (f'  <text class="{cls}" x="{T_WORD_X:g}" y="{y + lift:g}"'
           f' font-size="{size:g}">{word}</text>\n'
           f'  <text class="etym-gloss" x="{T_GLOSS_X:g}" y="{y + lift:g}">'
           f'{gloss}</text>\n')
    if rule:
        out = (f'  <path class="etym-claim" d="M{T_WORD_X:g} {y + lift + 10:g} '
               f'H{T_WORD_X + 108:g}"/>\n') + out
    return out


tall = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}"
     class="etym etym-tall" role="img" focusable="false"
     aria-labelledby="etym-tall-title">
  <title id="etym-tall-title">One root, *weyd-, to see, and three words that came
    from it: Latin videre, English wit, and the Greek word for a witness, which is
    the name of this tool.</title>
  <!-- The same descent as etymology.svg, read downward so a phone gets a
       composition rather than a scaled one. Regenerate with
       Source/tools/make-etymology.py -- do not hand-edit. -->

  <text class="etym-root" x="{T_WORD_X:g}" y="{T_ROOT_BASE:g}">*weyd-</text>
  <text class="etym-gloss" x="{T_GLOSS_X:g}" y="{T_ROOT_BASE:g}">root · to see</text>

  <g stroke="var(--rule)" stroke-width="1" fill="none">
    <path class="etym-rail" d="M{T_RAIL_X:g} {T_TOP:g} V{T_ROWS[2]:g}"/>
'''
for y in T_ROWS:
    tall += f'    <path class="etym-branch" d="M{T_RAIL_X:g} {y:g} H{T_STUB_END:g}"/>\n'
tall += '  </g>\n\n  <g fill="var(--ink-3)">\n'
for y in T_ROWS:
    tall += (f'    <circle class="etym-node" cx="{T_RAIL_X:g}" cy="{y:g}" '
             f'r="{NODE_R:g}"/>\n')
tall += '  </g>\n\n'
tall += tall_entry(T_ROWS[0], "videre", "latin · to see")
tall += tall_entry(T_ROWS[1], "wit", "english · to know")
tall += tall_entry(T_ROWS[2], "ἵστωρ", "greek · a witness", cls="etym-name",
                   size=40, lift=14, rule=True)
tall += '</svg>\n'

# Anchored to this file rather than to the shell's directory: this wrote to
# "../figures/" until 2026-09-20, which is right only from Source/tools and, from
# the repository root the docstring names, lands in the repository's parent.
FIG = Path(__file__).resolve().parent.parent / "figures"

# Every drawn string's measured width, for the extents gate: the gate
# recomputes each label's extent from these numbers and its start anchor, and
# holds it inside the viewBox. The words render in the display serif (Georgia
# metrics; the file is a Didot subset with the same widths at these sizes),
# the glosses in Inter at the page's label size - 13 units on the wide plate,
# 16 on the tall one below 430px, where the stylesheet moves the column 22
# units left to pay for the wider type (the note at .etym-tall .etym-gloss).
# The stylesheet's own media-query resize is why the tall glosses are measured
# at 16: that is the size they actually draw at in the plate's narrowest
# window, which is the width the cold read audits.
MEASURED = {
    ("*weyd-", 13.0): 46.0, ("root · to see", 13.0): 73.7,
    ("videre", 26.0): 71.2, ("latin · to see", 13.0): 74.9,
    ("wit", 26.0): 35.8, ("english · to know", 13.0): 104.9,
    ("ἵστωρ", 46.0): 118.0, ("greek · a witness", 13.0): 105.0,
    ("*weyd-", 16.0): 56.6, ("root · to see", 16.0): 90.7,
    ("videre", 28.0): 76.7, ("latin · to see", 16.0): 92.2,
    ("wit", 28.0): 38.5, ("english · to know", 16.0): 129.1,
    ("ἵστωρ", 34.0): 87.2, ("greek · a witness", 16.0): 129.2,
    # the tall plate's name at its viewBox size (40): the stylesheet's 34px
    # is a sub-430px render adjustment, and the gate holds the geometry the
    # viewBox states
    ("ἵστωρ", 40.0): 102.6,
}
for name, svg in (("etymology", wide), ("etymology-tall", tall)):
    out = FIG / ("%s.svg" % name)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("%-16s %5d bytes  (%d gzipped)  -> %s"
          % (name, len(svg.encode()), len(gzip.compress(svg.encode(), 9)),
             out.relative_to(out.parents[2])))

print("wide rows     %s" % ", ".join("%g" % y for y in rows()))
print("wide pitch    %g px between branches" % ROW_PITCH)
print("tall rows     %s" % ", ".join("%g" % y for y in T_ROWS))
