# test_trivy.py
from ai_slop_gate.providers.static.trivy import TrivyProvider

provider = TrivyProvider()
result = provider.collect(base_path="/home/serhiy/slop_test")

print(f"Found {len(result.observations)} vulnerabilities")
for obs in result.observations:
    print(f"  - {obs.signal}: {obs.message}")