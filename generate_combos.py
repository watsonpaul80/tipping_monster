#!/usr/bin/env python3
"""Generate smart doubles and trebles from high-confidence tips."""
from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

from tippingmonster import logs_path, send_telegram_message

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


def get_race_parts(race: str) -> tuple[str, str]:
    parts = str(race).split()
    time = parts[0] if parts else ""
    course = " ".join(parts[1:]) if len(parts) > 1 else ""
    return time, course


def format_tip(tip: Dict) -> str:
    time, course = get_race_parts(tip.get("race", ""))
    odds = tip.get("bf_sp") or tip.get("odds", "?")
    name = tip.get("name", "?")
    return f"{time} {course} - {name} @ {odds}"


def format_combo(tips: List[Dict]) -> str:
    parts = [format_tip(t) for t in tips]
    mult = combo_multiplier(tips)
    label = "Double" if len(tips) == 2 else "Treble"
    return f"\U0001f9e0 Monster {label}: {' + '.join(parts)} = {mult:.1f}x"


def compute_combo_roi(tips: List[Dict], date_str: str) -> Optional[float]:
    """Return ROI % for ``tips`` if results CSV for ``date_str`` exists."""
    results_path = Path(f"rpscrape/data/dates/all/{date_str.replace('-', '_')}.csv")
    if not results_path.exists():
        return None

    import pandas as pd

    try:
        df = pd.read_csv(results_path)
    except Exception:
        return None

    df.rename(
        columns={
            "off": "Race Time",
            "course": "Course",
            "horse": "Horse",
            "pos": "Position",
            "num": "Runners",
            "race_name": "Race Name",
        },
        inplace=True,
    )
    df["Horse"] = df["Horse"].astype(str).str.lower().str.strip()
    df["Course"] = (
        df["Course"]
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace(r"\s*\(ire\)", "", regex=True)
    )
    df["Race Time"] = df["Race Time"].astype(str).str.strip().str.lower()

    results = []
    for tip in tips:
        horse = str(tip.get("name", "")).split("(")[0].strip().lower()
        time, course = get_race_parts(tip.get("race", ""))
        time = time.lower()
        course = course.lower().strip()
        row = df[
            (df["Horse"] == horse)
            & (df["Race Time"] == time)
            & (df["Course"] == course)
        ]
        if row.empty:
            return None
        pos = str(row["Position"].iloc[0]).strip()
        results.append(pos == "1")

    stake = 1.0
    if all(results):
        profit = combo_multiplier(tips) - 1
    else:
        profit = -1.0
    return round((profit / stake) * 100, 2)


def log_combo(tips: List[Dict], date_str: str) -> None:
    """Append combo details to ROI log."""
    label = "Double" if len(tips) == 2 else "Treble"
    roi = compute_combo_roi(tips, date_str)
    log_path = logs_path("roi", f"combos_{date_str}.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    header = not log_path.exists()
    row = {
        "Date": date_str,
        "Type": label,
        "Horses": " | ".join(format_tip(t) for t in tips),
        "Multiplier": round(combo_multiplier(tips), 2),
        "ROI": "" if roi is None else roi,
    }
    import csv

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if header:
            writer.writeheader()
        writer.writerow(row)


def generate_combos(tips: List[Dict], min_conf: float = 0.90) -> List[List[Dict]]:
    filtered = filter_high_confidence(tips, min_conf)
    combos: List[List[Dict]] = []
    if len(filtered) >= 2:
        combos.append(filtered[:2])
    if len(filtered) >= 3:
        combos.append(filtered[:3])
    return combos


def generate_combo_messages(tips: List[Dict], min_conf: float = 0.90) -> List[str]:
    return [format_combo(c) for c in generate_combos(tips, min_conf)]


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
    combos = generate_combos(tips, args.min_conf)
    if not combos:
        print("\u26a0\ufe0f No combos generated.")
        return

    messages = [format_combo(c) for c in combos]
    text = "\n".join(messages)
    if args.telegram:
        send_telegram_message(text, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        for combo in combos:
            log_combo(combo, args.date)
    else:
        print(text)


if __name__ == "__main__":
    main()
