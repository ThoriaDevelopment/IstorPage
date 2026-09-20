#!/usr/bin/env python3
"""Assert that istor.fyi's artifact holds together — Stage 9's checks 4 to 9.

    python Source/tools/verify-links.py [_site]

`verify-budget.py` runs checks 1-3 and asks whether the bytes are right. This
one asks whether the SITE is right: that nothing points at a file that is not
there, that the new page keeps the promises §8 makes about behaviour, that the
colours still measure what the design plan says they measure, that no character
falls out of its font, that the home page really is the new one, and that the 75
carried pages survived the crossing.

    4  Every internal href/src resolves inside _site/ — 120 files, and in
       particular the library's relative `assets/fonts/...`, which is the one
       asset a deploy of this shape loses without noticing.
    5  No behaviour — ON THE LANDING PAGE ONLY. Scoped deliberately: all 75
       legacy pages carry an inline script and are published as they are.
    6  Contrast — the six ratios §1 states, recomputed from the tokens in the
       stylesheet, so a token edit cannot leave a comment behind.
    7  Codepoints — every RENDERED non-ASCII character is inside a declared
       `unicode-range`, or is on the one-entry allow-list below.
    8  The home page is the new one. This is the guard for §1.3's silent
       failure, and the reason the assembler copies by allowlist.
    9  Library integrity — 75 pages, the library's /styles.css, self-canonicals,
       the brand files, and the sitemap/llms.txt cross-check both ways.

Three of these are stronger than the plan asks, because the checks are cheap and
the failure they prevent is not:

* **Check 4 also verifies fragments.** `#how-it-answers` is in the page's own
  nav and `#m-fold` is in all 75 library pages; a href that resolves to a file
  but not to an id is still a broken link.
* **Check 6 recomputes from the tokens rather than trusting the table**, and
  asserts the two documented FAILURES as well (the #767676 floor, the rejected
  dark citation pair). A number in a comment that nothing recomputes is a number
  that is wrong within a month — this file was written after finding three.
* **The artifact must be LF-only.** A CRLF `sitemap.xml` already shipped once,
  and the byte-identity test that should have caught it compared decoded strings
  and passed. Check it here, on bytes.

Standard library only — no `pip install` in CI.
"""

from __future__ import annotations

import html as htmllib
import importlib.util
import pathlib
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent

# The library index generator, loaded the same way build-site.py loads it: a
# hyphenated filename cannot be imported by name. The continue-reading walk is
# asserted against the same GROUPS rule that built the directory, so the two
# cannot disagree about where an article's neighbours are.
_spec = importlib.util.spec_from_file_location(
    "make_library_index", HERE / "make-library-index.py")
assert _spec and _spec.loader
make_library_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_library_index)

# ---------------------------------------------------------------- expectations
# A library page is a directory at the artifact root holding an index.html.
# These four are directories at the root that are NOT pages.
# Directories in the artifact that are assets rather than pages.
NOT_A_PAGE = {"fonts", "img", "assets", "brand"}
# A directory in the artifact that holds a page but is not one of the 75 carried
# articles: the library's own index at /library/. It is checked like any other
# page — its 75 links are resolved by check 4 below — but it is not an article,
# so it does not move LIBRARY_PAGES.
NOT_AN_ARTICLE = {"library"}
LIBRARY_TOC = NOT_A_PAGE | NOT_AN_ARTICLE

LIBRARY_PAGES = 75
# §1.1: /styles.css is the library's file. This number is also in budget.json, and
# the duplication is deliberate: the two tools read the same artifact by different
# routes, so a size that only one of them knows about is itself the finding.
LIBRARY_STYLES_BYTES = 50980
ARTIFACT_FILES = 156                  # 138 + the four phone crops' 16 files + the library index
                                      # (9 exhibits x 4 files = 36, was 3 x 6 = 18) + /theme.js

# Check 8's marker. If the assembler ever globs OldVersion/ instead of copying by
# allowlist, the previous home page ships at this path and every other check here
# still passes. This string is the only thing standing between that and a deploy.
HOME_MARKER = "It shows you what it saw"

# Check 7. EMPTY, and that is a v2 result rather than an omission.
#
# Under v1 this held U+2192 (RIGHTWARDS ARROW), which the copy deck spelled eight
# times and which no shipped subset carried — Inter's 230 glyphs have no arrow,
# and neither Didot file does. `unicode-range` chooses among files that HAVE a
# glyph, so declaring it would render tofu; falling through to the system stack
# was correct.
#
# v2's copy deck has no arrow, so nothing falls through and the set is empty.
# The check still asserts it EXACTLY rather than dropping the assertion: an empty
# allow-list that must stay empty is what catches the next unsubsetted codepoint,
# and a check deleted for being empty would catch nothing at all.
FALLS_THROUGH: dict[int, str] = {}

# Check 6. v2's §4, and every figure below was MEASURED from this stylesheet's
# own tokens rather than transcribed from the plan — a plan's rounded figure is a
# description of a ratio, and this is the ratio.
#
# Two pairs are worth reading:
#   * --on-azure on --azure is the CTA, so it is the one ratio a visitor reads
#     text through on every screen of the page.
#   * text in the field is measured against --field-hi, the gradient's LIGHTEST
#     stop. Light text on a lighter ground is the worst case; measuring it
#     against --field-base would assert the easiest one and call it the hardest.
CONTRAST = [
    ("--ink", "--paper", 17.04, "§4: all text on paper"),
    ("--ink-2", "--paper", 5.71, "§4: secondary text on paper"),
    ("--azure", "--paper", 5.33, "§4: the accent on paper"),
    ("--on-azure", "--azure", 5.57, "§4: the CTA's ink on the CTA's fill"),
    ("--coral", "--paper", 5.32, "§4: the mark's artwork before it re-inks"),
    ("--field-ink", "--field-hi", 11.58, "§4: text in the field, worst case"),
    ("--field-ink-2", "--field-hi", 6.07, "§4: secondary text in the field"),
    ("--azure-lift", "--field-hi", 5.19, "§4: the accent in the field, worst case"),
    ("--cite-ink", "--cite-wash", 4.74, "§4: the citation numeral on its wash"),
    ("--on-azure-lift", "--azure-lift-hi", 7.72, "§4: the CTA's ink, hovered"),
    # M9's chips are the one control drawn in the WINDOW's scope rather than the
    # page's, so these two are hex literals for the reason above: the pane is
    # dark in both themes, and `--ink-2` resolves differently inside `.win`.
    ("#8B9199", "#111620", 5.70,
     "the hero chip's label at rest, on the pane's LIGHTEST stop"),
    ("#E5E8EE", "#303033", 10.72,
     "the hero chip's label on the active question, on --fill-card over the pane"),
]

# Asserted to FAIL, so the reasons recorded beside the tokens cannot rot into
# descriptions of pairs that would actually have been fine.
CONTRAST_BELOW_AA = [
    ("--azure-lift", "--cite-wash", 2.23, "why the citation wash keeps the light blue"),
    ("--on-azure", "--azure-lift", 2.63, "why the chip fills with --azure, not --azure-lift"),
    ("--state-ready", "--paper", 2.45, "why --state-ready is a DOT and never text"),
]

AA_NORMAL = 4.5

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "//")


