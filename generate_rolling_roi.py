#!/usr/bin/env python3
"""Compute a rolling 30-day ROI for sent tips.

Scans ``logs/`` for either ``tips_results_YYYY-MM-DD_advised_sent.csv`` or
``sent_tips_YYYY-MM-DD.jsonl`` and outputs a CSV with daily profit, stake, and
rolling totals to ``logs/roi/rolling_roi.csv``.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from tippingmonster import calculate_profit, logs_path, repo_path


def normalize_horse_name(name: str) -> str:
    return str(name).split("(")[0].strip().lower()


def parse_sent_csv(path: Path) -> tuple[float, float]:
    df = pd.read_csv(path)
    df["Profit"] = pd.to_numeric(df.get("Profit"), errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df.get("Stake"), errors="coerce").fillna(0)
    return float(df["Profit"].sum()), float(df["Stake"].sum())


def parse_sent_jsonl(date: str) -> tuple[float, float] | None:
    tips_file = logs_path(f"sent_tips_{date}.jsonl")
    if not os.path.exists(tips_file):
        return None

    results_file = repo_path(
        "rpscrape", "data", "dates", "all", f"{date.replace('-', '_')}.csv"
    )
    if not os.path.exists(results_file):
        print(f"Missing results for {date}: {results_file}")
        return None

    tips = []
    with open(tips_file, "r", encoding="utf-8") as f:
        for line in f:
            tip = json.loads(line)
            race = str(tip.get("race", ""))
            parts = race.split()
            time = parts[0] if parts else ""
            course = " ".join(parts[1:]) if len(parts) > 1 else ""
            tips.append(
                {
                    "Horse": normalize_horse_name(tip.get("name", "")),
                    "Race Time": time.lower(),
                    "Course": course.lower(),
                    "Odds": tip.get(
                        "realistic_odds", tip.get("bf_sp", tip.get("odds", 0.0))
                    ),
                    "Stake": 1.0,
                }
            )

    tips_df = pd.DataFrame(tips)

    res_df = pd.read_csv(results_file)
    res_df.rename(
        columns={
            "off": "Race Time",
            "course": "Course",
            "horse": "Horse",
            "num": "Runners",
            "pos": "Position",
            "race_name": "Race Name",
            "type": "Race Type",
            "class": "Class",
            "rating_band": "Rating Band",
        },
        inplace=True,
    )
    res_df["Horse"] = res_df["Horse"].apply(normalize_horse_name)
    res_df["Course"] = (
        res_df["Course"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s*\(ire\)", "", regex=True)
    )
    res_df["Race Time"] = res_df["Race Time"].astype(str).str.strip().str.lower()

    tips_df["Course"] = tips_df["Course"].astype(str).str.strip().str.lower()
    tips_df["Race Time"] = tips_df["Race Time"].astype(str).str.strip().str.lower()

    merged = pd.merge(
        tips_df,
        res_df,
        how="left",
        on=["Horse", "Race Time", "Course"],
    )
    merged["Position"] = merged["Position"].fillna("NR")
    merged["Profit"] = merged.apply(
        lambda row: 0.0 if row["Position"] == "NR" else calculate_profit(row), axis=1
    )
    return float(merged["Profit"].sum()), float(merged["Stake"].sum())


def collect_daily_results(days: int) -> pd.DataFrame:
    today = datetime.utcnow().date()
    rows = []
    for i in range(days):
        d = today - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        csv_path = logs_path(f"tips_results_{date_str}_advised_sent.csv")
        profit: float | None = None
        stake: float | None = None
        if os.path.exists(csv_path):
            try:
                profit, stake = parse_sent_csv(csv_path)
            except Exception as exc:
                print(f"Error reading {csv_path}: {exc}")
        if profit is None:
            result = parse_sent_jsonl(date_str)
            if result:
                profit, stake = result
        if profit is None:
            continue
        roi = (profit / stake * 100) if stake else 0.0
        rows.append({"Date": date_str, "Profit": profit, "Stake": stake, "ROI": roi})

    df = pd.DataFrame(sorted(rows, key=lambda r: r["Date"]))
    if df.empty:
        return df

    df["RollingProfit"] = df["Profit"].rolling(window=30, min_periods=1).sum()
    df["RollingStake"] = df["Stake"].rolling(window=30, min_periods=1).sum()
    df["RollingROI"] = df.apply(
        lambda r: (r.RollingProfit / r.RollingStake * 100) if r.RollingStake else 0.0,
        axis=1,
    )
    return df


def main(days: int) -> None:
    df = collect_daily_results(days)
    if df.empty:
        print("No ROI data found for the given period")
        return
    out_path = logs_path("roi", "rolling_roi.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Saved {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--days", type=int, default=30, help="Number of days to include"
    )
    args = parser.parse_args()
    main(args.days)
