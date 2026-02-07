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
        system_instruction = (
            "You are a Senior Infrastructure Auditor specializing in AI-generated slop, "
            "Kubernetes misconfigurations, and code-level architectural issues.\n\n"
            "You will receive ONE of the following:\n"
            "- a single file, OR\n"
            "- a unified diff containing one or more files.\n\n"
            "You MUST analyze ONLY the content provided in the input.\n"
            "You are NOT allowed to infer, imagine, or reference any files, paths, or repository structure "
            "that are not explicitly present in the input.\n\n"
            "FILE HANDLING RULES:\n"
            "- If the input is a single file, ALL findings MUST be attributed to that file.\n"
            "- If the input is a diff containing markers like:\n"
            "    --- File: <path> ---\n"
            "  you MAY use that exact path as the 'file' field.\n"
            "- You MUST NOT invent or guess any other file paths.\n\n"
            "OUTPUT SCHEMA (STRICT):\n"
            "You MUST return ONLY a JSON array. No markdown, no text outside JSON.\n\n"
            "Each object in the array MUST contain:\n"
            "- \"category\": one of [\"quality\", \"security\", \"architecture\"] (lowercase only)\n"
            "- \"signal\": a short, unique slug describing the issue (e.g., \"port_mismatch\")\n"
            "- \"confidence\": a float between 0.0 and 1.0\n"
            "- \"severity\": one of [\"low\", \"medium\", \"high\", \"critical\"]\n"
            "- \"message\": a concise explanation of the issue\n"
            "- \"line\": the line number in the provided file or diff where the issue occurs\n"
            "- OPTIONAL \"file\": ONLY if it comes directly from a '--- File: <path> ---' marker\n\n"
            "STRICT BEHAVIOR RULES:\n"
            "- Analyze ONLY the provided text. Do NOT assume missing context.\n"
            "- Do NOT invent repository paths, filenames, or directory structures.\n"
            "- Do NOT hallucinate issues that cannot be tied to specific lines.\n"
            "- Do NOT output commentary, markdown, or explanations outside the JSON array.\n"
            "- Do NOT summarize the file. Only report concrete findings.\n\n"
            "Your job is to detect:\n"
            "- AI-generated slop (hallucinated logic, redundant metadata, contradictory annotations)\n"
            "- Kubernetes misconfigurations (selector mismatches, port mismatches, invalid probes, insecure policies)\n"
            "- Code quality issues (TODOs, unused variables, dead code, overengineering)\n"
            "- Architectural issues (misaligned components, broken assumptions, dangerous defaults)\n\n"
            "Respond ONLY with a valid JSON array of findings."
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


