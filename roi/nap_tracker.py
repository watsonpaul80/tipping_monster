#!/usr/bin/env python3
"""Track NAP performance over time."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from tippingmonster import logs_path, send_telegram_message

HISTORY_FILE = logs_path("roi", "nap_history.csv")


def load_history(file_path: Path = HISTORY_FILE) -> pd.DataFrame:
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame(
        columns=["Date", "Tips", "Wins", "Profit", "Stake", "StrikeRate", "ROI"]
    )


def save_history(df: pd.DataFrame, file_path: Path = HISTORY_FILE) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)


def parse_tags(val: str) -> str:
    """Return lowercase tag string."""
    return str(val).lower()


def log_day(
    date_str: str,
    history_file: Path = HISTORY_FILE,
    csv_file: Path | None = None,
) -> dict | None:
    csv_file = csv_file or logs_path("roi", f"tips_results_{date_str}_advised.csv")
    if not os.path.exists(csv_file):
        print(f"Missing ROI CSV: {csv_file}")
        return None

    df = pd.read_csv(csv_file)
    if "tags" not in df.columns:
        print("CSV missing 'tags' column")
        return None

    df["tags"] = df["tags"].apply(parse_tags)
    nap_df = df[df["tags"].str.contains("nap", na=False)]
    if nap_df.empty:
        print(f"No NAP tips found for {date_str}")
        return None

    tips = len(nap_df)
    wins = (nap_df["Position"] == 1).sum()
    profit = nap_df["Profit"].sum()
    stake = nap_df["Stake"].sum()
    roi = profit / stake * 100 if stake else 0.0
    strike = wins / tips * 100 if tips else 0.0

    row = {
        "Date": date_str,
        "Tips": tips,
        "Wins": wins,
        "Profit": round(profit, 2),
        "Stake": round(stake, 2),
        "StrikeRate": round(strike, 2),
        "ROI": round(roi, 2),
    }

    history = load_history(history_file)
    if date_str in history.get("Date", []):
        history = history[history["Date"] != date_str]
    history = pd.concat([history, pd.DataFrame([row])], ignore_index=True)
    save_history(history, history_file)
    print(f"✅ Logged NAP results for {date_str}")
    return row


def summarise_history(history_file: Path = HISTORY_FILE) -> dict:
    df = load_history(history_file)
    if df.empty:
        return {}

    tips = df["Tips"].sum()
    wins = df["Wins"].sum()
    profit = df["Profit"].sum()
    stake = df["Stake"].sum()
    roi = profit / stake * 100 if stake else 0.0
    strike = wins / tips * 100 if tips else 0.0
    return {
        "Tips": int(tips),
        "Wins": int(wins),
        "Profit": round(profit, 2),
        "Stake": round(stake, 2),
        "StrikeRate": round(strike, 2),
        "ROI": round(roi, 2),
    }


def week_summary(week: str, history_file: Path = HISTORY_FILE) -> dict:
    year, wk = map(int, week.split("-W"))
    monday = datetime.strptime(f"{year}-W{wk}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    df = load_history(history_file)
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"] >= monday) & (df["Date"] <= sunday)
    week_df = df[mask]
    if week_df.empty:
        return {}

    tips = week_df["Tips"].sum()
    wins = week_df["Wins"].sum()
    profit = week_df["Profit"].sum()
    stake = week_df["Stake"].sum()
    roi = profit / stake * 100 if stake else 0.0
    strike = wins / tips * 100 if tips else 0.0
    return {
        "Week": week,
        "Tips": int(tips),
        "Wins": int(wins),
        "Profit": round(profit, 2),
        "Stake": round(stake, 2),
        "StrikeRate": round(strike, 2),
        "ROI": round(roi, 2),
    }


def send_weekly_summary(week: str) -> None:
    summary = week_summary(week)
    if not summary:
        print(f"No NAP data for week {week}")
        return

    msg = (
        f"*🧠 NAP Summary – {week}*\n\n"
        f"Tips: {summary['Tips']} | 🥇 {summary['Wins']}W\n"
        f"Strike Rate: {summary['StrikeRate']:.2f}%\n"
        f"Profit: {summary['Profit']:+.2f} pts\n"
        f"ROI: {summary['ROI']:.2f}%\n"
    )
    send_telegram_message(msg)
    print("✅ Sent Telegram summary")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Date in YYYY-MM-DD to log")
    parser.add_argument("--week", help="ISO week to summarise (YYYY-WW)")
    parser.add_argument("--telegram", action="store_true", help="Send Telegram summary")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    if args.date:
        log_day(args.date)
    if args.week and args.telegram:
        send_weekly_summary(args.week)
    elif args.week:
        summary = week_summary(args.week)
        if summary:
            print(summary)
        else:
            print(f"No NAP data for week {args.week}")
    if not args.date and not args.week:
        summary = summarise_history()
        if summary:
            print(summary)
        else:
            print("No NAP history found")


if __name__ == "__main__":
    main()
