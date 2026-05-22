"""Diff preview formatting for stash entries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

ADDED_PREFIX = "+"
REMOVED_PREFIX = "-"
HEADER_PREFIX = "@@"
META_PREFIXES = ("diff", "index", "---", "+++")


@dataclass
class DiffLine:
    content: str
    kind: str  # 'added', 'removed', 'header', 'meta', 'context'


def classify_line(line: str) -> str:
    """Return the semantic kind of a raw diff line."""
    if line.startswith(ADDED_PREFIX):
        return "added"
    if line.startswith(REMOVED_PREFIX):
        return "removed"
    if line.startswith(HEADER_PREFIX):
        return "header"
    for prefix in META_PREFIXES:
        if line.startswith(prefix):
            return "meta"
    return "context"


def parse_diff(raw: str) -> List[DiffLine]:
    """Parse a raw unified diff string into a list of DiffLine objects."""
    lines: List[DiffLine] = []
    for line in raw.splitlines():
        lines.append(DiffLine(content=line, kind=classify_line(line)))
    return lines


def summarise_diff(raw: str) -> dict:
    """Return a quick summary of additions/removals in a diff."""
    added = 0
    removed = 0
    files_changed: set[str] = set()
    for line in raw.splitlines():
        if line.startswith("+++ b/"):
            files_changed.add(line[6:])
        elif line.startswith(ADDED_PREFIX) and not line.startswith("+++"):
            added += 1
        elif line.startswith(REMOVED_PREFIX) and not line.startswith("---"):
            removed += 1
    return {
        "files_changed": sorted(files_changed),
        "additions": added,
        "deletions": removed,
    }


def format_summary_line(raw: str) -> str:
    """Return a compact one-line summary string for a diff."""
    s = summarise_diff(raw)
    files = len(s["files_changed"])
    return (
        f"{files} file(s) changed, "
        f"+{s['additions']} additions, "
        f"-{s['deletions']} deletions"
    )
