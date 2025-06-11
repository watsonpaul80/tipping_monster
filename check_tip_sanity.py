#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, List

DATE_RE = re.compile(r"sent_tips_(\d{4}-\d{2}-\d{2})\.jsonl$")


def find_latest_sent_file(logs_dir: Path = Path("logs")) -> Path:
    files = []
    for f in logs_dir.glob("sent_tips_*.jsonl"):
        m = DATE_RE.match(f.name)
        if m:
            files.append((m.group(1), f))
    if not files:
        raise FileNotFoundError("No sent_tips_YYYY-MM-DD.jsonl found in logs/")
    files.sort()
    return files[-1][1]


def load_tips(path: Path) -> List[dict]:
    tips: List[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                tips.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return tips


def check_tip_sanity(tips: Iterable[dict]) -> List[str]:
    warnings: List[str] = []
    nap: tuple[str, float] | None = None
    for tip in tips:
        race = tip.get("race", "?")
        name = tip.get("name", "?")
        try:
            conf = float(tip.get("confidence", 0))
        except Exception:
            conf = 0.0
        if conf < 0.5:
            warnings.append(
                f"\u26a0\ufe0f Low confidence {conf:.2f} at {race} ({name})"
            )
        if tip.get("bf_sp") is None and tip.get("odds") is None:
            warnings.append(f"\ud83d\udea8 Tip at {race} has missing odds")
        if tip.get("stake") is None:
            warnings.append(f"\ud83d\udea8 Tip at {race} has missing stake")
        tags = [str(t).lower() for t in tip.get("tags", [])]
        if any("nap" in t for t in tags):
            nap = (name, conf)
    if nap and nap[1] < 0.8:
        warnings.append(f"\u26a0\ufe0f NAP confidence is only {nap[1]:.2f} ({nap[0]})")
    return warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check latest sent tips for common issues"
    )
    parser.add_argument(
        "--logs-dir", default="logs", help="Directory containing sent_tips files"
    )
    args = parser.parse_args()
    latest = find_latest_sent_file(Path(args.logs_dir))
    tips = load_tips(latest)
    warns = check_tip_sanity(tips)
    if warns:
        for w in warns:
            print(w)
    else:
        print(f"\u2705 No issues found in {latest}")


if __name__ == "__main__":
    main()
