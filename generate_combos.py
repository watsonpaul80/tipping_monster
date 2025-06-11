#!/usr/bin/env python3
"""Generate smart doubles and trebles from high-confidence tips."""
from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from tippingmonster import send_telegram_message

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def load_tips(path: Path) -> List[Dict]:
    tips = []
    if not path.exists():
        return tips
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                tips.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return tips


def filter_high_confidence(tips: List[Dict], min_conf: float) -> List[Dict]:
    """Return top tips with ``confidence`` >= ``min_conf`` from unique races."""
    high = [t for t in tips if t.get("confidence", 0.0) >= min_conf]
    high.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
    unique: Dict[str, Dict] = {}
    for tip in high:
        race = tip.get("race", "")
        if race not in unique:
            unique[race] = tip
    return list(unique.values())


def combo_multiplier(tips: List[Dict]) -> float:
    mult = 1.0
    for t in tips:
        try:
            mult *= float(t.get("bf_sp") or t.get("odds", 1.0))
        except Exception:
            mult *= 1.0
    return mult


def format_combo(tips: List[Dict]) -> str:
    names = [t.get("name", "?") for t in tips]
    mult = combo_multiplier(tips)
    label = "Double" if len(tips) == 2 else "Treble"
    return f"\U0001f9e0 Monster {label}: {' + '.join(names)} = {mult:.1f}x"


def generate_combo_messages(tips: List[Dict], min_conf: float = 0.90) -> List[str]:
    filtered = filter_high_confidence(tips, min_conf)
    messages: List[str] = []
    if len(filtered) >= 2:
        messages.append(format_combo(filtered[:2]))
    if len(filtered) >= 3:
        messages.append(format_combo(filtered[:3]))
    return messages


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Monster doubles/trebles")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--min_conf", type=float, default=0.90)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    base = Path(f"predictions/{args.date}")
    path = base / "tips_with_odds.jsonl"
    if not path.exists():
        path = base / "output.jsonl"
        if not path.exists():
            print(f"\u274c No tips found for {args.date}")
            return

    tips = load_tips(path)
    messages = generate_combo_messages(tips, args.min_conf)
    if not messages:
        print("\u26a0\ufe0f No combos generated.")
        return

    text = "\n".join(messages)
    if args.telegram:
        send_telegram_message(text, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
    else:
        print(text)


if __name__ == "__main__":
    main()
