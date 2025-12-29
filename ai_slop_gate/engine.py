from .policy import load_policy
from .providers.openrouter import OpenRouterProvider
from .result import AIAnalysisResult

def run_analysis(policy_path: str, input_text: str) -> AIAnalysisResult:
    policy = load_policy(policy_path)

    provider = OpenRouterProvider(
        model=policy["model"],
        api_key=policy.get("api_key"),
    )

    return provider.analyze(input_text, policy)
