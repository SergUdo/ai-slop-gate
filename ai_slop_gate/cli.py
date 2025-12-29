# cli.py
import argparse
import os
from dotenv import load_dotenv
from ai_slop_gate.adapters.github import GitHubAdapter
from ai_slop_gate.reporters.github import GitHubReporter
from ai_slop_gate.engine import run_analysis

load_dotenv()  # Завантаження змінних з .env

def main() -> None:
    parser = argparse.ArgumentParser(description="ai-slop-gate — detect low-quality AI-generated code")
    parser.add_argument("--policy", required=True, help="Path to policy.yaml file")
    parser.add_argument("--mode", choices=["advisory", "blocking"], default="advisory", help="Run mode")
    parser.add_argument("--input", required=False, default="Example input text", help="Input text or code to analyze")
    parser.add_argument("--github-repo", help="GitHub repository (e.g., SergUdo/ai-slop-gate)")
    parser.add_argument("--pr-id", type=int, help="Pull Request ID to analyze")

    args = parser.parse_args()

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN is missing. Set it in .env or GitHub Secrets.")

    if args.github_repo and args.pr_id:
        adapter = GitHubAdapter(github_token)
        inputs = adapter.fetch_pr_diff(args.github_repo, args.pr_id)
        for input_text in inputs:
            result = run_analysis(args.policy, input_text)
            reporter = GitHubReporter(github_token)
            reporter.comment_on_pr(args.github_repo, args.pr_id, result)
    else:
        result = run_analysis(args.policy, args.input)
        from ai_slop_gate.reporters.console import print_result
        print_result(result)

if __name__ == "__main__":
    main()
