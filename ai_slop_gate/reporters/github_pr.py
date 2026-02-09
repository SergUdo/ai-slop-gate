import logging
from typing import List, Dict, Optional
from github import Github, GithubException
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

logger = logging.getLogger(__name__)

class GitHubPRReporter(Reporter):
    def __init__(self, token: str, repo_name: str, pr_id: int):
        if not token:
            logger.error("GitHub token is missing. GitHubPRReporter is disabled.")
            self.client = None
            return

        try:
            self.client = Github(token)
            self.repo = self.client.get_repo(repo_name)
            self.pr = self.repo.get_pull(int(pr_id))
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            self.client = None

    def report(self, report: CheckReport) -> None:
        if not self.client:
            logger.warning("Skipping PR reporting: GitHub client not initialized.")
            return

        # Determine status icon and text based on report status. We want to make it visually clear in the PR comment whether this is a pass, advisory, or fail, so we use emojis and consistent formatting.
        status_val = report.status.name.lower() if hasattr(report.status, 'name') else str(report.status).lower()
        
        status_map = {
            "pass": ("✅", "PASS"),
            "allow": ("✅", "PASS"),
            "advisory": ("⚠️", "ADVISORY"),
            "blocking": ("🚨", "FAIL"),
            "fail": ("🚨", "FAIL"),
        }
        status_icon, status_text = status_map.get(status_val, ("🔍", "UNKNOWN"))

        body = f"## {status_icon} {report.title}\n\n"
        body += f"> **Status:** {status_text}\n"
        body += f"> **Summary:** {report.summary}\n\n"

        if report.annotations:
            body += "### 📑 Detailed Observations\n"
            grouped = self._group_annotations(report.annotations)
            for group, annotations in grouped.items():
                body += f"\n#### {group}\n"
                for ann in annotations:
                    file_info = f" in `{ann.file}`" if ann.file else ""
                    line_info = f" L{ann.line}" if ann.line else ""
                    body += f"- **[{ann.level.upper()}]**{file_info}{line_info}: {ann.message}\n"

        body += "\n---\n*Reported by **[AI Slop Gate](https://github.com/SergUdo/ai-slop-gate)***"

        try:
            self.pr.create_issue_comment(body)
            logger.info(f"✅ Successfully posted PR comment to {self.repo.full_name}#{self.pr.number}")
        except GithubException as e:
            logger.error(f"Failed to create PR comment: {e}")

    def _group_annotations(self, annotations: List[CheckAnnotation]) -> Dict[str, List[CheckAnnotation]]:
        groups = {}
        for ann in annotations:
            # Group by the first part of the message (e.g. signal type) to organize observations. This helps reviewers quickly understand the main categories of issues without getting lost in details.
            group_key = ann.message.split("]")[0].replace("[", "") if "]" in ann.message else "Other"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(ann)
        return groups