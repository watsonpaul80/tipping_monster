#!/usr/bin/env python3
"""Send a daily ROI summary to Telegram."""

import argparse
import os
import sys
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

from tippingmonster import send_telegram_message

load_dotenv()


def send_daily_roi(date: Optional[str] = None, *, dev: bool = False) -> None:
    """Load the ROI CSV for ``date`` and send a Telegram summary."""

    if dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    mode = "advised"
    date = date or datetime.today().strftime("%Y-%m-%d")
    csv_path = f"logs/roi/tips_results_{date}_{mode}.csv"

    if not os.path.exists(csv_path):
        print(f"No ROI CSV found for {date}: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    df["Position"] = (
        pd.to_numeric(df["Position"], errors="coerce").fillna(0).astype(int)
    )

    tips = len(df)
    wins = (df["Position"] == 1).sum()
    places = df["Position"].apply(lambda x: 2 <= x <= 4).sum()
    profit = df["Profit"].sum()
    stake = df["Stake"].sum()
    roi = (profit / stake * 100) if stake else 0

    msg = (
        f"*📊 Tipping Monster Daily ROI – {date} ({mode.capitalize()})*\n\n"
        f"🏇 *Tips:* {tips}  |  🥇 *Winners:* {wins}  |  🥈 *Places:* {places}\n"
        f"💰 *Profit:* {profit:+.2f} pts\n"
        f"📈 *ROI:* {roi:.2f}%\n"
        f"🪙 *Staked:* {stake:.2f} pts"
    )

    try:
        send_telegram_message(msg, token=token, chat_id=chat_id)
        print(f"✅ Sent ROI summary to Telegram: {date}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")


def main(argv: Optional[list[str]] = None) -> None:
    """CLI entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date", type=str, help="Date in YYYY-MM-DD format", default=None
    )
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args(argv)

    send_daily_roi(date=args.date, dev=args.dev)


if __name__ == "__main__":
    main()
