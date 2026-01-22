import logging
from typing import List, Dict, Optional
from github import Github, GithubException
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

logger = logging.getLogger(__name__)

class GitHubPRReporter(Reporter):
    """
    Reporter that publishes analysis results as comments on GitHub Pull Requests.
    Uses PyGithub to interact with the GitHub REST API.
    """

    def __init__(self, token: str, repo_name: str, pr_id: int):
        if not token:
            logger.warning("GitHub token is missing. GitHubPRReporter is disabled.")
            self.client = None
            return

        try:
            self.client = Github(token)
            self.repo = self.client.get_repo(repo_name)
            self.pr = self.repo.get_pull(int(pr_id))
        except GithubException as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            self.client = None

    def report(self, report: CheckReport) -> None:
        """
        Formats the CheckReport into a Markdown comment and posts it to the PR.
        """
        if not self.client:
            logger.info("Skipping PR reporting: GitHub client not initialized.")
            return

        # Map internal status values to visual indicators
        status_map = {
            "pass": ("✅", "PASS"),
            "advisory": ("⚠️", "ADVISORY"),
            "fail": ("🚨", "FAIL"),
        }
        status_icon, status_text = status_map.get(report.status.value, ("🔍", "UNKNOWN"))

        # Construct the Markdown header and summary block
        body = f"## {status_icon} {report.title}\n\n"
        body += f"> **Status:** {status_text}\n"
        body += f"> **Summary:** {report.summary}\n\n"

        if report.annotations:
            body += "### 📑 Detailed Observations\n"
            use_spoiler = len(report.annotations) > 5
            if use_spoiler:
                body += "<details><summary>Click to view all findings</summary>\n\n"

            for ann in report.annotations:
                level_icon = "🛑" if ann.level == "failure" else "⚠️"
                location = f"in `{ann.file}`" if ann.file else ""
                line_info = f" L{ann.line}" if ann.line else ""
                body += f"- {level_icon} **[{ann.level.upper()}]** {location}{line_info}: {ann.message}\n"

            if use_spoiler:
                body += "\n</details>\n"

        # Add footer with project branding
        body += "\n---\n*Reported by **[AI Slop Gate](https://github.com/SergUdo/ai-slop-gate)***"

        try:
            self.pr.create_issue_comment(body)
            logger.info(f"Successfully posted PR comment to {self.repo.full_name}#{self.pr.number}")
        except GithubException as e:
            logger.error(f"Failed to create PR comment: {e}")
