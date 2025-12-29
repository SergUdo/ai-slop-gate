from github import Github
from ..result import AIAnalysisResult

class GitHubReporter:
    def __init__(self, token: str):
        self.client = Github(token)

    def comment_on_pr(self, repo_name: str, pr_id: int, result: AIAnalysisResult):
        repo = self.client.get_repo(repo_name)
        pr = repo.get_pull(pr_id)
        message = f"### AI Slop Gate Analysis\n**Summary:** {result.summary}\n"
        if result.issues:
            message += "\n**Issues:**\n"
            for issue in result.issues:
                message += f"- [{issue.severity}] {issue.message}\n"
        else:
            message += "\n✅ No issues found."
        pr.create_issue_comment(message)

from ..result import AIAnalysisResult

class GitHubReporter:
    def __init__(self, token: str):
        self.client = Github(token)

    def comment_on_pr(self, repo_name: str, pr_id: int, result: AIAnalysisResult):
        repo = self.client.get_repo(repo_name)
        pr = repo.get_pull(pr_id)
        message = f"### AI Slop Gate Analysis\n**Summary:** {result.summary}\n"
        if result.issues:
            message += "\n**Issues:**\n"
            for issue in result.issues:
                message += f"- [{issue.severity}] {issue.message}\n"
        else:
            message += "\n✅ No issues found."
        pr.create_issue_comment(message)
