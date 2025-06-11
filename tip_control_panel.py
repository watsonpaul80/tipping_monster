#!/usr/bin/env python3
"""Interactive CLI to review and manually send tips."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from typing import Iterable

from tippingmonster import repo_path, send_telegram_message


def load_tips(day: str) -> list[dict]:
    """Return list of tips from predictions directory."""
    path = repo_path("predictions", day, "tips_with_odds.jsonl")
    if not path.exists():
        raise FileNotFoundError(path)

    tips: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tips.append(json.loads(line))
    return tips


def display_tip(idx: int, tip: dict) -> None:
    conf = tip.get("confidence", 0.0) * 100
    odds = tip.get("bf_sp") or tip.get("odds", "N/A")
    tags = ", ".join(tip.get("tags", []))
    print(
        f"{idx}) {tip.get('race', '?')} - {tip.get('name', '?')} @ {odds} | {conf:.0f}% | {tags}"
    )


def choose_tips(tips: list[dict]) -> list[dict]:
    """Prompt user to select tip numbers to send."""
    for idx, tip in enumerate(tips, start=1):
        display_tip(idx, tip)
    raw = input("Send which tips? (comma list or 'all'): ").strip().lower()
    if raw == "all":
        return tips
    idxs = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            i = int(part)
            if 1 <= i <= len(tips):
                idxs.append(i - 1)
    return [tips[i] for i in idxs]


def override_tags(tip: dict) -> None:
    tags = input(
        f"Override tags for {tip.get('name', '?')}? (comma separated, blank to keep): "
    ).strip()
    if tags:
        tip["tags"] = [t.strip() for t in tags.split(",") if t.strip()]


def format_message(tip: dict) -> str:
    conf = tip.get("confidence", 0.0) * 100
    odds = tip.get("bf_sp") or tip.get("odds", "N/A")
    tags = " | ".join(tip.get("tags", []))
    return f"{tip.get('race', '?')}\n{tip.get('name', '?')} @ {odds}\nConfidence: {conf:.0f}%\n{tags}"


def send_messages(tips: Iterable[dict], telegram: bool) -> None:
    for tip in tips:
        msg = format_message(tip)
        if telegram:
            send_telegram_message(msg)
        else:
            print("\n" + msg)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tip Control Panel")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--telegram", action="store_true", help="Post to Telegram")
    parser.add_argument("--dev", action="store_true", help="Enable TM_DEV_MODE")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"

    tips = load_tips(args.date)
    if not tips:
        print("No tips available")
        return

    selected = choose_tips(tips)
    if not selected:
        print("No tips chosen")
        return

    for tip in selected:
        override_tags(tip)

    send_messages(selected, telegram=args.telegram)


if __name__ == "__main__":
    main()
