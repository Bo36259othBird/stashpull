"""Tests for stashpull.export."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from stashpull.export import (
    ExportResult,
    _sanitise_filename,
    export_entries,
    export_entry_to_file,
    format_export_summary,
)
from stashpull.stash import StashEntry


def _make_entry(ref: str = "stash@{0}", message: str = "WIP", branch: str = "main") -> StashEntry:
    return StashEntry(ref=ref, message=message, branch=branch, timestamp="2024-01-01 12:00:00")


FAKE_DIFF = "diff --git a/foo.py b/foo.py\n+++ b/foo.py\n+print('hello')\n"


# ---------------------------------------------------------------------------
# _sanitise_filename
# ---------------------------------------------------------------------------

def test_sanitise_filename_replaces_slashes():
    assert "/" not in _sanitise_filename("feature/my-branch")


def test_sanitise_filename_replaces_spaces():
    result = _sanitise_filename("stash@{0}")
    assert " " not in result


def test_sanitise_filename_truncates_long_names():
    long_label = "a" * 200
    assert len(_sanitise_filename(long_label)) <= 64


# ---------------------------------------------------------------------------
# export_entry_to_file
# ---------------------------------------------------------------------------

def test_export_creates_patch_file(tmp_path):
    entry = _make_entry()
    with patch("stashpull.export.get_stash_diff", return_value=FAKE_DIFF):
        result = export_entry_to_file(entry, tmp_path)

    assert result.success
    assert result.path is not None
    assert result.path.exists()
    assert result.path.read_text(encoding="utf-8") == FAKE_DIFF


def test_export_does_not_overwrite_by_default(tmp_path):
    entry = _make_entry()
    with patch("stashpull.export.get_stash_diff", return_value=FAKE_DIFF):
        first = export_entry_to_file(entry, tmp_path)
        second = export_entry_to_file(entry, tmp_path, overwrite=False)

    assert first.success
    assert not second.success
    assert "already exists" in (second.error or "")


def test_export_overwrites_when_flag_set(tmp_path):
    entry = _make_entry()
    with patch("stashpull.export.get_stash_diff", return_value=FAKE_DIFF):
        export_entry_to_file(entry, tmp_path)
        result = export_entry_to_file(entry, tmp_path, overwrite=True)

    assert result.success


def test_export_creates_directory_if_missing(tmp_path):
    entry = _make_entry()
    target = tmp_path / "nested" / "dir"
    with patch("stashpull.export.get_stash_diff", return_value=FAKE_DIFF):
        result = export_entry_to_file(entry, target)

    assert result.success
    assert target.is_dir()


# ---------------------------------------------------------------------------
# export_entries
# ---------------------------------------------------------------------------

def test_export_entries_returns_one_result_per_entry(tmp_path):
    entries = [_make_entry(f"stash@{{{i}}}", f"msg {i}") for i in range(3)]
    with patch("stashpull.export.get_stash_diff", return_value=FAKE_DIFF):
        results = export_entries(entries, tmp_path, overwrite=True)

    assert len(results) == 3
    assert all(r.success for r in results)


# ---------------------------------------------------------------------------
# format_export_summary
# ---------------------------------------------------------------------------

def test_format_summary_shows_ok_and_failed():
    entry = _make_entry()
    ok_result = ExportResult(entry=entry, path=Path("/tmp/x.patch"), success=True)
    fail_result = ExportResult(entry=entry, path=None, success=False, error="oops")
    summary = format_export_summary([ok_result, fail_result])
    assert "Exported 1" in summary
    assert "Failed 1" in summary
    assert "oops" in summary


def test_format_summary_empty_list():
    assert format_export_summary([]) == ""
