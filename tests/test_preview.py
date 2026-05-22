"""Tests for stashpull.preview."""

import pytest
from stashpull.preview import (
    classify_line,
    parse_diff,
    summarise_diff,
    format_summary_line,
    DiffLine,
)

SAMPLE_DIFF = """\
diff --git a/foo.py b/foo.py
index abc123..def456 100644
--- a/foo.py
+++ b/foo.py
@@ -1,4 +1,5 @@
 context line
-removed line
+added line one
+added line two
 another context
"""


def test_classify_added():
    assert classify_line("+new stuff") == "added"


def test_classify_removed():
    assert classify_line("-old stuff") == "removed"


def test_classify_header():
    assert classify_line("@@ -1,3 +1,4 @@ def foo():") == "header"


def test_classify_meta_diff():
    assert classify_line("diff --git a/x b/x") == "meta"


def test_classify_meta_index():
    assert classify_line("index abc..def 100644") == "meta"


def test_classify_context():
    assert classify_line(" ordinary line") == "context"


def test_parse_diff_returns_diff_lines():
    result = parse_diff(SAMPLE_DIFF)
    assert all(isinstance(dl, DiffLine) for dl in result)


def test_parse_diff_counts():
    result = parse_diff(SAMPLE_DIFF)
    kinds = [dl.kind for dl in result]
    assert kinds.count("added") == 2
    assert kinds.count("removed") == 1
    assert kinds.count("header") == 1


def test_summarise_diff_additions_deletions():
    s = summarise_diff(SAMPLE_DIFF)
    assert s["additions"] == 2
    assert s["deletions"] == 1


def test_summarise_diff_files_changed():
    s = summarise_diff(SAMPLE_DIFF)
    assert "foo.py" in s["files_changed"]


def test_summarise_diff_empty():
    s = summarise_diff("")
    assert s == {"files_changed": [], "additions": 0, "deletions": 0}


def test_format_summary_line():
    line = format_summary_line(SAMPLE_DIFF)
    assert "1 file(s) changed" in line
    assert "+2 additions" in line
    assert "-1 deletions" in line


def test_format_summary_line_empty():
    line = format_summary_line("")
    assert line == "0 file(s) changed, +0 additions, -0 deletions"
