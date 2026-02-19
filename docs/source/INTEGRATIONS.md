# CI/CD Integrations Guide

Complete guide for integrating ai-slop-gate into your CI/CD pipelines.

---

## Quick Reference

| Platform | Status |
|---|---|
| GitHub Actions | Full Support |
| GitLab CI | Full Support |
| Jenkins | Community |
| Azure DevOps | Community |
| CircleCI | Community |

---

## Before You Start

### `--policy` is required for every `run` command

`policy.yml` controls which directories are sent to providers via `include_paths`.
Without it, LLM providers receive the entire repository and fail with token-limit errors.

**Policy discovery order:**
1. `--policy <explicit path>` — always wins
2. `<--path>/policy.yml` — auto-discovered if the scanned repo has its own policy
3. `./policy.yml` — current working directory
4. Bundled default (permissive, no `include_paths` — not safe for LLM providers)

**Recommendation:** every repository you scan should have its own minimal `policy.yml`
(see the [Minimal Policy](#minimal-policy-for-a-target-repository) section below).

### Enforcement levels

| Flag | Behaviour | When to use |
|---|---|---|
| `--enforcement advisory` | Findings reported, CI always passes | Initial rollout, noise tuning |
| `--enforcement blocking` | CI fails on violations | Production gate |
| `--enforcement never` | Report only, exit 0 always | Dry-run / debugging |

Start with `advisory`. Switch to `blocking` once the baseline is clean.

---

## Minimal Policy for a Target Repository

Place this `policy.yml` in the root of the repository you want to scan.
The gate will auto-discover it when you pass `--path` pointing to that repository.

```yaml
# policy.yml — minimal config for the scanned repository
version: "v1.4"
project_name: "my-project"

enforcement: advisory   # start here; tighten to blocking after tuning

# Required for LLM providers.
# Without include_paths, the entire repo is sent to the API → token limit errors.
include_paths:
  - src   # adjust to your source directory

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

## Supported Providers

| Provider | API key required | Mode |
|---|---|---|
| `static` / `static_pipeline` | No | Deterministic — secrets, Dockerfile, PII, supply-chain |
| `groq` | `GROQ_API_KEY` | LLM — PR diff or `--llm-local` |
| `gemini` | `GEMINI_API_KEY` | LLM — PR diff or `--llm-local` |
| `ollama` | No (local) | LLM — local only, 100% private |

LLM providers in `--llm-local` mode automatically exclude: `.env`, `policy.yml`,
`docs/`, `scripts/`, lock files, minified bundles.

---

## GitHub Actions

### Recommended Workflow Structure

The official workflow uses **parallel jobs** so static, LLM, and compliance steps
run independently and never block each other by accident.
Use `--enforcement advisory` while tuning; switch individual jobs to `blocking` when ready.

```yaml
name: AI Slop Gate Analyze

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

jobs:
  # ──────────────────────────────────────────────────────────────────────────
  # STATIC ANALYSIS — runs on every push and PR
  # Fast, no API key required. Trivy and Syft must be installed for
  # vulnerability scanning and SBOM generation.
  # ──────────────────────────────────────────────────────────────────────────
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install ai-slop-gate
        run: pip install -e .

      - name: Install Trivy
        run: |
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
            | sh -s -- -b /usr/local/bin v0.50.4

      - name: Install Syft
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
            | sh -s -- -b /usr/local/bin

      - name: Run Static Analysis
        run: |
          python -m ai_slop_gate.cli run \
            --provider static \
            --policy policy.yml \
            --path . \
            --enforcement advisory \
            --verbose

  # ──────────────────────────────────────────────────────────────────────────
  # LLM ANALYSIS — PR only
  # Groq analyses the local source code. policy.yml must define include_paths
  # or the run aborts before sending anything to the API.
  # ──────────────────────────────────────────────────────────────────────────
  llm-analysis:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install ai-slop-gate
        run: pip install -e .

      - name: Cache LLM responses
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: llm-cache-${{ hashFiles('**/*.py', '**/*.js', '**/*.ts') }}
          restore-keys: llm-cache-

      - name: Run Groq LLM Analysis
        env:
          GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}
        run: |
          python -m ai_slop_gate.cli run \
            --provider groq \
            --llm-local \
            --policy policy.yml \
            --path . \
            --enforcement advisory \
            --verbose

  # ──────────────────────────────────────────────────────────────────────────
  # COMPLIANCE — runs on every push and PR
  # License audit, GDPR, secret detection. Scoped to application code only.
  # ──────────────────────────────────────────────────────────────────────────
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install ai-slop-gate
        run: pip install -e .

      - name: Run Compliance Check
        run: |
          python -m ai_slop_gate.cli run \
            --compliance \
            --policy policy.yml \
            --path ai_slop_gate \
            --enforcement advisory \
            --verbose

  # ──────────────────────────────────────────────────────────────────────────
  # PR COMMENT — PR only, runs after the other jobs
  # Posts a consolidated Groq report as a PR comment.
  # ──────────────────────────────────────────────────────────────────────────
  pr-comment:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    needs: [static-analysis, llm-analysis, compliance]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install ai-slop-gate
        run: pip install -e .

      - name: Restore LLM cache
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: llm-cache-${{ hashFiles('**/*.py', '**/*.js', '**/*.ts') }}
          restore-keys: llm-cache-

      - name: Post PR Comment
        env:
          GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m ai_slop_gate.cli run \
            --provider groq \
            --github-repo ${{ github.repository }} \
            --pr-id ${{ github.event.pull_request.number }} \
            --policy policy.yml \
            --path . \
            --enforcement advisory
```

---

### Minimal Static-Only Workflow

Fast gate with no API keys required:

```yaml
name: Static Analysis
on: [pull_request]

jobs:
  static:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -e .
      - run: |
          python -m ai_slop_gate.cli run \
            --provider static \
            --policy policy.yml \
            --enforcement advisory
```

---

### GitHub PR Comment (All-in-One)

```yaml
name: PR Analysis
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr-comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -e .

      - name: Analyze PR and Post Comment
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}
        run: |
          python -m ai_slop_gate.cli run \
            --provider groq \
            --github-repo ${{ github.repository }} \
            --pr-id ${{ github.event.pull_request.number }} \
            --policy policy.yml \
            --enforcement advisory
