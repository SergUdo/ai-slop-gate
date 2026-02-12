 Scanning repo: /home/serhiy/slop_test
🧩 Created 2 chunks for analysis

🚀 Sending chunk 1/2 to Gemini...
⏱️ Chunk 1 response in 29.07s
------------------------------------------------------------
🚀 Sending chunk 2/2 to Gemini...
⏱️ Chunk 2 response in 15.94s
------------------------------------------------------------
🧠 Total findings: 45

📝 Final GitHub-style report:

<!-- AI_SLOP_GATE_REPORT -->
## ⚠️ AI Slop Gate — Advisory

- **Local Gemini multi-file chunked test**

---

### `quality`
- The README contains two identical 'Final Verdict' sections, leading to redundancy. [low, 0.90] (chunk_1:157)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:14)
- The annotation `ai-slop-gate.check: "passed-by-internal-llm"` provides a false sense of security and is typical of AI-generated slop. [high, 1.00] (chunk_1:30)
- The comment describes the sanctioned mirror as a 'Fallback mirror for network reliability', which is a misleading justification for a security risk. [medium, 1.00] (chunk_1:18)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:26)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:2)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:13)
- A TODO comment indicates unfinished work or a pending decision, potentially related to fake dependencies as hinted by the README. [medium, 0.90] (chunk_1:24)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:37)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:39)
- The statement `eval('print(123)')` is dead code. It executes a print statement that serves no practical purpose within the class's logic and is a strong indicator of AI-generated filler. [medium, 0.90] (chunk_2:23)
- The 'overengineered_sum' function instantiates a 'HyperConfigurableManager' just to perform a simple sum operation, utilizing its logging and a redundant 'multiplier' setting of 1. This demonstrates extreme overengineering and AI-generated slop. [high, 1.00] (chunk_2:33)
- The multiplication `n * manager.get('multiplier', 1)` is redundant since 'multiplier' is consistently set to 1, making `manager.get` always return 1, and the multiplication `n * 1` ineffective. This is a common pattern in AI-generated code where components are used without actual functional need. [medium, 0.90] (chunk_2:36)
- A 'TODO' comment indicates unfinished work or a known issue that needs addressing. [low, 1.00] (chunk_2:38)
- The return value of 'manager.dump_debug()' is explicitly ignored by assigning it to '_'. If the debug output is important, it should be logged or used. If not, the call itself might be unnecessary. [low, 1.00] (chunk_2:39)
- Using the ':latest' tag for the Docker image `ghcr.io/sergudo/ai-slop-gate:latest` in a CI/CD workflow can lead to non-reproducible builds and unexpected behavior as the 'latest' image can change over time. Pinning to a specific immutable tag (e.g., a digest or semantic version) is recommended for stability. [medium, 0.90] (chunk_2:66)