class Report:
    """Collects pass/fail lines so one run reports everything, not just the first.

    Deliberately a copy of verify-budget.py's: the two scripts are separate
    entry points named by the build plan, and a shared module for fifteen lines
    would be a third file to keep in step with both.
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


# ------------------------------------------------------------------- text prep

def strip_css_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def rendered_text(page: str) -> str:
    """The page with its comments gone, what a font could actually be asked for.

    Comments are stripped and the `<style>` block is KEPT, because CSS reaches
    the screen through `content:` as surely as markup does: the `.pipe` arrows
    on this page exist only as `content: "→"`. Check 7 counts those.
    """
    return strip_css_comments(strip_html_comments(page))


def visible_text(page: str) -> str:
    """Return visitor-facing HTML text, excluding code, styles and comments."""
    text = re.sub(r"<script\b.*?</script>", "", page, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", "", text, flags=re.S | re.I)
    text = strip_html_comments(text)
    return re.sub(r"<[^>]+>", " ", text)


# --------------------------------------------------------------- the plan, as data

REPO = HERE.parent.parent                  # the checkout, from Source/tools/
PLAN_DOC = REPO / "Documentation" / "SITE_DESIGN_PLAN_V2.md"
DOCUMENTS = [PLAN_DOC, REPO / "README.md", REPO / "Documentation" / "OVERNIGHT_GOALS.md"]

# The string that makes §2's table THE TABLE: a reformat that breaks this line is a
# failure to re-point the check, not a silent skip. It is the header of the table
# that maps every act to its anchor id, its built headline and its exhibit.
PLAN_TABLE_HEAD = "| # | Act, by anchor id |"


def norm_text(s: str) -> str:
    """One comparable form for a string that exists in two files.

    NFC because act 11's heading is a Greek word carrying a breathing mark and an
    iota subscript: the same word written from a different keyboard can be a
    different byte sequence, and that would be a failure with nothing wrong behind
    it, which is how a check earns the reputation that gets it deleted.
    """
    s = htmllib.unescape(re.sub(r"<[^>]+>", "", s))
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s)).strip()


def plan_act_rows() -> list[list[str]] | None:
    """§2's table as data: one row of cells per numbered act.

    None means the document or the table's header is gone. Callers report that as a
    failure rather than skipping, because a check that goes quiet when its subject
    is renamed is worse than no check: nothing else in this file reads the plan.
    """
    if not PLAN_DOC.exists():
        return None
    rows: list[list[str]] = []
    inside = False
    for line in PLAN_DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith(PLAN_TABLE_HEAD):
            inside = True
            continue
        if inside:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].isdigit():
                rows.append(cells)
    return rows or None


# ------------------------------------------------------------------ css parsing

def css_rules(text: str, inside: str = "") -> list[tuple[str, str, str]]:
    """Every rule as (selector, body, enclosing at-rule), comments removed.

    A small recursive walk rather than a regex: the reduced-motion block nests
    rules inside an @media, and check 5 has to know whether a declaration is in
    there. No declaration on this page contains a brace or a quoted brace, so
    counting braces is sound for this input; it would not be for all CSS.
    """
    text = strip_css_comments(text)
    rules: list[tuple[str, str, str]] = []
    i = 0
    while True:
        j = text.find("{", i)
        if j < 0:
            return rules
        close = text.find("}", i)
        if 0 <= close < j:                      # stray `}` — skip it
            i = close + 1
            continue
        prelude = text[i:j].strip()
        depth, m = 1, j + 1
        while m < len(text) and depth:
            if text[m] == "{":
                depth += 1
            elif text[m] == "}":
                depth -= 1
            m += 1
        body = text[j + 1:m - 1]
        if prelude.startswith("@"):
            inner = f"{inside} {prelude}".strip()
            rules += css_rules(body, inner)
        else:
            rules.append((prelude, body, inside))
        i = m


def declarations(body: str) -> list[tuple[str, str]]:
    """(property, value) pairs from one rule body, `!important` kept."""
    out = []
    for chunk in body.split(";"):
        if ":" not in chunk:
            continue
        prop, value = chunk.split(":", 1)
        out.append((prop.strip().lower(), value.strip()))
    return out


def token_block(css: str, selector: str) -> dict[str, str]:
    """The custom properties declared by one selector, as written."""
    for sel, body, inside in css_rules(css):
        if sel == selector and not inside:
            out = {}
            for prop, value in declarations(body):
                if prop.startswith("--"):
                    out[prop] = value
            return out
    return {}


def hex_of(value: str, tokens: dict[str, str], depth: int = 0) -> str | None:
    """Resolve a token or hex literal to #RRGGBB, following var() aliases."""
    value = value.strip()
    m = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", value)
    if m:
        if depth > 8 or m.group(1) not in tokens:
            return None
        return hex_of(tokens[m.group(1)], tokens, depth + 1)
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})", value)
    return f"#{m.group(1).upper()}" if m else None


# ------------------------------------------------------------------- contrast

def _channel(c: int) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex6: str) -> float:
    h = hex6.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# -------------------------------------------------------------- unicode ranges

def declared_codepoints(css: str) -> set[int]:
    """Every codepoint the stylesheet's `unicode-range`s claim, as a set.

    The union across faces, not per face: a character is reachable if ANY
    shipped file can draw it, and which file is chosen is the browser's business.
    """
    out: set[int] = set()
    for value in re.findall(r"unicode-range\s*:([^;}]+)", strip_css_comments(css)):
        for part in value.split(","):
            part = part.strip()
            if not part.upper().startswith("U+"):
                continue
            body = part[2:].strip()
            if "?" in body:                      # wildcard form, unused here
                lo = int(body.replace("?", "0"), 16)
                out.update(range(lo, lo + 16 ** body.count("?")))
            elif "-" in body:
                a, b = body.split("-", 1)
                out.update(range(int(a, 16), int(b, 16) + 1))
            else:
                out.add(int(body, 16))
    return out


# ------------------------------------------------------------------ references

ATTR = re.compile(
    r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I
)
SRCSET = re.compile(r"""\bsrcset\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
CSS_URL = re.compile(r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]+))\s*\)""", re.I)


def refs_in(path: pathlib.Path, text: str) -> list[str]:
    """Every URL a file asks the browser to fetch, in document order."""
    out: list[str] = []
    if path.suffix.lower() == ".css":
        for m in CSS_URL.finditer(strip_css_comments(text)):
            out.append(next(g for g in m.groups() if g is not None))
        return out
    if path.suffix.lower() not in (".html", ".htm"):
        return out
    for m in ATTR.finditer(text):
        out.append(htmllib.unescape(next(g for g in m.groups() if g is not None)))
    # srcset is a comma-separated list of "url descriptor" pairs.
    for m in SRCSET.finditer(text):
        raw = htmllib.unescape(next(g for g in m.groups() if g is not None))
        for item in raw.split(","):
            item = item.strip()
            if item:
                out.append(item.split()[0])
    return out


def resolve(site: pathlib.Path, ref: str, from_file: pathlib.Path
            ) -> tuple[pathlib.Path | None, str | None, bool]:
    """Resolve one URL against the artifact.

    Returns (target file, fragment, found). `found` is False for a path that is
    not in the artifact. A directory URL resolves to its index.html, and so does
    an extensionless one, because both forms are used in the library.
    """
    frag = None
    if "#" in ref:
        ref, frag = ref.split("#", 1)
    if ref == "":
        return from_file, frag, from_file.is_file()
    if ref.startswith("/"):
        target = site / ref.lstrip("/")
    else:
        target = from_file.parent / ref
    target = pathlib.Path(target)
    if target.is_dir():
        target = target / "index.html"
    elif not target.is_file() and not target.suffix:
        candidate = target / "index.html"
        if candidate.is_file():
            target = candidate
    return target, frag, target.is_file()


