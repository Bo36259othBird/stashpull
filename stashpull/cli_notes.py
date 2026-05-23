"""CLI sub-commands for managing per-stash notes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stashpull.notes import delete_note, get_note, list_noted_refs, set_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stashpull-notes",
        description="Manage notes attached to git stash entries.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # set
    p_set = sub.add_parser("set", help="Attach a note to a stash entry.")
    p_set.add_argument("ref", help="Stash ref, e.g. stash@{0}")
    p_set.add_argument("text", help="Note text")

    # get
    p_get = sub.add_parser("get", help="Print the note for a stash entry.")
    p_get.add_argument("ref", help="Stash ref, e.g. stash@{0}")

    # delete
    p_del = sub.add_parser("delete", help="Remove the note for a stash entry.")
    p_del.add_argument("ref", help="Stash ref, e.g. stash@{0}")

    # list
    sub.add_parser("list", help="List all stash refs that have notes.")

    return parser


def run(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "set":
        set_note(args.ref, args.text, repo_root)
        print(f"Note set for {args.ref}.")

    elif args.command == "get":
        note = get_note(args.ref, repo_root)
        if note:
            print(note)
        else:
            print(f"No note found for {args.ref}.", file=sys.stderr)
            return 1

    elif args.command == "delete":
        removed = delete_note(args.ref, repo_root)
        if removed:
            print(f"Note deleted for {args.ref}.")
        else:
            print(f"No note found for {args.ref}.", file=sys.stderr)
            return 1

    elif args.command == "list":
        refs = list_noted_refs(repo_root)
        if refs:
            for ref in refs:
                print(ref)
        else:
            print("No notes recorded.")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
