#!/usr/bin/env python3
"""Compare ROI with and without self-training features.

This script trains two XGBoost models on the same historical dataset.
The first model uses only basic race features (baseline). The second
merges past tips from log files and includes those columns during
training (self-training). ROI for betting the top horse in each race is
reported for both models.
"""

import glob
import os

import pandas as pd
import xgboost as xgb

from train_model_v6 import load_all_results, merge_tip_logs, preprocess

BASE_FEATURES = [
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

SELF_FEATURES = BASE_FEATURES + ["was_tipped", "tip_confidence", "tip_profit"]

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

    log_base = os.getenv("TM_LOG_DIR", "logs")
    tip_logs = sorted(glob.glob(f"{log_base}/roi/tips_results_*_advised.csv"))
    df_self = df.copy()
    if tip_logs:
        print(f"📝 Injecting tip logs: {tip_logs[-3:]} …")
        df_self = merge_tip_logs(df_self, tip_logs)
    else:
        print("⚠️ No tip logs found, self-training will be identical to baseline.")

    print("🚀 Training baseline model…")
    model_base = fit_model(df, BASE_FEATURES)
    print("🚀 Training self-trained model…")
    model_self = fit_model(df_self, SELF_FEATURES)

    df["base_conf"] = model_base.predict_proba(df[BASE_FEATURES])[:, 1]
    df_self["self_conf"] = model_self.predict_proba(df_self[SELF_FEATURES])[:, 1]

    roi_base = calculate_roi(df, "base_conf")
    roi_self = calculate_roi(df_self, "self_conf")
    print(f"ROI baseline: {roi_base:.2f} | ROI self-training: {roi_self:.2f}")

    os.makedirs("logs", exist_ok=True)
    out = pd.DataFrame(
        {
            "Race": df["race"],
            "Horse": df["horse"],
            "base_conf": df["base_conf"],
            "self_conf": df_self["self_conf"],
            "winner": df["won"],
        }
    )
    out.to_csv("logs/evaluate_self_training.csv", index=False)
    print("✅ Evaluation saved to logs/evaluate_self_training.csv")


if __name__ == "__main__":
    main()
