#!/usr/bin/env python3
import json
import os
from datetime import timedelta

import boto3
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()


def get_confidence_band(conf: float) -> str | None:
    """Return the confidence band label for `conf`."""
    bins = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.00),
        (0.99, 1.01),
    ]
    for low, high in bins:
        if low <= conf < high:
            return f"{low:.2f}\u2013{high:.2f}"
    return None


def load_recent_roi_stats(path: str, ref_date: str, window: int = 30) -> dict:
    """Return ROI per confidence bin for `window` days up to `ref_date`."""
    if not os.path.exists(path):
        return {}

    df_roi = pd.read_csv(path)
    if df_roi.empty:
        return {}

    df_roi["Date"] = pd.to_datetime(df_roi["Date"], errors="coerce")
    df_roi["Win PnL"] = pd.to_numeric(df_roi["Win PnL"], errors="coerce").fillna(0)
    df_roi["Tips"] = pd.to_numeric(df_roi["Tips"], errors="coerce").fillna(0)

    ref = pd.to_datetime(ref_date)
    start = ref - timedelta(days=window)
    df_roi = df_roi[(df_roi["Date"] >= start) & (df_roi["Date"] <= ref)]

    roi = {}
    for band, grp in df_roi.groupby("Confidence Bin"):
        tips = grp["Tips"].sum()
        pnl = grp["Win PnL"].sum()
        roi[band] = pnl / tips if tips else 0.0
    return roi


def load_sent_confidence(date_str: str) -> dict:
    """Return mapping of (course, time, horse) to confidence for a date."""
    path = f"logs/sent_tips_{date_str}.jsonl"
    conf_map = {}
    if not os.path.exists(path):
        return conf_map
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                tip = json.loads(line)
                race = tip.get("race", "")
                if " " not in race:
                    continue
                time_str, course = race.split(" ", 1)
                horse = str(tip.get("name", "")).strip().lower()
                key = (course.strip().lower(), time_str.lstrip("0"), horse)
                conf_map[key] = float(tip.get("confidence", 0.0))
            except Exception:
                continue
    return conf_map


st.set_page_config(page_title="Tipping Monster P&L", layout="wide")

# === AWS S3 SETTINGS ===
# It's good practice to get these from Streamlit secrets or environment variables directly in Streamlit Cloud
# For local development, .env is fine.
bucket = os.getenv("S3_BUCKET")
key = os.getenv("S3_OBJECT")

# Download from S3 into local file
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)

try:
    s3.download_file(bucket, key, "master_subscriber_log.csv")
    df = pd.read_csv("master_subscriber_log.csv")
except NoCredentialsError:
    st.error("❌ AWS credentials missing or invalid.")
    st.stop()
except ClientError as e:
    st.error(f"❌ Could not download file from S3: {e}")
    st.stop()

# === CLEAN + FILTER ===
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

roi_map = load_recent_roi_stats(
    "monster_confidence_per_day_with_roi.csv",
    df["Date"].max().strftime("%Y-%m-%d"),
    30,
)
positive_bins = {band for band, val in roi_map.items() if val > 0}


def attach_confidence(row):
    date_str = row["Date"].date().isoformat()
    if date_str not in st.session_state.confidence_cache:
        st.session_state.confidence_cache[date_str] = load_sent_confidence(date_str)
    key = (
        str(row["Meeting"]).strip().lower(),
        str(row["Time"]).lstrip("0"),
        str(row["Horse"]).strip().lower(),
    )
    return st.session_state.confidence_cache[date_str].get(key)


# Initialize confidence_cache in Streamlit's session state
if 'confidence_cache' not in st.session_state:
    st.session_state.confidence_cache = {}

# Sidebar filters
st.sidebar.header("🔎 Filters")
all_dates = sorted(df["Date"].dt.date.unique())
selected_dates = st.sidebar.multiselect("Date Range", all_dates, default=all_dates[-7:])
filtered = df[df["Date"].dt.date.isin(selected_dates)]

# Apply "Positive ROI Bands Only" filter if checked
if st.sidebar.checkbox("Positive ROI Bands Only"):
    # Ensure confidence is attached only if this filter is active
    filtered = filtered.copy()
    filtered["Confidence"] = filtered.apply(attach_confidence, axis=1)
    filtered["Band"] = filtered["Confidence"].apply(get_confidence_band)
    filtered = filtered[filtered["Band"].isin(positive_bins)]

# Optional sidebar filters for the table view
show_winners_only = st.sidebar.checkbox("Show Winners Only")
show_placed_only = st.sidebar.checkbox("Show Placed Only")

# Summary Metrics
st.subheader("📦 Summary Stats")
total_tips = len(filtered)
winners = (filtered["Result"] == "1").sum()
profit = round(filtered["Profit"].sum(), 2)
best_profit = (
    round(filtered["Running Profit Best Odds"].iloc[-1], 2) if not filtered.empty else 0
)
stake_total = filtered["Stake"].sum()
roi = (profit / stake_total * 100) if stake_total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tips", total_tips)
col2.metric("Winners", winners)
col3.metric("Profit (pts)", profit)
col4.metric("ROI %", f"{roi:.2f}%")

# Line Chart – Running Profit
df_plot = filtered.groupby("Date")["Running Profit"].max().reset_index()
df_plot["Date"] = pd.to_datetime(df_plot["Date"])

st.subheader("📈 Cumulative Profit Over Time")
fig, ax = plt.subplots()
ax.plot(df_plot["Date"], df_plot["Running Profit"], marker="o", label="Standard Odds")
ax.set_xlabel("Date")
ax.set_ylabel("Profit (pts)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Table View
st.subheader("📋 Tips Breakdown")

# Apply optional filters for winners or placed horses for the table display
table_df = filtered.copy()
if show_winners_only:
    table_df = table_df[table_df["Result"] == "1"]
elif show_placed_only:
    # Assuming "Placed" means 1st, 2nd, or 3rd. Adjust if "Placed" has a specific result code.
    table_df = table_df[table_df["Result"].isin(["1", "2", "3"])]

st.dataframe(table_df.sort_values(by=["Date", "Time"], ascending=[False, True]))