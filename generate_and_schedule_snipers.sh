#!/bin/bash
# Run this at 05:10 daily (manually or via cron)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TM_ROOT:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"

cd "$REPO_ROOT/steam_sniper_intel" || exit 1

# Step 1: Activate venv and generate sniper schedule
source "$REPO_ROOT/.venv/bin/activate"
python build_sniper_schedule.py

# Step 2: Schedule sniper jobs using 'at' for each label
SCHEDULE_FILE="sniper_schedule.txt"
PIPELINE_SCRIPT="$REPO_ROOT/steam_sniper_intel/run_sniper_pipeline.sh"

if [ ! -f "$SCHEDULE_FILE" ]; then
    echo "❌ Schedule file not found: $SCHEDULE_FILE"
    exit 1
fi

while IFS= read -r label; do
    hour="${label:0:2}"
    minute="${label:2:2}"

    # Create inline script block to run the sniper job
    at $hour:$minute <<EOF
cd "$REPO_ROOT"
source .venv/bin/activate
bash "$PIPELINE_SCRIPT" $label
EOF

    echo "⏱ Scheduled sniper job at $hour:$minute (Label: $label)"
done < "$SCHEDULE_FILE"

