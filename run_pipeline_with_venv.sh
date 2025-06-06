#!/bin/bash
# Tipping Monster: Full Daily Pipeline (Run from cron or manually)
# Last updated: 2025-06-04

echo "🔄 Starting full pipeline: $(date)"

cd /home/ec2-user/tipping-monster || exit 1

# Activate virtual environment
source .venv/bin/activate

LOG_DIR="/home/ec2-user/tipping-monster/logs"
mkdir -p "$LOG_DIR"

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
.venv/bin/python fetch_betfair_odds.py >> "$LOG_DIR/odds.log" 2>&1

# 4. Run model inference (with last_class)
echo "🧠 Running model inference..."
.venv/bin/python run_inference_and_select_top1.py >> "$LOG_DIR/inference.log" 2>&1

# 5. Merge odds into tips
echo "🔗 Merging tips with odds..."
.venv/bin/python merge_odds_into_tips.py >> "$LOG_DIR/merge.log" 2>&1

# 6. (Optional) Generate commentary
echo "📝 Generating LLM commentary (optional)..."
.venv/bin/python generate_commentary_bedrock.py >> "$LOG_DIR/commentary.log" 2>&1

# 7. Dispatch tips to Telegram
echo "🚀 Dispatching tips to Telegram..."
TODAY=$(date +%F)
DISPATCH_LOG="$LOG_DIR/dispatch_${TODAY}.log"
.venv/bin/python dispatch_tips.py --min_conf 0.80 --telegram >> "$DISPATCH_LOG" 2>&1

# Confirm how many tips were sent
SENT_TIPS_PATH="logs/sent_tips_${TODAY}.jsonl"
SENT_COUNT=$(jq -s length "$SENT_TIPS_PATH" 2>/dev/null || echo "0")
echo "🧾 Dispatched $SENT_COUNT tip(s) to Telegram"

# Optional: Alert if no tips were dispatched
if [ "$SENT_COUNT" -eq 0 ]; then
    echo "⚠️ Warning: No tips were dispatched today." >> "$DISPATCH_LOG"
    curl -s -X POST "https://api.telegram.org/bot8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg/sendMessage" \
        -d chat_id="-1002580022335" \
        -d parse_mode="Markdown" \
        -d text="⚠️ *No tips were dispatched this morning.*\nCheck logs: \`$DISPATCH_LOG\`"
fi

# 8. Upload logs and dispatched tips to S3
echo "🗂️ Uploading tips and logs to S3..."
aws s3 cp "$SENT_TIPS_PATH" s3://tipping-monster/sent_tips/ --only-show-errors
aws s3 cp "logs/tips_results_${TODAY}_advised.csv" s3://tipping-monster/results/ --only-show-errors

echo "✅ Pipeline complete: $(date)"

