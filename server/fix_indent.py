#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
One-click indentation fixer for ./server directory.

What it does:
1) Scan all .py files under server/
2) Detect:
   - Tabs in leading indentation
   - Mixed indentation (tabs + spaces used for leading indentation)
3) Fix:
   - Replace leading tabs with 4 spaces each
   - Optionally normalize leading spaces to multiples of 4 (default ON)
4) Create backup files: <file>.bak_indentfix
5) Print a summary report

Usage:
  python3 server/fix_indent.py
  python3 server/fix_indent.py --check-only
  python3 server/fix_indent.py --no-normalize
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from typing import List, Tuple


SERVER_DIR = os.path.join(os.path.dirname(__file__), ".")
PY_FILE_RE = re.compile(r".*\.py$", re.IGNORECASE)


@dataclass
class FileReport:
    path: str
    had_tab_indent: bool
    had_space_indent: bool
    had_mixed_indent: bool
    lines_changed: int
    tabs_remaining: int
    total_lines: int


def iter_py_files(root: str) -> List[str]:
    out: List[str] = []
    for base, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(base, fn)
            if PY_FILE_RE.match(p):
                out.append(p)
    out.sort()
    return out


def count_remaining_tabs_in_indent(lines: List[str]) -> int:
    c = 0
    for line in lines:
        # count tabs only in leading whitespace
        m = re.match(r"^[ \t]+", line)
        if m and "\t" in m.group(0):
            c += 1
    return c


def analyze_indent(lines: List[str]) -> Tuple[bool, bool, bool]:
    """Returns (had_tab_indent, had_space_indent, had_mixed_indent)."""
    had_tab = False
    had_space = False
    for line in lines:
        m = re.match(r"^[ \t]+", line)
        if not m:
            continue
        ws = m.group(0)
        if "\t" in ws:
            had_tab = True
        if " " in ws:
            had_space = True
    return had_tab, had_space, (had_tab and had_space)


def fix_line_indent(line: str, normalize_spaces: bool) -> Tuple[str, bool]:
    """
    Fix one line:
      - replace leading tabs with 4 spaces
      - optionally normalize leading spaces to multiples of 4 (round down)
    Returns: (new_line, changed?)
    """
    m = re.match(r"^([ \t]+)(.*)$", line)
    if not m:
        return line, False

    ws, rest = m.group(1), m.group(2)

    # Replace tabs in leading indentation
    if "\t" in ws:
        ws2 = ws.replace("\t", " " * 4)
    else:
        ws2 = ws

    # Normalize leading spaces to multiples of 4
    # NOTE: This is a pragmatic fixer. If a file used 2-space indentation consistently,
    # you can disable this with --no-normalize.
    if normalize_spaces:
        # count spaces only (tabs already converted)
        space_count = len(ws2)
        # keep exact indentation for empty-line (pure whitespace) to avoid diff noise
        if rest.strip() == "" and line.strip() == "":
            ws3 = ws2
        else:
            ws3 = " " * (space_count - (space_count % 4))
        ws2 = ws3

    new_line = ws2 + rest
    return new_line, (new_line != line)


def fix_file(path: str, check_only: bool, normalize_spaces: bool) -> FileReport:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    had_tab, had_space, had_mixed = analyze_indent(lines)

    new_lines: List[str] = []
    changed = 0
    for line in lines:
        nl, ch = fix_line_indent(line, normalize_spaces=normalize_spaces)
        new_lines.append(nl)
        if ch:
            changed += 1

    tabs_remaining = count_remaining_tabs_in_indent(new_lines)

    if (not check_only) and changed > 0:
        backup = path + ".bak_indentfix"
        if not os.path.exists(backup):
            with open(backup, "w", encoding="utf-8") as bf:
                bf.writelines(lines)
        with open(path, "w", encoding="utf-8") as wf:
            wf.writelines(new_lines)

    return FileReport(
        path=path,
        had_tab_indent=had_tab,
        had_space_indent=had_space,
        had_mixed_indent=had_mixed,
        lines_changed=changed,
        tabs_remaining=tabs_remaining,
        total_lines=len(lines),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true", help="Only report, do not write changes")
    ap.add_argument("--no-normalize", action="store_true", help="Do not normalize spaces to multiples of 4")
    args = ap.parse_args()

    root = os.path.abspath(os.path.join(SERVER_DIR))
    files = iter_py_files(root)

    if not files:
        print("[indentfix] No .py files found under server/")
        return

    reports: List[FileReport] = []
    for p in files:
        rep = fix_file(p, check_only=args.check_only, normalize_spaces=(not args.no_normalize))
        reports.append(rep)

    # Summary
    touched = [r for r in reports if r.lines_changed > 0]
    mixed = [r for r in reports if r.had_mixed_indent]
    tabbed = [r for r in reports if r.had_tab_indent]
    still_tab = [r for r in reports if r.tabs_remaining > 0]

    mode = "CHECK" if args.check_only else "FIX"
    print(f"[indentfix:{mode}] scanned={len(reports)} files | changed={len(touched)} files")
    print(f"[indentfix:{mode}] had_tab_indent={len(tabbed)} | had_mixed_indent={len(mixed)} | tabs_remaining_after={len(still_tab)}")

    if touched:
        print("\n[indentfix] changed files:")
        for r in touched:
            print(f"  - {r.path} | lines_changed={r.lines_changed} | tabs_remaining={r.tabs_remaining}")

    if still_tab:
        print("\n[indentfix] WARNING: tabs still remain in leading indentation (please inspect):")
        for r in still_tab:
            print(f"  - {r.path} | tabs_remaining={r.tabs_remaining}")

    if not args.check_only:
        print("\n[indentfix] backups created as: *.bak_indentfix (only for files that changed, first run only)")


if __name__ == "__main__":
    main()