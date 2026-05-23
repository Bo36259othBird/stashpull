"""CLI sub-command: stashpull export — write selected stash entries to patch files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stashpull.export import export_entries, format_export_summary
from stashpull.filter import search
from stashpull.stash import list_stashes


def build_parser(parent: "argparse._SubParsersAction | None" = None) -> argparse.ArgumentParser:
    description = "Export stash entries as .patch files."
    if parent is not None:
        parser = parent.add_parser("export", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="stashpull export", description=description)

    parser.add_argument(
        "-o",
        "--output-dir",
        default="./stash-patches",
        metavar="DIR",
        help="Directory to write patch files into (default: ./stash-patches).",
    )
    parser.add_argument(
        "-q",
        "--query",
        default="",
        metavar="TEXT",
        help="Only export entries whose message matches TEXT.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing patch files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be exported without writing files.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the export command; returns an exit code."""
    entries = list_stashes()
    if not entries:
        print("No stash entries found.", file=sys.stderr)
        return 0

    if args.query:
        entries = search(entries, args.query)

    if not entries:
        print("No entries matched the query.", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)

    if args.dry_run:
        print(f"Would export {len(entries)} entr(ies) to {output_dir}:")
        for e in entries:
            print(f"  {e.ref}  {e.message}")
        return 0

    results = export_entries(entries, output_dir, overwrite=args.overwrite)
    summary = format_export_summary(results)
    if summary:
        print(summary)

    failed = [r for r in results if not r.success]
    return 1 if failed else 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
