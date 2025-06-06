#!/bin/bash

# === Activate python virtualenv ===
source /home/ec2-user/tipping-monster/.venv/bin/activate

# === Full paths ===
BASE_DIR="/home/ec2-user/tipping-monster"
SCHEDULE_FILE="${BASE_DIR}/steam_sniper_intel/sniper_schedule.txt"
PIPELINE_SCRIPT="${BASE_DIR}/steam_sniper_intel/run_sniper_pipeline.sh"
DISPATCH_SCRIPT="${BASE_DIR}/steam_sniper_intel/dispatch_snipers.py"

# === Wait for sniper_schedule.txt ===
TRIES=10
while [ ! -f "$SCHEDULE_FILE" ] && [ $TRIES -gt 0 ]; do
    echo "⏳ Waiting for $SCHEDULE_FILE..."
    sleep 5
    ((TRIES--))
done

if [ ! -f "$SCHEDULE_FILE" ]; then
    echo "❌ Failed to find $SCHEDULE_FILE after waiting"
    exit 1
fi

# === Loop through scheduled times ===
while IFS= read -r label; do
    hour="${label:0:2}"
    minute="${label:2:2}"

    CMD="/bin/bash $PIPELINE_SCRIPT $label && \
python $DISPATCH_SCRIPT --source ${BASE_DIR}/steam_sniper_intel/steamers_$(date +%F)_${label}.json"

    echo "$CMD" | at $hour:$minute
    echo "✅ Scheduled sniper + dispatch for $hour:$minute"
done < "$SCHEDULE_FILE"

