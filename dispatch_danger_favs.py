#!/usr/bin/env python3
"""Dispatch Danger Fav candidates to Telegram."""
from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from generate_lay_candidates import race_key
from tippingmonster import send_telegram_message

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BATCH_SIZE = 10


def load_jsonl(path: Path) -> List[Dict]:
    items = []
    if not path.exists():
        return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def build_price_map(snapshot: List[Dict]) -> Dict[tuple, float]:
    """Return mapping of (race_key, horse_lower) -> price."""
    price_map = {}
    for entry in snapshot:
        key = race_key(entry.get("race", ""))
        horse = str(entry.get("horse", "")).lower().strip()
        price = entry.get("bf_sp") or entry.get("price")
        if key and horse:
            price_map[(key, horse)] = float(price)
    return price_map


def tag_movers(cands: List[Dict], early_prices: Dict[tuple, float]) -> None:
    for cand in cands:
        key = (
            race_key(cand.get("race", "")),
            str(cand.get("name", "")).lower().strip(),
        )
        early = early_prices.get(key)
        final = cand.get("bf_sp")
        if early and final:
            delta = early - float(final)
            if delta >= 1.0:
                cand.setdefault("tags", []).append("🔥 Steamer")
            elif delta <= -1.0:
                cand.setdefault("tags", []).append("❄️ Drifter")


def format_entry(entry: Dict) -> str:
    race = entry.get("race", "?")
    name = entry.get("name", "?")
    price = entry.get("bf_sp") or "?"
    conf = round(float(entry.get("confidence", 0.0)) * 100)
    tags = " | ".join(entry.get("tags", []))
    return f"{race} – {name} @ {price} ({conf}%)\n{tags}"


def send_batches(messages: List[str], batch_size: int) -> None:
    for i in range(0, len(messages), batch_size):
        batch = "\n\n".join(messages[i : i + batch_size])
        send_telegram_message(batch, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Dispatch Danger Fav candidates")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args(argv)

    if args.dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"

    cand_file = Path(f"predictions/{args.date}/danger_favs.jsonl")
    cands = load_jsonl(cand_file)
    if not cands:
        print(f"No Danger Favs found at {cand_file}")
        return

    early_snapshots = sorted(Path("odds_snapshots").glob(f"{args.date}_*.json"))
    if early_snapshots:
        with open(early_snapshots[0]) as f:
            early_snapshot = json.load(f)
        price_map = build_price_map(early_snapshot)
        tag_movers(cands, price_map)

    messages = [format_entry(c) for c in cands]

    if args.telegram:
        send_batches(messages, BATCH_SIZE)
    else:
        for msg in messages:
            print(msg)
            print()


if __name__ == "__main__":
    main()
