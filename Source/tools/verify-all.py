#!/usr/bin/env python3
"""Audit a commit the way this session learned to: from nothing but itself.

    python Source/tools/verify-all.py [--quick]

Builds HEAD in an isolated temporary worktree and runs every gate against
the result, printing one pass/fail line per gate and a signed verdict.

WHY THIS EXISTS. Twice in one session the working tree lied to the battery.
An in-tree run went green on gates whose committed versions failed the
committed page: a budget.json sat uncommitted while the document it
re-baselined went out, and a motion harness fix sat uncommitted while the
committed harness false-failed the page it was fixed for. The lesson is now
a tool: the audit judges the COMMIT, not the tree. It checks out HEAD
somewhere else, builds there, and runs only what HEAD carries, so its
verdict is reproducible from a fresh clone with nothing else.

THE GATES, in the order they run:

  build      build-site.py, in the worktree
  figures    verify-figures.py (each generator's --self-test rides inside it,
             as does the verbatim census)
  budget     verify-budget.py
  copy       verify-copy.py
  links      verify-links.py
  contrast   audit-contrast.py --pages /   (headless Chrome, the slow half)
  motion     audit-motion.py --jobs 4      (headless Chrome, the other half)

The two audits run sequentially - the parallel draft starved motion's
scroll-pacing claims and failed them false; see the finding at the loop.
The four verifies run first because they need no browser and fail fast.
--quick skips the audits: the whole fast battery in about a minute, for
the middle of an edit. The full run takes five to ten minutes and is
meant for the moment before handing the page to someone else.

A gate that cannot run (no Chrome, say) is a FAIL with the tool's own
error, not a pass with an asterisk: a battery that can silently skip a gate
is a battery that lies slowly.

The worktree is removed whatever happens, this repository being sometimes
shared with another editor mid-thought.

Standard library only.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    # The audits take "/" as an argument; Git Bash turns that into a drive
    # letter unless this is set. Harmless everywhere else.
    env["MSYS_NO_PATHCONV"] = "1"
    # The tools print UTF-8 (their outputs carry ’ and Greek); this process's
    # own locale on Windows is cp1252, whose reader thread dies on those
    # bytes. PYTHONIOENCODING pins every child's stdio so the verdict lines
    # survive the trip. A decode that failed silently once would report
    # "(no output)" on a FAILING gate - a battery that lies slowly.
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          env=env, encoding="utf-8", errors="replace")


def tail(text: str, lines: int = 3) -> str:
    out = [l.strip() for l in (text or "").strip().splitlines() if l.strip()]
    return " | ".join(out[-lines:]) if out else "(no output)"


def short(sha: str) -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          cwd=str(REPO), capture_output=True, text=True
                          ).stdout.strip() or sha[:7]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="skip the two headless audits")
    args = ap.parse_args()

    sha = short("HEAD")
    started = time.time()

    tmp = Path(tempfile.mkdtemp(prefix="istor-audit-"))
    print(f"verify-all: auditing commit {sha} in {tmp}", flush=True)

    results: list[tuple[str, bool, str]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        results.append((name, ok, detail))
        print(f"  {'ok  ' if ok else 'FAIL'}  {name:<10} {detail}", flush=True)

    try:
        add = run(["git", "worktree", "add", "--detach", str(tmp), "HEAD"],
                  cwd=REPO)
        if add.returncode != 0:
            print(f"FAILED - could not check out HEAD: {tail(add.stderr, 2)}",
                  file=sys.stderr)
            return 1

        # The build, and the four gates that need no browser. Any failure
        # here ends the run: an audit on a stale build would audit nothing.
        # Every tool is invoked by its RELATIVE path with the worktree as
        # cwd - the house convention - so each tool resolves its own tree
        # from its own __file__ and reads the worktree, never this tree.
        # (Invoking this directory's copies by absolute path would build and
        # audit the MAIN tree while reporting on the commit.)
        b = run([sys.executable, "Source/tools/build-site.py"], cwd=tmp)
        record("build", b.returncode == 0,
               tail(b.stdout, 1) if b.returncode == 0 else tail(b.stderr, 2))
        if b.returncode != 0:
            return finish(results, sha, started)

        for name, tool in (
            ("figures", "verify-figures.py"),
            ("budget", "verify-budget.py"),
            ("copy", "verify-copy.py"),
            ("links", "verify-links.py"),
        ):
            g = run([sys.executable, f"Source/tools/{tool}"], cwd=tmp)
            record(name, g.returncode == 0,
                   tail(g.stdout, 1) if g.returncode == 0 else tail(g.stderr, 2))

        if args.quick:
            return finish(results, sha, started)

        # The two audits, SEQUENTIALLY. The first draft ran them in parallel
        # and the parallelism was a finding of its own: motion's claims read
        # scroll pacing off a live page, and contrast's screenshot barrage
        # starved the machine while it read, turning "a page-sized jump is
        # not a gesture" false - the same claim that passes when motion has
        # the machine to itself. A harness that races a sibling is not
        # measuring the page. Each writes its json inside the worktree so
        # nothing lands outside the tree being torn down.
        for name, cmd in (
            ("contrast",
             [sys.executable, "Source/tools/audit-contrast.py",
              "--pages", "/", "--json", "audit-contrast.json"]),
            ("motion",
             [sys.executable, "Source/tools/audit-motion.py",
              "--jobs", "4"]),
        ):
            print(f"verify-all: {name} starting (headless Chrome)",
                  flush=True)
            p = subprocess.Popen(
                cmd, cwd=str(tmp), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True,
                encoding="utf-8", errors="replace",
                env={**os.environ, "MSYS_NO_PATHCONV": "1",
                     "PYTHONIOENCODING": "utf-8"})
            out, _ = p.communicate()
            # The audits' verdict lines are "contrast ok - ..." and
            # "motion ok - ..."; failures print FAILED blocks.
            ok_line = next((l for l in reversed(out.splitlines())
                            if " ok - " in l or l.startswith("FAILED")), "")
            record(name, p.returncode == 0,
                   ok_line.strip() if p.returncode == 0 else tail(out, 2))

        return finish(results, sha, started)
    finally:
        run(["git", "worktree", "remove", "--force", str(tmp)], cwd=REPO)
        shutil.rmtree(tmp, ignore_errors=True)


def finish(results, sha: str, started: float) -> int:
    bad = [n for n, ok, _ in results if not ok]
    mins = (time.time() - started) / 60.0
    print(flush=True)
    if bad:
        print(f"verify-all FAILED - commit {sha}, {len(bad)} of "
              f"{len(results)} gates: {', '.join(bad)} ({mins:.1f} min)",
              file=sys.stderr)
        return 1
    print(f"verify-all ok - commit {sha}, every gate green with nothing but "
          f"what HEAD carries ({mins:.1f} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
