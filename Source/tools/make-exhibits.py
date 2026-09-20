"""Crop the shipped exhibits out of the raw captures, and export them for the web.

Every crop here is derived from a measurement of its own source file — the pane
split is NOT constant across captures (the answer column was measured at x=538,
550 and 561 in three different files), so no crop inherits another's bounds.

Geometry rule (SITE_DESIGN_PLAN_V2 §3.1):
    The captures are 1918px wide and are a 2x capture of a 959 CSS-px window.
    So display_width_css = crop_width_px / 2, which is exact at 1x AND 2x with
    no upscaling, and renders the app's own 16-17px text at its native size.

Outputs, per exhibit, into Assets/Exports/:
    <name>.avif  <name>.webp          at 1x  (crop / 2)
    <name>@2x.avif  <name>@2x.webp    at 2x  (crop at native capture size)

And, for the exhibits listed in PHONE, a second art-directed crop:
    <name>-phone.avif  <name>-phone@2x.avif   (and the webp pair)

WHY A PHONE CROP EXISTS AT ALL. The rule above — crop / 2 rendered at the
measured width — holds the app's text at its native size only when the browser
has that much room. On a 390px viewport the exhibit frame is 285 CSS px, so a
1200px crop (600 CSS px of app UI) renders at 0.475 and the app's 16px text
arrives at 7.6px: measured on 2026-09-19, and the reason the exhibits were the
one place the page failed the legibility the report ranks as load-bearing. A
600px-wide crop of the same window is 300 CSS px, which is what a common phone's
frame actually is, so it renders at 0.85 to 1.0 — near native or better — and the
text becomes readable instead of a grey smear.

What gets one, and what deliberately does not:
  * The four answer-bearing exhibits, cropped to the pane. Their claim lives in
the answer's own prose, which is exactly what the crop keeps.
  * exhibit-13 does NOT: it is a two-column disputed-claims table whose columns
together span the whole 860px crop. Any crop narrow enough to be legible on a
phone cuts either the claim or the status it is disputed against, which is the
exhibit's entire content. It stays at 0.66.
  * exhibits 14 and 15 do NOT: their crops are already 800 and 793px (0.71), and
their claim spans the full width of the settings panel — a row's label on the
left, its toggle or value on the right. Cropping to one column would cut the
value off the claim.
  * exhibits 16 and 17 do NOT: they are full-window overviews of a 1918px window
whose claim is the LAYOUT (sources left, notes right, the answer between), so a
larger scale would destroy the only thing they show.

Each phone rect is a sub-rect of its own desktop crop rather than a new
measurement against the source capture, so it inherits that crop's bounds and
cannot drift from them.

Generators run locally and their outputs are committed; CI never regenerates
artwork. Run from the repo root:  python Source/tools/make-exhibits.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "Assets" / "Istor Screenshots"
OUT = ROOT / "Assets" / "Exports"

# (name, source file, crop as WxH+X+Y, note)
#
# Bounds measured 2026-09-19 with .improvement/tools/measure-capture.py and
# .improvement/tools/modal-bounds.py. The y origin is 44 in every pane crop:
# y0-43 is the app's own title bar, y44 is the rule under it, and the title bar
# is dropped so our own --r-win radius frames the window rather than stacking a
# second title bar inside it. The two full-window exhibits keep it.
EXHIBITS = [
    ("exhibit-10-gate", "Black/Question1.png", "1200x884+359+44",
     "the grounding disclosure: question, the reasoning line, the answer"),
    ("exhibit-11-citations", "Black/verifiedsource.png", "1200x876+359+44",
     "the cited answer; carries the M4 witness interaction"),
    # exhibit-12-reading RETIRED 2026-09-20. Act 4's exhibit is a live DOM replica
    # now (see the markup note in act 4 of Source/index.html): the act's claim is
    # that you watch it read, and a bitmap cannot be watched. Its copy was
    # transcribed into the page from this capture before the crop was dropped, so
    # nothing was lost but the bytes. Regenerate with the line above restored if a
    # future act ever needs the capture as a bitmap again.
    ("exhibit-13-dispute", "Black/Question2.png", "860x960+540+44",
     "the twelve-row disputed-claims table, kept rather than resolved"),
    ("exhibit-14-research", "Black/settingsresearch.png", "800x568+560+226",
     "Web research off, keyless scrape, no API keys"),
    ("exhibit-15-models", "White/settingsmodels.png", "793x460+560+20",
     "Local model server at http://localhost:11434"),
    ("exhibit-16-library", "Black/Sourcesfullscreenmain.png", "1918x1016+0+0",
     "the full library window, dark"),
    ("exhibit-17-notes", "White/notesfullscreenmain.png", "1918x1015+0+0",
     "the full notes window, light"),
    ("exhibit-18-numbers", "Black/Question3.png", "1200x956+359+44",
     "354.08 holes at 68 percent; radial variation 0.028 mm"),
]

# Phone rects, as WxH+X+Y inside the exhibit's own desktop crop. 600px wide for
# the four answers, which is 300 CSS px on the page, chosen because 300 is
# measured as the exhibit frame's own width on a 390-400px viewport (the common
# phone), so the crop fills the frame instead of floating inside it. The y offset
# is 0 for all four: the whole answer column is the subject, and its height is
# the crop's.
PHONE = {
    "exhibit-10-gate": "600x884+540+0",
    "exhibit-11-citations": "600x876+540+0",
    "exhibit-18-numbers": "600x956+540+0",
}

AVIF_Q = "60"
WEBP_Q = "82"
PNG_Q = "92"


def run(*args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"failed: {' '.join(str(a) for a in args)}\n{r.stderr.strip()}")


def emit(tmp: Path, base: str, w: int, h: int) -> int:
    """Write one crop as four files, and return the bytes they add up to.

    The `!` is load-bearing. Without it, ImageMagick treats the geometry as
    a bounding BOX to fit inside, not an exact size: exhibit-17's crop is
    1918x1015, so a box of 959x507 fits at min(959/1918, 507/1015) = 0.4995
    and comes out 958 wide. The markup's width/height are read off the file,
    so a one-pixel shortfall there would be a one-pixel aspect error in the
    document. Force the size; the odd height is inherent (1015 is odd) and
    costs half a pixel of vertical scale across a 480px-tall exhibit.
    """
    total = 0
    for suffix, geom, fmt, q in [
        ("@2x", f"{w}x{h}!", "avif", AVIF_Q),
        ("@2x", f"{w}x{h}!", "webp", WEBP_Q),
        ("", f"{w // 2}x{h // 2}!", "avif", AVIF_Q),
        ("", f"{w // 2}x{h // 2}!", "webp", WEBP_Q),
    ]:
        dest = OUT / f"{base}{suffix}.{fmt}"
        run("magick", str(tmp), "-resize", geom, "-quality", q, str(dest))
        total += dest.stat().st_size
    return total


def size_of_image(path: Path) -> tuple[int, int]:
    out = subprocess.run(["magick", "identify", "-format", "%w %h", str(path)],
                         capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    print(f"{'exhibit':24} {'2x (px)':>12} {'css':>10} {'bytes':>10}  {'phone':>16}")
    for name, src, crop, _note in EXHIBITS:
        path = SHOTS / src
        if not path.exists():
            raise SystemExit(f"missing source capture: {src}")

        tmp = OUT / f".{name}.tmp.png"
        run("magick", path, "-crop", crop, "+repage", str(tmp))
        w, h = size_of_image(tmp)

        bytes_here = emit(tmp, name, w, h)

        phone = ""
        if name in PHONE:
            # Cropped out of the desktop crop, not the capture, so the two can
            # never disagree about where the window is.
            ptmp = OUT / f".{name}-phone.tmp.png"
            run("magick", str(tmp), "-crop", PHONE[name], "+repage", str(ptmp))
            pw, ph = size_of_image(ptmp)
            phone_bytes = emit(ptmp, f"{name}-phone", pw, ph)
            phone = f"{pw // 2}x{ph // 2} {phone_bytes:>8,} B"
            bytes_here += phone_bytes
            ptmp.unlink()

        total += bytes_here
        print(f"{name:24} {w:>5}x{h:<6} {w // 2:>5}x{h // 2:<4} {bytes_here:>10,}  {phone:>16}")
        tmp.unlink()

    files = (len(EXHIBITS) + len(PHONE)) * 4
    print(f"\n{len(EXHIBITS)} exhibits plus {len(PHONE)} phone crops, x4 files = {files} files")
    print(f"{total:,} B over both sets")


if __name__ == "__main__":
    sys.exit(main())
