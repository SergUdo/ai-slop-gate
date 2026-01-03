import logging
import os
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport

logger = logging.getLogger(__name__)

class GitHubChecksReporter(Reporter):
    def __init__(self, token: str, repo: str, sha: str):
        try:
            from github import Github
        except ImportError:
            raise RuntimeError("GitHubChecksReporter requires PyGithub. Run: pip install PyGithub")
            
        self.client = Github(token)
        self.repo = self.client.get_repo(repo)
        self.sha = sha

    def report(self, report: CheckReport) -> None:
        """
        Creates a GitHub Check Run with annotations.
        """
        # Convert CheckStatus to GitHub conclusion strings
        conclusion = "success"
        if report.status.value == "fail":
            conclusion = "failure"
        elif report.status.value == "advisory":
            conclusion = "neutral"

        output = {
            "title": report.title,
            "summary": report.summary,
            "annotations": []
        }

        if report.annotations:
            for ann in report.annotations:
                output["annotations"].append({
                    "path": ann.file,
                    "start_line": ann.line,
                    "end_line": ann.line,
                    "annotation_level": ann.level, # 'failure' or 'warning'
                    "message": ann.message,
                })

        try:
            # Create the check run on GitHub
            self.repo.create_check_run(
                name=report.title,
                head_sha=self.sha,
                status="completed",
                conclusion=conclusion,
                output=output
            )
            logger.info(f"GitHub Check Run created: {report.status}")
        except Exception as e:
            logger.error(f"Failed to create GitHub Check Run: {e}")