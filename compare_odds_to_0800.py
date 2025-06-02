import os
import json
import argparse
from datetime import date
from pathlib import Path

def get_earliest_snapshot_path(snapshot_dir="odds_snapshots"):
    today = date.today().isoformat()
    snapshot_files = [
        f for f in os.listdir(snapshot_dir)
        if f.startswith(today) and f.endswith(".json")
    ]
    if not snapshot_files:
        raise FileNotFoundError("⚠️ No snapshot files found for today")
    
    earliest = sorted(snapshot_files)[0]
    return os.path.join(snapshot_dir, earliest)

def load_snapshot(file_path):
    with open(file_path) as f:
        return json.load(f)

def find_steamers(snapshot_earlier, snapshot_later, drop_pct=30.0):
    early_map = {
        (item['market_id'], item['selection_id']): item
        for item in snapshot_earlier
        if item.get("price")
    }

    steamers = []
    for item in snapshot_later:
        key = (item['market_id'], item['selection_id'])
        early = early_map.get(key)
        if not early:
            continue

        early_price = early.get("price")
        later_price = item.get("price")
        if early_price and later_price and later_price < early_price:
            drop = ((early_price - later_price) / early_price) * 100
            if drop >= drop_pct:
                steamer = item.copy()
                steamer['early_price'] = early_price
                steamer['drop_pct'] = round(drop, 1)
                steamers.append(steamer)

    return steamers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=str, required=True, help="Path to current snapshot JSON")
    parser.add_argument("--label", type=str, default="current", help="Label to save output under")
    args = parser.parse_args()

    base_dir = "odds_snapshots"
    earliest_path = get_earliest_snapshot_path(base_dir)
    current_path = args.snapshot
    label = args.label
    date_str = date.today().isoformat()

    print(f"📥 Loading earliest: {earliest_path}")
    print(f"📥 Loading current: {current_path}")

    snapshot_earlier = load_snapshot(earliest_path)
    snapshot_later = load_snapshot(current_path)

    steamers = find_steamers(snapshot_earlier, snapshot_later)

    out_path = os.path.join(base_dir, f"steamers_{date_str}_{label}.json")
    with open(out_path, "w") as f:
        json.dump(steamers, f, indent=2)

    print(f"✅ Found {len(steamers)} steamers. Saved to {out_path}")

if __name__ == "__main__":
    main()