def ids_in(text: str) -> set[str]:
    """Every id= (and legacy name=) in a document, for fragment targets."""
    out = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", text))
    out |= set(re.findall(r"""\bname\s*=\s*["']([^"']+)["']""", text))
    return out


# ---------------------------------------------------------------------- checks

def check_4(rep: Report, site: pathlib.Path, docs: dict[pathlib.Path, str]) -> None:
    print("4  every internal href/src resolves")
    broken: list[str] = []
    refs = 0
    for path, text in docs.items():
        for ref in refs_in(path, text):
            if not ref or ref.startswith(EXTERNAL_SCHEMES) or ref.startswith("{"):
                continue
            refs += 1
            target, frag, found = resolve(site, ref, path)
            rel = path.relative_to(site).as_posix()
            if not found:
                broken.append(f"{rel} -> {ref}")
                continue
            if frag:
                # The fragment has to exist in whichever document it lands in.
                if frag not in ids_in(text if target == path
                                      else docs.get(target, target.read_text(
                                          encoding="utf-8", errors="replace"))):
                    broken.append(f"{rel} -> {ref} (no id=\"{frag}\")")
    if broken:
        for b in broken[:20]:
            rep.fail("broken reference", b)
        if len(broken) > 20:
            rep.fail("broken reference", f"and {len(broken) - 20} more")
    else:
        rep.ok(f"{refs} references across {len(docs)} documents",
               "every path and every fragment resolves")


