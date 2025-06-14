#!/usr/bin/env python3
"""Compare daily predictions from v6, v7 and v8 models."""

import argparse
from pathlib import Path

import pandas as pd


def load_jsonl(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_json(path, lines=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="Date in YYYY-MM-DD")
    parser.add_argument("--out", default=None, help="Output CSV path")
    args = parser.parse_args()

    date_str = args.date or pd.Timestamp.today().date().isoformat()
    pred_dir = Path("predictions") / date_str
    out_file = Path(args.out or f"logs/compare_models_{date_str}.csv")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    v6 = load_jsonl(pred_dir / "output_v6.jsonl")
    v7 = load_jsonl(pred_dir / "output_v7.jsonl")
    v8 = load_jsonl(pred_dir / "output_v8.jsonl")

    merged = (
        v6[["race", "name", "confidence"]]
        .rename(columns={"name": "v6_horse", "confidence": "v6_conf"})
        .merge(
            v7[["race", "name", "confidence"]].rename(
                columns={"name": "v7_horse", "confidence": "v7_conf"}
            ),
            on="race",
            how="outer",
        )
        .merge(
            v8[["race", "name", "final_confidence"]].rename(
                columns={"name": "v8_horse", "final_confidence": "v8_conf"}
            ),
            on="race",
            how="outer",
        )
    )

    merged.to_csv(out_file, index=False)
    print(f"Saved comparison to {out_file}")


if __name__ == "__main__":
    main()
