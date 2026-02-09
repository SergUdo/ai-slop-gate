import os
import json
import time
import logging
import requests
from typing import List, Optional

from ai_slop_gate.providers.llm.llm_provider import LlmProvider
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class GroqProvider(LlmProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.name = "groq"
        self.model = model
        self.api_key = api_key or os.getenv("SLOPE_GATE_GROQ")

        if not self.api_key:
            raise ValueError("SLOPE_GATE_GROQ is missing. Please set it in .env or environment variables.")

        if any(self.model.startswith(x) for x in ["llama", "mixtral"]):
            self.url = "https://api.groq.com/openai/v1/chat/completions"
        else:
            self.url = "https://api.groq.com/v1/chat/completions"

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        """Analyze a GitHub Pull Request."""
        from github import Github
        logger.info(f"GroqProvider: Analyzing PR {repo}#{pr_id}")

        try:
            gh = Github(token)
            repository = gh.get_repo(repo)
            pr = repository.get_pull(int(pr_id))

            diff_parts: List[str] = []
            total_chars = 0

            for file in pr.get_files():
                if not file.patch or len(file.patch) > 20000:
                    continue
                diff_parts.append(f"--- File: {file.filename} ---\n{file.patch}")
                total_chars += len(file.patch)
                if total_chars > 30000: break

            diff_content = "\n\n".join(diff_parts)
            if not diff_content:
                return ProviderObservation(self.name, self.model, [], "No changes to analyze.")

            return self.analyze(diff_content, input_file=f"PR_{pr_id}")

        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ProviderObservation(self.name, self.model, [], str(e))

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """Analyze code content using Groq API with retries and robust JSON parsing."""
        try:
            system_instruction = self._load_prompt("groq", "deep")
        except FileNotFoundError as e:
            logger.error(f"Prompt loading failed: {e}")
            return ProviderObservation(self.name, self.model, [], f"Error: {str(e)}")

        prompt = f"{system_instruction}\n\nINPUT CONTENT (logical name: {input_file}):\n{code}"

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                strict_json = (attempt == max_attempts - 1)
                response = self._call_groq_api(prompt, strict_json=strict_json)
                
                if not response or not response.get('text'):
                    continue

                raw_text = response['text'].strip()
                clean_json = raw_text
                
                if "```" in clean_json:
                    try:
                        if "```json" in clean_json:
                            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                        else:
                            clean_json = clean_json.split("```")[1].split("```")[0].strip()
                    except IndexError:
                        pass

                data = json.loads(clean_json)
                if not isinstance(data, list):
                    data = [data]

                obs = [
                    make_observation(
                        provider=self.name,
                        category=d.get("category", "quality"),
                        signal=d.get("signal", "slop_detected"),
                        confidence=float(d.get("confidence", 0.7)),
                        severity=d.get("severity", "medium"),
                        message=d.get("message", "Potential issue found"),
                        evidence={
                            "file": input_file or d.get("file") or "unknown",
                            "line": d.get("line", 1),
                        },
                    ) for d in data
                ]

                return ProviderObservation(self.name, self.model, obs, raw_text)

            except json.JSONDecodeError:
                logger.warning(f"Attempt {attempt+1}: Failed to parse JSON from Groq.")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}: Groq analysis failed: {e}")
                time.sleep(2 * (attempt + 1))

        return ProviderObservation(self.name, self.model, [], "Max retries reached or Rate Limit exceeded.")

    def _call_groq_api(self, prompt: str, strict_json: bool = False) -> dict | None:
        """Call the Groq API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "You are a strict code auditor. Return ONLY a valid JSON array."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }

        if strict_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=45)
            
            if resp.status_code == 429:
                # Rate Limit handlingwith respect to Groq's guidance
                retry_after = resp.headers.get("retry-after", "2")
                logger.warning(f"Groq Rate Limit (429). Waiting {retry_after}s...")
                time.sleep(float(retry_after))
                return None

            resp.raise_for_status()
            result = resp.json()

            # Correctly extract content from response
            if result.get('choices') and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return {'text': content}
            
            logger.error("Groq returned empty choices.")
            return None

        except Exception as e:
            logger.error(f"Groq API Request Error: {e}")
            return None