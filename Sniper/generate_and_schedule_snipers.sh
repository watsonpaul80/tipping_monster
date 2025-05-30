#!/bin/bash

# Activate python virtualenv
source ../.venv/bin/activate

SCHEDULE_FILE="steam_sniper_intel/sniper_schedule.txt"
PIPELINE_SCRIPT="steam_sniper_intel/run_sniper_pipeline.sh"

if [ ! -f "$SCHEDULE_FILE" ]; then
    echo "Schedule file not found: $SCHEDULE_FILE"
    exit 1
fi

while IFS= read -r label; do
    hour="${label:0:2}"
    minute="${label:2:2}"

    # Schedule pipeline run with 'at'
    echo "$PIPELINE_SCRIPT $label" | at $hour:$minute
    echo "Scheduled sniper job at $hour:$minute"
done < "$SCHEDULE_FILE"

