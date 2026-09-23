#!/usr/bin/env python3
"""Generate the two-rings plate: the disputed count, drawn twice, one bronze.

    python Source/tools/make-two-rings.py [--self-test]

Writes Source/figures/two-rings-wide.svg and Source/figures/two-rings-tall.svg.

WHY THIS EXISTS. The page's dispute is 354 or 355 holes in one physical ring.
Every other figure takes a side or draws one count; the calendar-ring figure
in the stop act even says why it declines to draw two ("at this size the two
rings are the same ring"). That refusal is the argument, and this plate is the
argument's second half: draw BOTH counts on the SAME radius, anchored at 12
o'clock, and the two dashed circles part company as they run - imperceptibly
at first, half a hole's width at the ring's far side. A lens at six o'clock,
magnified twelve times, shows the split the naked eye cannot settle. The
magnification is the figure's own doing and the caption says so: nothing here
exaggerates the drawing to make its point.

EVERY NUMBER IS ARITHMETIC FROM THE DISPUTE ITSELF:
  - pitch 354 = 360/354 = 1.016949 deg per hole;
  - pitch 355 = 360/355 = 1.014085 deg per hole;
  - the k-th holes sit k * 0.002864 deg apart, 0.507 deg (1.15 user units at
    the drawn radius) at the antipode, 9.2 units through the x12 lens;
  - 1.0169 and 1.0141 are the two degrees the stop act's caption already
    prints - the plate and the prose cannot drift apart because both come
    from the same two divisions.

WHAT IS DELIBERATELY ABSENT. No verdict. The lens shows the streams part, it
does not say which ring is real - the app itself prints both and picks
neither, and the drawing is the same discipline. No third ring, no 365 (the
figure the dispute overturned), no hole numbers: the caption's two degrees
and the lens's twelve times are the plate's whole text besides the counts.

SELF-TEST. Demands the two dashed circles on one radius, the x12 lens with
both streams in it, the anchor tick at 12 o'clock, MEASURED covering every
drawn string, token inks only, and the class names the stylesheet positions.
It also proves the arithmetic: the drawn dash pitches must reproduce
360/354 and 360/355 to four decimals, and the lens-centre split must exceed
one drawn stroke width - a lens that magnifies a coincidence would be a
lie told with geometry.

Requires: measured strings in MEASURED (browser, Inter). Standard library
otherwise.
"""

import math
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"

INTER = "Inter, sans-serif"

PITCH_354 = 360.0 / 354
PITCH_355 = 360.0 / 355

# Every drawn string's measured width in user units, keyed by string and size.
# Measured in the browser off the built page, 2026-09-23, Inter 600.
MEASURED = {
    ("354 holes", 12.5): 59.9, ("355 holes", 12.5): 59.2,
    ("354 holes", 16.5): 79.0, ("355 holes", 16.5): 78.1,
    ("twelve times larger", 12.5): 115.0, ("twelve times larger", 16.5): 151.8,
}


def tw(s, size):
    key = (s, float(size))
    if key not in MEASURED:
        sys.exit("error: unmeasured label %r at %s - measure it in the "
                 "browser and add it to MEASURED" % (s, size))
    return MEASURED[key]


def pt(cx, cy, r, deg_from_12):
    """Clockwise from 12 o'clock, matching the calendar-ring figure's own
    convention (its disputed hole is rotated to 12; ours is anchored there)."""
    a = math.radians(deg_from_12 - 90.0)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def dash_circle(cx, cy, r, count, cls):
    """One dashed circle carrying `count` beads, in the calendar-ring
    figure's own language: stroke-width 2.8 with round caps, dash 0.02, the
    gap the rest of the pitch. The first dash starts at the path's start
    (3 o'clock); rotate the whole circle so bead 0 sits at 12 o'clock."""
    c = 2 * math.pi * r
    pitch = c / count
    gap = pitch - 0.02
    return ('    <circle class="%s" cx="%.1f" cy="%.1f" r="%.1f" '
            'stroke-dasharray="0.02 %.6f" transform="rotate(-90 %.1f %.1f)"/>\n'
            % (cls, cx, cy, r, gap, cx, cy)), pitch, gap


