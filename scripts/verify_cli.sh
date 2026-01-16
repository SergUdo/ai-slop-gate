#!/usr/bin/env bash
# chmod +x scripts/verify_cli.sh
# ./scripts/verify_cli.sh
#!/usr/bin/env bash
set -e

echo "🔍 Stage 0 smoke test"

echo "▶ init"
python -m ai_slop_gate.cli.main init --force
test -f .ai-slop-gate.yml && echo "✔ config created"

echo "▶ run (static)"
python -m ai_slop_gate.cli.main run \
  --policy policy.yml \
  --provider static \
  --input-text "test"

echo "✔ Stage 0 OK"


