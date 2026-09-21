#!/usr/bin/env python3
"""Assemble istor.fyi's published artifact: Source/ + Assets/ + OldVersion/ -> _site/.

This is the same script locally and in CI, so what is reviewed is byte-identical
to what deploys (SITE_BUILD_PLAN.md §1.3). The full spec is §1.1 — this file
implements it and nothing else.

    python Source/tools/build-site.py

Preview the result with `python -m http.server` **inside _site/**. A file://
open would not resolve the root-absolute paths (/fonts/…, /brand/…), which is
exactly how they resolve in production.

The one way to break the deploy
------------------------------
`OldVersion/index.html` is the PREVIOUS home page, and it wants the same
published path as the new one. So the library is copied **by directory, from an
allowlist of directories that contain an index.html — never by globbing
`OldVersion/*`**. A wildcard would publish a complete, valid, working site
serving the wrong home page, and every other check in the build would pass.
`verify-links.py` re-asserts the marker string in `_site/index.html` precisely
because this failure is silent.

Deliberate duplication
----------------------
Four files ship at two paths each (§1.1) and none of them may be "optimised"
away: inter-var.woff2 and gfs-didot.woff2 at both /fonts/ and /assets/fonts/,
og-card.png at both /og-card.png and /brand/og-card.png, and
istor-wordmark.woff2 at both /fonts/ and /brand/. The library addresses its own
copies relatively and is not allowed to change; the new page addresses its at
the root. No visitor ever fetches both.

Standard library only.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]              # IstorPage/
SOURCE = ROOT / "Source"
ASSETS = ROOT / "Assets"
LEGACY = ROOT / "OldVersion"
SITE = ROOT / "_site"

# make-sitemap.py has a hyphen in its name, so it needs the loader rather than
# an import statement. §1.2 asks for it to be a module with a build() function
# so the byte-identity test is one call, and this is that call.
_spec = importlib.util.spec_from_file_location("make_sitemap", HERE / "make-sitemap.py")
make_sitemap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_sitemap)

# make-library-index.py, same reason and same shape: hyphenated name, and a
# build() so the page is one call rather than an import. It is generated here
# rather than committed because it is derived from the 75 pages, and a committed
# copy would be one more thing to keep in step with them.
_spec = importlib.util.spec_from_file_location("make_library_index",
                                              HERE / "make-library-index.py")
make_library_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_library_index)


# --------------------------------------------------------------------------
# The artifact's contents, as tables. §1.1 is the same list in prose.
# --------------------------------------------------------------------------

# Authored pages and root files. styles.css is absent on purpose: the assembler
# inlines it into index.html, and the /styles.css path belongs to the library.
# The last three are generator output, committed (Stage 0's rule) — CI checks
# them with make-favicons.py --check rather than regenerating them.

# Of those, the ones that ship with their comments stripped. They need their own
# pass because they are copied rather than assembled: every other page's
# reasoning is removed by the inliner, and these have no inliner to run.
LEANED = {"404.html"}

AUTHORED = [
    "404.html",
    "robots.txt",
    "llms.txt",
    "CNAME",
    "favicon.ico",
    "icon.svg",
    "apple-touch-icon.png",
]

# published path -> path under Assets/
ASSETS_PUBLISHED = {
    "/fonts/inter-var.woff2":      "fonts/inter-var.woff2",
    "/fonts/gfs-didot.woff2":      "fonts/gfs-didot.woff2",
    "/fonts/istor-wordmark.woff2": "brand/istor-wordmark.woff2",
    "/img/ground-grain.png":       "textures/ground-grain.png",
    "/og-card.png":                "brand/og-card.png",
}

# The eight captures the v2 page ships, in the order it uses them. Every one is a
# measured crop of a real capture, written by make-exhibits.py — see that file
# for the crop bounds and for why each is crop_px / 2 CSS px. The page carries
# nine exhibits, not eight: act 4's is the DOM reading log, which is not an export
# and therefore not in this list.
# exhibit-13-dispute RETIRED 2026-09-21: act 5's table is a DOM replica now, the
# second exhibit to make that move (see the markup note in act 5). A table locked
# in pixels is invisible to a screen reader and unsearchable; its copy was
# transcribed from the capture before the crop was dropped, so nothing was lost
# but the bytes. Restore the line and regenerate if a bitmap is ever wanted.
EXPORTS = [
    "exhibit-10-gate",
    "exhibit-10-gate-phone",
    "exhibit-11-citations",
    "exhibit-11-citations-phone",
    "exhibit-14-research",
    "exhibit-15-models",
    "exhibit-16-library",
    "exhibit-17-notes",
    "exhibit-18-numbers",
    "exhibit-18-numbers-phone",
]
# Note the leading dots: "@2x" attaches to the stem, so the retinas are
# exhibit-10-gate@2x.avif, not exhibit-10-gate.@2x.avif.
#
# No PNG. v1 shipped a PNG fallback and its six PNGs came to 523,598 B —
# between 3.3x and 8.0x the WebP beside each, and 75% of the 702,015 B the whole
# v1 export set weighed — for a format that no browser released since 2020 needs.
# AVIF first, WebP as the <source> fallback and as the <img src>, and the 511 KB
# that frees covers a little over half of what the six extra exhibits the v2 page
# carries cost: 1,156,132 B of exports now against 178,417 B of them before.
# 40 files, not 54.
#
# The four phone crops ride the same suffix loop, so their names are stems here
# rather than a second mechanism: "exhibit-10-gate-phone" + "@2x.avif" is the
# file make-exhibits.py writes. They are separate stems, not extra suffixes,
# because a phone crop is a different CROP, not a different encoding of the same
# one -- which is also why the markup reaches for them with a media query instead
# of srcset. See PHONE in make-exhibits.py for which exhibits get one and why.
EXPORT_SUFFIXES = [".avif", ".webp", "@2x.avif", "@2x.webp"]   # 52 files over 13 stems

# The library's non-page directories. The page directories are found by the
# index.html test below; these three are carried whole, outside that test.
LIBRARY_TREES = ["assets", "brand"]
# styles.css and theme.js are shared by every library page, so they sit at the
# site root rather than being duplicated into each page directory. theme.js is
# the theme control: one file, because 75 copies of the same 1.4 KB would be
# 105 KB of duplicated bytes and a fix would be 75 edits.
LIBRARY_FILES = ["styles.css", "theme.js"]
LIBRARY_ROOT_FILES = ["robots.txt", "08eaa6e8b97d4b94943057b2c49bd712.txt"]

# The three splice sites in Source/index.html. `kind` is only for the error
# message and the sanity check.
INCLUDES = {
    "styles":        (SOURCE / "styles.css",                  "css"),
    "icons":         (SOURCE / "icons.svg.partial",           "svg"),
    "calendar-ring": (SOURCE / "figures" / "calendar-ring.svg", "svg"),
    "poster-horizon": (SOURCE / "figures" / "poster-horizon.svg", "svg"),
    "etymology":      (SOURCE / "figures" / "etymology.svg",      "svg"),
    "etymology-tall": (SOURCE / "figures" / "etymology-tall.svg", "svg"),
    "hero-gears":     (SOURCE / "figures" / "hero-gears.svg",     "svg"),
    "close-gears":    (SOURCE / "figures" / "close-gears.svg",    "svg"),
    "boundary-wide":  (SOURCE / "figures" / "boundary-wide.svg",  "svg"),
    "boundary-mid":   (SOURCE / "figures" / "boundary-mid.svg",   "svg"),
    "boundary-tall":  (SOURCE / "figures" / "boundary-tall.svg",  "svg"),
}

# Library-only includes: offered to carried pages by splice_library_includes(),
# which splices only the markers a page actually carries. They are deliberately
# NOT in INCLUDES, whose splice_includes() requires every entry on the home
# page - a dictionary shared by both passes would make the home page fail for
# a marker it never had.
LIBRARY_INCLUDES = {
    "citation-anatomy-wide": (SOURCE / "figures" / "citation-anatomy-wide.svg", "svg"),
    "citation-anatomy-tall": (SOURCE / "figures" / "citation-anatomy-tall.svg", "svg"),
    "context-window-wide": (SOURCE / "figures" / "context-window-wide.svg", "svg"),
    "context-window-tall": (SOURCE / "figures" / "context-window-tall.svg", "svg"),
    "gguf-anatomy-wide": (SOURCE / "figures" / "gguf-anatomy-wide.svg", "svg"),
    "gguf-anatomy-tall": (SOURCE / "figures" / "gguf-anatomy-tall.svg", "svg"),
    "quant-ladder-wide": (SOURCE / "figures" / "quant-ladder-wide.svg", "svg"),
    "quant-ladder-tall": (SOURCE / "figures" / "quant-ladder-tall.svg", "svg"),
    "ram-budget-wide": (SOURCE / "figures" / "ram-budget-wide.svg", "svg"),
    "ram-budget-tall": (SOURCE / "figures" / "ram-budget-tall.svg", "svg"),
    "q4km-anatomy-wide": (SOURCE / "figures" / "q4km-anatomy-wide.svg", "svg"),
    "q4km-anatomy-tall": (SOURCE / "figures" / "q4km-anatomy-tall.svg", "svg"),
}

# A directory under _site/ that holds an index.html but is not a page.
NOT_A_PAGE = {"fonts", "img", "assets", "brand"}

MARKER = "It shows you what it saw"


class BuildError(Exception):
    """Something is missing, stale, or would publish the wrong site."""


def write_text_lf(path: pathlib.Path, text: str) -> None:
    """Write UTF-8 with LF, on every platform.

    `Path.write_text` translates "\\n" to os.linesep, so on Windows every line
    of the artifact came out CRLF: the spliced index.html and, worse, the
    sitemap — which must be byte-identical to the library's 11,052 B LF file.
    The entire carried library is LF-only, so the new page has to be too.
    """
    path.write_bytes(text.encode("utf-8"))


def copy_file(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.is_file():
        raise BuildError(f"missing build input: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def copy_tree(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.is_dir():
        raise BuildError(f"missing build input: {src}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def published(published_path: str) -> pathlib.Path:
    """'/fonts/inter-var.woff2' -> _site/fonts/inter-var.woff2, with the
    traversal guard that a leading-slash path needs."""
    rel = published_path.lstrip("/")
    if not rel or ".." in pathlib.PurePosixPath(rel).parts:
        raise BuildError(f"bad published path: {published_path!r}")
    return SITE / rel


# --------------------------------------------------------------------------
# 1 · clean
# --------------------------------------------------------------------------

def clean() -> None:
    """Rebuild from nothing. A stale file left in _site/ would be counted, and
    would be listed in sitemap.xml as a page that does not exist."""
    if SITE.name != "_site" or SITE.parent != ROOT:
        raise BuildError(f"refusing to clean {SITE} — not this repository's _site/")
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)


# --------------------------------------------------------------------------
# 2 · the new page and its own assets
# --------------------------------------------------------------------------

def copy_authored() -> None:
    for name in AUTHORED:
        if name in LEANED:
            source = (SOURCE / name).read_text(encoding="utf-8")
            shipped = lean_page(source)
            # The two clauses `inline_css` is held to, for the same reason: the
            # shipped page must carry no comment at all, and it must be the
            # source's markup with comments and whitespace removed and nothing
            # else changed. A byte count cannot tell those apart.
            if _ANY_COMMENT.search(shipped):
                raise BuildError(
                    f"{name}: comment stripping left a comment in the shipped "
                    "page — its style and script blocks must carry none"
                )
            if _lean(source) != _lean(shipped):
                raise BuildError(
                    f"{name}: stripping changed the page, not just its comments "
                    "and whitespace — the shipped page is no longer the source's"
                )
            write_text_lf(SITE / name, shipped)
            continue
        copy_file(SOURCE / name, SITE / name)


def copy_assets() -> None:
    for pub, rel in ASSETS_PUBLISHED.items():
        copy_file(ASSETS / rel, published(pub))
    for stem in EXPORTS:
        for suffix in EXPORT_SUFFIXES:
            name = f"{stem}{suffix}"
            copy_file(ASSETS / "Exports" / name, published(f"/img/{name}"))


# --------------------------------------------------------------------------
# 4 · stripping the stylesheet's comments on the way in
# --------------------------------------------------------------------------

def _lean(text: str) -> str:
    """CSS with its comments and every run of whitespace removed.

    Used to compare a stylesheet before and after inlining: whitespace between
    declarations is insignificant, so removing all of it leaves exactly the
    declarations, and two files that match on this are the same stylesheet.
    """
    return re.sub(r"\s+", "", _ANY_COMMENT.sub("", text))


_LEADING_COMMENT = re.compile(r"\A(\s*/\*.*?\*/)", re.S)
_ANY_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def inline_css(text: str) -> str:
    """The stylesheet as it ships: the leading header comment, and nothing else.

    The comments in `styles.css` are documentation for whoever reads the SOURCE,
    and there are a great many of them — 18,949 of the file's 34,003 bytes, 55%.
    Inlining that file shipped all of it to every visitor in the document that
    arrives first, where it cost **7,192 B gzipped: 35% of index.html**. The
    reasoning is worth keeping and not worth posting.

    So the header stays and the rest goes. The header is the one comment a reader
    of view-source needs, because it explains the thing that is otherwise a
    mystery there: why a page with a token system and a type scale has no
    stylesheet link. Everything else stays in Source/, one file away, where it is
    read by the person editing it.

    Two things this must not do, both checked by verify-links.py against the
    artifact rather than assumed here:

      * It must not remove a comment that is doing a JOB. None are: no comment
        in this stylesheet carries a `/*!`-style preservation marker, and none
        sits inside a value. A comment inside a string or a url() would be a bug
        in the stylesheet, not here, and the collapse below would show it.
      * It must not change what the CSS means. Whitespace between declarations
        is insignificant, and no string in this file spans a line, so collapsing
        blank runs is safe — but "no string spans a line" is an assumption about
        the input, and it is why this is a named function with this comment
        rather than an inline regex.
    """
    head = _LEADING_COMMENT.match(text)
    header = head.group(1) if head else ""
    rest = _ANY_COMMENT.sub("", text[len(header):])
    # Strip each line's trailing space, then collapse the blank runs the removed
    # comments leave behind. Without this the file still weighs 18 KB raw.
    rest = "\n".join(line.rstrip() for line in rest.split("\n"))
    rest = re.sub(r"\n{3,}", "\n\n", rest).lstrip("\n")
    return header.rstrip() + "\n" + rest


# A whole-line `//` comment: blank space to the line's end, then nothing else.
# Anchored, so it can only ever match a line that is entirely comment.
_JS_LINE_COMMENT = re.compile(r"^[ \t]*//[^\n]*(?:\n|$)", re.M)

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# A hand-authored page's own two comment channels, which `inline_markup` cannot
# reach: it runs on the assembled landing page and knows about html comments and
# `//`. The 404 is copied rather than assembled, so it is processed here instead.
_STYLE_BODY = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.S)
_SCRIPT_BODY = re.compile(r"(<script[^>]*>)(.*?)(</script>)", re.S)


def lean_page(text: str) -> str:
    """A copied page as it ships: no comment left inside its style or script.

    `404.html` is the one page that is not assembled, so it was the one page
    still posting its reasoning. Its comments are worth keeping where the next
    editor reads them and not worth sending with a page that exists for a
    mistyped address: written out in full they were 4.6 KB of the file's 10.2 KB.

    Only block comments go, and only inside those two elements. That keeps the
    transform blind to `//`, which a page's script is free to use for a URL, and
    the build's own assertion (the page before and the page after must be equal
    with comments and ALL whitespace removed) is what proves nothing else moved.
    """
    def lean(match: re.Match) -> str:
        body = _ANY_COMMENT.sub("", match.group(2))
        body = "\n".join(line.rstrip() for line in body.split("\n"))
        body = re.sub(r"\n{2,}", "\n", body).lstrip("\n")
        return match.group(1) + body + match.group(3)

    return _SCRIPT_BODY.sub(lean, _STYLE_BODY.sub(lean, text))


def inline_js(text: str) -> str:
    """The document's script as it ships: with no whole-line `//` comment in it.

    The same rule as its two siblings, applied to the third channel. `inline_css`
    strips the stylesheet's comments and `inline_markup` the markup's, both on the
    argument that the reasoning is "worth keeping and not worth posting" — and
    the script kept posting it. Measured 2026-09-21: 93 whole-line `//` comments,
    **7,144 B of the 19,815 B** the document shipped, parsed as script on every
    phone that opened the page. What surfaced it was the ceiling in
    budget.json: the shipped script had grown to 16,117 B against a 16,384 B
    ceiling — 267 B of headroom — while 36% of it was prose, and the next
    feature could not be added without either moving the prose or lying about
    the ceiling. Both channels' docstrings already say where the answer is.

    WHOLE-LINE COMMENTS ONLY, and that is the safety argument rather than an
    unfinished job: a line whose first non-blank characters are `//` cannot
    contain code, so removing it cannot change what the script does. Trailing
    comments are left alone because they would require knowing whether a `//`
    sits inside a string literal or a URL, which is a parser's question. This
    script has no template literal and no string spanning lines — the backtick
    count of its shipped code is asserted below to be zero, which is what proves
    no line INSIDE a string could have been mistaken for a comment, and what
    fails this build loudly if a future edit introduces one.

    Nothing is lost. Every comment stays in `Source/index.html` one file away,
    where the person editing it reads it, and the arguments the script used to
    carry are in the page's markup notes — the channel that was already carrying
    the long form of every one of them.
    """
    def lean(match: re.Match) -> str:
        body = match.group(2)
        stripped = _JS_LINE_COMMENT.sub("", body)
        # Two independent implementations of the same deletion, and they must
        # agree: the regex above, and a line filter below that knows nothing
        # about anchoring. Where the budget keeps two byte witnesses over one
        # artifact for exactly this reason, one transform of the shipper's input
        # gets the same treatment — a size check cannot see a line of code
        # swallowed, and a difference here means one of the two is wrong.
        by_lines = "".join(
            line + "\n" for line in body.split("\n")
            if not line.lstrip().startswith("//"))
        if _lean(stripped) != _lean(by_lines):
            raise BuildError(
                "inline_js's two removals disagree — the anchor and the line "
                "filter do not mean the same thing, and one of them is eating "
                "the other's code"
            )
        # No backtick may remain in the shipped CODE: a template literal can span
        # lines, and a `//` inside one is not a comment, so this strip is only
        # safe while every backtick lives on a comment line. If a future edit
        # needs one, extend this function rather than deleting the check.
        if "`" in stripped:
            raise BuildError(
                "inline_js found a backtick outside a whole-line comment: it "
                "cannot tell a `//` inside a string from a comment, so the "
                "strip has to stop and be taught about strings instead"
            )
        return match.group(1) + stripped + match.group(3)

    return _SCRIPT_BODY.sub(lean, text)


def inline_markup(text: str) -> str:
    """The page as it ships: with NO html comment left in it.

    This is the stylesheet's own rule, applied to the file it was never applied
    to. `inline_css` below strips the CSS comments because they were 55% of that
    file and cost 7,192 B gzipped, and its docstring says the reasoning "is worth
    keeping and not worth posting." The markup kept posting it: 21 comments,
    7,768 B, 18.3% of the document, **2,348 B gzipped**, which is 12% of what a
    visitor downloads before anything renders. Same reasoning, same answer.

    Nothing is lost. Every one of those comments stays in `Source/index.html`,
    one file away, where the person editing it reads it. And the page does not
    lose its explanation, because the inlined stylesheet's header comment ships
    and is exactly that: it says why a page with a token system and a type scale
    has no stylesheet link, which is the one thing view-source actually raises.

    Three things this must not do, and the last two are asserted rather than
    trusted:

      * It must not eat an include marker. It runs after the marker guard, and
        it asserts there is no comment of any kind left, so a marker that
        somehow survived splicing fails the build loudly instead of vanishing.
      * It must not change the page. Comments are not rendered, and the
        whitespace collapsing below is whitespace HTML collapses anyway, so the
        check is the same shape as `inline_css`'s: with comments and ALL
        whitespace removed from both versions, the two must be identical. That
        proves nothing but comments and whitespace was touched, which a byte
        count cannot.
      * It must not touch `<!--` inside the inline script. There is none: the
        script uses `//` comments. A regex cannot know that, so the contract
        check above is what catches it if one is ever added.
    """
    before = _markup_text(text)
    text = _HTML_COMMENT.sub("", text)
    # Remove the whitespace-only lines the comments leave behind, then collapse
    # the blank runs. Without this the page still weighs 40 KB raw.
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    if "<!--" in text:
        raise BuildError(
            "markup comment stripping left a `<!--` in the page — an include "
            "marker survived splicing, or a comment spans one"
        )
    if _markup_text(text) != before:
        raise BuildError(
            "markup comment stripping changed the page, not just its comments "
            "and whitespace — the shipped document is no longer the source's"
        )
    return text


def _markup_text(text: str) -> str:
    """A page reduced to what the two versions of it must agree on.

    Comments out, then every whitespace character out, including the ones
    inside attributes: the comparison is deliberately blind to formatting, so
    the only difference it can see is a difference in content.
    """
    return re.sub(r"\s+", "", _HTML_COMMENT.sub("", text))


def splice_includes() -> None:
    """Step 4. Read Source/index.html, splice, write _site/index.html.

    Note this is the only place the new home page is written. It reads the
    authored source and writes the artifact in one move, so there is no window
    where a copy of the page exists with unspliced markers in it.
    Everything spliced here has a generator, so a regenerated stylesheet or
    figure cannot be forgotten in a hand-paste.
    """
    src = SOURCE / "index.html"
    page = SITE / "index.html"
    text = src.read_text(encoding="utf-8")
    for name, (path, kind) in INCLUDES.items():
        marker = f"<!--#include {name}-->"
        if marker not in text:
            raise BuildError(
                f"{src.name} has no {marker} marker — the include and the page "
                "have drifted apart"
            )
        if not path.is_file():
            raise BuildError(
                f"missing include source for {marker}: {path}\n"
                "       Run the generator that writes it and commit the output."
            )
        chunk = path.read_text(encoding="utf-8")

        # An include source may not itself contain a marker literal. It gets
        # spliced in, so the literal lands in the page and the guard below
        # fires on the build's own output — which reads as a mystery. This
        # actually happened: styles.css's header comment spelled the marker out
        # while describing it.
        if "<!--#include" in chunk:
            raise BuildError(
                f"{path} contains an `<!--#include` marker literal.\n"
                "       Include sources are spliced verbatim, so a marker in one\n"
                "       reappears in the page. Describe the marker in prose, or\n"
                "       split it across the comment delimiters."
            )

        # Cheap structural checks: a stylesheet pasted into <style> that
        # contains </style> would end the element early and dump the rest of
        # the CSS into the document as text.
        if kind == "css" and "</style" in chunk.lower():
            raise BuildError(f"{path} contains `</style` — it cannot be inlined")
        if kind == "svg" and "<symbol id=" not in chunk and "<svg" not in chunk:
            raise BuildError(f"{path} does not look like SVG")

        # The stylesheet is the one include that ships smaller than it is read.
        if kind == "css":
            original = chunk
            chunk = inline_css(chunk)
            # inline_css is a regex over text, so assert its own contract on its
            # own output rather than trusting it. Two clauses, and the second is
            # the one that matters: with comments and ALL whitespace removed, the
            # shipped CSS must be character-for-character the source's. Whitespace
            # between declarations is insignificant, so this compares the thing
            # that is not — the declarations themselves. It is what proves the
            # strip cannot have eaten a rule, which a size check cannot.
            if len(_ANY_COMMENT.findall(chunk)) != 1:
                raise BuildError(
                    f"{path}: comment stripping left "
                    f"{len(_ANY_COMMENT.findall(chunk))} comments — the shipped "
                    "CSS must carry its header and no other comment"
                )
            if _lean(original) != _lean(chunk):
                raise BuildError(
                    f"{path}: inlining changed the stylesheet's declarations, not "
                    "just its comments — the shipped CSS is no longer the source's"
                )

        text = text.replace(marker, chunk)

    if "<!--#include" in text:
        raise BuildError("an include marker survived splicing — unknown include name?")
    # The marker is matched against the page's TEXT, not its markup: the h1
    # now carries an inline span around "what it saw" (the hero's one accent),
    # and a raw-substring match would reject the page for its own typography.
    # Stripping tags is what verify-copy.py's extractor does for the same
    # reason -- block tags become newlines, inline tags vanish -- so this strip
    # is the same normalisation the copy gate already trusts. A marker is a
    # contiguous phrase a reader sees, and a reader does not see tags.
    marker_text = re.sub(r"<[^>]+>", "", text)
    if MARKER not in marker_text:
        raise BuildError(
            f"the spliced page does not contain its marker string {MARKER!r}.\n"
            "       That string is what verify-links.py checks for in _site/, so\n"
            "       losing it here means losing the guard against publishing the\n"
            "       previous home page."
        )
    # Three comment channels, one rule, and the third was added last: the
    # stylesheet's, the markup's, and now the script's. See inline_js for what
    # surfaced it (a 267 B margin under the script's own ceiling, 36% of it prose).
    write_text_lf(page, inline_js(inline_markup(text)))


def splice_library_includes() -> int:
    """Splice include markers into CARRIED pages, after they are copied.

    The library ships verbatim - that rule is the build's spine, and the
    marker guard at the end of copy_library() exists to keep it that way. So
    the library's one concession to the include system is strictly opt-in: a
    page that carries no `<!--#include` marker is untouched, byte for byte,
    and this pass touches nothing else. A page that DOES carry one gets the
    same splice the home page gets: the real figure, from its generator, not
    a hand-pasted copy that can drift. Only svg includes are offered here; a
    library page has no business inlining a second stylesheet.
    """
    count = 0
    for d in sorted(SITE.iterdir()):
        page = d / "index.html" if d.is_dir() else None
        if not page or not page.exists():
            continue
        text = page.read_text(encoding="utf-8")
        if "<!--#include" not in text:
            continue
        for name, (path, kind) in LIBRARY_INCLUDES.items():
            marker = f"<!--#include {name}-->"
            if marker not in text:
                continue
            if not path.is_file():
                raise BuildError(
                    f"missing include source for {marker}: {path}\n"
                    "       Run the generator that writes it and commit the output."
                )
            chunk = path.read_text(encoding="utf-8")
            if "<!--#include" in chunk:
                raise BuildError(
                    f"{path} contains an `<!--#include` marker literal."
                )
            text = text.replace(marker, chunk)
            count += 1
        write_text_lf(page, text)
    if count:
        # the same final guard splice_includes() keeps: no marker may survive
        for d in sorted(SITE.iterdir()):
            page = d / "index.html" if d.is_dir() else None
            if not page or not page.exists():
                continue
            t = page.read_text(encoding="utf-8")
            if "<!--#include" in t:
                raise BuildError(
                    f"{page} still carries an include marker after splicing"
                )
    return count


# --------------------------------------------------------------------------
# 3 · the carried library
# --------------------------------------------------------------------------

def copy_library() -> int:
    """Copy the 75 live pages verbatim. Zero rewrites.

    By directory and by allowlist. See the module docstring: a glob here is the
    one way to publish the previous home page with every check passing.
    """
    pages = sorted(
        d for d in LEGACY.iterdir()
        if d.is_dir() and (d / "index.html").exists() and d.name not in NOT_A_PAGE
    )
    for d in pages:
        copy_tree(d, SITE / d.name)
    for name in LIBRARY_FILES:
        copy_file(LEGACY / name, SITE / name)
    for name in LIBRARY_TREES:
        copy_tree(LEGACY / name, SITE / name)
    for name in LIBRARY_ROOT_FILES:
        copy_file(LEGACY / name, SITE / name)
    # Same text-level match as the splice check above: the h1 carries an
    # inline span, and the guard asks about the page's words, not its tags.
    built_text = re.sub(r"<[^>]+>", "",
                        (SITE / "index.html").read_text(encoding="utf-8"))
    if built_text.find(MARKER) < 0:
        raise BuildError("the library overwrote the new home page")
    return len(pages)


# --------------------------------------------------------------------------
# 5 · the sitemap
# --------------------------------------------------------------------------

def page_paths() -> list[str]:
    """Every page the artifact actually contains. Derived from _site/, not
    from a list someone maintains by hand — the two would drift, and a page
    missing from this list is missing from sitemap.xml with nothing to say so."""
    paths = ["/"]
    for d in sorted(SITE.iterdir()):
        if d.is_dir() and d.name not in NOT_A_PAGE and (d / "index.html").exists():
            paths.append(f"/{d.name}/")
    return paths


def write_library_index() -> None:
    """The door to the carried library, built from the pages themselves.

    Published at /library/index.html rather than at the artifact root, which is
    the only difference between this page and the eight root files: it has a
    directory of its own because /library/ is how a reader reaches it, and
    because the two verifiers count a directory with an index.html in it as a
    library article. `NOT_AN_ARTICLE` over there is what keeps 75 meaning 75.
    """
    try:
        page = make_library_index.build()
    except make_library_index.MissingCopy as exc:
        raise BuildError(str(exc)) from None
    path = SITE / "library" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(path, page)


def write_sitemap() -> int:
    paths = page_paths()
    try:
        # lastmod comes from the checked-in dates file, never from mtimes and
        # never from now(). A page with no entry raises rather than guessing.
        xml = make_sitemap.build(paths)
    except make_sitemap.MissingDate as exc:
        raise BuildError(str(exc)) from None
    write_text_lf(SITE / "sitemap.xml", xml)
    return len(paths)


# --------------------------------------------------------------------------

def main() -> int:
    if not (SOURCE / "index.html").is_file():
        raise BuildError(f"no page to assemble: {SOURCE / 'index.html'}")

    clean()
    copy_authored()
    copy_assets()
    # The page comes before the library, because the guard at the end of
    # copy_library() reads _site/index.html to prove the page is still there.
    splice_includes()
    copy_library()
    # Library splicing runs after the copy: it is opt-in per page (a marker
    # in the page's own markup), so verbatim copy remains the default and
    # the count tells the build log which pages took figures.
    spliced = splice_library_includes()
    # The index is written before the sitemap, because write_sitemap() derives
    # its paths from what is in _site/ — a page that is not there is a page the
    # sitemap does not know about.
    write_library_index()
    urls = write_sitemap()

    files = [p for p in SITE.rglob("*") if p.is_file()]
    if not files:
        raise BuildError("_site/ is empty")
    total = sum(p.stat().st_size for p in files)
    print(f"_site/  {len(files)} files, {total:,} B")
    print(f"        {urls} urls in sitemap.xml")
    if spliced:
        print(f"        {spliced} library include(s) spliced")
    print("        preview:  python -m http.server --directory _site 8080")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
