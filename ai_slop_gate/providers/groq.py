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

        prompt = f"""
        Analyze the following code for 'AI slop' (low-quality AI-generated patterns,
        excessive TODOs, or poor justifications).
        "Focus on specific architectural flaws. Instead of 'Lack of input validation',
        focus on the actual problem, and point out what exactly can crash. If you find AI slop,
        explain why it looks like slop (e.g., 'over-commenting obvious logic'

        Return the results ONLY as a valid JSON list of objects with these fields:
        - category: (e.g., "code_quality", "technical_debt")
        - signal: (short description of the issue)
        - confidence: (a float between 0 and 1)
        - severity: (e.g., "high", "medium", "low")
        - message: (detailed description of the issue)
        - location: (file location or code snippet)
        - evidence: (optional, additional context)

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