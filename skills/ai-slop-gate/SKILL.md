---
name: ai-slop-gate
description: Contribute to ai-slop-gate — an open-source CI/CD policy gate that detects AI-generated code slop, security issues, and compliance violations. Use when adding a new LLM provider (Gemini, Groq, Ollama) or static provider, writing analysis rules, extending the policy engine, working with reporters, fixing compliance sidecar logic, or writing tests. Activate when working with ai_slop_gate/ source tree, policy.yml, snapshot, or GitHub Actions workflows.
license: MIT
metadata:
  author: SergUdo
  version: "1.2.8"
  snapshot: "7.5.0"
compatibility: Python 3.12+, pytest, GitHub Actions
---

ai-slop-gate is a vendor-agnostic CLI tool combining static analysis and multi-LLM code review to detect low-intent AI-generated code in CI/CD pipelines. Source of truth: `ai_slop_gate_snapshot.json`.

## Architecture Principles

- Policy is source of truth (`policy.yml`)
- CLI is thin — argument parsing and wiring only
- Engine is pure — no IO, no printing, no exit calls
- Compliance is a sidecar — never inside the engine
- Cache is cost control — LLM providers only, prevents duplicate token spend

## Execution Flow

```
CLI → Policy loaded → Providers run (LLM wrapped by CachedProvider optionally)
    → Compliance sidecar (optional) → PolicyEngine → Decision → Reporters → exit code
```

## Directory Structure

```
ai_slop_gate/
├── cli/              # Thin CLI layer (main.py, run.py, args.py, context.py)
├── engine/           # provider_factory.py
├── domain/           # PolicyEngine, Observation, Decision, CheckReport
│   └── compliance/   # Compliance sidecar (detector, profiles, rules)
├── providers/
│   ├── base.py       # BaseProvider ABC + ProviderObservation
│   ├── registry.py   # Provider registry
│   ├── cached_provider.py
│   ├── llm/          # GeminiProvider, GroqProvider, OllamaProvider + prompts/
│   └── static/       # 19 static/infra providers (see list below)
├── reporters/        # ConsoleReporter, GitHubPRReporter, GitHubChecksReporter, GitLabMRReporter
├── github/           # pr_commenter.py
├── cache/            # File and memory cache backends
└── tests/unit/ + tests/integration/
```

## Core Contracts (Never Break)

### ProviderObservation

```python
@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    model: str
    observations: List[Any]   # list of Observation objects
    raw_text: str
```

### BaseProvider

```python
class BaseProvider(ABC):
    name: str
    kind: str  # "llm" | "static" | "infra"

    def analyze(self, code: str, input_file: str = "") -> ProviderObservation: ...
    def collect(self, base_path: str = ".") -> ProviderObservation: ...
    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # Default raises NotImplementedError. LLM providers may implement.
        ...
```

### Observation

```python
@dataclass(frozen=True)
class Observation:
    category: str
    signal: str                          # snake_case identifier
    confidence: float                    # 0.0 – 1.0
    message: str
    severity: Optional[Severity]         # low|medium|high|critical
    evidence: Optional[Dict[str, Any]]
    rule_id: Optional[str]
    location: Optional[Location]         # { file: str, line: Optional[int] }
```

### Decision

```python
@dataclass(frozen=True)
class Decision:
    mode: DecisionMode   # allow | advisory | blocking
    reasons: List[str]
    annotations: Optional[List[Annotation]]
```

Exit codes: `allow` → 0, `advisory` → 0, `blocking` → 1.

## Provider Inventory

### LLM Providers (kind = "llm")

| Class | name | Prompt files | analyze_pr |
|---|---|---|---|
| `GeminiProvider` | `gemini` | `gemini/deep.prompt` | ✅ |
| `GroqProvider` | `groq` | `groq/deep.prompt`, `groq/fast.prompt` | ✅ |
| `OllamaProvider` | `ollama` | `ollama/qwen.prompt`, `ollama/mistral.prompt` | ❌ |

LLM providers implement both `analyze()` and `collect()`. `collect()` delegates to `LlmProvider.analyze_files()` which chunks the repo and calls `analyze()` per chunk with rate-limit sleep.

### Static Providers (kind = "static")

