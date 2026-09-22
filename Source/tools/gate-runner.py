#!/usr/bin/env python3
"""Run the site's gates detached, write one verdict file the agent polls.

WHY THIS EXISTS. The gates drive real browsers in real time, which makes them
the slowest thing in an improvement loop (the motion self-test alone is
minutes). An agent that runs them in its own shell STOPS WORKING while they
run. This script is started detached, writes `.improvement/gates/STATUS` the
moment it finishes, and the agent reads that file when it is good and ready:
work continues while the evidence accumulates.

Usage:
    python Source/tools/gate-runner.py            # the standard sweep
    python Source/tools/gate-runner.py --quick    # skip the slowest gates
    (detach from a shell with:  start /b python ... > log 2>&1  on Windows,
     or nohup ... & on POSIX)

The verdict file is one line: PASS or FAIL, then the per-gate verdicts, then
a pointer to the full log. Exit codes live in the log; the file is the only
thing a reader needs.
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / ".improvement" / "gates"

# (name, command list, quick-skip?). --quick exists because a full self-test
# is the single longest gate; everything else is seconds.
GATES = [
    ("build",   [sys.executable, "Source/tools/build-site.py"], False),
    ("budget",  [sys.executable, "Source/tools/verify-budget.py"], False),
    ("figures", [sys.executable, "Source/tools/verify-figures.py"], False),
    ("copy",    [sys.executable, "Source/tools/verify-copy.py"], False),
    ("links",   [sys.executable, "Source/tools/verify-links.py"], False),
    ("motion",  [sys.executable, "Source/tools/audit-motion.py", "--jobs", "4"], False),
    ("palette", [sys.executable, "Source/tools/audit-palette.py"], True),
    ("contrast", [sys.executable, "Source/tools/audit-contrast.py",
                  "--pages", "/"], True),
    ("selftest", [sys.executable, "Source/tools/audit-motion.py",
                  "--self-test", "--jobs", "4"], True),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true",
                    help="skip the long-tail gates (palette, contrast, self-test)")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%H%M%S")
    log_path = OUT / ("gate-%s.log" % stamp)
    status_path = OUT / "STATUS"

    status_path.write_text("RUNNING full=%s log=%s\n"
                           % (not args.quick, log_path.name), encoding="utf-8")
    lines = ["gate run %s (full=%s)" % (stamp, not args.quick)]
    worst = 0
    with open(log_path, "w", encoding="utf-8", newline="\n") as log:
        for name, cmd, skippable in GATES:
            if args.quick and skippable:
                continue
            if "--jobs" in cmd:
                cmd = [c for c in cmd]
                cmd[cmd.index("--jobs") + 1] = str(args.jobs)
            log.write("$ %s\n" % " ".join(cmd))
            log.flush()
            proc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=1800)
            verdict = "ok" if proc.returncode == 0 else "FAIL(%d)" % proc.returncode
            lines.append("%-9s %s" % (name, verdict))
            if proc.returncode != 0:
                worst = 1
                break   # first failure is the finding; later gates would re-print it
            log.write("\n")
        total = "PASS" if worst == 0 else "FAIL"
        lines.append("done %s %s"
                     % (total, datetime.datetime.now().strftime("%H:%M:%S")))
        log.write("\n".join(lines) + "\n")
    status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
