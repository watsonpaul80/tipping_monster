#!/bin/bash
# Upload ROI and dispatch logs to S3 while preserving folder structure.
# Set ROOT_DIR and S3_BUCKET to override defaults.

set -euo pipefail

ROOT_DIR="${ROOT_DIR:-/home/ec2-user/tipping-monster}"
S3_BUCKET="${S3_BUCKET:-tipping-monster-backups}"

ROI_DIR="$ROOT_DIR/logs/roi_logs"
DISPATCH_DIR="$ROOT_DIR/logs/dispatch_logs"

echo "Using ROOT_DIR=$ROOT_DIR"
echo "Uploading to bucket: $S3_BUCKET"

for dir in "$ROI_DIR" "$DISPATCH_DIR"; do
    if [ -d "$dir" ]; then
        prefix="$(basename "$dir")"
        echo "Uploading $dir to s3://$S3_BUCKET/$prefix/"
        aws s3 cp "$dir" "s3://$S3_BUCKET/$prefix/" \
            --recursive --exclude "*" --include "*.log" --include "*.csv"
    else
        echo "Skipping missing directory $dir"
    fi
done

echo "✅ Log upload complete"
