#!/bin/bash
set -euo pipefail

TODAY=$(date +"%Y/%m/%d")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TM_ROOT:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
OUTPUT_CSV="$REPO_ROOT/rpscrape/data/dates/all/$(date +"%Y_%m_%d").csv"
SCRIPT_PATH="$REPO_ROOT/rpscrape/scripts"
VENV="$REPO_ROOT/.venv/bin/activate"

source "$VENV"
cd "$SCRIPT_PATH"

echo "📅 Scraping results for $TODAY"
python rpscrape.py -d "$TODAY"

echo "☁️ Uploading results CSV to S3"
aws s3 cp "$OUTPUT_CSV" "s3://tipping-monster/results/$(date +"%Y_%m_%d").csv"

echo "✅ Results upload complete for $TODAY"

