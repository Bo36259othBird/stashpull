"""Tests for stashpull.config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stashpull.config import (
    _DEFAULT_CONFIG,
    get,
    load_config,
    save_config,
)


def test_load_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "nonexistent.json")
    assert cfg == _DEFAULT_CONFIG


def test_load_config_corrupt_file_returns_defaults(tmp_path: Path) -> None:
    bad = tmp_path / "config.json"
    bad.write_text("not json at all", encoding="utf-8")
    cfg = load_config(bad)
    assert cfg == _DEFAULT_CONFIG


def test_load_config_merges_partial_overrides(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"colour": False, "max_history_entries": 10}), encoding="utf-8")
    cfg = load_config(cfg_file)
    assert cfg["colour"] is False
    assert cfg["max_history_entries"] == 10
    # Unset keys still carry defaults
    assert cfg["default_restore_mode"] == _DEFAULT_CONFIG["default_restore_mode"]


def test_load_config_ignores_unknown_keys(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"unknown_key": "surprise"}), encoding="utf-8")
    cfg = load_config(cfg_file)
    assert "unknown_key" not in cfg
    assert cfg == _DEFAULT_CONFIG


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    cfg_file = tmp_path / "sub" / "config.json"
    overrides = dict(_DEFAULT_CONFIG)
    overrides["colour"] = False
    overrides["preview_context_lines"] = 5
    save_config(overrides, cfg_file)
    assert cfg_file.exists()
    loaded = load_config(cfg_file)
    assert loaded["colour"] is False
    assert loaded["preview_context_lines"] == 5


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "c" / "config.json"
    save_config(_DEFAULT_CONFIG, nested)
    assert nested.exists()


def test_get_returns_single_value(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"date_format": "%d/%m/%Y"}), encoding="utf-8")
    assert get("date_format", cfg_file) == "%d/%m/%Y"


def test_get_falls_back_to_default_for_missing_key(tmp_path: Path) -> None:
    assert get("max_history_entries", tmp_path / "no.json") == _DEFAULT_CONFIG["max_history_entries"]
