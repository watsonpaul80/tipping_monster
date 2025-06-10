#!/usr/bin/env python3

# --- Standard Library ---
import argparse
import glob
import json
import os
import sys
import tarfile
import tempfile
from datetime import date, datetime
from pathlib import Path

# --- Third-Party Libraries ---
import numpy as np
import orjson
import pandas as pd
import xgboost as xgb

from tippingmonster.utils import upload_to_s3

# --- Local Modules ---
sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.model_fetcher import download_if_missing
from tippingmonster.env_loader import load_env

# --- Load Environment Variables ---
load_env()

# === ARGUMENT PARSING ===
models = sorted(glob.glob("tipping-monster-xgb-model-*.tar.gz"))
if not models:
    raise FileNotFoundError(
        "No model tarball found. Download one from S3 or run training."
    )
latest_model = models[-1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--model", default=latest_model, help="Path to model .tar.gz (S3-relative or local)"
)
parser.add_argument("--input", default=None, help="Path to input JSONL")
parser.add_argument("--dev", action="store_true", help="Enable dev mode")
args = parser.parse_args()

if args.dev:
    os.environ["TM_DEV_MODE"] = "1"

# === PATHS ===
date_str = date.today().isoformat()
input_path = args.input or f"rpscrape/batch_inputs/{date_str}.jsonl"
output_path = f"predictions/{date_str}/output.jsonl"
os.makedirs(f"predictions/{date_str}", exist_ok=True)

model_arg = args.model
bucket = "tipping-monster"

# === DOWNLOAD MODEL FROM S3 IF MISSING ===
if os.path.exists(model_arg):
    model_path = model_arg
else:
    local_model_file = os.path.basename(model_arg)
    download_if_missing(bucket, model_arg, local_model_file)
    model_path = local_model_file

# === EXTRACT MODEL TAR ===
model_dir = tempfile.mkdtemp()
with tarfile.open(model_path, "r:gz") as tar:
    tar.extractall(model_dir)

model_file = os.path.join(model_dir, "tipping-monster-xgb-model.bst")
features_file = os.path.join(model_dir, "features.json")

# === LOAD MODEL ===
model = xgb.XGBClassifier()
model.load_model(model_file)

# === LOAD INPUT DATA ===
with open(input_path) as f:
    rows = [json.loads(line) for line in f]
df = pd.DataFrame(rows)

# === VALIDATE FEATURES ===
model_features = list(df.columns)  # Fallback if no features.json
if os.path.exists(features_file):
    with open(features_file) as f:
        model_features = json.load(f)

missing = [f for f in model_features if f not in df.columns]
if missing:
    print(f"❌ Feature mismatch. Missing: {missing}")
    exit(1)

X = df[model_features]
X = X.apply(pd.to_numeric, errors="coerce").fillna(-1)

# === RUN PREDICTIONS ===
df["confidence"] = model.predict_proba(X)[:, 1]
top_tips = df.sort_values("confidence", ascending=False).groupby("race").head(1)


# === SORT BY RACE TIME ===
def extract_race_sort_key(race):
    try:
        time_str, course = race.split(maxsplit=1)
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 9999


top_tips["sort_key"] = top_tips["race"].apply(extract_race_sort_key)
top_tips = top_tips.sort_values("sort_key").drop(columns="sort_key")


# === COMMENTARY GENERATOR ===
def generate_reason(tip):
    reason = []
    try:
        if float(tip.get("trainer_rtf", 0)) >= 25:
            reason.append("yard in form")
    except:
        pass
    try:
        days = float(tip.get("days_since_run", 999))
        if 7 <= days <= 14:
            reason.append("fresh off a short break")
        elif days > 180:
            reason.append("returning from a layoff")
    except:
        pass
    try:
        if float(tip.get("last_class", -1)) > float(tip.get("class", -1)):
            reason.append("down in class")
    except:
        pass
    try:
        form = float(tip.get("form_score", 0))
        if form >= 20:
            reason.append("strong recent form")
    except:
        pass
    try:
        draw = int(tip.get("draw", -1))
        distance = float(tip.get("dist_f", 99))
        draw_bias = float(tip.get("draw_bias_rank", 1.0))
        if draw > 0 and distance <= 16 and draw_bias < 0.4:
            reason.append("good draw position")
        if draw_bias > 0.7:
            reason.append("draw advantage")
    except:
        pass
    if reason:
        return "✍️ " + ", ".join(reason) + "."
    else:
        return "💬 Monster likes it — data suggests an edge."


# === TAG GENERATOR ===
def generate_tags(tip):
    tags = []
    try:
        rtf = float(tip.get("trainer_rtf", 0))
        if rtf >= 20:
            tags.append(f"🔥 Trainer {int(rtf)}%")
    except:
        pass
    try:
        if float(tip.get("last_class", -1)) > float(tip.get("class", -1)):
            tags.append("🟢 Class Drop")
    except:
        pass
    try:
        days = float(tip.get("days_since_run", 999))
        if 7 <= days <= 14:
            tags.append("⚡ Fresh")
        elif days > 180:
            tags.append("🚫 Layoff")
    except:
        pass
    try:
        if float(tip.get("lbs", 999)) < 135:
            tags.append("⚖️ Light Weight")
    except:
        pass
    try:
        if float(tip.get("form_score", 0)) >= 20:
            tags.append("📈 In Form")
    except:
        pass
    try:
        if float(tip.get("draw_bias_rank", 0)) > 0.7:
            tags.append("📊 Draw Advantage")
    except:
        pass
    tip_conf = tip.get("confidence", 0)
    global_max_conf = tip.get("global_max_confidence", 0)
    if tip_conf == global_max_conf:
        tags.append("🧠 Monster NAP")
    if tip_conf >= 0.90:
        tags.append("❗ Confidence 90%+")
    return tags


# === JSON SAFE CONVERSION ===
def make_json_safe(obj):
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    else:
        return obj


# === LAST CLASS LOGIC ===


def load_combined_results():
    master_paths = glob.glob("rpscrape/data/regions/gb/*/2015-2025.csv") + glob.glob(
        "rpscrape/data/regions/ire/*/2015-2025.csv"
    )
    master_frames = []
    for path in master_paths:
        try:
            df = pd.read_csv(
                path,
                usecols=["date", "course", "off", "class", "horse"],
                parse_dates=["date"],
            )
            master_frames.append(df)
        except:
            continue
    recent_paths = glob.glob("rpscrape/data/dates/all/*.csv")
    recent_frames = []
    for path in recent_paths:
        try:
            df = pd.read_csv(
                path,
                usecols=["date",