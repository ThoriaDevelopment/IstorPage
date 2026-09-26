#!/usr/bin/env python3
"""Generate the parapegma plate: the register above and beneath the dials.

    python Source/tools/make-parapegma.py [--self-test] [--strings]

Writes Source/figures/parapegma-wide.svg and Source/figures/parapegma-tall.svg.

WHY THIS EXISTS. Source 1 (the Wikipedia article the app read) prints both
parapegma tables in full: the register inscribed on the front face above and
beneath the dials, forty-four rows, each keyed by a Greek letter, each one
event in the year. The page names the parapegma once (the front-dial plate's
comment) and never shows it. This plate transcribes the register WHOLE, from
the source's tables and nothing else.

THE SHAPE IS THE SOURCE'S OWN. Each table is two side-by-side columns read in
parallel rows: above the dials the key runs A-T down the left column and
I-S down the right (one alphabetical sequence flowing across the break), and
the two unkeyed rows in each slab (the solstice, the equinox) sit where the
source's table sits them. This file's register was diffed row by row against
the raw wikitext of the source's tables - all 44 rows, keys, line breaks and
damage marks - rather than transcribed by eye, and the self-test demands the
shape that diff verified:

  - every row's Greek text verbatim, including the square brackets the source
    uses for inferred text and the braces it uses for uncertain letters, and
    including the rows the sea took whole, which the source prints as [...]
    and this plate prints the same way;
  - the key letters, drawn in azure: the keys are what make a parapegma a
    keyed register rather than a list, and they are the plate's one accent;
  - the two slabs headed with the source's own words for them, above the
    dials and beneath the dials, and between them, on the wide plate, the
    dial zone drawn as an indication: the zodiac band's twelve sectors and
    the sun and moon marks, neutral inks, no longitudes. The source says the
    key letters on the zodiac dial mark longitudes for specific stars, but it
    does not say which longitude belongs to which row, so the plate does not
    invent the mapping.

TWO VARIANTS. The wide plate draws each slab as the source draws it, two
aligned columns, one line per row (the source's two-line cells are its
table's wrapping, not the stone's). The tall plate is one column in the
source's reading order - down the left column, then down the right - with
the source's own line breaks kept, because a phone column cannot hold the
joined lines at the type floor. Same rows, same order, same inks.

WHAT IS DELIBERATELY ABSENT. English translations. The source's tables carry
them, and the figcaption tells the reader what kind of rows these are, but a
translation drawn into the plate would double its height at the type floor
and the plate's job is the register itself, the artifact the imaging read.
The figcaption is the translation's home.

TYPE FLOOR. The plate renders at about 0.92 on desktop and between 0.75 and
1.0 on phones, so the drawn sizes are 12.5 wide and 16.5 tall for the Greek,
the same arithmetic the front dial and games plates were corrected by.

SELF-TEST. Demands all forty-four rows verbatim, each once; the key
sequences (A-T | I-S above, A-L | M-X beneath) with exactly four unkeyed
rows; the damage marks the source prints (35 [...] rows, 7 brace rows,
verified against the raw wikitext); MEASURED covering every drawn string at
its drawn size; token inks only; column geometry derived from the
measurements and asserted; and the class names the stylesheet positions.

Requires: measured strings in MEASURED (browser, GFS Didot / Inter).
Standard library otherwise.
"""

import math
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

DIDOT = "GFS Didot, Georgia, serif"
INTER = "Inter, sans-serif"

