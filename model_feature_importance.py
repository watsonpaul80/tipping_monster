#!/usr/bin/env python3
"""Generate and optionally upload SHAP feature importance chart."""

from __future__ import annotations

import argparse
import glob
import json
import tarfile
import tempfile
from datetime import date
from pathlib import Path

import boto3
import matplotlib.pyplot as plt
import pandas as pd
import shap
import xgboost as xgb

from tippingmonster import logs_path, repo_path, send_telegram_photo
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


def generate_shap_chart(
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

    # Allow glob patterns for data_path
    data_paths = sorted(glob.glob(data_path))
    if not data_paths:
        raise FileNotFoundError(f"No dataset files found for pattern: {data_path}")

    df = load_data(data_paths)
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    plt.clf()
    shap.summary_plot(
        shap_values,
        X,
        feature_names=features,
        max_display=10,
        show=False,
        plot_type="bar",
    )
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


# Backwards compatibility for older CLI imports
generate_chart = generate_shap_chart


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SHAP feature importance chart"
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default=None,
        help="Dataset CSV or JSONL (glob pattern allowed). If not provided, uses the latest batch input.",
    )
    parser.add_argument(
        "--model",
        default="tipping-monster-xgb-model.bst",
        help="Path to model .bst or .tar.gz",
    )
    parser.add_argument("--out-file", help="Where to save PNG")
    parser.add_argument(
        "--telegram", action="store_true", help="Send chart to Telegram"
    )
    parser.add_argument("--s3-bucket", help="Upload chart to this S3 bucket")
    args = parser.parse_args(argv)

    try:
        out = generate_shap_chart(
            args.model,
            args.dataset,
            Path(args.out_file) if args.out_file else None,
            telegram=args.telegram,
        )
        print(f"📈 Feature chart saved to {out}")

        if args.s3_bucket:
            upload_to_s3(out, args.s3_bucket)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
