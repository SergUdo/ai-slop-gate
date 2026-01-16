import sys
from ai_slop_gate.cli.args import build_parser
from ai_slop_gate.cli.context import RuntimeContext
from ai_slop_gate.cli.init_cmd import run_init
from ai_slop_gate.cli.run import run_analysis


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        run_init(force=args.force)
        return

    if args.command == "run":
        ctx = RuntimeContext(
            input_text=args.input_text,
            input_file=args.input_file,
            repository=args.repo,
            policy_path=args.policy,
            enforcement=args.enforcement,
            provider=args.provider,
            compliance_enabled=args.compliance,
            eu_only=args.eu_only,
            license_policy=args.license_policy,
            github_repo=args.github_repo,
            github_sha=args.github_sha,
            pr_id=args.pr_id,
            github_checks=args.github_checks,
            github_token=args.github_token,
        )
        run_analysis(ctx)
        return

    sys.exit(1)


if __name__ == "__main__":
    main()
