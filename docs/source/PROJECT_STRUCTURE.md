# Project Structure

This document provides an overview of the directory layout of the **ai-slop-gate** project.  
It is intended to help contributors quickly understand where core logic, integrations, rules, and tests are located.

## Directory Overview

ai_slop_gate/
├── adapters/          # Integrations with external systems (GitHub, GitLab, etc.)
├── cache/             # Caching layer and storage helpers
├── cli/               # CLI entry points and subcommands
├── domain/            # Core business logic and compliance engine
│   └── compliance/    # Compliance rules, signals, and evaluation logic
├── engine/            # Core engine components and orchestration
├── fixtures/          # Test fixtures and sample data
│   └── k8s/           # Kubernetes-related fixtures
├── github/            # GitHub-specific API and PR integrations
├── providers/         # AI model providers (Groq, Gemini, Ollama)
│   ├── llm/           # LLM abstraction layer
│   │   └── prompts/   # Prompt templates for each provider
│   └── static/        # Static provider metadata
├── reporters/         # Reporting and PR comment generation
├── rulesets/          # Static rule definitions
│   └── eslint/        # ESLint-based JS/TS safety rules
└── tests/             # Unit and integration tests
    ├── integration/
    └── unit/
        ├── adapters/
        ├── cache/
        ├── cli/
        ├── domain/
        │   └── compliance/
        ├── loader/
        ├── policy_engine/
        ├── profiles/
        ├── providers/
        └── reporters/

## Additional Directories

- **ci/** — Continuous Integration configuration and pipelines  
- **docs/** — Project documentation (Sphinx/MkDocs structure)  
- **scripts/** — Utility scripts for development and automation  

