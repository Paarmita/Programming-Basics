#!/bin/bash
# PM Data Analyst — launcher script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Installing dependencies (using python3)..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet

echo ""
echo "🚀 Starting PM Data Analyst..."
echo "   Open your browser at http://localhost:8501"
echo ""

python3 -m streamlit run "$SCRIPT_DIR/app.py" \
  --server.port 8501 \
  --server.headless false \
  --browser.gatherUsageStats false
