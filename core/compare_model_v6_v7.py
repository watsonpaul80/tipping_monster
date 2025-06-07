#!/usr/bin/env python3
"""Train model v6 and v7 on the same dataset and log confidence comparison.

This script mirrors the logic of ``train_model_v6.py`` and ``train_modelv7.py``
but fits both models side by side. It then runs inference on the training
set and records the confidence scores for each horse in
``logs/compare_model_v6_v7.csv``.

Columns: ``Race``, ``Horse``, ``v6_conf``, ``v7_conf``, ``delta``, ``winner``.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import glob
import os
import pandas as pd
import xgboost as xgb
from datetime import date

from core.train_model_v6 import load_all_results, merge_tip_logs, preprocess


FEATURES_V6 = [
    "draw",
    "or",
    "rpr",
    "lbs",
    "age",
    "dist_f",
    "class",
    "going",
    "prize",
]

FEATURES_V7 = [
    "draw",
    "or",
    "rpr",
    "lbs",
    "age",
    "dist_f",
    "class",
    "going",
    "prize",
    "was_tipped",
    "tip_confidence",
    "tip_profit",
]

S3_KEYS = [
    "results/gb-flat-2015-2025.csv",
    "results/gb-jumps-2015-2025.csv",
    "results/ire-flat-2015-2025.csv",
    "results/ire-jumps-2015-2025.csv",
]


def fit_model(df: pd.DataFrame, feature_cols: list[str]) -> xgb.XGBClassifier:
    """Fit an XGBoost classifier and return the model."""
    X = df[feature_cols]
    y = df["won"]
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, y)
    return model


def calculate_roi(df: pd.DataFrame, conf_col: str) -> float:
    """Return simple ROI if betting the top horse per race."""
    profit = 0.0
    races = df["race"].unique()
    for race in races:
        race_df = df[df["race"] == race]
        top = race_df.loc[race_df[conf_col].idxmax()]
        sp = float(top.get("bf_sp", 1.0))
        profit += (sp - 1.0) if top["won"] else -1.0
    return profit / len(races) if len(races) else 0.0


def main() -> None:
    print("📅 Downloading historical data from S3…")
    df = load_all_results(S3_KEYS)
    print("🔧 Preprocessing…")
    df = preprocess(df)
    tip_logs = sorted(glob.glob("logs/roi/tips_results_*_advised.csv"))
    if tip_logs:
        print(f"📝 Injecting tip logs: {tip_logs[-3:]} …")
        df = merge_tip_logs(df, tip_logs)
    else:
        print("⚠️ No tip logs found, proceeding without tip enrichment.")

    print("🚀 Training model v6…")
    model_v6 = fit_model(df, FEATURES_V6)
    print("🚀 Training model v7…")
    model_v7 = fit_model(df, FEATURES_V7)

    df["v6_conf"] = model_v6.predict_proba(df[FEATURES_V6])[:, 1]
    df["v7_conf"] = model_v7.predict_proba(df[FEATURES_V7])[:, 1]
    df["delta"] = df["v7_conf"] - df["v6_conf"]

    roi_v6 = calculate_roi(df, "v6_conf")
    roi_v7 = calculate_roi(df, "v7_conf")
    print(f"ROI v6: {roi_v6:.2f} | ROI v7: {roi_v7:.2f}")

    out = df[["race", "horse", "v6_conf", "v7_conf", "delta", "won"]].copy()
    out.columns = ["Race", "Horse", "v6_conf", "v7_conf", "delta", "winner"]
    os.makedirs("logs", exist_ok=True)
    out.to_csv("logs/compare_model_v6_v7.csv", index=False)
    print("✅ Comparison saved to logs/compare_model_v6_v7.csv")


if __name__ == "__main__":
    main()
