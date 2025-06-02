import argparse
import os
import pandas as pd
import json
from datetime import datetime
import requests
import re

# === Telegram Config ===
TELEGRAM_TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
TELEGRAM_CHAT_ID = "-1002580022335"  # Tipping Monster channel

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    requests.post(url, data=payload)

def get_place_terms(row):
    try:
        runners = int(row.get("Runners", 0))
        is_handicap = "hcp" in str(row.get("Race Name", "")).lower()
        if is_handicap:
            if runners >= 16:
                return (0.25, 4)
            elif 12 <= runners <= 15:
                return (0.25, 3)
        if runners >= 8:
            return (0.20, 3)
        elif 5 <= runners <= 7:
            return (0.25, 2)
    except Exception:
        pass
    return (0.0, 1)  # Win only fallback

def normalize_horse_name(name):
    return re.sub(r"\s*\(.*?\)", "", str(name)).strip().lower()

def calculate_profit(row):
    odds = row["Odds"]
    position = str(row["Position"]).lower()
    stake = row["Stake"]

    if odds >= 5.0:
        win_stake = 0.5
        place_stake = 0.5
        place_fraction, place_places = get_place_terms(row)

        win_profit = (odds - 1) * win_stake if position == "1" else 0.0
        place_profit = ((odds * place_fraction) - 1) * place_stake if position.isdigit() and int(position) <= place_places and place_places > 1 else 0.0
        return round(win_profit + place_profit, 2)
    else:
        win_profit = (odds - 1) * stake if position == "1" else -stake
        return round(win_profit, 2)

def load_tips(date_str, min_conf, use_sent):
    if use_sent:
        input_file = f"logs/sent_tips_{date_str}_realistic.jsonl"
        if not os.path.exists(input_file):
            input_file = f"logs/sent_tips_{date_str}.jsonl"
    else:
        input_file = f"predictions/{date_str}/tips_with_odds.jsonl"

    if not os.path.exists(input_file):
        print(f"Missing tips file: {input_file}")
        return []

    tips = []
    with open(input_file, "r") as f:
        for line in f:
            tip = json.loads(line)
            if tip.get("confidence", 0.0) >= min_conf:
                tip["Race Time"] = tip.get("race", "??:?? Unknown").split()[0]
                tip["Course"] = " ".join(tip.get("race", "??:?? Unknown").split()[1:])
                tip["Horse"] = normalize_horse_name(tip.get("name", "Unknown"))
                tip["Confidence"] = tip.get("confidence", 0.0)
                bf_sp = tip.get("bf_sp", tip.get("odds", 0.0))
                realistic = tip.get("realistic_odds", bf_sp)
                tip["Odds"] = realistic
                tip["odds_delta"] = round(realistic - bf_sp, 2)
                tip["Date"] = date_str
                tip["Stake"] = 1.0
                tips.append(tip)
    return tips

