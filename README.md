# ai-slop-gate

**ai-slop-gate** — open-source CI/CD gate combining **static analysis** and **multi-LLM** code review (`Groq`, `Gemini`, `Ollama`) to detect low-intent AI-generated code. Implements deterministic normalization of LLM outputs for audit-friendly quality gates with built-in DevSecOps checks: SBOM generation, license audit, and CVE scanning.

> **Important Notice – LLM Data Processing**
>
> This project integrates external LLM providers (e.g., Gemini, Groq) for code analysis.
> When using **free-tier APIs**, requests may be processed through endpoints located **outside the European Union (e.g., United States)** even if EU regions are selected in provider settings.
>
> This repository intentionally demonstrates such configurations to highlight **potential GDPR / NIS2 data transfer considerations** when integrating AI services into CI/CD pipelines.
>
> For strict data residency requirements, use **local models (Ollama)** or enterprise EU-hosted LLM deployments.

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
[![Tessl Skill](https://img.shields.io/badge/agent--skill-tessl-6366f1)](https://tessl.io/registry/ai-slop-gate/ai-slop-gate)

---

## Documentation

Full documentation: **[ai-slop-gate.readthedocs.io](https://ai-slop-gate.readthedocs.io/)**

[Quick Start](docs/source/quick-start.rst) · [CLI Reference](docs/source/CLI_REFERENCE.md) · [Architecture](docs/source/ARCHITECTURE.md) · [CI/CD Integrations](docs/source/INTEGRATIONS.md) · [Docker](docs/source/DOCKER.md) · [Cache Guide](docs/source/CACHE.md)

---

## Detection Model

**ai-slop-gate** detects **low-intent AI-generated code** in Pull Requests and local repositories. It combines fast deterministic static analysis with deep LLM reasoning, normalizes outputs into structured observations, and applies policy-driven enforcement.

It combines deterministic static analysis with multi-LLM reasoning, normalizes outputs into structured observations, and applies policy-driven enforcement suitable for CI/CD governance and DevSecOps workflows.

**Goals:** 
- **Detect AI Slop:** Identify messy, repetitive, or context-free AI-generated code
- **Hybrid Analysis:** Combine static analysis with deep LLM insights
- **Shift-Left Review:** Audit code locally before pushing to production
- **Advisory Feedback:** Provide actionable insights directly in Pull Requests

**Not a replacement** for human code review. Not a formal security certification tool. Results are signals, not verdicts.

---

## Key Features

### Multi-Model LLM Analysis

| Provider | API Key | Notes |
|---|---|---|
| **Groq** (Llama 3.3) | `SLOPE_GATE_GROQ` | Extreme speed, free tier |
| **Google Gemini** | `GEMINI_API_KEY` | Free tier available |
| **Ollama** | None | 100% local, no API costs |

### Static Analysis

- **Languages:** Python, JavaScript/TypeScript, Ruby, Java, C++, C#
- **Infrastructure:** Docker, Kubernetes, Terraform
Includes: secrets detection, eval/exec patterns, PII, dead code, Dockerfile misconfigs, K8s manifests, Terraform plan analysis.
> Note: The above refers to static analyzers. LLMs can analyze any files and infrastructure.

### Supply Chain & DevSecOps

- CVE scanning via **Trivy**
- SBOM generation via **Syft** (SPDX 2.3, CycloneDX 1.6)
- Forbidden license detection (GPL, AGPL)
- AI-hallucinated dependency detection
- Assists in technical alignment with **[EU Cyber Resilience Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)** and **[DORA](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554)** supply chain security requirements. 


### Compliance

- GDPR/DSGVO data residency enforcement (EU-only LLM routing)
- NIS2 and EU Cyber Resilience Act alignment
- Audit-ready compliance reports
- Profiles: `default`, `eu`, `eu-strict`

> **Disclaimer:** This tool supports compliance workflows but does not guarantee legal compliance with `EU CRA` or `DORA` regulations.

### Enterprise Policy-as-Code

Centralized `policy.yml` with `include_paths`, enforcement levels, and rule definitions.

---

## Getting Started

### Install

```bash
git clone https://github.com/SergUdo/ai-slop-gate.git
cd ai-slop-gate
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
npm install                  # Required for JS/TS static analysis
npm install ts-prune
```

### Initialize Policy

```bash
python -m ai_slop_gate.cli init
```

Creates a default `policy.yml`. Always provide `--policy` when running — it controls `include_paths` that limit what providers see.

### Environment Variables

```bash
# LLM providers
export GEMINI_API_KEY="your-gemini-key"
export SLOPE_GATE_GROQ="your-groq-key"

# VCS integration
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

---

## Usage

### Static Analysis (no API key needed)

```bash
python -m ai_slop_gate.cli run --provider static --policy policy.yml --path /your/project
```

### LLM Analysis on Local Files

```bash
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml --path /your/project 
python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml --path /your/project
```

### GitHub PR Analysis

```bash
python -m ai_slop_gate.cli run \
  --provider groq \
  --llm-local \
  --github-repo owner/repo \
  --pr-id 123 \
  --policy policy.yml
```

#### Analyze a GitHub Pull Request use console locally ( example - PR #2 from repo SergUdo/slop_test)

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml --github-repo SergUdo/slop_test --pr-id 2
```

### Compliance Only

```bash
python -m ai_slop_gate.cli run --compliance --policy policy.yml --path /your/project
```

---

## Enforcement Levels

| Mode | Behavior | When to use |
|---|---|---|
| `advisory` | Findings reported, CI always passes | First rollout, baseline tuning |
| `blocking` | CI fails on violations | Production gate |
| `never` | Report only, exit code always 0 | Dry-run / debugging |

```bash
python -m ai_slop_gate.cli run --provider static --enforcement advisory --policy policy.yml --path /your/project
```

---

## Policy File

`--policy` is required for every `run` command. `include_paths` in `policy.yml` controls what providers see — without it, LLM providers receive the entire repository and hit token limits.

**Discovery order:**
1. `--policy <explicit path>` — always wins
2. `<--path>/policy.yml` — auto-discovered from scanned repo
3. `./policy.yml` — current working directory
4. Bundled default (permissive, not recommended for LLM)

**Minimal policy example:**

```yaml
version: "v1.4"
project_name: "my-project"
enforcement: advisory

include_paths:
  - src

ai_provider:
  name: groq
  models:
    groq: llama-3.3-70b-versatile

compliance:
  enabled: false

rules:
  - id: block-hardcoded-secrets
    when:
      signal: "hardcoded_.*"
    then:
      action: blocking
      message: "Hardcoded secret detected."
```

---

## Cache

LLM responses are cached automatically to prevent duplicate token spend:

| Run | API calls |
|---|---|
| First run | Yes |
| Cached run (same input + policy) | No |

```bash
# Disable cache (for debugging prompt changes only)
python -m ai_slop_gate.cli run --provider groq --llm-local --no-cache --policy policy.yml --path /your/project

# Custom cache directory
python -m ai_slop_gate.cli run --provider groq --llm-local --cache-dir /tmp/cache --policy policy.yml --path /your/project
```

LLM providers automatically exclude from API calls: `.env*`, `policy.yml`, `docs/`, `scripts/`, lock files, minified bundles.

---

## Supply Chain Artifacts

The gate automatically generates industry-standard security artifacts **when running the Static Analysis provider locally** (`--provider static`) or **CI/CD Integration**: See the [GitHub Actions Static Analysis Example](docs/source/examples/example_workflow_static.yml) or **GitLab CI/CD**: [Static Analysis Pipeline Example](docs/source/examples/gitlab-static-ci.yml) for a ready-to-use configuration:


| Artifact | Format |
|---|---|
| `sbom.json` | Syft Native |
| `sbom-spdx.json` | SPDX 2.3 |
| `sbom-cyclonedx.json` | CycloneDX 1.6 |
| `sbom-cyclonedx-vex.json` | CycloneDX + VEX |

These files are saved in the scanned directory and can be uploaded as CI/CD artifacts.
---

## Docker Support

```bash
docker pull ghcr.io/sergudo/ai-slop-gate:latest

 docker run --rm \
  -v /path_your_local_test_repo:/data \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /app/policy.yml --path /data
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

### GitHub Actions

- [Static analysis workflow](docs/source/examples/example_workflow_static.yml)
- [Gemini LLM workflow](docs/source/examples/example_workflow_gemini.yml)
- [Groq LLM workflow](docs/source/examples/example_workflow_groq.yml)
- [Compliance workflow](docs/source/examples/example_workflow_compliance.yml)

### GitLab CI/CD

- [Static pipeline](docs/source/examples/gitlab-static-ci.yml)
- [LLM pipeline](docs/source/examples/gitlab-llm-ci.yml)

## Example Test Dataset

For intentionally bad code samples used to test ai-slop-gate detection capabilities, see:

https://github.com/SergUdo/slop_test

**Live example:** [PR #2 in slop_test](https://github.com/SergUdo/slop_test/pull/2) — ai-slop-gate commenting on violations automatically.

Full integration guide: [docs/source/INTEGRATIONS.md](docs/source/INTEGRATIONS.md)

---

## Verify Image Signature

```bash
# Download public key
curl -O https://raw.githubusercontent.com/sergudo/ai-slop-gate/main/cosign.pub

# Verify
cosign verify --key cosign.pub ghcr.io/sergudo/ai-slop-gate:1.2.8
```

---

## Testing

```bash
python -m pytest ai_slop_gate/tests -v
python -m pytest ai_slop_gate/tests --cov=ai_slop_gate --cov-report=term-missing --cov-report=html
```

---

## Analysis Examples

- [LLM Analysis (Gemini)](docs/source/example_gemini_report.md)
- [LLM Analysis (Groq)](docs/source/example_groq_report.md)
- [LLM Analysis (Ollama)](docs/source/example_ollama_report.md)
- [Static Analysis](docs/source/example_static_pipeline_report.md)
- [Compliance Audit](docs/source/example_compliance_report.md)

---

## Contributing

See [Contributing Guidelines](docs/source/CONTRIBUTING.md) and [Architecture Overview](docs/source/ARCHITECTURE.md).

---

## License

MIT License © 2025 Vira Udovychenko. See [LICENSE](LICENSE).

---

## Support

[Documentation](https://ai-slop-gate.readthedocs.io/) · [Issue Tracker](https://github.com/SergUdo/ai-slop-gate/issues)
