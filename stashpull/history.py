"""Track and persist restore operation history for stashpull."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


_DEFAULT_HISTORY_FILE = Path.home() / ".local" / "share" / "stashpull" / "history.json"


@dataclass
class HistoryEntry:
    stash_ref: str
    message: str
    branch: str
    restored_at: str
    mode: str
    success: bool
    files_affected: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)


def _history_path() -> Path:
    env_override = os.environ.get("STASHPULL_HISTORY_FILE")
    if env_override:
        return Path(env_override)
    return _DEFAULT_HISTORY_FILE


def load_history(path: Optional[Path] = None) -> List[HistoryEntry]:
    """Load restore history from disk. Returns empty list if file missing."""
    target = path or _history_path()
    if not target.exists():
        return []
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
        return [HistoryEntry.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def save_history(entries: List[HistoryEntry], path: Optional[Path] = None) -> None:
    """Persist restore history to disk, creating parent directories as needed."""
    target = path or _history_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([e.to_dict() for e in entries], indent=2),
        encoding="utf-8",
    )


def record_restore(
    stash_ref: str,
    message: str,
    branch: str,
    mode: str,
    success: bool,
    files_affected: Optional[List[str]] = None,
    path: Optional[Path] = None,
) -> HistoryEntry:
    """Append a restore event to history and return the new entry."""
    entry = HistoryEntry(
        stash_ref=stash_ref,
        message=message,
        branch=branch,
        restored_at=datetime.now(timezone.utc).isoformat(),
        mode=mode,
        success=success,
        files_affected=files_affected or [],
    )
    existing = load_history(path)
    existing.append(entry)
    save_history(existing, path)
    return entry