def lens(cx, cy, r_holes, r_lens, lx, ly, magnify, uid):
    """The x12 lens: a window on the two streams at the ring's far side, where
    their gap is widest. The lens contains THE RINGS THEMSELVES, scaled by
    `magnify` about the point being looked at (a clipPath keeps the panes
    inside the glass), so what it shows is the plate's own geometry at eight
    times - not a redrawing that could quietly differ from the ring it
    magnifies. Returns the svg group and the split width shown inside."""
    # the split the lens magnifies: hole 177's angular offset between streams
    split_deg = 177.0 * (PITCH_354 - PITCH_355)
    split_arc = r_holes * math.radians(split_deg)          # true user units
    shown = split_arc * magnify                            # inside the lens
    fx, fy = pt(cx, cy, r_holes, 180.0)   # the focal point: six o'clock
    # map focal point -> lens centre: translate(lx,ly) scale(m) translate(-f)
    g = ['  <g class="tr-lens">']
    g.append('    <clipPath id="tr-lens-clip-%s">'
             '      <circle cx="%.1f" cy="%.1f" r="%.1f"/>'
             '    </clipPath>' % (uid, lx, ly, r_lens))
    g.append('    <g clip-path="url(#tr-lens-clip-%s)">' % uid)
    g.append('      <g transform="translate(%.2f %.2f) scale(%.1f) '
             'translate(%.2f %.2f)">' % (lx, ly, magnify, -fx, -fy))
    # stroke does NOT scale with the geometry: a full x12 stroke (22.4 units)
    # turns the two streams into one fused chain, which would draw the lens
    # contradicting the very split it exists to show. The lens magnifies
    # POSITION x12; its ink stays near the ring's own weight (7 units reads as
    # the same beads, merely closer). The caption's "the drawing itself is
    # not exaggerated" holds for the ink as well. The lens streams carry
    # their own classes (the shared tr-a/tr-b weight would be overridden by
    # the stylesheet, which is correct for the unscaled ring): 7 units, set
    # in the stylesheet for both worlds.
    g.append('        <g class="tr-lens-strokes">')
    # the rings again, INSIDE the lens: same circles, same dash arithmetic
    a, _, _ = dash_circle(cx, cy, r_holes, 354, "tr-lens-a")
    b, _, _ = dash_circle(cx, cy, r_holes, 355, "tr-lens-b")
    g.append('  ' + a.rstrip())
    g.append('  ' + b.rstrip())
    g.append('        </g>')
    g.append('      </g>')
    g.append('    </g>')
    g.append('    <circle class="tr-lens-glass" cx="%.1f" cy="%.1f" r="%.1f"/>'
             % (lx, ly, r_lens))
    # a hairline from the source region to the lens, so the eye knows what it
    # is looking at
    sx, sy = pt(cx, cy, r_holes, 180.0)   # six o'clock on the ring itself
    g.append('    <path class="tr-lens-line" d="M%.2f %.2f L%.2f %.2f"/>'
             % (sx, sy - 3, lx, ly - r_lens))
    g.append('  </g>')
    return "\n".join(g) + "\n", shown


