import json
import sys
from pathlib import Path

def load_json(path):
    if not Path(path).exists():
        return []
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return []

def main():
    static_results = load_json("static_results.json")
    groq_results = load_json("groq_results.json")

    combined = static_results + groq_results

    Path("combined_results.json").write_text(json.dumps(combined, indent=2))
    print(f"Combined {len(static_results)} static + {len(groq_results)} groq → {len(combined)} findings")

if __name__ == "__main__":
    main()
