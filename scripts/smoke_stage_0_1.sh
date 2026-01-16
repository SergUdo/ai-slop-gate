#!/usr/bin/env bash
# chmod +x scripts/smoke_stage_0_1.sh
# ./scripts/smoke_stage_0_1.sh

set -e

echo "🔍 Stage 0.1 Smoke Test"

echo "▶ ai-slop-gate init"
python -m ai_slop_gate.cli.main init --force

if [ -f ".ai-slop-gate.yml" ]; then
    echo "✔ Config file created"
else
    echo "❌ Config file missing"
    exit 1
fi

POLICY_FILE=".ai-slop-gate-test-policy.yml"
cat > $POLICY_FILE <<EOL
rules:
  - id: todo
    when:
      category: CODE_QUALITY
      signal: TODO
    then:
      action: advisory
      message: Remove TODO
EOL

echo "✔ Policy file created: $POLICY_FILE"

echo "▶ ai-slop-gate run (static)"
OUTPUT=$(python -m ai_slop_gate.cli.main run \
    --policy $POLICY_FILE \
    --provider static \
    --input-text "test" \
    2>&1
)

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "Decision:"; then
    echo "✔ Stage 0.1 run successful"
else
    echo "❌ Stage 0.1 run failed"
    exit 1
fi

echo "✅ Stage 0.1 Smoke Test Passed"
