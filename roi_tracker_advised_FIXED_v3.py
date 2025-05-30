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

def main(date_str, mode, min_conf, send_to_telegram, use_sent):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    date_display = date_obj.strftime("%Y-%m-%d")

    if use_sent:
        input_file = f"logs/sent_tips_{date_str}.jsonl"
    else:
        input_file = f"predictions/{date_str}/tips_with_odds.jsonl"

    results_path = f"rpscrape/data/dates/all/{date_str.replace('-', '_')}.csv"

    if not os.path.exists(input_file):
        print(f"Missing tips file: {input_file}")
        return

    if not os.path.exists(results_path):
        print(f"Missing results file: {results_path}")
        return

    tips = []
    with open(input_file, "r") as f:
        for line in f:
            tip = json.loads(line)
            if tip.get("confidence", 0.0) >= min_conf:
                tip["Race Time"] = tip.get("race", "??:?? Unknown").split()[0]
                tip["Course"] = " ".join(tip.get("race", "??:?? Unknown").split()[1:])
                tip["Horse"] = normalize_horse_name(tip.get("name", "Unknown"))
                tip["Confidence"] = tip.get("confidence", 0.0)
                tip["Odds"] = tip.get("bf_sp", tip.get("odds", 0.0))
                tip["Date"] = date_display
                tip["Mode"] = mode
                tip["Stake"] = 1.0
                tips.append(tip)

    if not tips:
        print(f"{date_display}   Tips: 0    Wins: 0   Places: 0   Stake: 0.00 Profit: 0.00 ROI: 0.00%")
        return

    tips_df = pd.DataFrame(tips)

    try:
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

    except Exception as e:
        print(f"Error reading results CSV: {e}")
        return

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

    summary = {
        "Date": date_display,
        "Tips": len(merged_df),
        "Wins": (merged_df["Position"] == "1").sum(),
        "Places": merged_df["Position"].apply(lambda x: str(x).isdigit() and 2 <= int(x) <= 4).sum(),
        "NRs": num_nrs,
        "Stake": merged_df["Stake"].sum(),
        "Profit": round(merged_df["Profit"].sum(), 2),
    }

    roi = (summary["Profit"] / summary["Stake"]) * 100 if summary["Stake"] > 0 else 0.0
    result_line = (
        f"{summary['Date']}   Tips: {summary['Tips']}    Wins: {summary['Wins']}   "
        f"Places: {summary['Places']}   NRs: {summary['NRs']}   Stake: {summary['Stake']:.2f} "
        f"Profit: {summary['Profit']:.2f} ROI: {roi:.2f}%"
    )
    print(result_line)

    output_path = f"logs/tips_results_{date_str}_{mode}.csv"
    merged_df[["Date", "Race Time", "Course", "Horse", "Odds", "Confidence", "Position", "Mode", "Stake", "Profit"]].to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path}")

    if send_to_telegram:
        message = (
            f"📊 *{date_display} ROI Summary*\n"
            f"🏇 *Tips:* {summary['Tips']} | 🥇 *Winners:* {summary['Wins']} | 🥈 *Places:* {summary['Places']}"
        )
        if summary["NRs"] > 0:
            message += f" | 🚫 *NRs:* {summary['NRs']}"
        message += (
            f"\n💸 *Stake:* {summary['Stake']} pts | *Profit:* {summary['Profit']} pts\n"
            f"📈 *ROI:* {roi:.2f}%"
        )
        send_telegram_message(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    parser.add_argument("--mode", choices=["advised", "level"], required=True)
    parser.add_argument("--min_conf", type=float, default=0.8)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--use_sent", action="store_true", help="Use sent tips file instead of predictions")
    args = parser.parse_args()

    main(args.date, args.mode, args.min_conf, args.telegram, args.use_sent)

