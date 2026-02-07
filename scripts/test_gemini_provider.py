# python -m  scripts.test_gemini_provider

import os
import logging
from pathlib import Path
from ai_slop_gate.providers.llm import GeminiProvider

logging.basicConfig(level=logging.ERROR)

def main():
    GITHUB_REPO = "SergUdo/slop_test"
    PR_ID = 1
    MODEL = "models/gemini-2.5-flash" 
    
    code = """
def process_data(data):
    # TODO: this is a placeholder for actual logic
    # FIXME: potential security risk here
    if data == "admin":
        return True
    return False
"""
    test_file = Path("test_example.py")
    test_file.write_text(code)

    print(f"\n{'='*60}")
    print(f"🚀 RUNNING GEMINI SMOKE TEST FOR: {GITHUB_REPO} (PR #{PR_ID})")
    print(f"{'='*60}\n")

    try:
        if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            print("❌ ERROR: Set GEMINI_API_KEY environment variable first!")
            return

        provider = GeminiProvider(model=MODEL)
        
        print(f"📡 Sending request to {MODEL}...")
        result = provider.analyze("", str(test_file))

        print(f"\n📊 Results from {result.provider} ({result.model}):")
        print("-" * 40)

        if result.observations:
            for i, obs in enumerate(result.observations, 1):
                sev = str(getattr(obs, 'severity', 'info')).lower()
                icon = "🔴" if sev == "high" else "🟡" if sev == "medium" else "🔵"
                
                print(f"{icon} Issue #{i} [{sev.upper()}]")
                print(f"   📝 Message:  {obs.message}")
                print(f"   🎯 Signal:   {getattr(obs, 'signal', 'N/A')}")
                
                evidence = getattr(obs, 'evidence', {})
                if evidence:
                    file_info = evidence.get('file', 'unknown')
                    line_info = evidence.get('line', 'N/A')
                    print(f"   📍 Location: {file_info}:{line_info}")
                print()
        else:
            print("✨ No observations returned. Code looks clean!")

        print("-" * 40)
        print("📝 Full Raw Output:")
        print(result.raw_text)

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
    
    finally:
        if test_file.exists():
            test_file.unlink()
            print("\n🧹 Temporary files cleaned up.")

if __name__ == "__main__":
    main()