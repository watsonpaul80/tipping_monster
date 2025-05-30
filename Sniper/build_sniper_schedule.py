from datetime import datetime, timedelta
from pathlib import Path
import json

RACECARDS_PATH = Path("rpscrape/batch_inputs") / datetime.now().strftime("%Y-%m-%d") + ".jsonl"
SCHEDULE_FILE = Path("steam_sniper_intel/sniper_schedule.txt")
SNAPSHOT_OFFSETS = [60, 30, 10]  # minutes before race time

def load_race_times():
    times = set()
    with open(RACECARDS_PATH, "r") as f:
        for line in f:
            entry = json.loads(line)
            race_str = entry.get("race", "")
            time_part = race_str.split()[0]  # grabs "8:22" from "8:22 Kempton (AW)"
            times.add(time_part)
    return sorted(times)

def build_schedule():
    race_times = load_race_times()
    today = datetime.now()
    schedule = set()

    for time_str in race_times:
        try:
            race_time = datetime.strptime(time_str, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
            for offset in SNAPSHOT_OFFSETS:
                snap_time = race_time - timedelta(minutes=offset)
                if snap_time > datetime.now():
                    schedule.add(snap_time.strftime("%H%M"))
        except Exception as e:
            print(f"Error parsing race time '{time_str}': {e}")

    with open(SCHEDULE_FILE, "w") as f:
        for snap in sorted(schedule):
            f.write(snap + "\n")

    print(f"Schedule written to {SCHEDULE_FILE} with times:\n{sorted(schedule)}")

if __name__ == "__main__":
    build_schedule()

