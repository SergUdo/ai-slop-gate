📁 [Ollama Mode] Scanning repo: /home/serhiy/slop_test
🧩 Created 6 chunks for analysis

🚀 Sending chunk 1/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 1: found 1 problems
⏱️ Chunk 1 response in 117.87s
------------------------------------------------------------
🚀 Sending chunk 2/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 2: found 1 problems
⏱️ Chunk 2 response in 60.60s
------------------------------------------------------------
🚀 Sending chunk 3/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 3: found 1 problems
⏱️ Chunk 3 response in 88.38s
------------------------------------------------------------
🚀 Sending chunk 4/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 4: found 1 problems
⏱️ Chunk 4 response in 34.29s
------------------------------------------------------------
🚀 Sending chunk 5/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 5: found 1 problems
⏱️ Chunk 5 response in 87.52s
------------------------------------------------------------
🚀 Sending chunk 6/6 to Local Ollama (qwen2.5-coder:1.5b)...
✅ Chunk 6: found 1 problems
⏱️ Chunk 6 response in 47.09s
------------------------------------------------------------

🧠 Total findings: 6

📝 Final Local AI Report:

<!-- AI_SLOP_GATE_REPORT -->
## ⚠️ AI Slop Gate — Advisory

- **Local Ollama analysis using qwen2.5-coder:1.5b**

---

### `quality`
-  [medium, 0.70] (chunk_1:1)
- The AI-generated annotation 'ai-slop-gate.check: passed-by-internal-llm' contradicts itself and is not a valid annotation for Kubernetes resources. [high, 0.95] (k8s_silent_slop.yaml:14)
-  [medium, 0.70] (chunk_4:1)
- The `overengineered_sum` function contains an AI-SLOP annotation that suggests over-engineering the logic, which can lead to unexpected behavior and security risks. [high, 0.95] (slop.py:12)

### `security`
- Hardcoded API key in compliance.py at line 21 — should be stored securely [high, 0.95] (compliance.py:21)
- Hardcoded secret 'password123' at line 47 in subtle_violation_with_backdoor.py [high, 0.95] (subtle_violation_with_backdoor.py:47)