```

> `--github-repo`, `--pr-id`, and `GITHUB_TOKEN` are all required together for PR commenting.
> In PR mode the LLM receives only the diff — `include_paths` guard is skipped.

---

### GitHub Secrets Setup

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `SLOPE_GATE_GROQ` | Groq API key |
| `GEMINI_API_KEY` | Google Gemini API key (if using Gemini) |
| `GITHUB_TOKEN` | Auto-provided by GitHub — no setup needed |

---

## GitLab CI

### Recommended `.gitlab-ci.yml`

```yaml
stages:
  - analyze

variables:
  GROQ_API_KEY: $GROQ_API_KEY
  GITLAB_TOKEN: $GITLAB_TOKEN

# ── Static analysis ─────────────────────────────────────────────────────────
static_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  script:
    - ai-slop-gate run
        --provider static
        --policy policy.yml
        --path .
        --enforcement advisory
        --verbose
  only:
    - merge_requests
    - main

# ── LLM analysis ─────────────────────────────────────────────────────────────
# policy.yml must define include_paths — otherwise the job aborts before any
# files are sent to the API.
llm_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GROQ_API_KEY: $GROQ_API_KEY
  cache:
    key: llm-cache-$CI_COMMIT_REF_SLUG
    paths:
      - .ai-slop-cache/
  script:
    - ai-slop-gate run
        --provider groq
        --llm-local
        --policy policy.yml
        --path .
        --enforcement advisory
  only:
    - merge_requests

# ── MR comment ───────────────────────────────────────────────────────────────
mr_comment:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GITLAB_TOKEN: $GITLAB_TOKEN
    GROQ_API_KEY: $GROQ_API_KEY
  script:
    - ai-slop-gate run
        --provider groq
        --gitlab-project $CI_PROJECT_PATH
        --mr-iid $CI_MERGE_REQUEST_IID
        --gitlab-url $CI_SERVER_URL
        --policy policy.yml
        --enforcement advisory
  only:
    - merge_requests

# ── Compliance ───────────────────────────────────────────────────────────────
compliance:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  script:
    - ai-slop-gate run
        --compliance
        --policy policy.yml
        --path .
        --enforcement advisory
  only:
    - merge_requests
    - main
```

---

### GitLab Variables Setup

Go to **Settings → CI/CD → Variables** and add (protected + masked):

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `GEMINI_API_KEY` | Google Gemini API key (if using Gemini) |
| `GITLAB_TOKEN` | GitLab access token with `api` scope |

---

## Jenkins

```groovy
pipeline {
    agent any
    environment {
        GROQ_API_KEY = credentials('groq-api-key')
    }
    stages {
        stage('AI Slop Gate') {
            steps {
                sh '''
                    pip install -e .
                    python -m ai_slop_gate.cli run \
                      --provider static groq \
                      --llm-local \
                      --policy policy.yml \
                      --enforcement advisory \
                      --path .
                '''
            }
        }
    }
}
```

---

## Azure DevOps

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- script: pip install -e .
  displayName: 'Install ai-slop-gate'

- script: |
    python -m ai_slop_gate.cli run \
      --provider static \
      --policy policy.yml \
      --enforcement advisory \
      --path .
  env:
    GROQ_API_KEY: $(GROQ_API_KEY)
  displayName: 'Run AI Slop Gate'
```

