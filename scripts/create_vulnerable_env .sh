# chmod +x scripts/create_vulnerable_env.sh
# ./scripts/create_vulnerable_env.sh

#!/bin/bash
# Create test environment with real vulnerable packages

echo "🔧 Creating test environment with vulnerable packages..."

cd /home/serhiy/slop_test

# 1. Create Python virtual environment with old packages
echo "📦 Installing old Python packages with known vulnerabilities..."

python3 -m venv .test_venv
source .test_venv/bin/activate

# Install old versions with known CVEs
pip install --quiet \
  requests==2.25.0 \
  django==3.1.0 \
  pillow==8.0.0 \
  urllib3==1.26.0 \
  jinja2==2.11.0

echo "✅ Installed vulnerable Python packages"

# 2. Create Node.js project with vulnerable packages
echo "📦 Installing old Node.js packages with known vulnerabilities..."

npm init -y > /dev/null 2>&1

npm install --silent \
  express@4.17.0 \
  lodash@4.17.19 \
  axios@0.21.0 \
  moment@2.29.0

echo "✅ Installed vulnerable Node.js packages"

echo ""
echo "🎯 Test environment ready!"
echo ""
echo "Now run Trivy scan:"
echo "  trivy fs --format json --severity CRITICAL,HIGH /home/serhiy/slop_test"
echo ""
echo "Or test with TrivyProvider:"
echo "  python test_trivy.py"