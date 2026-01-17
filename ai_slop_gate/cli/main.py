import argparse
from ai_slop_gate.cli.run import run_cli
from ai_slop_gate.cli.init import run_init



def main():
    parser = argparse.ArgumentParser(prog="ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init command
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")

    # run command
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", required=True)
    run_parser.add_argument("--input-file")
    run_parser.add_argument("--input-text")
    run_parser.add_argument("--k8s-manifests")
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument("--pr-id")
    run_parser.add_argument("--enforcement")
    run_parser.add_argument("--compliance", action="store_true")
    run_parser.add_argument("--profile")
    run_parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.command == "init":
        exit_code = run_init(args.force)
    elif args.command == "run":
        exit_code = run_cli(args)

    raise SystemExit(exit_code)

if __name__ == "__main__":
    main()
