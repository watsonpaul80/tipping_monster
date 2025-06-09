#!/usr/bin/env python3
"""Simulate different staking profiles over historical results."""

from __future__ import annotations

import argparse
from glob import glob
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from tippingmonster import calculate_profit


def load_results(files: Iterable[str]) -> pd.DataFrame:
    rows = []
    for path in files:
        try:
            df = pd.read_csv(path)
            rows.append(df)
        except Exception:
            continue
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def base_profit(row: pd.Series) -> float:
    temp = {
        "Odds": float(row["Odds"]),
        "Position": row["Position"],
        "Stake": 1.0,
        "Runners": row.get("Runners", 0),
        "Race Name": row.get("Race Name", ""),
    }
    return float(calculate_profit(temp))


def simulate(df: pd.DataFrame) -> dict:
    level_profit = 0.0
    level_stake = 0.0
    conf_profit = 0.0
    conf_stake = 0.0
    value_profit = 0.0
    value_stake = 0.0

    level_curve = []
    conf_curve = []
    value_curve = []

    for _, row in df.iterrows():
        bp = base_profit(row)

        # Level stakes
        stake = 1.0
        level_profit += bp * stake
        level_stake += stake
        level_curve.append(level_profit)

        # Confidence-weighted: (conf% - 70) / 10
        stake = max((float(row["Confidence"]) * 100 - 70) / 10, 0.0)
        conf_profit += bp * stake
        conf_stake += stake
        conf_curve.append(conf_profit)

        # Value staking: (conf * odds) - 1
        stake = max(float(row["Confidence"]) * float(row["Odds"]) - 1, 0.0)
        value_profit += bp * stake
        value_stake += stake
        value_curve.append(value_profit)

    results = {
        "level": {"profit": level_profit, "stake": level_stake, "curve": level_curve},
        "confidence": {
            "profit": conf_profit,
            "stake": conf_stake,
            "curve": conf_curve,
        },
        "value": {"profit": value_profit, "stake": value_stake, "curve": value_curve},
    }
    return results


def plot_curves(results: dict, out_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    for key, data in results.items():
        plt.plot(data["curve"], label=key.title())
    plt.xlabel("Bets")
    plt.ylabel("Profit (pts)")
    plt.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main(pattern: str, out: Path) -> None:
    files = sorted(glob(pattern))
    if not files:
        print(f"No files found for pattern: {pattern}")
        return

    df = load_results(files)
    if df.empty:
        print("No data to process")
        return

    results = simulate(df)
    for name, data in results.items():
        roi = (data["profit"] / data["stake"] * 100) if data["stake"] else 0.0
        print(f"{name.title():12s} Profit: {data['profit']:+.2f} ROI: {roi:.2f}%")

    plot_curves(results, out)
    print(f"✅ Saved plot to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate staking strategies")
    parser.add_argument(
        "--pattern",
        default="logs/tips_results_*_advised_sent.csv",
        help="Glob pattern for ROI CSVs",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("logs/roi/staking_simulation.png"),
        help="Output chart path",
    )
    args = parser.parse_args()
    main(args.pattern, args.out)
