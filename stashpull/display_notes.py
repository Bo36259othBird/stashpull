"""Helpers to incorporate per-stash notes into rendered output."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from stashpull.notes import get_note
from stashpull.stash import StashEntry

_NOTE_PREFIX = "\033[33m📝 "
_RESET = "\033[0m"
_DIM = "\033[2m"


def render_note_line(note: str, *, colour: bool = True) -> str:
    """Return a single formatted line for display in the TUI or plain output."""
    if not note:
        return ""
    if colour:
        return f"{_NOTE_PREFIX}{note}{_RESET}"
    return f"Note: {note}"


def annotate_entry_list(
    entries: Sequence[StashEntry],
    repo_root: Path | None = None,
    *,
    colour: bool = True,
) -> list[tuple[StashEntry, str]]:
    """Return *(entry, rendered_note)* pairs for every entry.

    The rendered note is an empty string when no note exists.
    """
    result: list[tuple[StashEntry, str]] = []
    for entry in entries:
        note = get_note(entry.ref, repo_root)
        result.append((entry, render_note_line(note, colour=colour)))
    return result


def format_entry_with_note(
    entry: StashEntry,
    repo_root: Path | None = None,
    *,
    colour: bool = True,
) -> str:
    """Return a multi-line string: the entry label followed by its note (if any)."""
    lines = [f"{entry.ref}  {entry.message}"]
    note = get_note(entry.ref, repo_root)
    if note:
        lines.append(render_note_line(note, colour=colour))
    return "\n".join(lines)