| Class | name |
|---|---|
| `StaticProvider` | `static` |
| `StaticSecurityProvider` | `static_security` |
| `StaticPipelineProvider` | `static_pipeline` |
| `StaticPythonProvider` | `static_python` |
| `StaticJSProvider` | `static_js` |
| `StaticTSJSProvider` | `static_ts_js` |
| `StaticDockerProvider` | `static_docker` |
| `StaticCppProvider` | `cpp_static` |
| `StaticCSharpProvider` | `csharp_static` |
| `StaticJavaProvider` | `java_static` |
| `StaticRubyProvider` | `ruby_static` |
| `ESLintProvider` | `eslint` |
| `KubernetesStaticProvider` | `k8s_static` |
| `TerraformStaticProvider` | `terraform_static` |
| `TerraformPlanProvider` | `terraform_plan` |
| `SupplyChainProvider` | `supply_chain` |
| `TrivyProvider` | `trivy` |
| `SBOMProvider` | `sbom` |
| `DeadCodeProvider` | `dead_code` |

### Infra Providers (kind = "infra")

| Class | name |
|---|---|
| `K8sRuntimeProvider` | `k8s_runtime` |

## Adding a New LLM Provider

1. Create `ai_slop_gate/providers/llm/<n>.py` extending `LlmProvider` (`kind = "llm"`)
2. Implement `analyze(code, input_file)` → `ProviderObservation`
3. Optionally implement `analyze_pr(repo, pr_id, token)`
4. Add prompt to `providers/llm/prompts/<n>/`
5. Register in `providers/registry.py`
6. Add `--provider <n>` to CLI
7. Write tests in `tests/unit/providers/`

**LLM JSON contract** — prompt must instruct model to return:
```json
{
  "issues": [
    {
      "category": "string",
      "signal": "snake_case",
      "message": "non-empty",
      "severity": "low|medium|high|critical",
      "confidence": 0.85,
      "file": "path/to/file.py",
      "line": 42
    }
  ]
}
```
No markdown, no text outside JSON, no line ranges, top-level key must be `issues`.

## Adding a New Static Provider

1. Create `ai_slop_gate/providers/static/<n>.py` extending `BaseProvider` (`kind = "static"` or `"infra"`)
2. Implement `collect(base_path)` → `ProviderObservation`
3. Register in `providers/registry.py`
4. Write tests with positive (detects issues) and negative (clean code) examples

## Cache Rules

- Cache wraps LLM providers only via `CachedProvider`
- Cache key: `provider_id + model + profile + policy_hash + input_fingerprint`
- Same key must NEVER trigger an LLM call twice
- Static providers are never cached
- Never add provider-specific logic to the cache layer

## Compliance Sidecar

Enabled by `policy.compliance.enabled` or `--compliance` / `--compliance-only` flag.
Runs after providers, before reporters. Profiles: `default`, `eu`, `eu-strict`.
Checks: forbidden licenses (GPL, AGPL), secret detection, GDPR data residency.

## Policy Engine

Input: `List[Observation]` → Output: `Decision`
Modes: `allow` (exit 0) | `advisory` (exit 0) | `blocking` (exit 1)
Engine is pure: no IO, no printing, no exit calls.

## CLI

```bash
python -m ai_slop_gate.cli.main run \
  --provider static groq \
  --llm-local \
  --policy policy.yml \
  --path /path/to/project \
  --enforcement advisory

python -m ai_slop_gate.cli.main run \
  --provider groq \
  --github-repo owner/repo \
  --pr-id 123 \
  --policy policy.yml
```

## Testing

```bash
python -m pytest ai_slop_gate/tests -v
python -m pytest ai_slop_gate/tests --cov=ai_slop_gate --cov-report=term-missing
```

Critical invariants: LLM token not spent twice for same cache key; cache key changes on input/policy change; static providers never cached.

## What NOT to Do

- Do not invent SDK methods, JSON fields, or file paths not in the snapshot
- Do not create new providers unless explicitly requested
- Do not modify architecture or retry logic unless explicitly requested
- Do not add provider-specific logic to cache or reporters
- Do not put business logic inside CLI
- Do not assume caching for non-LLM providers