"""Terminal display helpers for stash previews."""

from __future__ import annotations

from typing import List

from stashpull.preview import DiffLine, parse_diff, format_summary_line
from stashpull.stash import StashEntry

# ANSI colour codes
_GREEN = "\033[32m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"
_BOLD = "\033[1m"

_KIND_COLOUR = {
    "added": _GREEN,
    "removed": _RED,
    "header": _CYAN,
    "meta": _YELLOW,
    "context": "",
}


def _colourise(line: DiffLine, *, colour: bool = True) -> str:
    if not colour:
        return line.content
    prefix = _KIND_COLOUR.get(line.kind, "")
    suffix = _RESET if prefix else ""
    return f"{prefix}{line.content}{suffix}"


def render_diff(raw: str, *, colour: bool = True, max_lines: int = 0) -> str:
    """Render a unified diff as a colourised string.

    Args:
        raw: Raw diff text.
        colour: Whether to include ANSI colour codes.
        max_lines: If > 0, truncate output to this many diff lines.

    Returns:
        Formatted string ready for terminal output.
    """
    parsed: List[DiffLine] = parse_diff(raw)
    if max_lines > 0:
        parsed = parsed[:max_lines]
    return "\n".join(_colourise(dl, colour=colour) for dl in parsed)


def render_entry_header(entry: StashEntry, *, colour: bool = True) -> str:
    """Return a formatted header line for a stash entry."""
    index_str = f"stash@{{{entry.index}}}"
    if colour:
        return (
            f"{_BOLD}{_CYAN}{index_str}{_RESET} "
            f"{_YELLOW}[{entry.branch}]{_RESET} "
            f"{entry.message}"
        )
    return f"{index_str} [{entry.branch}] {entry.message}"


def render_preview(entry: StashEntry, raw_diff: str, *, colour: bool = True) -> str:
    """Combine entry header, summary, and diff into a single preview block."""
    header = render_entry_header(entry, colour=colour)
    summary = format_summary_line(raw_diff)
    diff_body = render_diff(raw_diff, colour=colour)
    separator = "-" * 60
    return "\n".join([header, summary, separator, diff_body])
