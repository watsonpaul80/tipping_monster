#!/bin/bash
# Tipping Monster: Full Daily Pipeline (Run from cron or manually)
# Last updated: 2025-07-13
set -euo pipefail

echo "🔄 Starting full pipeline: $(date)"

DEV_MODE=0
if [ "${1:-}" = "--dev" ]; then
    DEV_MODE=1
    export TM_DEV_MODE=1
    export TM_LOG_DIR="logs/dev"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"

cd "$REPO_ROOT" || exit 1

# Activate virtual environment
source .venv/bin/activate

LOG_DIR="$REPO_ROOT/${TM_LOG_DIR:-logs}"
mkdir -p "$LOG_DIR"
mkdir -p "$LOG_DIR/inference" "$LOG_DIR/dispatch"

# 1. Upload racecards
echo "📥 Uploading racecards..."
bash daily_upload_racecards.sh >> "$LOG_DIR/racecards.log" 2>&1

# 2. Flatten racecards
echo "🪬 Flattening racecards..."
bash daily_flatten.sh >> "$LOG_DIR/flatten.log" 2>&1

# === Wait until 08:50 before continuing ===
TARGET_TIME="08:50"
CURRENT_TIME=$(date +%s)
TARGET_EPOCH=$(date -d "$TARGET_TIME" +%s)

if [ "$CURRENT_TIME" -lt "$TARGET_EPOCH" ]; then
    WAIT_SECONDS=$((TARGET_EPOCH - CURRENT_TIME))
    echo "⏳ Waiting until $TARGET_TIME for peak market liquidity ($WAIT_SECONDS seconds)..."
    sleep $WAIT_SECONDS
else
    echo "⏩ It's already past $TARGET_TIME — continuing immediately."
fi

# 3. Fetch Betfair odds
echo "📈 Fetching Betfair odds..."
.venv/bin/python core/fetch_betfair_odds.py >> "$LOG_DIR/odds.log" 2>&1

# 4. Run model inference (with last_class)
echo "🧠 Running model inference..."
.venv/bin/python core/run_inference_and_select_top1.py >> "$LOG_DIR/inference/inference.log" 2>&1

# 5. Merge odds into tips
echo "🔗 Merging tips with odds..."
.venv/bin/python core/merge_odds_into_tips.py >> "$LOG_DIR/merge.log" 2>&1

# 6. (Optional) Generate commentary
# NOTE: The commentary script (`generate_commentary_bedrock.py`) is not included
# in this repository. The call is disabled to avoid errors in the daily cron.
# .venv/bin/python generate_commentary_bedrock.py >> "$LOG_DIR/commentary.log" 2>&1

# 7. Dispatch tips to Telegram
echo "🚀 Dispatching tips to Telegram..."
TODAY=$(date +%F)
DISPATCH_LOG="$LOG_DIR/dispatch/dispatch_${TODAY}.log"
.venv/bin/python core/dispatch_tips.py --min_conf 0.80 --telegram >> "$DISPATCH_LOG" 2>&1

# Confirm how many tips were sent
SENT_TIPS_PATH="$REPO_ROOT/logs/dispatch/sent_tips_${TODAY}.jsonl"
if [ -f "$SENT_TIPS_PATH" ]; then
    SENT_COUNT=$(wc -l < "$SENT_TIPS_PATH")
else
    SENT_COUNT=0
fi
SENT_COUNT="$(echo "$SENT_COUNT" | tr -d '[:space:]')"
echo "🧾 Dispatched $SENT_COUNT tip(s) to Telegram"

# Optional: Alert if no tips were dispatched
if [ "$SENT_COUNT" -eq 0 ]; then
    echo "⚠️ Warning: No tips were dispatched today." >> "$DISPATCH_LOG"
    if [ "$DEV_MODE" -eq 0 ]; then
        curl -s --max-time 10 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_CHAT_ID}" \
            -d parse_mode="Markdown" \
            -d text="⚠️ *No tips were dispatched this morning.*\nCheck logs: \`$DISPATCH_LOG\`"
    fi
fi

# 8. Upload logs and dispatched tips to S3
if [ "$DEV_MODE" -eq 0 ]; then
    if command -v aws >/dev/null; then
        echo "🗂️ Uploading tips and logs to S3..."
        aws s3 cp "$SENT_TIPS_PATH" s3://tipping-monster/sent_tips/ --only-show-errors
        aws s3 cp "$REPO_ROOT/logs/roi/tips_results_${TODAY}_advised.csv" s3://tipping-monster/results/ --only-show-errors
    else
        echo "⚠️ AWS CLI not found, skipping S3 uploads"
    fi
else
    echo "[DEV] Skipping S3 uploads"
fi

echo "✅ Pipeline complete: $(date)"

