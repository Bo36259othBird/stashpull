"""Tests for stashpull.selector.StashSelector."""

from __future__ import annotations

import pytest

from stashpull.selector import StashSelector
from stashpull.stash import StashEntry


def _make_entry(index: int) -> StashEntry:
    return StashEntry(
        index=index,
        ref=f"stash@{{{index}}}",
        branch="main",
        message=f"stash entry {index}",
    )


@pytest.fixture()
def selector() -> StashSelector:
    entries = [_make_entry(i) for i in range(4)]
    return StashSelector(entries)


def test_initial_state_empty(selector: StashSelector):
    assert selector.selection_count == 0
    assert selector.selected_entries == []


def test_select_single(selector: StashSelector):
    selector.select(2)
    assert selector.is_selected(2)
    assert selector.selection_count == 1


def test_deselect(selector: StashSelector):
    selector.select(1)
    selector.deselect(1)
    assert not selector.is_selected(1)


def test_deselect_nonexistent_is_noop(selector: StashSelector):
    selector.deselect(99)  # should not raise


def test_toggle_selects_then_deselects(selector: StashSelector):
    assert selector.toggle(0) is True
    assert selector.is_selected(0)
    assert selector.toggle(0) is False
    assert not selector.is_selected(0)


def test_select_all(selector: StashSelector):
    selector.select_all()
    assert selector.selection_count == 4
    assert all(selector.is_selected(i) for i in range(4))


def test_clear(selector: StashSelector):
    selector.select_all()
    selector.clear()
    assert selector.selection_count == 0


def test_selected_entries_sorted(selector: StashSelector):
    selector.select(3)
    selector.select(1)
    indices = [e.index for e in selector.selected_entries]
    assert indices == sorted(indices)


def test_summary(selector: StashSelector):
    selector.select(0)
    selector.select(2)
    s = selector.summary()
    assert s == {"total": 4, "selected": 2}


def test_select_invalid_index_raises(selector: StashSelector):
    with pytest.raises(ValueError, match="No stash entry"):
        selector.select(99)


def test_toggle_invalid_index_raises(selector: StashSelector):
    with pytest.raises(ValueError):
        selector.toggle(50)
