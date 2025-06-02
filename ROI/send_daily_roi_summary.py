#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
import requests
from datetime import datetime

# === ARGPARSE SETUP ===
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", default=None)
args = parser.parse_args()

# === CONFIG ===
TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
CHAT_ID = "-1002580022335"  # Tipping Monster channel
MODE = "advised"
DATE = args.date or datetime.today().strftime("%Y-%m-%d")
CSV_PATH = f"logs/tips_results_{DATE}_{MODE}.csv"

# === LOAD CSV ===
if not os.path.exists(CSV_PATH):
    print(f"No ROI CSV found for {DATE}: {CSV_PATH}")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)
df["Position"] = pd.to_numeric(df["Position"], errors="coerce").fillna(0).astype(int)

tips = len(df)
wins = (df["Position"] == 1).sum()
places = df["Position"].apply(lambda x: 2 <= x <= 4).sum()
profit = df["Profit"].sum()
stake = df["Stake"].sum()
roi = (profit / stake * 100) if stake else 0

# === FORMAT MESSAGE ===
msg = (
    f"*📊 Tipping Monster Daily ROI – {DATE} ({MODE.capitalize()})*\n\n"
    f"🏇 *Tips:* {tips}  |  🥇 *Winners:* {wins}  |  🥈 *Places:* {places}\n"
    f"💰 *Profit:* {profit:+.2f} pts\n"
    f"📈 *ROI:* {roi:.2f}%\n"
    f"🪙 *Staked:* {stake:.2f} pts"
)

# === SEND TO TELEGRAM ===
resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
)

if resp.status_code == 200:
    print(f"✅ Sent ROI summary to Telegram: {DATE}")
else:
    print(f"❌ Failed to send: {resp.text}")

