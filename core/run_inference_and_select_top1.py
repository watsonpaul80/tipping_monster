#!/usr/bin/env python3
import argparse
from datetime import date
from pathlib import Path

import orjson
import pandas as pd
import xgboost as xgb

from tippingmonster.env_loader import load_env
from tippingmonster.utils import upload_to_s3

load_env()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--input", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    out_dir = Path("predictions") / date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [orjson.loads(line) for line in input_path.read_text().splitlines()]
    X = pd.DataFrame(rows)
    model = xgb.XGBClassifier()
    model.load_model(args.model)
    proba = model.predict_proba(X)[:, 1]

    predictions = []
    races = {}
    global_max = proba.max()
    for row, conf in zip(rows, proba):
        race = row["race"]
        if race not in races or conf > races[race]["confidence"]:
            entry = {
                "race": race,
                "name": row["name"],
                "confidence": float(conf),
                "global_max_confidence": float(global_max),
                "tags": ["\U0001f9e0 Monster NAP", "\U0001f7e2 Class Drop"],
            }
            races[race] = entry
    predictions = list(races.values())

    out_file = out_dir / "output.jsonl"
    with open(out_file, "w") as f:
        for p in predictions:
            f.write(orjson.dumps(p).decode() + "\n")

    upload_to_s3(out_file, "tipping-monster", out_file.name)


if __name__ == "__main__":
    main()
