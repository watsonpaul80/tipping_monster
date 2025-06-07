#!/usr/bin/env python3
"""Validate tips JSONL file for common issues."""

from __future__ import annotations

import argparse
import json
from typing import Iterable, List

REQUIRED_FIELDS = ["race", "name", "confidence"]
NAP_TAG = "\U0001f9e0 Monster NAP"
CONF_TAG = "\u2757 Confidence 90%+"


def load_tips(path: str) -> List[dict]:
    """Load tips from a JSONL file."""
    tips: List[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                tips.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Line {line_no}: invalid JSON ({exc})")
    return tips


def validate_tips(tips: Iterable[dict]) -> List[str]:
    """Return a list of validation error messages."""
    errors: List[str] = []
    seen = set()
    tips = list(tips)

    if not tips:
        errors.append("No tips found")
        return errors

    max_conf = -1.0
    for tip in tips:
        try:
            conf_val = float(tip.get("confidence", -1))
        except Exception:
            conf_val = -1
        max_conf = max(max_conf, conf_val)

    nap_count = 0
    for i, tip in enumerate(tips, 1):
        prefix = f"Tip {i}"
        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in tip:
                errors.append(f"{prefix}: missing '{field}'")

        # Duplicate runner check
        key = (tip.get("race"), tip.get("name"))
        if key in seen:
            errors.append(f"{prefix}: duplicate runner {key}")
        seen.add(key)

        # Confidence validity
        try:
            conf = float(tip.get("confidence"))
            if not 0.0 <= conf <= 1.0:
                raise ValueError
        except Exception:
            errors.append(f"{prefix}: invalid confidence '{tip.get('confidence')}'")
            conf = -1

        # Odds validity (bf_sp or odds)
        odds_val = tip.get("bf_sp", tip.get("odds"))
        if odds_val is None:
            errors.append(f"{prefix}: missing odds")
        else:
            try:
                if float(odds_val) <= 0:
                    raise ValueError
            except Exception:
                errors.append(f"{prefix}: invalid odds '{odds_val}'")

        # Tags validation
        tags = tip.get("tags", [])
        if len(tags) != len(set(tags)):
            errors.append(f"{prefix}: duplicate tags")
        if CONF_TAG in tags and conf < 0.9:
            errors.append(f"{prefix}: has '{CONF_TAG}' but confidence {conf}")
        if NAP_TAG in tags:
            nap_count += 1
            if conf < max_conf:
                errors.append(f"{prefix}: marked NAP but not highest confidence")

    if nap_count != 1:
        errors.append(f"Expected exactly one NAP tag, found {nap_count}")

    return errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate tips JSONL file")
    parser.add_argument("path", help="Path to tips_with_odds.jsonl")
    args = parser.parse_args(argv)

    try:
        tips = load_tips(args.path)
    except Exception as exc:
        print(f"❌ {exc}")
        return 1

    errors = validate_tips(tips)
    if errors:
        for err in errors:
            print(f"❌ {err}")
        return 1

    print("✅ Tips file looks good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
