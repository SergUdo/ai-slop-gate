# GitLab CI Integration Guide

This document explains how to integrate **AI Slop Gate** into GitLab CI/CD pipelines, how to configure providers, and how to run different types of analysis inside private GitLab repositories.

---

## 1. Overview

AI Slop Gate supports four analysis providers:

- **static** — full static analysis (secrets, eval, Dockerfile, PII, TODO, supply‑chain)
- **groq** — LLM analysis (local full‑repo mode)
- **gemini** — LLM analysis (local full‑repo mode)
- **compliance** — GDPR, EU residency, license, supply‑chain compliance

GitLab CI runs AI Slop Gate using the official Docker image:

`ghcr.io/sergiudo/ai-slop-gate:latest`


---

## 2. Requirements

### Mandatory
- A `policy.yml` file in the root of your GitLab repository.
- A `.gitlab-ci.yml` file that invokes the Docker image.

**Policy Override**
You can override the default policy file using the `--policy` flag. This is particularly useful for monorepos or different environment stages (e.g., `audit-only.yml` vs `strict-production.yml`)

### Optional (for LLM providers)
Set GitLab CI/CD variables:

- `SLOPE_GATE_GROQ`
- `GEMINI_API_KEY`

LLM jobs will run only if at least one of these variables is present.

---

## 3. Example `.gitlab-ci.yml`

Below is the recommended configuration for GitLab CI:

```yaml
variables:
  SLOP_PROVIDERS: "gemini" 
  GEMINI_API_KEY: $GEMINI_API_KEY 
  SLOPE_GATE_GROQ: $SLOPE_GATE_GROQ

include:
  - remote: 'https://raw.githubusercontent.com/sergudo/ai-slop-gate/main/ci/gate-template.yml'
```
