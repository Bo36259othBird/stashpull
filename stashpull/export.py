"""Export stash entries to patch files or clipboard."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from stashpull.stash import StashEntry, get_stash_diff


@dataclass
class ExportResult:
    entry: StashEntry
    path: Optional[Path]
    success: bool
    error: Optional[str] = None


def _sanitise_filename(label: str) -> str:
    """Convert a stash label into a safe filename fragment."""
    safe = label.replace("/", "-").replace(" ", "_")
    safe = "".join(c for c in safe if c.isalnum() or c in "-_.")
    return safe[:64]


def export_entry_to_file(
    entry: StashEntry,
    directory: Path,
    overwrite: bool = False,
) -> ExportResult:
    """Write the diff of *entry* to a .patch file inside *directory*."""
    directory = Path(directory)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return ExportResult(entry=entry, path=None, success=False, error=str(exc))

    fragment = _sanitise_filename(entry.ref)
    filename = directory / f"{fragment}.patch"

    if filename.exists() and not overwrite:
        return ExportResult(
            entry=entry,
            path=filename,
            success=False,
            error=f"File already exists: {filename}",
        )

    diff = get_stash_diff(entry.ref)
    try:
        filename.write_text(diff, encoding="utf-8")
    except OSError as exc:
        return ExportResult(entry=entry, path=filename, success=False, error=str(exc))

    return ExportResult(entry=entry, path=filename, success=True)


def export_entries(
    entries: List[StashEntry],
    directory: Path,
    overwrite: bool = False,
) -> List[ExportResult]:
    """Export multiple stash entries; returns one result per entry."""
    return [export_entry_to_file(e, directory, overwrite=overwrite) for e in entries]


def format_export_summary(results: List[ExportResult]) -> str:
    """Return a human-readable summary of export results."""
    ok = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    lines: List[str] = []
    if ok:
        lines.append(f"Exported {len(ok)} patch file(s):")
        for r in ok:
            lines.append(f"  ✓  {r.path}")
    if failed:
        lines.append(f"Failed {len(failed)} export(s):")
        for r in failed:
            lines.append(f"  ✗  {r.entry.ref}: {r.error}")
    return os.linesep.join(lines)
