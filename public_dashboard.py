import ast
import glob
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tipping Monster Dashboard", layout="wide")


@st.cache_data
def load_sent_tips() -> pd.DataFrame:
    rows = []
    for path in sorted(glob.glob("logs/tips_results_*_advised_sent.csv")):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        date_str = (
            Path(path).stem.replace("tips_results_", "").replace("_advised_sent", "")
        )
        df["Date"] = pd.to_datetime(date_str)
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    df = pd.concat(rows, ignore_index=True)
    df["Profit"] = pd.to_numeric(df.get("Profit"), errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df.get("Stake"), errors="coerce").fillna(0)
    df["Position"] = df.get("Position").astype(str)
    return df


def parse_tags(val):
    if pd.isna(val):
        return []
    try:
        out = ast.literal_eval(val)
        return out if isinstance(out, list) else []
    except Exception:
        return []


def main() -> None:
    df = load_sent_tips()
    if df.empty:
        st.error("No sent tip data available")
        return

    df.sort_values("Date", inplace=True)

    # === Date Range Selector ===
    all_dates = sorted(df["Date"].dt.date.unique())
    default_start = all_dates[-30] if len(all_dates) >= 30 else all_dates[0]
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        value=(default_start, all_dates[-1]),
        min_value=all_dates[0],
        max_value=all_dates[-1],
    )

    df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

    # === Daily ROI Summary ===
    st.header("Daily ROI")
    daily = (
        df.groupby(df["Date"].dt.date)
        .agg(
            Tips=("Horse", "count"),
            Winners=("Position", lambda x: (x == "1").sum()),
            Profit=("Profit", "sum"),
            Stake=("Stake", "sum"),
        )
        .reset_index()
    )
    daily["ROI %"] = daily.apply(
        lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
    )
    st.dataframe(daily.round(2))

    # === Weekly ROI Summary ===
    st.header("Weekly ROI")
    df["Week"] = df["Date"].dt.strftime("%G-W%V")
    weekly = (
        df.groupby("Week")
        .agg(Tips=("Horse", "count"), Profit=("Profit", "sum"), Stake=("Stake", "sum"))
        .reset_index()
    )
    weekly["ROI %"] = weekly.apply(
        lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
    )
    st.dataframe(weekly.round(2))

    # === Cumulative Profit Chart ===
    st.header("Profit Chart")
    daily_profit = df.groupby(df["Date"].dt.date)["Profit"].sum()
    cum_profit = daily_profit.cumsum()
    st.line_chart(cum_profit)

    # === Emoji Stats ===
    st.header("Emoji Stats")
    tag_df = df.dropna(subset=["tags"]).copy()
    tag_df["Tag"] = tag_df["tags"].apply(parse_tags)
    tag_df = tag_df.explode("Tag")
    tag_df["Emoji"] = tag_df["Tag"].str.extract(r"(\X)")
    emoji_counts = tag_df["Emoji"].value_counts().reset_index()
    emoji_counts.columns = ["Emoji", "Count"]
    st.dataframe(emoji_counts)

    # === ROI by Tag ===
    st.header("ROI by Tag")
    if not tag_df.empty:
        tag_stats = tag_df.groupby("Tag").agg(
            Tips=("Profit", "count"),
            Profit=("Profit", "sum"),
            Stake=("Stake", "sum"),
        )
        tag_stats["ROI %"] = tag_stats.apply(
            lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
        )
        st.dataframe(tag_stats.sort_values("ROI %", ascending=False).round(2))
    else:
        st.write("No tag data available")


if __name__ == "__main__":
    main()
