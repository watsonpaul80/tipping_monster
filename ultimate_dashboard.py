import ast
import glob
from pathlib import Path

import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Ultimate Dashboard", layout="wide")


@st.cache_data
def load_tip_results(sent_only: bool) -> pd.DataFrame:
    """Load tip result CSVs into a dataframe."""
    pattern = (
        "logs/tips_results_*_advised_sent.csv"
        if sent_only
        else "logs/tips_results_*_advised*.csv"
    )
    rows = []
    for path in sorted(glob.glob(pattern)):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        date_str = Path(path).stem.split("_")[1]
        df["Date"] = pd.to_datetime(date_str)
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    df = pd.concat(rows, ignore_index=True)
    df["Profit"] = pd.to_numeric(df.get("Profit"), errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df.get("Stake"), errors="coerce").fillna(0)
    if "confidence" in df.columns:
        df["Confidence"] = pd.to_numeric(df.get("confidence"), errors="coerce").fillna(
            0
        )
    df["Position"] = df.get("Position").astype(str)
    return df


@st.cache_data
def load_confidence_roi() -> pd.DataFrame:
    path = Path("monster_confidence_per_day_with_roi.csv")
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


@st.cache_data
def parse_tags(val: str) -> list[str]:
    if pd.isna(val):
        return []
    try:
        out = ast.literal_eval(val)
        return out if isinstance(out, list) else []
    except Exception:
        return []


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    all_tags = (
        sorted({tag for tags in df["tags"].dropna().apply(parse_tags) for tag in tags})
        if "tags" in df.columns
        else []
    )
    trainers = (
        sorted(df["Trainer"].dropna().unique()) if "Trainer" in df.columns else []
    )
    courses = sorted(df["Course"].dropna().unique()) if "Course" in df.columns else []
    horses = sorted(df["Horse"].dropna().unique()) if "Horse" in df.columns else []
    dates = sorted(df["Date"].dt.date.unique())
    weekdays = sorted(df["Date"].dt.day_name().unique())

    st.sidebar.header("\U0001f50d Filters")
    sel_dates = st.sidebar.multiselect("Dates", dates, default=dates[-30:])
    sel_tags = st.sidebar.multiselect("Tags", all_tags)
    conf_min, conf_max = st.sidebar.slider("Confidence", 0.0, 1.0, (0.0, 1.0))
    tip_type = st.sidebar.selectbox("Tip Type", ["All", "Win", "EW"])
    sel_trainers = st.sidebar.multiselect("Trainers", trainers)
    sel_courses = st.sidebar.multiselect("Tracks", courses)
    sel_horses = st.sidebar.multiselect("Horses", horses)
    sel_weekdays = st.sidebar.multiselect("Day of Week", weekdays, default=weekdays)

    df_filt = df[df["Date"].dt.date.isin(sel_dates)] if sel_dates else df
    if "Confidence" in df_filt.columns:
        df_filt = df_filt[df_filt["Confidence"].between(conf_min, conf_max)]
    if sel_tags and "tags" in df_filt.columns:
        df_filt = df_filt[
            df_filt["tags"].apply(lambda x: any(t in parse_tags(x) for t in sel_tags))
        ]
    if tip_type != "All" and "EW/Win" in df_filt.columns:
        df_filt = df_filt[df_filt["EW/Win"] == tip_type]
    if sel_trainers and "Trainer" in df_filt.columns:
        df_filt = df_filt[df_filt["Trainer"].isin(sel_trainers)]
    if sel_courses and "Course" in df_filt.columns:
        df_filt = df_filt[df_filt["Course"].isin(sel_courses)]
    if sel_horses and "Horse" in df_filt.columns:
        df_filt = df_filt[df_filt["Horse"].isin(sel_horses)]
    if sel_weekdays:
        df_filt = df_filt[df_filt["Date"].dt.day_name().isin(sel_weekdays)]
    return df_filt


def summary_header(df: pd.DataFrame) -> None:
    profit = df["Profit"].sum()
    stake = df["Stake"].sum()
    pnl = profit
    roi = (profit / stake * 100) if stake else 0
    winners = (df["Position"] == "1").sum()
    placed = df["Position"].isin(["1", "2", "3"]).sum()
    total = len(df)
    win_pct = (winners / total * 100) if total else 0
    place_pct = (placed / total * 100) if total else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cumulative PnL", f"{pnl:.2f}")
    col2.metric("Win %", f"{win_pct:.1f}%")
    col3.metric("Place %", f"{place_pct:.1f}%")
    col4.metric("ROI %", f"{roi:.1f}%")