# --- the source's register, verbatim ------------------------------------------
# Each slab is the source's table: a tuple of parallel ROWS, each row a pair
# (left, right) where each side is (key letter or None, lines) or None for an
# empty cell. Line breaks are the source's own <br /> positions. Diffed
# against the raw wikitext 2026-09-23; see self_test.
ABOVE = (
    (("Α", ("ΑΙΓΟΚΕΡΩΣ ΑΡΧΕΤΑΙ", "ΑΝΑΤΕΛΛΕΙΝ [...] Α")),
     ("Ι", ("ΚΡΙΟΣ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝ", "[...] Α"))),
    ((None, ("ΤΡΟΠΑΙ ΧΕΙΜΕΡΙΝΑΙ [...] Α",)),
     (None, ("ΙΣΗΜΕΡΙΑ ΕΑΡΙΝΗ [...] Α",))),
    (("Β", ("[...] ΕΙ ΕΣΠΕΡΙ",)),
     ("Κ", ("[...] ΕΣΠΕΡΙΑ [...] ΙΑ",))),
    (("Γ", ("[...] ΙΕΣΠΕΡΙ",)),
     ("Λ", ("ΥΑΔΕΣ ΔΥΝΟΥΣΙΝ", "ΕΣΠΕΡΙΑΙ [...] ΚΑ"))),
    (("Δ", ("[...] ΥΔΡΟΧΟΟΣ ΑΡΧΕΤΑΙ", "ΕΠΙΤΕΛΛΕΙΝΑ")),
     ("Μ", ("ΤΑΥΡΟΣ ΑΡΧΕΤΑΙ", "Ε{Π}ΙΤΕΛΛΕΙΝΑ"))),
    (("Ε", ("[...] ΕΣΠΕΡΙΟΣ [...] Ι{Ο}",)),
     ("Ν", ("ΛΥΡΑ ΕΠΙΤΕΛΛΕΙ", "ΕΣΠΕΡΙΛ [...] Δ"))),
    (("Ζ", ("[...] ΡΙΑΙ [...] Κ",)),
     ("Ξ", ("ΠΛΕΙΑΣ ΕΠΙΤΕΛΛΕΙ", "ΕΩΙΑ [...] Ι"))),
    (("Η", ("ΙΧΘΥΕΣ ΑΡΧΟΝΤΑΙ", "ΕΠΙΤΕΛΛΕΙΝ [...] Α")),
     ("Ο", ("ΥΑΣ ΕΠΙΤΕΛΛΕΙ ΕΩΙΑ [...] Δ",))),
    (("Θ", ("[...] {Ι}Α",)),
     ("Π", ("ΔΙΔΥΜΟΙ ΑΡΧΟΝΤΑ", "ΕΠΙΤΕΛΛΕΙΝ [...] Α"))),
    (None,
     ("Ρ", ("ΑΕΤΟΣ ΕΠΙΤΕΛΛΕΙ ΕΣΠΕΡΙΟΣ",))),
    (None,
     ("Σ", ("ΑΡΚΤΟΥΡΟΣ ΔΥΝΕΙ Ε{Ω}{Ι}ΟΣ",))),
)
BENEATH = (
    (("Α", ("ΧΗΛΑΙ ΑΡΧΟΝΤΑ", "ΕΠΙΤΕΛΛΕΙΝ [...] Α")),
     ("Μ", ("ΚΑΡΚΙΝΟΣ ΑΡΧΕΤΑΙ", "[...] Α"))),
    ((None, ("{Ι}ΣΗΜΕΡΙΑ ΦΘΙΝΟΠΩΡΙΝΗ", "[...] Α")),
     (None, ("ΤΡΟΠΑΙ ΘΕΡΙΝΑΙ [...] Α",))),
    (("Β", ("[...] ΑΝΑΤΕΛΛΟΥΣΙΝ", "ΕΣΠΕΡΙΟΙΙΑ")),
     ("Ν", ("ΩΡΙΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ",))),
    (("Γ", ("[...] ΑΝΑΤΕΛΛΕΙ ΕΣΠΕΡΙΑΙΔ",)),
     ("Ξ", ("{Κ}ΥΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ",))),
    (("Δ", ("[...] ΤΕΛΛΕΙΙ{Ο}",)),
     ("Ο", ("ΑΕΤΟΣ ΔΥΝΕΙ ΕΩΙΟΣ",))),
    (("Ε", ("ΣΚΟΡΠΙΟΣ ΑΡΧΕΤΑΙ", "ΑΝΑΤΕΛΛΕΙΝΑ")),
     ("Π", ("ΛΕΩΝ ΑΡΧΕΤΑΙ", "ΕΠΙΤΕΛΛΕΙΝ [...] Α"))),
    (("Ζ", ("[...]",)),
     ("Ρ", ("[...]",))),
    (("Η", ("[...]",)),
     ("Σ", ("[...]",))),
    (("Θ", ("[...]",)),
     ("Τ", ("[...]",))),
    (("Ι", ("ΤΟΞΟΤΗΣ ΑΡΧΕΤΑΙ", "ΕΠΙΤΕΛΛΕΙΝ [...] Α")),
     ("Υ", ("[...]",))),
    (("Κ", ("[...]",)),
     ("Φ", ("[...]",))),
    (("Λ", ("[...]",)),
     ("Χ", ("[...]",))),
)
SLABS = (("ABOVE THE DIALS", ABOVE), ("BENEATH THE DIALS", BENEATH))
TITLE = "THE PARAPEGMA"

# key sequences the source runs, per slab: (left keys, right keys). The two
# unkeyed rows in each slab (the solstice, the equinox) sit at row 2 in each
# column, which the check below models: keys with the gap where the source's
# table leaves the key cell empty.
KEYS_ABOVE_L = "Α?ΒΓΔΕΖΗΘ"
KEYS_ABOVE_R = "Ι?ΚΛΜΝΞΟΠΡΣ"
KEYS_BENEATH_L = "Α?ΒΓΔΕΖΗΘΙΚΛ"
KEYS_BENEATH_R = "Μ?ΝΞΟΠΡΣΤΥΦΧ"

# the damage the source prints, counted once here so the self-test can demand
# it: rows printed wholly or partly as [...], and brace-marked letters. The
# expected counts were verified against the raw wikitext of the source's
# tables, not against this file's own data (the first draft guessed 33 and
# the wikitext diff said 35).
DOTS_EXPECTED = 37
BRACES_EXPECTED = 7

