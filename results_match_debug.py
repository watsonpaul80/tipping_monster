
import pandas as pd
import json
import argparse
from pathlib import Path

def normalize_time(time_str):
    """Convert 1:20 or 01:20 to 13:20 if PM is likely"""
    parts = time_str.strip().split(":")
    hour = int(parts[0])
    minute = parts[1]
    if hour < 8:
        hour += 12  # assume PM for racing times
    return f"{hour:02}:{minute}"

def normalize_course(course):
    return course.lower().replace(" ", "").replace("(ire)", "").strip()

def main(date_str):
    tips_path = Path(f"predictions/{date_str}/tips_with_odds.jsonl")
    results_path = Path(f"rpscrape/data/dates/all/{date_str.replace('-', '_')}.csv")

    if not tips_path.exists():
        print(f"Missing tips file: {tips_path}")
        return
    if not results_path.exists():
        print(f"Missing results file: {results_path}")
        return

    tips = [json.loads(l) for l in open(tips_path) if '"race":' in l]
    results_df = pd.read_csv(results_path)
    results_df.columns = results_df.columns.str.lower()

    results_df["key"] = results_df["off"].str[:5] + " " + results_df["course"].apply(normalize_course)
    available_keys = set(results_df["key"])

    print(f"✅ Loaded {len(tips)} tips and {len(results_df)} results")

    unmatched = []
    for tip in tips:
        try:
            raw_time, raw_course = tip["race"].split(" ", 1)
            tip_key = normalize_time(raw_time) + " " + normalize_course(raw_course)
            if tip_key not in available_keys:
                unmatched.append((tip["race"], tip.get("name", "Unknown")))
        except Exception as e:
            unmatched.append((tip.get("race", "??"), f"ERROR: {e}"))

    if not unmatched:
        print("✅ All tips matched successfully!")
    else:
        print(f"❌ {len(unmatched)} unmatched tips:")
        for race, horse in unmatched:
            print(f"🛑 {race:20} – {horse}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    args = parser.parse_args()
    main(args.date)
