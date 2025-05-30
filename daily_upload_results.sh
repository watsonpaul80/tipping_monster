#!/bin/bash
set -euo pipefail

TODAY=$(date +"%Y/%m/%d")
OUTPUT_CSV="/home/ec2-user/tipping-monster/rpscrape/data/dates/all/$(date +"%Y_%m_%d").csv"
SCRIPT_DIR="/home/ec2-user/tipping-monster/rpscrape/scripts"
VENV="/home/ec2-user/tipping-monster/.venv/bin/activate"

source "$VENV"
cd "$SCRIPT_DIR"

echo "📅 Scraping results for $TODAY"
python rpscrape.py -d "$TODAY"

echo "☁️ Uploading results CSV to S3"
aws s3 cp "$OUTPUT_CSV" "s3://tipping-monster/results/$(date +"%Y_%m_%d").csv"

echo "✅ Results upload complete for $TODAY"

