"""CLI entry-point for managing stash entry tags.

Usage examples::

    stashpull-tags add stash@{0} wip feature-x
    stashpull-tags remove stash@{0} wip
    stashpull-tags list stash@{0}
    stashpull-tags search wip
    stashpull-tags all
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from stashpull.tags import add_tag, remove_tag, get_tags, list_tagged, all_known_tags


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stashpull-tags",
        description="Manage user-defined tags on git stash entries.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add one or more tags to a stash ref.")
    p_add.add_argument("ref", help="Stash ref, e.g. stash@{0}")
    p_add.add_argument("tags", nargs="+", help="Tags to add.")

    p_rm = sub.add_parser("remove", help="Remove one or more tags from a stash ref.")
    p_rm.add_argument("ref", help="Stash ref, e.g. stash@{0}")
    p_rm.add_argument("tags", nargs="+", help="Tags to remove.")

    p_list = sub.add_parser("list", help="List tags for a stash ref.")
    p_list.add_argument("ref", help="Stash ref, e.g. stash@{0}")

    p_search = sub.add_parser("search", help="List all stash refs carrying a tag.")
    p_search.add_argument("tag", help="Tag to search for.")

    sub.add_parser("all", help="List every tag currently in use.")

    return parser


def run(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        for tag in args.tags:
            add_tag(args.ref, tag)
        current = get_tags(args.ref)
        print(f"{args.ref}: {', '.join(current) if current else '(no tags)'}")

    elif args.command == "remove":
        for tag in args.tags:
            remove_tag(args.ref, tag)
        current = get_tags(args.ref)
        print(f"{args.ref}: {', '.join(current) if current else '(no tags)'}")

    elif args.command == "list":
        tags = get_tags(args.ref)
        if tags:
            for t in tags:
                print(t)
        else:
            print(f"No tags for {args.ref}.")

    elif args.command == "search":
        refs = list_tagged(args.tag)
        if refs:
            for ref in refs:
                print(ref)
        else:
            print(f"No stash entries tagged '{args.tag}'.")

    elif args.command == "all":
        tags = all_known_tags()
        if tags:
            for t in tags:
                print(t)
        else:
            print("No tags defined.")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
