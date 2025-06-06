import os
from datetime import datetime, timedelta
import requests

# === CONFIG ===
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
BASE_DIR = "/home/ec2-user/tipping-monster"

# Use Paul's personal Telegram info directly
TG_USER_ID = "1054773464"  # Your personal Telegram user ID
TG_BOT_TOKEN = "6298132668:AAGja-iEQzAK1Ri5jBOoHwP4-YWZuywKjNU"  # Your bot token

# === FILE PATHS ===
output_path = f"{BASE_DIR}/predictions/{TODAY}/output.jsonl"
tips_path = f"{BASE_DIR}/predictions/{TODAY}/tips_with_odds.jsonl"
telegram_log = f"{BASE_DIR}/logs/dispatch/sent_tips_{TODAY}.jsonl"
roi_path = f"{BASE_DIR}/logs/roi/tips_results_{YESTERDAY}_advised.csv"

# === STATUS CHECKS ===
def check_file(path):
    return "✅" if os.path.exists(path) else "❌"

# === SUMMARY MESSAGE ===
msg = (
    f"📊 Morning Monster Digest — {TODAY}\n\n"
    f"{check_file(output_path)} Inference complete\n"
    f"{check_file(tips_path)} Tips saved\n"
    f"{check_file(telegram_log)} Sent to Telegram\n"
    f"{check_file(roi_path)} ROI for {YESTERDAY} tracked\n\n"
)

if "❌" in msg:
    msg += "👀 Please investigate logs. Something may have failed.\n"
else:
    msg += "🧠 All systems GO.\n"

msg += "#TippingMonster"

# === SEND TO TELEGRAM ===
requests.post(
    f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
    data={"chat_id": TG_USER_ID, "text": msg}
)

