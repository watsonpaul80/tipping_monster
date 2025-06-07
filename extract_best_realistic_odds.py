#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from datetime import datetime


def extract_race_key(race_str):
    """Parse a race string like '15:30 Chelmsford' into minutes and course."""
    try:
        time_part, course = race_str.split(" ", 1)
        h, m = map(int, time_part.strip().split(":"))
        course = course.strip().lower()
        if not course:
            return None, None
        return h * 60 + m, course
    except Exception:
        return None, None


def load_snapshots(date_str):
    snapshot_dir = Path("odds_snapshots")
    data_by_time = []
    for file in snapshot_dir.glob(f"{date_str}_*.json"):
        label = file.stem.split("_")[1].replace("-", "")
        try:
            h = int(label[:2])
            m = int(label[2:])
            snapshot_time = h * 60 + m
            with open(file) as f:
                data = json.load(f)
                data_by_time.append((snapshot_time, data))
        except BaseException:
            continue
    return sorted(data_by_time)


def find_best_odds(race_time_minutes, course, horse_name, snapshots):
    for label_minutes, runners in reversed(snapshots):
        if label_minutes >= race_time_minutes:
            continue
        for r in runners:
            snap_course = r.get("race", "").split(" ", 1)[-1].strip().lower()
            snap_name = r.get("horse", "").strip().lower()
            if snap_course == course and snap_name == horse_name:
                return r.get("price")
    return None


def main(date_str):
    sent_tips_path = Path(f"logs/dispatch/sent_tips_{date_str}.jsonl")
    output_path = Path(f"logs/dispatch/sent_tips_{date_str}_realistic.jsonl")

    if not sent_tips_path.exists():
        print(f"❌ Sent tips file not found: {sent_tips_path}")
        return

    snapshots = load_snapshots(date_str)
    if not snapshots:
        print("❌ No snapshots available to pull odds from.")
        return

    adjusted = []
    with open(sent_tips_path, "r") as f:
        for line in f:
            tip = json.loads(line)
            race = tip.get("race", "")
            name = tip.get("name", "").strip().lower()
            race_minutes, course = extract_race_key(race)
            if race_minutes is None:
                continue
            realistic_odds = find_best_odds(
                race_minutes, course, name, snapshots)
            if realistic_odds:
                tip["realistic_odds"] = realistic_odds
            else:
                tip["realistic_odds"] = tip.get("bf_sp", tip.get("odds", 0.0))
            adjusted.append(tip)

    with open(output_path, "w") as f:
        for tip in adjusted:
            f.write(json.dumps(tip) + "\n")

    print(f"✅ Realistic odds injected and saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        help="Date string in YYYY-MM-DD format",
        default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    main(args.date)
