"""Persistent bookmarking of stash entries by stash ref and message."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashpull.stash import StashEntry

_BOOKMARKS_FILENAME = "bookmarks.json"


def _bookmarks_path() -> Path:
    base = Path.home() / ".local" / "share" / "stashpull"
    return base / _BOOKMARKS_FILENAME


def load_bookmarks(path: Path | None = None) -> List[str]:
    """Return list of bookmarked stash refs (e.g. 'stash@{0}')."""
    target = path or _bookmarks_path()
    if not target.exists():
        return []
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(r) for r in data]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_bookmarks(refs: List[str], path: Path | None = None) -> None:
    """Persist the list of bookmarked stash refs to disk."""
    target = path or _bookmarks_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(refs, indent=2), encoding="utf-8")


def add_bookmark(entry: StashEntry, path: Path | None = None) -> List[str]:
    """Bookmark *entry*; return updated list of refs."""
    refs = load_bookmarks(path)
    if entry.ref not in refs:
        refs.append(entry.ref)
        save_bookmarks(refs, path)
    return refs


def remove_bookmark(entry: StashEntry, path: Path | None = None) -> List[str]:
    """Remove bookmark for *entry*; return updated list of refs."""
    refs = load_bookmarks(path)
    refs = [r for r in refs if r != entry.ref]
    save_bookmarks(refs, path)
    return refs


def is_bookmarked(entry: StashEntry, path: Path | None = None) -> bool:
    """Return True if *entry* is currently bookmarked."""
    return entry.ref in load_bookmarks(path)


def filter_bookmarked(
    entries: List[StashEntry], path: Path | None = None
) -> List[StashEntry]:
    """Return only entries whose ref appears in the bookmarks list."""
    refs = set(load_bookmarks(path))
    return [e for e in entries if e.ref in refs]
