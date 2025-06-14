#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from time import sleep

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.tip import Tip
from generate_lay_candidates import standardize_course_only
from tippingmonster import logs_path, send_telegram_message
from tippingmonster.env_loader import load_env
from tippingmonster.utils import load_override_or_default
from utils.commentary import generate_commentary

load_env()

# === CONFIG ===
NAP_ODDS_CAP = 21.0  # 20/1 in decimal
TODAY = date.today().isoformat()
PT_SIZE = 1
TELEGRAM_BATCH_SIZE = 5

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LOG_TO_CLI_ONLY = False
LLM_COMMENTARY_ENABLED = True


def calculate_monster_stake(
    confidence: float, odds: float, min_conf: float = 0.80
) -> float:
    return 1.0 if confidence >= min_conf else 0.0


def get_tip_composite_id(tip: Tip) -> str:
    return f"{tip.get('race', 'Unknown_Race')}_{tip.get('name', 'Unknown_Horse')}"


def generate_tags(tip: Tip, max_id: str, max_val: float):
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
    try:
        if float(tip.get("stable_form", 0)) >= 20:
            tags.append("🔍 Stable Intent")
    except Exception:
        pass
    if tip.get("multi_runner"):
        tags.append("🏠 Multiple Runners")
    if tip.get("class_drop_layoff"):
        tags.append("⬇️ Class Drop Layoff")
    try:
        if float(tip.get("draw_bias_rank", 0)) > 0.7:
            tags.append("📊 Draw Advantage")
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
        except:
            delta = None
    if delta is not None:
        if delta <= -1.0:
            tags.append("🔥 Market Mover")
        elif delta >= 1.0:
            tags.append("❄️ Drifter")
    try:
        if float(tip.get("value_score", 0)) > 5:
            tags.append("💰 Value Pick")
    except Exception:
        pass
    return tags or ["🎯 Solid pick"]


def read_tips(path: str) -> list[Tip]:
    tips: list[Tip] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                tips.append(Tip.from_dict(data))
            except json.JSONDecodeError:
                pass
    return tips


def confidence_label(conf: float) -> str:
    """Return a human-friendly confidence label."""
    if conf >= 0.9:
        return "High"
    if conf >= 0.8:
        return "Medium"
    return "Low"


TAG_REASON_MAP = {
    "🔽 Class Drop": "class drop",
    "📈 In Form": "in form",
    "⚡ Fresh": "fresh",
    "🪶 Light Weight": "light weight",
    "🚫 Layoff": "layoff",
    "💥 Monster Mode": "monster mode",
    "🔥 Market Mover": "market mover",
    "❄️ Drifter": "drifter",
    "🔍 Stable Intent": "stable intent",
    "🏠 Multiple Runners": "multiple runners",
    "⬇️ Class Drop Layoff": "class drop layoff",
}


def build_confidence_line(tip: dict) -> str:
    """Return a single line describing model confidence."""
    conf_pct = round(tip.get("confidence", 0.0) * 100)
    level = confidence_label(tip.get("confidence", 0.0))
    reasons = [TAG_REASON_MAP[t] for t in tip.get("tags", []) if t in TAG_REASON_MAP]
    reason_text = " + ".join(reasons)
    suffix = f" \u2014 {reason_text}" if reason_text else ""
    return f"\ud83e\udde0 Model Confidence: {level} ({conf_pct}%){suffix}."


def build_place_line(tip: dict) -> str | None:
    place_conf = tip.get("final_place_confidence")
    if place_conf is None:
        return None
    pct = round(place_conf * 100)
    return f"\ud83c\udfc5 Place Chance: {pct}%"


def get_confidence_band(conf: float) -> str | None:
    """Return the confidence band label for ``conf`` or ``None`` if out of range."""
    bins = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.00),
        (0.99, 1.01),
    ]
    for low, high in bins:
        if low <= conf < high:
            return f"{low:.2f}\u2013{high:.2f}"
    return None


def load_recent_roi_stats(path: str, ref_date: str, window: int = 30) -> dict:
    """Return ROI per confidence bin for ``window`` days up to ``ref_date``."""
    if not os.path.exists(path):
        return {}

    df = pd.read_csv(path)
    if df.empty:
        return {}

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Win PnL"] = pd.to_numeric(df["Win PnL"], errors="coerce").fillna(0)
    df["Tips"] = pd.to_numeric(df["Tips"], errors="coerce").fillna(0)

    ref = pd.to_datetime(ref_date)
    start = ref - timedelta(days=window)
    df = df[(df["Date"] >= start) & (df["Date"] <= ref)]

    roi = {}
    for band, grp in df.groupby("Confidence Bin"):
        tips = grp["Tips"].sum()
        pnl = grp["Win PnL"].sum()
        roi[band] = pnl / tips if tips else 0.0
    return roi


def should_skip_by_roi(conf: float, roi_map: dict, min_conf: float) -> bool:
    """Return True if ``conf`` should be skipped based on ROI mapping."""
    if conf >= min_conf:
        return False
    band = get_confidence_band(conf)
    if not band:
        return True
    return roi_map.get(band, 0.0) <= 0.0


