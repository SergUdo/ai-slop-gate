import re
import logging
from typing import List, Union
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.observation import Observation

logger = logging.getLogger(__name__)

class PolicyEngine:
    def __init__(self, rules: List[Union[dict, any]]):
        # Зберігаємо правила. В майбутньому тут має бути перетворення на об'єкти PolicyRule
        self.rules = rules or []

    def evaluate(self, observations: List[Observation]) -> Decision:
        if not self.rules:
            return Decision(mode=DecisionMode.ALLOW, reasons=[], annotations=[])

        reasons = []
        mode = DecisionMode.ALLOW

        for obs in observations:
            for rule in self.rules:
                # Гнучкий доступ: підтримуємо і словники (YAML), і об'єкти (Contracts)
                # rule.when -> rule['when']
                when = rule.get("when") if isinstance(rule, dict) else getattr(rule, "when", {})
                then = rule.get("then") if isinstance(rule, dict) else getattr(rule, "then", {})

                if not when or not then:
                    continue

                if self._matches(obs, when):
                    msg = then.get("message", "Policy violation")
                    reasons.append(msg)

                    action = then.get("action")
                    if action == "blocking":
                        mode = DecisionMode.BLOCKING
                    elif mode != DecisionMode.BLOCKING and action == "advisory":
                        mode = DecisionMode.ADVISORY

        return Decision(mode=mode, reasons=reasons, annotations=[])

    def _matches(self, obs: Observation, condition: dict) -> bool:
        """
        Логіка матчингу для Strict Mode:
        - Підтримує Regex для сигналів.
        - Підтримує списки для Severity.
        - Ігнорує відсутні поля (wildcard).
        """
        # 1. Category Match
        target_cat = condition.get("category")
        if target_cat and obs.category != target_cat:
            return False

        # 2. Signal Match (з підтримкою Regex)
        target_sig = condition.get("signal")
        if target_sig:
            if not re.match(f"^{target_sig}$", obs.signal):
                return False

        # 3. Severity Match (підтримка рядка або списку)
        target_sev = condition.get("severity")
        if target_sev:
            allowed = [target_sev] if isinstance(target_sev, str) else target_sev
            if obs.severity not in allowed:
                return False
                
        # 4. Confidence Match
        if obs.confidence < condition.get("min_confidence", 0.0):
            return False

        return True