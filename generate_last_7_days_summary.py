#!/usr/bin/env python3
import os
from datetime import date, timedelta
from glob import glob
import argparse
import requests

import pandas as pd
from dotenv import load_dotenv

MODE = "advised"
DAYS = 7

SEARCH_DIRS = ["logs/roi", "logs"]


def send_to_telegram(message: str, token: str, chat_id: str) -> None:
    """Send a Markdown-formatted message to Telegram."""
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
    )


def find_csv_files():
    files = []
    for d in SEARCH_DIRS:
        if os.path.isdir(d):
            pattern = os.path.join(d, f"tips_results_*_{MODE}.csv")
            files.extend(glob(pattern))
    return sorted(files)


def parse_date_from_filename(path):
    name = os.path.basename(path)
    parts = name.split("_")
    if len(parts) >= 3:
        return parts[2]
    return None


def load_recent_data():
    all_files = find_csv_files()
    if not all_files:
        return []
    today = date.today()
    start_date = today - timedelta(days=DAYS - 1)
    recent_rows = []
    for f in all_files:
        date_str = parse_date_from_filename(f)
        if not date_str:
            continue
        try:
            file_date = date.fromisoformat(date_str)
        except ValueError:
            continue
        if start_date <= file_date <= today:
            df = pd.read_csv(f)
            df["Date"] = date_str
            recent_rows.append(df)
    return recent_rows


def compute_stats(df):
    df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
    wins = df["Position"].eq(1).sum()
    places = df["Position"].between(2, 4).sum()
    tips = len(df)
    stake = pd.to_numeric(df.get("Stake", 0), errors="coerce").fillna(0).sum()
    profit = pd.to_numeric(df.get("Profit", 0), errors="coerce").fillna(0).sum()
    roi = (profit / stake * 100) if stake else 0
    return {
        "tips": tips,
        "wins": int(wins),
        "places": int(places),
        "stake": float(stake),
        "profit": float(profit),
        "roi": float(roi),
    }


def main(send_telegram=False):
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    data_frames = load_recent_data()
    if not data_frames:
        print("No ROI CSV files found for the last 7 days.")
        return

    daily_summary = []
    for df in data_frames:
        date_str = df["Date"].iloc[0]
        stats = compute_stats(df)
        daily_summary.append((date_str, stats))

    # Sort by date
    daily_summary.sort(key=lambda x: x[0])

    totals = {
        "tips": sum(r[1]["tips"] for r in daily_summary),
        "wins": sum(r[1]["wins"] for r in daily_summary),
        "places": sum(r[1]["places"] for r in daily_summary),
        "stake": sum(r[1]["stake"] for r in daily_summary),
        "profit": sum(r[1]["profit"] for r in daily_summary),
    }
    totals["roi"] = (totals["profit"] / totals["stake"] * 100) if totals["stake"] else 0
    totals["strike_rate"] = (totals["wins"] / totals["tips"] * 100) if totals["tips"] else 0
    totals["place_rate"] = (totals["places"] / totals["tips"] * 100) if totals["tips"] else 0

    md_lines = ["# 🧠 Tipping Monster – Last 7 Days ROI\n"]
    md_lines.append("| Date | Tips | 🟢 Wins | 🟡 Places | Profit | ROI |")
    md_lines.append("|------|-----:|-------:|---------:|-------:|----:|")

    for date_str, stats in daily_summary:
        md_lines.append(
            f"| {date_str} | {stats['tips']} | {stats['wins']} | {stats['places']} | {stats['profit']:+.2f} | {stats['roi']:.2f}% |"
        )

    md_lines.append(
        f"| **Total** | {totals['tips']} | {totals['wins']} | {totals['places']} | {totals['profit']:+.2f} | {totals['roi']:.2f}% |")
    md_lines.append("")
    md_lines.append(
        f"🏇 **Tips:** {totals['tips']}  |  🟢 {totals['wins']}W  |  🟡 {totals['places']}P  |  🔴 {totals['tips'] - totals['wins'] - totals['places']}L"
    )
    md_lines.append(
        f"🎯 **Strike Rate:** {totals['strike_rate']:.2f}%  |  🥈 **Place Rate:** {totals['place_rate']:.2f}%"
    )
    md_lines.append(f"💰 **Profit:** {totals['profit']:+.2f} pts")
    md_lines.append(f"📈 **ROI:** {totals['roi']:.2f}%")
    md_lines.append(f"🪙 **Staked:** {totals['stake']:.2f} pts")

    # Save to repository root so it's not ignored by .gitignore
    out_path = "last_7_days_roi_summary.md"
    with open(out_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"✅ Saved summary to {out_path}")

    if send_telegram and token and chat_id:
        send_to_telegram("\n".join(md_lines), token, chat_id)
        print("✅ Sent summary to Telegram")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--telegram", action="store_true", help="Send summary to Telegram")
    args = parser.parse_args()
    main(send_telegram=args.telegram)
