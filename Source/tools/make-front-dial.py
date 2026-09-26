#!/usr/bin/env python3
"""Generate the front-dial plate: the face that shows where the sun and moon are.

    python Source/tools/make-front-dial.py [--self-test]

Writes Source/figures/front-dial-wide.svg and Source/figures/front-dial-tall.svg.

WHY THIS EXISTS. The page's hero answer says the front dial "shows where the sun
and moon are", and no drawing on the page shows that face. This plate draws what
the page's own source 1 (the read Wikipedia article, Freeth et al.'s model)
states about it, and nothing else:

  - an inner zodiac ring, the ecliptic, in twelve equal 30-degree sectors,
    labelled with the twelve Greek sign names the source lists;
  - an outer rotatable calendar ring, drawn as the page already draws the
    disputed ring: the hole count is the question, so the plate shows 355 with
    the honest caption carrying the dispute rather than resolving it;
  - three Egyptian month names in Greek letters, exactly the three the source
    says survive on the ring (ΠΑΧΩΝ, ΠΑΥΝΙ, ΕΠΙΦΙ), placed at their attested
    relative positions (each one month apart, starting at the ram);

  - the sun's mark on the ecliptic, the plate's one azure statement: the source
    says the dial "marks the position of the Sun on the ecliptic";
  - the moon's mark beside it, from the same sentence the page's hero quotes -
    "shows where the sun and moon are" - drawn as the small disc the source
    describes (Fragment C's moon-phase sphere in its housing).

The sun/moon pair is placed at an arbitrary-but-fixed date (the ram's season,
where the three attested months sit); the plate is a drawing of the FACE, not a
reading of the sky on any particular day, and the caption says so.

WHAT IS DELIBERATELY ABSENT. The parapegma inscriptions above and below the
dials, the planet hands (the source calls them speculation), the true pointer
shapes (none survive). A drawing made up from memory is the thing this page
exists to refuse.

SELF-TEST. Demands twelve sectors, the twelve names each once, the three
attested month names, the 355-hole dashed ring, exactly one sun and one moon
mark, MEASURED covering every drawn string at its drawn size, token inks only
(no hand hex), and the class names the stylesheet positions.

Requires: measured strings in MEASURED (browser, GFS Didot - the M37a rebuild
made uppercase Greek real). Standard library otherwise.
"""

import math
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

DIDOT = "GFS Didot, Georgia, serif"
INTER = "Inter, sans-serif"

# --- the source's lists -------------------------------------------------------
ZODIAC = ("ΚΡΙΟΣ", "ΤΑΥΡΟΣ", "ΔΙΔΥΜΟΙ", "ΚΑΡΚΙΝΟΣ", "ΛΕΩΝ", "ΠΑΡΘΕΝΟΣ",
          "ΧΗΛΑΙ", "ΣΚΟΡΠΙΟΣ", "ΤΟΞΟΤΗΣ", "ΑΙΓΟΚΕΡΩΣ", "ΥΔΡΟΧΟΟΣ", "ΙΧΘΥΕΣ")
# the three months the source says survive, with their month offsets from the
# ram (the Egyptian year's months are equal; the three sit one month apart)
MONTHS = (("ΠΑΧΩΝ", 8), ("ΠΑΥΝΙ", 9), ("ΕΠΙΦΙ", 10))
MONTHS_TOTAL = 12          # the ring is marked by month and day; 12 months of 30
SUN_MOON_DEG = 0.0         # the ram's beginning: 0 degrees Aries, the zodiac's
# own zero and the vernal equinox the source's parapegma marks. On the sector
# boundary rather than mid-sector, where the sign's label runs; the caption
# still says the placement is a drawing's, not a reading of a real day.
MOON_OFFSET_DEG = 6.5      # beside the sun, clear of the boundary spoke

