#!/usr/bin/env python3
import json
from pathlib import Path

PREDICTIONS_DIR = Path("predictions")
OUTPUT_DIR = Path("logs")


def process_day(dir_path: Path):
    tips_file = dir_path / "tips_with_odds.jsonl"
    if not tips_file.exists():
        print(f"❌ Missing: {tips_file}")
        return
    date_str = dir_path.name
    out_path = OUTPUT_DIR / f"sent_tips_{date_str}.jsonl"
    with open(tips_file, "r") as infile, open(out_path, "w") as outfile:
        for line in infile:
            tip = json.loads(line)
            outfile.write(json.dumps(tip) + "\n")
    print(f"✅ Backfilled: {out_path}")


def run():
    for day_dir in sorted(PREDICTIONS_DIR.iterdir()):
        if day_dir.is_dir():
            process_day(day_dir)


if __name__ == "__main__":
    run()
