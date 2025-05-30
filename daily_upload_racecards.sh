#!/bin/bash
set -euo pipefail

TODAY=$(date +"%Y-%m-%d")
RACE_OUTPUT="/home/ec2-user/tipping-monster/rpscrape/racecards/${TODAY}.json"
SCRIPT_DIR="/home/ec2-user/tipping-monster/rpscrape/scripts"
VENV="/home/ec2-user/tipping-monster/.venv/bin/activate"

source "$VENV"
cd "$SCRIPT_DIR"

echo "📅 Generating racecards for $TODAY"
python racecards.py today

echo "☁️ Uploading to S3"
aws s3 cp "$RACE_OUTPUT" "s3://tipping-monster/racecards/${TODAY}.json"

echo "✅ Racecard upload complete for $TODAY"

