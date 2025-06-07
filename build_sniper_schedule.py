#!/usr/bin/env python3
import os
from pathlib import Path
from generate_race_schedule import generate_schedule_times

# === CONFIG ===
REPO_ROOT = Path(os.getenv("TM_ROOT", Path(__file__).resolve().parent))
SCRIPT_PATH = REPO_ROOT / "steam_sniper_auto_workflow.sh"
SCHEDULE_PATH = "steam_sniper_schedule.sh"

# === Build Sniper Schedule ===
schedule_times = generate_schedule_times()

with open(SCHEDULE_PATH, "w") as f:
    for time_str in sorted(schedule_times):
        f.write(f"echo '{str(SCRIPT_PATH)}' | at {time_str}\n")

print(f"✅ Saved sniper script: {SCHEDULE_PATH}")

