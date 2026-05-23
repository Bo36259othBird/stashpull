"""Tests for stashpull.cli_notes."""

from __future__ import annotations

from pathlib import Path

import pytest

from stashpull.cli_notes import run
from stashpull.notes import get_note, set_note


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


def test_set_command_stores_note(repo_root: Path) -> None:
    rc = run(["set", "stash@{0}", "hello world"], repo_root=repo_root)
    assert rc == 0
    assert get_note("stash@{0}", repo_root) == "hello world"


def test_get_command_prints_note(repo_root: Path, capsys: pytest.CaptureFixture) -> None:
    set_note("stash@{0}", "my note", repo_root)
    rc = run(["get", "stash@{0}"], repo_root=repo_root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "my note" in out


def test_get_command_missing_returns_nonzero(
    repo_root: Path, capsys: pytest.CaptureFixture
) -> None:
    rc = run(["get", "stash@{99}"], repo_root=repo_root)
    assert rc == 1
    assert "No note" in capsys.readouterr().err


def test_delete_command_removes_note(repo_root: Path) -> None:
    set_note("stash@{0}", "temp", repo_root)
    rc = run(["delete", "stash@{0}"], repo_root=repo_root)
    assert rc == 0
    assert get_note("stash@{0}", repo_root) == ""


def test_delete_command_missing_returns_nonzero(
    repo_root: Path, capsys: pytest.CaptureFixture
) -> None:
    rc = run(["delete", "stash@{0}"], repo_root=repo_root)
    assert rc == 1


def test_list_command_shows_refs(
    repo_root: Path, capsys: pytest.CaptureFixture
) -> None:
    set_note("stash@{0}", "a", repo_root)
    set_note("stash@{1}", "b", repo_root)
    rc = run(["list"], repo_root=repo_root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "stash@{0}" in out
    assert "stash@{1}" in out


def test_list_command_empty(repo_root: Path, capsys: pytest.CaptureFixture) -> None:
    rc = run(["list"], repo_root=repo_root)
    assert rc == 0
    assert "No notes" in capsys.readouterr().out
