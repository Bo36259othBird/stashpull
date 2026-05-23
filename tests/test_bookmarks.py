"""Tests for stashpull.bookmarks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stashpull.bookmarks import (
    add_bookmark,
    filter_bookmarked,
    is_bookmarked,
    load_bookmarks,
    remove_bookmark,
    save_bookmarks,
)
from stashpull.stash import StashEntry


def _make_entry(ref: str, message: str = "wip", branch: str = "main") -> StashEntry:
    return StashEntry(ref=ref, message=message, branch=branch, timestamp="2024-01-01")


@pytest.fixture()
def bm_path(tmp_path: Path) -> Path:
    return tmp_path / "bookmarks.json"


def test_load_bookmarks_missing_file_returns_empty(bm_path: Path) -> None:
    assert load_bookmarks(bm_path) == []


def test_load_bookmarks_corrupt_file_returns_empty(bm_path: Path) -> None:
    bm_path.write_text("not json", encoding="utf-8")
    assert load_bookmarks(bm_path) == []


def test_save_and_load_roundtrip(bm_path: Path) -> None:
    refs = ["stash@{0}", "stash@{2}"]
    save_bookmarks(refs, bm_path)
    assert load_bookmarks(bm_path) == refs


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "bookmarks.json"
    save_bookmarks(["stash@{0}"], nested)
    assert nested.exists()


def test_add_bookmark_new_entry(bm_path: Path) -> None:
    entry = _make_entry("stash@{0}")
    refs = add_bookmark(entry, bm_path)
    assert "stash@{0}" in refs


def test_add_bookmark_idempotent(bm_path: Path) -> None:
    entry = _make_entry("stash@{0}")
    add_bookmark(entry, bm_path)
    refs = add_bookmark(entry, bm_path)
    assert refs.count("stash@{0}") == 1


def test_remove_bookmark(bm_path: Path) -> None:
    entry = _make_entry("stash@{0}")
    add_bookmark(entry, bm_path)
    refs = remove_bookmark(entry, bm_path)
    assert "stash@{0}" not in refs


def test_remove_bookmark_not_present_is_safe(bm_path: Path) -> None:
    entry = _make_entry("stash@{99}")
    refs = remove_bookmark(entry, bm_path)  # should not raise
    assert "stash@{99}" not in refs


def test_is_bookmarked_true(bm_path: Path) -> None:
    entry = _make_entry("stash@{1}")
    add_bookmark(entry, bm_path)
    assert is_bookmarked(entry, bm_path) is True


def test_is_bookmarked_false(bm_path: Path) -> None:
    entry = _make_entry("stash@{5}")
    assert is_bookmarked(entry, bm_path) is False


def test_filter_bookmarked(bm_path: Path) -> None:
    e0 = _make_entry("stash@{0}")
    e1 = _make_entry("stash@{1}")
    e2 = _make_entry("stash@{2}")
    add_bookmark(e0, bm_path)
    add_bookmark(e2, bm_path)
    result = filter_bookmarked([e0, e1, e2], bm_path)
    assert result == [e0, e2]
