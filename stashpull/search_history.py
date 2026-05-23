"""Persist and recall recent search queries used in the interactive UI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

_MAX_ENTRIES = 50
_HISTORY_FILENAME = "search_history.json"


def _history_path() -> Path:
    base = os.environ.get("STASHPULL_CONFIG_DIR") or os.path.join(
        os.path.expanduser("~"), ".config", "stashpull"
    )
    return Path(base) / _HISTORY_FILENAME


def load_search_history() -> List[str]:
    """Return the list of recent search queries, newest first."""
    path = _history_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(q) for q in data if isinstance(q, str)]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_search_history(queries: List[str]) -> None:
    """Persist *queries* to disk, capping at _MAX_ENTRIES."""
    path = _history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    trimmed = queries[:_MAX_ENTRIES]
    path.write_text(json.dumps(trimmed, indent=2), encoding="utf-8")


def record_query(query: str) -> List[str]:
    """Add *query* to the front of the history, deduplicate, and save.

    Returns the updated history list.
    """
    query = query.strip()
    if not query:
        return load_search_history()
    history = load_search_history()
    # Remove existing occurrence so the new one floats to the top.
    history = [q for q in history if q != query]
    history.insert(0, query)
    save_search_history(history)
    return history


def clear_search_history() -> None:
    """Delete all persisted search queries."""
    path = _history_path()
    if path.exists():
        path.unlink()
