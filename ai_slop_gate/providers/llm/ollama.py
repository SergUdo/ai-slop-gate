import os
import json
import time
import logging
import requests
from typing import List

from ai_slop_gate.providers.llm.llm_provider import LlmProvider
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class OllamaProvider(LlmProvider):
    def __init__(self, model: str = "qwen2.5-coder:1.5b", host: str | None = None):
        super().__init__()
        self.name = "ollama"
        self.model = model
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.url = f"{self.host}/api/generate"

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        try:
            system_instruction = self._load_prompt("ollama", "qwen") 
        except FileNotFoundError as e:
            return ProviderObservation(self.name, self.model, [], str(e))

        prompt = f"{system_instruction}\n\n### INPUT CONTENT:\n{code}\n\n### OUTPUT (JSON ONLY):"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
                "num_predict": 8192,
            }
        }

        for attempt in range(3):
            try:
                response = requests.post(self.url, json=payload, timeout=300)
                response.raise_for_status()
                
                result = response.json()
                raw_text = result.get("response", "").strip()

                # Clean and parse JSON, after ensuring it's in the expected format
                clean_json = raw_text
                if "```" in clean_json:
                    parts = clean_json.split("```")
                    for part in parts:
                        if part.strip().startswith("json") or part.strip().startswith("["):
                            clean_json = part.replace("json", "").strip()
                            break

                # Parse JSON
                data = json.loads(clean_json)
                if not isinstance(data, list): 
                    data = [data]

                # Filter out generic messages and create observations
                obs = []
                for d in data:
                    msg = d.get("message", "")
                    if "Potential issue found" in msg and len(msg) < 30:
                        logger.warning(f"⚠️ Skipping generic message: {msg}")
                        continue
                    
                    obs.append(
                        make_observation(
                            provider=self.name,
                            category=d.get("category", "quality"),
                            signal=d.get("signal", "slop_detected"),
                            confidence=float(d.get("confidence", 0.7)),
                            severity=d.get("severity", "medium"),
                            message=msg,
                            evidence={
                                "file": d.get("file") or input_file or "unknown",
                                "line": d.get("line", 1)
                            },
                        )
                    )
                
                return ProviderObservation(self.name, self.model, obs, raw_text)

            except json.JSONDecodeError as e:
                logger.warning(f"❌ Ollama failed to parse JSON (attempt {attempt+1}): {raw_text[:200]}")
                if attempt == 2:
                    return ProviderObservation(self.name, self.model, [], f"JSON parse error: {e}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Ollama attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
                    continue
                return ProviderObservation(self.name, self.model, [], str(e))
        
        return ProviderObservation(self.name, self.model, [], "Max retries reached")

    def collect(self, base_path: str = ".") -> ProviderObservation:
        return ProviderObservation(self.name, self.model, [], "Use analyze() for LLM providers")