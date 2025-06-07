#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
cd "$REPO_ROOT" || exit 1
source "$REPO_ROOT/.venv/bin/activate"
# Clean up old model artifacts
LOG_DIR="$REPO_ROOT/logs"
echo "[INFO] Cleaning old models..." >> "$LOG_DIR/train.log"
rm -f "$REPO_ROOT/models/model-*.json"
rm -f "$REPO_ROOT/models/model-*.bst"
rm -f "$REPO_ROOT/models/model-*.tar.gz"

python core/train_model_v6.py >> "$LOG_DIR/train_$(date +%F).log" 2>&1

