"""Module for interacting with git stash entries."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StashEntry:
    """Represents a single git stash entry."""

    index: int
    ref: str
    message: str
    branch: str
    diff: str = field(default="", repr=False)

    @property
    def short_label(self) -> str:
        return f"stash@{{{self.index}}}: {self.message}"


def _run(cmd: List[str], cwd: Optional[str] = None) -> str:
    """Run a shell command and return stdout, raising on error."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command {cmd!r} failed:\n{result.stderr.strip()}"
        )
    return result.stdout


def list_stashes(repo_path: Optional[str] = None) -> List[StashEntry]:
    """Return all stash entries for the repository at *repo_path*."""
    raw = _run(
        ["git", "stash", "list", "--format=%gd|%s|%D"],
        cwd=repo_path,
    )
    entries: List[StashEntry] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 2)
        ref = parts[0].strip()          # e.g. stash@{0}
        message = parts[1].strip() if len(parts) > 1 else ""
        decorations = parts[2].strip() if len(parts) > 2 else ""
        # Extract branch name from decoration like "On main: ..."
        branch = ""
        for token in decorations.split(","):
            token = token.strip()
            if token.startswith("On "):
                branch = token[3:].strip()
                break
        index = int(ref.split("{")[1].rstrip("}"))
        entries.append(StashEntry(index=index, ref=ref, message=message, branch=branch))
    return entries


def get_stash_diff(ref: str, repo_path: Optional[str] = None) -> str:
    """Return the unified diff for a stash entry."""
    return _run(["git", "stash", "show", "-p", ref], cwd=repo_path)


def apply_stash(ref: str, repo_path: Optional[str] = None) -> str:
    """Apply a stash entry without dropping it."""
    return _run(["git", "stash", "apply", ref], cwd=repo_path)


def pop_stash(ref: str, repo_path: Optional[str] = None) -> str:
    """Apply a stash entry and remove it from the stash list."""
    return _run(["git", "stash", "pop", ref], cwd=repo_path)
