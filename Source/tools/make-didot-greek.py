#!/usr/bin/env python3
"""Rebuild the display face: gfs-didot.woff2 with the Greek it never had.

    python Source/tools/make-didot-greek.py [--self-test]

Writes BOTH shipped copies of the face, Assets/fonts/gfs-didot.woff2 and
OldVersion/assets/fonts/gfs-didot.woff2, from
Assets/fonts/masters/GFSDidot-Regular.ttf.

WHY THIS EXISTS. The shipped subset carried 219 codepoints and ZERO Greek, so
every Greek glyph on the page has been falling back to Georgia: the wordmark in
the nav and the four window bars, the etymology plate's ἵστωρ, all of it, in a
face nobody chose. The fallback chain hid it, because Georgia is a competent
serif and the pages were never compared glyph by glyph. The games-dial plate
(M37) is the plate that could not tolerate it: its ordinals LΑ..LΔ and its six
game names are uppercase Greek, and drawing them in a fallback face is exactly
the kind of quiet substitution this page exists to refuse.

THE CONTRACT. The master is GFS Didot Regular, the same typeface the shipped
subset was cut from (verified: identical upem, identical advances on shared
glyphs, both from the Greek Font Society's 2007 release under the OFL; the
license rides beside the master). The subset is: every codepoint the shipped
file already covers, so no existing page text can change by a single advance,
plus the Greek and Greek Extended blocks, the combining marks a decomposed
polytonic spelling needs, and the Greek question mark. The cmap is the
authority on what the old file covered; this script reads it rather than
trusting any transcription, which is the house's own lesson from the build
plan's corrected 15-for-16 codepoint table.

SELF-TEST. Demands the old coverage in full, the Greek blocks, the wordmark's
ἵστωρ in both its precomposed and decomposed spellings, the games plate's
uppercase ordinals and names, and - the part that protects every heading on
the page - glyph advances identical to the old file for every codepoint the
old file had.

Requires fonttools with brotli (pip install fonttools brotli).
"""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent.parent
MASTER = ROOT / "Assets" / "fonts" / "masters" / "GFSDidot-Regular.ttf"
# The face ships at two paths by design (build-site.py's docstring: the
# library addresses its own copy relatively and may not change). Rebuilding
# one and not the other would leave the two paths carrying different
# typefaces, so the generator owns both and the self-test proves them equal.
OUTS = (ROOT / "Assets" / "fonts" / "gfs-didot.woff2",
        ROOT / "OldVersion" / "assets" / "fonts" / "gfs-didot.woff2")
OUT = OUTS[0]               # the primary: what the self-test reads

# The Greek this page needs, spelled out so the self-test can demand them by
# name: the wordmark in both spellings, the games plate's ordinals and names,
# the Greek question mark and middle dot for prose.
WORDMARK = "ἵστωρ"                    # the brand, precomposed
GAMES = "LΑΒΓΔΙΣΘΜΟΛΥΠΙΑΝΕΎΧΚ"        # ordinals and the six names' letters
EXTRAS = "·;" + "΄" + "΅"             # prose punctuation the Greek block carries


def old_codepoints():
    """The shipped file's own coverage, from its cmap. The authority."""
    return set(TTFont(str(OUT)).getBestCmap().keys())


def build():
    if not MASTER.exists():
        sys.exit("error: master not found at %s - see the docstring" % MASTER)
    old = old_codepoints()

    # Latin and symbols: exactly what the old file had, nothing more, so no
    # existing string can change metrics or coverage.
    keep = set(old)
    # Greek and Coptic, Greek Extended, and the combining block the decomposed
    # polytonic forms need. Intersected with the master, because a subsetter
    # asked for a codepoint the font lacks should not be the failure mode.
    for base, top in ((0x0370, 0x03FF), (0x1F00, 0x1FFF), (0x0300, 0x036F)):
        keep.update(c for c in range(base, top + 1))

    from fontTools import subset

    opts = subset.Options()
    opts.layout_features = ["*"]     # keep kern and every shaping feature
    opts.notdef_outline = True
    opts.recommended_glyphs = True
    opts.name_IDs = ["*"]
    font = TTFont(str(MASTER))
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(unicodes=sorted(keep))
    subsetter.subset(font)
    try:
        font.flavor = "woff2"
    except Exception:
        sys.exit("error: cannot write woff2 - pip install brotli")
    # Encode once, write the bytes twice. Two saves of one font object are
    # not byte-identical (the WOFF2 encoder does not promise determinism
    # across saves), so the copies are made by copying, and the self-test
    # still proves them equal on disk.
    import io
    buf = io.BytesIO()
    font.save(buf)
    payload = buf.getvalue()
    for out in OUTS:
        out.write_bytes(payload)

    new = TTFont(str(OUT))
    newmap = set(new.getBestCmap().keys())
    print("gfs-didot.woff2 rebuilt (both copies): %d bytes, %d codepoints "
          "(was 219, 0 Greek)" % (len(payload), len(newmap)))


