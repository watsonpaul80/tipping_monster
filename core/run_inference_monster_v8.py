#!/usr/bin/env python3
"""Run stacked ensemble model (v8) and output one tip per race."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tarfile
import tempfile
from datetime import date, datetime
from pathlib import Path

import joblib
import orjson
import pandas as pd
from tensorflow import keras

sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.model_fetcher import download_if_missing
from core.run_inference_and_select_top1 import (extract_race_sort_key,
                                                generate_reason, generate_tags,
                                                get_last_class,
                                                load_combined_results,
                                                make_json_safe)
from tippingmonster.env_loader import load_env

DEF_MODEL = "models/monster_v8_stack.tar.gz"
BUCKET = "tipping-monster"


def load_ensemble(model_tar: str):
    tmpdir = tempfile.mkdtemp()
    with tarfile.open(model_tar, "r:gz") as tar:
        tar.extractall(tmpdir)
    models = {
        "cat_win": joblib.load(Path(tmpdir) / "cat_win.cb"),
        "cat_place": joblib.load(Path(tmpdir) / "cat_place.cb"),
        "xgb_win": joblib.load(Path(tmpdir) / "xgb_win.pkl"),
        "xgb_place": joblib.load(Path(tmpdir) / "xgb_place.pkl"),
        "mlp_win": keras.models.load_model(Path(tmpdir) / "mlp_win.keras"),
        "mlp_place": keras.models.load_model(Path(tmpdir) / "mlp_place.keras"),
        "meta_win": joblib.load(Path(tmpdir) / "meta_win.pkl"),
        "meta_place": joblib.load(Path(tmpdir) / "meta_place.pkl"),
    }
    with open(Path(tmpdir) / "features.json") as f:
        features = json.load(f)
    with open(Path(tmpdir) / "meta_features.json") as f:
        meta_features = json.load(f)
    return models, features, meta_features


def build_meta(df: pd.DataFrame) -> pd.DataFrame:
    win_cols = [c for c in df.columns if c.startswith("confidence_win_")]
    place_cols = [c for c in df.columns if c.startswith("confidence_place_")]
    meta = pd.DataFrame()
    meta["win_mean"] = df[win_cols].mean(axis=1)
    meta["win_std"] = df[win_cols].std(axis=1)
    meta["place_mean"] = df[place_cols].mean(axis=1)
    meta["place_std"] = df[place_cols].std(axis=1)
    meta = pd.concat([df[win_cols + place_cols], meta], axis=1)
    return meta


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEF_MODEL, help="Path to ensemble tar")
    parser.add_argument("--input", default=None, help="JSONL race input")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    date_str = date.today().isoformat()
    input_path = args.input or f"rpscrape/batch_inputs/{date_str}.jsonl"
    out_dir = Path(f"predictions/{date_str}")
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "output_v8.jsonl"

    model_arg = args.model
    if not os.path.exists(model_arg):
        local_name = os.path.basename(model_arg)
        download_if_missing(BUCKET, model_arg, local_name)
        model_arg = local_name

    models, features, meta_features = load_ensemble(model_arg)

    with open(input_path) as f:
        rows = [json.loads(line) for line in f]
    df = pd.DataFrame(rows)

    missing = [c for c in features if c not in df.columns]
    if missing:
        print(f"❌ Missing features: {missing}")
        sys.exit(1)
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)

    df["confidence_win_cat"] = models["cat_win"].predict_proba(X)[:, 1]
    df["confidence_win_xgb"] = models["xgb_win"].predict_proba(X)[:, 1]
    df["confidence_win_mlp"] = models["mlp_win"].predict(X).flatten()
    df["confidence_place_cat"] = models["cat_place"].predict_proba(X)[:, 1]
    df["confidence_place_xgb"] = models["xgb_place"].predict_proba(X)[:, 1]
    df["confidence_place_mlp"] = models["mlp_place"].predict(X).flatten()

    meta = build_meta(df)
    meta_full = pd.concat([meta, X.reset_index(drop=True)], axis=1)[meta_features]
    df["final_confidence"] = models["meta_win"].predict_proba(meta_full)[:, 1]

    top = df.sort_values("final_confidence", ascending=False).groupby("race").head(1)
    top["sort_key"] = top["race"].apply(extract_race_sort_key)
    top = top.sort_values("sort_key").drop(columns="sort_key")

    combined_results_df = load_combined_results()
    today_date = datetime.today().date()
    with open(output_path, "w") as f:
        max_conf = top["final_confidence"].max()
        for row in top.to_dict(orient="records"):
            row["last_class"] = get_last_class(
                row["name"], today_date, combined_results_df
            )
            row["global_max_confidence"] = max_conf
            row["tags"] = generate_tags(row)
            row["commentary"] = generate_reason(row)
            row["model_version"] = "v8_stack"
            row_safe = make_json_safe(row)
            f.write(orjson.dumps(row_safe).decode() + "\n")

    print(f"Saved {len(top)} tips to {output_path}")
    if os.getenv("TM_DEV_MODE") != "1":
        import boto3

        boto3.client("s3").upload_file(
            str(output_path), BUCKET, f"predictions/{date_str}/output_v8.jsonl"
        )
        print("✅ Uploaded to S3")


if __name__ == "__main__":
    main()
