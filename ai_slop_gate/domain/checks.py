from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CheckStatus(str, Enum):
    PASS = "pass"
    ADVISORY = "advisory"
    FAIL = "fail"


@dataclass(frozen=True)
class CheckAnnotation:
    file: str
    line: int
    message: str
    level: str  # "warning" | "failure"


@dataclass(frozen=True)
class CheckReport:
    title: str
    summary: str
    status: CheckStatus
    annotations: Optional[List[CheckAnnotation]] = None
