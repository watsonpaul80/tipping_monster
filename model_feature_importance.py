#!/usr/bin/env python3
"""Generate and optionally upload SHAP feature importance chart."""

from __future__ import annotations

import argparse
import glob
import json
from datetime import date
from pathlib import Path

import boto3
import matplotlib.pyplot as plt
import pandas as pd
import shap
import xgboost as xgb

from validate_features import load_dataset


def load_data(paths: list[str]) -> pd.DataFrame:
    """Load and concatenate dataset files."""
    frames = [load_dataset(p) for p in paths]
    return pd.concat(frames, ignore_index=True)


def generate_shap_chart(model_path: str, data: pd.DataFrame, features: list[str], out: Path) -> None:
    """Create SHAP bar chart and save to `out`."""
    X = data[features].apply(pd.to_numeric, errors="coerce").fillna(-1)
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap.summary_plot(shap_values, X, show=False, plot_type="bar")
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    print(f"SHAP chart saved to {out}")


def upload_to_s3(file_path: Path, bucket: str) -> None:
    """Upload file to S3 under model_explainability/ with today's date."""
    key = f"model_explainability/{date.today().isoformat()}_top_features.png"
    boto3.client("s3").upload_file(str(file_path), bucket, key)
    print(f"Uploaded SHAP chart to s3://{bucket}/{key}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate SHAP feature importance chart")
    parser.add_argument("dataset", help="Dataset CSV or JSONL (glob pattern allowed)")
    parser.add_argument("--model", default="tipping-monster-xgb-model.bst", help="Path to model .bst")
    parser.add_argument("--features", default="features.json", help="Path to features.json")
    parser.add_argument("--out", default="top_features.png", help="Output image path")
    parser.add_argument("--s3-bucket", help="Upload chart to this S3 bucket")
    args = parser.parse_args(argv)

    paths = sorted(glob.glob(args.dataset))
    if not paths:
        print(f"No dataset files found for pattern: {args.dataset}")
        return 1

    data = load_data(paths)
    with open(args.features) as fh:
        features = json.load(fh)

    generate_shap_chart(args.model, data, features, Path(args.out))

    if args.s3_bucket:
        upload_to_s3(Path(args.out), args.s3_bucket)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
