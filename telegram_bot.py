#!/usr/bin/env python3
"""Simple Telegram bot with /roi and /nap commands."""

from __future__ import annotations

import json
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


def get_recent_naps(days: int = 7, base_dir: Path | None = None) -> str:
    """Return last ``days`` NAPs with win/place/ROI summary."""
    base_dir = base_dir or repo_path()

    pred_root = base_dir / "predictions"
    if not pred_root.exists():
        return "No predictions directory found."

    date_dirs = sorted([d for d in pred_root.iterdir() if d.is_dir()], reverse=True)

    naps: list[dict[str, object]] = []
    for d in date_dirs:
        if len(naps) >= days:
            break
        pred_file = d / "tips_with_odds.jsonl"
        if not pred_file.exists():
            continue
        nap_tip = None
        with open(pred_file, "r", encoding="utf-8") as f:
            for line in f:
                tip = json.loads(line)
                tags = tip.get("tags", [])
                if any("NAP" in t for t in tags):
                    nap_tip = tip
                    break
        if not nap_tip:
            continue

        date_str = d.name
        results_csv = base_dir / "logs" / f"tips_results_{date_str}_advised.csv"
        if not results_csv.exists():
            continue
        df = pd.read_csv(results_csv)
        df["Horse"] = df["Horse"].str.lower()
        match = df[df["Horse"] == nap_tip["name"].lower()]
        if match.empty:
            continue
        row = match.iloc[0]
        naps.append(
            {
                "date": date_str,
                "horse": nap_tip["name"],
                "position": int(row["Position"]),
                "profit": float(row["Profit"]),
                "stake": float(row.get("Stake", 1.0)),
            }
        )

    if not naps:
        return "No NAP history found."

    naps = naps[:days][::-1]  # chronological order

    wins = sum(1 for n in naps if n["position"] == 1)
    places = sum(1 for n in naps if 0 < n["position"] <= 3)
    total_profit = sum(n["profit"] for n in naps)
    total_stake = sum(n["stake"] for n in naps)
    roi = (total_profit / total_stake * 100) if total_stake else 0.0

    lines = [
        f"{n['date']}: {n['horse']} - Pos {n['position']} ({n['profit']:+.2f} pts)"
        for n in naps
    ]
    lines.append(f"🏆 {wins}/{len(naps)} won, {places} placed")
    lines.append(f"💰 Profit: {total_profit:+.2f} pts")
    lines.append(f"📈 ROI: {roi:.2f}%")
    return "\n".join(lines)


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


async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /nap command."""
    try:
        days = int(context.args[0]) if context.args else 7
    except ValueError:
        days = 7
    message = get_recent_naps(days)
    await _reply(update, message)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN must be set")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roi", roi))
    application.add_handler(CommandHandler("nap", nap))
    application.run_polling()


if __name__ == "__main__":
    main()
