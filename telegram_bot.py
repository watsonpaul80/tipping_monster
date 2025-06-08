#!/usr/bin/env python3
"""Simple Telegram bot with /roi command."""

from __future__ import annotations

import os
from datetime import datetime
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
    await _reply(update, "Send /roi YYYY-MM-DD to get ROI summary.")


async def roi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /roi [DATE] command."""
    date = context.args[0] if context.args else datetime.today().strftime("%Y-%m-%d")
    message = get_roi_summary(date)
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
