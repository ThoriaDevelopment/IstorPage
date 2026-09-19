#!/usr/bin/env python3
"""Keep a Freebuff Desktop session moving by submitting "Please Continue".

This helper uses only Windows APIs exposed through ctypes. It does not inspect
Freebuff's private UI or require an automation package. The safest setup is to
measure the chat box once and pass its position relative to the Freebuff window:

    python Source/tools/freebuff-continue.py --chat-x 0.50 --chat-y 0.90 --interval 300

The interval is the reliable fallback. A sound detector is intentionally an
adapter rather than a guessed implementation: Windows does not expose a
portable way to identify one application's speaker cue. Use --cue-file with a
separate detector that touches a file, or --cue-command with a command that
returns exit code 0 when the cue has been heard. Without either option, the
helper submits on the interval.

TWO WAYS TO RUN IT WRONG, both of which the shell reports as something else
entirely, so neither is obvious from the error:

  * **Run it from the repository root, or from Source/tools without the
    prefix.** From Source/tools, `python Source/tools/freebuff-continue.py`
    resolves to Source/tools/Source/tools/... and fails with "can't open file".
  * **Keep every option on ONE line.** PowerShell ends the statement at each
    newline, so a pasted block where the options sit on their own lines parses
    line 2 as a statement beginning with `--`, which is the decrement operator,
    and reports "Missing expression after unary operator '--'". The `>>` at the
    start of those lines is PowerShell's continuation prompt, not part of the
    command.

Measure the click point before trusting it:

    python Source/tools/freebuff-continue.py --chat-x 0.50 --chat-y 0.90 --debug --dry-run

--dry-run moves the cursor to the computed point and types nothing, so a wrong
ratio costs nothing. --chat-x and --chat-y are ratios of the window's CLIENT
area, not pixels.

Stop with Ctrl+C. Use --max-sends to put a hard limit on unattended sends.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import pathlib
import subprocess
import sys
import time
from ctypes import wintypes

if os.name != "nt":
    raise SystemExit("freebuff-continue.py requires Windows")

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ULONG_PTR = getattr(wintypes, "ULONG_PTR", ctypes.c_size_t)

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.ClientToScreen.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
user32.SetCursorPos.restype = wintypes.BOOL
user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ULONG_PTR]
user32.mouse_event.restype = None
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ULONG_PTR]
user32.keybd_event.restype = None
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE

SW_RESTORE = 9
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56
VK_RETURN = 0x0D
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def window_title(hwnd: wintypes.HWND) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def find_window(title_fragment: str) -> tuple[wintypes.HWND, wintypes.RECT] | None:
    found: list[tuple[wintypes.HWND, wintypes.RECT]] = []
    wanted = title_fragment.casefold()

    @EnumWindowsProc
    def callback(hwnd: wintypes.HWND, _lparam: int) -> bool:
        if user32.IsWindowVisible(hwnd) and wanted in window_title(hwnd).casefold():
            rect = wintypes.RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                found.append((hwnd, rect))
                return False
        return True

    user32.EnumWindows(callback, 0)
    return found[0] if found else None


def set_clipboard(text: str) -> None:
    encoded = (text + "\0").encode("utf-16-le")
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    pointer = kernel32.GlobalLock(handle)
    if not pointer:
        kernel32.GlobalFree(handle)
        raise ctypes.WinError(ctypes.get_last_error())
    ctypes.memmove(pointer, encoded, len(encoded))
    kernel32.GlobalUnlock(handle)
    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise ctypes.WinError(ctypes.get_last_error())
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def key_press(vk: int) -> None:
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def chat_screen_point(hwnd: wintypes.HWND, x_ratio: float, y_ratio: float) -> tuple[int, int]:
    client = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(client)):
        raise ctypes.WinError(ctypes.get_last_error())
    origin = wintypes.POINT(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise ctypes.WinError(ctypes.get_last_error())
    width = client.right - client.left
    height = client.bottom - client.top
    return origin.x + int(width * x_ratio), origin.y + int(height * y_ratio)


def send_prompt(hwnd: wintypes.HWND, x_ratio: float, y_ratio: float, debug: bool = False, dry_run: bool = False) -> tuple[int, int]:
    user32.ShowWindow(hwnd, SW_RESTORE)
    if not user32.SetForegroundWindow(hwnd) and debug:
        print("Warning: Windows refused to make Freebuff foreground.", flush=True)
    time.sleep(0.4)
    x, y = chat_screen_point(hwnd, x_ratio, y_ratio)
    if debug:
        print(f"Clicking Freebuff client coordinate ({x}, {y}).", flush=True)
    user32.SetCursorPos(x, y)
    if dry_run:
        return x, y
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.25)
    set_clipboard("Please Continue")
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    key_press(VK_V)
    time.sleep(0.15)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.25)
    key_press(VK_RETURN)
    return x, y


def cue_ready(args: argparse.Namespace) -> bool:
    if args.cue_file:
        path = pathlib.Path(args.cue_file)
        if path.exists():
            path.unlink()
            return True
        return False
    if args.cue_command:
        return subprocess.run(args.cue_command, shell=True, cwd=args.cwd, check=False).returncode == 0
    return True


def parse_args() -> argparse.Namespace:
    # Raw form, so `--help` shows the worked examples on their own lines. The
    # default formatter reflows the docstring into one paragraph, which is how
    # the two run-it-wrong notes above became invisible to the person who hit
    # both of them in a row.
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--window", default="Freebuff", help="case-insensitive window-title fragment")
    parser.add_argument("--chat-x", type=float, required=True, help="chat-box x position as a window ratio from 0 to 1")
    parser.add_argument("--chat-y", type=float, required=True, help="chat-box y position as a window ratio from 0 to 1")
    parser.add_argument("--interval", type=float, default=300.0, help="fallback seconds between sends")
    parser.add_argument("--cue-file", help="wait for this file to appear, then send and remove it")
    parser.add_argument("--cue-command", help="shell command that returns 0 when a sound cue was detected")
    parser.add_argument("--max-sends", type=int, default=0, help="hard send limit; 0 means unlimited")
    parser.add_argument("--debug", action="store_true", help="print the selected window and click coordinate")
    parser.add_argument("--dry-run", action="store_true", help="move to the target only; do not click or type")
    parser.add_argument("--cwd", type=pathlib.Path, default=pathlib.Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 <= args.chat_x <= 1 or not 0 <= args.chat_y <= 1:
        raise SystemExit("--chat-x and --chat-y must be between 0 and 1")
    if args.interval < 1:
        raise SystemExit("--interval must be at least 1 second")
    if args.cue_file and args.cue_command:
        raise SystemExit("choose --cue-file or --cue-command, not both")
    sends = 0
    print("Freebuff Continue is running. Press Ctrl+C to stop.", flush=True)
    while args.max_sends == 0 or sends < args.max_sends:
        if cue_ready(args):
            target = find_window(args.window)
            if target is None:
                print("Freebuff window not found; retrying.", flush=True)
            else:
                hwnd, rect = target
                if args.debug:
                    print(f"Using window: {window_title(hwnd)!r} ({rect.left},{rect.top}) to ({rect.right},{rect.bottom}).", flush=True)
                x, y = send_prompt(hwnd, args.chat_x, args.chat_y, args.debug, args.dry_run)
                if args.dry_run:
                    print(f"Dry run moved the cursor to ({x}, {y}); nothing was typed.", flush=True)
                    return 0
                sends += 1
                print(f"Attempted Please Continue at ({x}, {y}) ({sends}). Verify the message appeared.", flush=True)
            if args.cue_file or args.cue_command:
                time.sleep(1)
            else:
                time.sleep(args.interval)
        else:
            time.sleep(min(1.0, args.interval))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
