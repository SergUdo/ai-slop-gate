import os
import google.generativeai as genai
from typing import List

from ai_slop_gate.domain.observation import Observation
from ai_slop_gate.providers.base import ProviderObservation


class GeminiProvider:
    """
    Stage 2.2 provider
    Emits observations only.
    No decisions. No policy awareness.
    """

    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def analyze(self, code: str) -> ProviderObservation:
        """
        Analyze code and return structured observations.
        """

        observations: List[Observation] = []

        # ---- deterministic signals (cheap, offline-friendly)
        if "TODO" in code:
            observations.append(
                Observation(
                    category="quality",
                    signal="negative",
                    confidence=0.8,
                    message="Code contains TODO comments",
                    evidence={"file": None, "line": None},
                )
            )

        if "FIXME" in code:
            observations.append(
                Observation(
                    category="quality",
                    signal="negative",
                    confidence=0.8,
                    message="Code contains FIXME comments",
                    evidence={"file": None, "line": None},
                )
            )

        # ---- LLM-based observation
        prompt = (
            "Analyze the following code and point out potential AI-generated issues, "
            "such as generic patterns, hallucinated logic, or low-quality constructs. "
            "Do NOT make any pass/fail decision.\n\n"
            f"{code}"
        )

        try:
            response = self._model.generate_content(prompt)
            raw_text = response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}")

        # ---- minimal heuristic parser (TEMPORARY)
        if any(word in raw_text.lower() for word in ["hallucination", "incorrect", "nonsensical"]):
            observations.append(
                Observation(
                    category="hallucination",
                    signal="negative",
                    confidence=0.6,
                    message=raw_text.strip(),
                    evidence={"file": None, "line": None},
                )
            )
        else:
            observations.append(
                Observation(
                    category="quality",
                    signal="neutral",
                    confidence=0.4,
                    message=raw_text.strip(),
                    evidence={"file": None, "line": None},
                )
            )

        return ProviderObservation(
            provider="gemini",
            model=self.model,
            observations=observations,
            raw_text=raw_text,
        )
