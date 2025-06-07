#!/usr/bin/env python3
"""Aggregate ROI by confidence band."""

from __future__ import annotations

import argparse
import os
from glob import glob

import pandas as pd
from dotenv import load_dotenv

from tippingmonster import send_telegram_message
from tippingmonster.env_loader import load_env

load_dotenv()
load_env()

BANDS = [(0.80, 0.85, "0.80–0.85"), (0.85, 0.90, "0.85–0.90"), (0.90, 1.01, "0.90+")]


def assign_band(conf: float) -> str | None:
    """Return the band label for ``conf`` or ``None`` if below 0.80."""
    if pd.isna(conf):
        return None
    for low, high, label in BANDS:
        if low <= conf < high:
            return label
    return None


def load_roi_rows(pattern: str) -> pd.DataFrame:
    """Load all ROI CSVs matching ``pattern`` into one DataFrame."""
    files = sorted(glob(pattern))
    rows = []
    for path in files:
        try:
            df = pd.read_csv(path)
            rows.append(df)
        except Exception:
            continue
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Confidence"] = pd.to_numeric(df.get("Confidence"), errors="coerce")
    df["Profit"] = pd.to_numeric(df.get("Profit"), errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df.get("Stake"), errors="coerce").fillna(0)
    df["Position"] = df.get("Position").astype(str)
    df["Band"] = df["Confidence"].apply(assign_band)
    df = df.dropna(subset=["Band"])
    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby("Band")
        .apply(
            lambda g: pd.Series(
                {
                    "Tips": len(g),
                    "Wins": (g["Position"] == "1").sum(),
                    "Stake": g["Stake"].sum(),
                    "Profit": g["Profit"].sum(),
                }
            )
        )
        .reset_index()
    )
    summary["Win %"] = (summary["Wins"] / summary["Tips"] * 100).round(2)
    summary["ROI %"] = summary.apply(
        lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
    ).round(2)
    return summary.sort_values("Band")


def send_summary(summary: pd.DataFrame, source: str) -> None:
    msg_lines = [f"*ROI by Confidence Band ({source})*"]
    for _, row in summary.iterrows():
        msg_lines.append(
            f"{row['Band']} → {int(row['Tips'])} tips, {row['Win %']:.1f}% win, {row['ROI %']:.1f}% ROI"
        )
    send_telegram_message("\n".join(msg_lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        choices=["sent", "all"],
        default="sent",
        help="Which ROI CSVs to use",
    )
    parser.add_argument(
        "--telegram", action="store_true", help="Send summary to Telegram"
    )
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    pattern = f"logs/tips_results_*_advised_{args.source}.csv"
    df = load_roi_rows(pattern)
    if df.empty:
        print(f"No ROI data found for pattern: {pattern}")
        return

    summary = summarise(df)
    output_path = f"logs/roi/roi_by_confidence_band_{args.source}.csv"
    summary.to_csv(output_path, index=False)
    print(f"✅ Saved summary to {output_path}")

    if args.telegram:
        send_summary(summary, args.source)


if __name__ == "__main__":
    main()
