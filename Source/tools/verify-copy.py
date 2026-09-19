#!/usr/bin/env python3
"""Assert that nothing a visitor can read was written by a chatbot — Stage 9's check 10.

    python Source/tools/verify-copy.py [_site]

`verify-budget.py` asks whether the bytes are right. `verify-links.py` asks
whether the site is right: links, contrast, codepoints, the library's crossing.
This one asks whether the WRITING is right, against the `humanizer` skill at
`~/.claude/skills/humanizer`, which the brief names as the standard for every
text a normal visitor can see on istor.fyi.

Before this file existed, two narrower things had been established: the landing
page was rewritten by hand against the skill, and a gate in verify-links.py
asserted that no published page contains an em or en dash. Dashes are one tell
out of sixteen. The rest of the skill's vocabularies were cleared by reading
whichever pages somebody happened to open, which is a different and much weaker
claim than "every page". This closes it.

    10  No published page's VISIBLE text contains a high-confidence AI tell.

Three decisions worth knowing about, because each is a place this check could
have gone wrong:

* **Only the high-confidence vocabularies are encoded.** The skill also names
  softer patterns — the rule of three, "superficial -ing analyses", inflated
  significance carried by whole sentences. A detector for those cannot be made
  precise enough to act on unattended, and a gate that cries wolf is worse than
  no gate, because it teaches its reader to skip the output.
* **The detector has to pass a positive control on every run.** A scan that has
  never been shown to fail is not evidence, and this repository has already been
  burned by that: twice in one night a measurement of ours reported a defect that
  did not exist. So a crafted page carrying known tells is scanned first, and if
  the detector does not fire on it the tool fails outright — "no hits" from a
  broken detector must never read as a clean bill of health.
* **An allowlist entry is a claim about the writing, so it carries its reason
  and the excused count is printed.** A phrase can be a tell in one sentence and
  the right word in another. Every entry below is a deliberate keep, and the
  total is reported on every run so the list cannot grow without being seen.

Standard library only — no `pip install` in CI.
"""

from __future__ import annotations

import pathlib
import re
import sys
from html.parser import HTMLParser

# --------------------------------------------------------- the tell vocabularies
# Grouped by the pattern each comes from in the skill, so a hit says which tell
# it is rather than only that a word matched.
TELLS: dict[str, list[str]] = {
    "significance": [
        r"is a testament to", r"a testament to the", r"stands as a", r"serves as a",
        r"underscores the importance", r"highlights the importance",
        r"reflects? broader", r"symboli[sz]es? (?:the|its) ongoing",
        r"setting the stage for", r"marks a (?:shift|turning point)",
        r"key turning point", r"evolving landscape", r"ever-evolving",
        r"indelible mark", r"deeply rooted", r"pivotal (?:role|moment)",
        r"vital role",
    ],
    "ing-analysis": [
        r"highlighting the", r"underscoring the", r"emphasizing the",
        r"ensuring that", r"reflecting the", r"symboli[sz]ing the",
        r"contributing to the", r"cultivating ", r"fostering ",
        r"encompassing ", r"showcasing ",
    ],
    "promotional": [
        r"\bboasts\b", r"\bvibrant\b", r"\bprofound\b", r"in the heart of",
        r"\bnestled\b", r"\bgroundbreaking\b", r"\brenowned\b", r"\bbreathtaking\b",
        r"must-visit", r"enhancing its",
    ],
    "vague-attribution": [
        r"industry reports", r"observers have (?:cited|noted)",
        r"experts argue", r"some critics argue", r"studies have shown",
    ],
    "formulaic-challenge": [
        r"faces several challenges", r"despite these challenges",
        r"challenges and legacy", r"future outlook",
    ],
    "vocabulary": [
        r"\bdelv(?:e|es|ing)\b", r"\btapestry\b", r"in the realm of",
        r"in the world of", r"in today's", r"when it comes to",
        r"\bleverage\b", r"\butili[sz]e", r"\bplethora\b", r"\bmyriad\b",
        r"\bseamless", r"\bgame.?changer", r"cutting-edge",
        r"state-of-the-art", r"\brevolutioni[sz]e", r"\bempower",
        r"harness the power", r"\bunleash", r"\bunlock the potential",
        r"\belevate\b", r"\bsupercharge\b", r"\bturbocharge\b",
        r"\bdive into\b", r"let's dive",
        r"everything you need to know", r"we've got you covered",
        r"look no further", r"the perfect blend", r"say goodbye to",
        r"\bnavigat(?:e|ing) the (?:complex|world|landscape)",
        r"it(?:'s| is) important to note", r"it(?:'s| is) worth noting",
        r"at the end of the day", r"the (?:key|secret) is that",
        r"whether you'?re a",
    ],
    "negative-parallelism": [
        r"not only .{1,60} but also", r"isn'?t just", r"not just a\b",
        r"more than just", r"is not a tool but",
    ],
    "chatbot-residue": [
        r"i hope this helps", r"let me know if", r"\bcertainly!", r"of course!",
        r"would you like me to", r"want me to", r"should i continue",
        r"here is a (?:list|breakdown|summary)",
    ],
}

