#!/bin/bash
set -euo pipefail

TODAY=$(date +"%Y-%m-%d")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
RACE_OUTPUT="$REPO_ROOT/rpscrape/racecards/${TODAY}.json"
SCRIPT_PATH="$REPO_ROOT/rpscrape/scripts"
VENV="$REPO_ROOT/.venv/bin/activate"

source "$VENV"
cd "$SCRIPT_PATH"

echo "📅 Generating racecards for $TODAY"
python racecards.py today

echo "☁️ Uploading to S3"
if [ "$TM_DEV_MODE" = "1" ]; then
    echo "[DEV] Skipping S3 upload"
else
    aws s3 cp "$RACE_OUTPUT" "s3://tipping-monster/racecards/${TODAY}.json"
fi

echo "✅ Racecard upload complete for $TODAY"

