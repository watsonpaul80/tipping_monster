#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
source "$REPO_ROOT/.venv/bin/activate"

DATE=$(date +%F)
INPUT="$REPO_ROOT/rpscrape/racecards/${DATE}.json"
OUTPUT="$REPO_ROOT/rpscrape/batch_inputs/${DATE}.jsonl"

# Flatten the racecard
python "$REPO_ROOT/core/flatten_racecards_v3.py" "$INPUT" "$OUTPUT"

# Upload to S3
if [ "$TM_DEV_MODE" = "1" ]; then
    echo "[DEV] Skipping S3 upload"
else
    aws s3 cp "$OUTPUT" "s3://tipping-monster/batch_inputs/${DATE}.jsonl"
fi

