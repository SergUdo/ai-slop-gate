from github import Github
from ai_slop_gate.reporters.base import CheckReporter
from ai_slop_gate.domain.checks import CheckReport, CheckStatus


class GitHubChecksReporter(CheckReporter):
    def __init__(self, token: str, repo: str, sha: str):
        self.client = Github(token)
        self.repo = self.client.get_repo(repo)
        self.sha = sha

    def report(self, report: CheckReport) -> None:
        conclusion = {
            CheckStatus.PASS: "success",
            CheckStatus.ADVISORY: "neutral",
            CheckStatus.FAIL: "failure",
        }[report.status]

        annotations = []
        for ann in report.annotations or []:
            annotations.append(
                {
                    "path": ann.file,
                    "start_line": ann.line,
                    "end_line": ann.line,
                    "annotation_level": ann.level,
                    "message": ann.message,
                }
            )

        self.repo.create_check_run(
            name="AI Slop Gate",
            head_sha=self.sha,
            status="completed",
            conclusion=conclusion,
            output={
                "title": report.title,
                "summary": report.summary,
                "annotations": annotations[:50],  # GitHub hard limit
            },
        )
