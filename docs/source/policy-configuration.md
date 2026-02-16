# Policy Configuration Guide

## Overview

The `policy.yml` file is the central configuration for AI Slop Gate. It defines:
- Which providers to use (static, LLM, compliance)
- AI provider settings (model, API keys)
- Security rules and severity levels
- Compliance requirements (GDPR, licenses, etc.)
- Enforcement mode (advisory, blocking)

---

## Quick Start

### Minimal policy.yml

```yaml
enforcement: advisory

ai_provider:
  name: gemini
  model: gemini-1.5-flash

rules:
  - signal: hardcoded_secret
    severity: critical
    action: block
```

### Initialize default policy

```bash
python -m ai_slop_gate.cli.main init
# Creates .ai-slop-gate.yml with sensible defaults
```

---

## File Structure

```yaml
# Enforcement mode (never, advisory, blocking)
enforcement: advisory

# AI Provider configuration
ai_provider:
  name: gemini
  model: gemini-1.5-flash
  region: us-central1
  models:
    gemini: gemini-1.5-flash
    groq: llama-3.1-70b-versatile
    ollama: llama3

# Compliance checks
compliance:
  enabled: true
  run_in_pr: false
  data_residency_mode: advisory
  
  license_audit:
    enabled: true
    forbidden_licenses:
      - AGPL-3.0
      - GPL-3.0
    severity: high
  
  security_audit:
    enabled: true
    detect_secrets: true
    detect_pii: true
    detect_suspicious_todos: true
    detect_non_eu_endpoints: true
    severity: critical
  
  gdpr_detection:
    enabled: true
    severity_email: medium
    severity_ssn: high

# Security rules
rules:
  - signal: hardcoded_secret
    severity: critical
    action: block
    tags: [security, secrets]
  
  - signal: eval_usage
    severity: high
    action: warn
    tags: [security, code-injection]
  
  - signal: pii_detected
    severity: high
    action: block
    tags: [privacy, gdpr]

# Code quality thresholds
code_quality:
  max_complexity: 10
  max_function_length: 50
  require_docstrings: false

# Infrastructure security
infrastructure_security:
  dockerfile_best_practices: true
  terraform_validation: true
  kubernetes_security: true

# AI Slop detection
ai_slop:
  detect_placeholder_comments: true
  detect_todo_pattern: true
  severity: medium

# File filtering
include_paths:
  - src/
  - lib/
  # Analyze only these directories
```

---

## AI Provider Configuration

### Supported Providers

```yaml
ai_provider:
  name: gemini  # or groq, ollama
  model: gemini-1.5-flash
```

### Multiple Models

Configure different models for different providers:

```yaml
ai_provider:
  name: gemini  # Default provider
  model: gemini-1.5-flash  # Default model
  
  models:
    gemini: gemini-1.5-flash      # Fast, cheap
    groq: llama-3.1-70b-versatile # Powerful, free tier
    ollama: llama3                # Local, free
```

Usage:
```bash
# Uses gemini with gemini-1.5-flash
python -m ai_slop_gate.cli.main run --provider gemini --llm-local

# Uses groq with llama-3.1-70b-versatile  
python -m ai_slop_gate.cli.main run --provider groq --llm-local

# Uses ollama with llama3
python -m ai_slop_gate.cli.main run --provider ollama --llm-local
```

### Regional Configuration

For GDPR compliance:

```yaml
ai_provider:
  name: gemini
  model: gemini-1.5-flash
  region: europe-west1  # EU region
```

---

## Enforcement Modes

Controls how AI Slop Gate responds to findings:

```yaml
enforcement: advisory  # never, advisory, blocking
```

| Mode | Behavior | Exit Code | Use Case |
|------|----------|-----------|----------|
| `never` | Report only, always pass | 0 | Monitoring, gradual rollout |
| `advisory` | Report and warn, but pass | 0 | Default, non-blocking |
| `blocking` | Report and fail on violations | 1 | Strict enforcement, CI/CD gates |

**Override at runtime:**
```bash
python -m ai_slop_gate.cli.main run \
  --provider static \
  --enforcement blocking
```

---

## Rules Configuration

### Rule Structure

```yaml
rules:
  - signal: <detection_type>     # What to detect
    severity: <level>             # critical, high, medium, low
    action: <action>              # block, warn, ignore
    tags: [tag1, tag2]            # Optional categorization
    message: "Custom message"     # Optional override
```

### Built-in Signals

#### Security

```yaml
# Hardcoded secrets
- signal: hardcoded_secret
  severity: critical
  action: block
  tags: [security, secrets]

# Code injection (eval, exec)
- signal: eval_usage
  severity: high
  action: warn
  tags: [security, code-injection]

# Unsafe deserialization
- signal: unsafe_deserialization
  severity: high
  action: block
  tags: [security]

# SQL injection patterns
- signal: sql_injection
  severity: critical
  action: block
  tags: [security, database]
```

