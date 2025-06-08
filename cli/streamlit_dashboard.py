#!/usr/bin/env python3
import os

import boto3
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Tipping Monster P&L", layout="wide")


def calc_win_profit(row: pd.Series) -> float:
    """Return profit for a win-only bet based on SP."""
    if str(row.get("Result")) == "NR":
        return 0.0
    stake = row.get("Stake", 1.0)
    sp = float(row.get("SP", 0.0))
    return round((sp - 1) * stake if str(row.get("Result")) == "1" else -stake, 2)


def calc_ew_profit(row: pd.Series) -> float:
    """Return profit for an each-way bet assuming 1/5 odds, 3 places."""
    if str(row.get("Result")) == "NR":
        return 0.0
    sp = float(row.get("SP", 0.0))
    result = str(row.get("Result"))
    win_part = (sp - 1) * 0.5 if result == "1" else 0.0
    place_part = (
        ((sp * 0.2) - 1) * 0.5 if result.isdigit() and int(result) <= 3 else -0.5
    )
    return round(win_part + place_part, 2)


# === AWS S3 SETTINGS ===
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
    st.error("\u274c AWS credentials missing or invalid.")
    st.stop()
except ClientError as e:
    st.error(f"\u274c Could not download file from S3: {e}")
    st.stop()

df["Profit Win"] = df.apply(calc_win_profit, axis=1)
df["Profit EW"] = df.apply(calc_ew_profit, axis=1)
df["Running Profit Win"] = df["Profit Win"].cumsum()
df["Running Profit EW"] = df["Profit EW"].cumsum()

# === CLEAN + FILTER ===
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Sidebar filters
st.sidebar.header("\ud83d\udd0d Filters")
all_dates = sorted(df["Date"].dt.date.unique())
selected_dates = st.sidebar.multiselect("Date Range", all_dates, default=all_dates[-7:])
roi_view = st.sidebar.radio("ROI View", ("Win Only", "Each-Way"))
filtered = df[df["Date"].dt.date.isin(selected_dates)]

# Summary Metrics
st.subheader("\ud83d\udcbe Summary Stats")
total_tips = len(filtered)
winners = (filtered["Result"] == "1").sum()
profit_col = "Profit Win" if roi_view == "Win Only" else "Profit EW"
run_col = "Running Profit Win" if roi_view == "Win Only" else "Running Profit EW"
profit = round(filtered[profit_col].sum(), 2)
best_profit = round(filtered[run_col].iloc[-1], 2) if not filtered.empty else 0
stake_total = filtered["Stake"].sum()
roi = (profit / stake_total * 100) if stake_total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tips", total_tips)
col2.metric("Winners", winners)
col3.metric("Profit (pts)", profit)
col4.metric("ROI %", f"{roi:.2f}%")

# Line Chart – Running Profit
df_plot = filtered.groupby("Date")[run_col].max().reset_index()
df_plot["Date"] = pd.to_datetime(df_plot["Date"])

st.subheader("\ud83d\udcca Cumulative Profit Over Time")
fig, ax = plt.subplots()
ax.plot(df_plot["Date"], df_plot[run_col], marker="o", label=roi_view)
ax.set_xlabel("Date")
ax.set_ylabel("Profit (pts)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Table View
st.subheader("\ud83d\udcc4 Tips Breakdown")
show_cols = [
    "Date",
    "Time",
    "Horse",
    "EW/Win",
    profit_col,
    "Result",
]
st.dataframe(
    filtered.sort_values(by=["Date", "Time"], ascending=[False, True])[show_cols]
)
