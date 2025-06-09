#!/usr/bin/env python3
"""Profile trainer intent and tag tips accordingly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from core.trainer_stable_profile import (compute_trainer_stats,
                                         load_recent_results)


def load_trainer_form(results_dir: str, ref_date: str, window: int = 30) -> dict:
    df = load_recent_results(Path(results_dir), ref_date, window)
    stats = compute_trainer_stats(df)
    return {row["Trainer"]: row["Win %"] for _, row in stats.iterrows()}


def load_tips(path: Path) -> list[dict]:
    tips: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tips.append(json.loads(line))
    return tips


def tag_tips(tips: list[dict], trainer_form: dict) -> list[dict]:
    counts: dict[str, int] = {}
    for t in tips:
        tr = t.get("trainer")
        if tr:
            counts[tr] = counts.get(tr, 0) + 1

    out: list[dict] = []
    for tip in tips:
        trainer = tip.get("trainer")
        form = trainer_form.get(trainer, 0.0)
        tags = tip.get("tags", []) or []
        if form >= 20:
            tags.append("🔍 Stable Intent")
            tip["stable_form"] = form
        if counts.get(trainer, 0) > 1:
            tags.append("🏠 Multiple Runners")
        try:
            if (
                float(tip.get("last_class", -1)) > float(tip.get("class", -1))
                and float(tip.get("days_since_run", 0)) > 60
            ):
                tags.append("⬇️ Class Drop Layoff")
        except Exception:
            pass
        tip["tags"] = tags
        tip.setdefault("stable_form", form)
        out.append(tip)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Trainer intent profiler")
    parser.add_argument("tips_file", help="Tips JSONL file")
    parser.add_argument("--results_dir", default="rpscrape/data/dates/all")
    parser.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--out", help="Output JSONL file")
    args = parser.parse_args()

    trainer_form = load_trainer_form(args.results_dir, args.date, args.window)
    tips = load_tips(Path(args.tips_file))
    tagged = tag_tips(tips, trainer_form)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for row in tagged:
                f.write(json.dumps(row) + "\n")
    else:
        for row in tagged:
            print(json.dumps(row))


if __name__ == "__main__":
    main()
