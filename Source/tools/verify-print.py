#!/usr/bin/env python3
"""Verify the printed sheet, by printing it.

    python Source/tools/verify-print.py [--site DIR] [--pages / ...]
                                        [--json PATH] [--self-test]

Writes nothing into the site; prints one pass/fail per claim and a verdict
line. Requires headless Chrome and pypdf (pip install pypdf).

WHY THIS EXISTS. M60 found that a sheet printed from the top of the page
carried prose with every visual blank: the landing's whole reveal family
stayed cold on paper, because the print block released the close's cold
state (M24) and nothing else. The release now exists, and the contrast
audit's print pass measures its inks - but a measurement of colour is not a
measurement of presence, and nothing failed when the sheet went blank
because no gate read the sheet. This gate reads the sheet. It prints each
page with headless Chrome (--print-to-pdf, the same print media a reader's
browser applies), extracts the text, and asserts that the content the cold
states hide is actually there: the hero lines, the reading log's rows, the
plates' drawn strings, the accordion's answers printed open. A future rule
that re-arms a cold state on paper, or re-closes a disclosure, fails here
with the missing witness named - not three milestones later, if ever.

WHY PRINT THE PAGE RATHER THAN READ THE CASCADE. The same lesson M60 paid
for twice: the on-screen probe said a closed accordion panel computed
visible while the printed sheet said blank, and the sheet was right - the
UA hides a closed panel on its ::details-content pseudo, which child-level
cascade reasoning never sees. A PDF is the browser's own answer to "what
would print", extraction is the sheet's own account of what it carried, and
neither can be talked into a pass by a rule that loses.

WHAT THE MASK LESSON MEANS FOR THE PROBES. A masked element's text can
still extract (the h1's second line did), and a line-wrap splits a probe
string (it did). So every probe is prose that was verifiably ABSENT before
M60's fix and PRESENT after - the reading-log rows, the boundary plate's
labels, the etymology caption, the accordion's closed answers - and the
probe strings are kept short enough to survive the sheet's own wrapping.
The hero line is probed too, but it is the least trustworthy witness and
the failure message says so.

--self-test doctors a fixture the way audit-motion's does: one page whose
stylesheet releases the cold state on paper (which must pass) and one whose
stylesheet omits the release (which must fail). The gate has not proven
itself until it catches its own defect.

Standard library except pypdf; Chrome found as audit-contrast finds it.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import functools
import http.server
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

# The landing is the page the cold states live on: the reveal family, the
# stop ring's roll, the ruler's estimate, the accordion. The library shares
# the same stylesheet and arms the same cold state on an article's figure
# itself (M65: the vram-split plate printed blank from the top of the page,
# one arm of the shared rule later), so one article rides in the default
# scope with its plate's own drawn strings as probes.
DEFAULT_PAGES = ["/", "/what-is-vram/"]

# Per-page probes: the landing's claims are the shared PROBES list; a library
# page's claims are the drawn strings of its own plate. Keyed by page path.
PAGE_PROBES = {
    "/what-is-vram/": [
        ("the vram-split plate's title line", "one model, one card, two bit-widths"),
        ("the 8-bit rung's label", "at 8 bits"),
        ("the 8-bit rung's VRAM bar", "VRAM 4 GB"),
        ("the split's own sentence", "16 of 32 layers fit"),
        ("the split's cost", "every token pays the trip"),
        ("the 4-bit rung's label", "at 4 bits"),
    ],
}

# Every probe: (name, string that must appear in the sheet's extracted text).
# Each one is rendered prose or a drawn plate string, and each was verifiably
# absent from the pre-M60 sheet. Short strings: the sheet wraps lines, and a
# probe that spans a wrap point fails for the wrong reason.
PROBES = [
    ("the reading log's first row", "discovered in 1901"),
    ("the reading log's third source", "Nature.com"),
    ("the unverified mark", "Unverified, check the source."),
    ("the evidence's first number", "354.08"),
    ("the stop ring's caption", "1.0141"),
    ("the boundary plate's label", "a document you gave it"),
    ("the etymology caption", "reconstructed"),
    ("the accordion's second answer", "we do not print a number"),
    ("the accordion's third answer", "Ollama or llama.cpp installed"),
    ("the hero's second line (the least trustworthy witness: a mask can hide text a PDF still extracts)", "what it saw"),
]


def find_chrome() -> str:
    env = os.environ.get("CHROME")
    if env:
        return env
    for c in CHROME_CANDIDATES:
        if os.path.sep in c or "/" in c:
            if os.path.isfile(c):
                return c
        else:
            found = shutil.which(c)
            if found:
                return found
    sys.exit("verify-print: no Chrome found. Set CHROME=/path/to/chrome.")


class Quiet(http.server.SimpleHTTPRequestHandler):
    """A server log no one reads is noise between the gate and its verdict."""

    def log_message(self, *a):
        pass


def serve(site: Path):
    handler = functools.partial(Quiet, directory=str(site))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def print_to_pdf(chrome: str, url: str, out: Path) -> str:
    """One sheet. Returns chrome's stderr tail if the PDF never appeared."""
    cmd = [chrome, "--headless", "--disable-gpu",
           f"--print-to-pdf={out}", "--no-pdf-header-footer",
           "--print-to-pdf-no-header", "--virtual-time-budget=12000", url]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    if not out.is_file() or out.stat().st_size == 0:
        tail = " | ".join((p.stderr or "").strip().splitlines()[-2:]) or "(no output)"
        return tail
    return ""


