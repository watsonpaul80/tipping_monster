import os
import pandas as pd
import argparse
from datetime import datetime, timedelta
import requests

def get_week_dates(iso_week):
    year, week = iso_week.split("-W")
    monday = datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%u")
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def load_week_data(week_dates, mode="advised"):
    rows = []
    for date_str in week_dates:
        path = f"logs/tips_results_{date_str}_{mode}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["Date"] = date_str
            rows.append(df)
    return pd.concat(rows) if rows else pd.DataFrame()

def send_to_telegram(msg, token, chat_id):
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
    )

def main(week, send_telegram=False):
    mode = "advised"
    TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
    CHAT_ID = "-1002580022335"

    week_dates = get_week_dates(week)
    df = load_week_data(week_dates, mode)

    if df.empty:
        print(f"No data for week {week}")
        return

    # Ensure Profit and Stake are numeric before grouping
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)
    df["Stake"] = pd.to_numeric(df["Stake"], errors="coerce").fillna(0)

    tips = len(df)
    wins = (df["Position"] == 1).sum()
    stake = df["Stake"].sum()
    profit = df["Profit"].sum()
    roi = (profit / stake * 100) if stake else 0

    print(f"📅 *Week: {week}*")
    print(f"💰 *Mode: {mode.capitalize()}* → ROI: {roi:.2f}%, Profit: {profit:+.2f} pts ({stake:.2f} staked)")

    # Proper grouped daily summary with safe numeric aggregation
    summary = (
        df.groupby("Date", as_index=False)
          .agg({
              "Horse": "count",
              "Position": lambda x: (x == 1).sum(),
              "Profit": "sum",
              "Stake": "sum"
          })
          .rename(columns={"Horse": "Tips", "Position": "Wins"})
    )
    summary["ROI"] = summary.apply(lambda row: (row.Profit / row.Stake * 100) if row.Stake else 0, axis=1)

    for _, row in summary.iterrows():
        print(f"📆 {row.Date} → Tips: {int(row.Tips)} | Wins: {int(row.Wins)} | Profit: {row.Profit:+.2f} pts | ROI: {row.ROI:.2f}%")

    if send_telegram:
        msg = f"*📊 Weekly ROI Summary ({week}) – {mode.capitalize()}*\n\n"
        msg += f"🏇 Tips: {tips} | 🥇 Wins: {wins}\n💰 Profit: {profit:+.2f} pts | ROI: {roi:.2f}%\n\n"
        for _, row in summary.iterrows():
            msg += f"📆 {row.Date} → {int(row.Tips)} tips, {int(row.Wins)} wins, ROI: {row.ROI:.2f}%\n"
        send_to_telegram(msg, TOKEN, CHAT_ID)
        print("✅ Sent to Telegram")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True)
    parser.add_argument("--telegram", action="store_true")
    args = parser.parse_args()
    main(args.week, send_telegram=args.telegram)

