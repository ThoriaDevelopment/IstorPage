# tools

The generators for any asset on this site that a camera or a designer did not
produce.

## The rule

**A generated asset ships the script that made it.** The script lives here, and
it is committed in the same commit as the asset it produced, with the license,
the source and the exact command recorded beside the file in
`assets/*/SOURCE.md` — exactly as a third-party asset carries its licence.

A generated asset with no committed generator is an unfalsifiable blob. Nobody
can rebuild it, nobody can revise it in six months, and nobody can tell it apart
from something scraped. This directory is what makes that checkable.

The convention is the same one `assets/textures/SOURCE.md` already follows for
the studio photograph: say where the thing came from, say how it was transformed,
and leave the means to do it again.

## Naming

`<what it makes>.<ext>` — `grain-field.py`, `hero-render.blend` plus
`hero-render.py`, `seal-draw.js`. One generator per asset where that is honest,
one generator per family where a family genuinely shares a method.

Shared plumbing is the exception, and it is named for what it is rather than for
an output. `bench.py` resolves tool paths and makes nothing.

A Blender file is a generator and ships for the same reason; the Python that
drives it headless ships beside it, because `blender -b -P script.py` is how it
runs and the `.blend` alone does not say what the script does to it.

## Cost

This directory is tracked, so it counts in the repo-weight row of the loop's
budget table. That cost is small and it is taken deliberately: a few kilobytes of
script against the alternative, which is a megabyte of pixels that nobody can
explain.

## Resolving the tools

`bench.py` is the single place that knows where the bench's binaries live. The
skill's bench table records absolute paths because **Blender and Inkscape are on
no PATH at all**; this module automates that lookup so every generator does not
carry its own copy of the same candidate list and drift from the others.
`mark-export.py` grew exactly that list before this module existed.

```python
import bench
blender = bench.find("blender")
```

Run it on its own to see the state of the machine:

```sh
python tools/bench.py
```

It exits non-zero when a tool is missing, so it works as a preflight check.
Keep its output ASCII: Windows consoles default to cp1252 and raise
`UnicodeEncodeError` on anything else.

## What is on the bench

The full table, with versions, delegate lists and the rules on what may be
installed without asking, is in
[`../.claude/skills/continuous-improvement/SKILL.md`](../.claude/skills/continuous-improvement/SKILL.md)
under "The bench: the tools that make things". That section is the authority on
what the bench *is*; `bench.py` is the authority on *where* each piece is,
because it resolves paths rather than naming them.

Verified on this machine 2026-09-18:

- **Blender 5.2.1 LTS** — 3D, renders, bakes. Headless with `blender -b -P`.
  Not on PATH; installed at `C:\Program Files\Blender Foundation\Blender 5.2\`.
  The `-P` path is verified end to end: a script rendered a PNG and ImageMagick
  read it back. In 5.x the EEVEE engine enum is `BLENDER_EEVEE`; the
  `BLENDER_EEVEE_NEXT` spelling from 4.2 and later is gone and raises
  `TypeError` on assignment.
- **Inkscape 1.4.4** — hand-authored SVG, and rasterising it. Not on PATH;
  installed at `C:\Program Files\Inkscape\bin\`.
- **ImageMagick 7.1.2** — `magick`, for conversion, compositing and optimisation.
  Its delegates carry `webp`, `heic` (which is what encodes AVIF), `lcms` and
  `rsvg`, so it also rasterises SVG. On PATH. **Never `convert`**: on Windows
  that name belongs to the FAT-to-NTFS filesystem tool, and it is destructive.
- **ffmpeg 7.1** — encoding, frame extraction. On PATH.
- **Python 3.14** with PIL, numpy, scipy and matplotlib — procedural raster.
- **Node 24** — build-time only, nothing shipped.

Nothing here reaches the reader. Every generator runs at build time and produces
a file; the site serves the file and never the tool.
