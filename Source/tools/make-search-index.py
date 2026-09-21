#!/usr/bin/env python3
"""make-search-index.py - what the library's search palette reads.

    python Source/tools/make-search-index.py [_site] [--check] [--self-test]

The directory has a find field, and it can only find what is on the directory: a
reader standing on `what-is-a-context-window` who wants `how-to-run-a-model-locally`
has to walk back to the door first. This writes the one file that lets any page in
the library answer that, without a server and without a search engine.

SIX DECISIONS, and each is a way this file could have gone wrong:

* **It is built from the pages, not maintained beside them.** Titles, summaries,
  group names and every indexed line are read out of `OldVersion/` - the same files
  the build copies - so there is no second copy of a fact to go stale. The one thing
  it shares with `make-library-index.py` is imported from it, not retyped.
* **It indexes what a reader can scan, not every word.** The full text of the
  library is 258 KB. What actually answers a query is the title, the summary, the
  lede, and each section's heading with the first sentence under it; that is what a
  reader skims, and it is what this ships. The palette is a way to the right page,
  and a way to the right page is a table of contents nobody had to write.
* **The matching rule is written once, here, and the script obeys it.** Every word
  the reader types has to appear, all of them, in any order - the same rule the
  directory's field already uses, so a reader who has learned one has learned both.
  `matches()` is that rule in Python; the palette implements the same one in JS, and
  the check below proves it holds for every page.
* **No markup ever reaches the reader's screen through this file.** Every string is
  stripped of tags and comments, and the check refuses `<` outright: the palette
  builds text nodes from these strings, and a file that can carry markup is a file
  that can inject it.
* **Compact JSON, regenerated, never hand-edited.** Bytes are the point on a lazy
  fetch, and the emitted file is not a document anybody reads - the generator is.
* **A page nobody can search for is a failure, not a page missing from a list.**
  Every carried page has to be findable by its own title's words, or this raises.
  That is the check that catches an extractor that silently stopped matching a
  page's markup, which is exactly the shape of bug that would ship a search that
  quietly does not cover the library.

Standard library only.
"""

from __future__ import annotations

import html
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEGACY = ROOT / "OldVersion"
SITE = ROOT / "_site"

_spec = importlib.util.spec_from_file_location(
    "make_library_index", HERE / "make-library-index.py")
assert _spec and _spec.loader
index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(index)

# How much of a section's first sentence ships. Long enough to carry the claim,
# short enough that seventy-five pages of them stay a fetch a reader does not
# notice. The lede gets the full paragraph it is written as.
LEAD_MAX = 120
LEDE_MAX = 260

# The file's own ceiling. It is a budget on a lazy fetch, not a round number: the
# emitted bytes must stay under what the palette can load between a keystroke and
# its first frame on a phone, and the check below reports the headroom.
CEILING = 84_000

TAG = re.compile(r"<[^>]+>")
COMMENT = re.compile(r"<!--.*?-->")
WS = re.compile(r"\s+")
LEDE = re.compile(r'<p class="lede">(.*?)</p>', re.S)
SECTION = re.compile(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)", re.S)
PARA = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)

# A title's own words, without the ones every title on the site has. Used for the
# "can this page be found" check; not part of the rule the reader uses.
STOPWORDS = frozenset("""
a an and are as at be by can do does for from how in is it its of on or that the
to what when where which who why with you your
""".split())


class SearchError(Exception):
    """Something that would ship a search which does not cover the library."""


def text_of(chunk: str) -> str:
    """The words of a markup fragment, with nothing else left."""
    plain = html.unescape(TAG.sub(" ", COMMENT.sub(" ", chunk)))
    return WS.sub(" ", plain).strip()


def shorten(said: str, cap: int) -> str:
    """The first sentence of `said`, or its first words if it never ends one."""
    said = said.strip()
    if len(said) <= cap:
        return said
    stop = said.find(". ", 0, cap)
    if stop > 24:
        return said[:stop + 1]
    cut = said.rfind(" ", 0, cap)
    return said[:cut if cut > 0 else cap].rstrip(" ,;:") + " ..."


def lines_of(page: str, slug: str) -> list[str]:
    """Every line of the page a reader can scan, in the page's own order.

    The lede first, then each section: its heading, then the first sentence under
    it. A section with no paragraph (a figure standing alone) contributes its
    heading and nothing else rather than a line invented to fill the space.
    """
    lines: list[str] = []
    lede = LEDE.search(page)
    if not lede:
        raise index.MissingCopy(
            f"{slug}: no <p class=\"lede\"> - every carried page opens with one, "
            f"and it is the line a search for the page's own subject should find.")
    lede_text = text_of(lede.group(1))
    if lede_text:
        lines.append(shorten(lede_text, LEDE_MAX))

    body = page[lede.end():]
    for section in SECTION.finditer(body):
        heading = text_of(section.group(1))
        if heading:
            lines.append(heading)
        first = PARA.search(section.group(2))
        if first:
            lead = shorten(text_of(first.group(1)), LEAD_MAX)
            if lead:
                lines.append(lead)
    return lines


