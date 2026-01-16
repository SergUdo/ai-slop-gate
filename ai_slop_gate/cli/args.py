import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # INIT
    init_parser = subparsers.add_parser("init", help="Initialize ai-slop-gate config")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--policy")
    init_parser.add_argument("--provider")

    # RUN
    run_parser = subparsers.add_parser("run", help="Run analysis")

    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")

    run_parser.add_argument("--input-text")
    run_parser.add_argument("--input-file")
    run_parser.add_argument("--repo")

    # Compliance (intent only)
    run_parser.add_argument("--compliance", action="store_true")
    run_parser.add_argument("--eu-only", action="store_true")
    run_parser.add_argument("--license-policy")

    # GitHub
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-token")

    run_parser.add_argument(
        "--enforcement",
        choices=["never", "blocking", "advisory"],
        default="advisory",
    )

    return parser