# Hits that are in the copy on purpose. Keyed by (group, the matched text) and
# pointing at the one page it is allowed on, so a second use of the same phrase
# anywhere else still fails.
ALLOWED: dict[tuple[str, str], tuple[str, str]] = {
    ("vocabulary", "leverage"): (
        "what-is-prompt-engineering",
        "\"real leverage over the shape of an answer and no leverage over its "
        "truth\": the concrete noun, not the corporate verb, and the repetition "
        "is the sentence's whole construction",
    ),
    ("negative-parallelism", "more than just"): (
        "what-is-a-gguf",
        "\"encodes more than just the bit depth\": a quantity the code carries, "
        "not the \"more than just a tool, it is\" device the skill names",
    ),
}

# The positive control. Every one of these must fire, or the detector is broken
# and this tool's silence means nothing.
CONTROL = """<h2>Control</h2>
<p>This tool is a testament to the evolving landscape of local AI, highlighting the need for care.</p>
<p>It is important to note that you should delve into the pristine tapestry of options.</p>
<p>This is more than just a tool. Let me know if you want to continue.</p>
<p>High-<strong>quality</strong> output, seamlessly integrated.</p>
"""
CONTROL_MIN_HITS = 8
CONTROL_MIN_GROUPS = 5

PAGES_EXPECTED = 77          # 76 urls in the sitemap, plus 404.html

BLOCK = {
    "p", "div", "section", "article", "header", "footer", "nav", "main", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "td", "th", "dt", "dd",
    "figcaption", "blockquote", "pre", "table", "thead", "tbody", "ul", "ol",
    "br", "hr", "form", "label", "button", "fieldset", "legend",
}
SKIP = {"script", "style", "svg", "head", "template", "noscript"}


class Report:
    """Collects pass/fail lines so one run reports everything, not just the first.

    Deliberately a copy of verify-budget.py's and verify-links.py's: these are
    separate entry points named by the build plan, and a shared module for
    fifteen lines would be a fourth file to keep in step with all three.
    """

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def ok(self, label: str, detail: str = "") -> None:
        self.checks += 1
        print(f"  ok    {label}" + (f"  {detail}" if detail else ""))

    def fail(self, label: str, detail: str) -> None:
        self.checks += 1
        self.failures.append(f"{label}: {detail}")
        print(f"  FAIL  {label}  {detail}", file=sys.stderr)


