import os
from pathlib import Path
from ai_slop_gate.providers.gemini import GeminiProvider

def main():
    # Example code to analyze
    code = """
def foo():
    # TODO: refactor this
    return 42
"""

    # Example file to analyze
    test_file = Path("test_example.py")
    test_file.write_text(code)

    try:
        provider = GeminiProvider(model="models/gemini-2.5-flash")
        result = provider.analyze("", str(test_file))

        print("Provider:", result.provider)
        print("Model:", result.model)
        print("Raw text:")
        print(result.raw_text)
        print("\nObservations:")
        for obs in result.observations:
            print(f"- {obs}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    main()