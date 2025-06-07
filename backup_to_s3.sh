#!/bin/bash

# === CONFIG ===
DATE=$(date +%F)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
SOURCE_DIR="$REPO_ROOT"
ARCHIVE_PATH="/tmp/tipping-monster-backup-$DATE.tar.gz"
S3_BUCKET="s3://tipping-monster-backups"

# === CREATE ARCHIVE ===
echo "[+] Zipping $SOURCE_DIR into $ARCHIVE_PATH"
tar --exclude='*.pyc' --exclude='env' --exclude='__pycache__' -czf "$ARCHIVE_PATH" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

# === UPLOAD TO S3 ===
echo "[+] Uploading to $S3_BUCKET/$DATE/"
aws s3 cp "$ARCHIVE_PATH" "$S3_BUCKET/$DATE/tipping-monster-backup.tar.gz"

# === CLEANUP ===
echo "[+] Cleaning up archive"
rm -f "$ARCHIVE_PATH"

echo "[✓] Backup complete at $(date)"

