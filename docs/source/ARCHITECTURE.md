# ai-slop-gate — Canonical Architecture

> **Single source of truth:** `ai_slop_gate_snapshot.json` (v7.4.0)
> If this document diverges from the snapshot, the snapshot wins.

**Stage:** 6 (current) | **Status:** canonical

---

## Architectural Principles

| Principle | Meaning |
|---|---|
| No hidden logic | Every decision is traceable to policy |
| Policy is source of truth | `policy.yml` drives all enforcement |
| Compliance is a sidecar | Runs alongside analysis, never inside it |
| Engine is pure | No IO, no printing, no exit calls |
| CLI is thin | Argument parsing and wiring only |
| Tests lock contracts, not behavior | Critical invariants, not implementation |
| Cache is cost control, not performance | LLM only, prevents duplicate token spend |

---

## Execution Flow

```
CLI parses flags
  → Policy loaded and resolved
  → Providers collect or analyze inputs
      → LLM providers optionally wrapped by CachedProvider
  → Compliance sidecar optionally runs
  → Policy engine evaluates all observations
  → Decision produced (allow | advisory | blocking)
  → Reporters render output
  → Exit code derived from decision (0 | 1)
```

---

## Directory Structure

```
ai_slop_gate/
├── cli/                    # CLI entry points and subcommands (thin layer)
│   ├── main.py             # Entrypoint: python -m ai_slop_gate.cli.main
│   ├── run.py              # run command logic: run_analysis()
│   ├── args.py             # Argument parsing
│   ├── context.py          # Runtime context
│   ├── logger.py           # Logging setup
│   └── utils.py            # CLI utilities
├── engine/
│   └── provider_factory.py # Instantiates providers from registry
├── domain/
│   ├── observation.py      # Observation dataclass (immutable)
│   ├── decision.py         # Decision dataclass (allow|advisory|blocking)
│   ├── policy.py           # PolicyRule dataclass
│   ├── policy_engine.py    # Evaluates observations → Decision
│   ├── checks.py           # CheckReport
│   ├── check_mapper.py     # Maps checks to observations
│   ├── signals.py          # Signal definitions
│   ├── contracts.py        # Policy evaluation contracts
│   ├── observation_factory.py
│   ├── observation_result.py
│   └── compliance/         # Compliance sidecar
│       ├── detector.py
│       ├── enforcement.py
│       ├── gateway.py
│       ├── pipeline.py
│       ├── profile_resolver.py
│       ├── profiles.py
│       └── rules.py
├── providers/
│   ├── base.py             # BaseProvider ABC + ProviderObservation
│   ├── registry.py         # Provider registry
│   ├── cached_provider.py  # CachedProvider wrapper (LLM only)
│   ├── rate_limit_guard.py
│   ├── llm/
│   │   ├── llm_provider.py # LlmProvider base (chunked file scanning)
│   │   ├── gemini.py       # GeminiProvider
│   │   ├── groq.py         # GroqProvider
│   │   ├── ollama.py       # OllamaProvider (local, no API key)
│   │   └── prompts/
│   │       ├── gemini/deep.prompt
│   │       ├── groq/deep.prompt
│   │       ├── groq/fast.prompt
│   │       ├── ollama/qwen.prompt
│   │       └── ollama/mistral.prompt
│   └── static/
│       ├── static.py               # StaticProvider (general)
│       ├── static_security.py      # StaticSecurityProvider
│       ├── static_pipeline.py      # StaticPipelineProvider
│       ├── static_python.py        # StaticPythonProvider
│       ├── static_js.py            # StaticJSProvider
│       ├── static_ts_js.py         # StaticTSJSProvider
│       ├── static_docker.py        # StaticDockerProvider
│       ├── cpp_static.py           # StaticCppProvider
│       ├── csharp_static.py        # StaticCSharpProvider
│       ├── java_static.py          # StaticJavaProvider
│       ├── ruby_static.py          # StaticRubyProvider
│       ├── eslint.py               # ESLintProvider (JS/TS rules)
│       ├── k8s_static.py           # KubernetesStaticProvider
│       ├── k8s_runtime.py          # K8sRuntimeProvider (kind: infra)
│       ├── terraform_static.py     # TerraformStaticProvider
│       ├── terraform_plan.py       # TerraformPlanProvider
│       ├── supply_chain.py         # SupplyChainProvider
│       ├── trivy.py                # TrivyProvider (CVE scanning)
│       ├── sbom.py                 # SBOMProvider (Syft)
│       └── dead_code.py            # DeadCodeProvider
├── reporters/
│   ├── base.py             # Reporter ABC
│   ├── console.py          # ConsoleReporter (stdout, human-readable)
│   ├── github_pr.py        # GitHubPRReporter (PR comments)
│   ├── github_checks.py    # GitHubChecksReporter (check-run annotations)
│   ├── gitlab_mr.py        # GitLabMRReporter (MR comments)
│   └── formatter.py        # PR comment formatter
├── github/
│   └── pr_commenter.py     # GitHub PR comment logic
├── cache/                  # LLM response cache
├── rulesets/
│   └── eslint/             # ESLint rules for JS/TS
│       ├── base.mjs
│       ├── prod_safety.mjs
│       └── secrets.mjs
└── tests/
    ├── unit/
    └── integration/
```

