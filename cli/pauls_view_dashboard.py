#!/usr/bin/env python3
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Paul's View - Tipping Monster", layout="wide")

# === Load CSV ===
uploaded_file = st.file_uploader("Upload _all.csv Tip Log", type="csv")
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)
df["Date"] = pd.to_datetime(df["Date"])

# === Sidebar Filters ===
st.sidebar.header("\U0001f50d Filters")
all_dates = sorted(df["Date"].dt.date.unique())
selected_dates = st.sidebar.multiselect(
    "Date Range", all_dates, default=all_dates[-14:]
)

all_tags = sorted(
    tag for sublist in df["Tags"].dropna().str.split(",") for tag in sublist
)
selected_tags = st.sidebar.multiselect("Tags", all_tags)

min_conf, max_conf = st.sidebar.slider("Confidence Range", 0.0, 1.0, (0.8, 1.0))

only_naps = st.sidebar.checkbox("\U0001f9e0 Only NAPs")
use_best_odds = st.sidebar.radio("Profit Mode", ["Default Odds", "Best Odds"], index=1)

# === Filter Data ===
df_filtered = df[df["Date"].dt.date.isin(selected_dates)]
df_filtered = df_filtered[df_filtered["Confidence"].between(min_conf, max_conf)]
if only_naps:
    df_filtered = df_filtered[df_filtered["Tags"].str.contains("NAP", na=False)]
if selected_tags:
    df_filtered = df_filtered[
        df_filtered["Tags"].apply(lambda x: any(tag in str(x) for tag in selected_tags))
    ]

# === ROI Summary ===
st.subheader("\U0001f4b8 ROI Summary")
profit_col = "Profit Best Odds" if use_best_odds == "Best Odds" else "Profit"

summary = (
    df_filtered.groupby("Date")
    .agg(
        {
            "Profit": "sum",
            "Profit Best Odds": "sum",
            "Stake": "sum",
            "Position": lambda x: (x == 1).sum(),
        }
    )
    .rename(columns={"Position": "Winners"})
)
summary["ROI"] = (summary[profit_col] / summary["Stake"]) * 100

st.dataframe(summary.round(2))

# === Cumulative Profit Chart ===
st.subheader("\U0001f4c8 Cumulative Profit")
cum_profit = df_filtered.groupby("Date")[profit_col].sum().cumsum()
cum_profit.plot(marker="o", grid=True)
st.pyplot(plt.gcf())

# === Breakdown Table ===
st.subheader("\U0001f4cc Full Tip Breakdown")
show_cols = [
    "Date",
    "Time",
    "Race",
    "Horse",
    "Confidence",
    "Tags",
    "Stake",
    "Odds",
    "Profit",
    "Profit Best Odds",
]
st.dataframe(
    df_filtered[show_cols].sort_values(by=["Date", "Time"], ascending=[False, True])
)

# === Best Tracks Summary ===
st.subheader("\U0001f3c3 Best Tracks")
course_stats = (
    df_filtered.groupby("Course")
    .agg(
        {
            "Profit": "sum",
            "Profit Best Odds": "sum",
            "Stake": "sum",
            "Horse": "count",
        }
    )
    .rename(columns={"Horse": "Tips"})
)
course_stats["ROI"] = (course_stats[profit_col] / course_stats["Stake"]) * 100
course_stats = course_stats.sort_values("ROI", ascending=False)
st.dataframe(course_stats.round(2))

# === Flat vs Jumps Summary ===
st.subheader("\U0001f3c7 Flat vs Jumps Performance")
df_filtered["Type"] = df_filtered["Race Type"].fillna("Unknown")
type_stats = (
    df_filtered.groupby("Type")
    .agg(
        {
            "Profit": "sum",
            "Profit Best Odds": "sum",
            "Stake": "sum",
            "Horse": "count",
        }
    )
    .rename(columns={"Horse": "Tips"})
)
type_stats["ROI"] = (type_stats[profit_col] / type_stats["Stake"]) * 100
st.dataframe(type_stats.round(2))

# === Export CSV ===
st.subheader("\U0001f4be Export Filtered Data")
export_buf = BytesIO()
df_filtered.to_csv(export_buf, index=False)
st.download_button(
    "Download CSV",
    data=export_buf.getvalue(),
    file_name="filtered_tips.csv",
    mime="text/csv",
)
