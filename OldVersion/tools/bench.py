#!/usr/bin/env python3
"""Resolve the asset bench's binaries.

Why this exists
---------------
Two of the bench tools are installed on this machine but are **not on PATH**,
verified 2026-09-18:

    blender    C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe
    inkscape   C:\\Program Files\\Inkscape\\bin\\inkscape.exe

`magick`, `ffmpeg`, `python`, `node` and `uv` are on PATH and need no help.

Without this module every generator re-derives the same candidate list, and each
one drifts. `mark-export.py` grew exactly such a list before this file existed.

Usage
-----
As a library, from another generator in this directory:

    import bench
    blender = bench.find("blender")

On the command line, to see the state of the bench:

    python tools/bench.py

Notes
-----
* Nothing here is shipped. The site serves files, never tools.
* `find()` exits with an actionable message rather than raising, because every
  caller is a build script whose only useful response is to tell a human what to
  install.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Absolute locations to try, in order, when a tool is not on PATH. These are
# installers' own locations on Windows, plus the usual Unix ones so the same
# script works on a second machine.
CANDIDATES: dict[str, list[str]] = {
    "blender": [
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/usr/bin/blender",
    ],
    "inkscape": [
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
        "/usr/bin/inkscape",
    ],
    "magick": [
        r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe",
        "/usr/bin/magick",
        "/usr/local/bin/magick",
    ],
    "ffmpeg": [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ],
}

# Where to send someone when a tool is missing entirely.
INSTALL_HINT = {
    "blender": "https://www.blender.org/download/",
    "inkscape": "https://inkscape.org/release/",
    "magick": "https://imagemagick.org/script/download.php",
    "ffmpeg": "https://ffmpeg.org/download.html",
}

# The Blender install directory carries the version, so a hardcoded path goes
# stale on the first upgrade. Scan for whatever is actually there and take the
# highest version, rather than pinning one that will rot.
BLENDER_ROOTS = [
    Path(r"C:\Program Files\Blender Foundation"),
    Path("/Applications"),
]


def _newest_blender() -> str | None:
    """Return the newest installed blender.exe, or None."""
    found: list[tuple[tuple[int, ...], Path]] = []
    for root in BLENDER_ROOTS:
        if not root.is_dir():
            continue
        for child in root.glob("Blender*/blender.exe"):
            # "Blender 5.2" -> (5, 2). Anything unparseable sorts last.
            parts = child.parent.name.replace("Blender", "").strip().split(".")
            key = tuple(int(p) for p in parts if p.isdigit())
            found.append((key or (0,), child))
    if not found:
        return None
    found.sort(key=lambda pair: pair[0])
    return str(found[-1][1])


def find(tool: str, explicit: str | None = None) -> str:
    """Return a usable path to `tool`.

    Resolution order: an explicit path from the caller, then PATH, then the
    candidate locations above. Exits with an actionable message if none work.
    """
    if explicit:
        if Path(explicit).is_file():
            return explicit
        sys.exit(f"error: --{tool} points at {explicit}, which is not a file")

    on_path = shutil.which(tool)
    if on_path:
        return on_path

    if tool == "blender":
        scanned = _newest_blender()
        if scanned:
            return scanned

    for cand in CANDIDATES.get(tool, []):
        if Path(cand).is_file():
            return cand

    where = INSTALL_HINT.get(tool, "")
    sys.exit(
        f"error: could not find {tool} on PATH or in any known location.\n"
        f"       Install it from {where}\n"
        f"       or pass an explicit path."
    )


def probe(tool: str) -> tuple[str, str]:
    """Return (status, detail) for the bench report. Never exits."""
    try:
        return "found", find(tool)
    except SystemExit:
        return "MISSING", INSTALL_HINT.get(tool, "")


def main() -> int:
    print("Asset bench as resolved on this machine\n")
    width = max(len(t) for t in CANDIDATES)
    missing = 0
    for tool in CANDIDATES:
        status, detail = probe(tool)
        if status == "MISSING":
            missing += 1
        print(f"  {tool:<{width}}  {status:<7}  {detail}")

    print("\nOn PATH, no resolution needed:")
    for tool in ("python", "node", "uv", "git"):
        path = shutil.which(tool)
        print(f"  {tool:<{width}}  {'found' if path else 'MISSING':<7}  {path or ''}")

    if missing:
        print(f"\n{missing} bench tool(s) missing. Generators that need them will stop.")

    # ASCII only. Windows consoles default to cp1252 and turn any non-ASCII
    # character in stdout into a UnicodeEncodeError, which is the exact bug
    # DESIGN.md records against the APCA skill. Do not put a middle dot here.
    print(f"\npython {sys.version.split()[0]} | platform {os.name}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
