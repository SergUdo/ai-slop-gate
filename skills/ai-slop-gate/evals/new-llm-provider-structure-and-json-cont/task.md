# Add Mistral LLM Provider to ai-slop-gate

## Problem/Feature Description

Your team is extending the ai-slop-gate CI/CD analysis tool to support Mistral AI as a new code review backend. A growing number of enterprise customers use Mistral's API for compliance reasons, and they want ai-slop-gate to call Mistral's endpoint when scanning pull requests for AI-generated slop and security issues.

You have been asked to scaffold the new Mistral provider. The codebase follows strict conventions around how providers are structured, what interfaces they must implement, and what format the LLM prompt must produce. The compliance team also needs the provider to support PR-level analysis (not just file-level analysis). You should write the provider implementation and its prompt file, register it in the provider registry, and add the necessary CLI option — following the existing patterns in the codebase.

Do not set up a working Mistral API key or run the code against the real API. Your job is to produce a correct, well-structured implementation stub that fits the project's conventions. Write the code so that a reviewer can inspect it and verify it follows the project standards.

## Output Specification

Produce the following files (paths relative to your working directory):

- `ai_slop_gate/providers/llm/mistral.py` — the provider implementation
- `ai_slop_gate/providers/llm/prompts/mistral/deep.prompt` — the prompt template for Mistral
- `ai_slop_gate/providers/registry_patch.py` — a short code snippet (not a full registry rewrite) that shows how to register the new provider and wire the CLI option, with inline comments explaining each step
- `implementation_notes.md` — a brief document summarising the design decisions made, including the class hierarchy used, the interface methods implemented, and the JSON contract the prompt enforces

## Input Files

The following skeleton is provided to help you understand the existing patterns. Extract these files before beginning.

=============== FILE: ai_slop_gate/providers/llm/groq.py ===============
# Existing Groq provider — use this as a reference for the pattern
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.providers.llm.base import LlmProvider
from typing import List

class GroqProvider(LlmProvider):
    name = "groq"
    kind = "llm"

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        # calls Groq API, parses JSON response
        ...

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # PR-level analysis via Groq
        ...
=============== END FILE ===============

=============== FILE: ai_slop_gate/providers/base.py ===============
from dataclasses import dataclass
from typing import List, Any, Optional, Dict

@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    model: str
    observations: List[Any]
    raw_text: str

class BaseProvider:
    name: str
    kind: str  # "llm" | "static" | "infra"

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation: ...
    def collect(self, base_path: str = ".") -> ProviderObservation: ...
    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        raise NotImplementedError
=============== END FILE ===============
