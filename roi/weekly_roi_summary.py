#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import requests  # noqa: F401
from dotenv import load_dotenv

load_dotenv()

from roi_by_confidence_band import assign_band
from tippingmonster.env_loader import load_env
from tippingmonster.utils import logs_path, send_telegram_message

load_env()

BANKROLL_FILE = logs_path("roi", "bankroll_tracker.csv")


def load_bankroll() -> pd.DataFrame:
    if os.path.exists(BANKROLL_FILE):
        return pd.read_csv(BANKROLL_FILE)
    return pd.DataFrame(
        columns=[
            "Date",
            "Profit",
            "Stake",
            "Bankroll",
            "Peak",
            "Drawdown",
            "WorstDrawdown",
        ]
    )


def get_week_dates(iso_week):
    year, week = iso_week.split("-W")
    monday = datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%u")
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


def summarise_bands(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Confidence"] = pd.to_numeric(df.get("Confidence"), errors="coerce")
    df["Profit"] = pd.to_numeric(df.get("Profit"), errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df.get("Stake"), errors="coerce").fillna(0)
    df["Band"] = df["Confidence"].apply(assign_band)
    df = df.dropna(subset=["Band"])
    if df.empty:
        return pd.DataFrame()
    summary = (
        df.groupby("Band")
        .apply(
            lambda g: pd.Series(
                {
                    "Tips": len(g),
                    "Wins": (g["Position"].astype(str) == "1").sum(),
                    "Stake": g["Stake"].sum(),
                    "Profit": g["Profit"].sum(),
                }
            )
        )
        .reset_index()
    )
    summary["ROI"] = summary.apply(
        lambda r: (r.Profit / r.Stake * 100) if r.Stake else 0, axis=1
    )
    return summary.sort_values("Band")


def generate_commentary_block(summary: pd.DataFrame) -> str:
    """Return commentary lines for the weekly summary."""
    if summary.empty:
        return ""

    top = summary.loc[summary["ROI"].idxmax()]
    worst = summary.loc[summary["ROI"].idxmin()]
    positives = (summary["Profit"] > 0).sum()
    negatives = (summary["Profit"] < 0).sum()
    trend = "rising" if positives >= negatives else "falling"

    lines = [
        f"Top performer: {top.Date} ({top.ROI:.2f}% ROI, {top.Profit:+.2f} pts)",
        f"Worst day: {worst.Date} ({worst.ROI:.2f}% ROI, {worst.Profit:+.2f} pts)",
        f"Overall trend: {trend}",
    ]
    return "\n".join(lines)


def plot_roi_trend(summary: pd.DataFrame, week: str) -> None:
    """Save a line chart of ROI per day for ``week``."""
    if summary.empty:
        return

    summary = summary.sort_values("Date")
    plt.figure(figsize=(8, 4))
    plt.plot(summary["Date"], summary["ROI"], marker="o")
    plt.xlabel("Date")
    plt.ylabel("ROI (%)")
    plt.title(f"ROI Trend {week}")
    plt.xticks(rotation=45)
    out_path = logs_path("roi", f"roi_trend_{week}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Saved ROI trend chart to {out_path}")


def load_week_data(week_dates, mode="advised"):
    rows = []
    for date_str in week_dates:
        path = f"logs/roi/tips_results_{date_str}_{mode}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["Date"] = date_str
            rows.append(df)
    return pd.concat(rows) if rows else pd.DataFrame()


def send_to_telegram(msg, token, chat_id):
    send_telegram_message(msg, token=token, chat_id=chat_id)


def main(week, send_telegram=False):
    mode = "advised"
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    week_dates = get_week_dates(week)
    df = load_week_data(week_dates, mode)

    if df.empty:
        print(f"No data for week {week}")
        return

    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df["Stake"], errors="coerce").fillna(0)

    def is_win(pos):
        return str(pos).isdigit() and int(pos) == 1

    def is_place(pos):
        return str(pos).isdigit() and 2 <= int(pos) <= 4

    tips = len(df)
    wins = df["Position"].apply(is_win).sum()
    places = df["Position"].apply(is_place).sum()
    stake = df["Stake"].sum()
    profit = df["Profit"].sum()
    roi = (profit / stake * 100) if stake else 0
    strike_rate = (wins / tips * 100) if tips else 0
    place_rate = (places / tips * 100) if tips else 0

    bank_df = load_bankroll()
    if bank_df.empty:
        bankroll = 0.0
        worst_dd = 0.0
    else:
        bankroll = float(bank_df["Bankroll"].iloc[-1])
        worst_dd = float(bank_df["WorstDrawdown"].iloc[-1])

    print(
        f"\n📅 *Week: {week}*\n💰 *Mode: {mode.capitalize()}* → "
        f"ROI: {roi:.2f}%, Profit: {profit:+.2f} pts ({stake:.2f} staked)\n"
        f"Bankroll: {bankroll:+.2f} | Worst DD: {worst_dd:.2f}"
    )

    summary = (
        df.groupby("Date", as_index=False)
        .agg({"Horse": "count", "Position": list, "Profit": "sum", "Stake": "sum"})
        .rename(columns={"Horse": "Tips"})
    )

    summary["Wins"] = summary["Position"].apply(
        lambda x: sum(1 for p in x if str(p).isdigit() and int(p) == 1)
    )
    summary["Places"] = summary["Position"].apply(
        lambda x: sum(1 for p in x if str(p).isdigit() and 2 <= int(p) <= 4)
    )
    summary.drop(columns="Position", inplace=True)
    summary["ROI"] = summary.apply(
        lambda row: (row.Profit / row.Stake * 100) if row.Stake else 0, axis=1
    )

    for _, row in summary.iterrows():
        print(
            f"📆 {row.Date} → Tips: {int(row.Tips)} | 🥇 Wins: {int(row.Wins)} "
            f"| 🥈 Places: {int(row.Places)} | Profit: {row.Profit:+.2f} pts "
            f"| ROI: {row.ROI:.2f}%"
        )

    plot_roi_trend(summary, week)

    band_summary = summarise_bands(df)
    band_path = logs_path("roi", f"band_summary_{week}.csv")
    if not band_summary.empty:
        band_summary.to_csv(band_path, index=False)

        best_band = band_summary.loc[band_summary["ROI"].idxmax(), "Band"]
        worst_band = band_summary.loc[band_summary["ROI"].idxmin(), "Band"]

        for _, row in band_summary.iterrows():
            emoji = ""
            if row.Band == best_band:
                emoji = " 🏆"
            elif row.Band == worst_band:
                emoji = " 🐌"
            print(
                f"🔹 {row.Band} → {int(row.Tips)} tips, {int(row.Wins)}W, "
                f"Profit: {row.Profit:+.2f} pts | ROI: {row.ROI:.2f}%{emoji}"
            )
    else:
        best_band = worst_band = None

    commentary = generate_commentary_block(summary)
    if commentary:
        com_path = logs_path("roi", f"summary_commentary_{week}.txt")
        with open(com_path, "w", encoding="utf-8") as f:
            f.write(commentary + "\n")
        print(f"📝 Saved commentary to {com_path}")

    if send_telegram:
        msg = (
            f"*📊 Weekly ROI Summary ({week}) – {mode.capitalize()}*\n\n"
            f"🏇 Tips: {tips}  |  🟢 {wins}W  |  🟡 {places}P  |  "
            f"🔴 {tips - wins - places}L\n"
            f"🎯 Strike Rate: {strike_rate:.2f}% | 🥈 Place Rate: {place_rate:.2f}%\n"
            f"💰 Profit: {profit:+.2f} pts\n"
            f"📈 ROI: {roi:.2f}%\n"
            f"💰 Bankroll: {bankroll:+.2f} pts\n"
            f"🔻 Worst DD: {worst_dd:.2f} pts\n"
            f"🪙 Staked: {stake:.2f} pts\n"
        )
        for _, row in summary.iterrows():
            msg += (
                f"\n📆 {row.Date} → {int(row.Tips)} tips, "
                f"🟢 {int(row.Wins)}W, 🟡 {int(row.Places)}P, "
                f"ROI: {row.ROI:.2f}%"
            )
        if not band_summary.empty:
            msg += "\n\n*By Confidence Band*"
            for _, row in band_summary.iterrows():
                emoji = ""
                if row.Band == best_band:
                    emoji = " 🏆"
                elif row.Band == worst_band:
                    emoji = " 🐌"
                msg += (
                    f"\n{row.Band} → {int(row.Tips)} tips, {int(row.Wins)}W, "
                    f"ROI: {row.ROI:.2f}%{emoji}"
                )
        send_to_telegram(msg, TOKEN, CHAT_ID)
        print("✅ Sent to Telegram")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()
    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"
    main(args.week, send_telegram=args.telegram)
