#!/usr/bin/env python3
"""Generate weekly ROI summary CSV from daily advised results."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd

# === Helpers ===


def get_repo_root() -> Path:
    env_root = os.getenv("TIPPING_MONSTER_HOME")
    if env_root:
        return Path(env_root)
    try:
        out = Path(__file__).resolve().parent.joinpath("..").resolve()
        return Path(os.popen(f"git -C {out} rev-parse --show-toplevel").read().strip())
    except Exception:
        return Path(__file__).resolve().parents[1]


REPO_ROOT = get_repo_root()
LOG_DIR = REPO_ROOT / "logs"
OUT_DIR = LOG_DIR / "weekly_summaries"
os.makedirs(OUT_DIR, exist_ok=True)


# === Utilities ===


def is_win(pos: str | int) -> bool:
    try:
        return int(pos) == 1
    except Exception:
        return False


def is_place(pos: str | int) -> bool:
    try:
        p = int(pos)
        return 2 <= p <= 4
    except Exception:
        return False


# === Main Logic ===


def collect_files() -> dict[str, list[Path]]:
    weekly: dict[str, list[Path]] = {}
    for csv in LOG_DIR.glob("tips_results_*_advised.csv"):
        name = csv.name.replace("tips_results_", "").replace("_advised.csv", "")
        try:
            date_obj = datetime.strptime(name, "%Y-%m-%d")
        except ValueError:
            continue
        year, week, _ = date_obj.isocalendar()
        key = f"{year}-W{week:02d}"
        weekly.setdefault(key, []).append(csv)
    return weekly


def summarize_week(paths: list[Path], week: str) -> pd.DataFrame:
    rows = []
    for path in sorted(paths):
        df = pd.read_csv(path)
        date_str = path.stem.replace("tips_results_", "").replace("_advised", "")
        df["Date"] = date_str
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)
        df["Stake"] = pd.to_numeric(df["Stake"], errors="coerce").fillna(0)
        rows.append(df)

    if not rows:
        return pd.DataFrame()

    week_df = pd.concat(rows, ignore_index=True)

    summary = (
        week_df.groupby("Date", as_index=False)
        .agg({"Horse": "count", "Position": list, "Profit": "sum", "Stake": "sum"})
        .rename(columns={"Horse": "Tips"})
    )

    summary["Wins"] = summary["Position"].apply(lambda x: sum(is_win(p) for p in x))
    summary["Places"] = summary["Position"].apply(lambda x: sum(is_place(p) for p in x))
    summary.drop(columns="Position", inplace=True)
    summary["ROI"] = summary.apply(
        lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
    )

    totals = summary.agg(
        {
            "Date": lambda x: "TOTAL",
            "Tips": "sum",
            "Wins": "sum",
            "Places": "sum",
            "Stake": "sum",
            "Profit": "sum",
        }
    )
    totals["ROI"] = (totals["Profit"] / totals["Stake"] * 100) if totals["Stake"] else 0
    summary = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)
    summary.insert(0, "Week", week)

    return summary


def main() -> None:
    weekly_files = collect_files()
    for week, paths in weekly_files.items():
        summary = summarize_week(paths, week)
        if summary.empty:
            continue
        out_file = OUT_DIR / f"weekly_summary_{week}.csv"
        summary.to_csv(out_file, index=False)
        print(f"✅ Saved {out_file}")


if __name__ == "__main__":
    main()