def check_5(rep: Report, page: str) -> None:
    """The composition gate, and the page's behaviour contract.

    Order matters here: the composition assertions come FIRST, because they are
    the ones that would have caught v1.

    v1 passed 53 green assertions on a page that read as a blog post. Every one
    of them was true — every byte accounted for, every link resolving, every
    contrast pair measured, every heading in order — and not one of them could
    see that the result was nine identical sections of prose with three pictures
    in it. Green checks are not a design review.

    This check cannot judge whether the page is any *good*. It can fail a page
    that has quietly collapsed back into v1's shape, which is the failure that
    actually happened, and it is the only assertion in this file that is about
    the design rather than about the bytes.
    """
    print("\n5  composition, then behaviour (landing page only)")
    body = strip_html_comments(page)

    # ---- the composition gate (§3, §2) ------------------------------------
    acts = re.split(r"(?=<section\b)", body, flags=re.I)[1:]
    if len(acts) != 12:
        rep.fail("section count", f"{len(acts)} <section> elements — §2's architecture "
                                  f"has twelve acts, and a page that has collapsed back "
                                  f"to a handful is v1 again. An act added or removed is "
                                  f"§2's table's edit to make, in the same commit, which "
                                  f"is why this is exact rather than a floor")
    else:
        rep.ok("12 sections", "§2's acts are present")

    # ---- §2's table, read against the page ---------------------------------
    # This is the drift that actually happened, and it lasted a week: §2's table
    # listed ten acts under a prose line that said eleven, on a page that shipped
    # twelve, with every assertion in this file green — because the table is a
    # claim about this file and nothing here was reading it. Counting sections
    # cannot catch a table that describes a different page.
    #
    # So the table is read as DATA. Three things are asserted, and each is a way
    # the plan and the page can disagree while both look fine:
    #
    #   * the row count, which is the "eleven acts" bug itself;
    #   * each row's anchor id against the act's own `id`, because the ids are what
    #     the nav, the hero's rail and the ring's plate link to — the table is
    #     where a renamed one would be documented wrongly;
    #   * each row's headline against the act's real <h1>/<h2>, because the table
    #     paraphrased them, and a paraphrase is how a 12-word headline sat under a
    #     rule that allows seven.
    rows = plan_act_rows()
    if rows is None:
        rep.fail("§2's table is readable",
                 f"{PLAN_DOC.name} is missing, or its table no longer starts with "
                 f"{PLAN_TABLE_HEAD!r}. This check reads that table as data, so a "
                 f"reformat has to re-point it rather than pass quietly")
    elif len(rows) != len(acts):
        rep.fail("§2's table matches the page",
                 f"the plan lists {len(rows)} acts against {len(acts)} sections — the "
                 f"table and the page are describing different pages, which is the "
                 f"exact failure this check exists for")
    else:
        wrong_head, wrong_id, missing_ex = [], [], []
        for i, cells in enumerate(rows, start=1):
            chunk = acts[i - 1]
            m = re.search(r"<h[12]\b[^>]*>(.*?)</h[12]>", chunk, re.S | re.I)
            page_head = norm_text(m.group(1)) if m else "(no heading)"
            if page_head != norm_text(cells[2]):
                wrong_head.append(f"act {i}: plan {cells[2]!r} vs page {page_head!r}")
            want = re.search(r"#([A-Za-z][\w-]*)", cells[1])
            has = re.search(r"<section\b[^>]*\bid\s*=\s*[\"']([^\"']*)[\"']",
                            chunk, re.I)
            if want and (not has or has.group(1) != want.group(1)):
                wrong_id.append(f"act {i}: plan #{want.group(1)} vs page "
                                f"{'#' + has.group(1) if has else '(no id)'}")
            if not want and has:
                wrong_id.append(f"act {i}: plan says no id, page has #{has.group(1)}")
            product = cells[5] if len(cells) > 5 else ""
            for ex in sorted(set(re.findall(r"exhibit-\d+", product))):
                if f"/img/{ex}" not in body:
                    missing_ex.append(f"act {i}: {ex} is not on the page")
        if wrong_head:
            rep.fail("§2's headlines are the page's",
                     "; ".join(wrong_head) + " — the table has to quote the built "
                     "markup rather than paraphrase it, because the paraphrase is "
                     "where the length rule went unchecked")
        else:
            rep.ok("§2's headlines are the page's", f"{len(rows)} rows, read from the plan")
        if wrong_id:
            rep.fail("§2's anchor ids are the page's", "; ".join(wrong_id))
        else:
            rep.ok("§2's anchor ids are the page's", "every id in the table is on the act it names")
        if missing_ex:
            rep.fail("§2's exhibits are the page's", "; ".join(missing_ex))
        else:
            rep.ok("§2's exhibits are the page's", "every exhibit the table names is in the markup")

    # ---- the rhythm gate (§2, report #12) ---------------------------------
    # §2 opens by claiming the page alternates its compositions deliberately, and
    # the report ranks alternation #12 — its example is Gemini Notebook, called the
    # least memorable of the five "despite having the best single element".
    #
    # Nothing measured that claim until this block. What it cost is worth stating:
    # the gate counted sections while §2's table listed ten acts under a prose line
    # that said eleven, and the page had twelve. Every assertion was green and the
    # one document that describes the design described a different page. A claim
    # about a reader is not a claim about markup, but these two are read off the
    # built markup and are what makes the claim true:
    #
    #   * **The paired acts alternate side.** That is C2's entire contribution. Two
    #     in a row on the same side is the zig-zag collapsing into a column.
    #   * **No more than five consecutive acts share one ground.** The page measures
    #     D P P P P P D P P P P D — runs of five and four. The report's rule is
    #     "every third changes the ground or accent", and five is where this page
    #     lands, so five is the number asserted: the failure is a SIXTH paper act in
    #     a row, which is the run length the page's own evidence says reads as a
    #     list. Asserting three would fail a page that already works.
    ground, flips = [], []
    for chunk in acts:
        tag = re.search(r"<section\b[^>]*>", chunk, re.I)
        attr = ""
        if tag:
            cls = re.search(r"""\bclass\s*=\s*["']([^"']*)["']""", tag.group(0), re.I)
            attr = cls.group(1) if cls else ""
        ground.append("D" if re.search(r"\b(field|poster)\b", attr) else "P")
        if re.search(r"""\bclass\s*=\s*["'][^"']*\bsplit\b[^"']*["']""", chunk, re.I):
            flips.append(bool(re.search(
                r"""\bclass\s*=\s*["'][^"']*\bsplit\b[^"']*\bis-flip\b""", chunk, re.I)))
    sequence = "".join(ground)

    runs, cur = [], 1
    for i in range(1, len(ground)):
        if ground[i] == ground[i - 1]:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    longest = max(runs)
    if longest > 5:
        rep.fail("ground rhythm", f"{longest} acts in a row on one ground ({sequence}) — "
                                   f"§2's page has never run longer than five, and a "
                                   f"longer run is the page reading as a list")
    else:
        rep.ok("ground rhythm", f"{sequence} — longest run {longest}, alternates "
                                 f"{len(runs) - 1} times")

    same_side = [i for i in range(1, len(flips)) if flips[i] == flips[i - 1]]
    if len(flips) < 4 or same_side:
        rep.fail("C2 alternates side", f"{len(flips)} paired acts, sides "
                                       f"{[int(f) for f in flips]}"
                                       + (f", same side at {same_side}" if same_side else "")
                                       + " — §3's C2 is a zig-zag or it is a column")
    else:
        rep.ok("C2 alternates side", f"{len(flips)} paired acts, sides "
                                     f"{[int(f) for f in flips]}")

    # The five compositions are C1 field-full, C2 split, C3 pair, C4 band,
    # C5 poster. A page using one of them everywhere is a document; the whole
    # point of §3 is that the page alternates.
    # Scanned across every class attribute in the body, not just the ones on
    # <section>. C2's grid has to sit on a wrapper (the section is full-bleed and
    # the grid is inside the page's width), so a `split` that only ever appears on
    # an inner element is still the page using C2. The assertion is "the page uses
    # N of the five", which a document-shaped page fails either way.
    classes = set()
    for attr in re.findall(r"""\bclass\s*=\s*["']([^"']*)["']""", body, re.I):
        for name in ("field", "split", "pair", "band", "poster"):
            if re.search(rf"\b{name}\b", attr):
                classes.add(name)
    if len(classes) < 4:
        rep.fail("composition variety", f"{sorted(classes)} — §3 names five "
                                        f"compositions and the page must use at "
                                        f"least four of them")
    else:
        rep.ok(f"{len(classes)} compositions in use", ", ".join(sorted(classes)))

    pictures = len(re.findall(r"<picture\b", body, re.I))
    if pictures < 9:
        rep.fail("exhibit count", f"{pictures} <picture> elements — §6 ships nine")
    else:
        rep.ok(f"{pictures} exhibits", "§6's exhibit set is present")

    # v1 shipped the FAQ as a plain <dl> and wrote a comment explaining that an
    # accordion "would hide precisely the answers this audience came for". Every
    # reference site has one. This asserts the reversal stuck.
    if "<details" not in body:
        rep.fail("no <details>", "§12: the FAQ is an accordion on <details>, and "
                                 "v1's refusal to build one is what v2 reverses")
    else:
        rep.ok(f"{body.count('<details')} <details>",
               "the FAQ is a real disclosure, not a list")

    # And the hero's two reserved answers are among them, which is a claim about a
    # reader rather than about markup: the refusal demonstrates the promise the
    # rest of the page asks to be taken on trust, and it used to sit behind a
    # click that only script could answer. The audit's scriptless pass found that;
    # this keeps it found. Checked by walking the disclosure blocks rather than by
    # looking for the ids anywhere on the page, because the ids are also what the
    # chips point at once the script has moved the answers into the pane.
    reserved = ("ans-who", "ans-inscriptions")
    opened = set()
    for block in re.findall(r'<details class="hero-more"[^>]*>(.*?)</details>', page, re.S):
        for name in reserved:
            if f'id="{name}"' in block:
                opened.add(name)
    if opened == set(reserved):
        rep.ok("the hero's reserved answers are disclosures",
               "reachable with no script")
    else:
        rep.fail("the hero's reserved answers",
                 f"{sorted(set(reserved) - opened)} are not inside a `details.hero-more`, "
                 "so the refusal a reader is told to trust is unreachable with no script")

    if not re.search(r"position\s*:\s*sticky", page):
        rep.fail("no sticky element", "§9: the nav is sticky — v1's only nav was "
                                      "painted inside a screenshot")
    else:
        rep.ok("the nav is sticky", "§9")

    # §5: the display size is spent ONCE. v1 topped out at 68px and reused it;
    # the top tier of the reference set runs 5.3-6.4x over body, the two sites
    # that feel most web-default run 3.0-3.1x. One use is what buys the ratio.
    display_uses = len(re.findall(r"var\(\s*--t-display\s*\)", page))
    if display_uses != 1:
        rep.fail("display size", f"--t-display is used {display_uses} times — §5 "
                                 f"spends it once, on the h1")
    else:
        rep.ok("the display size is spent once")

    # ---- the behaviour contract ------------------------------------------
    #
    # v2 responds to clicks on purpose — the citation chips are operable and the
    # FAQ is a disclosure — so the v1 prohibition is gone. What replaces it is a
    # narrower rule: the page's ONE script must stay small, inline, and incapable
    # of being the reason anything works.
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", body, re.S | re.I)
    tags = re.findall(r"<script\b[^>]*>", body, re.I)
    if len(tags) != 1:
        rep.fail("script count", f"{len(tags)} <script> tags — the page carries "
                                 f"exactly one")
    elif re.search(r"\bsrc\s*=", tags[0], re.I):
        rep.fail("<script src>", f"{tags[0].strip()} — the one script must be "
                                 f"inline, or §12's payload arithmetic changes")
    else:
        rep.ok("exactly one <script>, inline, no src")

    src = scripts[0] if scripts else ""

    # Event-handler ATTRIBUTES are still forbidden: they are the shape of
    # behaviour bolted onto markup. The script is scanned separately below, so a
    # variable named `onScroll` is not mistaken for an attribute.
    without_script = re.sub(r"<script\b.*?</script>", "", body, flags=re.S | re.I)
    bad = re.findall(r"\bon[a-z]+\s*=", without_script, re.I)
    if bad:
        rep.fail("event handler attribute", ", ".join(sorted(set(bad))))
    else:
        rep.ok("no event-handler attributes")

    if re.search(r"""\b(?:href|src)\s*=\s*["']\s*javascript:""", body, re.I):
        rep.fail("javascript: URL", "the page must not carry one")
    else:
        rep.ok("no javascript: URL")

    # Device sniffing is still forbidden — §16 declares the lighter build in
    # media queries and nowhere else. matchMedia itself is fine; matchMedia
    # asking about anything but the accessibility query is the same sniffing
    # wearing a different API.
    # The ban is on the UA string and the platform, not on measuring the
    # viewport. `getBoundingClientRect().top < innerHeight` asks "is this element
    # below the fold", which is a question about a position, not about a device —
    # and any layout consequence of the answer is still CSS's. Banning innerHeight
    # would have banned the one measurement the reveal needs while permitting the
    # sniffing the rule exists to stop.
    for needle in ("userAgent", "userAgentData", "navigator.platform"):
        if needle in src:
            rep.fail(f"the script uses {needle}",
                     "§16: the lighter build stays declared in media queries, "
                     "never sniffed at run time")
    for query in re.findall(r"""matchMedia\(\s*['"]([^'"]+)['"]""", src):
        if "prefers-reduced-motion" not in query:
            rep.fail("device detection in matchMedia", query)
    if "IntersectionObserver" not in src:
        rep.fail("the script's shape", "it reveals panels and reads scroll "
                                       "position through an IntersectionObserver")
    else:
        rep.ok("the script only observes and toggles")

    # EVERY transition and animation must sit inside the reduced-motion guard.
    # This is the assertion that replaces v1's "one transition, one target": the
    # rule is no longer *how much* motion there is but that all of it is
    # optional. A rule outside the guard runs for a visitor who asked it not to.
    outside: list[str] = []
    inside_count = 0
    for sel, rule_body, inside in css_rules(page):
        moving = [(p, v) for p, v in declarations(rule_body)
                  if p.startswith(("transition", "animation"))]
        if "prefers-reduced-motion" in inside:
            inside_count += len(moving)
        else:
            outside += [f"{sel} {{ {p}: {v} }}" for p, v in moving]
    if outside:
        for o in outside:
            rep.fail("motion outside the reduced-motion guard", o)
    else:
        rep.ok(f"{inside_count} motion declarations",
               "all of them inside @media (prefers-reduced-motion: no-preference)")
    if "prefers-reduced-motion" not in page:
        rep.fail("prefers-reduced-motion", "there is nothing to honour")


