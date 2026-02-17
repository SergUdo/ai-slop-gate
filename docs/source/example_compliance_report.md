# Compliance Audit Example

## Execution Information

- **Timestamp:** 2026-02-15 11:11:37
- **Policy file:** policy.yml
- **Mode:** Compliance-only
- **Repository:** /home/serhiy/slop_test

## Execution Mode Detection

- Providers requested: (none)
- --compliance flag: True
- --compliance-only flag: False
- GitHub PR mode: False
- GitLab MR mode: False
- policy.compliance.enabled: True
- policy.compliance.run_in_pr: False

## Analysis Steps

### Step 1: Provider Analysis
**Status:** Skipped (compliance-only mode)

### Step 2: Compliance Checks
**Status:** Running

#### License Audit Configuration
- **Enabled:** True
- **Forbidden licenses:** GPL-2.0, GPL-3.0, AGPL-3.0
- **Severity:** high
- **Tags:** license, supply-chain, legal

#### Findings

**GPL License Violations (6 total):**

1. GPL license detected in requirements.txt (package: gpl-python-lib): GPL-3.0
   - Location: requirements.txt:6
   - Severity: FAILURE

2. AGPL license detected in requirements.txt (package: agpl-django-app): AGPL-3.0
   - Location: requirements.txt:7
   - Severity: FAILURE

3. GPL license detected in requirements.txt (package: readline-gpl): GPL-2.0
   - Location: requirements.txt:8
   - Severity: FAILURE

4. GPL license detected in package.json (explicit license field): GPL-3.0
   - Location: package.json:1
   - Severity: FAILURE

5. GPL license detected in package.json (licenses array): GPL-3.0
   - Location: package.json:1
   - Severity: FAILURE

6. GPL license detected in package.json (file content scan): GPL-3.0
   - Location: package.json:1
   - Severity: FAILURE

### Step 3: Policy Evaluation
- **Total observations:** 6
- **Policy Verdict:** BLOCKING

---

## Final Report

### AI SLOP GATE REPORT

**Title:** AI Slop Gate Report
**Summary:** Verdict: BLOCKING. Found 6 issues.
**Verdict:** BLOCKING
**Total findings:** 6

### Issues

1. **FAILURE:** requirements.txt:6 - [gpl_license_detected] GPL license detected in requirements.txt (package: gpl-python-lib): GPL-3.0

2. **FAILURE:** requirements.txt:7 - [agpl_license_detected] AGPL license detected in requirements.txt (package: agpl-django-app): AGPL-3.0

3. **FAILURE:** requirements.txt:8 - [gpl_license_detected] GPL license detected in requirements.txt (package: readline-gpl): GPL-2.0

4. **FAILURE:** package.json:1 - [gpl_license_detected] GPL license detected in package.json (explicit license field): GPL-3.0

5. **FAILURE:** package.json:1 - [gpl_license_detected] GPL license detected in package.json (licenses array): GPL-3.0

6. **FAILURE:** package.json:1 - [gpl_license_detected] GPL license detected in package.json (file content scan): GPL-3.0

---

## Summary

**Execution Status:** Completed Successfully
**Exit Code:** 1 (BLOCKING violations found)
**Total execution time:** ~0.04s

**Compliance checks performed:**
- License audit: FAIL
- Forbidden licenses found: 6
- GPL/AGPL violations in both Python and JavaScript dependencies

**Recommendation:** Remove or replace dependencies with forbidden licenses before merging.