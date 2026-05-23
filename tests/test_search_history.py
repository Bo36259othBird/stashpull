"""Tests for stashpull.search_history."""

from __future__ import annotations

import json
import os
import pytest

from stashpull.search_history import (
    load_search_history,
    save_search_history,
    record_query,
    clear_search_history,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPULL_CONFIG_DIR", str(tmp_path))
    yield tmp_path


def test_load_history_missing_file_returns_empty():
    assert load_search_history() == []


def test_load_history_corrupt_file_returns_empty(isolated_config):
    bad = isolated_config / "search_history.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert load_search_history() == []


def test_save_and_load_roundtrip():
    queries = ["fix bug", "feature branch", "wip"]
    save_search_history(queries)
    assert load_search_history() == queries


def test_save_trims_to_max_entries():
    queries = [f"query-{i}" for i in range(100)]
    save_search_history(queries)
    loaded = load_search_history()
    assert len(loaded) == 50
    assert loaded[0] == "query-0"


def test_record_query_adds_to_front():
    save_search_history(["old query"])
    result = record_query("new query")
    assert result[0] == "new query"
    assert result[1] == "old query"


def test_record_query_deduplicates():
    save_search_history(["alpha", "beta", "gamma"])
    result = record_query("beta")
    assert result.count("beta") == 1
    assert result[0] == "beta"


def test_record_query_ignores_blank():
    save_search_history(["existing"])
    result = record_query("   ")
    assert result == ["existing"]


def test_record_query_persists(isolated_config):
    record_query("persisted")
    loaded = load_search_history()
    assert loaded[0] == "persisted"


def test_clear_search_history_removes_file(isolated_config):
    save_search_history(["something"])
    clear_search_history()
    assert load_search_history() == []


def test_clear_search_history_no_error_if_missing():
    # Should not raise even when no file exists.
    clear_search_history()
