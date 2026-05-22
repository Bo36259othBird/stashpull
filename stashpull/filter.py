"""Filtering and searching utilities for stash entries."""

from __future__ import annotations

import re
from typing import List, Optional

from stashpull.stash import StashEntry


def filter_by_message(entries: List[StashEntry], query: str) -> List[StashEntry]:
    """Return entries whose message contains *query* (case-insensitive)."""
    if not query:
        return list(entries)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [e for e in entries if pattern.search(e.message)]


def filter_by_branch(entries: List[StashEntry], branch: str) -> List[StashEntry]:
    """Return entries that were created on *branch*."""
    if not branch:
        return list(entries)
    pattern = re.compile(re.escape(branch), re.IGNORECASE)
    return [e for e in entries if pattern.search(e.branch)]


def filter_by_index_range(
    entries: List[StashEntry],
    start: int,
    end: Optional[int] = None,
) -> List[StashEntry]:
    """Return entries whose numeric index falls within [start, end]."""
    if end is None:
        end = start
    return [e for e in entries if start <= e.index <= end]


def search(entries: List[StashEntry], query: str) -> List[StashEntry]:
    """Broad search across message and branch fields."""
    if not query:
        return list(entries)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [
        e
        for e in entries
        if pattern.search(e.message) or pattern.search(e.branch)
    ]


def sort_entries(
    entries: List[StashEntry], key: str = "index", reverse: bool = False
) -> List[StashEntry]:
    """Sort entries by *key* ('index', 'branch', or 'message')."""
    valid_keys = {"index", "branch", "message"}
    if key not in valid_keys:
        raise ValueError(f"sort key must be one of {valid_keys}, got {key!r}")
    return sorted(entries, key=lambda e: getattr(e, key), reverse=reverse)
