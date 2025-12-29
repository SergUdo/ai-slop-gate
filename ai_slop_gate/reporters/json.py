import json
from ai_slop_gate.result import AIAnalysisResult

def print_json(result: AIAnalysisResult):
    output = {
        "summary": result.summary,
        "issues": [{"severity": i.severity, "message": i.message} for i in result.issues]
    }
    print(json.dumps(output, indent=2))
