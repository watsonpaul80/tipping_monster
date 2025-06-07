#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import date
from time import sleep

from dotenv import load_dotenv

load_dotenv()

from tippingmonster import logs_path, send_telegram_message
from tippingmonster.env_loader import load_env

load_env()
from tippingmonster.env_loader import load_env

load_env()

# === CONFIG ===
NAP_ODDS_CAP = 21.0  # 20/1 in decimal
TODAY = date.today().isoformat()
DEFAULT_DATE = TODAY

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEND_TO_TELEGRAM = True
LOG_TO_CLI_ONLY = False
LLM_COMMENTARY_ENABLED = True
PT_SIZE = 1
TELEGRAM_BATCH_SIZE = 5


def calculate_monster_stake(
    confidence: float, odds: float, min_conf: float = 0.80
) -> float:
    return 1.0 if confidence >= min_conf else 0.0


def get_tip_composite_id(tip: dict) -> str:
    return f"{tip.get('race', 'Unknown_Race')}_{tip.get('name', 'Unknown_Horse')}"


def generate_tags(tip, max_id, max_val):
    tags = []
    try:
        if float(tip.get("last_class", -1)) > float(tip.get("class", -1)):
            tags.append("🔽 Class Drop")
    except:
        pass
    try:
        d = float(tip.get("days_since_run", -1))
        if 7 <= d <= 14:
            tags.append("⚡ Fresh")
        elif d > 180:
            tags.append("🚫 Layoff")
    except:
        pass
    try:
        if float(tip.get("lbs", 999)) < 135:
            tags.append("🪶 Light Weight")
    except:
        pass
    try:
        if float(tip.get("form_score", -1)) >= 20:
            tags.append("📈 In Form")
    except:
        pass
    if get_tip_composite_id(tip) == max_id and tip.get("confidence", 0.0) == max_val:
        tags.append("🧠 Monster NAP")
    if tip.get("confidence", 0.0) >= 0.90:
        tags.append("❗ Confidence 90%+")
    if tip.get("monster_mode"):
        tags.append("💥 Monster Mode")
    delta = tip.get("odds_delta")
    if delta is None and "realistic_odds" in tip and "bf_sp" in tip:
        try:
            delta = float(tip["realistic_odds"]) - float(tip["bf_sp"])
        except Exception:
            delta = None
    if delta is not None:
        if delta <= -1.0:
            tags.append("🔥 Market Mover")
        elif delta >= 1.0:
            tags.append("❄️ Drifter")
    return tags or ["🎯 Solid pick"]


def read_tips(path):
    tips = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                tips.append(json.loads(line.strip()))
            except:
                pass
    return tips


def log_nap_override(original: dict, new: dict | None, path: str) -> None:
    """Append a NAP override message to ``path``."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    orig_name = original.get("name", "Unknown")
    orig_odds = original.get("bf_sp") or original.get("odds")
    if new is None:
        msg = f"Blocked NAP: {orig_name} @ {orig_odds} (no replacement)"
    else:
        new_name = new.get("name", "Unknown")
        new_odds = new.get("bf_sp") or new.get("odds")
        msg = f"Blocked NAP: {orig_name} @ {orig_odds} -> " f"{new_name} @ {new_odds}"
    with open(path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def select_nap_tip(
    tips: list[dict], odds_cap: float = NAP_ODDS_CAP, log_path: str = ""
) -> tuple[dict | None, float]:
    """Return the tip to mark as NAP and its confidence.

    If the top-confidence tip exceeds ``odds_cap`` and does not have
    ``override_nap`` set, the next highest qualifying tip becomes the NAP.
    Any blocked/reassigned NAP is logged to ``log_path``.
    """
    if not tips:
        return None, 0.0

    sorted_tips = sorted(tips, key=lambda x: x.get("confidence", 0.0), reverse=True)
    top_tip = sorted_tips[0]

    for tip in sorted_tips:
        odds = tip.get("bf_sp") or tip.get("odds", 0.0)
        if tip.get("override_nap") or odds <= odds_cap:
            if tip is not top_tip and log_path:
                log_nap_override(top_tip, tip, log_path)
            return tip, tip.get("confidence", 0.0)

    if log_path:
        log_nap_override(top_tip, None, log_path)
    return None, 0.0


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
    ew_label = (
        " EW"
        if stake == 1.0 and isinstance(raw_odds, (float, int)) and raw_odds >= 5.0
        else ""
    )
    is_nap = get_tip_composite_id(tip) == max_id
    title_prefix = "🧠 *NAP* –" if is_nap else "🏇"
    title = f"{title_prefix} {horse} @ {odds}"
    header = f"⏱ {race_time} {course}"
    stats = (
        f"📊 Confidence: {conf}% | Odds: {odds} | Stake: {stake_pts:.2f} pts{ew_label}"
    )
    tags = " | ".join(tip.get("tags", []))
    comment = (
        f"✍️ {tip['commentary']}"
        if LLM_COMMENTARY_ENABLED and tip.get("commentary")
        else "💬 Commentary coming soon..."
    )
    return f"{header}\n{title}\n{stats}\n{tags}\n{comment}\n{'-'*30}"


def send_to_telegram(text):
    if LOG_TO_CLI_ONLY:
        print(text)
        return
    try:
        send_telegram_message(text, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        print(f"❌ Message content:\n{text}")


def send_batched_messages(tips, batch_size):
    for i in range(0, len(tips), batch_size):
        batch = "\n\n".join(tips[i : i + batch_size])
        send_to_telegram(batch)
        sleep(1.5)


def dispatch(
    date: str = DEFAULT_DATE,
    *,
    mode: str = "advised",
    min_conf: float = 0.80,
    telegram: bool = False,
    dev: bool = False,
) -> None:
    """Format today's tips and optionally send them to Telegram."""

    if dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    PREDICTIONS_PATH = f"predictions/{date}/tips_with_odds.jsonl"
    SUMMARY_PATH = f"predictions/{date}/tips_summary.txt"
    SENT_TIPS_PATH = logs_path("dispatch", f"sent_tips_{date}.jsonl")

    if not os.path.exists(PREDICTIONS_PATH):
        print(f"❌ No tips file found at {PREDICTIONS_PATH}")
        sys.exit(1)

    tips = read_tips(PREDICTIONS_PATH)
    if not tips:
        print("⚠️ No valid tips to process.")
        sys.exit(1)

    nap_log = logs_path(f"nap_override_{date}.log")
    nap_tip, max_conf = select_nap_tip(
        tips, odds_cap=NAP_ODDS_CAP, log_path=str(nap_log)
    )
    max_id = get_tip_composite_id(nap_tip) if nap_tip else None

    enriched = []
    for tip in tips:
        tip["tags"] = generate_tags(tip, max_id, max_conf)
        odds = tip.get("bf_sp") or tip.get("odds", 0.0)
        stake = calculate_monster_stake(
            tip.get("confidence", 0.0), odds, min_conf=min_conf
        )
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

    if telegram and not LOG_TO_CLI_ONLY:
        print("📤 Sending batches to Telegram...")
        send_batched_messages(formatted, TELEGRAM_BATCH_SIZE)
    elif not telegram:
        print("ℹ️ Telegram sending not triggered (run with `--telegram`)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument("--mode", default="advised")
    parser.add_argument("--min_conf", type=float, default=0.80)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true", help="Enable dev mode")
    args = parser.parse_args(argv)

    dispatch(
        date=args.date,
        mode=args.mode,
        min_conf=args.min_conf,
        telegram=args.telegram,
        dev=args.dev,
    )


if __name__ == "__main__":
    main()
