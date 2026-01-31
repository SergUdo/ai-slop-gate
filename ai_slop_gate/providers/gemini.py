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

    # -------------------------------------------------------------------------
    # PR ANALYSIS: працює з реальним diff з GitHub
    # -------------------------------------------------------------------------
    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        """
        Fetches the PR diff and sends it for analysis.
        """
        logger.info(f"GeminiProvider: Analyzing PR {repo}#{pr_id}")

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

            logger.info(f"Sending {len(diff_content)} chars of diff to Gemini...")
            # Тут ми явно кажемо: це PR, а не локальний код
            return self.analyze(diff_content, input_file=f"PR_{pr_id}")

        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ProviderObservation(self.name, self.model, [], str(e))

    # -------------------------------------------------------------------------
    # CORE ANALYSIS: аналізує ТІЛЬКИ те, що ти передав у `code`
    # -------------------------------------------------------------------------
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        """
        Core analysis logic with refined prompting for descriptive signals.

        ВАЖЛИВО:
        - Аналізує ТІЛЬКИ переданий `code`.
        - НЕ сканує репозиторій.
        - НЕ має права вигадувати інші file‑paths.
        - УСІ findings прив’язуються до `input_file`.
        """
        system_instruction = (
            "You are a Senior Infrastructure Auditor specializing in 'AI Slop' and K8s misconfigurations.\n"
            "You will be given EITHER:\n"
            "- a single file, OR\n"
            "- a unified diff for one or more files.\n\n"
            "You MUST analyze ONLY the provided content. You are NOT allowed to invent or assume other files.\n"
            "If the input represents a single file, treat ALL findings as belonging to that file.\n"
            "If the input is a diff with '--- File: <path> ---' markers, you MAY use that exact path as 'file'.\n\n"
            "SCHEMA REQUIREMENTS:\n"
            "- 'category': 'quality', 'security', or 'architecture'.\n"
            "- 'signal': A short, unique slug (e.g., 'port_mismatch', 'resource_limit_mismatch'). NOT just 'ai_slop'.\n"
            "- 'confidence': 0.0 to 1.0.\n"
            "- 'severity': 'low', 'medium', 'high', 'critical'.\n"
            "- 'message': A concise explanation of the issue.\n"
            "- 'line': The line number in the diff or file where the issue occurs.\n"
            "- OPTIONAL 'file': ONLY if it comes directly from a '--- File: <path> ---' marker in the input.\n\n"
            "IMPORTANT:\n"
            "- Respond ONLY with a valid JSON array. No markdown, no conversational text.\n"
            "- Use only lowercase for 'category' (e.g., 'architecture', 'security').\n"
            "- Do NOT invent repository paths like './scripts/test_pr_reporter.py' if they are not present in the input.\n"
        )

        prompt = f"{system_instruction}\n\nINPUT CONTENT (file or diff, logical name: {input_file}):\n{code}"

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
                    # КРИТИЧНА ЗМІНА:
                    # Ми БІЛЬШЕ НЕ ДОВІРЯЄМО d["file"] від моделі.
                    # Усі findings жорстко прив’язуємо до input_file.
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
                logger.warning(f"Attempt {attempt+1} failed to parse or reach Gemini: {e}")
                if attempt < 1:
                    time.sleep(2)
                    continue
                return ProviderObservation(self.name, self.model, [], f"Error: {str(e)}")

        return ProviderObservation(self.name, self.model, [], "Max retries reached.")

    # -------------------------------------------------------------------------
    # LOCAL FALLBACK: якщо хтось викличе collect() напряму
    # -------------------------------------------------------------------------
    def collect(self) -> ProviderObservation:
        return ProviderObservation(
            provider=self.name,
            model=self.model,
            observations=[],
            raw_text="LLM provider does not support collect(). Use analyze_pr() or analyze()."
        )


