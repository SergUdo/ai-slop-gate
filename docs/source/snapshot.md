# Project Snapshot

**Version:** 7.4.0  
**Status:** Canonical  
**Stage:** Stage 1

## Overview

**ai-slop-gate** is a policy-driven AI, supply-chain and compliance gate for code and infrastructure.

## Core Principles

- ✅ **No Hidden Logic** - All behavior is explicit and configurable
- ✅ **Policy is Source of Truth** - Policy files define all rules
- ✅ **Compliance is Sidecar** - Compliance checks are optional extensions
- ✅ **Engine is Pure** - Core engine has no side effects
- ✅ **CLI is Thin** - CLI only handles argument parsing and wiring
- ✅ **Tests Lock Contracts** - Tests verify contracts, not implementation details
- ✅ **Cache is Cost Control** - Caching prevents duplicate LLM token spending

## Supported Languages & Technologies

* ✅ **Ruby** (Full support)
* ✅ **Python** (Full support)
* ✅ **JavaScript / TypeScript** (Full support)
* ✅ **Java** (Full support)
* ✅ **C++** (Full support)
* ✅ **C#** (Full support)
* ✅ **Docker** (Full support)
* ✅ **Kubernetes** (Full support)
* ✅ **Terraform** (Full support)

## Execution Model

The tool follows a clear execution flow:

1. CLI parses flags
2. Policy is loaded and resolved
3. Providers collect or analyze inputs
4. LLM providers are optionally wrapped by CachedProvider
5. Compliance sidecar optionally runs
6. Policy engine evaluates observations
7. Decision is produced
8. Reporters render output
9. Exit code is derived from decision
10. Release pipeline runs (determine version → build → sign → publish)

## CLI Commands

### `init`
Initialize a new policy file.

### `run`
Execute analysis based on policy.

**Key Flags:**
- `--policy` - Path to policy.yml (required)
- `--provider` - Provider name (static, k8s-runtime, supply-chain, llm)
- `--input-file` - Input file for providers
- `--compliance` - Force enable compliance sidecar
- `--enforcement` - never | advisory | blocking
- `--verbose` - Emit full resolved state and observations

## Policy Structure

Policies are defined in `policy.yml` with the following sections:

- **enforcement** - Enforcement mode (advisory, blocking, never)
- **ai_provider** - LLM provider configuration
- **compliance** - Compliance rules and profiles
- **profiles** - Reusable compliance profiles (default, eu, eu-strict)
- **rules** - Custom policy rules

## Built-in Providers

### Static Analysis Providers
- StaticProvider
- StaticSecurityProvider
- StaticPipelineProvider
- ESLintProvider
- StaticDockerProvider
- StaticJSProvider
- StaticPythonProvider
- StaticTSJSProvider
- StaticRubyProvider
- StaticJavaProvider
- StaticCSharpProvider
- StaticCppProvider

### Infrastructure Providers
- K8sRuntimeProvider
- KubernetesStaticProvider
- TerraformPlanProvider
- TerraformStaticProvider

### Supply Chain Providers
- SupplyChainProvider
- TrivyProvider
- SBOMProvider

## Cache System

**Purpose:** Prevent repeated LLM token spending

**Scope:** LLM providers only

**Cache Key Components:**
- Provider ID
- Model name
- Compliance profile
- Policy hash
- Normalized input fingerprint

**Cache Invalidation Triggers:**
- Input content change
- Policy change
- Profile change
- Model change

**Backends:**
- **File** (default) - `.ai-slop-cache/`
- **Memory** (tests only)

## Compliance Profiles

### default
Inherits base compliance configuration

### eu
Enforces GPL/AGPL license ban and EU data residency requirements

### eu-strict
Blocking enforcement with strict EU compliance rules

## Decision Modes

- **allow** - No issues detected (exit code 0)
- **advisory** - Issues detected but not blocking (exit code 0)
- **blocking** - Issues detected, blocking deployment (exit code 1)

## Reporters

- **stdout** - Human-readable terminal output
- **github_pr** - GitHub Pull Request comments
- **github_checks** - GitHub Checks annotations

## Release Pipeline

### Versioning Strategy
Semantic versioning based on conventional commits:
- `fix:` → patch bump
- `feat:` → minor bump
- `BREAKING CHANGE:` → major bump

### Multi-Architecture Support
- `linux/amd64`
- `linux/arm64`

### Security Features
- **Image Signing** - Cosign key-pair signing
- **SBOM Generation** - Syft-generated SBOM
- **Vulnerability Scanning** - Trivy scanning

### Distribution
- **Registry:** `ghcr.io/public`
- **Visibility:** Public
- **Tags:** `vX.Y.Z`, `latest`, `sha-<short>`

## Non-Goals

- ❌ Automatic code fixing
- ❌ Code rewriting
- ❌ Business logic inside CLI
- ❌ Provider-specific policy logic
- ❌ Caching for non-LLM providers

## Required Secrets for Release

- `GHCR_TOKEN` - Write access to GitHub Container Registry
- `COSIGN_PRIVATE_KEY` - Private key for image signing
- `COSIGN_PASSWORD` - Password protecting cosign.key
- `GITHUB_TOKEN` - Automated changelog/release creation