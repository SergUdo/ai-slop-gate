python -m ai_slop_gate.cli run --policy policy.yml --provider static_pipeline --path /home/serhiy/slop_test
2026-02-08 13:36:12,174 [INFO] ai_slop_gate: --- AI SLOP GATE STARTING ---
2026-02-08 13:36:12,174 [INFO] ai_slop_gate: Loading policy file: policy.yml
2026-02-08 13:36:12,210 [INFO] ai_slop_gate: Providers selected: ['static_pipeline']
2026-02-08 13:36:12,211 [INFO] ai_slop_gate: Running provider: static_pipeline (static)
2026-02-08 13:36:13,233 [INFO] ai_slop_gate: Running compliance pipeline...
2026-02-08 13:36:13,236 [INFO] ai_slop_gate: Policy Verdict: ALLOW

=== AI SLOP GATE REPORT ===
Title: AI Slop Gate Report
Summary: Verdict: BLOCKING. Found 7 issues.
Verdict: BLOCKING
Total findings: 7

Issues:
  WARNING: slop.js:24 — [todo_found] Unresolved TODO found in code.
  WARNING: slop.py:42 — [todo_found] Unresolved TODO found in code.
  FAILURE: slop.py:23 — [dangerous_function] Dangerous function 'eval' detected.
  FAILURE: slop.js:43 — [dangerous_eval] Use of eval() detected.
  FAILURE: Dockerfile:8 — [extreme_privilege] Recursive chmod 777 detected in Dockerfile.
  WARNING: /home/serhiy/slop_test/slop.js:24 — [suspicious_todo] Suspicious TODO comment found.
  WARNING: /home/serhiy/slop_test/slop.py:42 — [suspicious_todo] Suspicious TODO comment found.

=== END OF REPORT ===

[INFO] ai_slop_gate: --- Execution Completed Successfully ---
