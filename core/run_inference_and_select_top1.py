#!/usr/bin/env python3

# --- Standard Library ---
import argparse
import glob
import json
import os
import pickle
import sys
import tarfile
import tempfile
from datetime import date, datetime
from pathlib import Path

# --- Third-Party Libraries ---
import boto3
import numpy as np
import orjson
import pandas as pd
import xgboost as xgb

# --- Local Modules ---
sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.model_fetcher import download_if_missing
from tippingmonster.env_loader import load_env

# ... [KEEP ALL YOUR EXISTING FUNCTION DEFINITIONS HERE: generate_reason, generate_tags, make_json_safe, load_combined_results, get_last_class, extract_race_sort_key] ...

def main() -> None:
    load_env()

    models = sorted(glob.glob("tipping-monster-xgb-model-*.tar.gz"))
    if not models:
        raise FileNotFoundError(
            "No model tarball found. Download one from S3 or run training."
        )
    latest_model = models[-1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default=latest_model,
        help="Path to model .tar.gz (S3-relative or local)",
    )
    parser.add_argument("--input", default=None, help="Path to input JSONL")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    date_str = date.today().isoformat()
    input_path = args.input or f"rpscrape/batch_inputs/{date_str}.jsonl"
    output_path = f"predictions/{date_str}/output.jsonl"
    os.makedirs(f"predictions/{date_str}", exist_ok=True)

    model_arg = args.model
    bucket = "tipping-monster"

    if os.path.exists(model_arg):
        model_path = model_arg
    else:
        local_model_file = os.path.basename(model_arg)
        download_if_missing(bucket, model_arg, local_model_file)
        model_path = local_model_file

    with tempfile.TemporaryDirectory() as model_dir:
        with tarfile.open(model_path, "r:gz") as tar:
            tar.extractall(model_dir)

        model_file = os.path.join(model_dir, "tipping-monster-xgb-model.bst")
        features_file = os.path.join(model_dir, "features.json")

        model = xgb.XGBClassifier()
        model.load_model(model_file)

        # Load optional meta place model
        meta_place_model = None
        meta_feat_file = os.path.join(model_dir, "meta_place_features.json")
        meta_model_file = os.path.join(model_dir, "meta_place_model.pkl")
        if os.path.exists(meta_model_file) and os.path.exists(meta_feat_file):
            with open(meta_model_file, "rb") as f:
                meta_place_model = pickle.load(f)
            with open(meta_feat_file) as f:
                meta_place_features = json.load(f)
        else:
            meta_place_features = []

        with open(input_path) as f:
            rows = [json.loads(line) for line in f]
        df = pd.DataFrame(rows)

        model_features = list(df.columns)
        if os.path.exists(features_file):
            with open(features_file) as f:
                model_features = json.load(f)

        missing = [f for f in model_features if f not in df.columns]
        if missing:
            print(f"❌ Feature mismatch. Missing: {missing}")
            sys.exit(1)

        X = df[model_features]
        X = X.apply(pd.to_numeric, errors="coerce").fillna(-1)

        df["confidence"] = model.predict_proba(X)[:, 1]

        # Generate final_place_confidence if meta place model is available
        if meta_place_model and meta_place_features:
            missing_meta = [f for f in meta_place_features if f not in df.columns]
            if missing_meta:
                print(f"❌ Place feature mismatch. Missing: {missing_meta}")
            else:
                X_place = df[meta_place_features]
                X_place = X_place.apply(pd.to_numeric, errors="coerce").fillna(-1)
                df["final_place_confidence"] = meta_place_model.predict_proba(X_place)[:, 1]

        top_tips = df.sort_values("confidence", ascending=False).groupby("race").head(1)

        top_tips["sort_key"] = top_tips["race"].apply(extract_race_sort_key)
        top_tips = top_tips.sort_values("sort_key").drop(columns="sort_key")

        combined_results_df = load_combined_results()
        today_date = datetime.today().date()

        with open(output_path, "w") as f:
            max_conf = top_tips["confidence"].max()
            for row in top_tips.to_dict(orient="records"):
                row["last_class"] = get_last_class(
                    row["name"], today_date, combined_results_df
                )
                row["global_max_confidence"] = max_conf
                row["tags"] = generate_tags(row)
                row["commentary"] = generate_reason(row)
                row_safe = make_json_safe(row)
                f.write(orjson.dumps(row_safe).decode() + "\n")

        print(f"Saved {len(top_tips)} top tips to {output_path}")

    if os.getenv("TM_DEV_MODE") == "1":
        print(f"[DEV] Skipping S3 upload of {output_path}")
    else:
        s3 = boto3.client("s3")
        s3.upload_file(output_path, bucket, f"predictions/{date_str}/output.jsonl")
        print(f"✅ Uploaded to s3://{bucket}/predictions/{date_str}/output.jsonl")


if __name__ == "__main__":
    main()