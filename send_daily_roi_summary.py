#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === ARGPARSE SETUP ===
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", default=None)
args = parser.parse_args()

# === CONFIG ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in environment variables.")
    # sys.exit(1) # This script's primary function is to send to Telegram, so exiting might be appropriate.

MODE = "advised"
DATE = args.date or datetime.today().strftime("%Y-%m-%d")
CSV_PATH = f"logs/roi/tips_results_{DATE}_{MODE}.csv"

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
if TOKEN and CHAT_ID: # Only attempt to send if credentials exist
    resp = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )

    if resp.status_code == 200:
        print(f"✅ Sent ROI summary to Telegram: {DATE}")
    else:
        print(f"❌ Failed to send: {resp.text}")
else:
    print("ℹ️ Telegram credentials not set. Skipping send to Telegram.")
