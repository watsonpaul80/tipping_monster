import os
from pathlib import Path
from datetime import datetime, timedelta

from tippingmonster import send_telegram_message

"""Send a morning digest to Telegram.

Requires the following environment variables:
    TG_USER_ID    - Telegram user ID to send the message to
    TG_BOT_TOKEN  - Bot token used for authentication
"""

# === CONFIG ===
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
BASE_DIR = os.getenv("TM_ROOT", str(Path(__file__).resolve().parents[1]))

# Read Telegram credentials from environment variables
# Required variables: TG_USER_ID, TG_BOT_TOKEN
TG_USER_ID = os.getenv("TG_USER_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")


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
send_telegram_message(msg, token=TG_BOT_TOKEN, chat_id=TG_USER_ID)

