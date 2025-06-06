#!/bin/bash
set -e

# Accept optional override date
if [[ -n "$1" ]]; then
    DATE="$1"
else
    DATE=$(date +%F)
fi

PYTHON="/home/ec2-user/tipping-monster/.venv/bin/python"
LOGDIR="/home/ec2-user/tipping-monster/logs/roi"
SENT_TIPS="logs/dispatch/sent_tips_${DATE}.jsonl"
PREDICTIONS="predictions/${DATE}/tips_with_odds.jsonl"

mkdir -p $LOGDIR

echo "🔁 Injecting realistic odds..."
$PYTHON extract_best_realistic_odds.py --date $DATE >> $LOGDIR/inject_real_odds_$DATE.log 2>&1

echo "📊 Generating ROI CSVs..."
$PYTHON generate_tip_results_csv_with_mode_FINAL.py --mode advised --date $DATE >> $LOGDIR/generate_roi_csv_$DATE.log 2>&1

if [[ -f "$SENT_TIPS" ]]; then
    echo "📊 Tracking ROI (advised)..."
    $PYTHON roi_tracker_advised.py --mode advised --date $DATE --use_sent > $LOGDIR/roi_advised_$DATE.log 2>&1
else
    echo "⚠️ Sent tips file not found: $SENT_TIPS — skipping advised ROI"
fi

if [[ -f "$PREDICTIONS" ]]; then
    echo "📊 Tracking ROI (level)..."
    $PYTHON roi_tracker_advised.py --mode level --date $DATE > $LOGDIR/roi_level_$DATE.log 2>&1
else
    echo "⚠️ Predictions file not found: $PREDICTIONS — skipping level ROI"
fi

echo "📤 Sending daily ROI summary..."
$PYTHON send_daily_roi_summary.py --date $DATE >> $LOGDIR/roi_telegram_$DATE.log 2>&1

echo "🏷️ Updating tag ROI tracker..."
$PYTHON tag_roi_tracker.py --date $DATE --mode advised >> $LOGDIR/tag_roi_$DATE.log 2>&1

