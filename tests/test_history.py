"""Tests for stashpull.history module."""

import json
from pathlib import Path

import pytest

from stashpull.history import (
    HistoryEntry,
    load_history,
    record_restore,
    save_history,
)


def _make_entry(**kwargs) -> HistoryEntry:
    defaults = dict(
        stash_ref="stash@{0}",
        message="WIP on main: abc1234 initial",
        branch="main",
        restored_at="2024-01-15T10:00:00+00:00",
        mode="apply",
        success=True,
        files_affected=["README.md"],
    )
    defaults.update(kwargs)
    return HistoryEntry(**defaults)


def test_load_history_missing_file(tmp_path):
    result = load_history(tmp_path / "no_such_file.json")
    assert result == []


def test_load_history_corrupt_file(tmp_path):
    p = tmp_path / "history.json"
    p.write_text("not valid json", encoding="utf-8")
    result = load_history(p)
    assert result == []


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "history.json"
    entries = [_make_entry(), _make_entry(stash_ref="stash@{1}", success=False)]
    save_history(entries, p)
    loaded = load_history(p)
    assert len(loaded) == 2
    assert loaded[0].stash_ref == "stash@{0}"
    assert loaded[1].success is False


def test_save_creates_parent_directories(tmp_path):
    p = tmp_path / "nested" / "dir" / "history.json"
    save_history([_make_entry()], p)
    assert p.exists()


def test_history_entry_to_dict_roundtrip():
    entry = _make_entry()
    d = entry.to_dict()
    restored = HistoryEntry.from_dict(d)
    assert restored == entry


def test_record_restore_appends_entry(tmp_path):
    p = tmp_path / "history.json"
    first = record_restore(
        stash_ref="stash@{0}",
        message="first",
        branch="main",
        mode="apply",
        success=True,
        path=p,
    )
    second = record_restore(
        stash_ref="stash@{1}",
        message="second",
        branch="dev",
        mode="pop",
        success=False,
        files_affected=["a.py", "b.py"],
        path=p,
    )
    history = load_history(p)
    assert len(history) == 2
    assert history[0].message == "first"
    assert history[1].files_affected == ["a.py", "b.py"]


def test_record_restore_returns_entry(tmp_path):
    p = tmp_path / "history.json"
    entry = record_restore(
        stash_ref="stash@{0}",
        message="msg",
        branch="feat",
        mode="apply",
        success=True,
        path=p,
    )
    assert isinstance(entry, HistoryEntry)
    assert entry.stash_ref == "stash@{0}"
    assert entry.restored_at  # non-empty timestamp


def test_load_history_ignores_missing_keys(tmp_path):
    p = tmp_path / "history.json"
    p.write_text(json.dumps([{"stash_ref": "stash@{0}"}]), encoding="utf-8")
    result = load_history(p)
    assert result == []