def roi_trends(df: pd.DataFrame) -> None:
    st.subheader("Daily ROI")
    daily = df.groupby(df["Date"].dt.date).agg(
        Profit=("Profit", "sum"), Stake=("Stake", "sum")
    )
    daily["ROI"] = (daily["Profit"] / daily["Stake"] * 100).fillna(0)
    st.line_chart(daily["ROI"])

    st.subheader("Weekly ROI")
    weekly = df.groupby(df["Date"].dt.to_period("W")).agg(
        Profit=("Profit", "sum"), Stake=("Stake", "sum")
    )
    weekly["ROI"] = (weekly["Profit"] / weekly["Stake"] * 100).fillna(0)
    st.bar_chart(weekly["ROI"])

    st.subheader("Monthly ROI")
    monthly = df.groupby(df["Date"].dt.to_period("M")).agg(
        Profit=("Profit", "sum"), Stake=("Stake", "sum")
    )
    monthly["ROI"] = (monthly["Profit"] / monthly["Stake"] * 100).fillna(0)
    st.line_chart(monthly["ROI"])


def confidence_heatmap(df_conf: pd.DataFrame) -> None:
    if df_conf.empty:
        st.write("No confidence ROI data available")
        return
    pivot = df_conf.pivot(index="Date", columns="Confidence Bin", values="Win ROI %")
    fig = sns.heatmap(pivot, cmap="RdYlGn", center=0)
    st.pyplot(fig.figure)


def tag_breakdown(df: pd.DataFrame) -> None:
    if "tags" not in df.columns:
        st.write("No tag data available")
        return
    tag_df = df.dropna(subset=["tags"]).copy()
    tag_df["Tag"] = tag_df["tags"].apply(parse_tags)
    tag_df = tag_df.explode("Tag")
    tag_stats = tag_df.groupby("Tag").agg(
        Profit=("Profit", "sum"), Stake=("Stake", "sum"), Tips=("Horse", "count")
    )
    tag_stats["ROI %"] = (tag_stats["Profit"] / tag_stats["Stake"] * 100).fillna(0)
    st.dataframe(tag_stats.sort_values("ROI %", ascending=False).round(2))


def top_winners(df: pd.DataFrame) -> None:
    winners = df[df["Position"] == "1"].copy()
    if winners.empty:
        st.write("No winners available")
        return

    cols = [
        c
        for c in ["Date", "Horse", "bf_sp", "confidence", "Profit"]
        if c in winners.columns
    ]

    by_profit = winners.sort_values("Profit", ascending=False)[cols].head(10)
    by_conf = winners.sort_values("confidence", ascending=False)[cols].head(10)
    by_odds = winners.sort_values("bf_sp", ascending=False)[cols].head(10)

    col1, col2, col3 = st.columns(3)
    col1.subheader("By Profit")
    col1.table(by_profit)

    col2.subheader("By Confidence")
    col2.table(by_conf)

    col3.subheader("By Odds")
    col3.table(by_odds)


def tips_table(df: pd.DataFrame) -> None:
    st.subheader("All Tips")
    if df.empty:
        st.write("No data")
        return
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_tips.csv", "text/csv")


def main() -> None:
    mode = st.sidebar.radio("Mode", ["Premium", "Public"])
    sent_only = mode == "Public"
    df = load_tip_results(sent_only=sent_only)
    if df.empty:
        st.error("No tip data found")
        return
    df_conf = load_confidence_roi()
    df_filtered = filter_dataframe(df)

    st.title("\U0001f3c6 Ultimate Tipping Monster Dashboard")
    summary_header(df_filtered)
    roi_trends(df_filtered)
    st.subheader("Confidence ROI Heatmap")
    confidence_heatmap(df_conf)
    st.subheader("Tag Profitability")
    tag_breakdown(df_filtered)
    st.subheader("Top Winners")
    top_winners(df_filtered)
    tips_table(df_filtered)


if __name__ == "__main__":
    main()
