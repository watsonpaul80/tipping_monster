#!/usr/bin/env python3
"""Compute recent win rate and ROI per trainer."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path("rpscrape/data/dates/all")


def _parse_date_from_filename(path: Path) -> datetime | None:
    try:
        return datetime.strptime(path.stem, "%Y_%m_%d")
    except ValueError:
        return None


def load_recent_results(
    results_dir: Path, ref_date: str, days: int = 30
) -> pd.DataFrame:
    """Return DataFrame of results within ``days`` up to ``ref_date``."""
    ref = datetime.strptime(ref_date, "%Y-%m-%d")
    start = ref - timedelta(days=days)
    frames = []
    for path in results_dir.glob("*.csv"):
        d = _parse_date_from_filename(path)
        if not d or not (start <= d <= ref):
            continue
        try:
            df = pd.read_csv(path)
            frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def compute_trainer_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return runs, wins, win rate and ROI per trainer from ``df``."""
    if df.empty:
        return pd.DataFrame(columns=["Trainer", "Runs", "Wins", "Win %", "ROI %"])
    df["Position"] = df["Position"].astype(str).str.lower()
    df["Win"] = df["Position"].apply(lambda x: str(x) == "1")
    df["BFSP"] = pd.to_numeric(df.get("BFSP"), errors="coerce")

    def profit(row):
        if row["Win"]:
            return row.get("BFSP", 0.0) - 1
        return -1.0

    df["Profit"] = df.apply(profit, axis=1)
    summary = df.groupby("Trainer").agg(
        Runs=("Win", "count"),
        Wins=("Win", "sum"),
        Profit=("Profit", "sum"),
    )
    summary["Win %"] = (summary["Wins"] / summary["Runs"] * 100).round(2)
    summary["ROI %"] = (summary["Profit"] / summary["Runs"] * 100).round(2)
    return summary.reset_index()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute 30-day trainer stats")
    parser.add_argument(
        "--results_dir", default=str(RESULTS_DIR), help="Results directory"
    )
    parser.add_argument("--date", default=datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument(
        "--window", type=int, default=30, help="Lookback window in days"
    )
    args = parser.parse_args()

    df = load_recent_results(Path(args.results_dir), args.date, args.window)
    stats = compute_trainer_stats(df)
    if stats.empty:
        print("No results found for window")
        return
    print(stats.to_csv(index=False))


if __name__ == "__main__":
    main()
