#!/usr/bin/env python3
"""Summarise win rate and ROI by tag across all tips."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List

import pandas as pd

from tippingmonster import calculate_profit


def normalize_horse_name(name: str) -> str:
    """Return a lowercased horse name without parenthetical notes."""
    return re.sub(r"\s*\(.*?\)", "", str(name)).strip().lower()


def load_results(path: Path) -> pd.DataFrame:
    """Load race results CSV from ``path`` with normalised columns."""
    df = pd.read_csv(path)
    df.rename(
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
    df["Horse"] = df["Horse"].apply(normalize_horse_name)
    df["Course"] = (
        df["Course"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s*\(ire\)", "", regex=True)
        .str.strip()
    )
    df["Race Time"] = df["Race Time"].astype(str).str.strip().str.lower()
    return df


def load_tips(path: Path, date_str: str, min_conf: float) -> pd.DataFrame:
    """Load tips JSONL and return a DataFrame."""
    tips: List[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tip = json.loads(line)
            if tip.get("confidence", 0.0) < min_conf:
                continue
            tip["Race Time"] = tip.get("race", "??:??").split()[0]
            tip["Course"] = " ".join(tip.get("race", "??").split()[1:])
            tip["Horse"] = normalize_horse_name(tip.get("name", ""))
            tip["Odds"] = tip.get(
                "realistic_odds", tip.get("bf_sp", tip.get("odds", 0.0))
            )
            tip["Date"] = date_str
            tip["Stake"] = 1.0
            tips.append(tip)
    return pd.DataFrame(tips)


def merge_tips_results(tips_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
    """Return ``tips_df`` merged with ``results_df`` and profit calculated."""
    tips_df = tips_df.copy()
    tips_df["Horse"] = tips_df["Horse"].astype(str).str.strip().str.lower()
    tips_df["Course"] = tips_df["Course"].astype(str).str.strip().str.lower()
    tips_df["Race Time"] = tips_df["Race Time"].astype(str).str.strip().str.lower()

    merged = pd.merge(
        tips_df,
        results_df,
        how="left",
        left_on=["Horse", "Race Time", "Course"],
        right_on=["Horse", "Race Time", "Course"],
    )
    merged["Position"] = merged["Position"].fillna("NR")
    merged["Profit"] = merged.apply(
        lambda r: 0.0 if r["Position"] == "NR" else calculate_profit(r), axis=1
    )
    return merged


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """Return time-decayed win rate and ROI per tag."""
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    now = df["Date"].max()

    def _weight(date: pd.Timestamp) -> float:
        days = (now - date).days
        if days <= 30:
            return 1.0
        if days <= 90:
            return 0.5
        return 0.1

    df["Weight"] = df["Date"].apply(_weight)

    rows = []
    for _, row in df.iterrows():
        for tag in row.get("tags", []) or []:
            rows.append(
                {
                    "Tag": tag,
                    "Profit": row["Profit"],
                    "Position": row["Position"],
                    "Weight": row["Weight"],
                }
            )

    tag_df = pd.DataFrame(rows)
    if tag_df.empty:
        return pd.DataFrame()

    tag_df["Win"] = (tag_df["Position"].astype(str) == "1").astype(float)
    tag_df["WeightedTips"] = tag_df["Weight"]
    tag_df["WeightedWins"] = tag_df["Win"] * tag_df["Weight"]
    tag_df["WeightedProfit"] = tag_df["Profit"] * tag_df["Weight"]

    summary = tag_df.groupby("Tag").agg(
        Tips=("WeightedTips", "sum"),
        Wins=("WeightedWins", "sum"),
        Profit=("WeightedProfit", "sum"),
    )
    summary["Win %"] = (summary["Wins"] / summary["Tips"] * 100).round(2)
    summary["ROI %"] = (summary["Profit"] / summary["Tips"] * 100).round(2)
    return summary.sort_values("ROI %", ascending=False)


def compute_summary(
    pred_dir: str, results_dir: str, min_conf: float = 0.8
) -> pd.DataFrame:
    """Aggregate ROI by tag across all dates."""
    pred_root = Path(pred_dir)
    result_root = Path(results_dir)
    merged_rows = []
    for tips_path in sorted(pred_root.glob("*/tips_with_odds.jsonl")):
        date_str = tips_path.parent.name
        result_path = result_root / f"{date_str.replace('-', '_')}.csv"
        if not result_path.exists():
            continue
        tips_df = load_tips(tips_path, date_str, min_conf)
        results_df = load_results(result_path)
        merged_rows.append(merge_tips_results(tips_df, results_df))

    if not merged_rows:
        return pd.DataFrame()
    full_df = pd.concat(merged_rows, ignore_index=True)
    return summarise(full_df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute win rate and ROI per tag.")
    parser.add_argument(
        "--pred_dir", default="predictions", help="Prediction directory root"
    )
    parser.add_argument(
        "--results_dir", default="rpscrape/data/dates/all", help="Results CSV directory"
    )
    parser.add_argument(
        "--min_conf", type=float, default=0.8, help="Minimum confidence to include"
    )
    args = parser.parse_args()

    summary = compute_summary(args.pred_dir, args.results_dir, args.min_conf)
    if summary.empty:
        print("No tips or results found.")
        return
    print(summary.to_string(float_format=lambda x: f"{x:.2f}"))


if __name__ == "__main__":
    main()
