import json
from pathlib import Path
from datetime import datetime

SNIPER_DATA_DIR = Path("steam_sniper_intel/sniper_data")

def load_snapshots(date_str):
    files = sorted(SNIPER_DATA_DIR.glob(f"{date_str}_*.json"))
    snapshots = []
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
            snapshots.append((f.stem.split('_')[1], data))  # (label, data)
    return snapshots

def merge_odds_progression(snapshots):
    merged = {}
    for label, data in snapshots:
        for runner in data:
            key = (runner["race"], runner["horse"])
            if key not in merged:
                merged[key] = {
                    "race": runner["race"],
                    "horse": runner["horse"],
                    "odds_progression": [],
                    "volume": 0
                }
            merged[key]["odds_progression"].append(runner.get("price"))
            merged[key]["volume"] = max(merged[key]["volume"], runner.get("volume", 0))

    return list(merged.values())

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    snapshots = load_snapshots(today)
    merged_data = merge_odds_progression(snapshots)

    output_file = SNIPER_DATA_DIR / f"merged_{today}.json"
    with open(output_file, "w") as f:
        json.dump(merged_data, f, indent=2)
    print(f"[+] Saved merged sniper data to {output_file}")

if __name__ == "__main__":
    main()

