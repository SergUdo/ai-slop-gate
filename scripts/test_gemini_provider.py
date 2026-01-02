# python -m scripts.test_gemini_provider

from ai_slop_gate.providers.gemini import GeminiProvider

code = """
def foo():
    # TODO: refactor this
    return 42
"""

provider = GeminiProvider(model="models/gemini-2.5-flash")
result = provider.analyze(code)

print("Provider:", result.provider)
print("Model:", result.model)
print("Raw text:")
print(result.raw_text)
print("\nObservations:")
for obs in result.observations:
    print("-", obs)
