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
    ("exhibit-12-reading", "Black/FetchingPages.png", "1200x928+400+44",
     "the reading log - domain by domain, the only capture showing real fetching"),
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
     "354.08 holes at 99.99%; radial variation 0.028 mm"),
]

AVIF_Q = "60"
WEBP_Q = "82"
PNG_Q = "92"


def run(*args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"failed: {' '.join(str(a) for a in args)}\n{r.stderr.strip()}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    print(f"{'exhibit':24} {'2x (px)':>12} {'css':>10} {'bytes':>10}")
    for name, src, crop, _note in EXHIBITS:
        path = SHOTS / src
        if not path.exists():
            raise SystemExit(f"missing source capture: {src}")

        tmp = OUT / f".{name}.tmp.png"
        run("magick", path, "-crop", crop, "+repage", str(tmp))

        w, h = (int(v) for v in subprocess.run(
            ["magick", "identify", "-format", "%w %h", str(tmp)],
            capture_output=True, text=True).stdout.split())

        # 2x: the crop at its native capture size. 1x: exactly half.
        #
        # The `!` is load-bearing. Without it, ImageMagick treats the geometry as
        # a bounding BOX to fit inside, not an exact size: exhibit-17's crop is
        # 1918x1015, so a box of 959x507 fits at min(959/1918, 507/1015) = 0.4995
        # and comes out 958 wide. The markup's width/height are read off the file,
        # so a one-pixel shortfall there would be a one-pixel aspect error in the
        # document. Force the size; the odd height is inherent (1015 is odd) and
        # costs half a pixel of vertical scale across a 480px-tall exhibit.
        for suffix, geom, fmt, q in [
            ("@2x", f"{w}x{h}!", "avif", AVIF_Q),
            ("@2x", f"{w}x{h}!", "webp", WEBP_Q),
            ("", f"{w // 2}x{h // 2}!", "avif", AVIF_Q),
            ("", f"{w // 2}x{h // 2}!", "webp", WEBP_Q),
        ]:
            dest = OUT / f"{name}{suffix}.{fmt}"
            run("magick", str(tmp), "-resize", geom, "-quality", q, str(dest))
            total += dest.stat().st_size

        print(f"{name:24} {w:>5}x{h:<6} {w // 2:>5}x{h // 2:<4} {total:>10,}")
        tmp.unlink()

    print(f"\n{len(EXHIBITS)} exhibits x4 files = {len(EXHIBITS) * 4} files, {total:,} B")


if __name__ == "__main__":
    sys.exit(main())
