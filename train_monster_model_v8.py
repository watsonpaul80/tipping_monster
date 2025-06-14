#!/usr/bin/env python3
"""Train Monster model v8 using a stacked ensemble.

This script trains CatBoost, XGBoost and Keras MLP base models to
predict both win and place outcomes. Their predictions feed a logistic
regression meta model. The final ensemble is packaged as
`models/monster_v8_stack.tar.gz`.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import tarfile
import tempfile
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from catboost import CatBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, classification_report
from sklearn.model_selection import train_test_split
from tensorflow import keras

from tippingmonster.utils import get_place_terms, upload_to_s3
from train_model_v6 import load_all_results
from validate_features import validate_dataset_features

BUCKET = "tipping-monster"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning and target creation."""
    df["horse"] = (
        df["horse"]
        .astype(str)
        .str.strip()
        .str.replace(r" \([A-Z]{2,3}\)", "", regex=True)
    )
    df["course"] = df["course"].astype(str).str.strip()
    df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(-1)
    df["or"] = pd.to_numeric(df["or"], errors="coerce").fillna(-1)
    df["lbs"] = pd.to_numeric(df["lbs"], errors="coerce").fillna(-1)
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(-1)
    df["dist_f"] = pd.to_numeric(df["dist_f"], errors="coerce").fillna(-1)
    df["prize"] = pd.to_numeric(df["prize"], errors="coerce").fillna(-1)
    df["rpr"] = (
        df["rpr"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
        .fillna(-1)
    )
    df["going"] = df["going"].astype(str).str.strip().astype("category").cat.codes
    df["class"] = (
        df["class"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
        .fillna(-1)
    )
    df["won"] = (df["pos"].astype(str) == "1").astype(int)
    df["placed"] = compute_place_label(df)
    return df


def compute_place_label(df: pd.DataFrame) -> pd.Series:
    """Return dynamic place label based on runners if available."""
    if {"Runners", "Race Name"}.issubset(df.columns):

        def label(row: pd.Series) -> int:
            try:
                _frac, places = get_place_terms(
                    {"Runners": row["Runners"], "Race Name": row["Race Name"]}
                )
            except Exception:
                places = 3
            pos = str(row["pos"])
            return int(pos.isdigit() and int(pos) <= places)

        return df.apply(label, axis=1)
    return df["pos"].astype(str).isin(["1", "2", "3", "4"]).astype(int)


def build_meta_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return features for the meta model."""
    win_cols = [c for c in df.columns if c.startswith("confidence_win_")]
    place_cols = [c for c in df.columns if c.startswith("confidence_place_")]
    meta = pd.DataFrame()
    meta["win_mean"] = df[win_cols].mean(axis=1)
    meta["win_std"] = df[win_cols].std(axis=1)
    meta["place_mean"] = df[place_cols].mean(axis=1)
    meta["place_std"] = df[place_cols].std(axis=1)
    meta = pd.concat([df[win_cols + place_cols], meta], axis=1)
    return meta


def train_base_models(X_train: pd.DataFrame, y_win: pd.Series, y_place: pd.Series):
    cat_win = CatBoostClassifier(verbose=False)
    cat_win.fit(X_train, y_win)
    cat_place = CatBoostClassifier(verbose=False)
    cat_place.fit(X_train, y_place)

    xgb_win = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    xgb_win.fit(X_train, y_win)
    xgb_place = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    xgb_place.fit(X_train, y_place)

    def build_mlp(input_dim: int) -> keras.Model:
        model = keras.Sequential(
            [
                keras.layers.Input(shape=(input_dim,)),
                keras.layers.Dense(64, activation="relu"),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dense(1, activation="sigmoid"),
            ]
        )
        model.compile(
            optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"]
        )
        return model

    mlp_win = build_mlp(X_train.shape[1])
    mlp_win.fit(X_train, y_win, epochs=10, batch_size=32, verbose=0)
    mlp_place = build_mlp(X_train.shape[1])
    mlp_place.fit(X_train, y_place, epochs=10, batch_size=32, verbose=0)

    return {
        "cat_win": cat_win,
        "cat_place": cat_place,
        "xgb_win": xgb_win,
        "xgb_place": xgb_place,
        "mlp_win": mlp_win,
        "mlp_place": mlp_place,
    }


def merge_tip_logs_dedup(
    base_df: pd.DataFrame, tip_files: list[str]
) -> tuple[pd.DataFrame, int]:
    """Merge self-training tips, deduplicated by date/course/horse."""
    tip_dfs = [pd.read_csv(f) for f in tip_files if os.path.exists(f)]
    if not tip_dfs:
        return base_df, 0
    tips = pd.concat(tip_dfs, ignore_index=True)
    before = len(tips)
    tips = tips.drop_duplicates(subset=["Date", "Course", "Horse"])
    merged_count = len(tips)

    base_df["was_tipped"] = 0
    base_df["tip_confidence"] = None
    base_df["tip_profit"] = None
    base_df["confidence_band"] = None

    for _, row in tips.iterrows():
        mask = (
            (base_df["date"].astype(str) == str(row["Date"]))
            & (base_df["course"].astype(str).str.lower() == str(row["Course"]).lower())
            & (base_df["horse"].astype(str).str.lower() == str(row["Horse"]).lower())
        )
        base_df.loc[mask, "was_tipped"] = 1
        base_df.loc[mask, "tip_confidence"] = row.get("Confidence", None)
        base_df.loc[mask, "tip_profit"] = row.get("Profit", None)
        conf = row.get("Confidence", None)
        if pd.notnull(conf):
            conf = float(conf)
            if conf < 0.7:
                band = "low"
            elif conf < 0.8:
                band = "ok"
            elif conf < 0.9:
                band = "strong"
            else:
                band = "elite"
            base_df.loc[mask, "confidence_band"] = band

    print(f"Merged {merged_count} unique tips (deduped {before - merged_count})")
    return base_df, merged_count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    parser.add_argument(
        "--self-train", action="store_true", help="Include tip logs for self-training"
    )
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    s3_keys = [
        "results/gb-flat-2015-2025.csv",
        "results/gb-jumps-2015-2025.csv",
        "results/ire-flat-2015-2025.csv",
        "results/ire-jumps-2015-2025.csv",
    ]
    print("📅 Downloading historical data from S3…")
    df = load_all_results(s3_keys)
    df = preprocess(df)

    tip_logs: list[str] = []
    merged_tips = 0
    if args.self_train:
        tip_logs = sorted(glob.glob("logs/roi/tips_results_*_advised.csv"))
        if tip_logs:
            print(f"📝 Injecting tip logs: {tip_logs[-3:]}…")
            df, merged_tips = merge_tip_logs_dedup(df, tip_logs)

    feature_cols = [
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
    if "stale_penalty" in df.columns:
        feature_cols.append("stale_penalty")

    missing, extra = validate_dataset_features(feature_cols, df)
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
    if extra:
        print(f"Ignoring extra columns: {extra}")

    X = df[feature_cols]
    y_win = df["won"]
    y_place = df["placed"]

    X_train, X_meta, y_train_win, y_meta_win, y_train_place, y_meta_place = (
        train_test_split(X, y_win, y_place, test_size=0.2, random_state=42)
    )

    print("🚀 Training base models…")
    models = train_base_models(X_train, y_train_win, y_train_place)

    # Generate predictions for meta training
    for key, model in models.items():
        preds = (
            model.predict_proba(X_meta)[:, 1]
            if hasattr(model, "predict_proba")
            else model.predict(X_meta).flatten()
        )
        col = f"confidence_{key}"
        X_meta[col] = preds
        print(f"{col} example: {preds[:3]}")

    meta_features = build_meta_features(X_meta)
    meta_X = pd.concat(
        [meta_features, X_meta[feature_cols].reset_index(drop=True)], axis=1
    )

    print("🚀 Training meta models…")
    meta_win = LogisticRegression(max_iter=1000)
    meta_win.fit(meta_X, y_meta_win)
    meta_place = LogisticRegression(max_iter=1000)
    meta_place.fit(meta_X, y_meta_place)

    final_win = meta_win.predict_proba(meta_X)[:, 1]
    final_place = meta_place.predict_proba(meta_X)[:, 1]
    acc_win = accuracy_score(y_meta_win, final_win > 0.5)
    acc_place = accuracy_score(y_meta_place, final_place > 0.5)
    brier_win = brier_score_loss(y_meta_win, final_win)
    print(f"Meta win accuracy: {acc_win:.3f}, Brier: {brier_win:.3f}")
    print(f"Meta place accuracy: {acc_place:.3f}")
    print(classification_report(y_meta_win, final_win > 0.5, zero_division=0))

    explainer = shap.LinearExplainer(meta_win, meta_X, feature_dependence="independent")
    shap_values = explainer.shap_values(meta_X)
    importance = np.abs(shap_values).mean(axis=0)
    top_features = pd.Series(importance, index=meta_X.columns).sort_values(
        ascending=False
    )[:10]
    print("Top meta-model features:\n", top_features)
    date_str = date.today().isoformat()
    shap_log = Path("logs") / f"shap_top_features_{date_str}.csv"
    shap_log.parent.mkdir(parents=True, exist_ok=True)
    top_df = top_features.reset_index()
    top_df.columns = ["feature", "importance"]
    top_df.to_csv(shap_log, index=False)
    print(f"🔍 SHAP features saved to {shap_log}")

    print("\n📋 Model config summary")
    print(f"Records used: {len(df)}")
    print(f"Features: {feature_cols}")
    print("Top SHAP:")
    print(top_df.head())
    print(f"Meta win acc: {acc_win:.3f} | Brier: {brier_win:.3f}")
    if merged_tips:
        print(f"Merged past tips: {merged_tips}")

    # Save
    out_dir = Path(tempfile.mkdtemp())
    for name, model in models.items():
        if hasattr(model, "save_model"):
            model.save_model(out_dir / f"{name}.cb")
        elif hasattr(model, "save"):
            model.save(out_dir / f"{name}.keras")
        else:
            joblib.dump(model, out_dir / f"{name}.pkl")
    joblib.dump(meta_win, out_dir / "meta-win.pkl")
    joblib.dump(meta_place, out_dir / "meta-place.pkl")
    (out_dir / "features.json").write_text(json.dumps(feature_cols))
    (out_dir / "meta-features.json").write_text(json.dumps(list(meta_X.columns)))
    (out_dir / "shap-top-features.csv").write_text(top_df.to_csv(index=False))
    model_id = {
        "version": "v8",
        "ensemble": ["cat", "xgb", "mlp"],
        "meta": "logreg",
        "timestamp": date_str,
    }
    (out_dir / "model-id.json").write_text(json.dumps(model_id))

    tar_path = Path("models/monster_v8_stack.tar.gz")
    tar_path.parent.mkdir(exist_ok=True)
    with tarfile.open(tar_path, "w:gz") as tar:
        for file in out_dir.iterdir():
            tar.add(file, arcname=file.name)
    print(f"📦 Saved ensemble model to {tar_path}")
    upload_to_s3(tar_path, BUCKET, f"models/{tar_path.name}")


if __name__ == "__main__":
    main()
