#!/bin/bash
set -e

# Use today's date — all data is same-day now
DATE=$(date +%F)
PYTHON="/home/ec2-user/tipping-monster/.venv/bin/python"
LOGDIR="/home/ec2-user/tipping-monster/logs/roi_logs"

mkdir -p $LOGDIR

echo "🔁 Injecting realistic odds..."
$PYTHON /home/ec2-user/tipping-monster/extract_best_realistic_odds.py --date $DATE >> $LOGDIR/inject_real_odds_$DATE.log 2>&1

echo "📊 Tracking ROI (advised)..."
$PYTHON /home/ec2-user/tipping-monster/roi_tracker_advised.py --mode advised --date $DATE --use_sent --telegram > $LOGDIR/roi_advised_$DATE.log 2>&1

echo "📊 Tracking ROI (level)..."
$PYTHON /home/ec2-user/tipping-monster/roi_tracker_advised.py --mode level --date $DATE > $LOGDIR/roi_level_$DATE.log 2>&1

echo "📤 Sending daily ROI summary..."
$PYTHON /home/ec2-user/tipping-monster/send_daily_roi_summary.py --date $DATE >> $LOGDIR/roi_telegram_$DATE.log 2>&1

echo "🏷️ Updating tag ROI tracker..."
$PYTHON /home/ec2-user/tipping-monster/tag_roi_tracker.py --date $DATE --mode advised >> $LOGDIR/tag_roi_$DATE.log 2>&1

