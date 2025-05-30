#!/bin/bash

# === CONFIG ===
DATE=$(date +%F)
SOURCE_DIR="/home/ec2-user/tipping-monster"
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

