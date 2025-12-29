# engine.py
from .policy import load_policy
from .providers.openrouter import OpenRouterProvider
from .providers.gemini import GeminiProvider
from .result import AIAnalysisResult, AnalysisInput
import os

def run_analysis(policy_path: str, input_text: str | AnalysisInput) -> AIAnalysisResult:
    policy = load_policy(policy_path)

    if policy.get("provider") == "gemini":
        provider = GeminiProvider(
            model=policy["model"],
            api_key=os.getenv("GEMINI_API_KEY")
        )
    else:
        provider = OpenRouterProvider(
            model=policy["model"],
            api_key=os.getenv("LLAMA_API_KEY2")
        )

    if isinstance(input_text, AnalysisInput):
        text = input_text.text
    else:
        text = input_text

    return provider.analyze(text, policy)