def filter_tips_by_course(tips: list[Tip], course: str) -> list[Tip]:
    """Return tips matching ``course`` (case-insensitive)."""
    target = standardize_course_only(course)
    return [t for t in tips if standardize_course_only(t.get("race", "")) == target]


def log_nap_override(original: dict, new: dict | None, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    orig_name = original.get("name", "Unknown")
    orig_odds = original.get("bf_sp") or original.get("odds")
    if new is None:
        msg = f"Blocked NAP: {orig_name} @ {orig_odds} (no replacement)"
    else:
        new_name = new.get("name", "Unknown")
        new_odds = new.get("bf_sp") or new.get("odds")
        msg = f"Blocked NAP: {orig_name} @ {orig_odds} -> {new_name} @ {new_odds}"
    with open(path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def select_nap_tip(tips, odds_cap=NAP_ODDS_CAP, log_path=""):
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
    explain = tip.get("explanation")
    explain_line = f"💡 Why we tipped this: {explain}" if explain else ""
    confidence_line = build_confidence_line(tip)
    place_line = build_place_line(tip)
    parts = [header, title, stats, confidence_line]
    if place_line:
        parts.append(place_line)
    parts.extend([tags, comment])
    if explain_line:
        parts.append(explain_line)
    parts.append("-" * 30)
    return "\n".join(parts)


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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=TODAY)
    parser.add_argument("--mode", default="advised")
    parser.add_argument("--min_conf", type=float, default=0.80)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--course", help="Filter tips for a racecourse")
    parser.add_argument(
        "--explain", action="store_true", help="Include SHAP explanations"
    )
    parser.add_argument(
        "--comment-style",
        choices=["basic", "expressive"],
        default=os.getenv("TM_COMMENT_STYLE", "basic"),
        help="Tone for generated commentary",
    )
    args = parser.parse_args(argv)

    min_conf = load_override_or_default(args.min_conf)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    predictions_path = f"predictions/{args.date}/tips_with_odds.jsonl"
    summary_path = f"predictions/{args.date}/tips_summary.txt"
    sent_path = logs_path("dispatch", f"sent_tips_{args.date}.jsonl")

    if not os.path.exists(predictions_path):
        print(f"❌ No tips file found at {predictions_path}")
        sys.exit(1)

    tips = read_tips(predictions_path)
    if args.course:
        tips = filter_tips_by_course(tips, args.course)
    if not tips:
        print("⚠️ No valid tips to process.")
        sys.exit(1)

    roi_file = "monster_confidence_per_day_with_roi.csv"
    roi_map = load_recent_roi_stats(roi_file, args.date, 30)

    explanations = {}
    if args.explain:
        try:
            from explain_model_decision import generate_explanations

            explanations = generate_explanations(predictions_path)
        except Exception as e:
            print(f"⚠️ Failed to generate SHAP explanations: {e}")

    nap_log = logs_path(f"nap_override_{args.date}.log")
    nap_tip, max_conf = select_nap_tip(
        tips, odds_cap=NAP_ODDS_CAP, log_path=str(nap_log)
    )
    max_id = get_tip_composite_id(nap_tip) if nap_tip else None

    enriched = []
    for tip in tips:
        tip["tags"] = generate_tags(tip, max_id, max_conf)
        tip["commentary"] = generate_commentary(
            tip["tags"],
            tip.get("confidence", 0.0),
            tip.get("trainer_rtf"),
            style=args.comment_style,
        )
        odds = tip.get("bf_sp") or tip.get("odds", 0.0)
        stake = calculate_monster_stake(
            tip.get("confidence", 0.0), odds, min_conf=min_conf
        )
        if stake == 0.0 and should_skip_by_roi(
            tip.get("confidence", 0.0), roi_map, min_conf
        ):
            continue
        if stake == 0.0:
            stake = 1.0
        tip["stake"] = stake
        if tip.get("odds_drifted") and tip.get("confidence", 0.0) >= 0.95:
            tip["monster_mode"] = True
        if args.explain:
            tip_id = get_tip_composite_id(tip)
            tip["explanation"] = explanations.get(tip_id, "")
        enriched.append(tip)

    formatted = []
    for t in sorted(enriched, key=lambda x: x.get("race_time", "99:99")):
        msg = format_tip_message(t, max_id)
        if msg:
            formatted.append(msg)

    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as f:
        f.write("\n\n".join(formatted))
    with open(sent_path, "w") as f:
        for tip in enriched:
            json.dump(tip.to_dict(), f)
            f.write("\n")

    print(f"📄 Tip summary and sent tips saved to: {sent_path}")

    if args.telegram:
        print("📤 Sending to Telegram...")
        send_batched_messages(formatted, TELEGRAM_BATCH_SIZE)
    else:
        print("ℹ️ Telegram not triggered. Use `--telegram`.")


if __name__ == "__main__":
    main()
