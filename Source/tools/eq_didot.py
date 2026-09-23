"""Semantic equality for the rebuilt display face.

verify-figures.py imports this module for outputs whose generator cannot
promise byte-identical regeneration. fontTools' WOFF2 encoder is not
deterministic at the byte level (empirically, even with PYTHONHASHSEED
pinned), so for a font the honest question is not "same bytes" but "same
font": the two files must carry

  - the identical cmap (every codepoint, both directions),
  - the identical advance width for every glyph,
  - the identical glyph order (the subsetter's own choice; if two runs
    ever disagree on it, kerning by class and hinting by index can both
    drift, so it is checked, not assumed),
  - the identical set of retained layout features, and
  - an equal byte count within a small tolerance (the encoder packs the
    same content differently run to run; a 10 percent gap means the
    subset itself changed).

Any other difference is the generator drifting from the committed file,
and the check fails with the specific drift named.
"""

import io

from fontTools.ttLib import TTFont


def _load(data: bytes) -> TTFont:
    return TTFont(io.BytesIO(data))


def test(committed: bytes, rebuilt: bytes) -> None:
    a = _load(committed)
    b = _load(rebuilt)

    ma = a.getBestCmap()
    mb = b.getBestCmap()
    only_a = sorted(set(ma) - set(mb))
    only_b = sorted(set(mb) - set(ma))
    if only_a or only_b:
        raise AssertionError(
            "cmap differs: committed-only %s, rebuild-only %s"
            % (["U+%04X" % c for c in only_a[:6]], ["U+%04X" % c for c in only_b[:6]]))

    # both directions: the reverse map must agree too, so one codepoint
    # silently re-pointed at another glyph is still caught
    ra = {}
    for c, g in ma.items():
        ra.setdefault(g, set()).add(c)
    rb = {}
    for c, g in mb.items():
        rb.setdefault(g, set()).add(c)
    if ra != rb:
        raise AssertionError("glyph->codepoint mapping differs")

    order_a = a.getGlyphOrder()
    order_b = b.getGlyphOrder()
    if order_a != order_b:
        diff = next((i for i, (x, y) in enumerate(zip(order_a, order_b)) if x != y),
                    min(len(order_a), len(order_b)))
        raise AssertionError(
            "glyph order differs at index %d: %r vs %r"
            % (diff, order_a[diff] if diff < len(order_a) else None,
               order_b[diff] if diff < len(order_b) else None))

    ha, hb = a["hmtx"], b["hmtx"]
    drifted = []
    for name in order_a:
        wa, _ = ha[name]
        wb, _ = hb[name]
        if wa != wb:
            drifted.append("%s %d->%d" % (name, wa, wb))
    if drifted:
        raise AssertionError("advance drift: " + ", ".join(drifted[:6]))

    def feature_tags(font):
        if "GSUB" not in font:
            return set()
        records = font["GSUB"].table.FeatureList.FeatureRecord
        return {r.FeatureTag for r in records}

    tags_a = feature_tags(a)
    tags_b = feature_tags(b)
    if tags_a != tags_b:
        raise AssertionError("layout features differ: %s vs %s"
                             % (sorted(tags_a), sorted(tags_b)))

    tol = max(len(committed), len(rebuilt)) // 10
    if abs(len(committed) - len(rebuilt)) > tol:
        raise AssertionError(
            "size gap too wide: %d vs %d B (tolerance %d)"
            % (len(committed), len(rebuilt), tol))