#### Privacy & GDPR

```yaml
# Personal Identifiable Information
- signal: pii_detected
  severity: high
  action: block
  tags: [privacy, gdpr]

# Email addresses in code
- signal: email_in_code
  severity: medium
  action: warn
  tags: [privacy]

# Phone numbers
- signal: phone_number
  severity: medium
  action: warn
  tags: [privacy]

# SSN/Tax IDs
- signal: ssn_detected
  severity: high
  action: block
  tags: [privacy, gdpr]
```

#### Code Quality

```yaml
# TODO comments
- signal: suspicious_todo
  severity: low
  action: warn
  tags: [code-quality]

# High complexity
- signal: high_complexity
  severity: medium
  action: warn
  tags: [code-quality]

# Missing error handling
- signal: missing_error_handling
  severity: medium
  action: warn
  tags: [code-quality]
```

#### AI Slop

```yaml
# Placeholder comments
- signal: placeholder_comment
  severity: low
  action: warn
  tags: [ai-slop]
  # Examples: "TODO: implement", "FIXME: add logic"

# Copy-paste artifacts
- signal: duplicate_code
  severity: low
  action: warn
  tags: [ai-slop]
```

### Action Types

| Action | Behavior | When to Use |
|--------|----------|-------------|
| `block` | Fail build if detected | Critical security issues |
| `warn` | Report but continue | Important but not critical |
| `ignore` | Skip detection | Disabled rules |

---

## Compliance Configuration

### License Audit

Detect forbidden open-source licenses:

```yaml
compliance:
  license_audit:
    enabled: true
    forbidden_licenses:
      - AGPL-3.0        # Copyleft, viral
      - GPL-3.0         # Copyleft
      - SSPL-1.0        # Server Side Public License
      - Commons Clause  # Non-commercial restriction
    severity: high
    tags: [compliance, legal]
```

**Detected in:**
- `package.json` (npm)
- `requirements.txt` (pip)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `pom.xml` (Maven)

### Security Audit

```yaml
compliance:
  security_audit:
    enabled: true
    detect_secrets: true              # API keys, tokens
    detect_pii: true                  # Personal data
    detect_suspicious_todos: true     # TODO: remove admin access
    detect_non_eu_endpoints: true     # AWS us-east-1, etc.
    enforce_data_residency: true      # Block non-EU endpoints
    severity: critical
```

### GDPR Detection

```yaml
compliance:
  gdpr_detection:
    enabled: true
    severity_email: medium      # email@example.com
    severity_ssn: high          # SSN, tax IDs
    severity_todo: medium       # TODO: add GDPR consent
    severity_non_eu_endpoint: medium  # us-east-1.amazonaws.com
```

### Data Residency

For EU/GDPR compliance:

```yaml
compliance:
  data_residency_mode: blocking  # advisory or blocking
  
  security_audit:
    detect_non_eu_endpoints: true
    enforce_data_residency: true
```

**Detects:**
- AWS regions: `us-east-1`, `ap-southeast-1`
- GCP regions: `us-central1`, `asia-east1`
- Azure regions: `eastus`, `southeastasia`

**Allows:**
- `eu-west-1`, `europe-west1`, `westeurope`

---

## Code Quality Configuration

```yaml
code_quality:
  max_complexity: 10          # McCabe complexity
  max_function_length: 50     # Lines per function
  max_file_length: 500        # Lines per file
  require_docstrings: false   # Python docstrings
  require_type_hints: false   # Python type hints
```

---

## Infrastructure Security

```yaml
infrastructure_security:
  dockerfile_best_practices: true
  terraform_validation: true
  kubernetes_security: true
```

### Dockerfile Checks

