from github import Github
from typing import List
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.reporters.formatter import format_pr_comment, MARKER
from ai_slop_gate.domain.decision import Decision
from ai_slop_gate.domain.observation import Observation


class GitHubPRReporter(Reporter):
    def __init__(self, token: str, repo: str, pr_number: int):
        self.client = Github(token)
        self.repo = self.client.get_repo(repo)
        self.pr = self.repo.get_pull(pr_number)

    def report(
        self,
        decision: Decision,
        observations: List[Observation],
    ) -> None:
        body = format_pr_comment(decision, observations)

        for comment in self.pr.get_issue_comments():
            if MARKER in comment.body:
                comment.edit(body)
                return

        self.pr.create_issue_comment(body)
