#!/usr/bin/env python3
"""Run unattended Istor improvement cycles with an external coding agent.

The runner starts one fresh agent process per goal, waits for it to finish,
records the result, and starts the next goal. It does not grant git permissions
or invent an agent command. Configure ISTOR_AGENT_COMMAND or pass --agent-command.

Examples:
    python Source/tools/background-runner.py --cycles 3
    python Source/tools/background-runner.py --forever --interval 30
    set ISTOR_AGENT_COMMAND=claude -p {prompt}
    python Source/tools/background-runner.py --forever
"""

from __future__ import annotations

import argparse
import datetime as datetime_module
import os
import pathlib
import shlex
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_GOALS = ROOT / "Documentation" / "OVERNIGHT_GOALS.md"
DEFAULT_LOG = ROOT / ".improvement" / "BACKGROUND_RUNNER.log"
DEFAULT_LOCK = ROOT / ".improvement" / "BACKGROUND_RUNNER.lock"
DEFAULT_COMMAND = "claude -p {prompt}"

MASTER_PROMPT = """You are working unattended in the IstorPage repository.
Read README.md before making decisions. Continue from the current checkout,
inspect existing changes before editing, and make the next useful improvement
rather than asking the user questions. Audit reference material and the running
preview when relevant. Every visitor-facing string must follow the project's
humanizer rule, and the site's own visible text must contain no em or en dashes.
Prefer creative, evidence-led improvements over cosmetic churn. Run the build
and validation checks after meaningful changes. Do not rewrite or discard
changes you did not make. Keep changes local unless the invoking command grants
git permissions. Complete this goal and exit successfully; the runner starts the
next goal in a fresh process. Do not return a conversational summary to the user.
"""


class RunnerError(RuntimeError):
    """A runner input or lifecycle failure."""


def timestamp() -> str:
    return datetime_module.datetime.now().astimezone().isoformat(timespec="seconds")


def resolve(root: pathlib.Path, value: pathlib.Path) -> pathlib.Path:
    return value if value.is_absolute() else root / value


def read_goals(path: pathlib.Path) -> list[str]:
    if not path.is_file():
        raise RunnerError(f"goal file does not exist: {path}")
    goals = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    goals = [line for line in goals if line and not line.startswith("#")]
    if not goals:
        raise RunnerError(f"goal file has no usable goals: {path}")
    return goals


def make_command(template: str, prompt: str) -> list[str]:
    try:
        parts = shlex.split(template, posix=(os.name != "nt"))
    except ValueError as exc:
        raise RunnerError(f"invalid agent command: {exc}") from exc
    if not parts:
        raise RunnerError("agent command is empty")
    if "{prompt}" in parts:
        return [part.replace("{prompt}", prompt) for part in parts]
    return [*parts, prompt]


def write_log(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        if not text.endswith("\n"):
            stream.write("\n")


def lock_pid(path: pathlib.Path) -> int | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("pid="):
                return int(line[4:])
    except (OSError, ValueError):
        return None
    return None


def process_is_alive(pid: int | None) -> bool:
    if pid is None:
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def take_lock(path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        if process_is_alive(lock_pid(path)):
            raise RunnerError(f"another runner appears active: {path}") from exc
        path.unlink(missing_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"pid={os.getpid()}\nstarted={timestamp()}\n")


def drop_lock(path: pathlib.Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def cycle_prompt(goal: str, number: int, total: str) -> str:
    return (
        f"{MASTER_PROMPT}\n\n"
        f"Unattended cycle {number}{total}.\n"
        f"Current goal:\n{goal}\n\n"
        "Do the work now. The runner captures your stdout and stderr in its log."
    )


def run_cycle(args: argparse.Namespace, goal: str, number: int, total: str) -> int:
    prompt = cycle_prompt(goal, number, total)
    command = make_command(args.agent_command, prompt)
    write_log(args.log, f"\n[{timestamp()}] cycle {number} START\nGOAL: {goal}\nCOMMAND: {command[0]}\n")
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=args.timeout or None,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        write_log(args.log, f"[{timestamp()}] cycle {number} TIMEOUT\n{exc}\n")
        return 124
    except OSError as exc:
        write_log(args.log, f"[{timestamp()}] cycle {number} ERROR\n{exc}\n")
        return 127
    write_log(
        args.log,
        f"[{timestamp()}] cycle {number} EXIT {result.returncode}\n"
        f"--- stdout ---\n{result.stdout or ''}\n"
        f"--- stderr ---\n{result.stderr or ''}\n",
    )
    return result.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goals", type=pathlib.Path, default=DEFAULT_GOALS)
    parser.add_argument("--log", type=pathlib.Path, default=DEFAULT_LOG)
    parser.add_argument("--lock", type=pathlib.Path, default=DEFAULT_LOCK)
    parser.add_argument("--agent-command", default=os.environ.get("ISTOR_AGENT_COMMAND", DEFAULT_COMMAND))
    parser.add_argument("--cycles", type=int, default=1, help="number of cycles; 0 means forever")
    parser.add_argument("--forever", action="store_true", help="same as --cycles 0")
    parser.add_argument("--interval", type=float, default=15.0, help="seconds between cycles")
    parser.add_argument("--timeout", type=float, default=0.0, help="cycle timeout; 0 means none")
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.cycles < 0 or args.interval < 0:
        raise RunnerError("cycles and interval cannot be negative")
    args.goals = resolve(ROOT, args.goals)
    args.log = resolve(ROOT, args.log)
    args.lock = resolve(ROOT, args.lock)
    goals = read_goals(args.goals)
    take_lock(args.lock)
    try:
        cycle = 0
        unlimited = args.forever or args.cycles == 0
        while unlimited or cycle < args.cycles:
            cycle += 1
            total = "" if unlimited else f" of {args.cycles}"
            code = run_cycle(args, goals[(cycle - 1) % len(goals)], cycle, total)
            if code and not args.continue_on_error:
                return code
            if unlimited or cycle < args.cycles:
                time.sleep(args.interval)
        return 0
    finally:
        drop_lock(args.lock)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RunnerError as exc:
        print(f"background-runner: {exc}", file=sys.stderr)
        raise SystemExit(2)
