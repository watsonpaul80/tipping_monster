import os
from generate_race_schedule import generate_schedule_times

# === CONFIG ===
SCRIPT_PATH = "/home/ec2-user/tipping-monster/steam_sniper_auto_workflow.sh"
SCHEDULE_PATH = "steam_sniper_schedule.sh"

# === Build Sniper Schedule ===
schedule_times = generate_schedule_times()

with open(SCHEDULE_PATH, "w") as f:
    for time_str in sorted(schedule_times):
        f.write(f"echo '{SCRIPT_PATH}' | at {time_str}\n")

print(f"✅ Saved sniper script: {SCHEDULE_PATH}")

