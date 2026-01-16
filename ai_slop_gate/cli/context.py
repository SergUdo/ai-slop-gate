from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class RuntimeContext:
    # Input
    input_text: Optional[str] = None
    input_file: Optional[str] = None
    repository: Optional[str] = None

    # Policy
    policy_path: str = "policy.yml"
    enforcement: str = "advisory"

    # Providers
    provider: str = "static"
    enabled_providers: Optional[List[str]] = None

    # Compliance
    compliance_enabled: bool = False
    eu_only: bool = False
    license_policy: Optional[str] = None

    # GitHub
    github_repo: Optional[str] = None
    github_sha: Optional[str] = None
    pr_id: Optional[int] = None
    github_checks: bool = False
    github_token: Optional[str] = None

    # Runtime
    is_ci: bool = False
    is_docker: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__
