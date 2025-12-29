from github import Github
from typing import List
from ..result import AnalysisInput

class GitHubAdapter:
    def __init__(self, token: str):
        self.client = Github(token)

    def fetch_pr_diff(self, repo_name: str, pr_id: int) -> List[AnalysisInput]:
        repo = self.client.get_repo(repo_name)
        pr = repo.get_pull(pr_id)
        files = pr.get_files()
        return [
            AnalysisInput(
                text=repo.get_contents(file.filename).decoded_content.decode(),
                filename=file.filename
            )
            for file in files
        ]
