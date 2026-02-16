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
            # GitHub parameters
            github_repo=args.github_repo,
            pr_id=args.pr_id,
            github_sha=args.github_sha,
            github_token=args.github_token,
            # GitLab parameters
            gitlab_project=getattr(args, 'gitlab_project', None),
            mr_iid=getattr(args, 'mr_iid', None),
            gitlab_url=getattr(args, 'gitlab_url', 'https://gitlab.com'),
            gitlab_token=getattr(args, 'gitlab_token', None),
            # Other parameters
            policy_path=args.policy,
            verbose=args.verbose,
            compliance=getattr(args, 'compliance', False),
            compliance_only=getattr(args, 'compliance_only', False),
            # Cache parameters
            cache_dir=getattr(args, 'cache_dir', '.ai-slop-cache'),
            no_cache=getattr(args, 'no_cache', False)
        )
        return run_cli(ctx)

    raise SystemExit(1)


if __name__ == "__main__":
    sys.exit(main())
    