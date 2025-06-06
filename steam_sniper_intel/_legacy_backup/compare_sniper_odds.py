# compare_sniper_odds.py

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

SNAPSHOT_DIR = "steam_sniper_intel/sniper_data"

def load_snapshot(path):
    with open(path) as f:
        return json.load(f)

def find_earliest_snapshot(date_str):
    files = sorted([
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.startswith(date_str) and f.endswith(".json")
    ])
    return files[0] if files else None

def save_steamers(steamers, date_str, label):
    out_path = os.path.join(SNAPSHOT_DIR, f"steamers_{date_str}_{label}.json")
    with open(out_path, "w") as f:
        json.dump(steamers, f, indent=2)
    print(f"✅ {len(steamers)} steamers saved to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, help="Later snapshot to compare")
    parser.add_argument("--label", required=True, help="Time label for output file")
    args = parser.parse_args()

    snapshot_later_path = args.snapshot
    date_str = Path(snapshot_later_path).stem.split("_")[0]
    earliest_name = find_earliest_snapshot(date_str)

    if not earliest_name:
        print("❌ No early snapshot found")
        return

    snapshot_early_path = os.path.join(SNAPSHOT_DIR, earliest_name)
    print(f"📥 Loading earliest: {snapshot_early_path}")
    print(f"📥 Loading current: {snapshot_later_path}")

    snapshot_early = load_snapshot(snapshot_early_path)
    snapshot_later = load_snapshot(snapshot_later_path)

    early_map = {
        (entry["market_id"], entry["selection_id"]): entry
        for entry in snapshot_early if entry.get("price")
    }

    steamers = []

    for later_entry in snapshot_later:
        key = (later_entry["market_id"], later_entry["selection_id"])
        if not later_entry.get("price") or key not in early_map:
            continue

        early_price = early_map[key]["price"]
        new_price = later_entry["price"]

        if early_price > new_price:
            drop_pct = (early_price - new_price) / early_price
            if drop_pct >= 0.30:
                steamers.append({
                    "race": later_entry["race"],
                    "horse": later_entry["horse"],
                    "price_then": round(early_price, 2),
                    "price_now": round(new_price, 2),
                    "drop_pct": round(drop_pct * 100, 1),
                    "market_id": later_entry["market_id"],
                    "selection_id": later_entry["selection_id"],
                })

    save_steamers(steamers, date_str, args.label)

if __name__ == "__main__":
    main()

