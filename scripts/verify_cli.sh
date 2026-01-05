#!/usr/bin/env bash
# chmod +x scripts/verify_cli.sh
# ./scripts/verify_cli.sh
#!/bin/bash
#!/bin/bash
set -e

echo "▶️ Verify CLI basic commands"

# --- test init
echo ">>> Testing 'init' command"
python -m ai_slop_gate.cli.main init --force --policy policy.yml --provider static

# --- test run with static provider
echo ">>> Testing 'run' command with static provider"
python -m ai_slop_gate.cli.main run --policy policy.yml --provider static

# --- test run with eslint provider
echo ">>> Testing 'run' command with eslint provider"
python -m ai_slop_gate.cli.main run --policy policy.yml --provider eslint

# --- test run with terraform-plan provider
echo ">>> Testing 'run' command with terraform-plan provider"
python -m ai_slop_gate.cli.main run --policy policy.yml --provider terraform-plan


