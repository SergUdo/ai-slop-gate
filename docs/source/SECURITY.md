# Security Policy

## Overview
AI Slop Gate is committed to providing a secure, transparent, and resilient tool for AI-assisted compliance. This document outlines our security practices, vulnerability reporting process, and compliance status.

## Security Controls (Automated)
We monitor OS-level licenses but allow standard GPL/LGPL components required for the Debian runtime environment, as they do not impose requirements on our proprietary application logic.
We employ a "Shift-Left" security approach by integrating the following gates directly into our CI/CD pipeline:

| Control | Tool | Purpose |
| :--- | :--- | :--- |
| **SAST** | AI Reasoning | Static analysis of source code for logic flaws and secrets. |
| **SCA** | Trivy | Continuous scanning of container images for known vulnerabilities (CVEs). |
| **SBOM** | Syft | Generation of a Software Bill of Materials (SPDX) for supply chain transparency. |
| **License Audit** | Trivy | Automated blocking of unauthorized licenses (e.g., AGPL) to ensure legal compliance. |

## Supported Versions
Only the latest version of AI Slop Gate is supported for security updates.

| Version | Supported |
| :--- | :--- |
| Latest (Main) | ✅ Yes |
| < Latest | ❌ No |

## Reporting a Vulnerability
If you discover a security vulnerability, please do not open a public issue. Instead, follow these steps:

1. **Report:** Send an email to [YOUR_EMAIL@example.com] or use GitHub's private vulnerability reporting feature.
2. **Acknowledgement:** You will receive an acknowledgement within 48 hours.
3. **Disclosure:** We follow a 90-day responsible disclosure policy. We will coordinate a fix and public announcement.

## Compliance & Standards
### EU AI Act Compliance
- **Transparency:** Every container image is accompanied by an SPDX SBOM.
- **Robustness:** Images are hardened (Debian-slim with security upgrades) and scanned for `CRITICAL` vulnerabilities.

### Supply Chain Security (DORA)
We enforce strictly defined build environments and maintain a history of security scans to ensure the integrity of our delivery pipeline.

## License Policy
We permit the use of permissive licenses (MIT, Apache 2.0, BSD) and standard OS-level copyleft licenses (GPL, LGPL). We strictly prohibit the inclusion of licenses that enforce source disclosure for SaaS/cloud environments (e.g., AGPL, SSPL) without explicit approval.