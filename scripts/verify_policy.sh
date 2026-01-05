#!/usr/bin/env bash
# chmod +x scripts/verify_policy.sh
# ./scripts/verify_policy.sh
# Purpose: Verify that the policy_engine evaluate_policy function works
# with all main providers without raising errors.

set -euo pipefail

AI_SLOP_CLI="python -m ai_slop_gate.cli.main"
POLICY_FILE="policy.yml"

PROVIDERS=("static" "eslint" "terraform-plan")

echo "▶️ Verify policy_engine with all providers"
echo ""

for provider in "${PROVIDERS[@]}"; do
    echo ">>> Testing provider: $provider"
    # Run ai-slop-gate CLI with the given provider and policy file
    if $AI_SLOP_CLI run --provider "$provider" --policy "$POLICY_FILE"; then
        echo "✔ Provider $provider completed successfully"
    else
        echo "❌ Provider $provider failed"
    fi
    echo ""
done

echo "✅ All providers verified successfully (if no errors above)"
