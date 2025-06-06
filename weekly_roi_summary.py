import os
import pandas as pd
import argparse
from datetime import datetime, timedelta

from tippingmonster import send_telegram_message

def get_week_dates(iso_week):
    year, week = iso_week.split("-W")
    monday = datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%u")
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def load_week_data(week_dates, mode="advised"):
    rows = []
    for date_str in week_dates:
        path = f"logs/roi/tips_results_{date_str}_{mode}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["Date"] = date_str
            rows.append(df)
    return pd.concat(rows) if rows else pd.DataFrame()


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

    print(f"\n📅 *Week: {week}*\n💰 *Mode: {mode.capitalize()}* → ROI: {roi:.2f}%, Profit: {profit:+.2f} pts ({stake:.2f} staked)")

    summary = (
        df.groupby("Date", as_index=False)
          .agg({
              "Horse": "count",
              "Position": list,
              "Profit": "sum",
              "Stake": "sum"
          })
          .rename(columns={"Horse": "Tips"})
    )

    summary["Wins"] = summary["Position"].apply(lambda x: sum(1 for p in x if str(p).isdigit() and int(p) == 1))
    summary["Places"] = summary["Position"].apply(lambda x: sum(1 for p in x if str(p).isdigit() and 2 <= int(p) <= 4))
    summary.drop(columns="Position", inplace=True)
    summary["ROI"] = summary.apply(lambda row: (row.Profit / row.Stake * 100) if row.Stake else 0, axis=1)

    for _, row in summary.iterrows():
        print(f"📆 {row.Date} → Tips: {int(row.Tips)} | 🥇 Wins: {int(row.Wins)} | 🥈 Places: {int(row.Places)} | Profit: {row.Profit:+.2f} pts | ROI: {row.ROI:.2f}%")

    if send_telegram:
        msg = f"""*📊 Weekly ROI Summary ({week}) – {mode.capitalize()}*

🏇 Tips: {tips}  |  🟢 {wins}W  |  🟡 {places}P  |  🔴 {tips - wins - places}L
🎯 Strike Rate: {strike_rate:.2f}% | 🥈 Place Rate: {place_rate:.2f}%
💰 Profit: {profit:+.2f} pts
📈 ROI: {roi:.2f}%
🪙 Staked: {stake:.2f} pts\n"""
        for _, row in summary.iterrows():
            msg += f"\n📆 {row.Date} → {int(row.Tips)} tips, 🟢 {int(row.Wins)}W, 🟡 {int(row.Places)}P, ROI: {row.ROI:.2f}%"
        send_telegram_message(msg, token=TOKEN, chat_id=CHAT_ID)
        print("✅ Sent to Telegram")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True)
    parser.add_argument("--telegram", action="store_true")
    args = parser.parse_args()
    main(args.week, send_telegram=args.telegram)

