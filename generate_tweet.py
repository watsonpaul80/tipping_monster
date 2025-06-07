#!/usr/bin/env python3
import os
import json
from pathlib import Path
import pandas as pd
from datetime import date, timedelta

from tippingmonster import repo_path

# === Config ===
<<<<<<< HEAD
def get_repo_root() -> Path:
    env_root = os.getenv("TIPPING_MONSTER_HOME")
    if env_root:
        return Path(env_root)
    try:
        import subprocess
        out = subprocess.check_output([
            "git",
            "-C",
            str(Path(__file__).resolve().parent),
            "rev-parse",
            "--show-toplevel",
        ], text=True).strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parent

BASE_DIR = str(get_repo_root())
=======
BASE_DIR = repo_path()
>>>>>>> 349c480117f6ad4ee9dc5b1823b33ef8c00d1b0b
TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TIPS_PATH = str(repo_path("logs", "dispatch", f"sent_tips_{TODAY}.jsonl"))
ROI_PATH = str(repo_path("logs", "roi", f"tips_results_{YESTERDAY}_advised.csv"))

# === Load tips ===
tips = []
if os.path.exists(TIPS_PATH):
    with open(TIPS_PATH, "r") as f:
        tips = [json.loads(line.strip()) for line in f if line.strip()]
    tips = sorted(tips, key=lambda x: x["confidence"], reverse=True)[:4]

# === Load ROI summary ===
roi_summary = "📊 ROI Yday: No data"
if os.path.exists(ROI_PATH):
    try:
        df = pd.read_csv(ROI_PATH)
        total_staked = df['Stake'].sum()
        profit = df['Profit'].sum()
        roi = (profit / total_staked) * 100 if total_staked > 0 else 0
        roi_summary = f"📊 ROI Yday: {roi:.1f}% ({profit:+.2f} pts)"
    except Exception:
        roi_summary = "📊 ROI Yday: Error"

# === Build tweet text ===
lines = [f"🧠 TIPPING MONSTER — AI Tips for {TODAY}"]
for tip in tips:
    try:
        race_time, course = tip["race"].split(" ", 1)
        selection = tip["name"]
        conf = round(tip["confidence"] * 100)
        odds = tip.get("bf_sp", "?")
        lines.append(f"🏇 {race_time} {course} — {selection} ({conf}% @ {odds})")
    except Exception:
        continue

lines.append(f"{roi_summary} | Join the stable 🧠🐎👇")
lines.append("t.me/tippingmonsterai")
lines.append("#TippingMonster #HorseRacing #BettingTips #AIpunter")

# === Output ===
tweet = "\n".join(lines)
print("\n" + tweet + "\n")