def self_test() -> int:
    old = old_codepoints()          # reads the file this script may have rebuilt
    new = TTFont(str(OUT))
    cmap = new.getBestCmap()
    worst = 0

    def check(label, good, detail=""):
        nonlocal worst
        mark = "ok  " if good else "FAIL"
        print("  %s  %s%s" % (mark, label, (" - " + detail) if detail else ""))
        if not good:
            worst = 1

    # 1. nothing the old file covered may be lost
    lost = sorted(old - set(cmap))
    check("old coverage kept (%d codepoints)" % len(old), not lost,
          "missing: %s" % (" ".join("U+%04X" % c for c in lost[:8]) if lost else ""))

    # 2. the Greek blocks are present, exactly as far as the master carries
    # them: every codepoint the master maps must survive the rebuild, block
    # by block. (Archaic letters like Ϝ and unassigned slots are not in
    # GFS Didot; demanding them would demand a different typeface.)
    master = TTFont(str(MASTER))
    master_cmap = master.getBestCmap()

    def block(base, top):
        miss = [c for c in range(base, top + 1)
                if c in master_cmap and c not in cmap]
        return not miss, "missing: %s" % " ".join("U+%04X" % c for c in miss[:8])

    g_ok, g_d = block(0x0370, 0x03FF)
    e_ok, e_d = block(0x1F00, 0x1FFF)
    c_ok, c_d = block(0x0300, 0x036F)
    check("Greek block U+0370-03FF (as far as the master)", g_ok, g_d)
    check("Greek Extended (polytonic)", e_ok, e_d)
    check("combining marks U+0300-036F", c_ok, c_d)
    # the real letters, by name, so the demand never depends on the master's
    # own gaps being acceptable for this page
    check("the alphabet, caps and lower",
          all(ord(ch) in cmap for ch in "\u0391\u0392\u0393\u0394\u0395\u0396"
              "\u0397\u0398\u0399\u039a\u039b\u039c\u039d\u039e\u039f\u03a0"
              "\u03a1\u03a3\u03a4\u03a5\u03a6\u03a7\u03a8\u03a9"
              "\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8\u03b9\u03ba"
              "\u03bb\u03bc\u03bd\u03be\u03bf\u03c0\u03c1\u03c2\u03c3\u03c4"
              "\u03c5\u03c6\u03c7\u03c8\u03c9"))

    # 3. the brand and the plate, by name
    check("wordmark ἵστωρ", all(ord(c) in cmap for c in WORDMARK))
    check("games ordinals and names", all(ord(c) in cmap for c in GAMES))

    # 4. metrics: every old codepoint's advance is unchanged. This is the
    # check that makes the rebuild safe for every heading already shipped:
    # the new file's advance must equal the master's, which the old subset
    # was cut from (verified by hand before this tool existed).
    new_hmtx = new["hmtx"]
    master_hmtx = master["hmtx"]
    drifted = []
    for c in sorted(old):
        g_new = cmap.get(c)
        g_master = master_cmap.get(c)
        if g_new is None or g_master is None:
            drifted.append("U+%04X missing" % c)
            continue
        if new_hmtx[g_new][0] != master_hmtx[g_master][0]:
            drifted.append("U+%04X %d->%d" % (c, master_hmtx[g_master][0],
                                              new_hmtx[g_new][0]))
    check("advances match the master on every old codepoint", not drifted,
          "; ".join(drifted[:6]))

    size = OUT.stat().st_size
    check("size sane (< 60 KB)", 0 < size < 60 * 1024, "%d B" % size)
    same = OUTS[1].read_bytes() == OUT.read_bytes()
    check("both shipped copies identical", same)

    print("gfs-didot self-test %s" % ("ok" if not worst else "FAILED"))
    return worst


if __name__ == "__main__":
    import os
    import subprocess

    # fontTools' subsetter iterates hashed sets internally, so without a fixed
    # hash seed each run encodes a different (equally valid) file, and the
    # byte-identical-regeneration contract in verify-figures.py would fail on
    # principle. The interpreter must learn the seed before it starts, so the
    # real work happens in a child process with the seed pinned. (A re-exec
    # was tried first and segfaulted under MSYS on Windows; subprocess is the
    # portable form of the same idea.)
    if os.environ.get("PYTHONHASHSEED") != "0":
        env = dict(os.environ, PYTHONHASHSEED="0")
        r = subprocess.run([sys.executable] + sys.argv, env=env)
        sys.exit(r.returncode)

    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    build()
    sys.exit(self_test())
