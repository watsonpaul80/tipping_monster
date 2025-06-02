import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# === ARGUMENTS ===
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="Target date (YYYY-MM-DD). Defaults to yesterday.")
args = parser.parse_args()

if args.date:
    START_DATE = END_DATE = datetime.strptime(args.date, "%Y-%m-%d")
else:
    today = datetime.today()
    START_DATE = END_DATE = today - timedelta(days=1)

# === CONFIG ===
PLACE_LIMIT = 3
PLACE_ODDS_FRACTION = 1 / 5
STAKE = 1.0
STAKE_GBP = 10.0

PRED_DIR = Path("predictions")
RESULT_DIR = Path("rpscrape/data/dates/all")
CSV_OUTPUT = Path("logs/monster_confidence_per_day_with_roi.csv")

bins = [(round(c, 2), round(c + 0.1, 2)) for c in np.arange(0.5, 0.99, 0.1)]
bins.append((0.99, 1.01))

def clean_time(t):
    t = str(t).strip()
    try:
        return datetime.strptime(t, "%I:%M").strftime("%H:%M")
    except:
        try:
            return datetime.strptime(t, "%H:%M").strftime("%H:%M")
        except:
            return t

def clean_course(name):
    return name.strip().lower().split(" (")[0]

def clean_horse(name):
    return name.lower().split(" (")[0].strip()

# === MAIN ===
per_day_data = []
current = START_DATE

while current <= END_DATE:
    date_str = current.strftime("%Y-%m-%d")
    pred_path = PRED_DIR / date_str / "tips_with_odds.jsonl"
    result_path = RESULT_DIR / f"{current.strftime('%Y_%m_%d')}.csv"

    if not pred_path.exists() or not result_path.exists():
        current += timedelta(days=1)
        continue

    with open(pred_path) as f:
        tips = [json.loads(line) for line in f]

    df_results = pd.read_csv(result_path)
    df_results["clean_course"] = df_results["course"].apply(clean_course)
    df_results["clean_time"] = df_results["off"].apply(clean_time)
    df_results["horse_lower"] = df_results["horse"].apply(clean_horse)
    df_results["pos"] = pd.to_numeric(df_results["pos"], errors="coerce").fillna(99).astype(int)

    daily_bins = {f"{low:.2f}–{high:.2f}": {
        "tips": 0, "wins": 0, "places": 0,
        "win_pnl": 0.0, "ew_pnl": 0.0
    } for (low, high) in bins}

    for tip in tips:
        try:
            time_part, course_part = tip["race"].strip().split(" ", 1)
            tip_time = clean_time(time_part)
            tip_course = clean_course(course_part)
            tip_name = clean_horse(tip["name"])
            conf = float(tip.get("confidence", 0))
            odds = float(tip.get("bf_sp", 0))

            bin_key = next(
                (f"{low:.2f}–{high:.2f}" for (low, high) in bins if low <= conf < high),
                None
            )
            if not bin_key:
                continue

            match = df_results[
                (df_results["clean_course"] == tip_course) &
                (df_results["clean_time"] == tip_time) &
                (df_results["horse_lower"] == tip_name)
            ]

            if match.empty:
                continue

            pos = match.iloc[0]["pos"]
            is_win = pos == 1
            is_place = pos <= PLACE_LIMIT
            win_pnl = (odds - 1) * STAKE if is_win else -STAKE

            if odds >= 5.0:
                place_pnl = ((odds * PLACE_ODDS_FRACTION) - 1) * (STAKE / 2) if is_place else -(STAKE / 2)
                ew_pnl = place_pnl + (STAKE / 2 if is_win else -(STAKE / 2))
            else:
                ew_pnl = 0.0

            stats = daily_bins[bin_key]
            stats["tips"] += 1
            stats["wins"] += int(is_win)
            stats["places"] += int(is_place)
            stats["win_pnl"] += win_pnl
            stats["ew_pnl"] += ew_pnl

        except Exception:
            continue

    for bin_key, stats in daily_bins.items():
        tips = stats["tips"]
        win_pnl = stats["win_pnl"]
        ew_pnl = stats["ew_pnl"]
        win_roi = (win_pnl / tips * 100) if tips else 0
        ew_roi = (ew_pnl / tips * 100) if tips else 0

        per_day_data.append({
            "Date": date_str,
            "Confidence Bin": bin_key,
            "Tips": tips,
            "Wins": stats["wins"],
            "Win %": round(stats["wins"] / tips * 100, 2) if tips else 0,
            "Places": stats["places"],
            "Place %": round(stats["places"] / tips * 100, 2) if tips else 0,
            "Win PnL": round(win_pnl, 2),
            "EW PnL (5.0+)": round(ew_pnl, 2),
            "Win ROI %": round(win_roi, 2),
            "EW ROI %": round(ew_roi, 2),
            "Win Profit £": round(win_pnl * STAKE_GBP, 2),
            "EW Profit £": round(ew_pnl * STAKE_GBP, 2),
        })

    current += timedelta(days=1)

# === SAVE (DEDUPLICATED) CSV ===
df = pd.DataFrame(per_day_data)

if CSV_OUTPUT.exists():
    existing = pd.read_csv(CSV_OUTPUT)
    if not df.empty and "Date" in df.columns:
        existing = existing[~existing["Date"].isin(df["Date"])]
        df = pd.concat([existing, df], ignore_index=True)
    else:
        print("⚠️ No new data to append or missing 'Date' column in new DataFrame.")
        df = existing

df.to_csv(CSV_OUTPUT, index=False)
print(f"✅ Overwrote ROI report with deduplicated data to {CSV_OUTPUT}")

