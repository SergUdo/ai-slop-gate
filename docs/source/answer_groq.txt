📁 Scanning repo: /home/serhiy/slop_test
🧩 Created 1 chunks for analysis

🚀 Sending chunk 1/1 to Groq...
⏱️ Chunk 1 response in 2.83s
------------------------------------------------------------
🧠 Total findings: 15

📝 Final GitHub-style report:

<!-- AI_SLOP_GATE_REPORT -->
## ⚠️ AI Slop Gate — Advisory

- **Local Groq multi-file chunked test**

---

### `security`
- Hardcoded secret in Dockerfile [high, 0.90] (chunk_1:5)
- Hardcoded API key in compliance_hell.py [medium, 0.80] (chunk_1:10)
- SQL injection vulnerability in slop_hell.py [medium, 0.90] (chunk_1:15)
- Hardcoded token in slop_hell.ts [high, 0.90] (chunk_1:20)
- XSS vulnerability in slop_hell.js [medium, 0.80] (chunk_1:25)
- Insecure DOM injection in slop_hell.js [medium, 0.80] (chunk_1:30)
- Hardcoded password in Dockerfile [medium, 0.90] (chunk_1:10)
- Insecure network policy in k8s_silent_slop.yaml [medium, 0.80] (chunk_1:25)

### `quality`
- Unused variable in slop.py [low, 0.70] (chunk_1:20)
- Overengineered code in slop.py [low, 0.70] (chunk_1:30)
- TODO comment in slop.py [low, 0.70] (chunk_1:40)
- Dead code in slop.js [low, 0.70] (chunk_1:35)

### `architecture`
- Selector and label mismatch in k8s_silent_slop.yaml [medium, 0.80] (chunk_1:10)
- Port mapping mismatch in k8s_silent_slop.yaml [high, 0.90] (chunk_1:15)
- HPA target mismatch in k8s_silent_slop.yaml [medium, 0.80] (chunk_1:20)

