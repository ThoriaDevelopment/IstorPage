#!/usr/bin/env python3
"""Generate the three favicons from the two brand marks.

    python Source/tools/make-favicons.py            # write the three outputs
    python Source/tools/make-favicons.py --check    # verify they are current

Outputs, all committed (Stage 0's rule: generators run locally, CI never
regenerates artwork):

    Source/favicon.ico          16/32/48, from Assets/brand/istor-eye.svg
    Source/icon.svg             from Assets/brand/istor-page.svg, + a dark block
    Source/apple-touch-icon.png 180x180, from istor-page.svg, opaque on white

Why icon.svg carries its own media query
----------------------------------------
The marks re-ink through a CSS custom-property contract — `var(--mark-ink,
#171717)` and three siblings. That contract works for **inline** SVG, where the
page's cascade reaches the shapes. It cannot cross the `<img>` boundary, and a
favicon is on the far side of it. An SVG favicon is its own document, so the
query goes inside the file rather than in the page's CSS.

Without it the tab icon is `#171717` ink on a dark tab strip, which measures
1.04:1 against the dark world's gradient edge and 1.25:1 against its core —
the same failure the design plan already records for `<img>` instances of this
mark. An ink that is not there at either end of the gradient.

The dark literals are the design plan's §1 ruling, not the icon file's own
documented pair. istor-page.svg's comment calls for `#56C0EC` / `#2E97F2` on a
dark ground; §1 rejects that hue as the outlier and settles one brand blue at
three steps — `#0066CC` on white, `#4DA3FF` and `#0073E6` on dark. The iris
takes `#4DA3FF` (`--azure-lift`) and the pupil `#0073E6` (`--azure-deep`),
keeping the pupil the darker of the two, which is the direction §1 asks for.
The paper and ink are the Black theme's own measured pair from styles.css.

Rasterizing does NOT rely on Inkscape understanding `var()`
----------------------------------------------------------
Inkscape's support for custom properties varies by version, and a dropped
`var()` silently renders the page shape unfilled rather than failing. So the
two raster sources are passed through `literalize()` first, which resolves every
`var(--name, fallback)` to its fallback — the light mark, which is what a
favicon slot wants by default anyway. `icon.svg` keeps its `var()` calls, and
its `<style>` block declares all four properties in both themes, so it renders
correctly with or without the block.

Uses Inkscape and ImageMagick, resolved through the existing bench.py because
neither is on PATH. Standard library only otherwise.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE.parent           # IstorPage/Source
ROOT = HERE.parents[1]         # IstorPage/
BRAND = ROOT / "Assets" / "brand"

EYE = BRAND / "istor-eye.svg"
PAGE = BRAND / "istor-page.svg"

OUT_ICO = SOURCE / "favicon.ico"
OUT_SVG = SOURCE / "icon.svg"
OUT_TOUCH = SOURCE / "apple-touch-icon.png"

ICO_SIZES = (16, 32, 48)
TOUCH_SIZE = 180

# The mark's contract, in both worlds. Light values are the fallbacks already
# written into both files; dark values are design plan §1's ruling.
LIGHT = {
    "mark-paper": "#FFFFFF",
    "mark-ink":   "#171717",
    "mark-iris":  "#F2726F",
    "mark-pupil": "#D93A3A",
}
DARK = {
    "mark-paper": "#0B0C0F",   # the Black theme's paper, measured
    "mark-ink":   "#E5E8EE",   # its ink — #171717 is the 1.04:1 failure here
    "mark-iris":  "#4DA3FF",   # --azure-lift
    "mark-pupil": "#0073E6",   # --azure-deep
}

VAR = re.compile(r"var\(\s*--([a-z-]+)\s*,\s*([^)]+?)\s*\)")

# Chunks that carry a timestamp and therefore change on every run. Inkscape
# writes tIME; ImageMagick writes three date:* tEXt chunks. Two builds of the
# same 180px render were 137 bytes apart with identical IDATs because of them.
#
# They are stripped here rather than with ImageMagick's
# `-define png:exclude-chunks=`, so the guarantee is visible in this file and
# does not depend on which tool wrote the pixels last. `--check` is only useful
# if a rebuild is byte-stable.
TIMESTAMPED_CHUNKS = {b"tIME", b"tEXt", b"zTXt", b"iTXt"}


def strip_png_metadata(path: pathlib.Path) -> None:
    """Rewrite a PNG keeping every chunk except the ones that carry a clock."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"error: {path.name} is not a PNG")
    out = [data[:8]]
    i = 8
    while i < len(data):
        length = int.from_bytes(data[i:i + 4], "big")
        kind = data[i + 4:i + 8]
        end = i + 12 + length           # length + type + body + CRC
        if kind not in TIMESTAMPED_CHUNKS:
            out.append(data[i:end])
        if kind == b"IEND":
            break
        i = end
    path.write_bytes(b"".join(out))


