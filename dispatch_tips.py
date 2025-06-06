import os
import json
from datetime import date
import requests
from time import sleep
import sys
import argparse

TODAY = date.today().isoformat()
DEFAULT_DATE = TODAY

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEND_TO_TELEGRAM = True
LOG_TO_CLI_ONLY = False
LLM_COMMENTARY_ENABLED = True
PT_SIZE = 1
TELEGRAM_BATCH_SIZE = 5

def calculate_monster_stake(confidence: float, odds: float, min_conf: float = 0.80) -> float:
    return 1.0 if confidence >= min_conf else 0.0

def get_tip_composite_id(tip: dict) -> str:
    return f"{tip.get('race', 'Unknown_Race')}_{tip.get('name', 'Unknown_Horse')}"

def generate_tags(tip, max_id, max_val):
    tags = []
    try:
        if float(tip.get("last_class", -1)) > float(tip.get("class", -1)):
            tags.append("🔽 Class Drop")
    except: pass
    try:
        d = float(tip.get("days_since_run", -1))
        if 7 <= d <= 14: tags.append("⚡ Fresh")
        elif d > 180: tags.append("🚫 Layoff")
    except: pass
    try:
        if float(tip.get("lbs", 999)) < 135:
            tags.append("🪶 Light Weight")
    except: pass
    try:
        if float(tip.get("form_score", -1)) >= 20:
            tags.append("📈 In Form")
    except: pass
    if get_tip_composite_id(tip) == max_id and tip.get("confidence", 0.0) == max_val:
        tags.append("🧠 Monster NAP")
    if tip.get("confidence", 0.0) >= 0.90:
        tags.append("❗ Confidence 90%+")
    if tip.get("monster_mode"):
        tags.append("💥 Monster Mode")
    return tags or ["🎯 Solid pick"]

def read_tips(path):
    tips = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                tips.append(json.loads(line.strip()))
            except: pass
    return tips

def format_tip_message(tip, max_id):
    race_info = tip.get("race", "")
    race_time, course = "??:??", "Unknown"
    if " " in race_info:
        race_time, course = race_info.split(" ", 1)
    else:
        race_time = tip.get("race_time", "??:??")
        course = race_info or "Unknown"

    horse = tip.get("name", "Unknown Horse")
    raw_odds = tip.get("bf_sp") or tip.get("odds", "N/A")
    odds = f"{raw_odds:.1f}" if isinstance(raw_odds, (float, int)) else str(raw_odds)
    conf = round(tip.get("confidence", 0.0) * 100)
    stake = tip.get("stake", 0.0)
    if stake == 0.0:
        return None
    stake_pts = stake / PT_SIZE
    ew_label = " EW" if stake == 1.0 and isinstance(raw_odds, (float, int)) and raw_odds >= 5.0 else ""
    is_nap = get_tip_composite_id(tip) == max_id
    title_prefix = "🧠 *NAP* –" if is_nap else "🏇"
    title = f"{title_prefix} {horse} @ {odds}"
    header = f"⏱ {race_time} {course}"
    stats = f"📊 Confidence: {conf}% | Odds: {odds} | Stake: {stake_pts:.2f} pts{ew_label}"
    tags = " | ".join(tip.get("tags", []))
    comment = f"✍️ {tip['commentary']}" if LLM_COMMENTARY_ENABLED and tip.get("commentary") else "💬 Commentary coming soon..."
    return f"{header}\n{title}\n{stats}\n{tags}\n{comment}\n{'-'*30}"

def send_to_telegram(text):
    if LOG_TO_CLI_ONLY:
        print(text)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        print(f"❌ Message content:\n{text}")

def send_batched_messages(tips, batch_size):
    for i in range(0, len(tips), batch_size):
        batch = "\n\n".join(tips[i:i + batch_size])
        send_to_telegram(batch)
        sleep(1.5)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument("--mode", default="advised")
    parser.add_argument("--min_conf", type=float, default=0.80)
    parser.add_argument("--telegram", action="store_true")
    args = parser.parse_args()

    PREDICTIONS_PATH = f"predictions/{args.date}/tips_with_odds.jsonl"
    SUMMARY_PATH = f"predictions/{args.date}/tips_summary.txt"
    SENT_TIPS_PATH = f"logs/dispatch/sent_tips_{args.date}.jsonl"

    if not os.path.exists(PREDICTIONS_PATH):
        print(f"❌ No tips file found at {PREDICTIONS_PATH}")
        sys.exit(1)

    tips = read_tips(PREDICTIONS_PATH)
    if not tips:
        print("⚠️ No valid tips to process.")
        sys.exit(1)

    max_conf, max_id = 0.0, None
    for t in tips:
        conf = t.get("confidence", 0.0)
        cid = get_tip_composite_id(t)
        if conf > max_conf:
            max_conf, max_id = conf, cid

    enriched = []
    for tip in tips:
        tip["tags"] = generate_tags(tip, max_id, max_conf)
        odds = tip.get("bf_sp") or tip.get("odds", 0.0)
        stake = calculate_monster_stake(tip.get("confidence", 0.0), odds, min_conf=args.min_conf)
        if stake == 0.0:
            continue
        tip["stake"] = stake
        if tip.get("odds_drifted") and tip.get("confidence", 0.0) >= 0.95:
            tip["monster_mode"] = True
        enriched.append(tip)

    print(f"DEBUG: {len(enriched)} tips after enrichment")

    formatted = []
    for t in sorted(enriched, key=lambda x: x.get("race_time", "99:99")):
        msg = format_tip_message(t, max_id)
        if msg:
            formatted.append(msg)

    print(f"DEBUG: {len(formatted)} messages formatted")

    if not formatted:
        print("⚠️ No tips qualified after formatting.")
        return

    with open(SUMMARY_PATH, "w") as f:
        f.write("\n\n".join(formatted))
    with open(SENT_TIPS_PATH, "w") as f:
        for tip in enriched:
            json.dump(tip, f)
            f.write("\n")

    print(f"📄 Saved tip summary and sent_tips to {SENT_TIPS_PATH}")

    if args.telegram and not LOG_TO_CLI_ONLY:
        print("📤 Sending batches to Telegram...")
        send_batched_messages(formatted, TELEGRAM_BATCH_SIZE)
    elif not args.telegram:
        print("ℹ️ Telegram sending not triggered (run with `--telegram`)")

if __name__ == "__main__":
    main()

