import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Telegram config
TELEGRAM_BOT_TOKEN = "8120960859:AAFKirWdN5hCRyW_KZy4XF_p0sn8ESqI3rg"
TELEGRAM_CHAT_ID = "-1002580022335"

STEAMER_DIR = Path("steam_sniper_intel")
LOG_PATH = STEAMER_DIR / "logs"
LOG_PATH.mkdir(exist_ok=True)

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

def fractional_odds(decimal_price):
    try:
        dec = float(decimal_price)
        if dec <= 1.0:
            return "1/100"
        numerator = round((dec - 1) * 100)
        denominator = 100
        while numerator % 5 == 0 and denominator % 5 == 0 and denominator > 1:
            numerator //= 5
            denominator //= 5
        return f"{numerator}/{denominator}"
    except:
        return "?"

def is_race_future(race_str):
    try:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        race_time = datetime.strptime(f"{today} {race_str.split()[0]}", "%Y-%m-%d %H:%M")
        return race_time > now
    except:
        return True  # Fail-safe: include if uncertain

def tag_steamer(drop_pct):
    if drop_pct >= 50:
        return "💣 BOOMER"
    elif drop_pct >= 30:
        return "🔥 Steamer"
    else:
        return None

def format_steamer(s):
    odds_list = s.get("odds_progression", [])
    if not odds_list or len(odds_list) < 2:
        return None, 0
    try:
        odds_path = " → ".join(fractional_odds(o) for o in odds_list)
        drop_pct = int(round((1 - odds_list[-1]/odds_list[0]) * 100))
    except:
        return None, 0

    tag = tag_steamer(drop_pct)
    if not tag:
        return None, drop_pct

    return (
        f"{tag} *Steam Sniper Intel*\n"
        f"📍 {s.get('race', 'Unknown')}\n"
        f"🐎 *{s.get('horse', 'Unknown')}*\n"
        f"📉 Odds Drop: {odds_path}\n"
        f"📊 Drop: {drop_pct}%"), drop_pct

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to steamers JSON file")
    parser.add_argument("--dryrun", action="store_true", help="Print to console only, don’t send Telegram")
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

    today_str = datetime.now().strftime("%Y-%m-%d")
    jsonl_log = LOG_PATH / f"dispatched_steamers_{today_str}.jsonl"
    
    batch = []
    sent = 0
    batch_size = 20

    for s in steamers:
        if not is_race_future(s.get("race", "")):
            continue

        msg, drop = format_steamer(s)
        if not msg:
            continue

        if args.dryrun:
            print(msg + "\n")
        else:
            batch.append(msg)
            with open(jsonl_log, "a") as logf:
                logf.write(json.dumps({"race": s.get("race"), "horse": s.get("horse"), "drop": drop}) + "\n")
            if len(batch) == batch_size:
                send_telegram_message("\n".join(batch))
                sent += len(batch)
                batch = []

    if batch and not args.dryrun:
        send_telegram_message("\n".join(batch))
        sent += len(batch)

    print(f"[+] {'Printed' if args.dryrun else 'Sent'} {sent if not args.dryrun else 'all'} steamers.")

if __name__ == "__main__":
    main()

