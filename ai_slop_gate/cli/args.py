import argparse
import os


def build_parser():
    parser = argparse.ArgumentParser(
        description="AI Slop Gate — Multi-provider AI & Static Code Analysis"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------------------
    # INIT COMMAND
    # -----------------------------
    init_cmd = subparsers.add_parser("init", help="Initialize default policy.yml")
    init_cmd.add_argument("--force", action="store_true", help="Overwrite existing files")

    # -----------------------------
    # RUN COMMAND
    # -----------------------------
    run_cmd = subparsers.add_parser("run", help="Run analysis")

    run_cmd.add_argument(
        "--provider",
        "-p",
        nargs="+",
        required=True,
        help="List of providers to run (static, gemini, etc.)",
    )

    run_cmd.add_argument(
        "--path",
        default=".",
        help="Path to the project for static analysis",
    )

    run_cmd.add_argument(
        "--llm-local",
        action="store_true",
        help="Enable local LLM analysis",
    )

    run_cmd.add_argument(
        "--github-repo",
        help="GitHub repository (owner/repo)",
    )

    run_cmd.add_argument(
        "--pr-id",
        type=int,
        help="Pull Request ID",
    )

    run_cmd.add_argument(
        "--github-sha",
        help="Commit SHA for GitHub Checks",
    )

    run_cmd.add_argument(
        "--github-token",
        help="GitHub token",
    )

    run_cmd.add_argument(
        "--policy",
        default="policy.yml",
        help="Path to policy.yml",
    )

    run_cmd.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    return parser