def check_6(rep: Report, css: str) -> None:
    print("\n6  contrast")
    # §1's table is the LIGHT theme's, so every pair resolves against `:root`.
    # Reading `.win` or `.world-dark` here is the easy mistake and it is a silent
    # one: `--ink` exists in all three blocks, so merging them turns the first
    # row into white-on-white and reports a confident 1.00:1. A pair that is
    # genuinely dark-scoped is written as a hex literal in the table above, with
    # its reason, rather than looked up.
    tokens = token_block(css, ":root")

    def resolve_token(name: str) -> str | None:
        """A token name or a literal hex -> #RRGGBB, following var() aliases."""
        return name.upper() if name.startswith("#") else hex_of(tokens.get(name, ""), tokens)

    for fg, bg, claimed, why in CONTRAST:
        a, b = resolve_token(fg), resolve_token(bg)
        if a is None or b is None:
            rep.fail(f"{fg} on {bg}", "could not resolve the pair to hex")
            continue
        got = contrast(a, b)
        dp = len(str(claimed).split(".")[1])
        if abs(got - claimed) > (0.005 if dp == 2 else 0.05):
            rep.fail(f"{fg} on {bg}",
                     f"{got:.2f}:1, §1 says {claimed}:1  ({a} on {b})  — {why}")
        else:
            rep.ok(f"{fg} on {bg}", f"{got:.2f}:1  ({a} on {b})")

    for fg, bg, claimed, why in CONTRAST_BELOW_AA:
        a, b = resolve_token(fg), resolve_token(bg)
        if a is None or b is None:
            rep.fail(f"{fg} on {bg}", "could not resolve the pair to hex")
            continue
        got = contrast(a, b)
        if got >= AA_NORMAL:
            rep.fail(f"{fg} on {bg}",
                     f"{got:.2f}:1 — it is above AA, so the token's justification "
                     f"({why}) is no longer true")
        elif abs(got - claimed) > 0.05:
            rep.fail(f"{fg} on {bg}", f"{got:.2f}:1, the comment says {claimed}:1")
        else:
            rep.ok(f"{fg} on {bg} still fails AA", f"{got:.2f}:1  — {why}")

    # The stylesheet's own promise, and it has to be read off the RULES: a scan
    # of raw lines finds every hex named inside a comment, which is most of them.
    strays = []
    for sel, body, inside in css_rules(css):
        for prop, value in declarations(body):
            if prop.startswith("--"):
                continue
            if re.search(r"#[0-9A-Fa-f]{3,8}\b|\brgba?\(", value):
                strays.append(f"{sel} {{ {prop}: {value} }}")
    if strays:
        for s in strays[:10]:
            rep.fail("colour outside a token", s)
    else:
        rep.ok("every colour is a token", "no hex or rgb() in a declaration")


def check_7(rep: Report, page: str, css: str) -> None:
    print("\n7  codepoints")
    declared = declared_codepoints(css)
    rendered = rendered_text(page)
    visible = visible_text(page)
    punctuation = sorted({c for c in visible if c in "—–"})
    if punctuation:
        rep.fail("visible dash punctuation", ", ".join(repr(c) for c in punctuation) +
                 " appears in visitor-facing text; use a comma, colon or full stop")
    else:
        rep.ok("visible copy has no em or en dash")

    # The stricter form, and it is only available now that the page ships without
    # its html comments. Visible text was the RULE; the whole document is the
    # measurement. It is worth having because four dashes used to survive in the
    # inlined stylesheet's header comment and one in the inline script: none of
    # them reaches a visitor, and every one of them makes an auditor scanning the
    # artifact for dashes stop and re-derive why it is allowed. A rule that needs
    # an exception explained is weaker than one that does not.
    somewhere = sorted({c for c in page if c in "—–"})
    if somewhere:
        rep.fail("em or en dash anywhere in the document",
                 ", ".join(repr(c) for c in somewhere) +
                 " — the landing page ships no comment that needs one")
    else:
        rep.ok("no em or en dash anywhere in the document",
               "comments and the inline script included")

    seen = sorted({ord(c) for c in rendered if ord(c) > 127})
    out_of_range = [c for c in seen if c not in declared and c not in FALLS_THROUGH]

    for c in out_of_range:
        rep.fail(f"U+{c:04X}",
                 "outside every declared unicode-range and not allow-listed — it "
                 "renders in a system face, not in a shipped subset")
    if not out_of_range:
        rep.ok(f"{len(seen)} rendered non-ASCII codepoints",
               "all inside a declared unicode-range")

    # The allow-list is asserted EXACTLY. A new entry is a decision, not a
    # convenience: it means a glyph the copy needs cannot be drawn by any subset.
    used = sorted(c for c in seen if c in FALLS_THROUGH)
    if used != sorted(FALLS_THROUGH):
        rep.fail("the fall-through allow-list",
                 f"{[f'U+{c:04X}' for c in used]} rendered, "
                 f"{[f'U+{c:04X}' for c in sorted(FALLS_THROUGH)]} allow-listed")
    else:
        for c in used:
            rep.ok(f"U+{c:04X} falls through by design", FALLS_THROUGH[c])


def check_8(rep: Report, page: str) -> None:
    print("\n8  the home page is the new one")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S | re.I)
    # The marker is matched against the h1's TEXT: the h1 now carries an inline
    # span around "what it saw" (the hero's one accent), and a tag is not a
    # word. Same normalisation the copy gate's extractor uses.
    h1_text = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else ""
    if not h1 or HOME_MARKER not in h1_text:
        found = h1_text[:60] if h1 else "no <h1>"
        rep.fail("_site/index.html",
                 f"does not carry §1.3's marker. Found: {found!r}. The assembler "
                 f"copied the previous home page.")
    else:
        rep.ok("_site/index.html carries the new <h1>", h1_text)


