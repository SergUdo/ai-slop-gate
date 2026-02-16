from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuntimeContext:
    """
    Unified runtime context for AI Slop Gate CLI.
    Contains all parameters required by run.py.
    """

    # Multi-provider mode
    providers: List[str]

    # Local static analysis path
    path: str

    # LLM local mode (LLM allowed to analyze local files)
    llm_local: bool = False

    # GitHub PR mode
    github_repo: Optional[str] = None
    pr_id: Optional[int] = None
    github_sha: Optional[str] = None
    github_token: Optional[str] = None

    # GitLab MR mode  
    gitlab_project: Optional[str] = None
    mr_iid: Optional[int] = None
    gitlab_url: str = 'https://gitlab.com'
    gitlab_token: Optional[str] = None

    # Policy file path
    policy_path: str = "policy.yml"

    # Verbose console output
    verbose: bool = False

    # Compliance mode
    compliance: bool = False
    compliance_only: bool = False

    # Cache configuration
    cache_dir: str = ".ai-slop-cache"
    no_cache: bool = False
    