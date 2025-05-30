import json
from pathlib import Path
from datetime import datetime
import argparse
import logging

SNIPER_DATA_DIR = Path("steam_sniper_intel/sniper_data")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def load_merged(date_str: str):
    path = SNIPER_DATA_DIR / f"merged_{date_str}.json"
    if not path.exists():
        logging.error(f"Merged data file not found: {path}")
        return []
    with open(path, "r") as f:
        return json.load(f)

def detect_steamers(merged_data):
    steamers = []
    for runner in merged_data:
        odds_prog = runner.get("odds_progression", [])
        if not odds_prog or len(odds_prog) < 2:
            continue
        if any(o is None for o in odds_prog):
            continue

        first_odds = odds_prog[0]
        last_odds = odds_prog[-1]

        if first_odds <= last_odds:
            continue

        drop_pct = (first_odds - last_odds) / first_odds
        if drop_pct >= 0.3:
            steamer = {
                "race": runner.get("race", "Unknown"),
                "horse": runner.get("horse", "Unknown"),
                "odds_progression": odds_prog,
                "volume": runner.get("volume", 0),
                "drop_pct": round(drop_pct * 100, 1)
            }
            steamers.append(steamer)

    logging.info(f"Detected {len(steamers)} steamers with ≥30% drop")
    return steamers

def save_steamers(steamers, date_str, label):
    out_file = SNIPER_DATA_DIR / f"steamers_{date_str}_{label}.json"
    with open(out_file, "w") as f:
        json.dump(steamers, f, indent=2)
    logging.info(f"Saved steamers to {out_file}")
    return out_file

def main():
    parser = argparse.ArgumentParser(description="Detect steamers from merged sniper data")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                        help="Date string YYYY-MM-DD (default: today)")
    parser.add_argument("--label", type=str, default=datetime.now().strftime("%H%M"),
                        help="Snapshot label/time e.g. 1420 (default: now)")
    args = parser.parse_args()

    merged_data = load_merged(args.date)
    if not merged_data:
        logging.warning("No merged data to process, exiting.")
        return

    steamers = detect_steamers(merged_data)
    if steamers:
        save_steamers(steamers, args.date, args.label)
    else:
        logging.info("No steamers detected, nothing to save.")

if __name__ == "__main__":
    main()

