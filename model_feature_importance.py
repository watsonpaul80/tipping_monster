#!/usr/bin/env python3
"""Generate SHAP feature importance charts for the current model."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
import tarfile
import tempfile
import glob

import pandas as pd
import shap
import matplotlib.pyplot as plt
import xgboost as xgb

import boto3

from tippingmonster import logs_path, repo_path, send_telegram_photo, in_dev_mode
from validate_features import load_dataset

def load_model(model_path: str) -> tuple[xgb.XGBClassifier, list[str]]:
    """Load XGBoost model and feature list from ``model_path``.

    ``model_path`` may be a ``.bst`` file or a ``.tar.gz`` archive containing
    ``tipping-monster-xgb-model.bst`` and ``features.json``.
    """
    if model_path.endswith(".tar.gz"):
        tmpdir = tempfile.mkdtemp()
        with tarfile.open(model_path, "r:gz") as tar:
            tar.extractall(tmpdir)
        model_file = Path(tmpdir) / "tipping-monster-xgb-model.bst"
        features_file = Path(tmpdir) / "features.json"
    else:
        model_file = Path(model_path)
        features_file = model_file.with_name("features.json")
        if not features_file.exists():
            features_file = repo_path("features.json")
    model = xgb.XGBClassifier()
    model.load_model(str(model_file))
    with open(features_file) as f:
        features = json.load(f)
    return model, features

def load_data(paths: list[str]) -> pd.DataFrame:
    """Load and concatenate dataset files."""
    frames = [load_dataset(p) for p in paths]
    return pd.concat(frames, ignore_index=True)

def upload_to_s3(file_path: Path, bucket: str) -> None:
    """Upload file to S3 under model_explainability/ with today's date."""
    key = f"model_explainability/{date.today().isoformat()}_top_features.png"
    boto3.client("s3").upload_file(str(file_path), bucket, key)
    print(f"Uploaded SHAP chart to s3://{bucket}/{key}")

def generate_chart(
    model_path: str,
    data_path: str | None = None,
    out: Path | None = None,
    telegram: bool = False,
) -> Path:
    """Create a SHAP bar chart of the top 10 features.

    Returns the path to the saved PNG file.
    """
    model, features = load_model(model_path)

    if data_path is None:
        latest = sorted(Path("rpscrape/batch_inputs").glob("*.jsonl"))[-1]
        data_path = str(latest)

    with open(data_path) as f:
        df = pd.DataFrame(json.loads(line) for line in f)
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    plt.clf()
    shap.summary_plot(shap_values, X, feature_names=features,
                      max_display=10, show=False, plot_type="bar")
    plt.tight_layout()

    if out is None:
        out = logs_path("model", f"feature_importance_{date.today().isoformat()}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    plt.close()

    if telegram:
        caption = f"Top model features {date.today().isoformat()}"
        send_telegram_photo(out, caption=caption)
    return out

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate SHAP feature importance chart")
    parser.add_argument("--model", default="tipping-monster-xgb-model.bst",
                        help="Path to model .bst or .tar.gz")
    parser.add_argument("--data", help="Input JSONL with model features")
    parser.add_argument("--out-file", help="Where to save PNG")
    parser.add_argument("--telegram", action="store_true", help="Send chart to Telegram")
    parser.add_argument("--s3-bucket", help="Upload chart to this S3 bucket")
    args = parser.parse_args(argv)

    out = generate_chart(args.model, args.data, Path(args.out_file) if args.out_file else None,
                         telegram=args.telegram)
    print(f"📈 Feature chart saved to {out}")

    if args.s3_bucket:
        upload_to_s3(out, args.s3_bucket)

if __name__ == "__main__":
    main()
