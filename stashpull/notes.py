"""Per-stash user notes stored in a JSON file alongside other stashpull data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def _notes_path(repo_root: Path | None = None) -> Path:
    base = repo_root or Path.cwd()
    return base / ".git" / "stashpull_notes.json"


def load_notes(repo_root: Path | None = None) -> Dict[str, str]:
    """Return a mapping of stash ref -> note text."""
    path = _notes_path(repo_root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}


def save_notes(notes: Dict[str, str], repo_root: Path | None = None) -> None:
    """Persist *notes* to disk, creating the file if necessary."""
    path = _notes_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


def set_note(ref: str, text: str, repo_root: Path | None = None) -> None:
    """Add or update the note for *ref*."""
    notes = load_notes(repo_root)
    notes[ref] = text
    save_notes(notes, repo_root)


def get_note(ref: str, repo_root: Path | None = None) -> str:
    """Return the note for *ref*, or an empty string if none exists."""
    return load_notes(repo_root).get(ref, "")


def delete_note(ref: str, repo_root: Path | None = None) -> bool:
    """Remove the note for *ref*. Returns True if a note was removed."""
    notes = load_notes(repo_root)
    if ref not in notes:
        return False
    del notes[ref]
    save_notes(notes, repo_root)
    return True


def list_noted_refs(repo_root: Path | None = None) -> list[str]:
    """Return sorted list of stash refs that have notes."""
    return sorted(load_notes(repo_root).keys())
