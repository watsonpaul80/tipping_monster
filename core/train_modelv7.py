#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import glob
import json
import os
import shutil
import tarfile
import tempfile
from datetime import date

import boto3
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from core.validate_features import validate_dataset_features
from tippingmonster.utils import in_dev_mode, upload_to_s3

BUCKET = "tipping-monster"


def load_all_results(s3_keys):
    s3 = boto3.client("s3")
    paths = []
    for key in s3_keys:
        local_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
        s3.download_file(BUCKET, key, local_path)
        paths.append(local_path)
    dfs = [pd.read_csv(path, low_memory=False) for path in paths]
    return pd.concat(dfs, ignore_index=True)


def merge_tip_logs(base_df, tip_files):
    base_df["was_tipped"] = 0
    base_df["tip_confidence"] = None
    base_df["tip_profit"] = None
    base_df["confidence_band"] = None
    for tip_file in tip_files:
        if not os.path.exists(tip_file):
            continue
        tips = pd.read_csv(tip_file)
        for idx, row in tips.iterrows():
            mask = (
                (base_df["date"].astype(str) == str(row["Date"]))
                & (
                    base_df["course"].astype(str).str.lower()
                    == str(row["Course"]).lower()
                )
                & (
                    base_df["horse"].astype(str).str.lower()
                    == str(row["Horse"]).lower()
                )
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
    return base_df


def preprocess(df):
    df["horse"] = (
        df["horse"]
        .astype(str)
        .str.strip()
        .str.replace(r" \([A-Z]{2,3}\)", "", regex=True)
    )
    df["course"] = df["course"].astype(str).str.strip()
    df["trainer"] = df["trainer"].astype(str).str.strip()
    df["jockey"] = df["jockey"].astype(str).str.strip()
    df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(-1)
    df["or"] = pd.to_numeric(df["or"], errors="coerce").fillna(-1)
    df["lbs"] = pd.to_numeric(df["lbs"], errors="coerce").fillna(-1)
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(-1)
    df["dist_f"] = pd.to_numeric(df["dist_f"], errors="coerce").fillna(-1)
    df["btn"] = pd.to_numeric(df["btn"], errors="coerce").fillna(-1)
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
    print("Distribution of 'won':\n", df["won"].value_counts())
    return df


def train_model(df, feature_cols):
    print(f"\n🧠 Using features: {feature_cols}")
    print(f"📘 Rows before training: {len(df)}")
    missing, extra = validate_dataset_features(feature_cols, df)
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
    if extra:
        print(f"Ignoring extra columns: {extra}")
    df["was_tipped"] = df["was_tipped"].fillna(0).astype(int)
    df["tip_confidence"] = df["tip_confidence"].fillna(0.0)
    df["tip_profit"] = df["tip_profit"].fillna(0.0)
    X = df[feature_cols]
    y = df["won"]
    print("Target label distribution:\n", y.value_counts())
    if y.sum() == 0 or y.sum() == len(y):
        raise ValueError(
            "Error: No class variance in target variable ('won')! Check your data."
        )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"✅ Accuracy: {acc:.4f}")
    print(
        "\n📘 Classification Report:\n"
        + classification_report(y_test, preds, zero_division=0)
    )

    date_str = date.today().isoformat()
    dated_file = f"tipping-monster-xgb-model-{date_str}.bst"
    model.get_booster().save_model(dated_file)
    shutil.copyfile(dated_file, "tipping-monster-xgb-model.bst")
    tar_path = f"tipping-monster-xgb-model-{date_str}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add("tipping-monster-xgb-model.bst")
        with open("features.json", "w", encoding="utf-8") as f:
            json.dump(feature_cols, f)
        tar.add("features.json")
    print(f"📦 Model saved and packaged as {tar_path}")
    upload_to_s3(tar_path, BUCKET, f"models/{tar_path}")
    if not in_dev_mode():
        print(f"✅ Model uploaded to S3: models/{tar_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    s3_keys = [
        "results/gb-flat-2015-2025.csv",
        "results/gb-jumps-2015-2025.csv",
        "results/ire-flat-2015-2025.csv",
        "results/ire-jumps-2015-2025.csv",
    ]
    print("📅 Downloading historical data from S3...")
    df = load_all_results(s3_keys)
    print("🔧 Preprocessing...")
    df = preprocess(df)
    log_base = os.getenv("TM_LOG_DIR", "logs")
    tip_logs = sorted(glob.glob(f"{log_base}/roi/tips_results_*_advised.csv"))
    if tip_logs:
        print(f"📝 Injecting tip logs: {tip_logs[-3:]} ...")
        df = merge_tip_logs(df, tip_logs)
    else:
        print("⚠️ No tip logs found, proceeding without tip enrichment.")
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
        "was_tipped",
        "tip_confidence",
        "tip_profit",
    ]
    print("🚀 Training model...")
    train_model(df, feature_cols)
