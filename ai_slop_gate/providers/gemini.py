import os
import json
import google.generativeai as genai
from typing import List, Optional

from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class GeminiProvider:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def collect(self, content: str = "") -> ProviderObservation:
        """
        Interface method for the provider registry.
        Redirects to analyze method.
        """
        return self.analyze(content)

    def analyze(self, code: str) -> ProviderObservation:
        # Avoid calling API with empty content
        if not code or len(code.strip()) == 0:
            return ProviderObservation(
                provider="gemini",
                model=self.model,
                observations=[],
                raw_text="Empty input provided",
            )

        system_instruction = (
            "You are a Senior Code Auditor specialized in identifying 'AI Slop' (generic, low-quality AI generated code).\n"
            "Analyze the code and return a JSON list of observations.\n"
            "Each observation must have: 'category' (quality/hallucination/security), 'signal', 'confidence' (0.0-1.0), "
            "'severity' (low/medium/high), and 'message'.\n"
            "Return ONLY valid JSON."
        )

        prompt = f"{system_instruction}\n\nCode to analyze:\n{code}"
        
        try:
            response = self._model.generate_content(prompt)
            raw_text = response.text or ""
            
            clean_json = raw_text.strip()
            if "```" in clean_json:
                clean_json = clean_json.split("```")[1].replace("json", "").strip()

            observations_data = json.loads(clean_json)
            
            final_observations = []
            for obs in observations_data:
                final_observations.append(
                    make_observation(
                        provider="gemini",
                        category=obs.get("category", "quality"),
                        signal=obs.get("signal", "ai_indicator"),
                        confidence=float(obs.get("confidence", 0.7)),
                        severity=obs.get("severity", "medium"),
                        message=obs.get("message", "No description provided"),
                    )
                )

            return ProviderObservation(
                provider="gemini",
                model=self.model,
                observations=final_observations,
                raw_text=raw_text,
            )

        except Exception as e:
            return ProviderObservation(
                provider="gemini",
                model=self.model,
                observations=[
                    make_observation(
                        provider="gemini",
                        category="error",
                        signal="provider_failure",
                        message=f"Failed to parse Gemini response: {str(e)}",
                        confidence=1.0
                    )
                ],
                raw_text=str(e),
            )
        