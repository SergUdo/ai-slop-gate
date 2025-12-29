import os
import google.genai as genai
from ..result import AIAnalysisResult, AnalysisIssue

class GeminiProvider:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)

    def analyze(self, text: str, policy: dict) -> AIAnalysisResult:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        model = genai.GenerativeModel(self.model)
        prompt = f"Analyze this code for AI slop:\n{text}"

        try:
            response = model.generate_content(prompt)
            summary = response.text

            issues = []
            if "TODO" in text:
                issues.append(AnalysisIssue(message="Found TODO in code", severity="warning"))

            return AIAnalysisResult(summary=summary, issues=issues)
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise ValueError(f"Gemini API request failed: {e}")
