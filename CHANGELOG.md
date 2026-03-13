# Changelog

All notable changes to ai-slop-gate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add ArtifactReporter — Versioned JSON Analysis Report per PR
- Add Trend Analysis - Derivative Signal for Findings Rate-of-Change
- Implement Mistral AI Provider for EU Data Residency (GDPR/DSGVO Compliance)
- Integrate GitHub Copilot SDK
- Add Policy Verdict Layer for machine-readable agent decisions
- Transform ai-slop-gate into a Cloud-Native Service with Enterprise Observability
- EU AI Act Compliance - Risk Category Classification
- EU AI Act Compliance - Accuracy Metrics Reporting
- Enhanced GDPR Compliance - Data Flow Visualization
- Dependency License Compatibility Check
- Google Cloud Secret Manager integration
- NIS2 Directive - Supply Chain Incident Reporting

## [1.2.7] - 2026-03-13

### Added
- **Agent Skills**: Added `skills/ai-slop-gate/SKILL.md` — published to Tessl registry for AI agent discovery and installation via `npx tessl install ai-slop-gate`.
- **Copilot Instructions**: Added `.github/copilot-instructions.md` — full architectural context for GitHub Copilot Chat with provider inventory, contracts, and contribution rules.
- **Documentation**: Added "Working with AI Assistants" section to `CONTRIBUTING.md` covering Copilot, Tessl, and Claude workflows.
- **Tessl Registry**: Published agent skill to [tessl.io/registry/ai-slop-gate/ai-slop-gate](https://tessl.io/registry/ai-slop-gate/ai-slop-gate) — install with `npx tessl install ai-slop-gate`.

### Changed
- **Documentation**: Rebuilt `ARCHITECTURE.md` from snapshot v7.5.0 — correct stage (6), full provider inventory (20+ providers), decision modes, Cache and Compliance sidecar sections.
- **Documentation**: Rebuilt `PROJECT_STRUCTURE.md` — complete directory tree including all static providers, `cache/`, `fixtures/`, `github/`.
- **Documentation**: Restructured `README.md` — removed duplicate sections, unified feature descriptions, consistent Ollama coverage throughout.
- **Documentation**: Updated `CONTRIBUTING.md` — correct `BaseProvider` contract, snapshot reference bumped to v7.5.0.

### Fixed
- **Snapshot**: Bumped `ai_slop_gate_snapshot.json` to v7.5.0 — fixed `stage` field (Stage 1 → Stage 6), added `base_classes`, `domain_models`, `llm_json_contract` sections, completed CLI flags, added `DeadCodeProvider` and `GitLabMRReporter` to inventory.

### Security
- **Docker**: Updated `tar` dependency to 7.5.11 to resolve CVE-2026-31802 (high severity).
- **Docker**: Added `.trivyignore` for `libexpat1` (CVE-2026-25210) and `libsystemd0` (CVE-2026-4105) — no fix available in Debian stable; documented rationale based on low exploitability in container context.

## [1.2.6] - 2026-03-08

### Added
- **GitLab CI/CD**: Added a complete template (`gitlab-static-ci.yml`) for automated SBOM generation and artifact archival in GitLab pipelines.
- **Documentation**: Enhanced "Supply Chain & Security" section in README with instructions for both GitHub and GitLab integrations.
- **Documentation**: Added clear environment variable guides for local CLI testing and repository integration.

## [1.2.5] - 2026-03-07

### Added
- **SBOM**: `SBOMProvider` now saves all three formats to disk (`sbom.json`, `sbom-spdx.json`, `sbom-cyclonedx.json`) alongside the scanned project, making artifacts available for download without additional workflow steps.
- **SBOM**: `TrivyProvider` now saves `sbom-cyclonedx-vex.json` (CycloneDX + CVE) to disk during the security scan.

### Fixed
- **Docker**: Added `vulture` to `[project.optional-dependencies]` and updated install target to `.[analysis]` to resolve `ModuleNotFoundError: No module named 'vulture'` in CI.

## [1.2.4] - 2026-03-06

### Fixed
- **Security**: Resolved vulnerability **CVE-2026-29786** in the base image by updating dependencies and the underlying Docker system layers.
- **Groq Provider**: Fixed 404 Not Found errors in CI/CD environments; implemented a universal OpenAI-compatible endpoint for all model types (Llama, Gemma, Mixtral).
- **Environment**: Updated `policy.yml` loading logic to prioritize local project files over the image-embedded defaults, ensuring configuration flexibility in GitLab CI.

### Changed
- Optimized `Dockerfile` to reduce attack surface by removing redundant packages that triggered security scanners.

## [1.2.3] - 2026-03-01

### Security
- **HIGH:** Fixed CVE-2026-27903 in minimatch — updated from 10.2.2 to 10.2.3
- **HIGH:** Pinned trivy to 0.69.1, syft to v1.42.1 to address Go stdlib CVEs
- **HIGH:** Added CVE-2026-24051 to .trivyignore (otel/sdk in syft gobinary, upstream not yet patched)

### Changed
- Pinned external Docker images: `aquasec/trivy:0.69.1`, `ghcr.io/anchore/syft:v1.42.1`
- Added OCI labels (`source`, `description`, `licenses`, `revision`)
- Removed `npm update` workaround — replaced with direct minimatch pin in `package.json`
- Updated `package-lock.json` to reflect resolved dependency versions

### Added
- Integrated [Renovate](https://developer.mend.io/) for automated dependency updates — Docker images, npm and pip packages will be updated automatically via PR

## [1.2.2] - 2026-02- - 2026-02-27

### Security
- **HIGH:** Fixed CVE-2026-27904 in minimatch dependency
  - Updated minimatch from 10.2.2 to 10.2.3+

### Changed
- Updated npm dependencies to latest secure versions

## [1.2.0] - 2026-02-26

### Added
- Published to GitHub Marketplace
- Multi-LLM provider support (Gemini, Groq, Ollama)
- Static analysis with Trivy and Syft
- GDPR/NIS2 compliance checking
- Smart caching reducing LLM costs by 67%
- ReadTheDocs documentation

### Security
- Cosign image signing
- SBOM generation (SPDX, CycloneDX)

## [1.2.1] and earlier

Earlier versions were during initial development phase.
Detailed changelog tracking started with v1.2.0.
