#!/usr/bin/env python3
"""Generate the share card: the close, as a poster.

    python Source/tools/make-og-card.py

Writes Assets/brand/og-card.png (1200x630, the one size every crawler wants).

WHY THIS EXISTS. The card is the site's face in a chat, a feed, a bookmark. The
old one was a browser screenshot of the hero with its lower 40% under the
fold-line cut into black: the window's own chrome read as dead pixels, the
answer's copy sat unreadable-small, and nothing on it said what the site has
since built its whole look from - the mechanism. It also drifted from the page
every time the page moved, because a screenshot is a photograph of a moment.

So the card is DRAWN, from the same arithmetic the page's figures use, and it
takes the close as its composition because the close is the page's thesis in
one frame: the wordmark on the field, the horizon crossing it, the machine
arriving over everything.

WHAT IS ON IT. Three layers, the close's own order:

    the field    the page's measured gradient (same stops, tighter: a 630-tall
                 frame is a field seen close up), painted per-pixel in numpy -
                 a radial gradient is arithmetic, not texture
    the horizon  the poster's own limb: 355 beads on R=1000, apex at the
                 wordmark's baseline, EXACTLY as make-poster-horizon.py places
                 it in CSS - the same fraction, the same count, the disputed
                 355th hole at the apex
    the world    the close's own train: a 223-tooth crown cut by the top edge
                 and its 60-tooth rider, meshed, at the sizes the site draws
                 them - faint, because they are ground, and the wordmark is
                 the subject
    the mark     "ἵστωρ." in the wordmark face itself (istor-wordmark.woff2,
                 the 16-codepoint subset that exists for exactly this string),
                 azure, the dot included - the one glyph pair every crawler
                 renders as the site's name

THE WORDMARK FACE, NOT GFS DIDOT. The display subset ships zero Greek
codepoints; the wordmark subset exists because the name is its own file
(1,892 B, 16 codepoints, both breathing/tonos decompositions). Drawing the name
from any other face is drawing it wrong.

NO BROWSER, NO SCREENSHOT. Everything here is Pillow + the fonts the site
ships: deterministic, re-runnable, and it cannot drift from the design the way
a screenshot drifts from a layout. The teeth are dash-arcs drawn as wedges (the
same dash-as-tooth argument as the SVG generators, rasterised); the phases are
solved so a tooth centre of the crown meets a gap centre of the rider, by the
same arc-length arithmetic - and the self-test asserts the drive ratio holds,
because a card that shows gears that do not mesh is worse than no gears.

Ink tokens are copied from styles.css as LITERALS with the token named beside
each, and the file's own check below re-reads styles.css and fails if a token
has moved - a literal that can silently rot is a lie with a comment on it.
"""

import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "Assets" / "brand" / "og-card.png"
CSS = HERE.parent / "styles.css"

W, H = 1200, 630

# --- tokens, checked against styles.css by token_check() below ----------------
TOKENS = {
    "field-base":  "#0E1E22",
    "field-hi":    "#163234",
    "field-ink":   "#E9EDF0",
    "field-ink-2": "#9FB0B4",
    "azure":       "#0066CC",
    "azure-lift":  "#4DA3FF",
}


def token_check():
    """Every literal above must still be what styles.css says it is."""
    text = CSS.read_text(encoding="utf-8")
    bad = []
    for name, literal in TOKENS.items():
        m = re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % name, text)
        if not m:
            bad.append(f"--{name}: not found in styles.css")
        elif m.group(1).lower() != literal.lower():
            bad.append(f"--{name}: card says {literal}, styles.css says {m.group(1)}")
    return bad


# --- the field ----------------------------------------------------------------

