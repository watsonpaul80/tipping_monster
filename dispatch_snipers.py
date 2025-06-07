import json
import argparse
import os
from pathlib import Path

from tippingmonster import send_telegram_message
from tippingmonster.env_loader import load_env

load_env()

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

