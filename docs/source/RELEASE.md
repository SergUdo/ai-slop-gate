# RELEASE

This document explains how to verify and use release artifacts produced by the release pipeline.

## What the release pipeline produces
- **Docker images** published to GHCR with tags: `vX.Y.Z`, `sha-<short>`, and `latest` (for default branch).
- **Multi-arch images** supporting `linux/amd64` and `linux/arm64`.
- **Signed images** using `cosign` (key-pair signing).
- **SBOM** in SPDX JSON format (`sbom-spdx.json`).
- **Vulnerability report** from Trivy in SARIF format (`trivy-results.sarif`).
- **CHANGELOG.md** generated from commit messages.
- **GitHub Release** optionally created with changelog content.

## Quick verification commands

### Verify image is published
```bash
# Example
docker pull ghcr.io/<owner>/<repo>:v1.2.3
```

### Verify cosign signature
```bash
# Verify using public key file cosign.pub
cosign verify --key cosign.pub ghcr.io/<owner>/<repo>:v1.2.3
```

### Inspect SBOM
```bash
# View SPDX JSON
jq . sbom-spdx.json
```

### Open Trivy SARIF

Download `trivy-results.sarif` from the workflow artifacts or check the Security tab in GitHub.

### How versioning works

**Commit message conventions**:

- `fix`: → patch

- `feat`: → minor

- `BREAKING CHANGE` → major

The pipeline determines the next semantic version, creates a `vX.Y.Z` tag, and publishes the release artifacts.

### Secrets required for release pipeline

**GHCR_TOKEN** — write access to GitHub Packages.

**COSIGN_PRIVATE_KEY** — contents of cosign.key (private key).

**COSIGN_PASSWORD** — password protecting the private key.

**GITHUB_TOKEN** — used by actions to create releases and changelogs (provided automatically).

### Troubleshooting

- If `cosign verify` fails, ensure `cosign.pub` matches the public key used to sign and that the correct tag is used.

- If images are missing for `arm64`, ensure `docker buildx` builder supports multi-arch and platforms includes `linux/arm64`.

- If changelog is empty, check commit message formats between the previous tag and the new tag.

### Notes
Release pipeline runs on tag push  `(v*.*.*)` or manual dispatch.

CI pipeline remains responsible for per-commit checks; release pipeline validates the final release artifact.