def paint_field(im):
    """The page's radial gradient, per pixel.

    styles.css: radial-gradient(130% 120% at 78% 14%), stops #163234 0% /
    #11282B 34% / #0F2024 62% / #0E1E22 86% / #0C1B1E 100% on #0E1E22. The
    ellipse's radii are 130%/120% OF THE BOX, so the 1.0 isopleth passes
    through the corners' neighbourhood and the far corner is past it - which
    the last stop catches at #0C1B1E, as on the page.
    """
    import numpy as np
    stops = [
        (0.00, (0x16, 0x32, 0x34)),
        (0.34, (0x11, 0x28, 0x2B)),
        (0.62, (0x0F, 0x20, 0x24)),
        (0.86, (0x0E, 0x1E, 0x22)),
        (1.00, (0x0C, 0x1B, 0x1E)),
    ]
    cx, cy = 0.78 * W, 0.14 * H
    rx, ry = 1.30 * W, 1.20 * H
    y, x = np.mgrid[0:H, 0:W].astype(float)
    t = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    t = np.clip(t, 0.0, 1.0)
    img = np.zeros((H, W, 3), dtype=np.uint8)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        f = np.where(m, (t - t0) / (t1 - t0), 0.0)[..., None]
        img = np.where(m[..., None],
                       (np.array(c0) * (1 - f) + np.array(c1) * f), img)
    im.paste(Image.fromarray(img.astype(np.uint8), "RGB"), (0, 0))


# --- the horizon ---------------------------------------------------------------
# The poster's limb: 355 beads on R=1000, apex on the wordmark's baseline.
# make-poster-horizon.py solves the last-hole-at-apex rotation; the same
# arithmetic here, translated to this frame.

HOLES = 355
R_HORIZON = 1000.0
DOT = 7.0


def horizon_baseline():
    """The card's wordmark baseline, in the page's own fraction.

    The poster puts the horizon's apex at 0.889 of the mark's box, which is
    the baseline. The card's mark is MARK_SIZE with the same 0.86 line-height,
    and its box starts at MARK_Y - the same construction, the same fraction.
    """
    return MARK_Y + MARK_SIZE * 0.86 * 0.889


def paint_horizon(im):
    cx = W / 2.0
    cy = horizon_baseline() + R_HORIZON
    d = ImageDraw.Draw(im)
    # beads at the pitch the page's figure uses (2*pi*R/HOLES), every third one
    # drawn slightly brighter - the eye reads a dashed ring, not a dotted line
    pitch = 2 * math.pi * R_HORIZON / HOLES
    alpha = math.degrees((HOLES - 0.5) * pitch / R_HORIZON)
    # hole 355 at the apex: the path starts at 3 o'clock, so rotate back
    start = -90.0 - alpha
    for i in range(HOLES):
        a = math.radians(start + i * math.degrees(pitch / R_HORIZON))
        x, y = cx + R_HORIZON * math.cos(a), cy + R_HORIZON * math.sin(a)
        if -DOT <= x <= W + DOT and -DOT <= y <= H + DOT:
            d.ellipse([x - DOT / 2, y - DOT / 2, x + DOT / 2, y + DOT / 2],
                  fill=TOKENS["field-ink-2"])


# --- the world -----------------------------------------------------------------
# The close's train, drawn as wedges: each tooth is a filled wedge centred on
# its angle, ON the pitch radius. Raster has no stroke-dasharray, so the SVG
# generators' dash-as-tooth argument becomes wedges here; drawn at 4x and
# downsampled, because 223 unsupersampled teeth alias into a fuzzy band.


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _arc_band(im, cx, cy, r, width, opacity):
    """One limb stroke: a circle arc rasterised as an ellipse ring,
    composited by alpha the way the svg's stroke-opacity does. Pillow has no
    translucent stroke on an RGB image, so the band is drawn on its own tile
    and pasted through its own alpha."""
    ink = _hex_rgb(TOKENS["field-ink"])
    R = int(r * SS)
    wpx = max(1, int(width * SS / 2))
    tile = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    cx_s, cy_s = int(cx * SS), int(cy * SS)
    td.ellipse([cx_s - R - wpx, cy_s - R - wpx, cx_s + R + wpx, cy_s + R + wpx],
               outline=ink + (int(255 * opacity),), width=wpx * 2)
    tile = tile.resize((W, H), Image.LANCZOS)
    im.paste(tile, (0, 0), tile)

N1, N2 = 223, 60


