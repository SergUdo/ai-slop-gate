#!/usr/bin/env bash
# chmod +x scripts/verify_cli.sh
# ./scripts/verify_cli.sh
#!/bin/bash
echo "▶️ Verify CLI basic commands"

# init
python -m ai_slop_gate.cli.main init --force --policy policy.yml --provider static

# run with static
python -m ai_slop_gate.cli.main run \
  --policy policy.yml \
  --provider static \
  --input-text "test input for static provider"