- Base image security (avoid `:latest`)
- User privileges (don't run as root)
- Secrets in build args
- Layer caching issues

### Terraform Checks

- Hardcoded credentials
- Public access on resources
- Encryption at rest
- Backup policies

### Kubernetes Checks

- Security contexts
- Resource limits
- Network policies
- RBAC misconfigurations

---

## File Filtering

### Include Paths

Analyze only specific directories:

```yaml
include_paths:
  - src/
  - lib/
  - api/
```

Without `include_paths`, all files are analyzed.

### Exclude Patterns (via .gitignore)

AI Slop Gate respects `.gitignore`:

```gitignore
# Automatically excluded
node_modules/
.venv/
dist/
build/
*.pyc
```

---

## Advanced Examples

### Strict Security Policy

```yaml
enforcement: blocking

ai_provider:
  name: gemini
  model: gemini-1.5-flash

compliance:
  enabled: true
  security_audit:
    enabled: true
    detect_secrets: true
    detect_pii: true
    severity: critical

rules:
  - signal: hardcoded_secret
    severity: critical
    action: block
  
  - signal: pii_detected
    severity: critical
    action: block
  
  - signal: eval_usage
    severity: high
    action: block
  
  - signal: sql_injection
    severity: critical
    action: block

# Fail CI if ANY critical issue found
```

### GDPR-Compliant Policy

```yaml
enforcement: blocking

ai_provider:
  name: gemini
  model: gemini-1.5-flash
  region: europe-west1  # EU region

compliance:
  enabled: true
  data_residency_mode: blocking
  
  license_audit:
    enabled: true
    forbidden_licenses: [AGPL-3.0, GPL-3.0]
  
  security_audit:
    enabled: true
    detect_pii: true
    detect_non_eu_endpoints: true
    enforce_data_residency: true
  
  gdpr_detection:
    enabled: true
    severity_email: high
    severity_ssn: critical

rules:
  - signal: pii_detected
    severity: critical
    action: block
  
  - signal: email_in_code
    severity: high
    action: block
  
  - signal: non_eu_endpoint
    severity: high
    action: block

include_paths:
  - src/
  - api/
```

### Open Source Friendly Policy

```yaml
enforcement: advisory  # Don't block PRs

ai_provider:
  name: ollama     # Free, local
  model: llama3
  
  models:
    ollama: llama3              # Local (free)
    groq: llama-3.1-8b-instant  # Free tier
    gemini: gemini-1.5-flash    # Free quota

compliance:
  enabled: true
  license_audit:
    enabled: true
    forbidden_licenses:
      - AGPL-3.0  # Avoid viral licenses

rules:
  - signal: hardcoded_secret
    severity: high
    action: warn  # Warn, don't block
  
  - signal: suspicious_todo
    severity: low
    action: warn

# Lenient for contributors
```

---

## Environment Variables

Override policy settings via environment:

```bash
# API Keys
export GEMINI_API_KEY="your_key"
export GROQ_API_KEY="your_key"
export OPENAI_API_KEY="your_key"

# GitHub/GitLab tokens
export GITHUB_TOKEN="ghp_..."
export GITLAB_TOKEN="glpat_..."

# Override enforcement
export AI_SLOP_GATE_ENFORCEMENT=blocking
```

---

## Testing Your Policy

### Dry Run

```bash
# See what would be detected without enforcing
python -m ai_slop_gate.cli.main run \
  --provider static \
  --policy policy.yml \
  --enforcement never
```

### Verbose Output

```bash
# See detailed detection reasons
python -m ai_slop_gate.cli.main run \
  --provider static \
  --policy policy.yml \
  --verbose
```

### Single Rule Testing

Create minimal test policy:

```yaml
# test-policy.yml
enforcement: advisory

rules:
  - signal: hardcoded_secret
    severity: critical
    action: block
```

```bash
python -m ai_slop_gate.cli.main run \
  --provider static \
  --policy test-policy.yml \
  --path ./test-files/
```

---

## Troubleshooting

### Policy Not Loading

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('policy.yml'))"

# Check file permissions
ls -l policy.yml
```

### Rules Not Triggering

```bash
# Run with verbose logging
python -m ai_slop_gate.cli.main run \
  --provider static \
  --policy policy.yml \
  --verbose 2>&1 | grep -A5 "signal"
```

### Wrong Enforcement Mode

```bash
# Check effective enforcement
python -m ai_slop_gate.cli.main run \
  --provider static \
  --verbose 2>&1 | grep "enforcement"
```

---

## Best Practices

1. **Start with `advisory` mode**
   - Monitor findings before blocking

2. **Use `blocking` in CI/CD**
   - Prevent bad code from merging

3. **Version control your policy**
   ```bash
   git add policy.yml
   git commit -m "chore: update security policy"
   ```

4. **Document custom rules**
   ```yaml
   rules:
     - signal: custom_pattern
       severity: high
       action: block
       # Why: Our internal security requirement
       # References: SECURITY.md
   ```

5. **Test policy changes**
   ```bash
   # Before merging policy changes
   python -m ai_slop_gate.cli.main run \
     --policy policy.yml \
     --enforcement never
   ```

6. **Use tags for organization**
   ```yaml
   rules:
     - signal: hardcoded_secret
       tags: [security, pci-dss, soc2]
   ```

---

## Migration Guide

### From v1.x to v2.x

```yaml
# Old (v1.x)
provider: gemini
model: gemini-pro

# New (v2.x)
ai_provider:
  name: gemini
  model: gemini-1.5-flash
```

### Adding Compliance

```yaml
# Add to existing policy.yml
compliance:
  enabled: true
  license_audit:
    enabled: true
    forbidden_licenses: [AGPL-3.0]
```

---

## Next Steps

- [Cache Integration Guide](cache-integration.md)
- [CI/CD Setup Guide](cicd-setup.md)
- [Contributing Guidelines](../CONTRIBUTING.md)