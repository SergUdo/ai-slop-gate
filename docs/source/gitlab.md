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

### Optional (for LLM providers)
Set GitLab CI/CD variables:

- `SLOPE_GATE_GROQ`
- `GEMINI_API_KEY`

LLM jobs will run only if at least one of these variables is present.

---

## 3. Example `.gitlab-ci.yml`

Below is the recommended configuration for GitLab CI:

```yaml
stages:
  - ai_slop_gate_static
  - ai_slop_gate_llm
  - ai_slop_gate_full

variables:
  DOCKER_IMAGE: "ghcr.io/sergiudo/ai-slop-gate:latest"
  WORKSPACE: "/workspace"

# -----------------------------
# STATIC ANALYSIS JOB
# -----------------------------
ai_slop_gate_static:
  stage: ai_slop_gate_static
  image: docker:latest
  services:
    - docker:dind
  script:
    - echo "Running AI Slop Gate (static providers only)"
    - docker run --rm \
        -v "$CI_PROJECT_DIR:$WORKSPACE" \
        "$DOCKER_IMAGE" \
        run \
          --path "$WORKSPACE" \
          --policy "$WORKSPACE/policy.yml" \
          --provider static \
          --fail-on blocking
  allow_failure: false

# -----------------------------
# LLM ANALYSIS JOB (Groq + Gemini)
# -----------------------------
ai_slop_gate_llm:
  stage: ai_slop_gate_llm
  image: docker:latest
  services:
    - docker:dind
  script:
    - echo "Running AI Slop Gate (LLM providers)"
    - docker run --rm \
        -e GEMINI_API_KEY="$GEMINI_API_KEY" \
        -e SLOPE_GATE_GROQ="$SLOPE_GATE_GROQ" \
        -v "$CI_PROJECT_DIR:$WORKSPACE" \
        "$DOCKER_IMAGE" \
        run \
          --path "$WORKSPACE" \
          --policy "$WORKSPACE/policy.yml" \
          --provider groq \
          --provider gemini \
          --fail-on blocking
  rules:
    - if: '$GEMINI_API_KEY || $SLOPE_GATE_GROQ'
      when: on_success
    - when: never
  allow_failure: false

# -----------------------------
# FULL ANALYSIS JOB (static + llm + compliance)
# -----------------------------
ai_slop_gate_full:
  stage: ai_slop_gate_full
  image: docker:latest
  services:
    - docker:dind
  script:
    - echo "Running AI Slop Gate (full providers)"
    - docker run --rm \
        -e GEMINI_API_KEY="$GEMINI_API_KEY" \
        -e SLOPE_GATE_GROQ="$SLOPE_GATE_GROQ" \
        -v "$CI_PROJECT_DIR:$WORKSPACE" \
        "$DOCKER_IMAGE" \
        run \
          --path "$WORKSPACE" \
          --policy "$WORKSPACE/policy.yml" \
          --provider static \
          --provider groq \
          --provider gemini \
          --provider compliance \
          --fail-on blocking
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success
    - when: never
  allow_failure: false
  ```

---

## 4. Running Different Types of Analysis

### Static analysis (always runs)
No environment variables required.

Runs automatically via:

```bash
ai_slop_gate_static
```

### LLM analysis (Groq + Gemini)

Requires at least one variable:

`SLOPE_GATE_GROQ`

`GEMINI_API_KEY`

Runs automatically via:

```bash
ai_slop_gate_llm
```


