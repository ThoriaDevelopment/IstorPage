#!/usr/bin/env python3
"""Assert that nothing a visitor can read is machine-written or untrue — Stage 9's checks 10 and 11.

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
    11  No published page offers Istor for download, calls it open source, or
        links a releases page, while there is no release.

Four decisions worth knowing about, because each is a place these checks could
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
* **Check 11 is the design plan's own rule, made executable.** §10.4 says
  "Nothing on istor.fyi may claim the source is available until it is". In prose,
  that rule had been obeyed on the landing page only: when this check was added,
  75 library pages still offered a "Download" and eight comparison pages called
  Istor open source and MIT licensed, while the landing page's own FAQ said "Not
  yet. The repository is public and empty." A rule that lives only in prose is
  applied to whichever page somebody happens to open, so both halves of it are
  assertions now.

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

# ------------------------------------------------- check 11: the release claims
# §10.4, executable. Deliberately narrow: an openness term in the same SENTENCE
# as the product's own name, an offer to download it, or a link to a releases
# page. Every competitor comparison on this site names other open-source tools
# in good faith, and a check that read those as lies would be turned off within
# a week. The sentence is the unit because the openness word and the name often
# share a line in a comparison while belonging to different subjects.
OPENNESS = re.compile(r"\bopen[-\s]?sourc\w*|\bMIT\b|\bGPLv?[23]?\b|\bApache-2\.0\b", re.I)
ISTOR = re.compile(r"\bistor\b", re.I)
# "downloading it" is about a model file, and this copy uses that phrasing a
# dozen times, so the offer has to name the product or the product's installer
# rather than lean on a pronoun.
OFFER = re.compile(r"\b(?:download|get|install|try)\s+(?:istor|the app|the installer)\b"
                   r"|\bistor'?s? (?:download|installer)\b", re.I)
RELEASES = re.compile(r"releases/(?:latest|tag)", re.I)
SENTENCE = re.compile(r"(?<=[.!?])\s+")
# A URL is not a claim. llms.txt is markdown, so every one of its links carries
# the domain in its target, and "the open-source engine" sat four words away from
# "istor.fyi" in a sentence about llama.cpp. Strip the targets, keep the link
# text, which is what a reader sees.
URLISH = re.compile(r"\]\([^)]*\)|https?://\S+|\bwww\.\S+")
# Published plain-text surfaces. llms.txt is written for machine readers, so a
# stale claim there travels further than one on a page nobody opens.
TEXT_SURFACES = ("llms.txt",)
CLAIM_CONTROL_PROSE = (
    "Istor is open source and MIT licensed, so download Istor today. "
    "Istor's code is under the GPL."
)
CLAIM_CONTROL_MIN = 3
# The table control is the sharper one: it puts a false claim in the Istor column
# and a TRUE one about a different product in the next column, so a detector that
# merely finds an openness word near a table name fails it. Only the paired cell
# may fire.
CLAIM_CONTROL_TABLE = """<table>
  <thead><tr><th scope="col"></th><th scope="col">Istor</th><th scope="col">Other tool</th></tr></thead>
  <tbody><tr><td>License</td><td>MIT, open source</td><td>Apache-2.0</td></tr></tbody>
</table>"""

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

PAGES_EXPECTED = 78          # 77 urls in the sitemap, plus 404.html

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


class Tables(HTMLParser):
    """A comparison table's data cells, each paired with its column header.

    A cell inherits its subject from the header two rows above it, so no sentence
    contains both the name and the claim: the header says "Istor" and the cell
    says "MIT, open source". That is the exact shape of the defect this check
    exists for, and it is invisible to a prose scan, so tables are read
    structurally instead. Assumes one header row of <th> cells, which is what
    every comparison table on this site uses.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables = 0
        self.headers: list[str] = []
        self.row: list[str] = []
        self.cell: list[str] = []
        self.in_cell = False
        self.header_cell = False
        self.claims: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self.tables += 1
            self.headers = []
        elif self.tables and tag == "tr":
            self.row = []
        elif self.tables and tag in ("td", "th"):
            self.in_cell, self.header_cell, self.cell = True, tag == "th", []

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self.tables:
            self.tables -= 1
        elif self.tables and tag in ("td", "th") and self.in_cell:
            text = " ".join("".join(self.cell).split())
            self.in_cell = False
            if self.header_cell:
                self.headers.append(text)
                return
            i = len(self.row)
            self.row.append(text)
            subject = self.headers[i] if i < len(self.headers) else ""
            if ISTOR.search(subject) and OPENNESS.search(text):
                self.claims.append(f'{subject} column: "{text}"')

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell.append(data)


