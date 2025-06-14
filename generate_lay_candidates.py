#!/usr/bin/env python3
"""Generate Danger Fav candidates from odds and Monster confidence."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

import orjson
import pandas as pd
import xgboost as xgb

sys.path.append(str(Path(__file__).resolve().parent))
from tippingmonster.env_loader import load_env
from tippingmonster.utils import send_telegram_message

FEATURES_FILE = Path("features.json")
MODEL_FILE = Path("tipping-monster-xgb-model.bst.gz.b64")


def standardize_course_only(race: str) -> str:
    race = race.strip().lower().replace("(aw)", "").strip()
    m1 = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", race)
    m2 = re.match(r"^(.+)\s+(\d{1,2}:\d{2})$", race)
    if m1:
        return m1.group(2).strip()
    if m2:
        return m2.group(1).strip()
    return race


def race_key(race: str) -> str:
    race = race.strip().lower().replace("(aw)", "")
    m1 = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", race)
    m2 = re.match(r"^(.+)\s+(\d{1,2}:\d{2})$", race)
    if m1:
        return f"{m1.group(1)} {m1.group(2).strip()}"
    if m2:
        return f"{m2.group(2)} {m2.group(1).strip()}"
    return race


def load_model(
    model_path: Path, features_path: Path
) -> tuple[xgb.XGBClassifier, List[str]]:
    model = xgb.XGBClassifier()
    model.load_model(str(model_path))
    with open(features_path) as f:
        features = json.load(f)
    return model, features


def predict_confidence(
    df: pd.DataFrame, model: xgb.XGBClassifier, features: List[str]
) -> pd.Series:
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)
    return pd.Series(model.predict_proba(X)[:, 1], index=df.index)


def find_danger_favs(
    df: pd.DataFrame, odds: List[Dict], threshold: float = 0.6
) -> List[Dict]:
    df = df.copy()
    df["race_key"] = df["race"].apply(race_key)
    df["horse_lower"] = df["name"].str.lower().str.strip()

    top_map = (
        df.sort_values("confidence", ascending=False)
        .groupby("race_key")["horse_lower"]
        .first()
        .to_dict()
    )

    fav_map: Dict[str, Dict] = {}
    for o in odds:
        key = race_key(o.get("race", ""))
        if not key:
            continue
        current = fav_map.get(key)
        if current is None or (o.get("bf_sp") or 99.0) < (current.get("bf_sp") or 99.0):
            fav_map[key] = {
                "race": key,
                "horse_lower": o.get("horse", "").lower().strip(),
                "bf_sp": o.get("bf_sp"),
            }

    candidates = []
    for key, fav in fav_map.items():
        match = df[(df["race_key"] == key) & (df["horse_lower"] == fav["horse_lower"])]
        if match.empty:
            continue
        row = match.iloc[0]
        if row["horse_lower"] == top_map.get(key):
            continue
        conf = float(row.get("confidence", 0.0))
        if conf < threshold:
            candidates.append(
                {
                    "race": row["race"],
                    "name": row["name"],
                    "bf_sp": fav["bf_sp"],
                    "confidence": conf,
                    "tags": ["⚠️ Danger Fav"],
                }
            )
    return candidates


def load_results_csv(path: Path) -> pd.DataFrame:
    """Return normalised results DataFrame from ``path``."""
    df = pd.read_csv(path)
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


def summarise_outcomes(cands: List[Dict], results_df: pd.DataFrame) -> dict:
    """Return win/place/loss summary for ``cands`` given ``results_df``."""
    if not cands:
        return {"bets": 0, "wins": 0, "places": 0, "losses": 0}

    df = pd.DataFrame(cands)
    df["Horse"] = df["name"].astype(str).str.strip().str.lower()
    df["Race Time"] = df["race"].astype(str).str.split().str[0].str.lower()
    df["Course"] = df["race"].astype(str).str.split().str[1:].str.join(" ").str.lower()

    merged = pd.merge(
        df,
        results_df,
        how="left",
        left_on=["Horse", "Race Time", "Course"],
        right_on=["Horse", "Race Time", "Course"],
    )

    merged["Position"] = merged["Position"].fillna("NR")
    wins = (merged["Position"] == "1").sum()
    places = (
        merged["Position"].apply(lambda x: str(x).isdigit() and 2 <= int(x) <= 4).sum()
    )
    nrs = (merged["Position"] == "NR").sum()
    losses = len(merged) - wins - places - nrs
    return {
        "bets": len(merged),
        "wins": int(wins),
        "places": int(places),
        "losses": int(losses),
    }


def append_history(date_str: str, summary: dict, path: Path) -> None:
    """Append ``summary`` for ``date_str`` to CSV at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        [
            {
                "date": date_str,
                "bets": summary.get("bets", 0),
                "wins": summary.get("wins", 0),
                "places": summary.get("places", 0),
                "losses": summary.get("losses", 0),
            }
        ]
    )
    header = not path.exists()
    df.to_csv(path, mode="a", header=header, index=False)


def main(argv: List[str] | None = None) -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Generate Danger Fav candidates")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--features", help="Input features JSONL")
    parser.add_argument("--odds", help="Odds snapshot JSON")
    parser.add_argument("--model", default=str(MODEL_FILE))
    parser.add_argument("--out", help="Output JSONL file")
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--results", help="Results CSV for outcome logging")
    parser.add_argument(
        "--history",
        default="logs/danger_fav_history.csv",
        help="Danger Fav history CSV",
    )
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    features_path = Path(args.features or f"rpscrape/batch_inputs/{args.date}.jsonl")
    if not features_path.exists():
        raise FileNotFoundError(features_path)

    odds_file = args.odds
    if not odds_file:
        snaps = sorted(Path("odds_snapshots").glob(f"{args.date}_*.json"))
        if not snaps:
            raise FileNotFoundError("No odds snapshot found")
        odds_file = snaps[0]

    out_file = Path(args.out or f"predictions/{args.date}/danger_favs.jsonl")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_json(features_path, lines=True)
    model, features = load_model(Path(args.model), FEATURES_FILE)
    df["confidence"] = predict_confidence(df, model, features)

    with open(odds_file) as f:
        odds = json.load(f)

    candidates = find_danger_favs(df, odds, args.threshold)
    with open(out_file, "w", encoding="utf-8") as f:
        for row in candidates:
            f.write(orjson.dumps(row).decode() + "\n")
    print(f"Saved {len(candidates)} danger favs -> {out_file}")

    if args.results is not None:
        results_path = Path(args.results)
    else:
        results_path = Path(
            f"rpscrape/data/dates/all/{args.date.replace('-', '_')}.csv"
        )
    if results_path.exists():
        results_df = load_results_csv(results_path)
        summary = summarise_outcomes(candidates, results_df)
        append_history(args.date, summary, Path(args.history))
        print(
            f"Danger Favs {args.date}: {summary['wins']}W {summary['places']}P {summary['losses']}L"
        )
        if args.telegram:
            msg = f"⚠️ Danger Favs went {summary['wins']}/{summary['bets']} today"
            send_telegram_message(msg)
    elif args.results:
        raise FileNotFoundError(results_path)


if __name__ == "__main__":
    main()
