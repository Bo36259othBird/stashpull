"""Tests for stashpull.notes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stashpull.notes import (
    delete_note,
    get_note,
    list_noted_refs,
    load_notes,
    save_notes,
    set_note,
)


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    return tmp_path


def test_load_notes_missing_file_returns_empty(repo_root: Path) -> None:
    assert load_notes(repo_root) == {}


def test_load_notes_corrupt_file_returns_empty(repo_root: Path) -> None:
    notes_file = repo_root / ".git" / "stashpull_notes.json"
    notes_file.write_text("not json", encoding="utf-8")
    assert load_notes(repo_root) == {}


def test_load_notes_wrong_type_returns_empty(repo_root: Path) -> None:
    notes_file = repo_root / ".git" / "stashpull_notes.json"
    notes_file.write_text(json.dumps(["a", "b"]), encoding="utf-8")
    assert load_notes(repo_root) == {}


def test_save_and_load_roundtrip(repo_root: Path) -> None:
    data = {"stash@{0}": "my note", "stash@{1}": "another"}
    save_notes(data, repo_root)
    assert load_notes(repo_root) == data


def test_set_note_creates_entry(repo_root: Path) -> None:
    set_note("stash@{0}", "important fix", repo_root)
    assert get_note("stash@{0}", repo_root) == "important fix"


def test_set_note_updates_existing(repo_root: Path) -> None:
    set_note("stash@{0}", "first", repo_root)
    set_note("stash@{0}", "second", repo_root)
    assert get_note("stash@{0}", repo_root) == "second"


def test_get_note_missing_returns_empty(repo_root: Path) -> None:
    assert get_note("stash@{99}", repo_root) == ""


def test_delete_note_removes_entry(repo_root: Path) -> None:
    set_note("stash@{0}", "to remove", repo_root)
    result = delete_note("stash@{0}", repo_root)
    assert result is True
    assert get_note("stash@{0}", repo_root) == ""


def test_delete_note_missing_returns_false(repo_root: Path) -> None:
    assert delete_note("stash@{0}", repo_root) is False


def test_list_noted_refs_sorted(repo_root: Path) -> None:
    set_note("stash@{2}", "c", repo_root)
    set_note("stash@{0}", "a", repo_root)
    set_note("stash@{1}", "b", repo_root)
    assert list_noted_refs(repo_root) == ["stash@{0}", "stash@{1}", "stash@{2}"]


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    """notes_path parent (.git) may not exist when using a custom root."""
    root = tmp_path / "newrepo"
    root.mkdir()
    # .git does NOT exist yet — save_notes must create it
    save_notes({"stash@{0}": "hi"}, root)
    assert (root / ".git" / "stashpull_notes.json").exists()
