from ..result import AIAnalysisResult, AnalysisIssue

class OpenRouterProvider:
    def __init__(self, model: str, api_key: str | None):
        self.model = model
        self.api_key = api_key

    def analyze(self, text: str, policy: dict) -> AIAnalysisResult:
        # Stage 1 — MOCK
        # Реальний HTTP буде у Stage 2

        issues = []

        if "TODO" in text:
            issues.append(
                AnalysisIssue(
                    message="Found TODO in code",
                    severity="warning",
                )
            )

        return AIAnalysisResult(
            summary="Mock analysis completed",
            issues=issues,
        )
