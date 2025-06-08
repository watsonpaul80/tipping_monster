#!/usr/bin/env python3
"""Simple Telegram bot with /roi command."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from tippingmonster import repo_path


def get_roi_summary(date: str, base_dir: Path | None = None) -> str:
    """Return one-line ROI summary for ``date``."""
    base_dir = base_dir or repo_path()
    csv_path = base_dir / "logs" / "roi" / f"tips_results_{date}_advised.csv"
    if not csv_path.exists():
        return f"No ROI CSV found for {date}: {csv_path}"

    df = pd.read_csv(csv_path)
    df["Position"] = (
        pd.to_numeric(df["Position"], errors="coerce").fillna(0).astype(int)
    )
    profit = df["Profit"].sum()
    stake = df["Stake"].sum()
    roi = (profit / stake * 100) if stake else 0
    tips = len(df)
    return f"ROI {date}: {profit:+.2f} pts ({roi:.2f}%) from {tips} tips"


def get_weekly_roi_summary(
    date: str | None = None, base_dir: Path | None = None
) -> str:
    """Return ROI summary for the ISO week containing ``date`` or today."""
    base_dir = base_dir or repo_path()
    target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.today()
    iso_year, iso_week, _ = target.isocalendar()
    monday = datetime.strptime(f"{iso_year}-W{iso_week}-1", "%G-W%V-%u")
    week_dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    rows = []
    for ds in week_dates:
        csv_path = base_dir / "logs" / "roi" / f"tips_results_{ds}_advised.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            rows.append(df)

    if not rows:
        week_label = f"{iso_year}-W{iso_week:02d}"
        return f"No ROI data for week {week_label}"

    df = pd.concat(rows, ignore_index=True)
    df["Position"] = (
        pd.to_numeric(df["Position"], errors="coerce").fillna(0).astype(int)
    )
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df["Stake"], errors="coerce").fillna(0)

    tips = len(df)
    wins = (df["Position"] == 1).sum()
    places = df["Position"].apply(lambda x: 2 <= x <= 4).sum()
    profit = df["Profit"].sum()
    stake = df["Stake"].sum()
    roi = (profit / stake * 100) if stake else 0
    week_label = f"{iso_year}-W{iso_week:02d}"
    return (
        f"Week {week_label}: {profit:+.2f} pts profit "
        f"({roi:.2f}% ROI) from {tips} tips ({wins}W/{places}P)"
    )


async def _reply(update: Update, message: str) -> None:
    """Send or log ``message`` based on dev mode."""
    if os.getenv("TM_DEV_MODE") == "1":
        log = repo_path("logs", "dev", "telegram.log")
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        print(f"[DEV] Telegram message suppressed: {message}")
    else:
        await update.message.reply_text(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await _reply(update, "Send /roi to get this week's ROI summary.")


async def roi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /roi [DATE] command."""
    date = context.args[0] if context.args else None
    message = get_weekly_roi_summary(date)
    await _reply(update, message)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN must be set")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roi", roi))
    application.run_polling()


if __name__ == "__main__":
    main()
