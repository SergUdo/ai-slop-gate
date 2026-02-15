# chmod +x scripts/verify_complaince.sh
# ./scripts/verify_complaince.sh


#!/bin/bash
# Quick Compliance Test Script

echo "=== Creating test files with GPL violations ==="

cd /home/serhiy/slop_test

# 1. Create requirements.txt with GPL
cat > requirements.txt << 'EOF'
# Python Dependencies
requests==2.31.0
numpy==1.24.0

# GPL Violations - should be detected
gpl-python-lib==1.2.3              # GPL-3.0
agpl-django-app==2.0.1             # AGPL-3.0
readline-gpl==6.3.0                # GPL-2.0
EOF

echo "✅ Created requirements.txt with GPL violations"

# 2. Create package.json with GPL
cat > package.json << 'EOF'
{
  "name": "test-compliance-app",
  "version": "1.0.0",
  "license": "GPL-3.0",
  "licenses": [
    {
      "type": "GPL-3.0",
      "url": "https://www.gnu.org/licenses/gpl-3.0.html"
    }
  ],
  "dependencies": {
    "express": "^4.18.0",
    "gpl-licensed-package": "^1.0.0"
  },
  "devDependencies": {
    "agpl-testing-tool": "^1.5.0"
  }
}
EOF

echo "✅ Created package.json with GPL violations"

# 3. Create a Python file with GPL in comments
cat > gpl_code.py << 'EOF'
"""
This module is licensed under GPL-3.0
Copyright (C) 2024
"""

# This code uses GPL-licensed libraries
LICENSE_TEXT = """
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

# AGPL-3.0 dependency
import agpl_package  # This is AGPL-3.0 licensed

def main():
    # TODO: This uses copyleft GPL code
    pass
EOF

echo "✅ Created gpl_code.py with GPL comments"

echo ""
echo "=== Test files created! ==="
echo ""
ls -la | grep -E "(requirements|package|gpl_code)"

echo ""
echo "=== Now run compliance check: ==="
echo "cd ~/ai-slop-gate"
echo "python -m ai_slop_gate.cli run --compliance --policy policy.yml --path /home/serhiy/slop_test"