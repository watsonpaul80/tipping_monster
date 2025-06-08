#!/usr/bin/env python3
"""Track ROI for laying Danger Fav candidates at BSP."""
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import List

import pandas as pd

from tippingmonster.utils import send_telegram_message

DEF_RESULTS_DIR = Path("rpscrape/data/dates/all")


def load_danger_favs(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    rows = [pd.read_json(path, lines=True)] if path.suffix == ".json" else None
    if rows:
        return rows[0]
    return pd.read_json(path, lines=True)


def load_results(date_str: str) -> pd.DataFrame:
    csv_path = DEF_RESULTS_DIR / f"{date_str.replace('-', '_')}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    df = pd.read_csv(csv_path)
    df.rename(
        columns={
            "off": "Race Time",
            "course": "Course",
            "horse": "Horse",
            "pos": "Position",
        },
        inplace=True,
    )
    df["Horse"] = df["Horse"].astype(str).str.strip().str.lower()
    df["Course"] = df["Course"].astype(str).str.strip().str.lower()
    df["Race Time"] = df["Race Time"].astype(str).str.strip().str.lower()
    return df


def normalize_race(row: pd.Series) -> tuple:
    time, course = str(row["race"]).split(" ", 1)
    return course.strip().lower(), time.lstrip("0")


def merge_results(cands: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    cands = cands.copy()
    cands[["Course", "Race Time"]] = cands.apply(
        normalize_race, axis=1, result_type="expand"
    )
    cands["Horse"] = cands["name"].str.lower().str.strip()

    merged = pd.merge(
        cands,
        results,
        how="left",
        left_on=["Horse", "Race Time", "Course"],
        right_on=["Horse", "Race Time", "Course"],
    )
    merged["Position"] = merged["Position"].fillna("NR")
    return merged


def lay_profit(position: str, price: float) -> float:
    if str(position) == "1":
        return -(price - 1)
    return 1.0


def summarise(df: pd.DataFrame) -> dict:
    df["LayProfit"] = df.apply(
        lambda r: lay_profit(r["Position"], float(r["bf_sp"])), axis=1
    )
    bets = len(df)
    wins = (df["Position"] == "1").sum()
    profit = df["LayProfit"].sum()
    roi = profit / bets * 100 if bets else 0.0
    win_pct = wins / bets * 100 if bets else 0.0
    return {
        "bets": bets,
        "wins": wins,
        "profit": profit,
        "roi": roi,
        "win_pct": win_pct,
    }


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Track Danger Fav lay ROI")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    cand_path = Path(f"predictions/{args.date}/danger_favs.jsonl")
    cands = load_danger_favs(cand_path)
    results = load_results(args.date)
    merged = merge_results(cands, results)
    summary = summarise(merged)

    msg = (
        f"⚠️ Danger Fav ROI {args.date}\n"
        f"Bets: {summary['bets']} | Winners: {summary['wins']}\n"
        f"Profit(Lay): {summary['profit']:+.2f} pts | ROI: {summary['roi']:.2f}%"
    )

    print(msg)
    if args.telegram:
        send_telegram_message(msg)


if __name__ == "__main__":
    main()
