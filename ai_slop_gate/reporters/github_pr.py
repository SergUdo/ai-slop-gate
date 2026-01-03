from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.reporters.formatter import format_pr_comment
from ai_slop_gate.domain.decision import Decision
from ai_slop_gate.domain.observation import Observation
from typing import List


class GitHubPRReporter(Reporter):
    def __init__(self, token: str, repo: str, pr_number: int):
        try:
            from github import Github
        except ImportError as e:
            raise RuntimeError(
                "GitHubPRReporter requires PyGithub. "
                "Install with: pip install PyGithub"
            ) from e

        self.client = Github(token)
        self.repo = self.client.get_repo(repo)
        self.pr = self.repo.get_pull(pr_number)

    def report(self, decision: Decision, observations: List[Observation]) -> None:
        body = format_pr_comment(decision, observations)
        self.pr.create_issue_comment(body)