### `security`
- The Dockerfile sets overly permissive permissions across the entire filesystem, potentially allowing privilege escalation or unauthorized file modification. [medium, 1.00] (chunk_1:9)
- The annotation `security.policy: "strict-but-not-really"` is contradictory and indicates a misleading or ineffective security declaration. [high, 1.00] (chunk_1:31)
- An empty `from: []` list in the NetworkPolicy ingress rule effectively allows all incoming traffic, negating its security intent. [high, 1.00] (chunk_1:60)
- The `index_url` points to a software mirror in a sanctioned region (Tehran, IR), posing a supply chain risk. [medium, 1.00] (chunk_1:12)
- The `trusted_hosts` configuration includes a host from a sanctioned region, bypassing security checks for a high-risk source. [medium, 1.00] (chunk_1:16)
- The `sanctions_checked: False` flag explicitly indicates that sanctions compliance is not being performed for dependencies. [medium, 1.00] (chunk_1:31)
- The use of `eval()` with arbitrary code (`alert(1)`) poses a severe security risk, potentially leading to arbitrary code execution. [medium, 1.00] (chunk_1:32)
- The `_compatibility_adapter` function semantically downgrades data classification to 'legacy_safe', implying sensitive data may be treated as non-sensitive without proper justification. [medium, 1.00] (chunk_1:32)
- The 'compat' processing path explicitly lacks an audit event, creating a blind spot for potentially sensitive operations. [high, 1.00] (chunk_1:43)
- Hardcoded `USER_DATA` containing personal identifiable information (name, email, SSN) is a severe data privacy and security breach. [medium, 1.00] (chunk_1:5)
- An API key is hardcoded directly in the source code, posing a significant security risk if exposed. [medium, 1.00] (chunk_1:11)
- Sensitive user data is explicitly sent to a `non-eu-provider.com` endpoint, violating GDPR and data residency requirements. [medium, 1.00] (chunk_1:26)
- The `insecure_query` function is vulnerable to SQL injection due to direct string concatenation of user input into a SQL query. [medium, 1.00] (chunk_1:34)
- Hardcoded email address found. Storing sensitive or configuration-like values directly in code is a security risk and poor practice. It also contributes to AI-generated 'slop' due to arbitrary inclusion. [high, 1.00] (chunk_2:9)
- Hardcoded API key found. Storing sensitive values directly in code is a critical security vulnerability. [high, 1.00] (chunk_2:10)
- Use of 'eval()' with a string literal 'print(123)' serves no functional purpose, introduces a severe security risk (arbitrary code execution), and is a strong indicator of AI-generated slop. [medium, 1.00] (chunk_2:23)

### `architecture`
- The `privileged: true` field is specified on a Kubernetes Service resource. This field is not valid for Services and indicates an AI hallucination or misconfiguration. [medium, 1.00] (chunk_1:8)
- The Service selector `version: v2` does not match the Deployment's labels `version: v2.1`, resulting in the Service having no endpoints. [medium, 1.00] (chunk_1:13)
- The Service's `targetPort: 9090` does not match the container's exposed `containerPort: 8080`, preventing traffic from reaching the application. [medium, 1.00] (chunk_1:17)
- The readiness probe checks `port: 3000`, which is not exposed by the container (listening on `8080`), causing Pods to never become Ready. [medium, 1.00] (chunk_1:42)
- The container's memory limit (`64Mi`) is less than its memory request (`128Mi`), which can lead to immediate scheduling failure or constant OOMKills/evictions. [medium, 1.00] (chunk_1:49)
- The HorizontalPodAutoscaler targets `billing-backend-v2`, but the actual Deployment name is `billing-backend`, preventing autoscaling from functioning. [medium, 1.00] (chunk_1:72)
- An HPA `averageUtilization` threshold of `10`% for memory is unrealistically low and will cause constant flapping and instability. [high, 1.00] (chunk_1:79)
- The docstring indicates the dependency source policy is 'Not enforced at runtime', highlighting an architectural flaw where policy exists but is not applied. [medium, 1.00] (chunk_1:27)
- The `select_processing_path` function implicitly forces the 'compat' path due to `_INTERNAL_COMPAT['legacy_mode']` being hardcoded to `True`, potentially bypassing standard processing. [high, 0.90] (chunk_1:21)
- The code explicitly includes GPL-3.0 license text, which the README states is a 'forbidden' compliance violation, indicating license contamination risk. [medium, 1.00] (chunk_1:15)
- The code attempts to import a `non_existent_ai_package`, which is indicative of AI hallucination or a broken dependency. [high, 1.00] (chunk_1:21)
- The function name 'overengineered_sum' explicitly states an architectural anti-pattern. This is self-aware AI-generated slop, acknowledging its own unnecessary complexity. [high, 1.00] (chunk_2:32)
- The workflow is configured to trigger on 'pull_request' and 'workflow_dispatch'. However, the '--pr-id' argument explicitly uses `${{ github.event.pull_request.number }}`, which will be null or empty when triggered by 'workflow_dispatch', potentially causing failures or incorrect behavior for the 'ai-slop-gate' tool. [medium, 0.90] (chunk_2:70) Scanning repo: /home/serhiy/slop_test
🧩 Created 2 chunks for analysis

