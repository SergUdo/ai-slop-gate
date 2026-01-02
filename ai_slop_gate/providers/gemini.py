import os
import google.generativeai as genai
from typing import List

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

    def analyze(self, code: str) -> ProviderObservation:
        observations = []

        if "TODO" in code:
            observations.append(
                make_observation(
                    provider="gemini",
                    category="quality",
                    signal="todo",
                    confidence=0.8,
                    message="Code contains TODO comments",
                )
            )

        if "FIXME" in code:
            observations.append(
                make_observation(
                    provider="gemini",
                    category="quality",
                    signal="fixme",
                    confidence=0.8,
                    message="Code contains FIXME comments",
                )
            )

        prompt = (
            "Analyze the following code and point out potential AI-generated issues.\n\n"
            f"{code}"
        )

        response = self._model.generate_content(prompt)
        raw_text = response.text or ""

        if any(word in raw_text.lower() for word in ["hallucination", "incorrect", "nonsensical"]):
            observations.append(
                make_observation(
                    provider="gemini",
                    category="hallucination",
                    signal="llm_warning",
                    confidence=0.6,
                    message=raw_text.strip(),
                )
            )
        else:
            observations.append(
                make_observation(
                    provider="gemini",
                    category="quality",
                    signal="neutral",
                    confidence=0.4,
                    message=raw_text.strip(),
                )
            )

        return ProviderObservation(
            provider="gemini",
            model=self.model,
            observations=observations,
            raw_text=raw_text,
        )
