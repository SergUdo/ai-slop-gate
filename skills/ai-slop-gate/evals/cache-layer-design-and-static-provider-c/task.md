# Add a Dead Link Detector Static Provider and Review Cache Behaviour

## Problem/Feature Description

The security team at a fintech firm uses ai-slop-gate to scan their repositories before merging. They want a new static provider that detects dead or broken hyperlinks in Python source files (links inside comments and docstrings that return HTTP 4xx/5xx when fetched). This is a purely static analysis concern — no LLM calls are needed.

At the same time, a new engineer on the team has proposed modifying the cache layer so that it caches results for all providers (including static ones) to speed up repeat runs. You have been asked to: (1) scaffold the new static "dead link" provider following project conventions, and (2) write a design document explaining whether the proposed caching change is appropriate and how the cache key scheme works.

You should also write unit tests for the new provider. The implementation does not need to actually make HTTP requests — a stub or mock-based implementation is fine. The goal is to demonstrate correct structure, placement, and test strategy.

## Output Specification

Produce the following files:

- `ai_slop_gate/providers/static/dead_link.py` — the static provider implementation
- `tests/unit/providers/test_dead_link.py` — unit tests covering at least a positive case (detects a dead link) and a negative case (clean code with no links)
- `cache_design_review.md` — a document (300–500 words) explaining the correct cache design: which provider kinds should be wrapped by CachedProvider, what fields compose the cache key, why static providers should or should not be cached, and whether the engineer's proposal is appropriate

## Input Files

The following reference is provided. Extract before beginning.

=============== FILE: ai_slop_gate/providers/static/example_static.py ===============
# Minimal example of an existing static provider for reference
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation, Observation
from typing import List

class ExampleStaticProvider(BaseProvider):
    name = "example_static"
    kind = "static"

    def collect(self, base_path: str = ".") -> ProviderObservation:
        observations: List[Observation] = []
        # ... scan files under base_path ...
        return ProviderObservation(
            provider=self.name,
            model="",
            observations=observations,
            raw_text=""
        )
=============== END FILE ===============
