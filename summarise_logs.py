#!/usr/bin/env python3
"""Summarise log status for recent days."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from tippingmonster.utils import logs_path


def parse_results(path: Path) -> tuple[int, int, int]:
    """Return tips, wins and places from a results CSV."""
    df = pd.read_csv(path)
    pos = pd.to_numeric(df.get("Position"), errors="coerce").fillna(0)
    wins = int((pos == 1).sum())
    places = int(((2 <= pos) & (pos <= 4)).sum())
    return len(df), wins, places


def summarise_day(date_str: str, base_dir: Path | None = None) -> str:
    base = base_dir or logs_path()
    tips_file = base / f"sent_tips_{date_str}.jsonl"
    if not tips_file.exists():
        return f"{date_str} ⚠️ Missing tips file"

    results_file = base / f"tips_results_{date_str}_advised.csv"
    roi_file = base / f"roi_{date_str}.log"

    parts = [f"{date_str} ✅"]
    if results_file.exists():
        try:
            tips, wins, places = parse_results(results_file)
            parts.append(f"{tips} tips | {wins}W {places}P")
        except Exception:
            parts.append("results unreadable")
    else:
        parts.append("results ❌")

    parts.append(f"ROI log {'✅' if roi_file.exists() else '❌'}")
    return " | ".join(parts)


def summarise_logs(days: int = 7, base_dir: Path | None = None) -> list[str]:
    today = datetime.now().date()
    lines = []
    for i in range(days):
        d = today - timedelta(days=i)
        lines.append(summarise_day(d.strftime("%Y-%m-%d"), base_dir))
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise recent logs")
    parser.add_argument("--days", type=int, default=7, help="Number of days")
    args = parser.parse_args()

    for line in summarise_logs(args.days):
        print(line)


if __name__ == "__main__":
    main()
