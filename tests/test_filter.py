"""Tests for stashpull.filter module."""

from __future__ import annotations

import pytest

from stashpull.filter import (
    filter_by_branch,
    filter_by_index_range,
    filter_by_message,
    search,
    sort_entries,
)
from stashpull.stash import StashEntry


def _make_entry(index: int, branch: str, message: str) -> StashEntry:
    return StashEntry(index=index, ref=f"stash@{{{index}}}", branch=branch, message=message)


FIXTURE_ENTRIES = [
    _make_entry(0, "main", "WIP: refactor auth"),
    _make_entry(1, "feature/login", "add login form"),
    _make_entry(2, "main", "hotfix typo in README"),
    _make_entry(3, "feature/signup", "WIP: signup flow"),
]


def test_filter_by_message_case_insensitive():
    result = filter_by_message(FIXTURE_ENTRIES, "wip")
    assert len(result) == 2
    assert all("WIP" in e.message for e in result)


def test_filter_by_message_empty_query_returns_all():
    result = filter_by_message(FIXTURE_ENTRIES, "")
    assert result == FIXTURE_ENTRIES


def test_filter_by_message_no_match():
    result = filter_by_message(FIXTURE_ENTRIES, "nonexistent")
    assert result == []


def test_filter_by_branch_exact():
    result = filter_by_branch(FIXTURE_ENTRIES, "main")
    assert len(result) == 2
    assert all(e.branch == "main" for e in result)


def test_filter_by_branch_partial():
    result = filter_by_branch(FIXTURE_ENTRIES, "feature")
    assert len(result) == 2


def test_filter_by_branch_empty_returns_all():
    result = filter_by_branch(FIXTURE_ENTRIES, "")
    assert result == FIXTURE_ENTRIES


def test_filter_by_index_range_single():
    result = filter_by_index_range(FIXTURE_ENTRIES, 1)
    assert len(result) == 1
    assert result[0].index == 1


def test_filter_by_index_range_span():
    result = filter_by_index_range(FIXTURE_ENTRIES, 1, 3)
    assert [e.index for e in result] == [1, 2, 3]


def test_search_matches_branch_and_message():
    result = search(FIXTURE_ENTRIES, "login")
    assert len(result) == 1
    assert result[0].branch == "feature/login"


def test_sort_entries_by_branch():
    result = sort_entries(FIXTURE_ENTRIES, key="branch")
    branches = [e.branch for e in result]
    assert branches == sorted(branches)


def test_sort_entries_invalid_key():
    with pytest.raises(ValueError, match="sort key"):
        sort_entries(FIXTURE_ENTRIES, key="timestamp")


def test_sort_entries_reverse():
    result = sort_entries(FIXTURE_ENTRIES, key="index", reverse=True)
    assert result[0].index == 3
