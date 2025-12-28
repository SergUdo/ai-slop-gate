# ai-slop-gate — Architecture

## Purpose

This document describes the architectural principles, boundaries, and staged evolution
of ai-slop-gate.

The primary goal is to build a vendor-agnostic, CI-platform-agnostic, extensible
tool for detecting low-quality AI-generated code ("AI slop"), security issues,
and policy violations in pull/merge requests.

---

## Core Architectural Principles

### 1. Clean Separation of Concerns

The system is explicitly split into four independent layers:

Adapters -> Engine -> Providers -> Reporters

Each layer has a single responsibility and must not leak abstractions across boundaries.

---

### 2. Adapter vs Provider (Critical Distinction)

A common architectural mistake is mixing code source with analysis engines.
ai-slop-gate explicitly avoids this.

Adapter:
- Knows where code comes from
- Fetches PR/MR diffs and metadata
- Talks to GitHub / GitLab / Bitbucket APIs
- Does NOT analyze code
- Does NOT know which AI model is used

Provider:
- Knows how code is analyzed
- Wraps an AI model or analysis backend
- Produces structured analysis results
- Does NOT know where code came from
- Does NOT talk to GitHub / GitLab directly

---

### 3. Why There Is No GitHub Copilot Adapter

GitHub Copilot is not a code source.

Copilot:
- does not provide PR diffs
- does not represent a CI trigger
- does not own repository state

Therefore:
- There is no Copilot adapter
- Copilot is implemented as a Provider

This avoids vendor lock-in and CI coupling.

---

## High-Level Architecture

Flow:

Developer pushes code
-> Adapter fetches changes
-> Engine orchestrates analysis
-> Providers analyze code
-> Reporter emits results

---

## Staged Development Plan

### Stage 1 — MVP (Current)

Goal:
Stabilize architecture and contracts.

Included:
- CLI entrypoint
- Core Engine
- GitHub Adapter (read-only PR analysis)
- Deterministic / stub AI Providers
- Advisory vs Blocking mode via policy.yaml
- Console Reporter
- Fixed contracts (AnalysisInput, AnalysisResult)

Explicitly not included:
- No real AI network calls
- No Copilot integration
- No paid APIs

This stage answers:
Is the architecture correct and extensible?

---

### Stage 2 — Fast & Free AI Providers

Goal:
Add practical AI analysis without cost barriers.

Planned:
- Groq Provider (Llama, Mixtral)
- OpenRouter Provider (free-tier models)
- Provider selection via policy

No architecture changes required.

---

### Stage 3 — Copilot & IDE-Adjacent Providers

Goal:
Integrate developer-native tools.

Planned:
- GitHub Copilot Provider
- Optional local execution modes

Copilot remains a Provider, not an Adapter.

---

### Stage 4 — Advanced Policy & Trust Scoring

Goal:
Move from warnings to trust signals.

Planned:
- Provider weighting
- Confidence scoring
- Cross-provider consensus
- Historical trend analysis

---

## Policy-Driven Behavior

All enforcement behavior is controlled via policy.yaml.

Supported concepts:
- Advisory mode (non-blocking)
- Blocking mode (fail pipeline)
- Severity thresholds
- Provider allow/deny lists

The engine must remain deterministic, explainable, and auditable.

---

## Non-Goals

Out of scope:
- IDE plugins
- Code generation
- Automatic code fixing
- Vendor-specific CI logic

---

## Summary

ai-slop-gate is designed to be:
- OSS-author friendly
- Vendor-agnostic
- CI-platform-agnostic
- Extensible without refactors

Architectural purity in early stages is a feature, not a delay.
