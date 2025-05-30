import json
import argparse
import requests
from pathlib import Path

# Telegram config (replace with your tokens or load from env/secrets)
TELEGRAM_BOT_TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
TELEGRAM_CHAT_ID = "-1002580022335"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to send message: {e}")

def format_steamer(s):
    odds_path = " → ".join(str(o) for o in s.get("odds_progression", []))
    volume = f"£{int(s.get('volume', 0)):,}" if s.get("volume", 0) else "Unknown"
    return (
        f"🔥 *Steam Sniper: Market Intelligence Report*\n\n"
        f"📍 {s.get('race', 'Unknown')}\n"
        f"🐎 *{s.get('horse', 'Unknown')}*\n"
        f"🔻 Odds Drop: {odds_path}\n"
        f"💰 Volume: {volume} matched\n"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to steamers JSON file")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"[!] No steamers file found at {source_path}")
        return

    with open(source_path, "r") as f:
        steamers = json.load(f)

    if not steamers:
        print("[+] No steamers to dispatch.")
        return

    batch = []
    for s in steamers:
        batch.append(format_steamer(s))
        if len(batch) == 5:
            send_telegram_message("\n".join(batch))
            batch = []

    if batch:
        send_telegram_message("\n".join(batch))

    print(f"[+] Sent {len(steamers)} steamers in batches.")

if __name__ == "__main__":
    main()

