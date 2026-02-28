# ai-slop-gate

**ai-slop-gate** — open-source **CI/CD** tool combining **static analysis** and **multi-LLM** (`Groq`, `Gemini`, `Ollama`) code review to detect low-intent AI-generated code. Implements deterministic normalization of LLM outputs (severity, confidence, signals) for audit-friendly automated quality gates with built-in **DevSecOps** checks: `SBOM` generation, `License` audit, and `CVE` scanning.


[![Docker Publish](https://github.com/SergUdo/ai-slop-gate/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/SergUdo/ai-slop-gate/actions/workflows/docker-publish.yml)
[![Tests](https://github.com/SergUdo/ai-slop-gate/actions/workflows/tests.yml/badge.svg)](https://github.com/SergUdo/ai-slop-gate/actions/workflows/tests.yml)
[![Code Analysis](https://github.com/SergUdo/ai-slop-gate/actions/workflows/analyze.yml/badge.svg)](https://github.com/SergUdo/ai-slop-gate/actions/workflows/analyze.yml)
[![Release](https://github.com/SergUdo/ai-slop-gate/actions/workflows/release.yml/badge.svg)](https://github.com/SergUdo/ai-slop-gate/actions/workflows/release.yml)
[![Documentation](https://readthedocs.org/projects/ai-slop-gate/badge/?version=latest)](https://ai-slop-gate.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/SergUdo/ai-slop-gate?sort=semver)](https://github.com/SergUdo/ai-slop-gate/releases/latest)
[![Docker](https://img.shields.io/badge/docker-GHCR-2496ED?logo=docker&logoColor=white)](https://github.com/SergUdo/ai-slop-gate/pkgs/container/ai-slop-gate)
[![Cosign](https://img.shields.io/badge/cosign-signed-success?logo=sigstore&logoColor=white)](https://github.com/SergUdo/ai-slop-gate/releases)
[![SBOM](https://img.shields.io/badge/SBOM-included-blue)](https://github.com/SergUdo/ai-slop-gate/releases)
[![GitHub stars](https://img.shields.io/github/stars/SergUdo/ai-slop-gate?style=social)](https://github.com/SergUdo/ai-slop-gate/stargazers)

---

## Documentation

Complete documentation: **[ai-slop-gate.readthedocs.io](https://ai-slop-gate.readthedocs.io/)**

### Quick Links
- [Quick Start Guide](docs/source/quick-start.rst)
- [Architecture Overview](docs/source/ARCHITECTURE.md)
- [CLI Reference](docs/source/CLI_REFERENCE.md)
- [Cache Guide](docs/source/CACHE.md)
- [Docker Setup](docs/source/DOCKER.md)
- [CI/CD Integrations](docs/source/INTEGRATIONS.md)
- [Security Policy](docs/source/SECURITY.md)

---

## Key Features

### Supply Chain Security
- Detects forbidden licenses (GPL, AGPL)
- Identifies AI-hallucinated or suspicious package names
- SBOM generation via Syft (SPDX-JSON)
- CVE scanning via Trivy
- Supports NIS2
- Assists in technical alignment with **[EU Cyber Resilience Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)** and **[DORA](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554)** supply chain security requirements. 

### GDPR/DSGVO Compliance
- Enforces EU-only data residency for AI processing
- Prevents non-compliant LLM routing
- Produces audit-ready compliance reports

### Enterprise Policy-as-Code
- Centralized `policy.yml` defining risk appetite and `include_paths`
- Deterministic evaluation for CI/CD gates
- Consistent governance across teams and repositories

### Multi-Model Intelligence
- **Groq (Llama 3.3)** — Extreme speed, free tier
- **Google Gemini** — Free tier available
- **Local LLMs (Ollama)** — 100% private, no API costs

### CI/CD Ready
- Automated PR commenting via GitHub API
- GitLab Merge Request integration
- `--enforcement advisory/blocking/never` for progressive rollout

---

## What ai-slop-gate Does

### Goals
- **Detect AI Slop:** Identify messy, repetitive, or context-free AI-generated code
- **Hybrid Analysis:** Combine static analysis with deep LLM insights
- **Shift-Left Review:** Audit code locally before pushing to production
- **Advisory Feedback:** Provide actionable insights directly in Pull Requests

### Non-Goals
ai-slop-gate is **NOT**:
- A replacement for human code reviews
- A formal security scanner or compliance certification tool
- A guarantee that AI-generated code is correct or safe

**Disclaimer:** This tool supports compliance workflows but does not guarantee legal compliance with `EU Cyber Resilience Act` or `DORA` regulations.

---

## Supported Languages & Infrastructure

- **Languages:** Python, JavaScript/TypeScript, Ruby, Java, C++, C#
- **Infrastructure:** Docker, Kubernetes, Terraform
> Note: The above refers to static analyzers. LLMs can analyze any files and infrastructure.

---

## Getting Started

### Installation

```bash
git clone https://github.com/SergUdo/ai-slop-gate.git
cd ai-slop-gate
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### Initialize Configuration

```bash
python -m ai_slop_gate.cli init
```

Creates a default `policy.yml` in the current directory.

### Set Up Environment Variables

```bash
# .env file
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
GITLAB_TOKEN=your_gitlab_token   # For GitLab integration
```

## Analysis Examples & Reports

Real-world execution logs and examples:

- [LLM Analysis (Gemini)](docs/source/example_gemini_report.md) - AI slop detection with Gemini
- [LLM Analysis (Groq)](docs/source/example_groq_report.md) - AI slop detection with Groq
- [LLM Analysis (Ollama)](docs/source/example_ollama_report.md) - Local AI slop detection
- [Static Analysis](docs/source/example_static_pipeline_report.md) - Security & quality gates
- [Compliance Audit](docs/source/example_compliance_report.md) - Legal and regulatory checks


---

## Policy File — Required

`--policy` is **required** for every `run` command. The `policy.yml` controls which directories
are sent to providers via `include_paths`. Without it, LLM providers receive the entire
repository and fail with token-limit errors.

**Policy discovery order** when the scanned repository has its own policy:

1. `--policy <explicit path>` — always wins
2. `<--path>/policy.yml` — policy inside the scanned repository (auto-discovered)
3. `./policy.yml` — current working directory
4. Bundled package default (permissive, not recommended for LLM use)

---

### Policy Configuration

**ai-slop-gate** is designed for speed and flexibility. You can start with zero configuration or fine-tune it for complex compliance needs.

### Option 1: Zero-Config Start (Recommended)
Don't have a policy yet? The gate uses a **robust built-in security policy** by default. It’s pre-configured to detect common AI-generated anti-patterns and basic security flaws.

Just run the Docker container or CLI; no configuration files are required for your first scan.

### Option 2: Custom Policy Control
To tailor the gate to your project's specific standards (e.g., custom severity levels or specific GDPR rules), place a `policy.yml` in your repository root. The gate will auto-discover it.

* **Auto-discovery:** Name your file `policy.yml` in the root.
* **Manual path:** Use the `--policy ./my-custom-rules.yml` flag.

[📄 View Minimal Policy Template](docs/source/examples/example_policy_minimal.yml)

---


## Run Your First Analysis

```bash
# Clone the repository
git clone https://github.com/SergUdo/ai-slop-gate.git
cd ai-slop-gate

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Create .env file with your API key(s)
touch .env

# Example content:
# SLOPE_GATE_GROQ=your_key_here
# GEMINI_API_KEY=your_key_here
# GITHUB_TOKEN=your_token_here

# Static analysis (fast, no API key required)
python -m ai_slop_gate.cli run --provider static --policy policy.yml --path /your/project

# LLM Groq analysis on local files
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml --path /your/project

# LLM Gemini analysis on local files
python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml --path /your/project

# Compliance check only
python -m ai_slop_gate.cli run --compliance --policy policy.yml --path /your/project

# Advisory mode — findings shown, CI never blocked
python -m ai_slop_gate.cli run --provider static --policy policy.yml --enforcement advisory --path /your/project

# Analyze a GitHub Pull Request (PR #2 from SergUdo/slop_test)
python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml --github-repo SergUdo/slop_test --pr-id 2
```

---

## Enforcement Levels

| Mode | Behaviour | When to use |
|---|---|---|
| `advisory` | Findings reported, CI always passes | First rollout, baseline tuning |
| `blocking` | CI fails on violations | Production gate |
| `never` | Report only, exit code always 0 | Dry-run / debugging |

```bash
# Override policy enforcement from CLI
python -m ai_slop_gate.cli run --provider static --policy policy.yml --enforcement advisory --path /your/project
```

---

## Sensitive File Exclusions

LLM providers automatically exclude the following from API calls (regardless of policy):

- `.env`, `.env.*`, `.env.example`
- `policy.yml`
- `docs/`, `scripts/`, `.ai-slop-cache/`
- Lock files: `package-lock.json`, `poetry.lock`, `yarn.lock`, etc.
- Minified bundles: `*.min.js`

Only source code extensions are sent: `.py`, `.js`, `.ts`, `.rb`, `.cs`, `.yml` (app config only), etc.

---

## Cache System

LLM responses are cached automatically to save tokens and speed up repeat runs:

| Run | Time | API calls |
|---|---|---|
| First run | ~15s | Yes |
| Cached run | ~0.5s | No |
| Savings | — | ~67% of tokens |

```bash
# Cache enabled by default
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml --path /your/project

# Disable cache (for debugging prompt changes only)
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml --no-cache --path /your/project

# Custom cache directory
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml --cache-dir /tmp/cache --path /your/project
```

---

## Docker Support

```bash
docker pull ghcr.io/sergudo/ai-slop-gate:latest

docker run --rm -v $(pwd):/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

Local build and run:

```bash
docker build --no-cache -t ai-slop-gate:latest .

docker run --rm \
  -v /path_your_local_test_repo:/data \
  ai-slop-gate:latest \
  run --provider static --policy policy.yml --path /data

```

Full Docker documentation: [docs/source/DOCKER.md](docs/source/DOCKER.md)

---

## CI/CD Integration

### GitHub Actions examples workflows:

- [Example workflow for static analyze](docs/source/examples/example_workflow_static.yml)

- [Example workflow for gemini analyze](docs/source/examples/example_workflow_gemini.yml)

- [Example workflow for groq analyze](docs/source/examples/example_workflow_groq.yml)

- [Example workflow for compliance analyze](docs/source/examples/example_workflow_compliance.yml)

### GitLab CI/CD example workflow:

- [Example workflow for Gitlab CI](docs/source/examples/.gitlab-ci.yml)

Full integration guide: [docs/source/INTEGRATIONS.md](docs/source/INTEGRATIONS.md)

**Live example:** See [this PR](https://github.com/SergUdo/slop_test/pull/2) where ai-slop-gate automatically commented on violations.

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
```

---

## Contributing

- [Architecture Overview](docs/source/ARCHITECTURE.md)
- [Contributing Guidelines](docs/source/CONTRIBUTING.md)

---

## License

MIT License © 2025 Vira Udovychenko. See [LICENSE](LICENSE).

---

## Support

- [Documentation](https://ai-slop-gate.readthedocs.io/)
- [Issue Tracker](https://github.com/SergUdo/ai-slop-gate/issues)
