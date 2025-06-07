import os
from datetime import datetime, timedelta
from pathlib import Path

import requests  # HTTP requests for Telegram API

from tippingmonster.env_loader import load_env

load_env()

"""
Send a morning digest to Telegram.

Requires the following environment variables:
    TELEGRAM_CHAT_ID or TG_USER_ID    - Telegram user ID to send the message to
    TELEGRAM_BOT_TOKEN or TG_BOT_TOKEN  - Bot token used for authentication
"""

# === CONFIG ===
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def get_repo_root() -> Path:
    env_root = os.getenv("TIPPING_MONSTER_HOME")
    if env_root:
        return Path(env_root)
    try:
        import subprocess

        out = subprocess.check_output(
            [
                "git",
                "-C",
                str(Path(__file__).resolve().parents[1]),
                "rev-parse",
                "--show-toplevel",
            ],
            text=True,
        ).strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parents[1]


BASE_DIR = str(get_repo_root())

# === ENV VARS ===
TG_USER_ID = os.getenv("TG_USER_ID") or os.getenv("TELEGRAM_CHAT_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

if not TG_USER_ID or not TG_BOT_TOKEN:
    raise RuntimeError(
        "Telegram credentials must be set via TG_USER_ID / TELEGRAM_CHAT_ID and TG_BOT_TOKEN / TELEGRAM_BOT_TOKEN"
    )

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
    data={"chat_id": TG_USER_ID, "text": msg},
)