def literalize(svg: str) -> str:
    """Resolve every `var(--name, fallback)` to its fallback.

    A rasterizer that does not implement custom properties renders an
    unresolved `fill` as none, which loses the page shape without any error.
    Resolving first makes the raster deterministic on any Inkscape version.
    """
    return VAR.sub(lambda m: m.group(2), svg)


def dark_block() -> str:
    """The `<style>` that carries icon.svg's literals in both themes.

    Kept to one line per world: a favicon is bytes fetched on every page load,
    and the four declarations are the whole file's reason for existing.
    """
    light = ";".join(f"--{k}:{v}" for k, v in LIGHT.items())
    dark = ";".join(f"--{k}:{v}" for k, v in DARK.items())
    return (
        "<style>\n"
        f"  svg{{{light}}}\n"
        f"  @media (prefers-color-scheme: dark){{svg{{{dark}}}}}\n"
        "</style>\n"
    )


def build_icon_svg() -> str:
    svg = PAGE.read_text(encoding="utf-8")
    if "<style" in svg:
        sys.exit("error: istor-page.svg already has a <style>; this script adds one")
    if VAR.search(svg) is None:
        sys.exit(
            "error: istor-page.svg has no var() contract left. Either the mark was\n"
            "       flattened to literals upstream, or the naming changed. The dark\n"
            "       block below is keyed on those property names."
        )
    marker = ">"
    head_end = svg.index(marker) + 1
    return svg[:head_end] + "\n" + dark_block() + svg[head_end:].lstrip("\n")


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"error: {' '.join(cmd[:3])} … failed\n{proc.stdout}{proc.stderr}")


def rasterize(inkscape: str, svg_text: str, size: int, out: pathlib.Path,
              flatten_white: bool, magick: str) -> None:
    """Render `svg_text` to a PNG of `size` x `size`."""
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "in.svg"
        src.write_text(svg_text, encoding="utf-8")
        run([
            inkscape, str(src),
            "--export-type=png",
            f"--export-filename={out}",
            f"--export-width={size}",
            f"--export-height={size}",
        ])
        if flatten_white:
            # iOS composites transparency onto black, so an apple-touch-icon
            # must be opaque. Flatten onto --paper rather than letting the
            # platform pick the ground.
            run([magick, str(out), "-background", LIGHT["mark-paper"],
                 "-alpha", "remove", "-alpha", "off", str(out)])
        strip_png_metadata(out)


def build(inkscape: str, magick: str, into: pathlib.Path) -> dict[str, pathlib.Path]:
    """Write the three outputs into `into`. Returns {name: path}."""
    eye = literalize(EYE.read_text(encoding="utf-8"))
    page = literalize(PAGE.read_text(encoding="utf-8"))

    pngs = []
    for size in ICO_SIZES:
        png = into / f"favicon-{size}.png"
        rasterize(inkscape, eye, size, png, flatten_white=False, magick=magick)
        pngs.append(png)
    ico = into / "favicon.ico"
    run([magick, *[str(p) for p in pngs], str(ico)])

    touch = into / "apple-touch-icon.png"
    rasterize(inkscape, page, TOUCH_SIZE, touch, flatten_white=True, magick=magick)

    icon = into / "icon.svg"
    # Bytes, not text: `write_text` translates "\n" to os.linesep and this file
    # came out CRLF on Windows while the whole library is LF-only.
    icon.write_bytes(build_icon_svg().encode("utf-8"))

    return {"favicon.ico": ico, "icon.svg": icon, "apple-touch-icon.png": touch}


def main(argv: list[str]) -> int:
    import bench

    check = "--check" in argv
    inkscape = bench.find("inkscape")

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        # magick is only needed for the flatten and the ico; find it lazily so
        # --check on a machine without it still reports on the committed files.
        try:
            magick = bench.find("magick")
        except SystemExit:
            if check:
                magick = "magick"
            else:
                raise
        made = build(inkscape, magick, tmp)

        outputs = {"favicon.ico": OUT_ICO, "icon.svg": OUT_SVG,
                   "apple-touch-icon.png": OUT_TOUCH}

        if check:
            stale = []
            for name, dest in outputs.items():
                if not dest.is_file():
                    stale.append(f"{dest.name}: MISSING")
                elif dest.read_bytes() != made[name].read_bytes():
                    stale.append(f"{dest.name}: differs from a fresh build")
            if stale:
                print("STALE:\n  " + "\n  ".join(stale), file=sys.stderr)
                return 1
            print("current: " + ", ".join(
                f"{n} ({p.stat().st_size:,} B)" for n, p in sorted(outputs.items())
            ))
            return 0

        for name, dest in outputs.items():
            dest.write_bytes(made[name].read_bytes())
        for name, dest in sorted(outputs.items()):
            print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