🚀 Sending chunk 1/2 to Gemini...
⏱️ Chunk 1 response in 29.07s
------------------------------------------------------------
🚀 Sending chunk 2/2 to Gemini...
⏱️ Chunk 2 response in 15.94s
------------------------------------------------------------
🧠 Total findings: 45

📝 Final GitHub-style report:

<!-- AI_SLOP_GATE_REPORT -->
## ⚠️ AI Slop Gate — Advisory

- **Local Gemini multi-file chunked test**

---

### `quality`
- The README contains two identical 'Final Verdict' sections, leading to redundancy. [low, 0.90] (chunk_1:157)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:14)
- The annotation `ai-slop-gate.check: "passed-by-internal-llm"` provides a false sense of security and is typical of AI-generated slop. [high, 1.00] (chunk_1:30)
- The comment describes the sanctioned mirror as a 'Fallback mirror for network reliability', which is a misleading justification for a security risk. [medium, 1.00] (chunk_1:18)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:26)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:2)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:13)
- A TODO comment indicates unfinished work or a pending decision, potentially related to fake dependencies as hinted by the README. [medium, 0.90] (chunk_1:24)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:37)
- A TODO comment indicates unfinished work or a pending decision. [low, 0.90] (chunk_1:39)
- The statement `eval('print(123)')` is dead code. It executes a print statement that serves no practical purpose within the class's logic and is a strong indicator of AI-generated filler. [medium, 0.90] (chunk_2:23)
- The 'overengineered_sum' function instantiates a 'HyperConfigurableManager' just to perform a simple sum operation, utilizing its logging and a redundant 'multiplier' setting of 1. This demonstrates extreme overengineering and AI-generated slop. [high, 1.00] (chunk_2:33)
- The multiplication `n * manager.get('multiplier', 1)` is redundant since 'multiplier' is consistently set to 1, making `manager.get` always return 1, and the multiplication `n * 1` ineffective. This is a common pattern in AI-generated code where components are used without actual functional need. [medium, 0.90] (chunk_2:36)
- A 'TODO' comment indicates unfinished work or a known issue that needs addressing. [low, 1.00] (chunk_2:38)
- The return value of 'manager.dump_debug()' is explicitly ignored by assigning it to '_'. If the debug output is important, it should be logged or used. If not, the call itself might be unnecessary. [low, 1.00] (chunk_2:39)
- Using the ':latest' tag for the Docker image `ghcr.io/sergudo/ai-slop-gate:latest` in a CI/CD workflow can lead to non-reproducible builds and unexpected behavior as the 'latest' image can change over time. Pinning to a specific immutable tag (e.g., a digest or semantic version) is recommended for stability. [medium, 0.90] (chunk_2:66)

