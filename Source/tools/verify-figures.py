#!/usr/bin/env python3
"""Assert that every committed figure is what its generator writes today.

    python Source/tools/verify-figures.py

Seven SVGs in `Source/figures/` are generated and committed. Each one carries a
"do not hand-edit" comment inside it, and **nothing checked that claim**: a
hand-edit, or a generator changed without its output being regenerated, ships a
page drawn by a version of the tool that no longer exists. That is not a
hypothetical failure mode. It happened twice on this site in one session, both
times caught by luck rather than by a check: an edit to the hero's placement that
was in the generator and not in the figure, and a plate whose box widths came from
a measurement the figure did not have.

The claim in SITE_BUILD_PLAN.md is that `verify-budget.py` catches a stale
regeneration. It does not, quite. It catches a stale figure that changes the
page's byte total past a ceiling it asserts, which is a different and much larger
event than a figure three hundred bytes out of date.

This is a gate, not a report, so it takes the four steps a gate needs:

  1  Run each generator, in place, in this working tree.
  2  Compare what it wrote to what was on disk, BY BYTES. `read_text()` and
     `write_text()` translate newlines, so a CRLF copy of the right drawing
     compares equal to a fresh LF one — the icon sprite learned that first, and
     .gitattributes says the same thing from the other side.
  3  Put the working tree back, whatever the comparison said. A check that leaves
     the workspace modified is a check nobody runs twice, and this repository is
     sometimes shared with another editor mid-thought.
  4  Run each generator's own `--self-test` where it has one, so the invariant
     tests travel with the gate instead of living in whoever remembers them.

Standard library only, and it needs no built site: it compares sources to sources.
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = HERE.parent
FIGURES = SOURCE / "figures"

# Outputs are named as paths from `Source/`, not as bare file names, and the reason is the
# dial: a generator writes one file that is not a figure and does not live in figures/
# (`temperature-dial.partial`, spliced into a carried page by the build). One rule for
# every output is cheaper to read than a rule with an exception on the end of it.

# Each generator, the figures it owns, and its self-test flag where it has one.
# The outputs are listed rather than discovered: a generator that quietly stops
# writing one variant should say so here, not pass because nothing looked for it.
GENERATORS: list[tuple[str, tuple[str, ...], bool]] = [
    ("make-boundary.py", ("figures/boundary-wide.svg", "figures/boundary-mid.svg", "figures/boundary-tall.svg"), True),
    ("make-calendar-ring.py", ("figures/calendar-ring.svg",), False),
    ("make-etymology.py", ("figures/etymology.svg", "figures/etymology-tall.svg"), False),
    ("make-hero-gears.py", ("figures/hero-gears.svg",), True),
    ("make-close-gears.py", ("figures/close-gears.svg",), True),
    ("make-poster-horizon.py", ("figures/poster-horizon.svg",), False),
    ("make-gguf-anatomy.py", ("figures/gguf-anatomy-wide.svg", "figures/gguf-anatomy-tall.svg"), True),
    ("make-citation-anatomy.py", ("figures/citation-anatomy-wide.svg", "figures/citation-anatomy-tall.svg"), True),
    ("make-context-window.py", ("figures/context-window-wide.svg", "figures/context-window-tall.svg"), True),
    ("make-group-marks.py", ("figures/group-mark-what-it-is.svg",
                             "figures/group-mark-how-it-works-and-why-it-behaves-that-way.svg",
                             "figures/group-mark-how-to-do-it.svg",
                             "figures/group-mark-whether-it-can.svg",
                             "figures/group-mark-using-it-for-your-own-work.svg",
                             "figures/group-mark-compared-with-other-tools.svg",
                             "figures/group-mark-the-project-log.svg"), True),
    ("make-quant-ladder.py", ("figures/quant-ladder-wide.svg", "figures/quant-ladder-tall.svg"), True),
    ("make-ram-budget.py", ("figures/ram-budget-wide.svg", "figures/ram-budget-tall.svg"), True),
    ("make-q4km-anatomy.py", ("figures/q4km-anatomy-wide.svg", "figures/q4km-anatomy-tall.svg"), True),
    ("make-token-rows.py", ("figures/token-rows-wide.svg", "figures/token-rows-tall.svg"), True),
    ("make-attention-profile.py", ("figures/attention-profile-wide.svg", "figures/attention-profile-tall.svg"), True),
    ("make-temperature.py", ("figures/temperature-wide.svg", "figures/temperature-tall.svg",
                           "temperature-dial.partial"), True),
]


class Report:
    """Collects pass/fail lines so one run reports everything, not just the first."""

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


def run(tool: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / tool), *args],
                          cwd=ROOT, capture_output=True, text=True)


def first_difference(a: bytes, b: bytes) -> str:
    """Where two blobs part company, in a form that fits on one line."""
    limit = min(len(a), len(b))
    at = next((i for i in range(limit) if a[i] != b[i]), limit)
    line = a[:at].count(b"\n") + 1
    return f"first difference at byte {at} (line {line}), {len(a)} B on disk vs {len(b)} B written"


def main() -> int:
    rep = Report()

    for tool, outputs, has_self_test in GENERATORS:
        # 1. Snapshot, so the tree can be restored exactly as it was found --
        #    including uncommitted work, which is the normal state of this repo.
        before = {}
        for name in outputs:
            path = SOURCE / name
            before[name] = path.read_bytes() if path.is_file() else None

        if has_self_test:
            st = run(tool, ["--self-test"])
            if st.returncode == 0:
                line = (st.stdout or "").strip().splitlines()
                rep.ok(f"{tool} --self-test", line[-1].strip() if line else "")
            else:
                rep.fail(f"{tool} --self-test", (st.stderr or st.stdout).strip()[:400])

        # 2. Generate.
        proc = run(tool, [])
        if proc.returncode != 0:
            rep.fail(tool, (proc.stderr or proc.stdout).strip()[:400] or
                     f"exited {proc.returncode}")

        # 3. Compare and restore, per output.
        for name in outputs:
            path = SOURCE / name
            old = before[name]
            new = path.read_bytes() if path.is_file() else None
            if new is None:
                rep.fail(f"{name}", f"the generator did not write it (expected in {FIGURES})")
            elif old is None:
                rep.fail(f"{name}", "not in the repository — a figure has to be committed, "
                                    "since the build inlines it")
            elif old == new:
                rep.ok(f"{name} matches its generator", f"{len(new):,} B")
            else:
                rep.fail(f"{name} is stale",
                         f"{first_difference(old, new)} — rerun {tool} and commit the result")
            # Whether it matched or not, put back what was here when we started.
            if old is not None:
                path.write_bytes(old)
            elif path.is_file():
                path.unlink()

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} checks", file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"figures ok - {rep.checks} checks, every committed figure is its generator's output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
