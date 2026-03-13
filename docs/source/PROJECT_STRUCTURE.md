# Project Structure

Overview of the **ai-slop-gate** directory layout.
For architectural decisions, see `ai_slop_gate_snapshot.json` (v7.4.0).

---

## Top-Level

```
ai-slop-gate/
├── ai_slop_gate/       # Core Python package
├── rulesets/           # Static analysis rule definitions
│   └── eslint/         # ESLint rules for JS/TS safety
├── ci/                 # CI configuration
├── docs/               # Project documentation
├── scripts/            # Utility and build scripts
├── action.yml          # GitHub Action definition
├── policy.yml          # Default policy configuration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── pytest.ini
├── eslint.config.js
├── package.json
└── renovate.json
```

---

## `ai_slop_gate/`

```
ai_slop_gate/
├── cli/                    # CLI layer (thin — arg parsing and wiring only)
│   ├── main.py             # Entrypoint: python -m ai_slop_gate.cli.main
│   ├── run.py              # run command: run_analysis()
│   ├── args.py             # Argument definitions
│   ├── context.py          # Runtime context object
│   ├── logger.py           # Logging configuration
│   └── utils.py
│
├── engine/
│   └── provider_factory.py # Instantiates providers by name from registry
│
├── domain/                 # Business logic — no IO
│   ├── observation.py      # Observation dataclass (immutable)
│   ├── observation_factory.py
│   ├── observation_result.py
│   ├── decision.py         # Decision dataclass (allow|advisory|blocking)
│   ├── policy.py           # PolicyRule dataclass
│   ├── policy_engine.py    # Evaluates List[Observation] → Decision
│   ├── checks.py           # CheckReport
│   ├── check_mapper.py
│   ├── signals.py          # Signal type definitions
│   ├── contracts.py        # Policy evaluation contracts
│   └── compliance/         # Compliance sidecar
│       ├── config.py
│       ├── detector.py
│       ├── enforcement.py
│       ├── gateway.py
│       ├── pipeline.py
│       ├── profile_resolver.py
│       ├── profiles.py
│       └── rules.py
│
├── providers/
│   ├── base.py             # BaseProvider ABC + ProviderObservation dataclass
│   ├── registry.py         # Provider registry
│   ├── cached_provider.py  # CachedProvider wrapper (LLM only)
│   ├── rate_limit_guard.py
│   │
│   ├── llm/                # LLM providers (kind = "llm")
│   │   ├── llm_provider.py # LlmProvider base: chunked file scanning, prompt loading
│   │   ├── gemini.py       # GeminiProvider
│   │   ├── groq.py         # GroqProvider
│   │   ├── ollama.py       # OllamaProvider (local, no API key required)
│   │   └── prompts/        # Provider-specific prompt files
│   │       ├── gemini/
│   │       │   └── deep.prompt
│   │       ├── groq/
│   │       │   ├── deep.prompt
│   │       │   └── fast.prompt
│   │       └── ollama/
│   │           ├── qwen.prompt
│   │           └── mistral.prompt
│   │
│   └── static/             # Static and infra providers
│       ├── static.py                   # StaticProvider
│       ├── static_security.py          # StaticSecurityProvider
│       ├── static_pipeline.py          # StaticPipelineProvider (CI/CD)
│       ├── static_python.py            # StaticPythonProvider (AST)
│       ├── static_js.py                # StaticJSProvider
│       ├── static_ts_js.py             # StaticTSJSProvider
│       ├── static_docker.py            # StaticDockerProvider
│       ├── cpp_static.py               # StaticCppProvider
│       ├── csharp_static.py            # StaticCSharpProvider
│       ├── java_static.py              # StaticJavaProvider
│       ├── ruby_static.py              # StaticRubyProvider
│       ├── eslint.py                   # ESLintProvider
│       ├── k8s_static.py               # KubernetesStaticProvider
│       ├── k8s_runtime.py              # K8sRuntimeProvider (kind = "infra")
│       ├── terraform_static.py         # TerraformStaticProvider
│       ├── terraform_plan.py           # TerraformPlanProvider
│       ├── supply_chain.py             # SupplyChainProvider
│       ├── trivy.py                    # TrivyProvider (CVE scanning)
│       ├── sbom.py                     # SBOMProvider (Syft, SPDX)
│       └── dead_code.py                # DeadCodeProvider
│
├── reporters/
│   ├── base.py             # Reporter ABC: report(CheckReport) -> None
│   ├── console.py          # ConsoleReporter
│   ├── github_pr.py        # GitHubPRReporter
│   ├── github_checks.py    # GitHubChecksReporter
│   ├── gitlab_mr.py        # GitLabMRReporter
│   ├── formatter.py        # PR comment formatting
│   └── stdout.py
│
├── github/
│   └── pr_commenter.py     # GitHub PR comment delivery
│
├── cache/                  # LLM response cache (file + memory backends)
│
├── fixtures/               # Test fixtures and sample data
│   └── k8s/                # Kubernetes fixture files
│
└── tests/
    ├── unit/
    │   ├── adapters/
    │   ├── cache/
    │   ├── cli/
    │   ├── domain/
    │   │   └── compliance/
    │   ├── loader/
    │   ├── policy_engine/
    │   ├── profiles/
    │   ├── providers/
    │   └── reporters/
    └── integration/
```

---

## `rulesets/eslint/`

Pre-configured ESLint rule sets for JavaScript/TypeScript static analysis:

| File | Purpose |
|---|---|
| `base.mjs` | Standard coding patterns |
| `prod_safety.mjs` | Production-ready safety checks |
| `secrets.mjs` | Leaked credential detection |
