"""Tests for stashpull.stash module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from stashpull.stash import (
    StashEntry,
    apply_stash,
    get_stash_diff,
    list_stashes,
    pop_stash,
)

STASH_LIST_OUTPUT = (
    "stash@{0}|WIP on main: fix typo|On main: fix typo\n"
    "stash@{1}|WIP on feature/foo: add bar|On feature/foo: add bar\n"
    "stash@{2}|index on main: 1234abc initial commit|\n"
)

DIFF_OUTPUT = "diff --git a/foo.py b/foo.py\n--- a/foo.py\n+++ b/foo.py\n"


def _make_run_result(stdout: str, returncode: int = 0) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.stderr = ""
    result.returncode = returncode
    return result


@patch("stashpull.stash.subprocess.run")
def test_list_stashes_returns_entries(mock_run):
    mock_run.return_value = _make_run_result(STASH_LIST_OUTPUT)
    entries = list_stashes()
    assert len(entries) == 3
    assert entries[0].index == 0
    assert entries[0].ref == "stash@{0}"
    assert entries[0].branch == "main"
    assert entries[1].index == 1
    assert entries[1].branch == "feature/foo"
    assert entries[2].branch == ""  # no branch decoration


@patch("stashpull.stash.subprocess.run")
def test_list_stashes_empty_repo(mock_run):
    mock_run.return_value = _make_run_result("")
    assert list_stashes() == []


@patch("stashpull.stash.subprocess.run")
def test_list_stashes_command_failure(mock_run):
    mock_run.return_value = _make_run_result("", returncode=128)
    with pytest.raises(RuntimeError, match="failed"):
        list_stashes()


@patch("stashpull.stash.subprocess.run")
def test_get_stash_diff(mock_run):
    mock_run.return_value = _make_run_result(DIFF_OUTPUT)
    diff = get_stash_diff("stash@{0}")
    assert "diff --git" in diff
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "stash@{0}" in cmd


@patch("stashpull.stash.subprocess.run")
def test_apply_stash(mock_run):
    mock_run.return_value = _make_run_result("Applied stash@{0}")
    out = apply_stash("stash@{0}")
    assert "Applied" in out


@patch("stashpull.stash.subprocess.run")
def test_pop_stash(mock_run):
    mock_run.return_value = _make_run_result("Dropped stash@{0}")
    out = pop_stash("stash@{0}")
    assert "Dropped" in out


def test_stash_entry_short_label():
    entry = StashEntry(index=3, ref="stash@{3}", message="my work", branch="dev")
    assert entry.short_label == "stash@{3}: my work"
