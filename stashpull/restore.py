"""Restore (apply/pop) selected stash entries via git."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

from stashpull.stash import StashEntry, _run


class RestoreMode(Enum):
    APPLY = auto()  # keep the stash entry after restoring
    POP = auto()    # drop the stash entry after restoring


@dataclass
class RestoreResult:
    entry: StashEntry
    success: bool
    output: str = ""
    error: str = ""


@dataclass
class RestoreSummary:
    results: List[RestoreResult] = field(default_factory=list)

    @property
    def succeeded(self) -> List[RestoreResult]:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> List[RestoreResult]:
        return [r for r in self.results if not r.success]

    @property
    def all_succeeded(self) -> bool:
        return bool(self.results) and all(r.success for r in self.results)


def restore_entry(
    entry: StashEntry,
    mode: RestoreMode = RestoreMode.APPLY,
    index: bool = False,
) -> RestoreResult:
    """Restore a single stash entry.

    Parameters
    ----------
    entry:
        The stash entry to restore.
    mode:
        APPLY keeps the stash; POP drops it afterwards.
    index:
        If True, pass ``--index`` to also restore the staging-area state.
    """
    verb = "pop" if mode is RestoreMode.POP else "apply"
    cmd = ["git", "stash", verb]
    if index:
        cmd.append("--index")
    cmd.append(entry.ref)

    proc = _run(cmd)
    return RestoreResult(
        entry=entry,
        success=proc.returncode == 0,
        output=proc.stdout.strip(),
        error=proc.stderr.strip(),
    )


def restore_entries(
    entries: List[StashEntry],
    mode: RestoreMode = RestoreMode.APPLY,
    index: bool = False,
    stop_on_failure: bool = True,
) -> RestoreSummary:
    """Restore multiple stash entries in descending index order.

    Descending order avoids ref-number shifts that occur when popping.
    """
    summary = RestoreSummary()
    for entry in sorted(entries, key=lambda e: e.index, reverse=True):
        result = restore_entry(entry, mode=mode, index=index)
        summary.results.append(result)
        if not result.success and stop_on_failure:
            break
    return summary