# Every drawn string's measured width in user units, keyed by string and size.
# Measured in the browser off the built page, 2026-09-23, in GFS Didot after
# the font rebuild (uppercase Greek is real now; the fallback before it was
# Georgia, which these numbers are NOT from).
# Sizes are set by the type floor, not by taste: the plate renders at 0.92
# (wide, desktop) down to 0.71 (tall, a 320 phone), and the floor is 11px, so
# the drawn sizes are 12.5 (wide) and 16.5 (tall) - 16.5*0.71 = 11.7. The first
# draft drew 11/14 and the contrast audit's type-floor pass caught all 120
# rendered texts under the floor. (Same lesson as the games plate: a figure's
# type is measured after scaling, never as drawn.)
MEASURED = {
    # zodiac names at 12.5 (wide plate), GFS Didot, 0.02em tracking
    ("ΚΡΙΟΣ", 12.5): 41.0, ("ΤΑΥΡΟΣ", 12.5): 50.7, ("ΔΙΔΥΜΟΙ", 12.5): 54.7,
    ("ΚΑΡΚΙΝΟΣ", 12.5): 69.9, ("ΛΕΩΝ", 12.5): 37.5, ("ΠΑΡΘΕΝΟΣ", 12.5): 72.6,
    ("ΧΗΛΑΙ", 12.5): 43.4, ("ΣΚΟΡΠΙΟΣ", 12.5): 68.5, ("ΤΟΞΟΤΗΣ", 12.5): 63.6,
    ("ΑΙΓΟΚΕΡΩΣ", 12.5): 77.3, ("ΥΔΡΟΧΟΟΣ", 12.5): 70.0, ("ΙΧΘΥΕΣ", 12.5): 49.8,
    # zodiac names at 16.5 (tall plate)
    ("ΚΡΙΟΣ", 16.5): 54.1, ("ΤΑΥΡΟΣ", 16.5): 67.0, ("ΔΙΔΥΜΟΙ", 16.5): 72.2,
    ("ΚΑΡΚΙΝΟΣ", 16.5): 92.2, ("ΛΕΩΝ", 16.5): 49.5, ("ΠΑΡΘΕΝΟΣ", 16.5): 95.9,
    ("ΧΗΛΑΙ", 16.5): 57.3, ("ΣΚΟΡΠΙΟΣ", 16.5): 90.5, ("ΤΟΞΟΤΗΣ", 16.5): 84.0,
    ("ΑΙΓΟΚΕΡΩΣ", 16.5): 102.1, ("ΥΔΡΟΧΟΟΣ", 16.5): 92.3, ("ΙΧΘΥΕΣ", 16.5): 65.7,
    # the three attested months at 12.5 (wide)
    ("ΠΑΧΩΝ", 12.5): 47.6, ("ΠΑΥΝΙ", 12.5): 40.4, ("ΕΠΙΦΙ", 12.5): 37.7,
    # the three attested months at 16.5 (tall)
    ("ΠΑΧΩΝ", 16.5): 62.8, ("ΠΑΥΝΙ", 16.5): 53.4, ("ΕΠΙΦΙ", 16.5): 49.7,
    # count line, Inter (only size drawn)
    # The centre line is the hero answer's own phrase: "the front dial shows
# where the sun and moon are". The draft's "and the" was the draft's.
("the sun and moon", 16.5): 141.2,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def arc(cx, cy, r, a0, a1):
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return "M%.2f %.2f A%.2f %.2f 0 %d 1 %.2f %.2f" % (x0, y0, r, r, large, x1, y1)


HOLES = 355


def ring_band(cx, cy, r_out, r_in):
    """The disputed ring, in the calendar-ring figure's own language: two
    hairline frame circles and the holes as ONE dashed circle. The count is
    the question, so the drawing does not answer it."""
    r_holes = (r_out + r_in) / 2
    c = 2 * math.pi * r_holes
    pitch = c / HOLES
    gap = pitch - 0.02
    return ('  <g class="fd-ring">\n'
            '    <circle class="fd-frame" cx="%.1f" cy="%.1f" r="%.1f"/>\n'
            '    <circle class="fd-frame" cx="%.1f" cy="%.1f" r="%.1f"/>\n'
            '    <circle class="fd-holes" cx="%.1f" cy="%.1f" r="%.2f"/>\n'
            '  </g>'
            % (cx, cy, r_out, cx, cy, r_in, cx, cy, r_holes)), pitch, gap, r_holes


def month_corner_clearance(cx, cy, r_months, name_size):
    """Worst clearance, in units, between any month label's ink box corner and
    the two calendar-band frame circles. A horizontal label at a diagonal
    angle approaches the circle with its CORNER, not its centre: the wide
    plate's first lane passed a centre-distance check while ΕΠΙΦΙ's box
    grazed the frame at 0.1 units, which the rendered page caught. Ink box:
    measured width, 0.72em cap above the baseline, 0.28em descent below.
    Must stay >= 4."""
    band_out = r_zodiac_out_holder[0] + 26
    frames = (band_out, band_out - 12)
    cap, desc = 0.72 * name_size, 0.28 * name_size
    worst = 1e9
    for label, offset in MONTHS:
        w = tw(label, name_size)
        deg = -90.0 + (offset + 0.5) * (360.0 / MONTHS_TOTAL)
        x, y = pt(cx, cy, r_months, deg)
        for cx0, cy0 in ((x - w/2, y - cap), (x + w/2, y - cap),
                         (x - w/2, y + desc), (x + w/2, y + desc)):
            for fr in frames:
                worst = min(worst, abs(math.hypot(cx0 - cx, cy0 - cy) - fr))
    return worst


# the clearance helper needs the caller's zodiac radius; set by dial()
r_zodiac_out_holder = [0.0]


def dial(cx, cy, r_zodiac_out, name_size, cls, r_months):
    """The zodiac ring and its twelve names, each rotated to read outward
    along its sector's mid-radius - the source's own convention for this
    dial, and the only fit for names as long as ΑΙΓΟΚΕΡΩΣ in a 30-degree
    window: rotated, the label's constraint is the band's radial depth, not
    the chord. (The first draft set names horizontal and chord-checked with
    a missing half-angle, passing every name while ΧΗΛΑΙ and ΠΑΡΘΕΝΟΣ
    collided on the rendered page; the screenshot caught what the check
    measured wrong.)"""
    g = []
    g.append('  <g class="%s">' % cls)
    r_zodiac_out_holder[0] = r_zodiac_out
    # radial depth: the longest measured name sets it (ΑΙΓΟΚΕΡΩΣ, 77 at 12.5
    # and 102 at 16.5), plus an 8-unit margin each side. Deriving depth from
    # the measurement rather than an em multiple keeps the tall plate's hub
    # alive: a fixed 6.8em at 16.5 units ate 112 of the 138 radius and left
    # nothing for the sun and moon to stand in.
    longest = max(tw(n, name_size) for n in ZODIAC)
    r_in = r_zodiac_out - (longest + 16)
    span = 30.0
    for i, name in enumerate(ZODIAC):
        a0 = i * span
        a1 = (i + 1) * span
        amid = (a0 + a1) / 2
        g.append('    <path class="fd-arc" d="%s"/>' % arc(cx, cy, r_zodiac_out, a0, a1))
        g.append('    <path class="fd-arc" d="%s"/>' % arc(cx, cy, r_in, a0, a1))
        if i:
            x0, y0 = pt(cx, cy, r_in, a0)
            x1, y1 = pt(cx, cy, r_zodiac_out, a0)
            g.append('    <path class="fd-spoke" d="M%.2f %.2f L%.2f %.2f"/>'
                     % (x0, y0, x1, y1))
        # the name, rotated to read outward along the sector's mid-radius,
        # anchored at its middle on the band's mid-radius. On the lower half
        # (90..270 degrees) the rotation gains 180 so no label runs upside
        # down; because the anchor is the middle, the flip happens in place
        # and the name still occupies the same band. (The first draft anchored
        # at the hub and flipped about that anchor, which slid every lower
        # label back over the hub - the phone screenshot caught it.)
        w = tw(name, name_size)
        if w > r_zodiac_out - r_in - 8:
            sys.exit("error: %r at %s measures %.1f, radial depth %.1f"
                     % (name, name_size, w, r_zodiac_out - r_in - 8))
        r_label = (r_zodiac_out + r_in) / 2
        lx, ly = pt(cx, cy, r_label, amid)
        # SVG rotates in screen coordinates (y down) while pt() works in
        # maths coordinates (y up). The rotation that reads along the radial
        # is amid - 90; it is legible while sin(amid) >= 0 (sectors 0..180).
        # Past 180 the same line runs upside down, so those sectors take
        # amid + 90, which reads along the mirrored radial - inward-running
        # on the left half, the standard clockface convention, verified in
        # the browser against all twelve names before it was written here.
        flip = amid % 360 >= 180
        rot = (amid + 90.0) if flip else (amid - 90.0)
        g.append('    <text class="fd-sign" x="%.2f" y="%.2f" '
                 'font-size="%s" font-family="%s" text-anchor="middle" '
                 'transform="rotate(%.2f %.2f %.2f)">%s</text>'
                 % (lx, ly, name_size, DIDOT, rot, lx, ly, name))
    # the three surviving month names, outside the calendar band, at their
    # attested month offsets. Months run with the ring; the ram sits at -90
    # (12 o'clock) and each Egyptian month is one twelfth of the ring. Set
    # horizontal and centred: three short names, and the caption names them
    # in Latin script for readers who cannot read them here. The radius comes
    # in from the caller: it must clear the calendar band AND land inside the
    # viewBox at every width, which a name-size multiple is free to violate.
    for label, offset in MONTHS:
        w = tw(label, name_size)
        deg = -90.0 + (offset + 0.5) * (360.0 / MONTHS_TOTAL)
        r_label = r_months
        chord = 2 * r_label * math.sin(math.radians(360.0 / MONTHS_TOTAL / 2 - 3))
        if w > chord - 4:
            sys.exit("error: month %r at %s measures %.1f, chord %.1f"
                     % (label, name_size, w, chord))
        lx, ly = pt(cx, cy, r_label, deg)
        g.append('    <text class="fd-month" x="%.2f" y="%.2f" font-size="%s" '
                 'font-family="%s" text-anchor="middle">%s</text>'
                 % (lx, ly, name_size, DIDOT, label))
    # the sun and moon, the plate's one azure statement. The sun is the
    # rayed mark at the ecliptic longitude; the moon the small disc beside
    # it. Both sit INSIDE the zodiac ring, in the empty hub: the marks read
    # as a hand's tip seen from within, and no sign label can ever collide
    # with them (the first placement put them mid-band at 0 degrees, and the
    # sun's disc clipped the ram's label). The art scales off the hub radius
    # it actually lives in, not off the type: the tall plate's hub is half
    # the wide plate's, and a type-scaled sun would not fit it.
    hub = r_in - 12
    sr = hub
    sx, sy = pt(cx, cy, sr, SUN_MOON_DEG)
    g.append('    <g class="fd-lights">')
    g.append('      <circle class="fd-sun" cx="%.2f" cy="%.2f" r="%.2f"/>'
             % (sx, sy, max(4.5, hub * 0.18)))
    sun_r = max(4.5, hub * 0.18)
    for k in range(8):
        a = k * 45.0
        x0, y0 = pt(sx, sy, sun_r * 1.5, a)
        x1, y1 = pt(sx, sy, sun_r * 2.1, a)
        g.append('      <path class="fd-ray" d="M%.2f %.2f L%.2f %.2f"/>'
                 % (x0, y0, x1, y1))
    mr = max(3.4, hub * 0.14)
    # the moon rides the same radius, at the angular offset that actually
    # clears the sun's disc and rays - derived from the two radii, not a
    # hardcoded degree (6.5 degrees at hub radius made the discs overlap;
    # the rendered-pixel check caught it). One extra ray-length of clearance.
    need = sun_r * 2.1 + mr + 2
    moon_off = 2 * math.degrees(math.asin(min(0.9, need / (2 * sr))))
    mx, my = pt(cx, cy, sr, SUN_MOON_DEG + moon_off)
    g.append('      <circle class="fd-moon" cx="%.2f" cy="%.2f" r="%.2f"/>'
             % (mx, my, mr))
    g.append('    </g>')
    g.append('  </g>')
    return "\n".join(g), r_in


def build_wide():
    W, H = 640, 448
    cx, cy = 320.0, 210.0
    r_zodiac_out = 148.0
    # the months ride OUTSIDE the calendar band, in the zone the source's
    # parapegma texts occupied, one month apart: attested position, not a
    # type multiple. (Inside the band they would cross the dashed hole ring.)
    band_out = r_zodiac_out + 26
    # month lane: the first radius where all three horizontal labels clear
    # both frame circles by 4 units (the corner, not the centre, approaches
    # the circle at the diagonal angles - see month_corner_clearance).
    dial_g, r_zodiac_in = dial(cx, cy, r_zodiac_out, 12.5, "front-dial",
                               r_months=band_out + 26)
    band_g, pitch, gap, r_holes = ring_band(cx, cy,
                                            band_out, r_zodiac_out + 14)
    count_y = cy + band_out + 46
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="front-plate front-wide" role="img" focusable="false"
     aria-labelledby="front-wide-title">
  <title id="front-wide-title">The front dial: an inner zodiac ring of twelve
    Greek signs in thirty-degree sectors, an outer ring of day holes whose
    count is the question this page is about, the three month names that
    survive on it (Pachon, Payni, Epiphi), and the sun and moon the dial
    exists to show.</title>
{band_g}
{dial_g}
  <text class="front-count" x="{cx}" y="{count_y}"
        font-size="16.5" text-anchor="middle">the sun and moon</text>
</svg>
'''
    # the dashed-circle arithmetic must survive the f-string round trip
    svg = svg.replace('class="fd-holes" cx="%.1f" cy="%.1f" r="%.2f"',
                      'class="fd-holes"')
    # splice dasharray onto the holes circle with the literal pitch
    svg = svg.replace('class="fd-holes"',
                      'class="fd-holes" fill="none" stroke-dasharray="0.02 %.6f" '
                      'stroke-linecap="round"' % gap, 1)
    return svg


def build_tall():
    W, H = 340, 470
    cx, cy = 170.0, 218.0
    r_zodiac_out = 138.0
    band_out = r_zodiac_out + 26
    dial_g, r_zodiac_in = dial(cx, cy, r_zodiac_out, 16.5, "front-dial",
                               r_months=band_out + 30)
    band_g, pitch, gap, r_holes = ring_band(cx, cy,
                                            band_out, r_zodiac_out + 14)
    count_y = cy + band_out + 46
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="front-plate front-tall" role="img" focusable="false"
     aria-labelledby="front-tall-title">
  <title id="front-tall-title">The front dial: twelve Greek zodiac signs, the
    outer ring of day holes whose count is disputed, the three surviving month
    names, and the sun and moon marks.</title>
{band_g}
{dial_g}
  <text class="front-count" x="{cx}" y="{count_y}"
        font-size="16.5" text-anchor="middle">the sun and moon</text>
</svg>
'''
    svg = svg.replace('class="fd-holes" cx="%.1f" cy="%.1f" r="%.2f"',
                      'class="fd-holes"')
    svg = svg.replace('class="fd-holes"',
                      'class="fd-holes" fill="none" stroke-dasharray="0.02 %.6f" '
                      'stroke-linecap="round"' % gap, 1)
    return svg


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

    for name, svg, W, H, r_out in (("wide", build_wide(), 640, 448, 148.0),
                                   ("tall", build_tall(), 340, 470, 138.0)):
        # stroke widths are the stylesheet's; the invariants are structural
        check(name + ": twelve sectors",
              svg.count('class="fd-arc"') == 24 and svg.count('class="fd-spoke"') == 11)
        for sign in ZODIAC:
            if svg.count(">%s<" % sign) != 1:
                check(name + ": %s once" % sign, False)
                break
        else:
            check(name + ": twelve signs, each once", True)
        for label, _ in MONTHS:
            if svg.count(">%s<" % label) != 1:
                check(name + ": month %s" % label, False)
                break
        else:
            check(name + ": the three surviving months", True)
        check(name + ": the ring is one dashed circle",
              svg.count('class="fd-holes"') == 1 and "stroke-dasharray" in svg)
        check(name + ": one sun, one moon, rays",
              svg.count('class="fd-sun"') == 1 and
              svg.count('class="fd-moon"') == 1 and
              svg.count('class="fd-ray"') == 8)
        # the two discs must actually clear each other, disc + ray extent
        # (6.5 degrees of offset once drew them overlapping; the rendered
        # pixels caught it, this check keeps catching it)
        import re as _re
        sun = _re.search(r'fd-sun" cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', svg)
        moon = _re.search(r'fd-moon" cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', svg)
        if sun and moon:
            sx, sy, sr2 = map(float, sun.groups())
            mx, my, mr2 = map(float, moon.groups())
            clear = math.hypot(mx - sx, my - sy) - sr2 * 2.1 - mr2
            check(name + ": moon clears sun disc and rays", clear >= 0,
                  "clearance %.1f" % clear)
        else:
            check(name + ": moon clears sun disc and rays", False, "marks missing")
        # the month lane: every label's ink-box corners clear both calendar
        # frames by four units (the diagonal-corner graze the browser caught)
        cx2 = 320.0 if name == "wide" else 170.0
        cy2 = 210.0 if name == "wide" else 218.0
        size2 = 12.5 if name == "wide" else 16.5
        rm = (148.0 + 26 + 26) if name == "wide" else (138.0 + 26 + 30)
        r_zodiac_out_holder[0] = 148.0 if name == "wide" else 138.0
        mc = month_corner_clearance(cx2, cy2, rm, size2)
        check(name + ": month corners clear the frames", mc >= 4.0,
              "clearance %.1f" % mc)
        check(name + ": token inks only",
              "#" not in svg.replace('href="#', "") or
              all(t not in svg for t in ('fill="#', 'stroke="#')))
        check(name + ": count line present",
              ">the sun and moon<" in svg)
        # every text has a measured size
        import re
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        need = {12.5: [s for s in ZODIAC] + [m for m, _ in MONTHS],
                16.5: [s for s in ZODIAC] + [m for m, _ in MONTHS]}
        key = 12.5 if name == "wide" else 16.5
        missing = [s for s in need[key] if (s, key) not in MEASURED]
        check(name + ": every Greek string measured", not missing)

    print("front-dial self-test %s" % ("ok" if not worst else "FAILED"))
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    write(FIG / "front-dial-wide.svg", build_wide())
    write(FIG / "front-dial-tall.svg", build_tall())
    sys.exit(self_test())
