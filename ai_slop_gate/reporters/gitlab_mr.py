import logging
from typing import List, Dict, Optional
import requests
from ai_slop_gate.reporters.base import Reporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation

logger = logging.getLogger(__name__)


class GitLabMRReporter(Reporter):
    """
    GitLab Merge Request reporter for AI Slop Gate.
    Posts analysis results as comments on GitLab Merge Requests.
    """

    def __init__(self, token: str, project_path: str, mr_iid: int, gitlab_url: str = "https://gitlab.com"):
        """
        Initialize GitLab MR Reporter.
        
        Args:
            token: GitLab API token (CI_JOB_TOKEN or personal access token)
            project_path: Project path (e.g., "username/project")
            mr_iid: Merge Request IID (internal ID)
            gitlab_url: GitLab instance URL (default: gitlab.com)
        """
        self.token = token
        self.project_path = project_path.replace('/', '%2F')
        self.mr_iid = mr_iid
        self.gitlab_url = gitlab_url.rstrip('/')
        self.api_url = f"{self.gitlab_url}/api/v4"
        
        if not token:
            logger.error("GitLab token is missing. GitLabMRReporter is disabled.")
            self.enabled = False
        else:
            self.enabled = True

    def report(self, report: CheckReport) -> None:
        """Post report as MR comment."""
        if not self.enabled:
            logger.warning("Skipping GitLab MR reporting: token not provided.")
            return

        status_val = report.status.name.lower() if hasattr(report.status, 'name') else str(report.status).lower()
        
        status_map = {
            "pass": ("✅", "PASS"),
            "allow": ("✅", "PASS"),
            "advisory": ("⚠️", "ADVISORY"),
            "blocking": ("🚨", "FAIL"),
            "fail": ("🚨", "FAIL"),
        }
        status_icon, status_text = status_map.get(status_val, ("📋", "UNKNOWN"))

        body = f"## {status_icon} {report.title}\n\n"
        body += f"> **Status:** {status_text}\n"
        body += f"> **Summary:** {report.summary}\n\n"

        if report.annotations:
            body += "### 🔍 Detailed Observations\n\n"
            grouped = self._group_annotations(report.annotations)
            
            for group, annotations in grouped.items():
                body += f"#### {group}\n\n"
                for ann in annotations:
                    file_info = f" in `{ann.file}`" if ann.file else ""
                    line_info = f":L{ann.line}" if ann.line else ""
                    body += f"- **[{ann.level.upper()}]**{file_info}{line_info}: {ann.message}\n"
                body += "\n"

        body += "---\n*Reported by **[AI Slop Gate](https://github.com/SergUdo/ai-slop-gate)***"

        self._post_mr_comment(body)

    def _post_mr_comment(self, body: str) -> None:
        """Post comment to GitLab Merge Request."""
        url = f"{self.api_url}/projects/{self.project_path}/merge_requests/{self.mr_iid}/notes"
        
        if self.token.startswith("glpat-"):
            auth_header = "PRIVATE-TOKEN"
        else:
            auth_header = "JOB-TOKEN"
            
        headers = {
            auth_header: self.token,
            "Content-Type": "application/json"
        }
        
        payload = {"body": body}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"✅ Successfully posted GitLab MR comment!")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to post GitLab MR comment: {e}")

    def _group_annotations(self, annotations: List[CheckAnnotation]) -> Dict[str, List[CheckAnnotation]]:
        """Group annotations by signal type."""
        groups = {}
        for ann in annotations:
            # Extract signal from message
            group_key = ann.message.split("]")[0].replace("[", "") if "]" in ann.message else "Other"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(ann)
        return groups