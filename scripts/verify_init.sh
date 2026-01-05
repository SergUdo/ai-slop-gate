# chmod +x scripts/verify_init.sh
# ./scripts/verify_init.sh

set -e

echo "▶️ Stage 6.1 smoke test"

echo "▶️ Cleanup"
rm -f .ai-slop-gate.yml

echo "▶️ 1. Init creates config"
python -m ai_slop_gate.cli init
test -f .ai-slop-gate.yml
echo "✔ Config created"

echo "▶️ 2. Init without --force fails"
if python -m ai_slop_gate.cli init 2>/dev/null; then
  echo "❌ Expected failure without --force"
  exit 1
else
  echo "✔ Properly refused overwrite"
fi

echo "▶️ 3. Init with --force overwrites"
python -m ai_slop_gate.cli init --force
echo "✔ Overwrite OK"

echo "▶️ 4. Config content sanity"
grep "mode: advisory" .ai-slop-gate.yml
grep "providers:" .ai-slop-gate.yml
echo "✔ Config content looks valid"

echo "▶️ 5. Run command still works"
python -m ai_slop_gate.cli run --help >/dev/null
echo "✔ Run command intact"

echo "🎉 Stage 6.1 smoke test PASSED"
