# engine.py
from .policy import load_policy
from .providers.openrouter import OpenRouterProvider
from .providers.gemini import GeminiProvider
from .result import AIAnalysisResult, AnalysisInput
import os

def run_analysis(policy_path: str, input_text: str | AnalysisInput, provider_override: str = None) -> AIAnalysisResult:
    policy = load_policy(policy_path)
    
    selected_provider = provider_override or policy.get("provider", "static")

    if selected_provider == "gemini":
        provider = GeminiProvider(
            model=policy.get("model", "models/gemini-2.5-flash"),
            api_key=os.getenv("GEMINI_API_KEY")
        )
    elif selected_provider == "static":
        from .providers.static import StaticProvider
        provider = StaticProvider()
    else:
        provider = OpenRouterProvider(
            model=policy.get("model", "llama3"),
            api_key=os.getenv("LLAMA_API_KEY2")
        )

    if isinstance(input_text, AnalysisInput):
        text = input_text.text
    else:
        text = input_text

    return provider.analyze(text, policy)


