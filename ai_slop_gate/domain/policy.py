from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PolicyRule:
    """
    Declarative rule parsed from policy.yml
    """

    id: str
    match: List[str]          # observation codes
    decision: str             # "advisory" | "blocking"
    message: str
