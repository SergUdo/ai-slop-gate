from dataclasses import dataclass
from typing import Literal

@dataclass
class AnalysisIssue:
    message: str
    severity: Literal["info", "warning", "error"]

@dataclass
class AIAnalysisResult:
    summary: str
    issues: list[AnalysisIssue]
