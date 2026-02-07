# ai_slop_gate/providers/llm/__init__.py

def __getattr__(name):
    if name == "GeminiProvider":
        from .gemini import GeminiProvider
        return GeminiProvider
    elif name == "GroqProvider":
        from .groq import GroqProvider
        return GroqProvider
    elif name == "OpenRouterProvider":
        from .openrouter import OpenRouterProvider
        return OpenRouterProvider
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "GeminiProvider",
    "GroqProvider",
    "OpenRouterProvider",
]