def check_9(rep: Report, site: pathlib.Path,
            docs: dict[pathlib.Path, str]) -> None:
    print("\n9  library integrity")
    pages = sorted(d for d in site.iterdir()
                   if d.is_dir() and (d / "index.html").is_file()
                   and d.name not in LIBRARY_TOC)
    if len(pages) != LIBRARY_PAGES:
        rep.fail("library page count",
                 f"{len(pages)}, expected {LIBRARY_PAGES}")
    else:
        rep.ok(f"{LIBRARY_PAGES} library pages present")

    styles = site / "styles.css"
    if not styles.is_file():
        rep.fail("/styles.css", "missing — 75 pages would render unstyled")
    elif styles.stat().st_size != LIBRARY_STYLES_BYTES:
        rep.fail("/styles.css",
                 f"{styles.stat().st_size:,} B, the library's file is "
                 f"{LIBRARY_STYLES_BYTES:,} B")
    else:
        rep.ok("/styles.css is the library's", f"{LIBRARY_STYLES_BYTES:,} B")

    # The directory tells its reader, in visible copy, that `/` focuses the field
    # and that the arrow keys walk the matches. That is a promise about behaviour,
    # which is the one kind this file's copy sibling cannot see: it reads text. So
    # the text is checked here against the script that has to keep it, by name.
    index = site / "library" / "index.html"
    script = docs.get(index, "")
    if "to search, then the arrow keys" in script:
        missing = [k for k in ("'/'", "ArrowDown", "ArrowUp") if k not in script]
        if missing:
            rep.fail("the directory's keyboard",
                     "the hint promises " + ", ".join(missing) + " and the script "
                     "does not handle it — a promise in visible copy, unkept")
        else:
            rep.ok("the directory's keyboard matches its own hint",
                   "slash, ArrowDown, ArrowUp")
    else:
        rep.fail("the directory's keyboard",
                 "/library/ no longer carries the hint that teaches the shortcut")

    lost = []
    for d in pages:
        text = docs.get(d / "index.html", "")
        m = re.search(r"""<link[^>]+rel=["']canonical["'][^>]*>""", text, re.I)
        if not m:
            lost.append(f"/{d.name}/ has no rel=canonical")
            continue
        href = re.search(r"""href=["']([^"']+)["']""", m.group(0), re.I)
        want = f"https://istor.fyi/{d.name}/"
        if not href or href.group(1).rstrip("/") + "/" != want:
            lost.append(f"/{d.name}/ canonicals to "
                        f"{href.group(1) if href else 'nothing'}, not {want}")
    if lost:
        for item in lost[:10]:
            rep.fail("self-canonical", item)
        if len(lost) > 10:
            rep.fail("self-canonical", f"and {len(lost) - 10} more")
    else:
        rep.ok(f"{len(pages)} self-canonicals intact")

    # The continue-reading pair, asserted as a WALK rather than sampled.
    #
    # Every carried article ends with a next and a previous link, written into it
    # by add-article-nav.py from the index generator's own grouping. Checking one
    # page's pair would pass while the chain had a hole in it, and a chain with a
    # hole is worse than no chain: a reader follows it and stops in the middle of
    # a library that claims seventy-five pages. So the walk is followed from the
    # one page that has no previous, and it has to reach every carried page
    # exactly once; then the same walk is followed backwards from the end. Two
    # directions because a broken prev is invisible to a next-only walk.
    step: dict[str, tuple[str | None, str | None]] = {}
    for d in pages:
        text = docs.get(d / "index.html", "")

        def href(rel: str, text: str = text) -> str | None:
            m = re.search(r'<a[^>]+href="/([^"/]+)/"[^>]*rel="%s"' % rel, text)
            return m.group(1) if m else None

        step[d.name] = (href("next"), href("prev"))

    starts = sorted(s for s, (_n, prev) in step.items() if prev is None)
    forward, cur = [], (starts[0] if len(starts) == 1 else None)
    while cur and cur not in forward:
        forward.append(cur)
        cur = step.get(cur, (None, None))[0]
    backward, cur = [], (forward[-1] if forward else None)
    while cur and cur not in backward:
        backward.append(cur)
        cur = step.get(cur, (None, None))[1]

    if (len(starts) != 1 or sorted(forward) != sorted(step)
            or sorted(backward) != sorted(step) or forward != backward[::-1]):
        rep.fail("the continue-reading walk",
                 f"{len(starts)} page(s) start the walk (one should), forwards "
                 f"reached {len(forward)} of {len(step)}, backwards reached "
                 f"{len(backward)}. Run Source/tools/add-article-nav.py.")
    else:
        crossing = sum(1 for i in range(1, len(forward))
                       if make_library_index.group_of(forward[i]) !=
                       make_library_index.group_of(forward[i - 1]))
        rep.ok(f"one walk through {len(forward)} articles",
               f"every page reached exactly once, both ways, {crossing} group "
               f"crossings")

    dash_pages = []
    for path, text in docs.items():
        if path.suffix.lower() not in (".html", ".htm"):
            continue
        punctuation = sorted({c for c in visible_text(text) if c in "—–"})
        if punctuation:
            dash_pages.append(f"/{path.relative_to(site).as_posix()}: " +
                              ", ".join(repr(c) for c in punctuation))
    if dash_pages:
        for item in dash_pages[:10]:
            rep.fail("visible dash punctuation", item)
        if len(dash_pages) > 10:
            rep.fail("visible dash punctuation", f"and {len(dash_pages) - 10} more pages")
    else:
        rep.ok("all published HTML copy has no em or en dash")

    for brand in ("brand/istor-page.svg", "brand/og-card.png"):
        if (site / brand).is_file():
            rep.ok(f"/{brand} present")
        else:
            rep.fail(f"/{brand}", "missing — §1.1 carries it for the library")

    # The two-sided page check: sitemap and llms.txt must name exactly the pages
    # that exist, and every page must carry a lastmod (§3, Stage 8).
    #
    # "Page" means a URL under istor.fyi that is the root or ends in a slash.
    # Both files also name non-pages — /styles.css and /favicon.ico in the
    # sitemap's neighbourhood, the GitHub release URL in llms.txt — and those
    # are not this check's business, so they are filtered by shape rather than
    # by an allowlist that would need editing every time a file is added.
    # Every page, the index included: this set is compared against the sitemap
    # and llms.txt, and both name /library/ now. `pages` above is the 75 carried
    # articles, which is a different question — whether the library is intact.
    all_pages = sorted(d for d in site.iterdir()
                       if d.is_dir() and (d / "index.html").is_file()
                       and d.name not in NOT_A_PAGE)
    have = {"/"} | {f"/{d.name}/" for d in all_pages}
    for name in ("sitemap.xml", "llms.txt"):
        path = site / name
        if not path.is_file():
            rep.fail(name, "missing from the artifact")
            continue
        text = path.read_text(encoding="utf-8")
        listed = set()
        for u in re.findall(r"https://istor\.fyi(/[^\s<>\"')\]]*)", text):
            u = u.split("#")[0]
            if u == "" or u.endswith("/"):
                listed.add(u or "/")
        missing = sorted(have - listed)
        extra = sorted(listed - have)
        if missing or extra:
            rep.fail(name, f"{len(listed)} pages listed of {len(have)} — "
                           f"missing {missing[:4]}, unknown {extra[:4]}")
        else:
            rep.ok(f"{name} names all {len(have)} pages",
                   f"{len(listed)} urls, both directions")

    sm = (site / "sitemap.xml").read_text(encoding="utf-8")
    entries = re.findall(r"<url>(.*?)</url>", sm, re.S)
    dateless = [re.search(r"<loc>([^<]+)</loc>", e).group(1)
                for e in entries if "<lastmod>" not in e]
    if dateless:
        rep.fail("lastmod", f"{len(dateless)} pages ship dateless: {dateless[:4]}")
    else:
        rep.ok(f"every page has a lastmod", f"{len(entries)} entries")


