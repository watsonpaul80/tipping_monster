import argparse
import json
import os
from collections import defaultdict
from datetime import date

from dotenv import load_dotenv

from tippingmonster import send_telegram_message

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def read_tips(path):
    tips = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                tips.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return tips


def send_to_telegram(text):
    """Send a single message to Telegram using the shared helper."""
    try:
        send_telegram_message(text, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        print(text)


def format_race_message(race, entries):
    parts = [f"⏱ {race}"]
    for tip in entries:
        odds = tip.get("bf_sp") or tip.get("odds", "N/A")
        conf = round(tip.get("confidence", 0.0) * 100)
        parts.append(f"- {tip.get('name', 'Unknown')} @ {odds} ({conf}%)")
    return "\n".join(parts)


def yield_batches(messages, batch_size, char_limit=3900):
    """Yield message batches respecting batch_size and Telegram char limits."""
    batch = []
    length = 0
    for msg in messages:
        msg_len = len(msg) + 2  # account for separator
        if batch and (len(batch) >= batch_size or length + msg_len > char_limit):
            yield "\n\n".join(batch)
            batch = [msg]
            length = len(msg)
        else:
            batch.append(msg)
            length += msg_len
    if batch:
        yield "\n\n".join(batch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=40,
        help="number of races per Telegram message",
    )
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args()

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    base = f"predictions/{args.date}"
    path = os.path.join(base, "tips_with_odds.jsonl")
    if not os.path.exists(path):
        path = os.path.join(base, "output.jsonl")
        if not os.path.exists(path):
            print(f"❌ No predictions found for {args.date}")
            return

    tips = read_tips(path)
    if not tips:
        print("⚠️ No tips loaded")
        return

    races = defaultdict(list)
    for t in tips:
        race = t.get("race", "Unknown")
        races[race].append(t)

    def race_key(r):
        time_part = r.split(" ")[0]
        try:
            h, m = map(int, time_part.split(":"))
            return h * 60 + m
        except Exception:
            return 9999

    messages = []
    for race, entries in sorted(races.items(), key=lambda x: race_key(x[0])):
        entries = sorted(entries, key=lambda x: x.get("confidence", 0.0), reverse=True)
        messages.append(format_race_message(race, entries))

    if args.telegram:
        for batch in yield_batches(messages, args.batch_size):
            send_to_telegram(batch)
    else:
        for batch in yield_batches(messages, args.batch_size):
            print(batch)
            print()


if __name__ == "__main__":
    main()
