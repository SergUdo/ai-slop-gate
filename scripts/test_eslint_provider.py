# node -v
# npx eslint --version
# python -m scripts.test_eslint_provider

from ai_slop_gate.providers.eslint import ESLintProvider

provider = ESLintProvider(target_path=".")

result = provider.collect()

print("Provider:", result.provider)
print("Observations:", len(result.observations))

for obs in result.observations[:5]:
    print(obs)
