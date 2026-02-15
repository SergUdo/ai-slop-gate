## 🧪 Compliance Smoke Test — Report

**Status:** Completed  
**Policy:** Forbidden licenses → `GPL-2.0`, `GPL-3.0`, `AGPL-3.0`  
**AI Region:** US  

---
INFO:main:=== COMPLIANCE SMOKE TEST STARTED ===

INFO:main:Policy loaded. Forbidden licenses: ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0']

INFO:main:Testing with AI region: US

INFO:main:Generated mock manifest at /home/serhiy/slop_test/.slop/supply_chain.json

INFO:main:--- Found 16 issues ---

---

### ⚠️ Findings (16)

[MEDIUM] non_eu_endpoint at /home/serhiy/slop_test/sanctioned_supply_chain.py:12 -> Non‑EU endpoint detected.  
[MEDIUM] non_eu_endpoint at /home/serhiy/slop_test/sanctioned_supply_chain.py:14 -> Non‑EU endpoint detected.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/slop.js:24 -> Suspicious TODO comment found.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/compliance.py:1 -> Suspicious TODO comment found.  
[MEDIUM] pii_email at /home/serhiy/slop_test/compliance.py:7 -> Email address detected in source code.  
[HIGH] hardcoded_secret at /home/serhiy/slop_test/compliance.py:12 -> Potential hardcoded secret detected.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/compliance.py:14 -> Suspicious TODO comment found.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/compliance.py:24 -> Suspicious TODO comment found.  
[MEDIUM] non_eu_endpoint at /home/serhiy/slop_test/compliance.py:26 -> Non‑EU endpoint detected.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/compliance.py:30 -> Suspicious TODO comment found.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/compliance.py:40 -> Suspicious TODO comment found.  
[MEDIUM] pii_email at /home/serhiy/slop_test/slop.py:9 -> Email address detected in source code.  
[HIGH] hardcoded_secret at /home/serhiy/slop_test/slop.py:10 -> Potential hardcoded secret detected.  
[MEDIUM] suspicious_todo at /home/serhiy/slop_test/slop.py:44 -> Suspicious TODO comment found.  
[HIGH] hardcoded_secret at /home/serhiy/slop_test/.github/workflows/ai-slop-gate-analyze.yml:18 -> Potential hardcoded secret detected.  
[MEDIUM] data_residency_violation at policy.yml:None -> AI provider region 'US' does not satisfy required residency 'EU' (mode: advisory).  

---

### 🧨 Final Decision

FINAL DECISION: BLOCKING

---

INFO:main:✅ SUCCESS: Compliance pipeline detected violations.