def extract_text(pdf: Path) -> str:
    from pypdf import PdfReader
    r = PdfReader(str(pdf))
    text = "\n".join((page.extract_text() or "") for page in r.pages)
    return re.sub(r"\s+", " ", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", help="built site directory (default ROOT/_site)")
    ap.add_argument("--pages", nargs="*", default=None,
                    help="pages to print (default: the landing)")
    ap.add_argument("--json", help="write the findings as JSON to this path")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.self_test:
        return self_test()

    site = Path(args.site) if args.site else ROOT / "_site"
    if not site.is_dir():
        sys.exit("verify-print: no built site at %s - run build-site.py first"
                 % site)
    try:
        import pypdf  # noqa: F401
    except ImportError:
        sys.exit("verify-print: pypdf is missing - pip install pypdf. "
                 "A gate that cannot read the sheet is a gate that cannot run, "
                 "and a gate that cannot run is a FAIL, not a pass with an "
                 "asterisk.")

    chrome = find_chrome()
    pages = args.pages if args.pages is not None else DEFAULT_PAGES
    srv = serve(site)
    port = srv.server_address[1]
    tmp = Path(tempfile.mkdtemp(prefix="istor-print-"))
    findings: list[dict] = []
    worst = 0
    try:
        for page in pages:
            url = "http://127.0.0.1:%d%s" % (port, page)
            pdf = tmp / (page.strip("/").replace("/", "_") or "index" + ".pdf")
            err = print_to_pdf(chrome, url, pdf)
            if err:
                findings.append({"page": page, "probe": "(the sheet itself)",
                                 "ok": False,
                                 "note": "chrome produced no PDF: %s" % err})
                worst = 1
                continue
            try:
                text = extract_text(pdf)
            except Exception as e:
                findings.append({"page": page, "probe": "(the sheet itself)",
                                 "ok": False,
                                 "note": "PDF unreadable: %s" % e})
                worst = 1
                continue
            # A library page's claims are its own plate's strings, not the
            # landing's - the vram article legitimately lacks the reading log.
            for name, needle in PAGE_PROBES.get(page, PROBES):
                ok = needle in text
                findings.append({"page": page, "probe": name, "ok": ok,
                                 "needle": needle})
                if not ok:
                    worst = 1
                print("  %s  %-28s %r" % ("ok  " if ok else "FAIL", name,
                                          needle), flush=True)
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(findings)
    bad = sum(1 for f in findings if not f["ok"])
    if worst:
        verdict = ("print FAILED - %d of %d claims missing from the sheet. "
                   "A cold state re-armed on paper, a disclosure re-closed, "
                   "or the page itself failed to print; the missing probe "
                   "names the witness." % (bad, total))
        print(verdict, file=sys.stderr)
    else:
        verdict = ("print ok - %d claims about the printed sheet, verified "
                   "by printing the pages rather than by reading them "
                   "(%s: cold states released, the accordion open)"
                   % (total, ", ".join(pages)))
        print(verdict)

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(
            {"verdict": verdict, "pages": pages, "findings": findings},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("verify-print: findings written %s" % args.json)
    return worst


# The self-test's fixture. One page whose stylesheet releases the cold state
# and the closed disclosure on paper; one identical page whose stylesheet
# omits the release. The fixture is a miniature of the landing on purpose:
# it carries the gate's own probe strings, so the same machinery that judges
# the real page judges the fixture. The cold state hides with visibility
# rather than opacity, because the M60 lesson cuts both ways - opacity:0
# text can still extract (the masked h1 did), and a self-test that passed
# for the wrong reason would be worse than none.
FIXTURE_HEAD = """<!doctype html><meta charset="utf-8">
<title>print self-test</title>
<style>
  body { font: 16px serif; }
  .is-cold .pv-piece { visibility: hidden; }
"""

FIXTURE_RELEASE = """  @media print {
    .is-cold .pv-piece { visibility: visible; }
    details::details-content { content-visibility: visible; block-size: auto; }
  }
"""

FIXTURE_BODY = """</style>
<p>the control sentence prints either way</p>
<div class="pv-cold is-cold">
  <p class="pv-piece">discovered in 1901</p>
  <p class="pv-piece">Nature.com</p>
  <p class="pv-piece">Unverified, check the source.</p>
  <p class="pv-piece">354.08</p>
  <p class="pv-piece">1.0141</p>
  <p class="pv-piece">a document you gave it</p>
  <p class="pv-piece">reconstructed</p>
  <p class="pv-piece">what it saw</p>
</div>
<details><summary>the question</summary>
  <div>we do not print a number</div>
  <div>Ollama or llama.cpp installed</div>
</details>
"""

FIXTURE_OK = FIXTURE_HEAD + FIXTURE_RELEASE + FIXTURE_BODY
FIXTURE_BAD = FIXTURE_HEAD + FIXTURE_BODY


def self_test() -> int:
    fixture = Path(tempfile.mkdtemp(prefix="istor-print-selftest-"))
    (fixture / "released.html").write_text(FIXTURE_OK, encoding="utf-8")
    (fixture / "doctored.html").write_text(FIXTURE_BAD, encoding="utf-8")
    here = Path(__file__).resolve()

    def run_gate(page: str):
        return subprocess.run(
            [sys.executable, str(here), "--site", str(fixture),
             "--pages", page],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300)

    print("print self-test: the released fixture must pass")
    ok_run = run_gate("/released.html")
    ok = ok_run.returncode == 0
    print("  %s  released fixture %s" % ("ok  " if ok else "FAIL",
                                         "passes" if ok else "did not pass:\n"
                                         + ok_run.stdout + ok_run.stderr))

    print("print self-test: the doctored fixture must fail")
    bad_run = run_gate("/doctored.html")
    caught = bad_run.returncode != 0
    named = "the reading log's first row" in (bad_run.stdout + bad_run.stderr)
    print("  %s  doctored fixture %s%s" %
          ("ok  " if caught else "FAIL",
           "fails, and the gate names the missing witness"
           if caught and named else "fails" if caught else "did not fail",
           "" if caught else ":\n" + bad_run.stdout + bad_run.stderr))

    shutil.rmtree(fixture, ignore_errors=True)
    if ok and caught:
        print("print self-test ok: the gate catches the re-armed cold state "
              "and passes the released page")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
