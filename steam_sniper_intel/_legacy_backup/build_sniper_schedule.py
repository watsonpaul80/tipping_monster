# steam_sniper_intel/build_sniper_schedule.py
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
import sys

# === CONFIG ===
RACEFILE = Path("/home/ec2-user/tipping-monster/rpscrape/batch_inputs") / (datetime.now().strftime("%Y-%m-%d") + ".jsonl")
SCHEDULE_FILE = Path("/home/ec2-user/tipping-monster/steam_sniper_intel/sniper_schedule.txt")
SNAPSHOT_OFFSETS = [60, 30, 10]  # Minutes before race

def wait_for_racefile(max_wait=600, check_interval=10):
    wait_seconds = 0
    while not RACEFILE.exists() and wait_seconds < max_wait:
        print(f"⏳ Waiting for racecards file {RACEFILE}... ({wait_seconds}s elapsed)")
        time.sleep(check_interval)
        wait_seconds += check_interval
    if not RACEFILE.exists():
        print(f"❌ Racecards not found after {max_wait}s. Aborting.")
        sys.exit(1)

def load_race_times():
    times = set()
    with open(RACEFILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                race_str = entry.get("race", "")
                if not race_str:
                    continue
                time_part = race_str.split()[0].strip()
                if ":" not in time_part:
                    continue
                parsed = datetime.strptime(time_part, "%I:%M")  # 12-hour format
                # Force PM assumption (typical UK racing)
                if 1 <= parsed.hour < 12:
                    parsed = parsed.replace(hour=parsed.hour + 12)
                times.add(parsed.strftime("%H:%M"))
            except Exception as e:
                print(f"⚠️ Skipping bad line: {e}")
    print(f"✅ Found race times: {sorted(times)}")
    return sorted(times)

def build_schedule():
    wait_for_racefile()
    race_times = load_race_times()
    today = datetime.now()
    schedule = set()

    for time_str in race_times:
        try:
            race_time = datetime.strptime(time_str, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            for offset in SNAPSHOT_OFFSETS:
                snap_time = race_time - timedelta(minutes=offset)
                if snap_time > datetime.now():
                    schedule.add(snap_time.strftime("%H%M"))
        except Exception as e:
            print(f"⚠️ Error parsing time '{time_str}': {e}")

    if not schedule:
        print("⚠️ No valid snapshot times found. Check racecard content.")
        return

    with open(SCHEDULE_FILE, "w") as f:
        for snap in sorted(schedule):
            f.write(snap + "\n")

    print(f"✅ Schedule written to {SCHEDULE_FILE} with times:\n{sorted(schedule)}")

if __name__ == "__main__":
    build_schedule()

