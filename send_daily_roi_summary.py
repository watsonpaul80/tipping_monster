
import os
import sys
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIG ===
TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
CHAT_ID = "-1002580022335"  # Tipping Monster channel
DATE = (datetime.today() - timedelta(days=0)).strftime("%Y-%m-%d")
CSV_PATH = f"logs/tips_results_{DATE}_advised.csv"

# === LOAD CSV ===
if not os.path.exists(CSV_PATH):
    print(f"⚠️ No ROI CSV found for {DATE}: {CSV_PATH}")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)
tips = len(df)
wins = len(df[df["Position"] == 1])
places = len(df[df["Position"] <= 3])
profit = df["Profit"].sum()
stake = df["Stake"].sum()
roi = (profit / stake * 100) if stake else 0

# === FORMAT MESSAGE ===
msg = f"""📊 Tipping Monster ROI – {DATE}

🏇 Tips: {tips} | 🥇 Wins: {wins} | 🥈 Places: {places}
💰 Profit: {profit:+.2f} pts
📈 ROI: {roi:.2f}%"""

# === SEND TO TELEGRAM ===
resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
)

if resp.status_code == 200:
    print(f"✅ Sent ROI summary to Telegram: {DATE}")
else:
    print(f"❌ Failed to send: {resp.text}")
