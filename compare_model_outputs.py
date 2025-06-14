#!/usr/bin/env python3
"""Compare predictions from two model versions on the same racecards."""

from __future__ import annotations

import argparse
import glob
import json
import os
import tarfile
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import shap
import xgboost as xgb

from core.model_fetcher import download_if_missing


def load_model(tar_path: str) -> tuple[xgb.XGBClassifier, list[str]]:
    """Extract and load model + feature list from a tarball."""
    if not os.path.exists(tar_path):
        bucket = "tipping-monster"
        local_name = os.path.basename(tar_path)
        download_if_missing(bucket, tar_path, local_name)
        tar_path = local_name
    tmpdir = tempfile.mkdtemp()
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(tmpdir)
    model_file = Path(tmpdir) / "tipping-monster-xgb-model.bst"
    features_file = Path(tmpdir) / "features.json"
    with open(features_file) as f:
        features = json.load(f)
    model = xgb.XGBClassifier()
    model.load_model(model_file)
    return model, features


def load_data(path: str) -> pd.DataFrame:
    """Load flattened racecards from JSONL."""
    paths = sorted(glob.glob(path))
    if not paths:
        raise FileNotFoundError(f"No input files match {path}")
    frames = []
    for p in paths:
        with open(p) as f:
            rows = [json.loads(line) for line in f]
        frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True)


def predict(
    df: pd.DataFrame, model: xgb.XGBClassifier, features: list[str]
) -> pd.Series:
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)
    return pd.Series(model.predict_proba(X)[:, 1], index=df.index)


def shap_summary(
    model: xgb.XGBClassifier, X: pd.DataFrame, features: list[str], top_n: int = 3
) -> str:
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(X)[0]
    idx = np.argsort(np.abs(values))[-top_n:][::-1]
    parts = [f"{features[i]}:{values[i]:+.2f}" for i in idx]
    return ", ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two model outputs")
    parser.add_argument(
        "--model-v6", required=True, help="Path or S3 key for v6 model tar.gz"
    )
    parser.add_argument(
        "--model-v7", required=True, help="Path or S3 key for v7 model tar.gz"
    )
    parser.add_argument(
        "--input", required=True, help="Flattened racecards JSONL pattern"
    )
    parser.add_argument(
        "--out", default="logs/compare_model_outputs.csv", help="Output CSV path"
    )
    args = parser.parse_args()

    df = load_data(args.input)

    model_v6, feats_v6 = load_model(args.model_v6)
    model_v7, feats_v7 = load_model(args.model_v7)

    df["v6_conf"] = predict(df, model_v6, feats_v6)
    df["v7_conf"] = predict(df, model_v7, feats_v7)

    rows = []
    for race, race_df in df.groupby("race"):
        top_v6 = race_df.loc[race_df["v6_conf"].idxmax()]
        top_v7 = race_df.loc[race_df["v7_conf"].idxmax()]
        shap_v6 = shap_summary(model_v6, top_v6[feats_v6].to_frame().T, feats_v6)
        shap_v7 = shap_summary(model_v7, top_v7[feats_v7].to_frame().T, feats_v7)
        rows.append(
            {
                "Race": race,
                "Tip_v6": top_v6["name"],
                "Conf_v6": top_v6["v6_conf"],
                "Tip_v7": top_v7["name"],
                "Conf_v7": top_v7["v7_conf"],
                "Delta": top_v7["v7_conf"] - top_v6["v6_conf"],
                "Same": top_v6["name"] == top_v7["name"],
                "Features_v6": shap_v6,
                "Features_v7": shap_v7,
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"✅ Saved comparison to {out_path}")


if __name__ == "__main__":
    main()
