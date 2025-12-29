import os
import google.generativeai as genai
from ..result import AIAnalysisResult, AnalysisIssue

class GeminiProvider:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=self.api_key)

    def analyze(self, text: str, policy: dict) -> AIAnalysisResult:
        model = genai.GenerativeModel(self.model)

        issues = []

        if "TODO" in text and policy.get("ai_slop", {}).get("detect_todo", False):
            issues.append(AnalysisIssue(message="Found TODO comment in code", severity="warning"))

        if "FIXME" in text and policy.get("ai_slop", {}).get("detect_fixme", False):
            issues.append(AnalysisIssue(message="Found FIXME comment in code", severity="warning"))

        ai_slop_rules = policy.get("ai_slop", {})
        for rule_name, rule_config in ai_slop_rules.items():
            if isinstance(rule_config, dict) and rule_config.get("enabled", False):
                prompt_template = rule_config.get("prompt_template", "")
                if prompt_template:
                    prompt = prompt_template.replace("{code_snippet}", text)
                    try:
                        response = model.generate_content(prompt)
                        print(f"Response for {rule_name}: {response.text}")
                        if "FAIL" in response.text:
                            issues.append(AnalysisIssue(
                                message=f"AI Slop detected by {rule_name}: {response.text}",
                                severity="warning"
                            ))
                    except Exception as e:
                        print(f"Error analyzing with {rule_name}: {str(e)}")

        prompt = f"Analyze this code for AI slop:\n{text}"
        try:
            response = model.generate_content(prompt)
            summary = response.text
            print("Gemini Response:", summary) 
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise ValueError(f"Gemini API request failed: {e}")

        return AIAnalysisResult(summary=summary, issues=issues)
