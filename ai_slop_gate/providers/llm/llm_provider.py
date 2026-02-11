import logging
import time
import random
import os
from pathlib import Path
from abc import abstractmethod
from typing import List, Any
import ai_slop_gate
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
        """Chunks a directory and sends it to the LLM."""
        repo_path = Path(path)
        logger.info(f"LLM Provider: Scanning local path {repo_path}")

        all_observations = []
        current_chunk = ""
        
        ignore_dirs = {".git", "node_modules", "venv", "__pycache__", ".idea", ".venv", "dist", "build"}

        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part in file_path.parts for part in ignore_dirs):
                continue

            try:
                # Limit to certain file types to avoid sending large binaries or irrelevant files to the LLM
                if file_path.suffix.lower() not in ['.py', '.js', '.ts', '.yaml', '.yml', '.dockerfile', '.md', '.txt', '.prompt']:
                    continue

                content = file_path.read_text(encoding="utf-8")
                rel_path = file_path.relative_to(repo_path)
                entry = f"--- File: {rel_path} ---\n{content}\n\n"

                if len(current_chunk) + len(entry) > self.MAX_CHUNK_SIZE:
                    if current_chunk:
                        res = self.analyze(current_chunk, input_file="local_batch")
                        all_observations.extend(res.observations)
                    current_chunk = entry
                    # Anti-rate limit: sleep a bit between requests to avoid hitting LLM rate limits
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
        """
        Loads a prompt template from the filesystem. 
        Uses absolute path resolution relative to the package root for reliability.
        """
        # Path to the package root (where __init__.py of ai_slop_gate is located)
        package_root = Path(os.path.dirname(ai_slop_gate.__file__))
        
        # Construct the absolute path to the prompt file based on the provider name and prompt name
        prompt_file = package_root / "providers" / "llm" / "prompts" / provider_name / f"{name}.prompt"
        
        if not prompt_file.exists():
            # If the prompt file does not exist, raise an error with a clear message
            raise FileNotFoundError(f"Prompt file missing: {prompt_file.absolute()}")
        
        logger.debug(f"Loading prompt from: {prompt_file}")
        return prompt_file.read_text(encoding="utf-8")