def check_newlines(rep: Report, site: pathlib.Path) -> None:
    print("\n   artifact integrity")
    # TEXT files only. A PNG, WebP or AVIF carries the bytes 0D 0A wherever the
    # compressor happened to emit them — scanning the images reports sixteen
    # CRLF "failures" that are JPEG coefficients, and the check stops being read.
    text_suffixes = {".html", ".htm", ".css", ".txt", ".xml", ".svg", ".js",
                     ".json", ".webmanifest"}
    crlf = [p.relative_to(site).as_posix()
            for p in site.rglob("*") if p.is_file()
            and p.suffix.lower() in text_suffixes
            and b"\r\n" in p.read_bytes()]
    if crlf:
        for name in crlf[:10]:
            rep.fail("CRLF", f"{name} — the repository is LF-only")
    else:
        rep.ok("the artifact is LF-only", "no CRLF in any text file")

    # The documents too, and the reason is not theoretical: a mutation script in
    # .improvement restored this plan with `write_text`, whose default newline
    # translation turned all 1381 lines CRLF, and nothing was watching the files
    # that are not the artifact. These three are read by hand and diffed on every
    # commit, so one of them arriving in CRLF is a diff of every line.
    doc_crlf = [p.relative_to(REPO).as_posix() for p in DOCUMENTS
                if p.exists() and b"\r\n" in p.read_bytes()]
    if doc_crlf:
        for name in doc_crlf:
            rep.fail("CRLF in a document", f"{name} — the repository is LF-only, and "
                                            f"a rewritten document is how this got "
                                            f"past a gate the first time")
    else:
        rep.ok("the documents are LF-only",
               f"{len([p for p in DOCUMENTS if p.exists()])} files")

    files = [p for p in site.rglob("*") if p.is_file()]
    if len(files) != ARTIFACT_FILES:
        rep.fail("artifact file count",
                 f"{len(files)} files, expected {ARTIFACT_FILES}")
    else:
        rep.ok("artifact file count", f"{ARTIFACT_FILES} files")


# ------------------------------------------------------------------------ main

def media_block(css: str, query: str) -> str:
    """The text inside `@media <query> { ... }`, by brace depth."""
    m = re.search(r"@media\s*" + query + r"\s*\{", css)
    if not m:
        return ""
    i, depth = m.end(), 1
    while i < len(css) and depth:
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
        i += 1
    return css[m.end():i - 1]


def check_10(rep: Report, page_css: str, library_css: str,
             notfound_css: str = "") -> None:
    """The two promises a stylesheet makes to a reader nobody sees.

    A reader prints the page, and a reader asks their system for more contrast.
    Both fail silently: without a print block, a reader whose system is dark prints
    the dark world's near-white ink onto white paper (measured before this block
    existed: 13 of 46 text elements on one article, 17 of 185 on the home page),
    and without a contrast block the reader who asked gets exactly what everyone
    else gets. So both are computed here rather than trusted, and the numbers are
    read out of the stylesheets rather than out of a comment about them.
    """
    print("\n10  the reader's own settings")

    for label, css in (("landing page", page_css), ("library", library_css),
                       ("not-found page", notfound_css)):
        got = media_block(css, r"print")
        if not got:
            rep.fail(f"{label} print block",
                     "no @media print — this half of the site prints its dark "
                     "inks onto white paper")
        else:
            rep.ok(f"{label} carries a print block")

        more = media_block(css, r"\(prefers-contrast:\s*more\)")
        if not more:
            rep.fail(f"{label} prefers-contrast: more",
                     "no block, so a reader who asks for more contrast is given "
                     "the same page as everyone else")
        else:
            rep.ok(f"{label} honours prefers-contrast: more")

    # The ink the print block promises, against the paper it will land on. Text
    # tokens at 4.5:1 or better, and the two that draw rules and rails at 3:1,
    # which is the same bar the screen version documents for a graphic.
    # Only the ROOT declarations of each print block, which is where the token
    # world is written. A print block can also redefine tokens for one component
    # (the landing page gives its replica the light window's own block), and those
    # are a component's internals rather than the paper's ink: `.win`'s `--rule`
    # is #E4E6E9 in both themes, so counting it here reported a 1.25:1 rule.
    printed = ""
    for css in (page_css, library_css, notfound_css):
        block = media_block(css, r"print")
        m = re.search(r":root[^{]*\{([^}]*)\}", block)
        printed += (m.group(1) if m else "")
    inks = re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;", printed)
    text_tokens = {t for t, _v in inks if t in
                   ("--ink", "--ink-2", "--mist", "--cite-ink", "--azure",
                    "--field-ink", "--field-ink-2")}
    rule_tokens = {t for t, _v in inks if t in ("--hairline", "--rule", "--field-rule")}
    worst_text, worst_rule = 21.0, 21.0
    for token, value in inks:
        if token in text_tokens:
            worst_text = min(worst_text, contrast(value, "#FFFFFF"))
        elif token in rule_tokens:
            worst_rule = min(worst_rule, contrast(value, "#FFFFFF"))
    if not text_tokens:
        rep.fail("the print block's ink", "no text token declared in print")
    elif worst_text < 4.5:
        rep.fail("the print block's ink",
                 f"a text token is {worst_text:.2f}:1 on white paper, under 4.5")
    else:
        rep.ok("every print ink clears AA on white paper",
               f"worst {worst_text:.2f}:1")
    if rule_tokens:
        if worst_rule < 3:
            rep.fail("the print block's rules",
                     f"a rule token is {worst_rule:.2f}:1 on white paper, under 3")
        else:
            rep.ok("every printed rule is visible", f"worst {worst_rule:.2f}:1")


# The three selectors that mean "the dark world" in these two files. Named
# exactly, because a looser match reads the wrong blocks: the library's print
# block declares a light world under a selector LIST that contains
# `:root[data-theme="dark"]`, and counting that reported black ink as a dark
# token the first time this was written.
DARK_SELECTORS = (
    ':root[data-theme="dark"]',
    ':root:not([data-theme])',
    ':root:not([data-theme="light"])',
)