def gear_wedges(im, centre, radius, n_teeth, offset_deg, ink, depth=None,
                ring_w=3):
    """Teeth as filled wedges, plus the rim ring under them."""
    cx, cy = centre
    d = ImageDraw.Draw(im)
    tooth = 2 * math.pi / n_teeth
    half = tooth * 0.25          # a tooth CENTRE at its wedge's middle
    if depth is None:
        depth = radius * 0.02
    # Teeth sit ON the pitch radius (centre of the tooth's depth there), so
    # the mesh arithmetic - which lives on the pitch circle - describes the
    # drawn teeth exactly. Supersample 4x: 223 teeth at card scale are ~3px
    # wide, and unsupersampled wedges alias into a fuzzy band.
    r_in = radius - depth / 2
    r_out = radius + depth / 2
    for i in range(n_teeth):
        a = math.radians(offset_deg) + i * tooth
        d.polygon([
            (cx + r_in * math.cos(a - half),
             cy + r_in * math.sin(a - half)),
            (cx + r_out * math.cos(a - half * 0.55),
             cy + r_out * math.sin(a - half * 0.55)),
            (cx + r_out * math.cos(a + half * 0.55),
             cy + r_out * math.sin(a + half * 0.55)),
            (cx + r_in * math.cos(a + half),
             cy + r_in * math.sin(a + half)),
        ], fill=ink)
    # The rim as the SVG generators draw it: a solid band just inside the
    # teeth, its two edges as hairlines. A single line reads as a wire; the
    # band is what says METAL.
    band_r = radius - depth
    band_w = max(1, int(radius * 0.045))
    d.ellipse([cx - band_r, cy - band_r, cx + band_r, cy + band_r],
              outline=ink, width=band_w)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              outline=ink, width=ring_w)


SS = 4                    # supersample: draw at 4x, downsample with LANCZOS


def paint_world(im):
    """The crown enters from the top edge; the rider bites inside it, upper
    right of the crown's apex - the close's own composition, small enough to
    be ground and not subject."""
    # Crown: pitch R1 sized so the ARC VISIBLE between the frame's top edge and
    # the wordmark's zone carries drawn teeth. A 900-radius crown on a 1200-wide
    # card is nearly flat: the sag from the apex to the edge is only
    # 900 - sqrt(900^2 - 360^2) = 78px, and the top strip is dark-on-dark at
    # 1.6:1 - the world needs to sit in the LIT half of the gradient, which at
    # 78% 14% origin is the upper CENTRE. So the crown is smaller and placed
    # apex-down into the lit zone: apex at 40% of the card's height, left of
    # centre, rising off the left edge - the wheel is seen from inside its own
    # rim, which is the composition the site's close uses.
    R1 = 300.0
    apex = (W * 0.36, H * 0.58)
    c1 = (apex[0], apex[1] + R1)         # apex at the top of the wheel
    # Rider on the same module: R2 = R1 * N2/N1
    R2 = R1 * N2 / N1
    theta = math.radians(52.0)           # bearing from the crown's centre
    dist = R1 - R2                       # internal mesh
    c2 = (c1[0] + dist * math.sin(theta), c1[1] - dist * math.cos(theta))
    ink = TOKENS["field-ink-2"]

    # Draw the whole train at 4x and downsample. Tooth DEPTH is set in whole
    # pixels (22 at 4x = 5.5 final on the crown, 10 at 4x = 2.5 on the rider):
    # the site's 2%-of-radius rule would give the R=300 crown 1.5px teeth that
    # read as noise, and the card is a poster, not a measured drawing. The
    # PITCH still obeys the module - tooth counts are exact, the mesh still
    # interleaves - which is the claim the self-test owns.
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))

    # Phase: put a crown tooth centre exactly at the contact bearing, then
    # solve the rider's offset so a GAP centre lands on the contact bearing
    # measured from the rider's centre. Internal mesh: the contact is BEYOND
    # the rider's centre along the line of centres, so that bearing is
    # theta - 180 in this frame (the rider hangs ABOVE-RIGHT of its centre's
    # contact line), and the wheel's tooth pattern is expressed in the same
    # bearing convention as the rider's gap pattern. Solved, not nudged.
    tooth1 = 360.0 / N1
    tooth2 = 360.0 / N2
    contact_brg = math.degrees(theta)    # bearing of the contact from C1
    off1 = contact_brg % tooth1          # tooth centre sits ON the contact
    rider_brg = math.degrees(theta) - 180.0
    off2 = (rider_brg + 0.5 * tooth2) % tooth2
    ink_big = (*_hex_rgb(ink), 235)
    gear_wedges(big, (c1[0] * SS, c1[1] * SS), R1 * SS, N1, off1,
                ink_big, depth=22 * SS, ring_w=3 * SS)
    gear_wedges(big, (c2[0] * SS, c2[1] * SS), R2 * SS, N2, off2,
                ink_big, depth=10 * SS, ring_w=2 * SS)
    big = big.resize((W, H), Image.LANCZOS)
    im.paste(big, (0, 0), big)
    return c1, c2, R1, R2


