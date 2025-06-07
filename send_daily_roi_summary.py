#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
from tippingmonster import send_telegram_message
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === ARGPARSE SETUP ===
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", default=None)
args = parser.parse_args()

# === CONFIG ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Tipping Monster channel
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
try:
    send_telegram_message(msg, token=TOKEN, chat_id=CHAT_ID)
    print(f"✅ Sent ROI summary to Telegram: {DATE}")
except Exception as e:
    print(f"❌ Failed to send Telegram message: {e}")

