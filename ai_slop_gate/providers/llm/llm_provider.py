import logging
import time
import random
from pathlib import Path
from abc import abstractmethod
from typing import List, Any
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation

logger = logging.getLogger(__name__)

class LlmProvider(BaseProvider):
    kind = "llm"
    MAX_CHUNK_SIZE = 20000  # 20 KB per request

    @abstractmethod
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        pass

    def collect(self, base_path: str = ".") -> ProviderObservation:
        """Create a ProviderObservation."""
        return self.analyze_files(base_path)

    def analyze_files(self, path: str) -> ProviderObservation:
        """Chanks a directory and sends it to the LLM."""
        repo_path = Path(path)
        logger.info(f"LLM Provider: Scanning local path {repo_path}")

        all_observations = []
        current_chunk = ""
        
        ignore_dirs = {".git", "node_modules", "venv", "__pycache__", ".idea"}

        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part in file_path.parts for part in ignore_dirs):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = file_path.relative_to(repo_path)
                # Wrap each file in a simple header to help the LLM understand the structure. This is especially useful for batch processing.
                entry = f"--- File: {rel_path} ---\n{content}\n\n"

                if len(current_chunk) + len(entry) > self.MAX_CHUNK_SIZE:
                    if current_chunk:
                        res = self.analyze(current_chunk, input_file="local_batch")
                        all_observations.extend(res.observations)
                    current_chunk = entry
                    time.sleep(1.5 + random.random())
                else:
                    current_chunk += entry
            except Exception as e:
                logger.warning(f"Skipping file {file_path}: {e}")

        if current_chunk:
            res = self.analyze(current_chunk, input_file="local_batch")
            all_observations.extend(res.observations)

        return ProviderObservation(
            provider=self.name,
            model=getattr(self, "model", "unknown"),
            observations=all_observations,
            raw_text="Batch analysis completed"
        )

    def _load_prompt(self, provider_name: str, name: str) -> str:
        """Load a prompt template from the filesystem based on provider and name. This allows us to keep our prompts organized and easily editable without changing code."""
        prompt_dir = Path(__file__).parent / "prompts" / provider_name
        prompt_file = prompt_dir / f"{name}.prompt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file missing: {prompt_file}")
        
        return prompt_file.read_text(encoding="utf-8")
    