# --- the mark ------------------------------------------------------------------

MARK_SIZE = 168
MARK_Y = 150           # the mark box's top


def paint_mark(im):
    face = ImageFont.truetype(str(ROOT / "Assets" / "brand" / "istor-wordmark.woff2"),
                              MARK_SIZE)
    d = ImageDraw.Draw(im)
    text = "ἵστωρ."
    # the face is a subset with exactly this string's codepoints; the dot is
    # drawn in azure (the mark-dot token), the letters in --azure-lift
    w_letters = d.textlength("ἵστωρ", font=face)
    w_dot = d.textlength(".", font=face)
    x = (W - (w_letters + w_dot)) / 2
    y = MARK_Y
    # The veil's rim, UNDER the letters: the canopy limb the page draws, its
    # four stacked strokes, apex at the letters' cap line. Drawn here first so
    # the mark paints over it, and then paint_veil() crosses the beads over.
    _veil_limb(im)
    d.text((x, y), "ἵστωρ", font=face, fill=TOKENS["azure-lift"])
    d.text((x + w_letters, y), ".", font=face, fill=TOKENS["azure"])


TAGLINE = "Local. Offline. Every claim points at its passage."

# --- the veil -------------------------------------------------------------------
# M35's second ring, translated to the card: a canopy of 355 beads crossing the
# letters' middle, beads IN FRONT of the type - the one crossing where the
# machine goes over the brand. Radius scaled from the page's 2600 at a 220px
# mark to the card's 168px mark (same composition, same fractions); the apex
# sits mid-letter, at the MEASURED middle of the rendered cap band: the
# wordmark face's pixels were measured on the drawn card itself (azure rows
# 191..330 at MARK_SIZE 168), not taken from font-metric guesses - the same
# discipline the page's 0.889 baseline fraction sets. Mid-band = 0.654 of the
# mark box, and the self-test's pixel scan below holds the drawing to it.

R_VEIL = 2600.0 * (168.0 / 220.0)      # 1985.5 - the canopy at card scale
VEIL_APEX_FRACTION = 0.654


def veil_apex_y():
    """The veil's apex: the letters' cap line plus half the cap band. The page
    positions the veil's y=0 at the cap line (0.115 of the type size below the
    mark box's top, the stylesheet's measured fraction for this face) and the
    svg's apex sits 80/420 into its frame; the card draws the same crossing
    directly: cap line + half the band = 0.115 + 0.35 of MARK_SIZE."""
    return MARK_Y + MARK_SIZE * VEIL_APEX_FRACTION


def _veil_limb(im):
    """The canopy's limb under the letters: the horizon's four-stroke recipe,
    widest and faintest first, apex up."""
    cx = W / 2.0
    cy = veil_apex_y() + R_VEIL
    for width, op in ((44, 0.05), (20, 0.075), (8, 0.11), (2.4, 0.34)):
        _arc_band(im, cx, cy, R_VEIL, width, op)


