import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import List

from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.name = "groq"
        self.kind = "llm"
        self.model = model
        self.api_key = api_key or os.getenv("SLOPE_GATE_GROQ")

        if not self.api_key:
            raise ValueError("SLOPE_GATE_GROQ is missing. Please set it in .env or environment variables.")

        if any(self.model.startswith(x) for x in ["llama", "mixtral"]):
             self.url = "https://api.groq.com/openai/v1/chat/completions"
        else:
            self.url = "https://api.groq.com/v1/chat/completions"

    # -------------------------------------------------------------------------
    # HELPER: Load prompt from external file
    # -------------------------------------------------------------------------
    def _load_prompt(self, name: str) -> str:
        """
        Load a system prompt from prompts/groq/{name}.prompt
        
        Args:
            name: prompt name (e.g., 'deep' for 'deep.prompt')
            
        Returns:
            The prompt text as a string.
            
        Raises:
            FileNotFoundError: if the prompt file does not exist.
        """
        prompt_dir = Path(__file__).parent / "prompts" / "groq"
        prompt_file = prompt_dir / f"{name}.prompt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}\n"
                f"Expected location: ai_slop_gate/providers/llm/prompts/groq/{name}.prompt"
            )
        
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    # -------------------------------------------------------------------------
    # PR ANALYSIS: works with real diff from GitHub
    # -------------------------------------------------------------------------
    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        """
        Fetches the PR diff and sends it for analysis.
        """
        from github import Github
        
        logger.info(f"GroqProvider: Analyzing PR {repo}#{pr_id}")

        try:
            gh = Github(token)
            repository = gh.get_repo(repo)
            pr = repository.get_pull(int(pr_id))

            diff_parts: List[str] = []
            total_chars = 0

            for file in pr.get_files():
                if not file.patch:
                    continue

                # Ignore excessively large files
                if len(file.patch) > 20000:
                    continue

                diff_parts.append(f"--- File: {file.filename} ---\n{file.patch}")
                total_chars += len(file.patch)

                if total_chars > 30000:
                    break

            diff_content = "\n\n".join(diff_parts)
            if not diff_content:
                return ProviderObservation(self.name, self.model, [], "No significant changes to analyze.")

            logger.info(f"Sending {len(diff_content)} chars of diff to Groq...")
            return self.analyze(diff_content, input_file=f"PR_{pr_id}")

        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ProviderObservation(self.name, self.model, [], str(e))

    # -------------------------------------------------------------------------
    # CORE ANALYSIS: analyzes ONLY the provided code
    # -------------------------------------------------------------------------
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Core analysis logic with strict JSON validation and retry logic.

        IMPORTANT:
        - Analyzes ONLY the provided `code`.
        - Does NOT scan the repository.
        - Does NOT make up other file paths.
        - ALL findings are bound to `input_file`.
        """
        try:
            system_instruction = self._load_prompt("deep")
        except FileNotFoundError as e:
            logger.error(f"Failed to load prompt: {e}")
            return ProviderObservation(self.name, self.model, [], f"Error: {str(e)}")

        prompt = f"{system_instruction}\n\nINPUT CONTENT (file or diff, logical name: {input_file}):\n{code}"

        for attempt in range(2):
            try:
                response = self._call_groq_api(prompt, strict_json=(attempt == 1))
                if not response or not response.get('text'):
                    continue

                raw_text = response['text'].strip()

                # Cleanup and parse JSON
                clean_json = raw_text
                if "```" in clean_json:
                    if "```json" in clean_json:
                        clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                    else:
                        clean_json = clean_json.split("```")[1].split("```")[0].strip()

                data = json.loads(clean_json)
                if not isinstance(data, list):
                    data = [data]

                obs = []
                for d in data:
                    # CRITICAL: We do NOT trust model's d["file"].
                    # All findings are strictly bound to input_file.
                    observation = make_observation(
                        provider=self.name,
                        category=d.get("category", "quality"),
                        signal=d.get("signal", "slop_detected"),
                        confidence=float(d.get("confidence", 0.7)),
                        severity=d.get("severity", "medium"),
                        message=d.get("message", "Potential AI slop found"),
                        evidence={
                            "file": input_file or d.get("file") or "unknown",
                            "line": d.get("line", 1),
                        },
                    )
                    obs.append(observation)

                return ProviderObservation(self.name, self.model, obs, raw_text)

            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Attempt {attempt+1} failed to parse or reach Groq: {e}")
                if attempt < 1:
                    time.sleep(2)
                    continue
                return ProviderObservation(self.name, self.model, [], f"Error: {str(e)}")

        return ProviderObservation(self.name, self.model, [], "Max retries reached.")

    # -------------------------------------------------------------------------
    # LOCAL FALLBACK: if someone calls collect() directly
    # -------------------------------------------------------------------------
    def collect(self, base_path: str = ".") -> ProviderObservation:
        return ProviderObservation(
            provider=self.name,
            model=self.model,
            observations=[],
            raw_text="LLM provider does not support collect(). Use analyze_pr() or analyze()."
        )

    # -------------------------------------------------------------------------
    # INTERNAL: Call Groq API with optional strict JSON mode
    # -------------------------------------------------------------------------
    def _call_groq_api(self, prompt: str, strict_json: bool = False) -> dict | None:
        """
        Calls Groq API with retry logic.
        On second attempt (strict_json=True), adds explicit JSON enforcement.
        
        Returns:
            dict with 'text' key if successful, None if failed.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict senior code reviewer looking for AI-generated slop. "
                    "Return ONLY valid JSON. No markdown, no explanations."
                )
            },
            {"role": "user", "content": prompt}
        ]

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }

        # On retry, explicitly enforce JSON output
        if strict_json:
            data["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('choices') and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return {'text': content}
            
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response: {e}")
            return None
