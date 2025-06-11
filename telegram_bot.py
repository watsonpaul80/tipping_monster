#!/usr/bin/env python3
"""Simple Telegram bot with /roi, /nap, /tip, /ping and /help commands."""

from __future__ import annotations

import json
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


def get_tip_info(name: str, base_dir: Path | None = None) -> str:
    """Return the most recent tip info for ``name``."""
    base_dir = base_dir or repo_path()
    logs_dir = base_dir / "logs"
    files = sorted(logs_dir.glob("sent_tips_*.jsonl"), reverse=True)
    if not files:
        return "No sent tips logs found."

    target = name.lower()
    for fpath in files:
        date_str = fpath.stem.split("_")[-1]
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                tip = json.loads(line)
                if tip.get("name", "").lower() == target:
                    confidence = tip.get("confidence")
                    tags = ", ".join(tip.get("tags", []))
                    commentary = tip.get("commentary", "")
                    odds = tip.get("bf_sp")
                    parts = [f"{date_str}: {tip.get('race', '')}"]
                    if odds:
                        parts[0] += f" @ {odds}"
                    if confidence is not None:
                        parts.append(f"Confidence {confidence * 100:.1f}%")
                    if tags:
                        parts.append(f"Tags: {tags}")
                    if commentary:
                        parts.append(commentary)
                    return "\n".join(parts)
    return f"No recent tip found for {name}."


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
    await _reply(update, "Send /help to see available commands.")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple healthcheck command."""
    await _reply(update, "Monster is alive \U0001f9df")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List available commands."""
    commands = [
        "/roi [DATE]",
        "/nap [DAYS]",
        "/tip HORSE",
        "/ping",
    ]
    await _reply(update, "Available: " + ", ".join(commands))


async def roi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /roi [DATE] command."""
    date = context.args[0] if context.args else None
    message = get_weekly_roi_summary(date)
    await _reply(update, message)


async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /nap command."""
    try:
        days = int(context.args[0]) if context.args else 7
    except ValueError:
        days = 7
    try:
        message = get_recent_naps(days)
    except Exception as exc:
        message = f"Error generating NAP summary: {exc}"
    await _reply(update, message)


async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tip HORSE command."""
    if not context.args:
        await _reply(update, "Usage: /tip HORSE_NAME")
        return
    name = " ".join(context.args)
    message = get_tip_info(name)
    await _reply(update, message)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN must be set")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("roi", roi))
    application.add_handler(CommandHandler("nap", nap))
    application.add_handler(CommandHandler("tip", tip))
    application.run_polling()


if __name__ == "__main__":
    main()