def claim_hits(text: str) -> list[tuple[str, str]]:
    """Every (kind, the sentence) in one document's PROSE that breaks §10.4.

    Lines are split before sentences, because a table's rows have no full stop in
    them: sentence-splitting the whole document glued a comparison table's header
    cell to a cell six rows later and reported a sentence nobody wrote.
    """
    hits: list[tuple[str, str]] = []
    for line in URLISH.sub(" ", text).splitlines():
        for raw in SENTENCE.split(line):
            s = " ".join(raw.split())
            if not s:
                continue
            if ISTOR.search(s) and OPENNESS.search(s):
                hits.append(("calls Istor open source", s))
            if OFFER.search(s):
                hits.append(("offers a download", s))
    return hits


def table_claims(html: str) -> list[str]:
    """Every openness claim sitting in the Istor column of a comparison table."""
    p = Tables()
    p.feed(html)
    p.close()
    return p.claims


def claim_control(rep: Report) -> None:
    """Same doctrine as the tell detector: fail on purpose before trusting silence."""
    prose = claim_hits(CLAIM_CONTROL_PROSE)
    label = "the release-claim detector fires on copy that breaks the rule"
    if len(prose) >= CLAIM_CONTROL_MIN:
        rep.ok(label, f"positive control: {len(prose)} prose claims")
    else:
        rep.fail(label, f"positive control produced only {len(prose)} claims, so a "
                        f"clean result below would mean nothing")

    table = table_claims(CLAIM_CONTROL_TABLE)
    label = "the table reader attributes a cell to its column, not to the page"
    if len(table) == 1:
        rep.ok(label, "positive control: the Istor cell fired, the neighbour did not")
    else:
        rep.fail(label, f"positive control produced {len(table)} table claims, "
                        f"expected exactly one — the Istor column fired or the "
                        f"next column did, and either way this reads cells wrongly")


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

    # Parsed once and shared: check 11 reads the same visible text, and the two
    # checks must never disagree about what a page says.
    parsed = {p: visible_lines(p) for p in pages}

    excused: list[tuple[str, str, str]] = []
    offenses: list[tuple[str, str, str, str]] = []
    for path in pages:
        rel = path.relative_to(site).parent.as_posix()
        rel = "index" if rel == "." else rel
        for group, text, line in scan(parsed[path]):
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
    print("11  the release claims  (SITE_DESIGN_PLAN_V2.md \u00a710.4)")
    claim_control(rep)

    surfaces: list[tuple[pathlib.Path, str]] = []
    for path in pages:
        rel = path.relative_to(site).as_posix()
        surfaces.append((path, "/" + (rel[: -len("index.html")]
                                       if rel.endswith("index.html") else rel)))
    for name in TEXT_SURFACES:
        p = site / name
        if p.is_file():
            surfaces.append((p, "/" + name))

    claims: list[tuple[str, str, str]] = []
    for path, where in surfaces:
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = "\n".join(parsed[path]) if path in parsed else raw
        for kind, sentence in claim_hits(text):
            claims.append((kind, sentence, where))
        for cell in table_claims(raw):
            claims.append(("calls Istor open source in a table", cell, where))
        for m in RELEASES.finditer(raw):
            claims.append(("links a releases page", m.group(0), where))

    for kind, sentence, where in claims:
        rep.fail(f"{kind} on {where}",
                 sentence if len(sentence) <= 160 else sentence[:157] + "...")
    if not claims:
        rep.ok("no release claims in any published text",
               f"{len(surfaces)} pages and text surfaces")

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"copy ok - {rep.checks} assertions, Stage 9 checks 10 and 11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