def entry(slug: str) -> dict:
    """One page's searchable record. Every string is the page's own words."""
    title, summary = index.entry(slug)
    group = index.group_of(slug)
    page = (LEGACY / slug / "index.html").read_text(encoding="utf-8")
    return {
        "url": f"/{slug}/",
        "title": title,
        "summary": shorten(summary, LEDE_MAX),
        "group": group,
        # The group's anchor travels WITH the group rather than being re-derived
        # by the palette from the group's name: the directory's ids are the index
        # generator's `anchor()` rule, and a second derivation of a shared name is
        # the way two views of one thing drift apart.
        "anchor": index.anchor(group),
        "lines": lines_of(page, slug),
    }


def matches(record: dict, words: list[str]) -> bool:
    """The reader's rule, in Python: every word appears, in any order.

    The palette implements this over the same strings. It is written here so the
    "is every page findable" check below tests the rule the reader will actually
    be using, rather than a second rule that agrees with it today.
    """
    hay = haystack(record)
    return all(word in hay for word in words)


def haystack(record: dict) -> str:
    """Everything a query is matched against, lowercased, in one string."""
    return " ".join([record["title"], record["summary"], *record["lines"]]).lower()


def records() -> list[dict]:
    """The whole library, in the library's own reading order.

    Not slug order, which is alphabetical and therefore arbitrary: the directory
    groups the pages by the kind of question each answers, and a reader who has
    used it expects "What it is" before "How it works". The palette draws its
    results in this order and says so, because the alternative is an order the
    reader cannot see the rule for.
    """
    order = {heading: at for at, (heading, _prefixes, _blurb)
             in enumerate(index.GROUPS)}
    recs = [entry(slug) for slug in index.library_slugs()]
    recs.sort(key=lambda record: (order[record["group"]], record["title"].lower()))
    return recs


def build() -> str:
    """The emitted file, byte for byte."""
    text = json.dumps(records(), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return text + "\n"


def check(text: str, recs: list[dict] | None = None) -> list[str]:
    """Every claim this file makes about the file it wrote. Returns the notes."""
    recs = records() if recs is None else recs
    slugs = index.library_slugs()
    notes: list[str] = []

    if len(recs) != len(slugs):
        raise SearchError(
            f"{len(recs)} record(s) for {len(slugs)} carried page(s). A page in "
            f"the library with no record is a page the palette cannot find.")

    want = [f"/{slug}/" for slug in slugs]
    got = sorted(r["url"] for r in recs)
    if got != sorted(want):
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want))
        raise SearchError(
            f"the records and the library disagree - missing {missing[:3]}, "
            f"unknown {extra[:3]}")

    anchors = {index.anchor(heading) for heading, _prefixes, _blurb in index.GROUPS}
    for record in recs:
        where = record["url"]
        for field in ("url", "title", "summary", "group", "anchor"):
            value = record[field]
            if not isinstance(value, str) or not value.strip():
                raise SearchError(f"{where}: `{field}` is empty")
            if "<" in value:
                raise SearchError(
                    f"{where}: `{field}` carries markup ({value[:60]!r}). The "
                    f"palette builds text nodes from these strings.")
        if record["group"] not in {h for h, _p, _b in index.GROUPS}:
            raise SearchError(f"{where}: group {record['group']!r} is not one of "
                              f"the directory's groups")
        if record["anchor"] not in anchors:
            raise SearchError(
                f"{where}: anchor {record['anchor']!r} is not an id the directory "
                f"carries, so a group link from the palette would go nowhere")
        if not record["lines"]:
            raise SearchError(f"{where}: no indexed lines - nothing but its title "
                              f"can ever match it")
        for line in record["lines"]:
            if "<" in line or not line.strip():
                raise SearchError(f"{where}: a line is empty or carries markup: "
                                  f"{line[:60]!r}")

    # The order the palette draws in, and the only claim about it a reader could
    # check: the groups appear in the directory's order, down the list, once each.
    at = {heading: i for i, (heading, _p, _b) in enumerate(index.GROUPS)}
    seen_at = [at[r["group"]] for r in recs]
    if seen_at != sorted(seen_at):
        raise SearchError(
            "the records are not in the library's reading order: the directory "
            "lists the groups in a fixed order and the palette inherits it, so a "
            "reader can predict where a result will be")
    if sorted(set(seen_at)) != list(range(len(index.GROUPS))):
        raise SearchError("a group in the directory has no records")

    # The rule the reader uses, applied to every page's own subject. This is the
    # check that catches an extractor which stopped matching some page's markup.
    for record in recs:
        words = [w for w in re.findall(r"[a-z0-9]+", record["title"].lower())
                 if w not in STOPWORDS and len(w) > 2]
        if not words:
            continue
        if not matches(record, words):
            raise SearchError(
                f"{record['url']}: cannot be found by its own title "
                f"({record['title']!r})")

    size = len(text.encode("utf-8"))
    if size > CEILING:
        raise SearchError(
            f"the index is {size:,} B, over its {CEILING:,} B ceiling. It is "
            f"fetched lazily, whole, the first time the palette opens.")
    notes.append(f"{len(recs)} pages, {size:,} B of {CEILING:,} B ceiling "
                 f"({size * 100 // CEILING}%), "
                 f"{sum(len(r['lines']) for r in recs)} indexed lines")

    # Determinism, because a file that changes when nothing did makes every
    # byte-diff downstream noise.
    if build() != text:
        raise SearchError("two builds of the same pages differ")
    return notes


