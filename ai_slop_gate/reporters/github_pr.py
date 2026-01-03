import logging
import os
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport

logger = logging.getLogger(__name__)

class GitHubPRReporter(Reporter):
    def __init__(self, token: str, repo_name: str, pr_number: int):
        try:
            from github import Github
        except ImportError:
            raise RuntimeError(
                "GitHubPRReporter requires PyGithub. Install with: pip install PyGithub"
            )

        self.client = Github(token)
        self.repo = self.client.get_repo(repo_name)
        self.pr = self.repo.get_pull(pr_number)

    def report(self, report: CheckReport) -> None:
        """
        Publishes the CheckReport as a comment on a GitHub Pull Request.
        """
        # Building the Markdown body from the CheckReport domain object
        status_icon = "✅" if report.status.value == "pass" else "⚠️"
        if report.status.value == "fail":
            status_icon = "🚨"

        body = f"## {status_icon} {report.title}\n\n"
        body += f"{report.summary}\n\n"
        
        if report.annotations:
            body += "### Detailed Observations:\n"
            for ann in report.annotations:
                level_icon = "❌" if ann.level == "failure" else "🔍"
                body += f"- {level_icon} **{ann.level.upper()}** in `{ann.file}` L{ann.line}: {ann.message}\n"
        
        body += "\n---\n*Reported by [AI Slop Gate](https://github.com/SergUdo/ai-slop-gate)*"

        try:
            self.pr.create_issue_comment(body)
            logger.info(f"Successfully posted PR comment to {self.repo.full_name}#{self.pr.number}")
        except Exception as e:
            logger.error(f"Failed to create PR comment: {str(e)}")