#!/usr/bin/env python3
"""Generate and optionally upload SHAP feature importance chart."""

from __future__ import annotations

import argparse
import base64
import glob
import gzip
import json
import os
import tarfile
import tempfile
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import xgboost as xgb

from core.validate_features import load_dataset
from tippingmonster import logs_path, repo_path, send_telegram_photo
from tippingmonster.utils import load_xgb_model, upload_to_s3


def load_model(model_path: str) -> tuple[xgb.XGBClassifier, list[str]]:
    """Load XGBoost model and feature list from `model_path`.

    `model_path` may be a plain `.bst` file, a gzip-compressed `.bst.gz` file,
    a Base64 encoded variant ending in `.b64`, or a `.tar.gz` archive
    containing `tipping-monster-xgb-model.bst` and `features.json`.
    """
    if model_path.endswith(".tar.gz"):
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(model_path, "r:gz") as tar:
                tar.extractall(tmpdir)
            model_file = Path(tmpdir) / "tipping-monster-xgb-model.bst"
            features_file = Path(tmpdir) / "features.json"
            model = load_xgb_model(str(model_file))
            with open(features_file) as f:
                features = json.load(f)
            return model, features
    else:
        data = Path(model_path).read_bytes()
        cleaned = model_path
        if cleaned.endswith(".b64"):
            data = base64.b64decode(data)
            cleaned = cleaned[:-4]

        if cleaned.endswith(".gz"):
            data = gzip.decompress(data)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bst")
            tmp.write(data)
            tmp.flush()
            tmp.close()
            model_file = Path(tmp.name)
            cleanup = True
        elif cleaned.endswith(".bst") and data is not None and cleaned != model_path:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bst")
            tmp.write(data)
            tmp.flush()
            tmp.close()
            model_file = Path(tmp.name)
            cleanup = True
        else:
            model_file = Path(cleaned)
            cleanup = False
        features_file = Path(model_path).with_name("features.json")
        if not features_file.exists():
            features_file = repo_path("features.json")
    model = load_xgb_model(str(model_file))
    if "cleanup" in locals() and cleanup:
        os.unlink(model_file)
    with open(features_file) as f:
        features = json.load(f)
    return model, features


def load_data(paths: list[str]) -> pd.DataFrame:
    """Load and concatenate dataset files."""
    frames = [load_dataset(p) for p in paths]
    return pd.concat(frames, ignore_index=True)


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

    # Save top 5 features per tip for internal review
    shap_rows = []
    for i, row in df.iterrows():
        values = shap_values[i]
        top_idx = list(np.argsort(np.abs(values))[-5:][::-1])
        tip_id = f"{row.get('race', '')}|{row.get('horse', '')}"
        for idx in top_idx:
            shap_rows.append(
                {
                    "Tip": tip_id,
                    "Feature": features[idx],
                    "Value": float(values[idx]),
                }
            )
    if shap_rows:
        shap_csv = logs_path("shap_explanations.csv")
        shap_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(shap_rows).to_csv(shap_csv, index=False)

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


def generate_chart(
    model_path: str,
    data_path: str | None = None,
    out: Path | None = None,
    telegram: bool = False,
) -> Path:
    """Alias for :func:`generate_shap_chart`."""
    return generate_shap_chart(model_path, data_path, out, telegram)


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
        default="tipping-monster-xgb-model.bst.gz.b64",
        help="Path to model .bst(.gz[.b64]) or .tar.gz",
    )
    parser.add_argument("--out-file", help="Where to save PNG")
    parser.add_argument(
        "--telegram", action="store_true", help="Send chart to Telegram"
    )
    parser.add_argument("--s3-bucket", help="Upload chart to this S3 bucket")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    try:
        out = generate_shap_chart(
            args.model,
            args.dataset,
            Path(args.out_file) if args.out_file else None,
            telegram=args.telegram,
        )
        print(f"📈 Feature chart saved to {out}")

        if args.s3_bucket:
            key = f"model_explainability/{date.today().isoformat()}_top_features.png"
            if os.getenv("TM_DEV_MODE") == "1":
                print(f"[DEV] Skipping S3 upload of {out}")
            else:
                upload_to_s3(out, args.s3_bucket, key)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
