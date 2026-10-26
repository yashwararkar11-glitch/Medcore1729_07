#!/usr/bin/env bash
# Double-click to launch (macOS). On Linux, run: ./run_app.command
cd "$(dirname "$0")"

# ---- Change this if your script has a different name ----
APP="app.py"

if [ ! -f "$APP" ]; then
  echo "Could not find $APP in $(pwd). Edit this file and set APP."
  read -p "Press Enter to close"
  exit 1
fi

[ -f ".venv/bin/activate" ] && source .venv/bin/activate

(sleep 4 && (open http://localhost:8501 2>/dev/null || xdg-open http://localhost:8501)) &
python3 -m streamlit run "$APP" --server.port 8501 --server.headless true --browser.gatherUsageStats false
