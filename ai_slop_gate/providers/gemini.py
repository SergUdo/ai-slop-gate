import os
import json
import time
import logging
import google.generativeai as genai
from typing import List, Optional
from github import Github

from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

logger = logging.getLogger(__name__)

class GeminiProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.name = "gemini"
        self.kind = "llm"
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set it in .env or environment variables.")

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        """
        Fetches the PR diff and sends it for analysis.
        """
        logger.info(f"GeminiProvider: Analyzing PR {repo}#{pr_id}")
        
        try:
            gh = Github(token)
            repository = gh.get_repo(repo)
            pr = repository.get_pull(int(pr_id))
            
            diff_parts = []
            total_chars = 0
            for file in pr.get_files():
                if file.patch:
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

            logger.info(f"Sending {len(diff_content)} chars of diff to Gemini...")
            return self.analyze(diff_content, input_file=f"PR_{pr_id}")

        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ProviderObservation(self.name, self.model, [], str(e))

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Core analysis logic with refined prompting for descriptive signals.
        """
        system_instruction = (
            "You are a Senior Infrastructure Auditor specializing in 'AI Slop' and K8s misconfigurations.\n"
            "Analyze the provided code diff and return a raw JSON list of objects.\n\n"
            "SCHEMA REQUIREMENTS:\n"
            "- 'category': 'quality', 'security', or 'architecture'.\n"
            "- 'signal': A short, unique slug (e.g., 'port_mismatch', 'resource_limit_mismatch'). NOT just 'ai_slop'.\n"
            "- 'confidence': 0.0 to 1.0.\n"
            "- 'severity': 'low', 'medium', 'high', 'critical'.\n"
            "- 'message': A concise explanation of the issue.\n"
            "- 'line': The line number in the diff where the issue occurs.\n\n"
            "IMPORTANT: Respond ONLY with a valid JSON array. No markdown, no conversational text." \
            "CRITICAL: Use only lowercase for 'category' (e.g., 'architecture', 'security').\n"
            "The 'signal' must be one of: 'service_targetport_mismatch', 'service_deployment_version_mismatch', etc."
        )

        prompt = f"{system_instruction}\n\nDIFF CONTENT:\n{code}"

        for attempt in range(2):
            try:
                response = self._model.generate_content(prompt)
                if not response or not response.text:
                    continue

                raw_text = response.text.strip()
                
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
                    observation = make_observation(
                        provider=self.name,
                        category=d.get("category", "quality"),
                        signal=d.get("signal", "slop_detected"),
                        confidence=float(d.get("confidence", 0.7)),
                        severity=d.get("severity", "medium"),
                        message=d.get("message", "Potential AI slop found"),
                        evidence={
                            "file": d.get("file") or input_file, 
                            "line": d.get("line", 1)
                        }
                    )
                    obs.append(observation)

                return ProviderObservation(self.name, self.model, obs, raw_text)

            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Attempt {attempt+1} failed to parse or reach Gemini: {e}")
                if attempt < 1:
                    time.sleep(2)
                    continue
                return ProviderObservation(self.name, self.model, [], f"Error: {str(e)}")

        return ProviderObservation(self.name, self.model, [], "Max retries reached.")

    def collect(self) -> ProviderObservation:
        """
        Fallback for non-PR or local analysis.
        """
        return self.analyze("", input_file="local_project")