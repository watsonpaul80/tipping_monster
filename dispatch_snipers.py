#!/usr/bin/env python3
import json
import argparse
import requests
import os
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Failed to send message: {e}")

def format_steamer(s):
    return (
        f"🏇 *{s['horse']}*\n"
        f"📍 {s['race']}\n"
        f"📉 *{s['old_price']}* → *{s['new_price']}* (-{s['drop_pct']}%)\n"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    args = parser.parse_args()

    if not Path(args.source).exists():
        print(f"[!] No steamers file: {args.source}")
        return

    with open(args.source, "r") as f:
        steamers = json.load(f)

    if not steamers:
        print("[+] No steamers to dispatch.")
        return

    # Batch of 5 per message
    batch = []
    for s in steamers:
        batch.append(format_steamer(s))
        if len(batch) == 5:
            send_telegram_message("🔥 *Steam Sniper Alerts*\n\n" + "\n".join(batch))
            batch = []

    if batch:
        send_telegram_message("🔥 *Steam Sniper Alerts*\n\n" + "\n".join(batch))

if __name__ == "__main__":
    main()

