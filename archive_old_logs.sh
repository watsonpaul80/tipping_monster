#!/bin/bash
# Archive log files older than a given number of days into zipped files.
# Defaults to 14 days.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
ARCHIVE_DIR="${LOG_DIR}/archive"
DAYS="${1:-14}"

mkdir -p "$ARCHIVE_DIR"

find "$LOG_DIR" -type f -name '*.log' -mtime +"$DAYS" | while read -r FILE; do
    REL_PATH="${FILE#$LOG_DIR/}"
    ZIP_PATH="${ARCHIVE_DIR}/${REL_PATH%.log}.zip"
    mkdir -p "$(dirname "$ZIP_PATH")"
    zip -j "$ZIP_PATH" "$FILE" && rm "$FILE"
done


