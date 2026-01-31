import os
import requests
import json
from typing import List, Dict, Any
from ai_slop_gate.domain.observation import Observation

class GroqProvider:
    def __init__(self):
        self.api_key = os.getenv("SLOPE_GATE_GROQ")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"

    def get_observations(self, content: str) -> List[Observation]:
        if not self.api_key:
            print("Warning: SLOPE_GATE_GROQ not set, skipping Groq analysis.")
            return []

        prompt =f"""
        You are NOT a general code reviewer.

        Your task is STRICTLY LIMITED to detecting "AI slop".

        Definition of AI slop:
        - Overly generic or placeholder code.
        - Code that looks correct but lacks real intent or business meaning.
        - Vague TODO comments without actionable detail.
        - Comments that restate obvious logic.
        - Code that appears written to "look right" rather than solve a real problem.
        - Explicit or implicit justification like "AI suggested this" without reasoning.

        DO NOT report:
        - Missing input validation
        - Performance concerns
        - Security issues
        - Naming conventions
        - Style or formatting issues
        - Best practices or refactoring advice

        ONLY report issues that strongly indicate AI-generated low-quality code.

        If no AI slop is detected, return an EMPTY JSON ARRAY [].

        Return ONLY valid JSON.
        Each item MUST contain:
        - category: "quality"
        - signal: short, specific description of the AI slop pattern
        - confidence: float between 0.0 and 1.0
        - severity: "low" | "medium" | "high"
        - message: clear explanation WHY this indicates AI slop

        Code to analyze:
        {content}

        JSON Output:
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a strict senior code reviewer looking for AI-generated slop."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            raw_content = result['choices'][0]['message']['content'].strip()

            if raw_content.startswith("```"):
                raw_content = raw_content.strip("`").replace("json", "", 1).strip()

            observations_data = json.loads(raw_content)

            observations = []
            for i, obs in enumerate(observations_data):
                main_message = obs.get('message', 'No message provided')
                evidence = obs.get('evidence')
                full_message = f"{main_message} | Evidence: {evidence}" if evidence else main_message

                observations.append(
                    Observation(
                        rule_id=f"groq_{i}",
                        category=obs.get('category', 'unknown'),
                        signal=obs.get('signal', 'unknown'),
                        confidence=float(obs.get('confidence', 0.9)),
                        severity=obs.get('severity', 'medium'),
                        message=full_message,
                        location=obs.get('location', 'unknown')
                    )
                )
            return observations

        except Exception as e:
            print(f"Groq API Error: {e}")
            return []