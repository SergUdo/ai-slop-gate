from ..result import AIAnalysisResult

def print_result(result: AIAnalysisResult):
    print("=== ai-slop-gate report ===")

    if not result.issues:
        print("(no issues found)")
    else:
        print(result.summary)
        print()
        for issue in result.issues:
            print(f"[{issue.severity.upper()}] {issue.message}")

    print("=== end of report ===")