def main(date_str, mode, min_conf, send_to_telegram, show=False):
    date_display = date_str
    results_path = f"rpscrape/data/dates/all/{date_str.replace('-', '_')}.csv"
    if not os.path.exists(results_path):
        print(f"Missing results file: {results_path}")
        return

    results_df = pd.read_csv(results_path)
    results_df.rename(columns={
        "off": "Race Time",
        "course": "Course",
        "horse": "Horse",
        "num": "Runners",
        "pos": "Position",
        "race_name": "Race Name",
        "type": "Race Type",
        "class": "Class",
        "rating_band": "Rating Band"
    }, inplace=True)

    results_df["Horse"] = results_df["Horse"].apply(normalize_horse_name)
    results_df["Course"] = results_df["Course"].astype(str).str.strip().str.lower().str.replace(r"\s*\(ire\)", "", regex=True).str.strip()
    results_df["Race Time"] = results_df["Race Time"].astype(str).str.strip().str.lower()

    for source in ["sent", "all"]:
        use_sent = (source == "sent")
        tips = load_tips(date_str, min_conf, use_sent)
        if not tips:
            continue

        tips_df = pd.DataFrame(tips)
        tips_df["Horse"] = tips_df["Horse"].astype(str).str.strip().str.lower()
        tips_df["Course"] = tips_df["Course"].astype(str).str.strip().str.lower()
        tips_df["Race Time"] = tips_df["Race Time"].astype(str).str.strip().str.lower()

        merged_df = pd.merge(
            tips_df,
            results_df,
            how="left",
            left_on=["Horse", "Race Time", "Course"],
            right_on=["Horse", "Race Time", "Course"],
        )

        merged_df["Position"] = merged_df["Position"].fillna("NR")
        merged_df["Profit"] = merged_df.apply(lambda row: 0.0 if row["Position"] == "NR" else calculate_profit(row), axis=1)

        num_nrs = (merged_df["Position"] == "NR").sum()
        wins = (merged_df["Position"] == "1").sum()
        places = merged_df["Position"].apply(lambda x: str(x).isdigit() and 2 <= int(x) <= 4).sum()
        losses = len(merged_df) - wins - places - num_nrs

        summary = {
            "Date": date_display,
            "Tips": len(merged_df),
            "Wins": wins,
            "Places": places,
            "NRs": num_nrs,
            "Stake": merged_df["Stake"].sum(),
            "Profit": round(merged_df["Profit"].sum(), 2),
        }

        roi = (summary["Profit"] / summary["Stake"]) * 100 if summary["Stake"] > 0 else 0.0
        strike_rate = (wins / summary["Tips"] * 100) if summary["Tips"] > 0 else 0.0
        place_rate = (places / summary["Tips"] * 100) if summary["Tips"] > 0 else 0.0

        output_path = f"logs/tips_results_{date_str}_{mode}_{source}.csv"
        merged_df["Mode"] = mode
        merged_df.to_csv(output_path, index=False)
        print(f"✅ Saved: {output_path}")

        tag_output = f"logs/tag_roi_summary_{source}.csv"
        if "tags" in merged_df.columns:
            merged_df["tags"] = merged_df["tags"].apply(lambda x: x if isinstance(x, list) else [])
            all_rows = []
            for _, row in merged_df.iterrows():
                for tag in row["tags"]:
                    all_rows.append({"Tag": tag, "Profit": row["Profit"], "Position": row["Position"]})
            tag_df = pd.DataFrame(all_rows)
            if not tag_df.empty:
                tag_summary = tag_df.groupby("Tag").agg(
                    Tips=("Profit", "count"),
                    Profit=("Profit", "sum"),
                    Wins=("Position", lambda x: (x == "1").sum())
                )
                tag_summary["ROI %"] = (tag_summary["Profit"] / tag_summary["Tips"]) * 100
                tag_summary = tag_summary.reset_index()
                tag_summary.to_csv(tag_output, index=False)
                print(f"✅ Tag ROI saved to {tag_output}")

        if send_to_telegram:
            message = f"""📊 *Tipping Monster Daily ROI – {date_display} ({mode.capitalize()} – {source.upper()})*

🏇 Tips: {summary['Tips']}  |  🟢 {wins}W  |  🟡 {places}P  |  🔴 {losses}L
🎯 Strike Rate: {strike_rate:.2f}% | 🥈 Place Rate: {place_rate:.2f}%
💰 Profit: {summary['Profit']:+.2f} pts
📈 ROI: {roi:.2f}%
🪙 Staked: {summary['Stake']:.2f} pts"""
            send_telegram_message(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    parser.add_argument("--mode", choices=["advised", "level"], required=True)
    parser.add_argument("--min_conf", type=float, default=0.8)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--show", action="store_true", help="Show summary in CLI only")
    args = parser.parse_args()

    main(args.date, args.mode, args.min_conf, args.telegram, args.show)

