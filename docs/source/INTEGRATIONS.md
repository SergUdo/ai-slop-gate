# CI/CD Integrations Guide

Complete guide for integrating ai-slop-gate into your CI/CD pipelines.

---

## Quick Reference

| Platform | Status | Documentation |
|----------|--------|---------------|
| GitHub Actions | Full Support | [See below](#github-actions) |
| GitLab CI | Full Support | [See below](#gitlab-ci) |
| Jenkins | Community | [See below](#jenkins) |
| Azure DevOps | Community | [See below](#azure-devops) |
| CircleCI | Community | [See below](#circleci) |

---

## Supported Providers

ai-slop-gate supports four analysis providers:

- **static** — Full static analysis (secrets, eval, Dockerfile, PII, TODO, supply-chain)
- **groq** — LLM analysis (local full-repo mode)
- **gemini** — LLM analysis (local full-repo mode)
- **ollama** — Local LLM (100% private)
- **compliance** — GDPR, EU residency, license, supply-chain compliance

---

## GitHub Actions

### Basic Setup

Create `.github/workflows/ai-slop-gate.yml`:

```yaml
name: AI Slop Gate
on:
  pull_request:
    branches: [main, develop]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run AI Slop Gate (Static)
        run: |
          docker run --rm \
            -v $(pwd):/src \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider static --policy /src/policy.yml --path /src
```

---

### Static Analysis Only

Fast, no API keys required:

```yaml
name: Static Analysis
on: [pull_request]

jobs:
  static:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Static Analysis
        run: |
          docker run --rm -v $(pwd):/src \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider static --path /src
```

---

### LLM Analysis with Cache

Saves tokens with persistent cache:

```yaml
name: LLM Analysis
on: [pull_request]

jobs:
  llm-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Cache AI Slop responses
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: ai-slop-cache-${{ hashFiles('**/*.py', '**/*.js') }}
          restore-keys: |
            ai-slop-cache-
      
      - name: Run LLM Analysis
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            -e GEMINI_API_KEY \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider gemini --llm-local --path /src
```

---

### PR Comment Integration

Post results directly to Pull Request:

```yaml
name: PR Analysis
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr-comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Analyze PR and Comment
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -e GITHUB_TOKEN \
            -e GEMINI_API_KEY \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run \
              --provider gemini \
              --github-repo ${{ github.repository }} \
              --pr-id ${{ github.event.pull_request.number }}
```

---

### Compliance Checks

GDPR, license, and supply chain audits:

```yaml
name: Compliance Gate
on: [pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Compliance Check
        run: |
          docker run --rm -v $(pwd):/src \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --compliance --path /src
```

---

### Full Analysis (Static + LLM + Compliance)

```yaml
name: Full Analysis
on: [pull_request]

jobs:
  full-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Cache responses
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: ai-slop-cache-${{ hashFiles('**/*') }}
      
      - name: Full Gate
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            -e GEMINI_API_KEY \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run \
              --provider static gemini \
              --llm-local \
              --compliance \
              --path /src
```

---

### GitHub Secrets Setup

Required secrets in repository settings:

1. Go to **Settings → Secrets and variables → Actions**
2. Add secrets:
   - `GEMINI_API_KEY` — Your Google Gemini API key
   - `GROQ_API_KEY` — Your Groq API key (if using Groq)
   - `GITHUB_TOKEN` — Auto-provided by GitHub (no setup needed)

---

## GitLab CI

### Overview

GitLab CI runs AI Slop Gate using the official Docker image:

`ghcr.io/sergudo/ai-slop-gate:latest`

### Requirements

#### Mandatory
- A `policy.yml` file in the root of your GitLab repository
- A `.gitlab-ci.yml` file that invokes the Docker image

**Policy Override:**
You can override the default policy file using the `--policy` flag. This is useful for monorepos or different environment stages (e.g., `audit-only.yml` vs `strict-production.yml`).

#### Optional (for LLM providers)
Set GitLab CI/CD variables:

- `GROQ_API_KEY`
- `GEMINI_API_KEY`

LLM jobs will run only if at least one of these variables is present.

---

### Basic Setup

Create `.gitlab-ci.yml`:

```yaml
stages:
  - analyze

static_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  script:
    - ai-slop-gate run --provider static --path .
  only:
    - merge_requests
```

---

### LLM Analysis with Cache

```yaml
llm_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GEMINI_API_KEY: $GEMINI_API_KEY
  cache:
    key: ai-slop-cache
    paths:
      - .ai-slop-cache/
  script:
    - ai-slop-gate run --provider gemini --llm-local --path .
  only:
    - merge_requests
```

---

### MR Comment Integration

Post results to Merge Request:

```yaml
mr_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GITLAB_TOKEN: $GITLAB_TOKEN
    GEMINI_API_KEY: $GEMINI_API_KEY
  script:
    - |
      ai-slop-gate run \
        --provider gemini \
        --gitlab-project $CI_PROJECT_PATH \
        --mr-iid $CI_MERGE_REQUEST_IID \
        --gitlab-url $CI_SERVER_URL
  only:
    - merge_requests
```

---

### Compliance Gate

```yaml
compliance:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  script:
    - ai-slop-gate run --compliance --path .
  only:
    - merge_requests
```

---

### Full Analysis

```yaml
full_analysis:
  stage: analyze
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GEMINI_API_KEY: $GEMINI_API_KEY
  cache:
    key: ai-slop-cache-$CI_COMMIT_REF_SLUG
    paths:
      - .ai-slop-cache/
  script:
    - |
      ai-slop-gate run \
        --provider static gemini \
        --llm-local \
        --compliance \
        --path .
  only:
    - merge_requests
```

---

### GitLab Variables Setup

1. Go to **Settings → CI/CD → Variables**
2. Add variables:
   - `GEMINI_API_KEY` — Your Gemini key (protected, masked)
   - `GROQ_API_KEY` — Your Groq key (protected, masked)
   - `GITLAB_TOKEN` — GitLab access token with API scope

---

### Recommended Configuration

```yaml
variables:
  SLOP_PROVIDERS: "gemini" 
  GEMINI_API_KEY: $GEMINI_API_KEY 
  GROQ_API_KEY: $GROQ_API_KEY

include:
  - remote: 'https://raw.githubusercontent.com/sergudo/ai-slop-gate/main/ci/gate-template.yml'
```

---

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        GEMINI_API_KEY = credentials('gemini-api-key')
    }
    
    stages {
        stage('AI Slop Gate') {
            steps {
                script {
                    docker.image('ghcr.io/sergudo/ai-slop-gate:latest').inside {
                        sh '''
                            ai-slop-gate run \
                              --provider static gemini \
                              --llm-local \
                              --path .
                        '''
                    }
                }
            }
        }
    }
}
```

---

### Scripted Pipeline

```groovy
node {
    stage('Checkout') {
        checkout scm
    }
    
    stage('Analysis') {
        withCredentials([string(credentialsId: 'gemini-api-key', variable: 'GEMINI_API_KEY')]) {
            docker.image('ghcr.io/sergudo/ai-slop-gate:latest').inside {
                sh 'ai-slop-gate run --provider gemini --llm-local'
            }
        }
    }
}
```

---

## Azure DevOps

### YAML Pipeline

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: Docker@2
  displayName: 'Run AI Slop Gate'
  inputs:
    command: 'run'
    arguments: |
      --rm \
      -v $(Build.SourcesDirectory):/src \
      -e GEMINI_API_KEY=$(GEMINI_API_KEY) \
      ghcr.io/sergudo/ai-slop-gate:latest \
      run --provider gemini --llm-local --path /src
```

---

## CircleCI

### Config Example

```yaml
version: 2.1

jobs:
  analyze:
    docker:
      - image: ghcr.io/sergudo/ai-slop-gate:latest
    steps:
      - checkout
      - run:
          name: AI Slop Gate
          command: |
            ai-slop-gate run \
              --provider static gemini \
              --llm-local \
              --path .

workflows:
  main:
    jobs:
      - analyze:
          filters:
            branches:
              only: /pull\/.*/
```

---

## Self-Hosted Runners

### GitHub Actions (Self-Hosted)

```yaml
name: Self-Hosted Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v3
      
      - name: Local Ollama Analysis
        run: |
          docker-compose up -d
          docker-compose run --rm gate \
            python -m ai_slop_gate.cli run \
            --provider ollama \
            --llm-local \
            --path /workspace
```

**Benefits:**
- 100% data privacy (code never leaves infrastructure)
- Zero API costs (local Ollama)
- GDPR compliant

---

### GitLab Runner (Docker)

```yaml
llm_local:
  stage: analyze
  tags:
    - docker
  services:
    - name: ollama/ollama:latest
      alias: ollama
  script:
    - ai-slop-gate run --provider ollama --llm-local
```

---

## Advanced Patterns

### Matrix Strategy (Multiple Providers)

```yaml
name: Multi-Provider Analysis
on: [pull_request]

jobs:
  analyze:
    strategy:
      matrix:
        provider: [static, gemini, groq]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Cache
        if: matrix.provider != 'static'
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: cache-${{ matrix.provider }}-${{ hashFiles('**/*') }}
      
      - name: Run ${{ matrix.provider }}
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            -e GEMINI_API_KEY -e GROQ_API_KEY \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider ${{ matrix.provider }} --llm-local --path /src
```

---

### Conditional Analysis (Changed Files)

```yaml
name: Smart Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Get changed files
        id: changed
        run: |
          echo "files=$(git diff --name-only origin/main...HEAD | tr '\n' ' ')" >> $GITHUB_OUTPUT
      
      - name: Run on changed files only
        if: steps.changed.outputs.files != ''
        run: |
          docker run --rm -v $(pwd):/src \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider static --path /src
```

---

### Scheduled Deep Analysis

```yaml
name: Weekly Deep Scan
on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM

jobs:
  deep-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Full LLM Scan
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -e GEMINI_API_KEY \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run \
              --provider static gemini groq \
              --llm-local \
              --compliance \
              --no-cache \
              --path /src
```

---

## Best Practices

### 1. Always Use Cache for LLM

```yaml
# Good: Saves 67% of API tokens
- uses: actions/cache@v3
  with:
    path: .ai-slop-cache
    key: cache-${{ hashFiles('**/*.py') }}
```

---

### 2. Separate Fast and Slow Jobs

```yaml
# Fast static check (always)
static:
  runs-on: ubuntu-latest
  steps:
    - run: ai-slop-gate run --provider static

# Slow LLM check (only on main branch)
llm:
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ai-slop-gate run --provider gemini --llm-local
```

---

### 3. Use Protected Secrets

```yaml
# Good: Secrets are masked in logs
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

# Bad: Never hardcode keys
env:
  GEMINI_API_KEY: "your-actual-key"
```

---

### 4. Fail Fast on Critical Issues

```yaml
- name: Critical Check
  run: |
    ai-slop-gate run \
      --provider static \
      --enforcement blocking \
      --path .
```

---

### 5. Advisory Mode for Development

```yaml
# Development branches: Advisory only
if: github.ref != 'refs/heads/main'
run: ai-slop-gate run --enforcement advisory

# Main branch: Blocking
if: github.ref == 'refs/heads/main'
run: ai-slop-gate run --enforcement blocking
```

---

## Troubleshooting

### Issue: "API rate limit exceeded"

**Solution:** Use cache and reduce frequency

```yaml
# Add cache
- uses: actions/cache@v3

# Or reduce runs
on:
  pull_request:
    types: [opened, ready_for_review]  # Not on every commit
```

---

### Issue: "Docker pull rate limit"

**Solution:** Use GitHub Container Registry

```yaml
# Good: No rate limits
docker pull ghcr.io/sergudo/ai-slop-gate:latest

# Avoid: Docker Hub rate limits
docker pull dockerhub/ai-slop-gate:latest
```

---

### Issue: "Secrets not found"

**Solution:** Check secret configuration

```bash
# GitHub: Settings → Secrets → Actions
# GitLab: Settings → CI/CD → Variables
```

---

### Issue: "Permission denied in container"

**Solution:** Fix volume permissions

```yaml
# Linux/macOS
- run: docker run --rm -v $(pwd):/src:rw ...

# Or set user
- run: docker run --rm --user $(id -u):$(id -g) ...
```

---

## Performance Optimization

### Cache Key Strategy

```yaml
# Good: Specific cache per file content
key: cache-${{ hashFiles('**/*.py', '**/*.js') }}

# Bad: Global cache (low hit rate)
key: global-cache
```

---

### Parallel Jobs

```yaml
jobs:
  static:
    runs-on: ubuntu-latest
    steps: [...]
  
  llm:
    runs-on: ubuntu-latest
    steps: [...]
  
  compliance:
    runs-on: ubuntu-latest
    steps: [...]
```

All run in parallel for faster feedback!

---

## Example Repositories

- [ai-slop-gate](https://github.com/SergUdo/ai-slop-gate) — Main repository
- [slop_test](https://github.com/SergUdo/slop_test) — Demo with violations

---

## Related Documentation

- [CLI Reference](CLI_REFERENCE.md)
- [Docker Guide](DOCKER.md)
- [Cache Guide](CACHE.md)
- [Policy Configuration](policy-configuration.md)

---

## Support

Integration issues? Check:
1. [GitHub Discussions](https://github.com/SergUdo/ai-slop-gate/discussions)
2. [Issue Tracker](https://github.com/SergUdo/ai-slop-gate/issues)
3. [Documentation](https://ai-slop-gate.readthedocs.io/)