class Visible(HTMLParser):
    """A page's visible text, with the two joining rules this check depends on.

    Block tags become a newline and inline tags become NOTHING. Deleting every
    tag would join the end of one paragraph to the start of the next and
    manufacture phrases across the seam; inserting a space for every tag instead
    would split "high-" from "quality" and manufacture hyphen fragments. Block =
    newline, inline = join is the only pair that reproduces what a reader sees,
    and getting it wrong is not hypothetical: an extraction bug of exactly this
    shape once had this project editing 49 files over 145 spaces that did not
    exist.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCK and not self.skip:
            self.out.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP and self.skip:
            self.skip -= 1
        elif tag in BLOCK and not self.skip:
            self.out.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.out.append(data)

    def lines(self) -> list[str]:
        raw = "".join(self.out).split("\n")
        return [ln for ln in (" ".join(x.split()) for x in raw) if ln]


def visible_lines(path: pathlib.Path) -> list[str]:
    p = Visible()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    p.close()
    return p.lines()


def scan(lines: list[str]) -> list[tuple[str, str, str]]:
    """Every (group, matched text, the line it is on) in the given lines."""
    hits: list[tuple[str, str, str]] = []
    for line in lines:
        for group, pats in TELLS.items():
            for pat in pats:
                for m in re.finditer(pat, line, re.I):
                    hits.append((group, m.group(0).lower(), line))
    return hits


def control(rep: Report) -> None:
    """Prove the detector fires before trusting its silence."""
    p = Visible()
    p.feed(CONTROL)
    p.close()
    hits = scan(p.lines())
    groups = {g for g, _t, _l in hits}
    label = "the detector fires on a page of known tells"
    if len(hits) >= CONTROL_MIN_HITS and len(groups) >= CONTROL_MIN_GROUPS:
        rep.ok(label, f"positive control: {len(hits)} hits over {len(groups)} groups")
    else:
        rep.fail(label, f"positive control produced only {len(hits)} hits over "
                        f"{len(groups)} groups, so a clean result below would mean "
                        f"nothing")


def main(argv: list[str]) -> int:
    # The Windows console is cp1252 by default, and the excerpts this file prints
    # are quoted published prose, which contains curly quotes and the like.
    # Same fix and same reason as verify-links.py: mojibake in the one line a
    # reader looks at costs more time than the encoding call does.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    site = pathlib.Path(argv[1] if len(argv) > 1 else "_site")
    if not site.is_dir():
        print(f"error: {site} is not a directory — run build-site.py first",
              file=sys.stderr)
        return 1

    rep = Report()

    print("10  the copy")
    control(rep)

    pages = sorted(p for p in site.rglob("*")
                   if p.is_file() and p.suffix.lower() in (".html", ".htm"))
    rep.ok("pages scanned", f"{len(pages)} html files")
    if len(pages) < PAGES_EXPECTED:
        rep.fail("pages scanned", f"only {len(pages)} pages, expected at least "
                                  f"{PAGES_EXPECTED} — a scan of nothing finds nothing")

    excused: list[tuple[str, str, str]] = []
    offenses: list[tuple[str, str, str, str]] = []
    for path in pages:
        rel = path.relative_to(site).parent.as_posix() or "index"
        for group, text, line in scan(visible_lines(path)):
            keep = ALLOWED.get((group, text))
            if keep and rel == keep[0]:
                excused.append((group, text, rel))
            else:
                offenses.append((group, text, rel, line))

    for group, text, rel, line in offenses:
        i = line.lower().index(text)
        lo, hi = max(0, i - 60), min(len(line), i + len(text) + 60)
        rep.fail(f"{group} on /{rel}/", f"{line[lo:i]}[{line[i:i + len(text)]}]{line[i + len(text):hi]}")

    if not offenses:
        rep.ok("no AI tells in any visible text",
               f"{len(pages)} pages, {sum(len(TELLS[g]) for g in TELLS)} patterns")

    total = len(excused)
    rep.ok("allow-list", f"{total} deliberate keep(s), {len(ALLOWED)} entries declared")
    for group, text, rel in excused:
        print(f"        kept  {group:20s} {text!r} on /{rel}/")
    for (group, text), (rel, why) in ALLOWED.items():
        if not any(g == group and t == text for g, t, _r in excused):
            rep.fail("allow-list", f"{group}/{text!r} is declared for /{rel}/ but "
                                   f"never matched — drop the entry rather than let "
                                   f"it excuse a future hit ({why})")

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"copy ok - {rep.checks} assertions, Stage 9 check 10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
