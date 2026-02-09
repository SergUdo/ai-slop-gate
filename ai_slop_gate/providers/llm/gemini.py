import os
import json
import time
import logging
import google.generativeai as genai
from github import Github

from ai_slop_gate.providers.llm.llm_provider import LlmProvider
from ai_slop_gate.providers.base import ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class GeminiProvider(LlmProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.name = "gemini"
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # Load PR diff using GitHub API, then analyze with Gemini. This avoids sending large diffs through CLI args and allows us to focus on changed code.
        try:
            gh = Github(token)
            repository = gh.get_repo(repo)
            pr = repository.get_pull(int(pr_id))
            
            diff_parts = []
            for file in pr.get_files():
                if file.patch and len(file.patch) < 20000:
                    diff_parts.append(f"--- File: {file.filename} ---\n{file.patch}")
            
            diff_content = "\n\n".join(diff_parts)
            return self.analyze(diff_content, input_file=f"PR_{pr_id}")
        except Exception as e:
            return ProviderObservation(self.name, self.model, [], str(e))

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        try:
            system_instruction = self._load_prompt("gemini", "deep")
        except FileNotFoundError as e:
            return ProviderObservation(self.name, self.model, [], str(e))

        prompt = f"{system_instruction}\n\nINPUT CONTENT (logical name: {input_file}):\n{code}"

        for attempt in range(2):
            try:
                response = self._model.generate_content(prompt)
                if not response or not response.text: continue

                raw_text = response.text.strip()
                clean_json = raw_text
                if "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].replace("json", "").strip()

                data = json.loads(clean_json)
                if not isinstance(data, list): data = [data]

                obs = [
                    make_observation(
                        provider=self.name,
                        category=d.get("category", "quality"),
                        signal=d.get("signal", "slop_detected"),
                        confidence=float(d.get("confidence", 0.7)),
                        severity=d.get("severity", "medium"),
                        message=d.get("message", "Potential issue found"),
                        evidence={"file": input_file or d.get("file", "unknown"), "line": d.get("line", 1)},
                    ) for d in data
                ]
                return ProviderObservation(self.name, self.model, obs, raw_text)
            except Exception as e:
                if attempt == 0: time.sleep(2); continue
                return ProviderObservation(self.name, self.model, [], str(e))
        return ProviderObservation(self.name, self.model, [], "Max retries reached")
    