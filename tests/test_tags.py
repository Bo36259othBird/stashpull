"""Tests for stashpull.tags."""

import json
import pytest
from pathlib import Path

from stashpull.tags import (
    load_tags,
    save_tags,
    add_tag,
    remove_tag,
    get_tags,
    list_tagged,
    all_known_tags,
)


@pytest.fixture()
def tag_file(tmp_path: Path) -> Path:
    return tmp_path / "tags.json"


def test_load_tags_missing_file_returns_empty(tag_file: Path) -> None:
    assert load_tags(tag_file) == {}


def test_load_tags_corrupt_file_returns_empty(tag_file: Path) -> None:
    tag_file.write_text("not json", encoding="utf-8")
    assert load_tags(tag_file) == {}


def test_load_tags_wrong_type_returns_empty(tag_file: Path) -> None:
    tag_file.write_text(json.dumps(["a", "b"]), encoding="utf-8")
    assert load_tags(tag_file) == {}


def test_save_and_load_roundtrip(tag_file: Path) -> None:
    mapping = {"stash@{0}": ["wip", "feature-x"], "stash@{1}": ["bugfix"]}
    save_tags(mapping, tag_file)
    assert load_tags(tag_file) == mapping


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "tags.json"
    save_tags({"stash@{0}": ["test"]}, nested)
    assert nested.exists()


def test_add_tag_new_ref(tag_file: Path) -> None:
    result = add_tag("stash@{0}", "wip", tag_file)
    assert result == {"stash@{0}": ["wip"]}


def test_add_tag_existing_ref(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    result = add_tag("stash@{0}", "feature", tag_file)
    assert result["stash@{0}"] == ["wip", "feature"]


def test_add_tag_duplicate_ignored(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    result = add_tag("stash@{0}", "wip", tag_file)
    assert result["stash@{0}"].count("wip") == 1


def test_remove_tag_existing(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    add_tag("stash@{0}", "done", tag_file)
    result = remove_tag("stash@{0}", "wip", tag_file)
    assert result["stash@{0}"] == ["done"]


def test_remove_tag_last_tag_removes_ref(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    result = remove_tag("stash@{0}", "wip", tag_file)
    assert "stash@{0}" not in result


def test_remove_tag_nonexistent_is_noop(tag_file: Path) -> None:
    result = remove_tag("stash@{0}", "ghost", tag_file)
    assert result == {}


def test_get_tags_returns_list(tag_file: Path) -> None:
    add_tag("stash@{0}", "alpha", tag_file)
    assert get_tags("stash@{0}", tag_file) == ["alpha"]


def test_get_tags_unknown_ref_returns_empty(tag_file: Path) -> None:
    assert get_tags("stash@{99}", tag_file) == []


def test_list_tagged(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    add_tag("stash@{1}", "wip", tag_file)
    add_tag("stash@{2}", "done", tag_file)
    assert sorted(list_tagged("wip", tag_file)) == ["stash@{0}", "stash@{1}"]


def test_all_known_tags(tag_file: Path) -> None:
    add_tag("stash@{0}", "wip", tag_file)
    add_tag("stash@{1}", "done", tag_file)
    add_tag("stash@{2}", "wip", tag_file)
    assert all_known_tags(tag_file) == ["done", "wip"]