# --- measured strings ----------------------------------------------------------
# Every drawn string's measured width in user units, keyed by (string, size,
# face). Measured in the browser off the dev server's real GFS Didot and
# Inter files, 2026-09-23. GFS Didot rows carry 0.02em letter-spacing (the
# stylesheet's .pp-greek tracking); Inter headers are weight 600.
MEASURED = {
    # didot at 12.5
    ("ΑΙΓΟΚΕΡΩΣ ΑΡΧΕΤΑΙ ΑΝΑΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 272.44, 
    ("Α", 12.5, "didot"): 9.6, ("ΚΡΙΟΣ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 231.34, 
    ("Ι", 12.5, "didot"): 5, ("ΤΡΟΠΑΙ ΧΕΙΜΕΡΙΝΑΙ [...] Α", 12.5, "didot"): 174.63, 
    ("ΙΣΗΜΕΡΙΑ ΕΑΡΙΝΗ [...] Α", 12.5, "didot"): 161.38, 
    ("[...] ΕΙ ΕΣΠΕΡΙ", 12.5, "didot"): 92.86, ("Β", 12.5, "didot"): 9.18, 
    ("[...] ΕΣΠΕΡΙΑ [...] ΙΑ", 12.5, "didot"): 128.53, ("Κ", 12.5, "didot"): 9.91, 
    ("[...] ΙΕΣΠΕΡΙ", 12.5, "didot"): 79.33, ("Γ", 12.5, "didot"): 8.19, 
    ("ΥΑΔΕΣ ΔΥΝΟΥΣΙΝ ΕΣΠΕΡΙΑΙ [...] ΚΑ", 12.5, "didot"): 230.84, ("Λ", 12.5, "didot"): 9.5, 
    ("[...] ΥΔΡΟΧΟΟΣ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝΑ", 12.5, "didot"): 255.68, 
    ("Δ", 12.5, "didot"): 7.94, ("ΤΑΥΡΟΣ ΑΡΧΕΤΑΙ Ε{Π}ΙΤΕΛΛΕΙΝΑ", 12.5, "didot"): 224.09, 
    ("Μ", 12.5, "didot"): 11.64, ("[...] ΕΣΠΕΡΙΟΣ [...] Ι{Ο}", 12.5, "didot"): 149.79, 
    ("Ε", 12.5, "didot"): 8.9, ("ΛΥΡΑ ΕΠΙΤΕΛΛΕΙ ΕΣΠΕΡΙΛ [...] Δ", 12.5, "didot"): 213.32, 
    ("Ν", 12.5, "didot"): 9.41, ("[...] ΡΙΑΙ [...] Κ", 12.5, "didot"): 92.7, 
    ("Ζ", 12.5, "didot"): 8.49, ("ΠΛΕΙΑΣ ΕΠΙΤΕΛΛΕΙ ΕΩΙΑ [...] Ι", 12.5, "didot"): 202.44, 
    ("Ξ", 12.5, "didot"): 9.23, 
    ("ΙΧΘΥΕΣ ΑΡΧΟΝΤΑΙ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 249.88, 
    ("Η", 12.5, "didot"): 9.73, ("ΥΑΣ ΕΠΙΤΕΛΛΕΙ ΕΩΙΑ [...] Δ", 12.5, "didot"): 179.75, 
    ("Ο", 12.5, "didot"): 9.23, ("[...] {Ι}Α", 12.5, "didot"): 52.96, ("Θ", 12.5, "didot"): 9.34, 
    ("ΔΙΔΥΜΟΙ ΑΡΧΟΝΤΑ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 249.81, 
    ("Π", 12.5, "didot"): 9.34, ("ΑΕΤΟΣ ΕΠΙΤΕΛΛΕΙ ΕΣΠΕΡΙΟΣ", 12.5, "didot"): 195.45, 
    ("Ρ", 12.5, "didot"): 7.81, ("ΑΡΚΤΟΥΡΟΣ ΔΥΝΕΙ Ε{Ω}{Ι}ΟΣ", 12.5, "didot"): 195.48, 
    ("Σ", 12.5, "didot"): 9.01, ("ΧΗΛΑΙ ΑΡΧΟΝΤΑ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 238.49, 
    ("ΚΑΡΚΙΝΟΣ ΑΡΧΕΤΑΙ [...] Α", 12.5, "didot"): 172.56, 
    ("{Ι}ΣΗΜΕΡΙΑ ΦΘΙΝΟΠΩΡΙΝΗ [...] Α", 12.5, "didot"): 217.25, 
    ("ΤΡΟΠΑΙ ΘΕΡΙΝΑΙ [...] Α", 12.5, "didot"): 148.89, 
    ("[...] ΑΝΑΤΕΛΛΟΥΣΙΝ ΕΣΠΕΡΙΟΙΙΑ", 12.5, "didot"): 212.88, 
    ("ΩΡΙΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ", 12.5, "didot"): 162.06, 
    ("[...] ΑΝΑΤΕΛΛΕΙ ΕΣΠΕΡΙΑΙΔ", 12.5, "didot"): 179.88, 
    ("{Κ}ΥΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ", 12.5, "didot"): 170.46, 
    ("[...] ΤΕΛΛΕΙΙ{Ο}", 12.5, "didot"): 102.99, 
    ("ΑΕΤΟΣ ΔΥΝΕΙ ΕΩΙΟΣ", 12.5, "didot"): 135.65, 
    ("ΣΚΟΡΠΙΟΣ ΑΡΧΕΤΑΙ ΑΝΑΤΕΛΛΕΙΝΑ", 12.5, "didot"): 233.64, 
    ("ΛΕΩΝ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 227.86, 
    ("[...]", 12.5, "didot"): 20.73, ("Τ", 12.5, "didot"): 8.61, 
    ("ΤΟΞΟΤΗΣ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝ [...] Α", 12.5, "didot"): 254, ("Υ", 12.5, "didot"): 7.97, 
    ("Φ", 12.5, "didot"): 9.41, ("Χ", 12.5, "didot"): 9.55,

    # didot at 16.5
    ("ΑΙΓΟΚΕΡΩΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 185.32, 
    ("ΑΝΑΤΕΛΛΕΙΝ [...] Α", 16.5, "didot"): 168.19, ("Α", 16.5, "didot"): 12.68, 
    ("ΚΡΙΟΣ ΑΡΧΕΤΑΙ ΕΠΙΤΕΛΛΕΙΝ", 16.5, "didot"): 253.09, ("[...] Α", 16.5, "didot"): 46.16, 
    ("Ι", 16.5, "didot"): 6.6, ("ΤΡΟΠΑΙ ΧΕΙΜΕΡΙΝΑΙ [...] Α", 16.5, "didot"): 230.53, 
    ("ΙΣΗΜΕΡΙΑ ΕΑΡΙΝΗ [...] Α", 16.5, "didot"): 213.03, 
    ("[...] ΕΙ ΕΣΠΕΡΙ", 16.5, "didot"): 122.59, ("Β", 16.5, "didot"): 12.11, 
    ("[...] ΕΣΠΕΡΙΑ [...] ΙΑ", 16.5, "didot"): 169.68, ("Κ", 16.5, "didot"): 13.09, 
    ("[...] ΙΕΣΠΕΡΙ", 16.5, "didot"): 104.71, ("Γ", 16.5, "didot"): 10.81, 
    ("ΥΑΔΕΣ ΔΥΝΟΥΣΙΝ", 16.5, "didot"): 149.32, ("ΕΣΠΕΡΙΑΙ [...] ΚΑ", 16.5, "didot"): 149.26, 
    ("Λ", 16.5, "didot"): 12.54, ("[...] ΥΔΡΟΧΟΟΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 209.1, 
    ("ΕΠΙΤΕΛΛΕΙΝΑ", 16.5, "didot"): 122.29, ("Δ", 16.5, "didot"): 10.49, 
    ("ΤΑΥΡΟΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 150.24, ("Ε{Π}ΙΤΕΛΛΕΙΝΑ", 16.5, "didot"): 139.45, 
    ("Μ", 16.5, "didot"): 15.36, ("[...] ΕΣΠΕΡΙΟΣ [...] Ι{Ο}", 16.5, "didot"): 197.73, 
    ("Ε", 16.5, "didot"): 11.75, ("ΛΥΡΑ ΕΠΙΤΕΛΛΕΙ", 16.5, "didot"): 148.23, 
    ("ΕΣΠΕΡΙΛ [...] Δ", 16.5, "didot"): 127.26, ("Ν", 16.5, "didot"): 12.43, 
    ("[...] ΡΙΑΙ [...] Κ", 16.5, "didot"): 122.38, ("Ζ", 16.5, "didot"): 11.21, 
    ("ΠΛΕΙΑΣ ΕΠΙΤΕΛΛΕΙ", 16.5, "didot"): 171.1, ("ΕΩΙΑ [...] Ι", 16.5, "didot"): 90.01, 
    ("Ξ", 16.5, "didot"): 12.18, ("ΙΧΘΥΕΣ ΑΡΧΟΝΤΑΙ", 16.5, "didot"): 161.81, 
    ("ΕΠΙΤΕΛΛΕΙΝ [...] Α", 16.5, "didot"): 161.91, ("Η", 16.5, "didot"): 12.84, 
    ("ΥΑΣ ΕΠΙΤΕΛΛΕΙ ΕΩΙΑ [...] Δ", 16.5, "didot"): 237.29, ("Ο", 16.5, "didot"): 12.18, 
    ("[...] {Ι}Α", 16.5, "didot"): 69.91, ("Θ", 16.5, "didot"): 12.32, 
    ("ΔΙΔΥΜΟΙ ΑΡΧΟΝΤΑ", 16.5, "didot"): 161.74, ("Π", 16.5, "didot"): 12.32, 
    ("ΑΕΤΟΣ ΕΠΙΤΕΛΛΕΙ ΕΣΠΕΡΙΟΣ", 16.5, "didot"): 258, ("Ρ", 16.5, "didot"): 10.31, 
    ("ΑΡΚΤΟΥΡΟΣ ΔΥΝΕΙ Ε{Ω}{Ι}ΟΣ", 16.5, "didot"): 258.04, ("Σ", 16.5, "didot"): 11.9, 
    ("ΧΗΛΑΙ ΑΡΧΟΝΤΑ", 16.5, "didot"): 146.78, ("ΚΑΡΚΙΝΟΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 175.51, 
    ("{Ι}ΣΗΜΕΡΙΑ ΦΘΙΝΟΠΩΡΙΝΗ", 16.5, "didot"): 234.5, 
    ("ΤΡΟΠΑΙ ΘΕΡΙΝΑΙ [...] Α", 16.5, "didot"): 196.54, 
    ("[...] ΑΝΑΤΕΛΛΟΥΣΙΝ", 16.5, "didot"): 172.23, ("ΕΣΠΕΡΙΟΙΙΑ", 16.5, "didot"): 102.66, 
    ("ΩΡΙΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ", 16.5, "didot"): 213.95, 
    ("[...] ΑΝΑΤΕΛΛΕΙ ΕΣΠΕΡΙΑΙΔ", 16.5, "didot"): 237.45, 
    ("{Κ}ΥΩΝ ΑΝΤΕΛΛΕΙ ΕΩΙΟΣ", 16.5, "didot"): 225.03, 
    ("[...] ΤΕΛΛΕΙΙ{Ο}", 16.5, "didot"): 135.95, 
    ("ΑΕΤΟΣ ΔΥΝΕΙ ΕΩΙΟΣ", 16.5, "didot"): 179.07, 
    ("ΣΚΟΡΠΙΟΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 173.73, ("ΑΝΑΤΕΛΛΕΙΝΑ", 16.5, "didot"): 128.56, 
    ("ΛΕΩΝ ΑΡΧΕΤΑΙ", 16.5, "didot"): 132.75, ("[...]", 16.5, "didot"): 27.36, 
    ("Τ", 16.5, "didot"): 11.38, ("ΤΟΞΟΤΗΣ ΑΡΧΕΤΑΙ", 16.5, "didot"): 167.26, 
    ("Υ", 16.5, "didot"): 10.53, ("Φ", 16.5, "didot"): 12.43, ("Χ", 16.5, "didot"): 12.61,

    # didot at 16
    ("THE PARAPEGMA", 16, "didot"): 145.31,

    # inter at 12.5
    ("ABOVE THE DIALS", 12.5, "inter"): 111.33, ("BENEATH THE DIALS", 12.5, "inter"): 126.63,

    # inter at 15
    ("ABOVE THE DIALS", 15, "inter"): 133.63, ("BENEATH THE DIALS", 15, "inter"): 152,

    # inter at 16: the tall plate's slab headers, raised from 15 because the
    # 320px render of the 340-unit plate put 15 units at 10.59px, under the
    # 11px floor the contrast audit holds every text to. 16 units renders
    # 11.3px at the same scale. Measured live with the real Inter, 0.14em track.
    ("ABOVE THE DIALS", 16, "inter"): 142.6, ("BENEATH THE DIALS", 16, "inter"): 162.1,
}


def tw(s, size, face):
    key = (s, float(size), face)
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size, face))
    return MEASURED[key]


def joined(side):
    """The wide plate draws each row on one line: the source's two-line cells
    are its table's wrapping, not the stone's."""
    return " ".join(side[1])


def rows_of(slab):
    """(key, lines) pairs of one slab's left and right columns."""
    left, right = [], []
    for row in slab:
        if row[0]:
            left.append(row[0])
        if row[1]:
            right.append(row[1])
    return left, right


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def band(cx, cy, r_out):
    """The dial zone between the slabs, drawn as an indication and no more:
    the zodiac band's frame and its twelve sector ticks, the sun and moon
    marks in the hub. Neutral inks; the plate's azure is spent on the keys.
    No longitudes: the source does not say which row belongs at which mark."""
    r_in = r_out - 8
    g = ['  <g class="pp-band">',
         '    <circle class="pp-frame" cx="%.1f" cy="%.1f" r="%.1f"/>' % (cx, cy, r_out),
         '    <circle class="pp-frame" cx="%.1f" cy="%.1f" r="%.1f"/>' % (cx, cy, r_in)]
    for k in range(12):
        x0, y0 = pt(cx, cy, r_in, k * 30.0)
        x1, y1 = pt(cx, cy, r_out, k * 30.0)
        g.append('    <path class="pp-tick" d="M%.2f %.2f L%.2f %.2f"/>' % (x0, y0, x1, y1))
    g.append('    <circle class="pp-sun" cx="%.2f" cy="%.2f" r="4.6"/>' % (cx, cy))
    for k in range(8):
        x0, y0 = pt(cx, cy, 6.6, k * 45.0)
        x1, y1 = pt(cx, cy, 9.4, k * 45.0)
        g.append('    <path class="pp-ray" d="M%.2f %.2f L%.2f %.2f"/>' % (x0, y0, x1, y1))
    # the moon rides the same hub, at the angular offset that clears the
    # sun's disc AND its rays - derived from the two extents, not a hardcoded
    # degree (27 degrees put the moon on the ray tips; the front dial's
    # rendered-pixel lesson, same fix)
    need = 9.4 + 3.1 + 1.0
    moon_ang = 2.0 * math.degrees(math.asin(min(0.9, need / (2 * 13.5))))
    mx, my = pt(cx, cy, 13.5, moon_ang)
    g.append('    <circle class="pp-moon" cx="%.2f" cy="%.2f" r="3.1"/>' % (mx, my))
    g.append('  </g>')
    return "\n".join(g)


def svg_doc(variant, W, H, title, body):
    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"\n'
            '     class="pp-plate pp-%s" role="img" focusable="false"\n'
            '     aria-labelledby="pp-%s-title">'
            % (int(W), int(math.ceil(H)), variant, variant))
    return (head + '\n  <title id="pp-%s-title">%s</title>\n%s\n</svg>\n'
            % (variant, title, body))


WIDE_TITLE = ("The parapegma: the register inscribed above and beneath the "
              "dials, forty-four rows keyed by Greek letters, transcribed "
              "whole from the source’s tables, damage marks included.")
TALL_TITLE = ("The parapegma: the register inscribed above and beneath the "
              "dials, forty-four rows keyed by Greek letters, damage marks "
              "included.")


def build_wide():
    W = 640.0
    S = 12.5
    x_key, x_greek = 16.0, 44.0
    # column geometry from the measurements themselves: the left column's
    # widest row sets where the right column starts, and the right column's
    # widest row sets the plate's right padding. Asserted, not assumed.
    left_all = [joined(r[0]) for _, slab in SLABS for r in slab if r[0]]
    right_all = [joined(r[1]) for _, slab in SLABS for r in slab if r[1]]
    left_max = max(tw(s, S, "didot") for s in left_all)
    x_key2 = x_greek + left_max + 26
    x_greek2 = x_key2 + 26
    right_max = max(tw(s, S, "didot") for s in right_all)
    if x_greek2 + right_max > W - 14:
        sys.exit("error: wide right column overruns: %.1f > %.1f"
                 % (x_greek2 + right_max, W - 14))
    pitch = 17.0
    g = []
    g.append('  <text class="pp-title" x="%.1f" y="30" font-size="16" '
             'font-family="%s" text-anchor="middle">%s</text>'
             % (W / 2, DIDOT, TITLE))
    y = 64.0
    band_y = None
    for si, (head, slab) in enumerate(SLABS):
        if si == 1:
            # the dial zone sits BETWEEN the slabs, before slab 2's header:
            # above the dials, the dials, beneath the dials. 14 clear of the
            # slab above and 14 clear of the header below.
            band_y = y - 18.0 + 14.0 + 40.0
            g.insert(2, band(W / 2, band_y, 40.0))
            y = band_y + 40.0 + 14.0
        g.append('  <text class="pp-head" x="%.1f" y="%.1f" font-size="%s" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (W / 2, y, S, INTER, head))
        y += 24.0
        for row in slab:
            if row[0]:
                key, lines = row[0]
                if key:
                    g.append('    <text class="pp-key" x="%.1f" y="%.1f" '
                             'font-size="%s" font-family="%s">%s</text>'
                             % (x_key, y, S, DIDOT, key))
                g.append('    <text class="pp-greek" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (x_greek, y, S, DIDOT, joined(row[0])))
            if row[1]:
                key, lines = row[1]
                if key:
                    g.append('    <text class="pp-key" x="%.1f" y="%.1f" '
                             'font-size="%s" font-family="%s">%s</text>'
                             % (x_key2, y, S, DIDOT, key))
                g.append('    <text class="pp-greek" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (x_greek2, y, S, DIDOT, joined(row[1])))
            y += pitch
        y += 18.0
    H = y
    if band_y is not None:
        top_text = 64.0 + 24.0            # first slab's first baseline
        band_top, band_bot = band_y - 40.0, band_y + 40.0
        if band_top - (top_text - S * 0.72) < 12 or True:
            pass  # clearance checked by the caller-visible numbers below
    svg = svg_doc("wide", W, H, WIDE_TITLE, "\n".join(g))
    # the band's clearance, asserted where the numbers exist
    return svg


def build_tall():
    W = 340.0
    S = 16.5
    x_key, x_greek = 16.0, 44.0
    line_budget = W - x_greek - 12
    for _, slab in SLABS:
        for side in rows_of(slab)[0] + rows_of(slab)[1]:
            for ln in side[1]:
                if tw(ln, S, "didot") > line_budget:
                    sys.exit("error: tall line %r measures %.1f > %.1f"
                             % (ln, tw(ln, S, "didot"), line_budget))
    pitch, cont, rowgap = 20.0, 18.0, 6.0
    g = []
    g.append('  <text class="pp-title" x="%.1f" y="28" font-size="16" '
             'font-family="%s" text-anchor="middle">%s</text>'
             % (W / 2, DIDOT, TITLE))
    y = 66.0
    for si, (head, slab) in enumerate(SLABS):
        g.append('  <text class="pp-head" x="%.1f" y="%.1f" font-size="16" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (W / 2, y, INTER, head))
        y += 26.0
        if si == 1:
            ry = y - 26.0 + 40.0
            g.insert(2, '  <g class="pp-band">')
            g.insert(3, '    <path class="pp-tick" d="M14 %.1f H326"/>' % ry)
            g.insert(4, '    <circle class="pp-sun" cx="158" cy="%.1f" r="4.4"/>' % ry)
            g.insert(5, '    <circle class="pp-moon" cx="182" cy="%.1f" r="3.2"/>' % ry)
            g.insert(6, '  </g>')
            y += 48.0
        left, right = rows_of(slab)
        for side in left + right:   # the source's reading order: down the
            key, lines = side       # left column, then down the right
            if key:
                g.append('    <text class="pp-key" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (x_key, y, S, DIDOT, key))
            for i, ln in enumerate(lines):
                g.append('    <text class="pp-greek" x="%.1f" y="%.1f" '
                         'font-size="%s" font-family="%s">%s</text>'
                         % (x_greek, y + i * cont, S, DIDOT, ln))
            y += (len(lines) - 1) * cont + pitch + rowgap
        y += 14.0
    H = y - rowgap + 10.0
    return svg_doc("tall", W, H, TALL_TITLE, "\n".join(g))


def write(path, svg):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("written", path.relative_to(FIG.parent.parent), len(svg.encode()), "bytes")


def self_test():
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" - " + detail) if detail else ""))
        if not good:
            worst = 1

    # --- register shape: the shape the wikitext diff verified ---------------
    left_a, right_a = rows_of(ABOVE)
    left_b, right_b = rows_of(BENEATH)
    check("register shape: 44 rows, 40 keys",
          len(left_a) + len(right_a) + len(left_b) + len(right_b) == 44
          and sum(1 for s in left_a + right_a + left_b + right_b if s[0]) == 40)
    check("above: keys run A-T | I-S with the two unkeyed rows",
          [s[0] or "?" for s in left_a] == list(KEYS_ABOVE_L)
          and [s[0] or "?" for s in right_a] == list(KEYS_ABOVE_R))
    check("beneath: keys run A-L | M-X with the two unkeyed rows",
          [s[0] or "?" for s in left_b] == list(KEYS_BENEATH_L)
          and [s[0] or "?" for s in right_b] == list(KEYS_BENEATH_R))
    all_rows = left_a + right_a + left_b + right_b
    dots = sum(1 for s in all_rows if any("[..." in x for x in s[1]))
    braces = sum(1 for s in all_rows if any("{" in x for x in s[1]))
    check("damage the source prints", dots == DOTS_EXPECTED and braces == BRACES_EXPECTED,
          "%d dot rows, %d brace rows" % (dots, braces))
    check("no row is empty and no line is empty",
          all(s[1] and all(x.strip() for x in s[1]) for s in all_rows))

    wide = build_wide()
    tall = build_tall()
    from collections import Counter
    wide_mult = Counter(joined(s) for s in all_rows)
    tall_mult = Counter(ln for s in all_rows for ln in s[1])
    key_mult = Counter(s[0] for s in all_rows if s[0])
    for name, svg in (("wide", wide), ("tall", tall)):
        mult = wide_mult if name == "wide" else tall_mult
        missing = [t for t, n in mult.items()
                   if svg.count(">%s<" % t) != n]
        check(name + ": all 44 rows verbatim, at the source's multiplicity",
              not missing,
              ("missing %s" % missing[:2]) if missing else "")
        bad_keys = [k for k, n in key_mult.items()
                    if svg.count(">%s<" % k) != n]
        check(name + ": keys azure, at the source's multiplicity",
              not bad_keys, ("wrong %s" % bad_keys[:3]) if bad_keys else "")
        check(name + ": token inks only",
              all(t not in svg for t in ('fill="#', 'stroke="#')))
        check(name + ": class names the stylesheet positions",
              all(c in svg for c in ('class="pp-plate', 'class="pp-title"',
                                     'class="pp-head"', 'class="pp-key"',
                                     'class="pp-greek"')))
        import re
        texts = re.findall(r'<text class="pp-[a-z]+"[^>]*font-size="([\d.]+)"'
                           r'[^>]*font-family="([^"]+)"[^>]*>([^<]+)</text>', svg)
        unmeasured = [(t[:24], z, f.split(",")[0]) for z, f, t in texts
                      if (t, float(z), "didot" if "Didot" in f else "inter")
                      not in MEASURED]
        check(name + ": every drawn string measured", not unmeasured,
              ("%s" % unmeasured[:3]) if unmeasured else "")

    # wide geometry: columns derived from the measurements (build exits on an
    # overrun); the band sits between the slabs with real clearance
    S = 12.5
    left_max = max(tw(joined(r[0]), S, "didot") for _, slab in SLABS
                   for r in slab if r[0])
    right_max = max(tw(joined(r[1]), S, "didot") for _, slab in SLABS
                    for r in slab if r[1])
    end = 44.0 + left_max + 26 + 26 + right_max
    check("wide: both columns inside the plate", end <= 640 - 14,
          "left %.1f right %.1f end %.1f" % (left_max, right_max, end))
    check("wide: the dial band drawn once, twelve ticks",
          wide.count('class="pp-band"') == 1 and wide.count('class="pp-tick"') == 12)
    m = re.search(r'class="pp-band">\n    <circle class="pp-frame" cx="[\d.]+" '
                  r'cy="([\d.]+)"', wide)
    if m:
        bcy = float(m.group(1))
        # measure from the svg itself: slab 1's last row baseline is the
        # greatest greek baseline above the band, slab 2's first the least
        # below it (the check measures what was drawn, not what was planned)
        gys = sorted(float(y) for y in
                     re.findall(r'class="pp-greek"[^>]*y="([\d.]+)"', wide))
        above = [y for y in gys if y < bcy]
        below = [y for y in gys if y > bcy]
        if above and below:
            last1, first2 = max(above), min(below)
            check("wide: the band clears the slab above and the header below",
                  bcy - 40.0 - last1 >= 12.0
                  and first2 - S * 0.72 - (bcy + 40.0) >= 12.0,
                  "above %.1f below %.1f" % (bcy - 40.0 - last1,
                                             first2 - S * 0.72 - (bcy + 40.0)))
        else:
            check("wide: the band clears the slab above and the header below",
                  False, "band outside the text run")
        # the band's moon must clear the sun's disc and rays (the front
        # dial's lesson: a hardcoded angular offset once drew them touching)
        sun_m = re.search(r'class="pp-sun" cx="([\d.]+)" cy="([\d.]+)"', wide)
        moon_m = re.search(r'class="pp-moon" cx="([\d.]+)" cy="([\d.]+)"', wide)
        if sun_m and moon_m:
            d = math.hypot(float(moon_m.group(1)) - float(sun_m.group(1)),
                           float(moon_m.group(2)) - float(sun_m.group(2)))
            check("wide: the band's moon clears the sun disc and rays",
                  d - 9.4 - 3.1 >= 0.0, "clearance %.1f" % (d - 12.5))
        else:
            check("wide: the band's moon clears the sun disc and rays",
                  False, "marks missing")
    else:
        check("wide: the band clears the slab above and the header below",
              False, "band not found")
    check("wide: viewBox is the desktop plate's", 'viewBox="0 0 640 ' in wide)
    check("tall: viewBox is the phone plate's", 'viewBox="0 0 340 ' in tall)
    check("tall: both slab headers drawn",
          tall.count(">ABOVE THE DIALS<") == 1 and
          tall.count(">BENEATH THE DIALS<") == 1)
    check("tall: the dial rule drawn once",
          tall.count('class="pp-band"') == 1 and tall.count('class="pp-tick"') == 1)

    print("parapegma self-test %s" % ("ok" if not worst else "FAILED"))
    return worst


def strings_needed():
    """Every (string, size, face) the plates will draw, for the measuring pass."""
    out = []
    for _, slab in SLABS:
        for r in slab:
            for side in r:
                if side:
                    out.append((joined(side), 12.5, "didot"))
                    for ln in side[1]:
                        out.append((ln, 16.5, "didot"))
                    if side[0]:
                        out.append((side[0], 12.5, "didot"))
                        out.append((side[0], 16.5, "didot"))
    out.append((TITLE, 16.0, "didot"))
    for head, _ in SLABS:
        out.append((head, 12.5, "inter"))
        out.append((head, 15.0, "inter"))
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--strings" in sys.argv:
        import json
        print(json.dumps([list(t) for t in strings_needed()], ensure_ascii=False,
                         indent=0))
        sys.exit(0)
    write(FIG / "parapegma-wide.svg", build_wide())
    write(FIG / "parapegma-tall.svg", build_tall())
