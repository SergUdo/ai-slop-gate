# Changelog

All notable changes to ai-slop-gate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-arch Docker support (amd64, arm64)
- Google Cloud Secret Manager integration

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
