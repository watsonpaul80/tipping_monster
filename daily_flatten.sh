#!/bin/bash
source /home/ec2-user/tipping-monster/.venv/bin/activate

DATE=$(date +%F)
INPUT="/home/ec2-user/tipping-monster/rpscrape/racecards/${DATE}.json"
OUTPUT="/home/ec2-user/tipping-monster/rpscrape/batch_inputs/${DATE}.jsonl"

# Flatten the racecard
python /home/ec2-user/tipping-monster/flatten_racecards_v3.py "$INPUT" "$OUTPUT"

# Upload to S3
aws s3 cp "$OUTPUT" "s3://tipping-monster/batch_inputs/${DATE}.jsonl"

