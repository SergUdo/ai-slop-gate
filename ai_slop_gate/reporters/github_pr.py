from typing import List, Dict, Optional
from github import Github, GithubException
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

class GitHubPRReporter(Reporter):
    def __init__(self, token: str, repo_name: str, pr_id: int):
        if not token:
            print("GitHub token is missing. GitHubPRReporter is disabled.")
            self.client = None
            return

        try:
            self.client = Github(token)
            self.repo = self.client.get_repo(repo_name)
            self.pr = self.repo.get_pull(int(pr_id))
        except GithubException as e:
            print(f"Failed to initialize GitHub client: {e}")
            self.client = None

    def report(self, report: CheckReport) -> None:
        if not self.client:
            print("Skipping PR reporting: GitHub client not initialized.")
            return

        status_map = {
            "pass": ("✅", "PASS"),
            "advisory": ("⚠️", "ADVISORY"),
            "fail": ("🚨", "FAIL"),
        }
        status_icon, status_text = status_map.get(report.status.value, ("🔍", "UNKNOWN"))

        body = f"## {status_icon} {report.title}\n\n"
        body += f"> **Status:** {status_text}\n"
        body += f"> **Summary:** {report.summary}\n\n"

        if report.annotations:
            body += "### 📑 Detailed Observations\n"
            grouped_annotations = self._group_annotations(report.annotations)

            for group, annotations in grouped_annotations.items():
                body += f"\n#### {group}\n"
                for ann in annotations:
                    file_info = f" in `{ann.file}`" if ann.file else ""
                    line_info = f" L{ann.line}" if ann.line else ""
                    body += f"- **[{ann.level.upper()}]**{file_info}{line_info}: {ann.message}\n"

        body += "\n---\n*Reported by **[AI Slop Gate](https://github.com/SergUdo/ai-slop-gate)***"

        try:
            self.pr.create_issue_comment(body)
            print(f"Successfully posted PR comment to {self.repo.full_name}#{self.pr.number}")
        except GithubException as e:
            print(f"Failed to create PR comment: {e}")

    def _group_annotations(self, annotations: List[CheckAnnotation]) -> Dict[str, List[CheckAnnotation]]:
        groups = {}
        for ann in annotations:
            group_key = ann.message.split(":")[0] if ":" in ann.message else "Other"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(ann)
        return groups
