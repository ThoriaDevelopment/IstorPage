#!/usr/bin/env python3
"""audit-palette.py - the search palette, driven.

    python Source/tools/audit-palette.py [--self-test] [--site _site] [--json f.json]

The library's search is the newest thing on the site and the least covered: it lives
on all 76 library pages plus the landing, it is built at runtime - a dialog the script
creates, rows the script draws from a fetched index - and neither of the other two
audits can see any of it. `audit-contrast.py` measures pages a reader can load and this
dialog only exists after a click; `audit-motion.py` measures arrivals, which is a
different question. So this drives it, in a real browser, with real events, and asserts
twenty-six things a reader would notice if they broke.

WHAT IS DRIVEN RATHER THAN READ, and why each one needs a browser:

* **The order of two events**: that nothing fetches the index until a reader opens the
  palette. Read as source, "fetch happens in open()" is a claim about the code; measured
  as `performance.getEntriesByType('resource')` it is a claim about the network, and the
  two differ the moment load() is called from the bottom of the file.
* **Focus**, which is the whole keyboard story: the caret lands in the field, ArrowDown
  moves real focus onto a real link, the walk turns round at both ends, and closing hands
  focus back to the trigger. Every one of those is invisible in the source and obvious in
  the browser.
* **A synthetic click's default action**: the trigger is an `<a href="/library/">`, so
  what makes it a dialog is one `preventDefault()`. Remove it and the page navigates to
  the directory - which is the no-script behaviour, arriving from a script.
* **Two keys on one page**: `/` belongs to the directory's own field (it has one, and its
  copy invites the reader to use it), and Cmd/Ctrl+K opens the palette there. That
  precedence is a fact about two scripts and one document, not about either file.
* **Reduced motion**, where the palette must still open: its transition is gated, its
  behaviour is not.
* **What counts as a match**, which is a rule and not a line: the fold below turns a typed
  word into the few spellings of it that count, and the only honest way to check a rule
  like that is to type the words - a plural the library wrote in the singular, a spelling
  it does not use, a base form whose inflected form is the only one on the page, and the
  word it must still refuse.

FOUR THINGS THIS FILE IS CAREFUL ABOUT, each the shape of a bug it would otherwise miss:

* **An absent answer is a finding.** `audit-motion.py`'s harness reports success when a
  scenario returns nothing, because a probe that never calls itself back evaluates to a
  function and `JSON.stringify` drops it. Same trap here, same treatment, inherited
  rather than re-learned: the run is imported from that tool.
* **A patch that patches nothing is a failure of the self-test**, not a pass: every
  doctored file asserts the text it edits was actually there.
* **The claim a patch is aimed at has to be the claim that FAILS**, by name. A patch that
  trips some other assertion proves the suite works and not that this check works.
* **A claim about a rule is proved by the queries it answers, not by reading the table.**
  Each patch below removes one published row of the fold or one guard around it, and the
  suite fails if the claim that row exists for is not the claim that broke - so the table
  in `search.js` cannot quietly lose a row and keep a passing suite.

Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load_sibling(name: str):
    """Import a hyphenated sibling, the way the other audits do."""
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        sys.exit("audit-palette: %s is missing, and this tool drives its harness "
                 "rather than a second copy of one" % path)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


AC = load_sibling("audit-contrast.py")
AM = load_sibling("audit-motion.py")

# The page the palette is expected to work on, and the directory, which has a find
# field of its own and is therefore the interesting second case.
LIBRARY_PAGE = "/what-is-a-gguf/"


# --------------------------------------------------------------------------
# The scenarios. Each is ONE expression, awaited by the harness, with `d` (the
# framed document) and `w` (its window) in scope.
# --------------------------------------------------------------------------

PALETTE_SCENARIO = r"""
(async (d, w) => {
  const out = {};
  const until = async (fn, ms) => {
    const t0 = Date.now();
    while (Date.now() - t0 < (ms || 6000)) {
      if (fn()) return true;
      await new Promise(r => w.setTimeout(r, 50));
    }
    return false;
  };
  const fetches = () => w.performance.getEntriesByType('resource')
    .filter(e => e.name.indexOf('search-index.json') !== -1).length;

  const trigger = d.querySelector('[data-search-open]');
  out.triggerTag = trigger ? trigger.tagName : null;
  out.triggerHref = trigger ? trigger.getAttribute('href') : null;
  out.roleBefore = trigger ? trigger.getAttribute('role') : null;
  out.expandedBefore = trigger ? trigger.getAttribute('aria-expanded') : null;
  out.dialogBefore = !!d.querySelector('.palette');
  out.fetchesBeforeOpen = fetches();
  if (!trigger) return out;

  /* Focus first, because a real click on a link focuses it and a synthetic one does
     not: without this the platform hands focus back to the body on close, and the
     probe would report a focus bug the browser never has. */
  out.pathBefore = w.location.pathname;
  trigger.focus();
  trigger.click();
  out.dialogAfter = !!d.querySelector('.palette');
  const dialog = d.querySelector('.palette');
  out.isModal = dialog ? dialog.matches(':modal') : false;

  /* The trigger is a link, so what makes it open a dialog is one preventDefault.
     Waited for on the HARNESS's own clock rather than the frame's, because the
     failure this measures is the frame navigating away - and a timer owned by a
     document that has just been replaced never fires. `w` is a window proxy, so its
     location is the new document's, which is exactly the thing being read. */
  await new Promise(r => setTimeout(r, 400));
  out.pathAfter = w.location.pathname;
  /* Three ways out before the rest of the walk, all of them the failure itself: the
     dialog never opened, or the frame followed the link. Carrying on would run the
     remaining probes against a document that is not this one, and the run would
     report "the scenario threw" instead of the claim that broke. */
  if (!out.dialogAfter || out.pathAfter !== out.pathBefore) return out;
  out.roleAfter = trigger.getAttribute('role');
  out.haspopup = trigger.getAttribute('aria-haspopup');
  out.expandedOpen = trigger.getAttribute('aria-expanded');
  const field = d.getElementById('palette-field');
  out.caretInField = d.activeElement === field;

  const got = await until(() => d.querySelectorAll('.palette-link').length > 0);
  out.rowsAppeared = got;
  out.fetchesAfterOpen = fetches();
  out.rowCount = d.querySelectorAll('.palette-link').length;
  out.openRowsAreGroups = d.querySelectorAll('.palette-hit.is-group').length;
  out.saidWhenEmpty = (d.querySelector('.palette-said') || {}).textContent || null;

  /* A query that matches: the rows, their links, and the marks. */
  field.value = 'quantization';
  field.dispatchEvent(new w.Event('input', {bubbles: true}));
  await until(() => (d.querySelector('.palette-said') || {}).textContent
    && d.querySelector('.palette-said').textContent.indexOf('match') !== -1);
  out.saidWithQuery = d.querySelector('.palette-said').textContent;
  const links = [].slice.call(d.querySelectorAll('.palette-link'));
  out.hrefs = links.map(a => a.getAttribute('href'));
  out.marks = d.querySelectorAll('.palette mark').length;
  out.foreignElements = d.querySelectorAll('.palette img, .palette script, ' +
                                           '.palette iframe, .palette object').length;
  out.pwned = typeof w.__pwned;

  /* The walk. ArrowDown from the field enters the list; both ends turn round. */
  field.focus();
  field.dispatchEvent(new w.KeyboardEvent('keydown',
    {key: 'ArrowDown', bubbles: true, cancelable: true}));
  out.firstStop = d.activeElement && d.activeElement.tagName;
  out.firstStopHref = d.activeElement && d.activeElement.getAttribute
    ? d.activeElement.getAttribute('href') : null;
  field.dispatchEvent(new w.KeyboardEvent('keydown',
    {key: 'ArrowDown', bubbles: true, cancelable: true}));
  out.secondStopHref = d.activeElement ? d.activeElement.getAttribute('href') : null;
  d.activeElement.dispatchEvent(new w.KeyboardEvent('keydown',
    {key: 'ArrowUp', bubbles: true, cancelable: true}));
  out.backUpHref = d.activeElement ? d.activeElement.getAttribute('href') : null;
  d.activeElement.dispatchEvent(new w.KeyboardEvent('keydown',
    {key: 'ArrowUp', bubbles: true, cancelable: true}));
  out.upFromFirstIsField = d.activeElement === field;

  /* Enter opens the first result. The click is intercepted so the frame does not
     navigate: what is being asserted is that Enter activates the first row's link. */
  let entered = null;
  const first = d.querySelector('.palette-link');
  out.enterExpected = first ? first.getAttribute('href') : null;
  if (first) {
    first.addEventListener('click', function (event) {
      entered = first.getAttribute('href');
      event.preventDefault();
    }, true);
    field.focus();
    field.dispatchEvent(new w.KeyboardEvent('keydown',
      {key: 'Enter', bubbles: true, cancelable: true}));
  }
  out.enterOpened = entered;

  /* The platform's own dismissal: the script must not stand in for it. Closing
     hands focus back and clears the announced state, which a dialog that traps
     focus itself has to be told to do. */
  field.value = 'quantization';
  field.dispatchEvent(new w.Event('input', {bubbles: true}));
  const keptOpen = d.querySelector('.palette').open;
  d.querySelector('.palette').close();
  await new Promise(r => w.setTimeout(r, 200));
  out.wasOpen = keptOpen;
  out.closedNow = !d.querySelector('.palette').open;
  out.focusBack = d.activeElement === trigger;
  out.expandedClosed = trigger.getAttribute('aria-expanded');

  trigger.click();
  await new Promise(r => w.setTimeout(r, 200));
  out.keptQuery = d.getElementById('palette-field').value;
  d.querySelector('.palette').close();
  out.fetchesAtEnd = fetches();
  return out;
})(d, w)
"""

DIRECTORY_SCENARIO = r"""
(async (d, w) => {
  const out = {};
  const key = (target, k, mods) => target.dispatchEvent(new w.KeyboardEvent('keydown',
    Object.assign({key: k, bubbles: true, cancelable: true}, mods || {})));

  /* `/` on the directory belongs to the page's own field, whose copy tells the
     reader so. The palette must not take it. */
  key(d, '/');
  out.focusAfterSlash = d.activeElement ? d.activeElement.id : null;
  out.dialogAfterSlash = !!d.querySelector('.palette');

  key(d, 'k', {ctrlKey: true});
  await new Promise(r => w.setTimeout(r, 400));
  out.dialogAfterCtrlK = !!d.querySelector('.palette');
  out.modalAfterCtrlK = d.querySelector('.palette')
    ? d.querySelector('.palette').matches(':modal') : false;
  out.caretAfterCtrlK = d.activeElement ? d.activeElement.id : null;
  if (d.querySelector('.palette')) d.querySelector('.palette').close();
  return out;
})(d, w)
"""

LANDING_SCENARIO = r"""
(async (d, w) => {
  const out = {};
  const until = async (fn, ms) => {
    const t0 = Date.now();
    while (Date.now() - t0 < (ms || 6000)) {
      if (fn()) return true;
      await new Promise(r => w.setTimeout(r, 50));
    }
    return false;
  };
  const trigger = d.querySelector('[data-search-open]');
  out.trigger = !!trigger;
  out.inTheClose = !!(trigger && trigger.closest('#the-library ~ * , .reading'));
  out.scriptTags = d.querySelectorAll('script[src="/search.js"]').length;
  if (!trigger) return out;
  trigger.click();
  const field = d.getElementById('palette-field');
  out.opened = !!d.querySelector('.palette');
  out.caret = d.activeElement === field;
  await until(() => d.querySelectorAll('.palette-link').length > 0);
  field.value = 'hallucination';
  field.dispatchEvent(new w.Event('input', {bubbles: true}));
  await until(() => d.querySelectorAll('.palette-hit').length > 0);
  const first = d.querySelector('.palette-link');
  out.firstHref = first ? first.getAttribute('href') : null;
  out.rows = d.querySelectorAll('.palette-link').length;
  out.said = (d.querySelector('.palette-said') || {}).textContent || null;
  d.querySelector('.palette').close();
  return out;
})(d, w)
"""

REDUCED_SCENARIO = r"""
(async (d, w) => {
  const out = {};
  const until = async (fn, ms) => {
    const t0 = Date.now();
    while (Date.now() - t0 < (ms || 6000)) {
      if (fn()) return true;
      await new Promise(r => w.setTimeout(r, 50));
    }
    return false;
  };
  const trigger = d.querySelector('[data-search-open]');
  out.reduced = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!trigger) return out;
  trigger.click();
  out.opened = !!d.querySelector('.palette');
  await until(() => d.querySelectorAll('.palette-link').length > 0);
  const field = d.getElementById('palette-field');
  field.value = 'quantization';
  field.dispatchEvent(new w.Event('input', {bubbles: true}));
  await until(() => d.querySelectorAll('.palette-hit').length > 0);
  out.rows = d.querySelectorAll('.palette-hit').length;
  out.firstHref = d.querySelector('.palette-link')
    ? d.querySelector('.palette-link').getAttribute('href') : null;
  out.opacity = d.querySelector('.palette')
    ? w.getComputedStyle(d.querySelector('.palette')).opacity : null;
  d.querySelector('.palette').close();
  return out;
})(d, w)
"""

FOLD_SCENARIO = r"""
(async (d, w) => {
  /* Seven queries in one page load, typed the way a reader types them, and for each
     one what the palette said, how many rows it drew, where the first one goes and
     what it marked. The claims below are all about this table, so the probes read
     the palette's own output rather than any part of the fold implementation. */
  const out = {results: {}, error: null};
  const until = async (fn, ms) => {
    const t0 = Date.now();
    while (Date.now() - t0 < (ms || 6000)) {
      if (fn()) return true;
      await new Promise(r => w.setTimeout(r, 50));
    }
    return false;
  };
  const trigger = d.querySelector('[data-search-open]');
  if (!trigger) { out.error = 'no trigger on the page'; return out; }
  trigger.click();
  const field = d.getElementById('palette-field');
  const drew = await until(() => d.querySelectorAll('.palette-hit.is-group').length > 0);
  if (!field || !drew) { out.error = 'the palette never drew its groups'; return out; }

  const queries = ['hallucinations', 'llms', 'gpus', 'cars', 'quantisation',
                   'tokeniser', 'boundary', 'mixture of experts', 'quantiz'];
  for (const q of queries) {
    field.value = q;
    field.dispatchEvent(new w.Event('input', {bubbles: true}));
    /* Waited for by the query's own name or by the nothing line: a stale render from
       the previous query satisfies neither, so a probe cannot read the last answer. */
    const answered = await until(() => {
      const said = (d.querySelector('.palette-said') || {}).textContent || '';
      return said.indexOf(q) !== -1 || said.indexOf('Nothing') !== -1;
    });
    const links = [].slice.call(d.querySelectorAll('.palette-results .palette-link'));
    const first = d.querySelector('.palette-results .palette-hit');
    out.results[q] = {
      answered: answered,
      rows: links.length,
      firstHref: links.length ? links[0].getAttribute('href') : null,
      said: (d.querySelector('.palette-said') || {}).textContent || null,
      marks: first
        ? [].slice.call(first.querySelectorAll('mark')).map(m => m.textContent) : []
    };
  }
  d.querySelector('.palette').close();
  return out;
})(d, w)
"""


# --------------------------------------------------------------------------
# The claims. Counted, so the verdict can say how much was asserted.
# --------------------------------------------------------------------------

CHECKED = [0]
PALETTE_CLAIMS = (
    "the trigger is a link to the directory before anything runs",
    "no dialog exists until a reader asks for one",
    "the index is not fetched until the palette opens",
    "clicking the trigger opens the dialog instead of following its link",
    "opening shows a modal dialog with the caret in the field",
    "the palette fetches the index exactly once",
    "a query draws rows that link into the library, with the matched words marked",
    "the count line names how many pages matched",
    "ArrowDown walks the results as real links, and the walk is bounded",
    "Enter from the field opens the first result",
    "closing returns focus to the trigger and says it is closed",
    "reopening keeps what was typed",
    "the trigger's role and state are announced once a script can honour them",
    "no element reaches the palette from the page's own text",
)
DIRECTORY_CLAIMS = (
    "`/` still belongs to the directory's own field",
    "Cmd/Ctrl+K opens the palette over the directory",
)
LANDING_CLAIMS = (
    "the landing's close offers the search, and it opens the same dialog",
    "a result opened from the landing links into the library",
)
REDUCED_CLAIMS = (
    "with motion reduced the palette still opens and works",
)

# The fold. Every one of these is a sentence a reader could hold the palette to, and
# every one was measured against the built index before the rule was written: the
# numbers in the details are what the rule buys, and one of them is what it refuses.
FOLD_CLAIMS = (
    "a plural the library does not write finds the page that writes the singular",
    "a two-letter stem still folds, so the short plurals of acronyms work too",
    "a folded spelling only counts as the whole word, so a word this library never uses finds nothing",
    "the spelling this library does not use finds the one it does",
    "a base form finds the page that only ever writes it inflected",
    "a query this library cannot answer still reports nothing",
    "a partial word marks the whole word it was found in",
)


def _ok(failures: list, label: str, good: bool, detail: str = "") -> None:
    CHECKED[0] += 1
    print("  %s  %-62s %s" % ("ok  " if good else "FAIL", label, detail))
    if not good:
        failures.append(label)


def check_palette(doc: dict, failures: list) -> None:
    if "error" in doc:
        _ok(failures, "the scenario ran", False, doc["error"])
        return
    v = doc

    _ok(failures, "the trigger is a link to the directory before anything runs",
        v.get("triggerTag") == "A" and v.get("triggerHref") == "/library/",
        "%s[href=%s]" % (v.get("triggerTag"), v.get("triggerHref")))
    _ok(failures, "no dialog exists until a reader asks for one",
        v.get("dialogBefore") is False, "nothing in the DOM before the click")

    _ok(failures, "the trigger's role and state are announced once a script can honour them",
        v.get("roleAfter") == "button" and v.get("haspopup") == "dialog"
        and v.get("expandedOpen") == "true" and v.get("roleBefore") == "button"
        and v.get("expandedBefore") == "false",
        "role=%s, haspopup=%s, expanded %s then %s"
        % (v.get("roleBefore"), v.get("haspopup"), v.get("expandedBefore"),
           v.get("expandedOpen")))
    _ok(failures, "clicking the trigger opens the dialog instead of following its link",
        v.get("pathAfter") == v.get("pathBefore") and v.get("dialogAfter"),
        "%s -> %s, dialog %s" % (v.get("pathBefore"), v.get("pathAfter"),
                                  v.get("dialogAfter")))
    _ok(failures, "opening shows a modal dialog with the caret in the field",
        v.get("dialogAfter") and v.get("isModal") and v.get("caretInField"),
        "modal %s, caret in the field %s" % (v.get("isModal"), v.get("caretInField")))
    _ok(failures, "the index is not fetched until the palette opens",
        v.get("fetchesBeforeOpen") == 0,
        "%s request(s) for search-index.json before the click"
        % v.get("fetchesBeforeOpen"))
    _ok(failures, "the palette fetches the index exactly once",
        v.get("fetchesAfterOpen") == 1 and v.get("fetchesAtEnd") == 1,
        "%s after opening, %s by the end" % (v.get("fetchesAfterOpen"),
                                             v.get("fetchesAtEnd")))

    hrefs = v.get("hrefs") or []
    _ok(failures, "a query draws rows that link into the library, with the matched words marked",
        v.get("rowsAppeared") and hrefs and all(h and h.startswith("/") for h in hrefs)
        and (v.get("marks") or 0) > 0,
        "%s row(s), %s mark(s), first %s" % (len(hrefs), v.get("marks"),
                                             hrefs[0] if hrefs else "-"))
    _ok(failures, "the count line names how many pages matched",
        isinstance(v.get("saidWithQuery"), str)
        and "match" in v["saidWithQuery"] and "\"" in v["saidWithQuery"],
        (v.get("saidWithQuery") or "")[:52])
    _ok(failures, "ArrowDown walks the results as real links, and the walk is bounded",
        v.get("firstStop") == "A" and v.get("firstStopHref") in hrefs
        and v.get("secondStopHref") in hrefs
        and v.get("secondStopHref") != v.get("firstStopHref")
        and v.get("backUpHref") == v.get("firstStopHref")
        and v.get("upFromFirstIsField") is True,
        "down enters the list, up walks back and leaves through the field")
    _ok(failures, "Enter from the field opens the first result",
        v.get("enterOpened") is not None
        and v.get("enterOpened") == v.get("enterExpected"),
        "Enter activated %s" % v.get("enterOpened"))

    _ok(failures, "closing returns focus to the trigger and says it is closed",
        v.get("wasOpen") and v.get("closedNow") and v.get("focusBack")
        and v.get("expandedClosed") == "false",
        "was %s, now closed %s, focus back %s, expanded %s"
        % (v.get("wasOpen"), v.get("closedNow"), v.get("focusBack"),
           v.get("expandedClosed")))
    _ok(failures, "reopening keeps what was typed",
        v.get("keptQuery") == "quantization", "the field came back as %r"
        % v.get("keptQuery"))
    _ok(failures, "no element reaches the palette from the page's own text",
        (v.get("foreignElements") or 0) == 0 and v.get("pwned") == "undefined",
        "no img/script/iframe in the panel, no side effect")


def check_directory(doc: dict, failures: list) -> None:
    if "error" in doc:
        _ok(failures, "the scenario ran", False, doc["error"])
        return
    _ok(failures, "`/` still belongs to the directory's own field",
        doc.get("focusAfterSlash") == "find" and doc.get("dialogAfterSlash") is False,
        "focus on #find, no palette")
    _ok(failures, "Cmd/Ctrl+K opens the palette over the directory",
        doc.get("dialogAfterCtrlK") and doc.get("modalAfterCtrlK")
        and doc.get("caretAfterCtrlK") == "palette-field",
        "dialog %s, modal %s, focus %s"
        % (doc.get("dialogAfterCtrlK"), doc.get("modalAfterCtrlK"),
           doc.get("caretAfterCtrlK")))


def check_landing(doc: dict, failures: list) -> None:
    if "error" in doc:
        _ok(failures, "the scenario ran", False, doc["error"])
        return
    _ok(failures, "the landing's close offers the search, and it opens the same dialog",
        doc.get("trigger") and doc.get("inTheClose") and doc.get("scriptTags") == 1
        and doc.get("opened") and doc.get("caret") and (doc.get("rows") or 0) > 0,
        "%s row(s) for 'hallucination'" % doc.get("rows"))
    _ok(failures, "a result opened from the landing links into the library",
        isinstance(doc.get("firstHref"), str) and doc["firstHref"].startswith("/"),
        doc.get("firstHref") or "-")


def check_fold(doc: dict, failures: list) -> None:
    if doc.get("error"):
        _ok(failures, "the scenario ran", False, doc.get("error") or doc["error"])
        return
    r = doc.get("results") or {}

    def of(q: str) -> dict:
        return r.get(q) or {}

    plural = of("hallucinations")
    _ok(failures, FOLD_CLAIMS[0],
        plural.get("firstHref") == "/what-is-ai-hallucination/"
        and (plural.get("rows") or 0) >= 1,
        "'hallucinations' -> %s, %s row(s), and the library's own count says %s"
        % (plural.get("firstHref") or "nothing", plural.get("rows"),
           (plural.get("said") or "").split(".")[0]))

    # Both of the library's acronyms, and the first of them is why the strip row's
    # guard was measured rather than reasoned about: a version that refused a word
    # ending in `us` found nothing for "gpus" while "gpu" is a word of eight pages.
    short, gpus = of("llms"), of("gpus")
    _ok(failures, FOLD_CLAIMS[1],
        short.get("firstHref") == "/what-is-a-local-llm/" and (gpus.get("rows") or 0) >= 1,
        "'llms' -> %s, 'gpus' -> %s row(s) where it found none"
        % (short.get("firstHref") or "nothing", gpus.get("rows")))

    # The bound. "car" is a substring of 22 indexed pages - card, care, carries,
    # carry - and a whole word of none of them, so a reader who types "cars" must be
    # told the library has nothing rather than handed 22 pages that never said it.
    bound = of("cars")
    _ok(failures, FOLD_CLAIMS[2],
        (bound.get("rows") or 0) == 0
        and "Nothing" in (bound.get("said") or ""),
        "'cars' -> %s row(s), though 'car' is inside 22 indexed pages: %s"
        % (bound.get("rows"), (bound.get("said") or "")[:40]))

    oz = of("quantisation")
    iser = of("tokeniser")
    _ok(failures, FOLD_CLAIMS[3],
        oz.get("firstHref") == "/what-is-quantization/" and (iser.get("rows") or 0) >= 1,
        "'quantisation' -> %s, 'tokeniser' -> %s row(s)"
        % (oz.get("firstHref") or "nothing", iser.get("rows")))

    base = of("boundary")
    _ok(failures, FOLD_CLAIMS[4],
        base.get("firstHref") == "/how-document-chunking-works/",
        "'boundary' -> %s, which is the only page that writes 'boundaries'"
        % (base.get("firstHref") or "nothing"))

    nothing = of("mixture of experts")
    _ok(failures, FOLD_CLAIMS[5],
        (nothing.get("rows") or 0) == 0
        and "Nothing" in (nothing.get("said") or ""),
        "'mixture of experts' -> %s row(s): the fold offers spellings, not answers"
        % nothing.get("rows"))

    partial = of("quantiz")
    _ok(failures, FOLD_CLAIMS[6],
        "quantization" in (partial.get("marks") or []),
        "'quantiz' marks %s rather than the seven letters typed"
        % (partial.get("marks") or ["nothing"]))


def check_reduced(doc: dict, failures: list) -> None:
    if "error" in doc:
        _ok(failures, "the scenario ran", False, doc["error"])
        return
    _ok(failures, "with motion reduced the palette still opens and works",
        doc.get("reduced") is True and doc.get("opened")
        and (doc.get("rows") or 0) > 0 and doc.get("firstHref", "").startswith("/")
        and doc.get("opacity") in ("1", ""),
        "reduced motion, %s row(s), opacity %s" % (doc.get("rows"), doc.get("opacity")))


# --------------------------------------------------------------------------
# The self-test: every claim above, handed a file that breaks it.
# --------------------------------------------------------------------------

# (what, [(old, new)], the claim it must break, (file it doctors, page to drive))
SELF_TESTS = [
    ("the click no longer prevents the link's default",
     [("opener.addEventListener('click', function (event) {\n    event.preventDefault();\n    open();",
       "opener.addEventListener('click', function (event) {\n    open();")],
     "clicking the trigger opens the dialog instead of following its link",
     ("search.js", "/what-is-a-gguf/")),
    ("the dialog is opened without showModal, so it is not modal",
     [("dialog.showModal();", "dialog.setAttribute('open', '');")],
     "opening shows a modal dialog with the caret in the field",
     ("search.js", "/what-is-a-gguf/")),
    ("the index is fetched at load rather than when a reader asks",
     [("  document.addEventListener('keydown', function (event) {",
       "  load();\n\n  document.addEventListener('keydown', function (event) {")],
     "the index is not fetched until the palette opens",
     ("search.js", "/what-is-a-gguf/")),
    ("ArrowDown no longer walks into the results",
     [("    if (event.key === 'ArrowDown') {\n      if (walk(1)) event.preventDefault();\n      return;\n    }",
       "    if (event.key === 'ArrowDown') {\n      return;\n    }")],
     "ArrowDown walks the results as real links, and the walk is bounded",
     ("search.js", "/what-is-a-gguf/")),
    ("Enter no longer opens the first result",
     [("      var links = rows();\n      if (links.length) {\n        event.preventDefault();\n        links[0].click();\n      }",
       "      return;")],
     "Enter from the field opens the first result",
     ("search.js", "/what-is-a-gguf/")),
    ("the reader's query is not kept between openings",
     [("    if (kept) field.value = kept;", "    field.value = '';")],
     "reopening keeps what was typed",
     ("search.js", "/what-is-a-gguf/")),
    ("closing no longer clears the announced state",
     [("      opener.setAttribute('aria-expanded', 'false');", "")],
     "closing returns focus to the trigger and says it is closed",
     ("search.js", "/what-is-a-gguf/")),
    ("the palette takes the slash key the directory's field owns",
     [("    if (event.key === '/' && plain && !typing && !pageFind &&",
       "    if (event.key === '/' && plain && !typing && true &&")],
     "`/` still belongs to the directory's own field",
     ("search.js", "/library/")),
    ("the palette is unreachable by keyboard on the directory",
     [("    if ((event.metaKey || event.ctrlKey) && (event.key === 'k' || event.key === 'K')) {",
       "    if (false) {")],
     "Cmd/Ctrl+K opens the palette over the directory",
     ("search.js", "/library/")),
    ("the landing stops naming the palette's script",
     [('<script src="/search.js" defer></script>', "")],
     "the landing's close offers the search, and it opens the same dialog",
     ("index.html", "/")),
    ("the marked words stop being marked",
     [("      var mark = document.createElement('mark');", "      var mark = document.createElement('b');")],
     "a query draws rows that link into the library, with the matched words marked",
     ("search.js", "/what-is-a-gguf/")),
    # The fold's own patches. Each removes one published row or one guard, so what
    # fails is the claim that row is there for and nothing else about the palette.
    ("the plural stops folding, so a typed plural finds nothing",
     [("    ['strip', 's', ''],\n", "")],
     "a plural the library does not write finds the page that writes the singular",
     ("search.js", LIBRARY_PAGE)),
    ("the spelling this library does not use stops being swapped",
     [("    ['swap', 'isation', 'ization'], ['swap', 'iser', 'izer'],\n", "")],
     "the spelling this library does not use finds the one it does",
     ("search.js", LIBRARY_PAGE)),
    ("a base form stops being completed into the plural the page writes",
     [("    ['add', 'y', 'ies'],\n", "")],
     "a base form finds the page that only ever writes it inflected",
     ("search.js", LIBRARY_PAGE)),
    ("a folded spelling is allowed to match inside a longer word",
     [("      if (!whole || (!WORDISH.test(before) && !WORDISH.test(after))) {",
       "      if (true) {")],
     "a folded spelling only counts as the whole word, so a word this library never uses finds nothing",
     ("search.js", LIBRARY_PAGE)),
    ("a partial word stops widening to the word it was found in",
     [("  function widen(text, from, to) {\n    while (from > 0 && WORDISH.test(text.charAt(from - 1))) from--;\n"
       "    while (to < text.length && WORDISH.test(text.charAt(to))) to++;\n    return [from, to];\n  }",
       "  function widen(text, from, to) {\n    return [from, to];\n  }")],
     "a partial word marks the whole word it was found in",
     ("search.js", LIBRARY_PAGE)),
]

# The one patch that is not a script edit: the index is doctored with markup in a
# title, which the generator refuses to write, and the palette has to render it as
# text. It is a self-test because the real file cannot contain it.
INDEX_PATCH = ("a doctored index carries markup in a title",
               "the palette draws it as text, and nothing runs")


def self_test(chrome, site, width, height, tmp, only: str = "") -> int:
    print("self-test: %d doctored files, each of which must fail one named claim"
          % (len(SELF_TESTS) + 1))
    worst = 0
    for i, (what, edits, expected, (rel, url)) in enumerate(SELF_TESTS):
        if only and only not in what:
            continue
        broken = os.path.join(tmp, "broken-%d" % i)
        if os.path.isdir(broken):
            shutil.rmtree(broken)
        shutil.copytree(site, broken)
        patched = os.path.join(broken, rel)
        if not os.path.isfile(patched):
            print("  FAIL  %s: %s is not a file in the built site, so this self-test "
                  "is checking nothing" % (what, rel))
            worst = 1
            continue
        text = open(patched, encoding="utf-8").read()
        missing = [old for old, _new in edits if old not in text]
        if missing:
            print("  FAIL  %s: the text it patches is not in %s (%r), so this self-test "
                  "is checking nothing" % (what, rel, missing[0][:48]))
            worst = 1
            continue
        for old, new in edits:
            text = text.replace(old, new, 1)
        AC.write(patched, text)

        # The patch is driven by the family its claim belongs to and no other: a
        # browser per patch is the cost, and one that loads four pages to prove one
        # thing is a self-test nobody runs. The claim is read off the patch's own
        # declaration, so a new patch cannot forget to name the page it needs.
        failures: list = []
        if expected in REDUCED_CLAIMS:
            scenario, extra, checker = (REDUCED_SCENARIO,
                                        ["--force-prefers-reduced-motion"],
                                        check_reduced)
        elif expected in DIRECTORY_CLAIMS:
            scenario, extra, checker = DIRECTORY_SCENARIO, None, check_directory
        elif expected in LANDING_CLAIMS:
            scenario, extra, checker = LANDING_SCENARIO, None, check_landing
        elif expected in FOLD_CLAIMS:
            scenario, extra, checker = FOLD_SCENARIO, None, check_fold
        else:
            scenario, extra, checker = PALETTE_SCENARIO, None, check_palette
        doc = AM.run(chrome, broken, tmp, url, width, height, scenario,
                     extra=extra, tag="st%d" % i)
        checker(doc, failures)
        named = expected in failures
        print("  %s  %s -> %s" % ("ok  " if named else "FAIL", what,
                                  (", ".join(failures) or "nothing failed")))
        if not named:
            worst = 1

    # The doctored index. Markup in a title, and a query that matches it: the palette
    # must draw the string as text, and no element or side effect may appear.
    what, expected = INDEX_PATCH
    if not only or only in what:
        broken = os.path.join(tmp, "broken-index")
        if os.path.isdir(broken):
            shutil.rmtree(broken)
        shutil.copytree(site, broken)
        path = os.path.join(broken, "search-index.json")
        records = json.load(open(path, encoding="utf-8"))
        for record in records:
            if record["url"] == "/what-is-a-gguf/":
                record["title"] = ('<img src=x onerror="w.__pwned=1"> '
                                   'What is a GGUF file?')
        AC.write(path, json.dumps(records, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":")) + "\n")
        doc = AM.run(chrome, broken, tmp, "/what-is-a-gguf/", width, height,
                     PALETTE_SCENARIO, extra=None, tag="st-index")
        failures = []
        check_palette(doc, failures)
        ok = ("no element reaches the palette from the page's own text" in failures
              or doc.get("foreignElements") == 0) and doc.get("pwned") == "undefined" \
            and isinstance(doc.get("saidWithQuery"), str)
        # The claim has to be the one that is asserted, so this asks the SAME line
        # the standing run asks rather than a second version of it.
        print("  %s  %s -> %s" % ("ok  " if ok else "FAIL", what,
                                  ("markup stayed text" if ok
                                   else ", ".join(failures) or "nothing failed")))
        if not ok:
            worst = 1

    if worst == 0:
        print("self-test ok - every doctored file is caught by the claim it breaks")
    return worst


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", default=os.path.join(ROOT, "_site"))
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--json", default="")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--only", default="",
                    help="with --self-test, run only the patches whose name contains "
                         "this text: a whole run is a dozen browsers")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.site):
        print("error: %s is not a directory - run build-site.py first" % a.site,
              file=sys.stderr)
        return 1
    chrome = AC.find_chrome()
    tmp = tempfile.mkdtemp(prefix="istor-palette-")
    try:
        if a.self_test:
            return self_test(chrome, a.site, a.width, a.height, tmp, a.only)

        print("the search palette, driven: %s at %dpx" % (a.site, a.width))
        failures: list = []
        doc = AM.run(chrome, a.site, tmp, LIBRARY_PAGE, a.width, a.height,
                     PALETTE_SCENARIO, extra=None, tag="palette")
        check_palette(doc, failures)
        fdoc = AM.run(chrome, a.site, tmp, LIBRARY_PAGE, a.width, a.height,
                      FOLD_SCENARIO, extra=None, tag="fold")
        check_fold(fdoc, failures)
        ddoc = AM.run(chrome, a.site, tmp, "/library/", a.width, a.height,
                      DIRECTORY_SCENARIO, extra=None, tag="directory")
        check_directory(ddoc, failures)
        ldoc = AM.run(chrome, a.site, tmp, "/", a.width, a.height,
                      LANDING_SCENARIO, extra=None, tag="landing")
        check_landing(ldoc, failures)
        rdoc = AM.run(chrome, a.site, tmp, LIBRARY_PAGE, a.width, a.height,
                      REDUCED_SCENARIO, extra=["--force-prefers-reduced-motion"],
                      tag="reduced")
        check_reduced(rdoc, failures)

        if a.json:
            with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"palette": doc, "fold": fdoc, "directory": ddoc,
                           "landing": ldoc, "reduced": rdoc,
                           "failures": failures}, fh, indent=1)
            print("\nfindings written to %s" % a.json)

        print()
        if failures:
            print("FAILED - %d of %d claims are not true of the page:\n  %s"
                  % (len(failures), CHECKED[0], "\n  ".join(failures)))
            return 1
        print("palette ok - %d claims about the library's search, on a carried page, "
              "the directory and the landing, verified by driving them"
              % CHECKED[0])
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
