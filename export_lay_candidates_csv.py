#!/usr/bin/env python3
"""Export Danger Fav candidates to CSV for easy viewing."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_jsonl(path: Path) -> List[Dict]:
    items: List[Dict] = []
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export Danger Fav candidates to CSV")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument(
        "--out",
        help="Output CSV file",
        default=None,
    )
    args = parser.parse_args(argv)

    cand_path = Path(f"predictions/{args.date}/danger_favs.jsonl")
    items = load_jsonl(cand_path)
    if not items:
        print(f"No Danger Favs found at {cand_path}")
        return

    df = pd.DataFrame(items)
    df = df[["race", "name", "bf_sp", "confidence"]]
    df.rename(
        columns={
            "name": "Horse",
            "bf_sp": "SP",
            "race": "Race",
            "confidence": "Confidence",
        },
        inplace=True,
    )

    out_path = Path(args.out) if args.out else cand_path.with_name("lay_candidates.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} entries to {out_path}")


if __name__ == "__main__":
    main()