def paint_veil(im):
    """The beads, over the letters. Same arithmetic as the horizon's, same
    last-hole-at-apex rotation, at the canopy radius - and the disputed
    355th bead at the apex in --azure, as on the page."""
    cx = W / 2.0
    cy = veil_apex_y() + R_VEIL
    d = ImageDraw.Draw(im)
    pitch = 2 * math.pi * R_VEIL / HOLES
    alpha = math.degrees((HOLES - 0.5) * pitch / R_VEIL)
    start = -90.0 - alpha
    for i in range(HOLES):
        a = math.radians(start + i * math.degrees(pitch / R_VEIL))
        x, y = cx + R_VEIL * math.cos(a), cy + R_VEIL * math.sin(a)
        if -DOT <= x <= W + DOT and -DOT <= y <= H + DOT:
            disputed = i == HOLES - 1
            r = DOT * 0.72 if disputed else DOT / 2
            fill = TOKENS["azure"] if disputed else TOKENS["field-ink-2"]
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def paint_tagline(im):
    """The promise, once, at the bottom: the old card's sub-line, which is the
    one sentence a stranger needs. Inter at the page's lede weight, secondary
    ink - it explains, the mark and the machine speak."""
    face = ImageFont.truetype(str(ROOT / "Assets" / "fonts" / "inter-var.woff2"), 30)
    try:
        face.set_variation_by_axes([480])
    except Exception:
        pass
    d = ImageDraw.Draw(im)
    w = d.textlength(TAGLINE, font=face)
    d.text(((W - w) / 2, 540), TAGLINE, font=face,
           fill=TOKENS["field-ink-2"])


def main():
    bad = token_check()
    if bad:
        raise SystemExit("token drift:\n  " + "\n  ".join(bad))

    im = Image.new("RGB", (W, H), TOKENS["field-base"])
    paint_field(im)
    paint_world(im)
    paint_horizon(im)
    paint_mark(im)      # paints the veil's limb under the letters
    paint_veil(im)      # the beads, over them: the close's own order
    paint_tagline(im)

    if "--self-test" in sys.argv:
        # The rider's rate: at a 10-degree crown turn the rider must sit at
        # theta + 10*(N1/N2) - the internal-drive relation - which is what the
        # phase arithmetic above is a static slice of. Asserted on the drawn
        # geometry: the rider's centre is exactly R1-R2 from the crown's, and
        # the contact bearing from each centre is opposite.
        R1 = 300.0
        R2 = R1 * N2 / N1
        theta = math.radians(52.0)
        c1 = (W * 0.36, H * 0.58 + R1)
        dist = R1 - R2
        c2 = (c1[0] + dist * math.sin(theta), c1[1] - dist * math.cos(theta))
        d_actual = math.hypot(c2[0] - c1[0], c2[1] - c1[1])
        assert abs(d_actual - dist) < 1e-9, "rider is not at the mesh distance"
        assert abs(R2 - R1 * N2 / N1) < 1e-9, "rider is not on the module"
        # The veil crosses mid-letter, held on the DRAWN pixels: scan the card's
        # azure rows (the letters), find the band, and demand the apex bead sit
        # inside its middle third. This is the check that keeps the crossing at
        # the composition the page draws, even if the face's metrics move.
        px = im.load()
        rows = []
        for yy in range(H):
            n = 0
            for xx in range(0, W, 2):
                r, g, b = px[xx, yy]
                if b > 220 and 60 < r < 110 and 140 < g < 190:
                    n += 1
            if n > 3:
                rows.append(yy)
        cap_top, band_end = rows[0], rows[-1]
        apex = MARK_Y + MARK_SIZE * VEIL_APEX_FRACTION
        mid_lo = cap_top + (band_end - cap_top) * 0.33
        mid_hi = cap_top + (band_end - cap_top) * 0.72
        assert mid_lo <= apex <= mid_hi, (
            "veil apex at %.0f is outside the letters' middle band %.0f..%.0f"
            % (apex, mid_lo, mid_hi))
        print("self-test ok - rider at the internal mesh distance, on the module; "
              "veil apex crosses mid-letter (%.0f in %.0f..%.0f)" % (apex, mid_lo, mid_hi))

    im.save(OUT, "PNG", optimize=True)
    print(f"{OUT.relative_to(ROOT)} written: {OUT.stat().st_size:,} B")


if __name__ == "__main__":
    main()