---

## CircleCI

```yaml
version: 2.1

jobs:
  analyze:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install ai-slop-gate
          command: pip install -e .
      - restore_cache:
          keys:
            - llm-cache-{{ checksum "**/*.py" }}
      - run:
          name: Static Analysis
          command: |
            python -m ai_slop_gate.cli run \
              --provider static \
              --policy policy.yml \
              --enforcement advisory
      - save_cache:
          key: llm-cache-{{ checksum "**/*.py" }}
          paths:
            - .ai-slop-cache

workflows:
  main:
    jobs:
      - analyze
```

---

## Advanced Patterns

### Progressive Enforcement

Run advisory on feature branches, blocking on main:

```yaml
- name: Run Analysis
  run: |
    ENFORCEMENT="advisory"
    if [ "${{ github.ref }}" = "refs/heads/main" ]; then
      ENFORCEMENT="blocking"
    fi
    python -m ai_slop_gate.cli run \
      --provider static \
      --policy policy.yml \
      --enforcement $ENFORCEMENT
```

---

### Matrix Strategy (Multiple Providers in Parallel)

```yaml
jobs:
  analyze:
    strategy:
      fail-fast: false
      matrix:
        provider: [static, groq]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -e .

      - name: Cache (LLM only)
        if: matrix.provider != 'static'
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: llm-cache-${{ matrix.provider }}-${{ hashFiles('**/*.py') }}

      - name: Run ${{ matrix.provider }}
        env:
          GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}
        run: |
          EXTRA=""
          if [ "${{ matrix.provider }}" != "static" ]; then
            EXTRA="--llm-local"
          fi
          python -m ai_slop_gate.cli run \
            --provider ${{ matrix.provider }} \
            --policy policy.yml \
            --enforcement advisory \
            $EXTRA
```

---

### Scheduled Deep Scan (Weekly)

```yaml
name: Weekly Deep Scan
on:
  schedule:
    - cron: '0 2 * * 1'   # Every Monday at 2 AM

jobs:
  deep-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -e .

      - name: Full Scan (no cache — fresh results)
        env:
          GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}
        run: |
          python -m ai_slop_gate.cli run \
            --provider static groq \
            --llm-local \
            --compliance \
            --policy policy.yml \
            --no-cache \
            --enforcement advisory \
            --verbose
```

---

## Best Practices

### 1. Always include `--policy` with `include_paths`

```bash
# ✅ GOOD — scoped to source directory
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml

# ❌ BAD — entire repo sent to the API, token limit hit
python -m ai_slop_gate.cli run --provider groq --llm-local
```

### 2. Start with `advisory`, tighten later

```bash
# Step 1: understand findings
--enforcement advisory

# Step 2: once baseline is clear
--enforcement blocking
```

### 3. Always cache LLM responses in CI

```yaml
- uses: actions/cache@v3
  with:
    path: .ai-slop-cache
    key: llm-cache-${{ hashFiles('**/*.py', '**/*.js') }}
    restore-keys: llm-cache-
```

### 4. Use secrets, never inline API keys

```yaml
# ✅ GOOD
env:
  GROQ_API_KEY: ${{ secrets.SLOPE_GATE_GROQ }}

# ❌ BAD — visible in logs and git history
env:
  GROQ_API_KEY: "gsk_actual_key_here"
```

### 5. Run static and LLM jobs in parallel

Static analysis is fast (~5s). LLM analysis takes ~15s on first run (cached after).
Running them as separate parallel jobs gives faster overall feedback.

---

## Troubleshooting

### "the following arguments are required: --policy"

Every `run` command requires `--policy`. Add it:

```bash
python -m ai_slop_gate.cli run --provider static --policy policy.yml
```

### "LLM providers require include_paths"

Your `policy.yml` is missing `include_paths`. Add it:

```yaml
include_paths:
  - src
```

### "API rate limit exceeded"

Enable cache (default) and avoid `--no-cache` in CI. Cache persists between runs
with `actions/cache`.

### "Trivy / Syft binary not found"

Install them explicitly in the workflow before running static analysis:

```yaml
- name: Install Trivy
  run: |
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
      | sh -s -- -b /usr/local/bin v0.50.4

- name: Install Syft
  run: |
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
      | sh -s -- -b /usr/local/bin
```

---

## Related Documentation

- [CLI Reference](CLI_REFERENCE.md) — All flags and options
- [Docker Guide](DOCKER.md) — Docker usage
- [Cache Guide](CACHE.md) — Cache configuration
- [Policy Configuration](policy-configuration.md) — Policy settings

---

## Support

- [GitHub Discussions](https://github.com/SergUdo/ai-slop-gate/discussions)
- [Issue Tracker](https://github.com/SergUdo/ai-slop-gate/issues)
- [Documentation](https://ai-slop-gate.readthedocs.io/)
