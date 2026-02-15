# chmod +x scripts/setup_trivy.sh
# ./scripts/setup_trivy.sh


#!/bin/bash
# Setup script for Trivy vulnerability testing
# This installs VULNERABLE packages intentionally for testing purposes
# DO NOT use in production environments!

set -e

echo "=============================================="
echo "🔧 Trivy Vulnerability Test Setup"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will install VULNERABLE packages!"
echo "   Only use for testing Trivy detection."
echo ""

TEST_DIR="/home/serhiy/slop_test_trivy"

# Ask for confirmation
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create test directory
echo "📁 Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# ============================================================================
# Python Vulnerable Environment
# ============================================================================
echo ""
echo "🐍 Setting up Python vulnerable environment..."

# Copy requirements.txt
cat > requirements.txt << 'EOF'
# Requirements.txt with KNOWN VULNERABILITIES for Trivy Testing
# These are intentionally OLD versions with documented CVEs

# HIGH/CRITICAL Vulnerabilities
django==3.1.0              # CVE-2021-33571, CVE-2021-33203
djangorestframework==3.11.0
requests==2.25.0           # CVE-2023-32681
pillow==8.0.0              # CVE-2021-25287, CVE-2021-25288
jinja2==2.11.0             # CVE-2020-28493
pyyaml==5.3                # CVE-2020-14343
urllib3==1.26.0            # CVE-2021-33503
cryptography==3.2          # CVE-2023-23931
sqlalchemy==1.3.0          # CVE-2019-7164

# MEDIUM Vulnerabilities
werkzeug==0.16.0
tornado==6.0.0
certifi==2020.12.5
EOF

echo "✅ Created requirements.txt with vulnerable packages"

# Create Python virtual environment
if command -v python3 &> /dev/null; then
    echo "   Creating Python venv..."
    python3 -m venv .venv
    
    echo "   Installing vulnerable packages..."
    source .venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt || echo "   ⚠️  Some packages may have failed (expected)"
    deactivate
    
    echo "✅ Python environment ready"
else
    echo "⚠️  Python3 not found, skipping Python setup"
fi

# ============================================================================
# Node.js Vulnerable Environment
# ============================================================================
echo ""
echo "📦 Setting up Node.js vulnerable environment..."

cat > package.json << 'EOF'
{
  "name": "trivy-test-vulnerable-app",
  "version": "1.0.0",
  "description": "Test app with KNOWN VULNERABILITIES",
  "dependencies": {
    "express": "4.17.0",
    "lodash": "4.17.19",
    "axios": "0.21.0",
    "node-fetch": "2.6.0",
    "minimist": "1.2.0",
    "ajv": "6.12.2",
    "moment": "2.29.0",
    "serialize-javascript": "3.0.0",
    "json-schema": "0.2.3",
    "underscore": "1.12.0",
    "async": "2.6.3",
    "validator": "13.0.0",
    "qs": "6.9.4"
  },
  "devDependencies": {
    "webpack": "4.44.0"
  }
}
EOF

echo "✅ Created package.json with vulnerable packages"

if command -v npm &> /dev/null; then
    echo "   Installing Node.js packages..."
    npm install --silent --no-audit 2>&1 | grep -v "npm WARN" || true
    echo "✅ Node.js environment ready"
else
    echo "⚠️  npm not found, skipping Node.js setup"
fi

# ============================================================================
# Create Dockerfile
# ============================================================================
echo ""
echo "🐳 Creating vulnerable Dockerfile..."

cat > Dockerfile << 'EOF'
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3.6 \
    python3-pip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt || true

ENV ADMIN_PASSWORD=admin123
ENV API_KEY=hardcoded-key-12345

EXPOSE 8080
CMD ["python3", "-m", "http.server", "8080"]
EOF

echo "✅ Created Dockerfile"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "Test directory: $TEST_DIR"
echo ""
echo "📊 What was created:"
echo "   - requirements.txt (Python vulnerable packages)"
echo "   - .venv/ (Python environment with vulnerabilities)"
echo "   - package.json (Node.js vulnerable packages)"
echo "   - node_modules/ (Node.js packages with CVEs)"
echo "   - Dockerfile (Vulnerable container image)"
echo ""
echo "🔍 Run Trivy scans:"
echo ""
echo "  # Scan filesystem"
echo "  trivy fs --severity HIGH,CRITICAL $TEST_DIR"
echo ""
echo "  # Scan with JSON output"
echo "  trivy fs --format json --severity HIGH,CRITICAL $TEST_DIR"
echo ""
echo "  # Scan specific files"
echo "  trivy config Dockerfile"
echo "  trivy fs --security-checks vuln requirements.txt"
echo ""
echo "  # Run through ai-slop-gate"
echo "  cd ~/ai-slop-gate"
echo "  python -m ai_slop_gate.cli run --provider static --policy policy.yml --path $TEST_DIR"
echo ""
echo "📈 Expected results:"
echo "   - Python: 15-25 HIGH/CRITICAL vulnerabilities"
echo "   - Node.js: 10-20 HIGH/CRITICAL vulnerabilities"
echo "   - Dockerfile: 5-15 vulnerabilities"
echo "   - Total: ~30-60 vulnerabilities"
echo ""
echo "⚠️  Remember: These are INTENTIONALLY vulnerable packages!"
echo "   Do NOT use in production or expose to networks."
echo ""