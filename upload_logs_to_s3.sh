#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TM_ROOT:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
LOG_DIR="$REPO_ROOT/logs"
S3_BUCKET="tipping-monster"
S3_PREFIX="logs-archive"
TMP_ZIP="/tmp/tipping-monster-logs-$(date +%F).zip"

# Zip all logs older than 7 days
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -print0 | zip -@ "$TMP_ZIP"

if [ -f "$TMP_ZIP" ]; then
    aws s3 cp "$TMP_ZIP" "s3://$S3_BUCKET/$S3_PREFIX/$(basename $TMP_ZIP)"
    if [ $? -eq 0 ]; then
        echo "Uploaded $TMP_ZIP to s3://$S3_BUCKET/$S3_PREFIX/"
        # Optional: delete zipped file after upload
        rm "$TMP_ZIP"
        # Optional: delete local logs after successful upload
        find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete
    else
        echo "Upload failed!"
    fi
else
    echo "No logs to zip/upload."
fi

