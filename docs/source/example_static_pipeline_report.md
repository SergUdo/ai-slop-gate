# Static Pipeline Analysis Example

## Execution Information

- **Timestamp:** 2026-02-15 11:12:53
- **Policy file:** policy.yml
- **Mode:** Static analysis with compliance
- **Repository:** /home/serhiy/slop_test_trivy

## Execution Mode Detection

- Providers requested: ['static']
- --compliance flag: False
- GitHub PR mode: False
- GitLab MR mode: False
- policy.compliance.enabled: True

## Analysis Steps

### Step 1: Static Provider Analysis

#### Trivy Vulnerability Scan
- **Severities scanned:** CRITICAL, HIGH
- **Scan duration:** ~9s
- **Vulnerabilities found:** 67

#### Static Pipeline Aggregation
- **Raw observations:** 593
- **Aggregated observations:** 73
- **Duration:** ~3.5s

### Step 2: Compliance Checks
**Status:** Running (policy.compliance.enabled=true)

#### License Audit
- **Forbidden licenses:** GPL-2.0, GPL-3.0, AGPL-3.0
- **Violations found:** 0

### Step 3: Policy Evaluation
- **Total observations:** 73
- **Policy Verdict:** BLOCKING

---

## Vulnerability Findings (Sample)

### Critical/High NPM Vulnerabilities

**async@2.6.3**
- CVE-2021-43138: Prototype Pollution in async

**axios@0.21.0**
- CVE-2021-3749: Regular expression denial of service in trim function
- CVE-2025-27152: Possible SSRF and Credential Leakage via Absolute URL
- CVE-2026-25639: Denial of Service via __proto__ Key in mergeConfig

**body-parser@1.19.0**
- CVE-2024-45590: Denial of Service Vulnerability

**json-schema@0.2.3**
- CVE-2021-3918: Prototype pollution vulnerability

**lodash@4.17.19**
- CVE-2021-23337: Command injection via template

**minimist@1.2.0**
- CVE-2021-44906: Prototype pollution

**moment@2.29.0**
- CVE-2022-24785: Path traversal in moment.locale
- CVE-2022-31129: Inefficient parsing algorithm resulting in DoS

**qs@6.7.0 & 6.9.4**
- CVE-2022-24999: Prototype poisoning causes hang
- CVE-2025-15284: Denial of Service via improper input validation

### Critical/High Python Vulnerabilities

**certifi@2020.12.5**
- CVE-2023-37920: Removal of e-Tugra root certificate

**cryptography@3.2**
- CVE-2020-36242: Integer overflow in symmetric encryption
- CVE-2023-0286: X.400 address type confusion
- CVE-2023-50782: Bleichenbacher timing oracle attack
- CVE-2026-26007: Subgroup Attack Due to Missing Validation

**django@3.1.0**
- CVE-2021-35042: SQL injection via unsanitized QuerySet.order_by()
- CVE-2025-64459: Django SQL injection
- CVE-2020-24583: Incorrect permissions on intermediate directories
- CVE-2021-31542: Potential directory-traversal via uploaded files
- CVE-2025-57833: SQL injection in FilteredRelation column aliases

**pillow@8.0.0** (Multiple critical vulnerabilities)
- CVE-2021-25289: Insufficient fix for CVE-2020-35654
- CVE-2021-34552: Buffer overflow in image convert function
- CVE-2022-22817: PIL.ImageMath.eval allows evaluation of arbitrary expressions
- CVE-2023-50447: Arbitrary Code Execution via environment parameter
- Multiple buffer overflow and memory allocation issues

---

## Final Report

### AI SLOP GATE REPORT

**Title:** AI Slop Gate Report
**Summary:** Verdict: BLOCKING. Found 73 issues.
**Verdict:** BLOCKING
**Total findings:** 73

### Issue Categories

1. **npm packages:** 20 vulnerabilities
   - async, axios, body-parser, json-schema, lodash, minimist, moment, node-fetch, path-to-regexp, qs, serialize-javascript, underscore, validator

2. **Python packages:** 53 vulnerabilities
   - certifi, cryptography, django, pillow

### Severity Distribution

- **CRITICAL:** 25 vulnerabilities
- **HIGH:** 48 vulnerabilities

---

## Summary

**Execution Status:** Completed Successfully
**Exit Code:** 1 (BLOCKING violations found)
**Total execution time:** ~13s

**Analysis performed:**
- Trivy vulnerability scan: 67 CVEs detected
- Static code analysis: 73 observations aggregated
- License compliance: PASS (0 forbidden licenses)
- Final verdict: BLOCKING (critical vulnerabilities present)

**Recommendation:** 
- Update outdated dependencies (async, axios, django, pillow)
- Review security advisories for each CVE
- Consider using dependency scanning in CI/CD pipeline