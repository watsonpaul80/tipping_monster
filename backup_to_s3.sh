#!/bin/bash

# === CONFIG ===
DATE=$(date +%F)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
SOURCE_DIR="$REPO_ROOT"
ARCHIVE_PATH="/tmp/tipping-monster-backup-$DATE.tar.gz"
S3_BUCKET="s3://tipping-monster-backups"
DEV_MODE=0
if [ "$1" = "--dev" ]; then
    DEV_MODE=1
    export TM_DEV_MODE=1
    export TM_LOG_DIR="logs/dev"
fi

# === CREATE ARCHIVE ===
echo "[+] Zipping $SOURCE_DIR into $ARCHIVE_PATH"
tar --exclude='*.pyc' --exclude='env' --exclude='__pycache__' -czf "$ARCHIVE_PATH" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

# === UPLOAD TO S3 ===
if [ "$DEV_MODE" -eq 0 ]; then
    echo "[+] Uploading to $S3_BUCKET/$DATE/"
    aws s3 cp "$ARCHIVE_PATH" "$S3_BUCKET/$DATE/tipping-monster-backup.tar.gz"
else
    echo "[DEV] Skipping S3 upload"
fi

# === CLEANUP ===
echo "[+] Cleaning up archive"
rm -f "$ARCHIVE_PATH"

echo "[✓] Backup complete at $(date)"

