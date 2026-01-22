# ai_slop_gate/providers/gemini.py
import os
import json
import time
import google.generativeai as genai
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

load_dotenv()

class GeminiProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.name = "gemini"
        self.kind = "llm"
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def collect(self, content: str = "", input_file: str = "") -> ProviderObservation:
        return self.analyze(content, input_file)

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        if not code and not input_file:
            return ProviderObservation(
                provider=self.name,
                model=self.model,
                observations=[],
                raw_text="Empty input provided",
            )

        if input_file:
            try:
                file_path = Path(input_file)
                if file_path.is_file():
                    code = file_path.read_text()
                elif file_path.is_dir():
                    code = ""
                    for py_file in file_path.rglob("*.py"):
                        code += f"\n\n# File: {py_file}\n\n"
                        code += py_file.read_text()
            except Exception as e:
                return ProviderObservation(
                    provider=self.name,
                    model=self.model,
                    observations=[
                        make_observation(
                            provider=self.name,
                            category="error",
                            signal="file_read_error",
                            message=f"Failed to read file: {str(e)}",
                            confidence=1.0
                        )
                    ],
                    raw_text=str(e),
                )

        if not code or len(code.strip()) == 0:
            return ProviderObservation(
                provider=self.name,
                model=self.model,
                observations=[],
                raw_text="Empty input provided",
            )

        system_instruction = (
            "You are a Senior Code Auditor specialized in identifying 'AI Slop' (generic, low-quality AI generated code).\n"
            "Analyze the code and return a JSON list of observations.\n"
            "Each observation must have: 'category' (quality/hallucination/security), 'signal', 'confidence' (0.0-1.0), "
            "'severity' (low/medium/high), 'message', 'file' (optional), and 'line' (optional).\n"
            "Return ONLY valid JSON."
        )

        prompt = f"{system_instruction}\n\nCode to analyze:\n{code}"

        max_retries = 3
        retry_delay = 30

        for attempt in range(max_retries):
            try:
                response = self._model.generate_content(prompt,generation_config={"max_output_tokens": 2048} )
                raw_text = response.text or ""

                clean_json = raw_text.strip()
                if "```" in clean_json:
                    clean_json = clean_json.split("```")[1].replace("json", "").strip()

                observations_data = json.loads(clean_json)

                final_observations = []
                for obs in observations_data:
                    final_observations.append(
                        make_observation(
                            provider=self.name,
                            category=obs.get("category", "quality"),
                            signal=obs.get("signal", "ai_indicator"),
                            confidence=float(obs.get("confidence", 0.7)),
                            severity=obs.get("severity", "medium"),
                            message=obs.get("message", "No description provided"),
                            evidence={
                                "file": obs.get("file"),
                                "line": obs.get("line")
                            }
                        )
                    )

                return ProviderObservation(
                    provider=self.name,
                    model=self.model,
                    observations=final_observations,
                    raw_text=raw_text,
                )

            except Exception as e:
                error_message = str(e)
                if "429" in error_message and attempt < max_retries - 1:
                    print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                elif "504" in error_message and attempt < max_retries - 1:
                    print(f"Deadline exceeded. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return ProviderObservation(
                        provider=self.name,
                        model=self.model,
                        observations=[
                            make_observation(
                                provider=self.name,
                                category="error",
                                signal="provider_failure",
                                message=f"Failed to parse Gemini response: {error_message}",
                                confidence=1.0
                            )
                        ],
                        raw_text=error_message,
                    )

        return ProviderObservation(
            provider=self.name,
            model=self.model,
            observations=[
                make_observation(
                    provider=self.name,
                    category="error",
                    signal="max_retries_exceeded",
                    message=f"Max retries ({max_retries}) exceeded for Gemini API",
                    confidence=1.0
                )
            ],
            raw_text=f"Max retries ({max_retries}) exceeded",
        )