def dark_world(css: str) -> dict[str, set[str]]:
    """Every value a stylesheet gives each token in a dark world block.

    A SET of values, not one value, and that is the whole point: both files say
    the same thing twice, once under the media query that covers a reader with no
    script and once under the attribute the head stamp writes, and a check that
    read one block only would report a clean bill of health for a world where the
    other had drifted. The first version of this did exactly that, and the
    negative test that caught it is why the docstring names it.
    """
    out: dict[str, set[str]] = {}
    for selector, body in re.findall(r"([^{}@]*?)\{([^{}]*)\}", css):
        if " ".join(selector.split()) not in DARK_SELECTORS:
            continue
        for token, value in re.findall(
                r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;", body):
            out.setdefault(token, set()).add(value.lower())
    return out


def check_11(rep: Report, site: pathlib.Path, library_css: str) -> None:
    """The not-found page, whose reader is the one visitor who is already lost.

    The page used to answer a missing address with one link home, while 75 of the
    site's 76 pages are in the library. Three promises are asserted here and none
    of them can be read off a screenshot:

    * **It ships no comment.** It is the artifact's only hand-authored page that
      the assembler does not touch, so it was the only page still posting the
      reasoning behind its own markup: 4.6 KB of it. build-site.py strips it on
      the way in, and this reads the artifact rather than the tool, because a
      strip that ran on the wrong file would look exactly like one that worked.
    * **Its search needs no script.** The form's own action and method have to
      reach /library/?q=, which is a path the directory has read since it grew
      the find control. A page that only searched itself when its script ran
      would be a 404 that helps nobody, on the browsers where help is least.
    * **A lost reader still has somewhere to go with no script at all**, after
      the form, so no suggestion has to have appeared for the page to work.

    And one promise between two files: the dark world here is the library's dark
    world. They are separate stylesheets on purpose (this page is one screen and
    inlining the library's 48 KB for it would be the wrong kind of
    consistency), which is exactly how two token blocks drift apart.
    """
    print("\n11  the page for a missing address")
    path = site / "404.html"
    if not path.is_file():
        rep.fail("/404.html", "missing from the artifact")
        return
    page = path.read_text(encoding="utf-8")

    if "/*" in page or "<!--" in page:
        rep.fail("/404.html carries a comment",
                 "the only hand-authored page the assembler does not touch, so "
                 "its reasoning ships unless build-site.py strips it")
    else:
        rep.ok("/404.html ships with no comment in it")

    open_tag = re.search(r"<form[^>]*>", page)
    form = page[open_tag.start():(page.find("</form>", open_tag.start())
                                  if open_tag else 0)] if open_tag else ""
    missing = []
    if not re.search(r'action\s*=\s*"/library/"', form, re.I):
        missing.append('action="/library/"')
    if not re.search(r'method\s*=\s*"get"', form, re.I):
        missing.append('method="get"')
    if not re.search(r'name\s*=\s*"q"', form, re.I):
        missing.append('an input named "q"')
    if missing:
        rep.fail("the not-found page's search",
                 "no " + ", no ".join(missing) + ". Without all three a reader "
                 "whose script did not run types a query and lands nowhere")
    else:
        rep.ok("its search reaches the directory with no script")

    after = page[page.find("</form>"):] if "</form>" in page else page
    if re.search(r'href="/library/"', after):
        rep.ok("a link into the library follows the search", "no script needed")
    else:
        rep.fail("the way on from a missing address",
                 "nothing after the form links to /library/, so the only path out "
                 "of the page assumes its script ran")

    style = re.search(r"<style\b[^>]*>(.*?)</style>", page, re.S | re.I)
    mine = dark_world(style.group(1) if style else "")
    roles = {"--paper": "--canvas", "--field": "--subtle", "--ink": "--ink",
             "--ink-2": "--mist", "--rule": "--hairline", "--azure": "--cite-ink"}
    theirs = dark_world(library_css)
    drifted = []
    for token, their_token in roles.items():
        declared, installed = mine.get(token, set()), theirs.get(their_token, set())
        if declared and installed and declared - installed:
            drifted.append(f"{token} {sorted(declared)} against the library's "
                           f"{their_token} {sorted(installed)}")
    if not mine:
        rep.fail("the not-found page's dark world",
                 "no dark tokens at all, so a dark reader gets a white page")
    elif drifted:
        rep.fail("the not-found page's dark world",
                 "drifted from the library's: " + "; ".join(drifted))
    else:
        rep.ok("its dark world is the library's",
               f"{len(roles)} roles, same values")


def check_12(rep: Report, site: pathlib.Path, library_css: str) -> None:
    """The directory's two ways between its seventy-five entries.

    Forty of them are one group, so the page offers a jump row and a heading that
    pins while its own group is on screen. Three of those four claims are in two
    different files and one of them cannot be seen at all:

    * The jump row names every group its own headings name, and nothing else. The
      two lists are built from one another by the generator, which is exactly the
      kind of coupling that survives a refactor in one of them and not the other.
    * The row is authored VISIBLE. It is static markup with static links, so a
      reader whose script never ran still gets a way between groups, and the way
      this fails is somebody adding `hidden` beside the find field's own.
    * The pinned heading declares a ground. A sticky heading with a transparent
      background is unreadable the moment an entry scrolls under it, and nothing
      about the source says so: the declaration is the whole promise.
    * The row does not print. It is navigation for a screen, and the library's
      print block is where a page's furniture is already listed.
    """
    print("\n12  the directory's ways between its groups")
    page = site / "library" / "index.html"
    if not page.is_file():
        rep.fail("/library/index.html", "missing from the artifact")
        return
    html = page.read_text(encoding="utf-8")

    ids = set(re.findall(r'<section class="index-group" id="([^"]+)"', html))
    nav = re.search(r'(<nav class="index-jump"[^>]*>)(.*?)</nav>', html, re.S)
    hrefs = set(re.findall(r'href="#([^"]+)"', nav.group(2))) if nav else set()
    if not nav:
        rep.fail("the directory's jump row",
                 "no nav.index-jump in the page — forty entries in one group and "
                 "no way past them but the scroll wheel")
    elif "hidden" in nav.group(1):
        rep.fail("the directory's jump row",
                 "authored hidden, so a reader without script cannot use it: it is "
                 "links, and the script only ever hides it")
    elif hrefs == ids and hrefs:
        rep.ok(f"its jump row names all {len(ids)} groups", "and no others")
    else:
        rep.fail("the directory's jump row",
                 f"jumps to {sorted(hrefs - ids)} which are not groups, and misses "
                 f"{sorted(ids - hrefs)}")

    sticky = re.search(r"\.page-index \.index-group h2 \{(.*?)\}", library_css, re.S)
    body = sticky.group(1) if sticky else ""
    if not re.search(r"position:\s*sticky", body):
        rep.fail("the directory's pinned heading",
                 "no sticky group heading: while a reader scrolls forty entries "
                 "nothing on screen says which group they are in")
    elif not re.search(r"background:\s*var\(--canvas\)", body):
        rep.fail("the directory's pinned heading",
                 "sticky with no ground of its own, so the entries scroll through "
                 "the heading instead of under it")
    else:
        rep.ok("its group heading pins over its own group", "on an opaque ground")

    printed = media_block(library_css, r"print")
    if re.search(r"\.index-jump\s*[,{]|,\s*\n\s*\.index-jump", printed):
        rep.ok("the jump row does not print")
    else:
        rep.fail("the directory's print block",
                 ".index-jump is not listed as furniture, so a sheet of paper "
                 "carries a row of fragment links")


def main(argv: list[str]) -> int:
    # The Windows console is cp1252 by default, and this file's output is full of
    # section signs and em dashes. Reconfigure rather than strip them: the
    # verdict lines are the only thing a reader sees, and mojibake there wastes
    # more time than the encoding fix costs.
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

    page = (site / "index.html").read_text(encoding="utf-8")
    docs: dict[pathlib.Path, str] = {}
    for p in sorted(site.rglob("*")):
        if p.is_file() and p.suffix.lower() in (".html", ".htm", ".css"):
            docs[p] = p.read_text(encoding="utf-8", errors="replace")

    # The stylesheet lives inlined in the page; checks 6 and 7 read it from
    # there so they measure what ships, not what Source/ holds. A build that
    # failed to inline would already have failed verify-budget.py's check 3.
    style = re.search(r"<style\b[^>]*>(.*?)</style>", page, re.S | re.I)
    css = style.group(1) if style else page

    rep = Report()
    check_4(rep, site, docs)
    check_5(rep, page)
    check_6(rep, css)
    check_7(rep, page, css)
    check_8(rep, page)
    check_9(rep, site, docs)
    library_css = (site / "styles.css").read_text(encoding="utf-8")
    notfound = re.search(r"<style\b[^>]*>(.*?)</style>",
                         (site / "404.html").read_text(encoding="utf-8"), re.S | re.I)
    check_10(rep, css, library_css, notfound.group(1) if notfound else "")
    check_11(rep, site, library_css)
    check_12(rep, site, library_css)
    check_newlines(rep, site)

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"links ok - {rep.checks} assertions, Stage 9 checks 4-12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
