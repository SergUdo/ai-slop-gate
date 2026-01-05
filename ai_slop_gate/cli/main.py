import argparse
import sys

from ai_slop_gate.cli.init import run_init


def main() -> None:
    parser = argparse.ArgumentParser("ai-slop-gate")

    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing config",
    )
    # run (STUB, для Stage 6.1)
    run_parser = subparsers.add_parser(
        "run",
        help="Run slop gate analysis (not implemented yet)",
    )

    args = parser.parse_args()

    if args.command == "init":
        run_init(force=args.force)
        return
    if args.command == "run":
        print("Run command is not implemented yet.")
        return


    parser.print_help()
    sys.exit(1)