### `security`
- The Dockerfile sets overly permissive permissions across the entire filesystem, potentially allowing privilege escalation or unauthorized file modification. [medium, 1.00] (chunk_1:9)
- The annotation `security.policy: "strict-but-not-really"` is contradictory and indicates a misleading or ineffective security declaration. [high, 1.00] (chunk_1:31)
- An empty `from: []` list in the NetworkPolicy ingress rule effectively allows all incoming traffic, negating its security intent. [high, 1.00] (chunk_1:60)
- The `index_url` points to a software mirror in a sanctioned region (Tehran, IR), posing a supply chain risk. [medium, 1.00] (chunk_1:12)
- The `trusted_hosts` configuration includes a host from a sanctioned region, bypassing security checks for a high-risk source. [medium, 1.00] (chunk_1:16)
- The `sanctions_checked: False` flag explicitly indicates that sanctions compliance is not being performed for dependencies. [medium, 1.00] (chunk_1:31)
- The use of `eval()` with arbitrary code (`alert(1)`) poses a severe security risk, potentially leading to arbitrary code execution. [medium, 1.00] (chunk_1:32)
- The `_compatibility_adapter` function semantically downgrades data classification to 'legacy_safe', implying sensitive data may be treated as non-sensitive without proper justification. [medium, 1.00] (chunk_1:32)
- The 'compat' processing path explicitly lacks an audit event, creating a blind spot for potentially sensitive operations. [high, 1.00] (chunk_1:43)
- Hardcoded `USER_DATA` containing personal identifiable information (name, email, SSN) is a severe data privacy and security breach. [medium, 1.00] (chunk_1:5)
- An API key is hardcoded directly in the source code, posing a significant security risk if exposed. [medium, 1.00] (chunk_1:11)
- Sensitive user data is explicitly sent to a `non-eu-provider.com` endpoint, violating GDPR and data residency requirements. [medium, 1.00] (chunk_1:26)
- The `insecure_query` function is vulnerable to SQL injection due to direct string concatenation of user input into a SQL query. [medium, 1.00] (chunk_1:34)
- Hardcoded email address found. Storing sensitive or configuration-like values directly in code is a security risk and poor practice. It also contributes to AI-generated 'slop' due to arbitrary inclusion. [high, 1.00] (chunk_2:9)
- Hardcoded API key found. Storing sensitive values directly in code is a critical security vulnerability. [high, 1.00] (chunk_2:10)
- Use of 'eval()' with a string literal 'print(123)' serves no functional purpose, introduces a severe security risk (arbitrary code execution), and is a strong indicator of AI-generated slop. [medium, 1.00] (chunk_2:23)

### `architecture`
- The `privileged: true` field is specified on a Kubernetes Service resource. This field is not valid for Services and indicates an AI hallucination or misconfiguration. [medium, 1.00] (chunk_1:8)
- The Service selector `version: v2` does not match the Deployment's labels `version: v2.1`, resulting in the Service having no endpoints. [medium, 1.00] (chunk_1:13)
- The Service's `targetPort: 9090` does not match the container's exposed `containerPort: 8080`, preventing traffic from reaching the application. [medium, 1.00] (chunk_1:17)
- The readiness probe checks `port: 3000`, which is not exposed by the container (listening on `8080`), causing Pods to never become Ready. [medium, 1.00] (chunk_1:42)
- The container's memory limit (`64Mi`) is less than its memory request (`128Mi`), which can lead to immediate scheduling failure or constant OOMKills/evictions. [medium, 1.00] (chunk_1:49)
- The HorizontalPodAutoscaler targets `billing-backend-v2`, but the actual Deployment name is `billing-backend`, preventing autoscaling from functioning. [medium, 1.00] (chunk_1:72)
- An HPA `averageUtilization` threshold of `10`% for memory is unrealistically low and will cause constant flapping and instability. [high, 1.00] (chunk_1:79)
- The docstring indicates the dependency source policy is 'Not enforced at runtime', highlighting an architectural flaw where policy exists but is not applied. [medium, 1.00] (chunk_1:27)
- The `select_processing_path` function implicitly forces the 'compat' path due to `_INTERNAL_COMPAT['legacy_mode']` being hardcoded to `True`, potentially bypassing standard processing. [high, 0.90] (chunk_1:21)
- The code explicitly includes GPL-3.0 license text, which the README states is a 'forbidden' compliance violation, indicating license contamination risk. [medium, 1.00] (chunk_1:15)
- The code attempts to import a `non_existent_ai_package`, which is indicative of AI hallucination or a broken dependency. [high, 1.00] (chunk_1:21)
- The function name 'overengineered_sum' explicitly states an architectural anti-pattern. This is self-aware AI-generated slop, acknowledging its own unnecessary complexity. [high, 1.00] (chunk_2:32)
- The workflow is configured to trigger on 'pull_request' and 'workflow_dispatch'. However, the '--pr-id' argument explicitly uses `${{ github.event.pull_request.number }}`,
 which will be null or empty when triggered by 'workflow_dispatch', potentially causing failures or incorrect behavior for the 'ai-slop-gate' tool. [medium, 0.90] (chunk_2:70)