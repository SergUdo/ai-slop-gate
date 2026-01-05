import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("ai-slop-gate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # INIT
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument("--force", action="store_true", help="Overwrite config")
    init_parser.add_argument("--policy", help="Path to policy.yml")
    init_parser.add_argument("--provider", help="Default provider for initial run")

    # RUN
    run_parser = subparsers.add_parser("run", help="Run slop gate analysis")
    run_parser.add_argument("--policy", required=True)
    run_parser.add_argument("--provider", default="static")
    run_parser.add_argument("--k8s-manifests", help="Path to K8s manifests YAML")
    run_parser.add_argument("--pr-id", type=int)
    run_parser.add_argument("--github-checks", action="store_true")
    run_parser.add_argument("--github-repo")
    run_parser.add_argument("--github-sha")
    run_parser.add_argument(
        "--enforcement",
        choices=["never", "blocking", "advisory"],
        default="advisory",
    )

    return parser