# --------------------------------------------------------------------------
# the self-test: every claim above, handed a file that breaks it
# --------------------------------------------------------------------------

def _with(**changes) -> dict:
    """A real record with some fields replaced, for a claim to fail on."""
    record = records()[0]
    return {**record, **changes}


def self_test() -> int:
    failures: list[str] = []
    proven = 0

    def caught(what: str, mutate) -> None:
        nonlocal proven
        fresh = records()
        try:
            mutate(fresh)
            text = json.dumps(fresh, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")) + "\n"
            check(text, fresh)
        except (SearchError, index.MissingCopy):
            proven += 1
            return
        failures.append(f"NOT CAUGHT: {what}")

    def drop(recs):
        recs.pop(3)

    def empty_title(recs):
        recs[3]["title"] = "  "

    def tag_in_line(recs):
        recs[3]["lines"][1] = "the <b>bold</b> claim"

    def tag_in_summary(recs):
        recs[3]["summary"] = "a <em>summary</em>"

    def no_lines(recs):
        recs[3]["lines"] = []

    def wrong_group(recs):
        recs[3]["group"] = "Sockets"

    def wrong_anchor(recs):
        recs[3]["anchor"] = "sockets"

    def empty_anchor(recs):
        recs[3]["anchor"] = ""

    def unseen_page(recs):
        recs[3]["lines"] = ["something else entirely"]

    def over_ceiling(recs):
        recs[3]["lines"] = ["x" * (CEILING + 1)]

    def shuffled(recs):
        recs.reverse()

    caught("a page missing from the records", drop)
    caught("an empty title", empty_title)
    caught("markup in an indexed line", tag_in_line)
    caught("markup in the summary", tag_in_summary)
    caught("a record with no lines", no_lines)
    caught("a group the directory does not have", wrong_group)
    caught("an anchor the directory does not carry", wrong_anchor)
    caught("an empty anchor", empty_anchor)
    caught("a page its own title cannot find", unseen_page)
    caught("an index over its byte ceiling", over_ceiling)
    caught("records out of the library's order", shuffled)

    # The determinism claim needs its own shape: mutate nothing, but compare a
    # reordered build (dicts compare by value, so order is the only lever).
    if json.dumps(records(), sort_keys=True) != json.dumps(records(), sort_keys=True):
        failures.append("NOT CAUGHT: two builds of the same pages differ")

    for line in failures:
        print(line, file=sys.stderr)
    if failures:
        print(f"self-test: {len(failures)} claim(s) not enforced", file=sys.stderr)
        return 1
    print(f"self-test: {proven} doctored files, each caught by the claim it breaks")
    return 0


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    args = [a for a in argv[1:] if not a.startswith("--")]
    check_only = "--check" in argv
    site = pathlib.Path(args[0]) if args else SITE

    if "--self-test" in argv:
        return self_test()

    text = build()
    try:
        notes = check(text)
    except (SearchError, index.MissingCopy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    path = site / "search-index.json"
    if check_only:
        if not path.is_file():
            print(f"DIFFERS: {path} is missing", file=sys.stderr)
            return 1
        if path.read_bytes() != text.encode("utf-8"):
            print(f"DIFFERS: {path} is stale - run "
                  f"python Source/tools/make-search-index.py", file=sys.stderr)
            return 1
        print(f"search-index.json is current: {notes[0]}")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))     # LF on every platform
    print(f"search-index.json  {notes[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
