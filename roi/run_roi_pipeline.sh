#!/bin/bash
set -e

# Accept optional override date
if [[ -n "$1" ]]; then
    DATE="$1"
else
    DATE=$(date +%F)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"

PYTHON="$REPO_ROOT/.venv/bin/python"
LOGDIR="$REPO_ROOT/logs/roi"
SENT_TIPS="$REPO_ROOT/logs/dispatch/sent_tips_${DATE}.jsonl"
PREDICTIONS="$REPO_ROOT/predictions/${DATE}/tips_with_odds.jsonl"

mkdir -p $LOGDIR

echo "🔁 Injecting realistic odds..."
$PYTHON core/extract_best_realistic_odds.py --date $DATE >> $LOGDIR/inject_real_odds_$DATE.log 2>&1

echo "📊 Generating ROI CSVs..."
$PYTHON roi/generate_tip_results_csv_with_mode_FINAL.py --mode advised --date $DATE >> $LOGDIR/generate_roi_csv_$DATE.log 2>&1

if [[ -f "$SENT_TIPS" ]]; then
    echo "📊 Tracking ROI (advised)..."
    $PYTHON roi/roi_tracker_advised.py --mode advised --date $DATE --use_sent > $LOGDIR/roi_advised_$DATE.log 2>&1
else
    echo "⚠️ Sent tips file not found: $SENT_TIPS — skipping advised ROI"
fi

if [[ -f "$PREDICTIONS" ]]; then
    echo "📊 Tracking ROI (level)..."
    $PYTHON roi/roi_tracker_advised.py --mode level --date $DATE > $LOGDIR/roi_level_$DATE.log 2>&1
else
    echo "⚠️ Predictions file not found: $PREDICTIONS — skipping level ROI"
fi

echo "📤 Sending daily ROI summary..."
$PYTHON roi/send_daily_roi_summary.py --date $DATE >> $LOGDIR/roi_telegram_$DATE.log 2>&1

echo "🏷️ Updating tag ROI tracker..."
$PYTHON roi/tag_roi_tracker.py --date $DATE --mode advised >> $LOGDIR/tag_roi_$DATE.log 2>&1

