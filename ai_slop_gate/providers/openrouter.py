from ..result import AIAnalysisResult, AnalysisIssue
import os
import requests

class OpenRouterProvider:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("LLAMA_API_KEY2")

    def analyze(self, text: str, policy: dict) -> AIAnalysisResult:
        if not self.api_key:
            raise ValueError("LLAMA_API_KEY2 is missing.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/SergUdo/ai-slop-gate",
            "X-Title": "ai-slop-gate" 
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": f"Analyze this code for AI slop:\n{text}"}]
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            if "choices" not in response_data:
                raise ValueError(f"Unexpected API response: {response_data}")

            issues = []
            if "TODO" in text:
                issues.append(AnalysisIssue(message="Found TODO in code", severity="warning"))

            return AIAnalysisResult(
                summary=response_data["choices"][0]["message"]["content"],
                issues=issues
            )
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Response: {response.text if 'response' in locals() else 'No response'}")
            raise ValueError(f"API request failed: {e}")