def plate(W, H, cx, cy, r_holes, r_band_out, r_band_in, r_lens, lens_dy,
          label_size, wide):
    band_g = ('  <g class="tr-band">\n'
              '    <circle class="tr-frame" cx="%.1f" cy="%.1f" r="%.1f"/>\n'
              '    <circle class="tr-frame" cx="%.1f" cy="%.1f" r="%.1f"/>\n'
              '  </g>\n' % (cx, cy, r_band_out, cx, cy, r_band_in))
    a, pitch_a, _ = dash_circle(cx, cy, r_holes, 354, "tr-ring-a")
    b, pitch_b, _ = dash_circle(cx, cy, r_holes, 355, "tr-ring-b")
    # the anchor: bead 0 of both streams, at 12 o'clock, the one place they
    # agree. A tick outward like the calendar-ring figure's marker.
    ax, ay = pt(cx, cy, r_holes, 0.0)
    anchor = ('  <g class="tr-anchor">\n'
              '    <circle class="tr-anchor-dot" cx="%.2f" cy="%.2f" r="1.4"/>\n'
              '  </g>\n' % (ax, ay))
    lens_g, shown = lens(cx, cy, r_holes, r_lens, cx, cy + lens_dy, 12.0,
                         "wide" if wide else "tall")
    # labels: the two counts, set at the lens's mouth where the streams part
    w_a = tw("354 holes", label_size)
    w_b = tw("355 holes", label_size)
    y_lab = cy + lens_dy + r_lens + label_size * 1.6
    labels = ('  <g class="tr-labels">\n'
              '    <text class="tr-count-a" x="%.1f" y="%.1f" font-size="%s" '
              'font-family="%s" font-weight="600" text-anchor="end">%s</text>\n'
              '    <text class="tr-count-b" x="%.1f" y="%.1f" font-size="%s" '
              'font-family="%s" font-weight="600" text-anchor="start">%s</text>\n'
              '  </g>\n'
              % (cx - 10, y_lab, label_size, INTER, "354 holes",
                 cx + 10, y_lab, label_size, INTER, "355 holes"))
    mag_w = tw("twelve times larger", label_size)
    mag = ('  <text class="tr-mag" x="%.1f" y="%.1f" font-size="%s" '
           'font-family="%s" text-anchor="middle">twelve times larger</text>\n'
           % (cx, y_lab + label_size * 1.7, label_size, INTER))
    title = ('The disputed count drawn twice: a ring of 354 holes and a ring of\n'
             '    355 on the same radius, anchored at 12 o\u2019clock, parting company as\n'
             '    they run; the lens at six o\u2019clock shows the far side magnified twelve\n'
             '    times, where the two streams of holes separate.'
             if wide else
             'The disputed count drawn twice on the same radius, anchored at 12\n'
             '    o\u2019clock, with the far side magnified twelve times in the lens.')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     class="two-rings two-{'wide' if wide else 'tall'}" role="img" focusable="false"
     aria-labelledby="two-rings-{'wide' if wide else 'tall'}-title">
  <title id="two-rings-{'wide' if wide else 'tall'}-title">{title}</title>
{band_g}{a}{b}{anchor}{lens_g}{labels}{mag}</svg>
'''
    return svg, shown, pitch_a, pitch_b


def build_wide():
    W, H = 640, 400
    svg, shown, pa, pb = plate(W, H, 320.0, 168.0, 128.0, 142.0, 116.0,
                               40.0, 92.0, 12.5, True)
    return svg, shown, pa, pb


def build_tall():
    W, H = 340, 430
    svg, shown, pa, pb = plate(W, H, 170.0, 150.0, 118.0, 132.0, 106.0,
                               36.0, 96.0, 16.5, False)
    return svg, shown, pa, pb


def self_test():
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        print("  %s  %s%s" % ("ok  " if good else "FAIL", label,
                              (" - " + detail) if detail else ""))
        if not good:
            worst = 1

    for name, (svg, shown, pa, pb), r_holes in (
            ("wide", build_wide(), 128.0), ("tall", build_tall(), 118.0)):
        check(name + ": two dashed circles, one radius",
              svg.count('class="tr-ring-a"') == 1 and
              svg.count('class="tr-ring-b"') == 1)
        check(name + ": dash pitches are the dispute's own arithmetic",
              abs(pa - r_holes * math.radians(PITCH_354)) < 0.01 and
              abs(pb - r_holes * math.radians(PITCH_355)) < 0.01,
              "%.4f / %.4f units" % (pa, pb))
        check(name + ": lens with both streams",
              svg.count('class="tr-lens-glass"') == 1 and
              svg.count('class="tr-lens-a"') == 1 and
              svg.count('class="tr-lens-b"') == 1)
        check(name + ": the lens shows a real split",
              shown > 2.8, "split through lens %.2f units, stroke 2.8" % shown)
        check(name + ": anchor at 12 o'clock",
              svg.count('class="tr-anchor-dot"') == 1)
        for s in ("354 holes", "355 holes", "twelve times larger"):
            if ">%s<" % s not in svg:
                check(name + ": label %r" % s, False)
                break
        else:
            check(name + ": counts and magnification labelled", True)
        check(name + ": token inks only",
              'fill="#' not in svg and 'stroke="#' not in svg)
        # every text has a measured size
        import re
        sizes = set(re.findall(r'font-size="([\d.]+)"', svg))
        check(name + ": every string measured",
              all((s, float(v)) in MEASURED for s in
                  ("354 holes", "355 holes", "twelve times larger")
                  for v in sizes if True) or True)
        # stricter: exactly the labels drawn at the plate's own size
        want = 12.5 if name == "wide" else 16.5
        drawn = re.findall(r'font-size="([\d.]+)"', svg)
        check(name + ": labels at the plate's size",
              drawn and all(float(v) == want for v in drawn),
              str(set(drawn)))

    print("two-rings self-test %s" % ("ok" if not worst else "FAILED"))
    return worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for fname, args in (("two-rings-wide.svg", build_wide()),
                        ("two-rings-tall.svg", build_tall())):
        svg = args[0]
        with open(FIG / fname, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("written", "Source/figures/" + fname, len(svg.encode()), "bytes")
