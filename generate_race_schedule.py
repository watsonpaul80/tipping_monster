# generate_race_schedule.py
import json
from datetime import datetime, timedelta
import pandas as pd
import os
import re

DATE = datetime.now().strftime("%Y-%m-%d")
CARD_PATH = f"rpscrape/batch_inputs/{DATE}.jsonl"
OUT_PATH = f"logs/sniper/sniper_schedule_{DATE}.json"

def get_snapshot_times(post_time_str):
    post_time = datetime.strptime(post_time_str, "%H:%M")
    return [
        (post_time - timedelta(minutes=60)).strftime("%H:%M"),
        (post_time - timedelta(minutes=30)).strftime("%H:%M"),
        (post_time - timedelta(minutes=10)).strftime("%H:%M"),
    ]

def extract_time(race_str):
    match = re.match(r"(\d{1,2}:\d{2})", race_str)
    return match.group(1) if match else None

schedule = {}

if os.path.exists(CARD_PATH):
    df = pd.read_json(CARD_PATH, lines=True)
    df["post_time"] = df["race"].apply(extract_time)
    for time in df["post_time"].dropna().unique():
        try:
            schedule[time] = get_snapshot_times(time)
        except Exception as e:
            print(f"⚠️ Failed to parse time '{time}': {e}")
            continue

    with open(OUT_PATH, "w") as f:
        json.dump(schedule, f, indent=2)
    print(f"✅ Saved snapshot schedule to {OUT_PATH}")
else:
    print(f"❌ Racecard not found: {CARD_PATH}")

