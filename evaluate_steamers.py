import os
import glob
import json
import pandas as pd
from datetime import datetime

DATE = datetime.now().strftime("%Y-%m-%d")
DATE_CSV = datetime.now().strftime("%Y_%m_%d")
STEAMER_FILES = glob.glob(f"steamers_{DATE}_*.json")
RESULTS_PATH = f"rpscrape/data/dates/all/{DATE_CSV}.csv"
OUT_PATH = f"logs/sniper/steam_snipers_results_{DATE}.csv"

# === Load race results if available ===
if os.path.exists(RESULTS_PATH):
    results_df = pd.read_csv(RESULTS_PATH)
    results_df["horse"] = results_df["horse"].str.lower().str.strip()
    results_df["race"] = results_df["race"].str.lower().str.strip()
else:
    print(f"[!] No results file for {DATE} — continuing without ROI checks")
    results_df = pd.DataFrame()

# === Process each steamers file ===
records = []

for path in STEAMER_FILES:
    with open(path, "r") as f:
        steamers = json.load(f)
    label = path.split("_")[-1].split(".")[0]  # e.g. "1425"

    for s in steamers:
        race = s["race"].lower().strip()
        horse = s["horse"].lower().strip()

        if results_df.empty:
            pos = "?"
            profit = 0.0
        else:
            match = results_df[(results_df["race"] == race) & (results_df["horse"] == horse)]
            if match.empty:
                print(f"[!] No result found for {horse} in {race}")
                continue

            row = match.iloc[0]
            # results CSV uses the column name 'pos' for finishing position
            # rather than 'position'
            pos = str(row["pos"]).lower()

            ew = s["old_price"] >= 5.0
            profit = 0.0

            if pos == "1":
                if ew:
                    profit += 0.5 * (s["new_price"] - 1)  # Win half
                    profit += 0.5 * ((s["new_price"] * 0.2) - 1)  # Place half
                else:
                    profit += (s["new_price"] - 1)
            elif pos in ["2", "3"]:
                if ew:
                    profit += 0.5 * ((s["new_price"] * 0.2) - 1)
                else:
                    profit -= 1
            else:
                profit -= 1

        records.append({
            "Date": DATE,
            "Race": s["race"],
            "Horse": s["horse"],
            "Old Odds": s["old_price"],
            "New Odds": s["new_price"],
            "Drop %": s["drop_pct"],
            "Snapshot": label,
            "Result": pos,
            "Profit": round(profit, 2)
        })

# === Save results ===
df = pd.DataFrame(records)
if not df.empty:
    df.to_csv(OUT_PATH, index=False)
    print(f"[+] Logged {len(df)} steamers to {OUT_PATH}")
else:
    print("[+] No steamers matched results yet.")

