# ai-slop-gate

**Status: Active Development (Beta)**

*ai-slop-gate is evolving rapidly. While we have implemented robust **DevSecOps gates** (SBOM, License Audit, CVE Scanning), the core AI reasoning logic and APIs are subject to change.*

---

**ai-slop-gate** — Open-source CI/CD tool combining static analysis and multi-LLM (Groq, Gemini, Ollama) code review to detect low-intent AI-generated code.  
Implements deterministic normalization of LLM outputs (severity, confidence, signals) for audit-friendly automated quality gates.

[![Documentation Status](https://readthedocs.org/projects/ai-slop-gate/badge/?version=latest)](https://ai-slop-gate.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Stage](https://img.shields.io/badge/stage-Beta-blue)
![Coverage](https://img.shields.io/badge/coverage-local-blue)
![Docker](https://img.shields.io/badge/docker-GHCR-success)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/SergUdo/ai-slop-gate?sort=semver)
![Cosign Verified](https://img.shields.io/badge/cosign-verified-brightgreen?logo=sigstore)

---

## Documentation

Complete documentation is available at:  
**[ai-slop-gate.readthedocs.io](https://ai-slop-gate.readthedocs.io/)**

### Quick Links
- [Quick Start Guide](docs/source/quick-start.rst)
- [Architecture Overview](docs/source/ARCHITECTURE.md)
- [CLI Reference](docs/source/CLI_REFERENCE.md)
- [Cache Guide](docs/source/CACHE.md)
- [Docker Setup](docs/source/DOCKER.md)
- [CI/CD Integrations](docs/source/INTEGRATIONS.md)
- [Testing Guide](docs/source/TESTING.md)
- [Security Policy](docs/source/SECURITY.md)
- [Release Notes](docs/source/RELEASE.md)

---

## Key Features

### Supply Chain Security  
- Detects forbidden licenses (GPL, AGPL)  
- Identifies AI-hallucinated or suspicious package names  
- Supports NIS2 and EU Cyber Resilience Act readiness
- Assists in technical alignment with **[EU Cyber Resilience Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)** and **[DORA](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554)** supply chain security requirements. 

### GDPR/DSGVO Compliance  
- Enforces EU-only data residency for AI processing  
- Prevents non-compliant LLM routing  
- Produces audit-ready compliance reports  

### Enterprise Policy-as-Code  
- Centralized `policy.yml` defining risk appetite  
- Deterministic evaluation for CI/CD  
- Consistent governance across teams and repositories

### Multi-Model Intelligence
- **Groq (Llama 3.3)** - Extreme speed, free tier
- **Google Gemini** - Free tier available
- **Local LLMs (Ollama)** - 100% private, no API costs

### CI/CD Ready
- Automated PR commenting via GitHub API
- GitLab Merge Request integration
- Advisory mode with optional blocking

---

## What ai-slop-gate Does

### Goals
- **Detect AI Slop:** Identify messy, repetitive, or context-free AI-generated code
- **Hybrid Analysis:** Combine Static Code Analysis with deep LLM insights
- **Shift-Left Review:** Audit code locally before pushing to production
- **Advisory Feedback:** Provide actionable insights directly in Pull Requests
- **Scalable Architecture:** Vendor-agnostic design supporting various AI models

### Non-Goals
ai-slop-gate is **NOT**:
- A replacement for human code reviews
- A formal security scanner or compliance certification tool
- A guarantee that AI-generated code is correct or safe
- A production-grade enforcement gate (yet)

**Disclaimer:** This tool supports compliance workflows but does not guarantee legal compliance with EU AI Act or DORA regulations. Use as part of a comprehensive compliance framework.

---

## Supported Languages & Infrastructure

- **Languages:** Ruby, Python, JavaScript/TypeScript, Java, C++, C#
- **Infrastructure:** Docker, Kubernetes, Terraform

---

## Getting Started

### Quick Installation

```bash
git clone https://github.com/SergUdo/ai-slop-gate.git
cd ai-slop-gate
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Initialize Configuration

```bash
python -m ai_slop_gate.cli init
```

This creates `.ai-slop-gate.yml` with default settings. Use `--force` to overwrite existing config.

### Set Up Environment Variables

Create a `.env` file:

```bash
# Required for GitHub PR commenting
GITHUB_TOKEN=your_github_personal_access_token

# Provider Keys (add based on your configuration)
GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
GITLAB_TOKEN=your_gitlab_token  # For GitLab integration
```

### Run Your First Analysis

```bash
# Static analysis (fast, no API keys required)
python -m ai_slop_gate.cli run --provider static --policy policy.yml

# LLM analysis with cache (recommended)
python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml

# Compliance check
python -m ai_slop_gate.cli run --compliance --policy policy.yml
```

---

## Analysis Examples & Reports

Real-world execution logs and examples:

- [LLM Analysis (Gemini)](docs/source/example_gemini_report.md) - AI slop detection with Gemini
- [LLM Analysis (Groq)](docs/source/example_groq_report.md) - AI slop detection with Groq
- [LLM Analysis (Ollama)](docs/source/example_ollama_report.md) - Local AI slop detection
- [Static Analysis](docs/source/example_static_pipeline_report.md) - Security & quality gates
- [Compliance Audit](docs/source/example_compliance_report.md) - Legal and regulatory checks

---

## Test Your Workflow

Try ai-slop-gate on our demo repository filled with intentional violations:

**[SergUdo/slop_test](https://github.com/SergUdo/slop_test)** — Test repository with bad code patterns

```bash
git clone https://github.com/SergUdo/slop_test
python -m ai_slop_gate.cli run --provider gemini --llm-local --path slop_test
```

**Live Example:** See [this PR](https://github.com/SergUdo/slop_test/pull/7) where ai-slop-gate automatically analyzed and commented on violations.

---

## Docker Support

Pull and run the pre-built image:

```bash
docker pull ghcr.io/sergudo/ai-slop-gate:latest

docker run --rm -v $(pwd):/src ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

**Full Docker documentation:** [docs/source/DOCKER.md](docs/source/DOCKER.md)

---

## Cache System

AI Slop Gate automatically caches LLM responses to save tokens and speed up analyses:

- **First run:** 15s, calls LLM API
- **Cached run:** 0.5s, no API call
- **Savings:** ~67% of tokens and time!

```bash
# Run with cache (default)
python -m ai_slop_gate.cli run --provider gemini --llm-local

# Disable cache
python -m ai_slop_gate.cli run --provider gemini --llm-local --no-cache

# Custom cache directory
python -m ai_slop_gate.cli run --provider gemini --llm-local --cache-dir /tmp/cache
```

**Full cache documentation:** [docs/source/CACHE.md](docs/source/CACHE.md)

---

## CI/CD Integration

### GitHub Actions

Example workflow for GitHub:

```yaml
name: AI Slop Gate
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AI Slop Gate
        run: |
          docker run --rm -v $(pwd):/src \
            -e GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }} \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider gemini --policy /src/policy.yml --path /src
```

**Full integration guide:** [docs/source/INTEGRATIONS.md](docs/source/INTEGRATIONS.md)

---

## Testing

```bash
# Run all tests
python -m pytest ai_slop_gate/tests -v

# With coverage
python -m pytest ai_slop_gate/tests \
  --cov=ai_slop_gate \
  --cov-report=term-missing \
  --cov-report=html

# View coverage report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
```

**Full testing guide:** [docs/source/TESTING.md](docs/source/TESTING.md)

---

## Security & Compliance

ai-slop-gate follows **DevSecOps** best practices:

- Vulnerability Scanning: Every build scanned by Trivy
- SBOM Generation: Full transparency with Syft (SPDX-JSON)
- License Compliance: Automated gates for restrictive licenses
- Data Sovereignty: Local LLM support for GDPR compliance
- EU Compliance: Supports NIS2, DORA, and EU AI Act requirements

For detailed security information, see [SECURITY.md](docs/source/SECURITY.md)

---

## Tips for Open Source Projects

1. **Use cache to save money** — Cache saves ~67% of tokens on repeated analyses
2. **Use free/local providers** — Ollama (100% free), Groq (free tier), Gemini Flash (free quota)
3. **Combine static + LLM** — Fast static analysis + cached LLM for best results
4. **Cache in CI/CD** — Persist `.ai-slop-cache/` between runs to save tokens

```yaml
# GitHub Actions cache example
- uses: actions/cache@v3
  with:
    path: .ai-slop-cache
    key: ai-slop-cache-${{ hashFiles('**/*.py') }}
```

---

## Contributing

We welcome contributions! See:
- [Architecture Overview](docs/source/ARCHITECTURE.md)
- [Development Setup](docs/source/DEV_SETUP.md)
- [Contributing Guidelines](docs/source/CONTRIBUTING.md)

---

## License

MIT License © 2025 Vira Udovychenko.  
See the [LICENSE](LICENSE) file for details.

---

## Support

- [Documentation](https://ai-slop-gate.readthedocs.io/)
- [Issue Tracker](https://github.com/SergUdo/ai-slop-gate/issues)

