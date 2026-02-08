import sys
from ai_slop_gate.cli.args import build_parser
from ai_slop_gate.cli.context import RuntimeContext
from ai_slop_gate.cli.run import run_cli
from ai_slop_gate.cli.init import run_init


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        run_init(force=args.force)
        return 0

    if args.command == "run":
        ctx = RuntimeContext(
            providers=args.provider,
            path=args.path,
            llm_local=args.llm_local,
            github_repo=args.github_repo,
            pr_id=args.pr_id,
            github_sha=args.github_sha,
            github_token=args.github_token,
            policy_path=args.policy,
            verbose=args.verbose,
            compliance_only=getattr(args, "compliance", False)
        )
        return run_cli(ctx)

    raise SystemExit(1)


if __name__ == "__main__":
    sys.exit(main())
