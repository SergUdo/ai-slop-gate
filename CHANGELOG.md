# Changelog

All notable changes to ai-slop-gate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Generate SBOM in Test Repository Workflow
- Multi-arch Docker support (amd64, arm64)
- EU AI Act Compliance - Risk Category Classification
- EU AI Act Compliance - Accuracy Metrics Reporting
- Enhanced GDPR Compliance - Data Flow Visualization
- Dependency License Compatibility Check
- Google Cloud Secret Manager integration
- NIS2 Directive - Supply Chain Incident Reporting

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
