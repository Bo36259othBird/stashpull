"""Tag management for stash entries — assign, remove, and query user-defined tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _tags_path() -> Path:
    """Return the path to the tags store (~/.local/share/stashpull/tags.json)."""
    return Path.home() / ".local" / "share" / "stashpull" / "tags.json"


def load_tags(path: Path | None = None) -> Dict[str, List[str]]:
    """Load the tag mapping {stash_ref: [tag, ...]} from disk.

    Returns an empty dict if the file is missing or corrupt.
    """
    target = path or _tags_path()
    try:
        raw = target.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return {k: list(v) for k, v in data.items() if isinstance(v, list)}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_tags(mapping: Dict[str, List[str]], path: Path | None = None) -> None:
    """Persist the tag mapping to disk, creating parent directories as needed."""
    target = path or _tags_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(mapping, indent=2), encoding="utf-8")


def add_tag(ref: str, tag: str, path: Path | None = None) -> Dict[str, List[str]]:
    """Add *tag* to *ref*.  Duplicate tags are silently ignored."""
    mapping = load_tags(path)
    tags = mapping.setdefault(ref, [])
    if tag not in tags:
        tags.append(tag)
    save_tags(mapping, path)
    return mapping


def remove_tag(ref: str, tag: str, path: Path | None = None) -> Dict[str, List[str]]:
    """Remove *tag* from *ref*.  No-op if the tag or ref does not exist."""
    mapping = load_tags(path)
    if ref in mapping:
        mapping[ref] = [t for t in mapping[ref] if t != tag]
        if not mapping[ref]:
            del mapping[ref]
    save_tags(mapping, path)
    return mapping


def get_tags(ref: str, path: Path | None = None) -> List[str]:
    """Return the list of tags for *ref*, or an empty list."""
    return load_tags(path).get(ref, [])


def list_tagged(tag: str, path: Path | None = None) -> List[str]:
    """Return all stash refs that carry *tag*."""
    return [ref for ref, tags in load_tags(path).items() if tag in tags]


def all_known_tags(path: Path | None = None) -> List[str]:
    """Return a sorted, deduplicated list of every tag in use."""
    seen: set[str] = set()
    for tags in load_tags(path).values():
        seen.update(tags)
    return sorted(seen)
