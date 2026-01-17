from dataclasses import dataclass
from typing import List

@dataclass
class ComplianceIssue:
    id: str
    license: str
    severity: str
    message: str


@dataclass
class ComplianceResult:
    issues: List[ComplianceIssue]

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
