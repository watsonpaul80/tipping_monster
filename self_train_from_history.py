#!/usr/bin/env python3
"""Aggregate past tip logs for self-training.

This script reads `logs/tips_results_*_advised_all.csv` files and
extracts columns needed for model fine-tuning:
`Confidence`, `Tags`, `Race Type`, `Result`, `Odds`, and `odds_delta`.
The output CSV is saved to `logs/roi/self_train_dataset.csv`.
"""

from __future__ import annotations

import ast
import glob
import os
from typing import List

import pandas as pd


def parse_tags(val: str | list | float | int | None) -> str:
    """Return a semicolon-separated string of tags."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if isinstance(val, list):
        return ";".join(map(str, val))
    if isinstance(val, str):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return ";".join(map(str, parsed))
        except Exception:
            pass
        return val
    return str(val)


def parse_result(pos: str | int | float) -> int:
    """Map finishing position to a binary result (1 = win)."""
    try:
        return 1 if int(pos) == 1 else 0
    except Exception:
        return 0


def load_files(paths: List[str]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for path in paths:
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            print(f"⚠️ Could not read {path}: {exc}")
            continue
        needed = [
            col
            for col in [
                "Confidence",
                "tags",
                "Race Type",
                "Position",
                "Odds",
                "odds_delta",
            ]
            if col in df.columns
        ]
        df = df[needed]
        df["Tags"] = df.get("tags").apply(parse_tags) if "tags" in df else ""
        df["Result"] = df.get("Position", 0).apply(parse_result)
        frames.append(
            df[["Confidence", "Tags", "Race Type", "Result", "Odds", "odds_delta"]]
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    files = sorted(glob.glob("logs/tips_results_*_advised_all.csv"))
    if not files:
        print("No tip result CSVs found in logs/.")
        return

    df = load_files(files)
    if df.empty:
        print("No data could be loaded from tip result files.")
        return

    out_path = "logs/roi/self_train_dataset.csv"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Dataset written to {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
