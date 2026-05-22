"""Multi-select logic for choosing stash entries to restore."""

from __future__ import annotations

from typing import Dict, List, Set

from stashpull.stash import StashEntry


class StashSelector:
    """Tracks which stash entries the user has selected."""

    def __init__(self, entries: List[StashEntry]) -> None:
        self._entries: List[StashEntry] = list(entries)
        self._selected: Set[int] = set()

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------

    def select(self, index: int) -> None:
        """Mark entry at *index* as selected."""
        self._validate(index)
        self._selected.add(index)

    def deselect(self, index: int) -> None:
        """Remove *index* from the selection."""
        self._selected.discard(index)

    def toggle(self, index: int) -> bool:
        """Toggle selection state; return True if now selected."""
        self._validate(index)
        if index in self._selected:
            self._selected.discard(index)
            return False
        self._selected.add(index)
        return True

    def select_all(self) -> None:
        """Select every entry."""
        self._selected = {e.index for e in self._entries}

    def clear(self) -> None:
        """Deselect all entries."""
        self._selected.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_selected(self, index: int) -> bool:
        return index in self._selected

    @property
    def selected_entries(self) -> List[StashEntry]:
        """Return selected entries sorted by index (ascending)."""
        return sorted(
            (e for e in self._entries if e.index in self._selected),
            key=lambda e: e.index,
        )

    @property
    def selection_count(self) -> int:
        return len(self._selected)

    def summary(self) -> Dict[str, int]:
        return {"total": len(self._entries), "selected": self.selection_count}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate(self, index: int) -> None:
        valid = {e.index for e in self._entries}
        if index not in valid:
            raise ValueError(f"No stash entry with index {index}")