---

## Core Contracts

### ProviderObservation

Every provider must return this. It is immutable (`frozen=True`):

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

    @abstractmethod
    def analyze(self, code: str, input_file: str = "") -> ProviderObservation:
        # LLM: analyze PR diff or code snippet
        ...

    @abstractmethod
    def collect(self, base_path: str = ".") -> ProviderObservation:
        # Static/infra: scan a directory
        # LLM: delegates to LlmProvider.analyze_files() (chunked scan)
        ...

    def analyze_pr(self, repo: str, pr_id: int, token: str) -> ProviderObservation:
        # Optional: direct GitHub PR analysis
        # Default raises NotImplementedError
        ...
```

### Observation

```python
@dataclass(frozen=True)
class Observation:
    category: str               # security | quality | architecture | ...
    signal: str                 # snake_case identifier
    confidence: float           # 0.0 – 1.0
    message: str
    severity: Optional[Severity]
    evidence: Optional[Dict[str, Any]]
    rule_id: Optional[str]
    location: Optional[Location]  # { file: str, line: Optional[int] }
```

### Decision

```python
@dataclass(frozen=True)
class Decision:
    mode: DecisionMode          # allow | advisory | blocking
    reasons: List[str]
    annotations: Optional[List[Annotation]]
```

**Exit code mapping:**

| mode | exit code |
|---|---|
| `allow` | 0 |
| `advisory` | 0 |
| `blocking` | 1 |

---

## Provider Inventory

### LLM Providers (`kind = "llm"`)

| Class | name | Prompt files | analyze_pr |
|---|---|---|---|
| `GeminiProvider` | `gemini` | `gemini/deep.prompt` | ✅ |
| `GroqProvider` | `groq` | `groq/deep.prompt`, `groq/fast.prompt` | ✅ |
| `OllamaProvider` | `ollama` | `ollama/qwen.prompt`, `ollama/mistral.prompt` | ❌ |

LLM providers support both `analyze()` (diff/snippet) and `collect()` (full repo via chunked scanning in `LlmProvider.analyze_files()`).

### Static Providers (`kind = "static"`)

| Class | name | Language/Target |
|---|---|---|
| `StaticProvider` | `static` | General |
| `StaticSecurityProvider` | `static_security` | Security patterns |
| `StaticPipelineProvider` | `static_pipeline` | CI/CD pipelines |
| `StaticPythonProvider` | `static_python` | Python AST |
| `StaticJSProvider` | `static_js` | JavaScript |
| `StaticTSJSProvider` | `static_ts_js` | TypeScript/JavaScript |
| `StaticDockerProvider` | `static_docker` | Dockerfile |
| `StaticCppProvider` | `cpp_static` | C++ |
| `StaticCSharpProvider` | `csharp_static` | C# |
| `StaticJavaProvider` | `java_static` | Java |
| `StaticRubyProvider` | `ruby_static` | Ruby |
| `ESLintProvider` | `eslint` | JS/TS (ESLint rules) |
| `KubernetesStaticProvider` | `k8s_static` | Kubernetes manifests |
| `TerraformStaticProvider` | `terraform_static` | Terraform HCL |
| `TerraformPlanProvider` | `terraform_plan` | Terraform plan JSON |
| `SupplyChainProvider` | `supply_chain` | Dependency risk |
| `TrivyProvider` | `trivy` | CVE scanning |
| `SBOMProvider` | `sbom` | SBOM generation (Syft) |
| `DeadCodeProvider` | `dead_code` | Unused code detection |

### Infra Providers (`kind = "infra"`)

| Class | name | Target |
|---|---|---|
| `K8sRuntimeProvider` | `k8s_runtime` | Kubernetes runtime |

---

## Cache

- **Purpose:** prevent repeated LLM token spending (not a performance cache)
- **Scope:** LLM providers only — never caches static providers
- **Integration:** via `CachedProvider` wrapper
- **Default location:** `.ai-slop-cache/`
- **Cache key components:** `provider_id` + `model` + `profile` + `policy_hash` + `normalized_input_fingerprint`
- **Invariant:** same key must NEVER trigger an LLM call twice

---

## Compliance Sidecar

- **Role:** runs alongside analysis, never inside engine
- **Enabled by:** `policy.compliance.enabled` or `--compliance` / `--compliance-only` flag
- **Capabilities:** forbidden license detection (GPL, AGPL), secret detection, GDPR/DSGVO data residency enforcement

| Profile | Description |
|---|---|
| `default` | inherits base compliance config |
| `eu` | enforces GPL/AGPL ban + EU residency |
| `eu-strict` | blocking enforcement |

---

## Reporters

| Class | Output | Description |
|---|---|---|
| `ConsoleReporter` | stdout | Human-readable, short or verbose mode |
| `GitHubPRReporter` | GitHub PR | Posts analysis as PR comment |
| `GitHubChecksReporter` | GitHub Checks | Creates check-run with annotations |
| `GitLabMRReporter` | GitLab MR | Posts analysis as MR comment |

All reporters receive `CheckReport` and are provider-agnostic.

---

## Non-Goals

- Automatic code fixing
- Code rewriting
- Business logic inside CLI
- Provider-specific policy logic
- Caching for non-LLM providers