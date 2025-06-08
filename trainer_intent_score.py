#!/usr/bin/env python3
"""Calculate a trainer intent score for racing tips.

The score is a simple heuristic based on how recently the horse ran,

jockey/trainer strike rates and the trend in available odds.
"""

from __future__ import annotations

from typing import Iterable


def trainer_intent_score(
    days_since_run: float | int,
    trainer_rtf: float | int,
    jockey_rtf: float | int,
    odds_history: Iterable[float] | None = None,
) -> float:
    """Return a percentage score representing trainer intent.

    Parameters
    ----------
    days_since_run : float | int
        Days since the horse last raced.
    trainer_rtf : float | int
        Trainer's recent strike rate (0-100).
    jockey_rtf : float | int
        Jockey's recent strike rate (0-100).
    odds_history : Iterable[float] | None, optional
        Sequence of odds from oldest to newest.

    Returns
    -------
    float
        Intent score between 0 and 100.
    """
    try:
        days = float(days_since_run)
    except Exception:
        days = 999.0
    try:
        trainer = float(trainer_rtf)
    except Exception:
        trainer = 0.0
    try:
        jockey = float(jockey_rtf)
    except Exception:
        jockey = 0.0

    recency = max(0.0, 30.0 - days) / 30.0
    combo = (trainer + jockey) / 200.0

    trend = 0.5
    if odds_history:
        values = [float(o) for o in odds_history if o is not None]
        if len(values) >= 2 and values[0] > 0:
            pct = max(-1.0, min(1.0, (values[0] - values[-1]) / values[0]))
            trend = 0.5 + (pct / 2.0)

    score = (0.4 * recency) + (0.4 * combo) + (0.2 * trend)
    return round(score * 100, 2)


if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Compute trainer intent scores")
    parser.add_argument("input", help="Input tips JSONL")
    parser.add_argument("--out", help="Output JSONL file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    for row in rows:
        row["trainer_intent"] = trainer_intent_score(
            row.get("days_since_run", -1),
            row.get("trainer_rtf", 0),
            row.get("jockey_rtf", 0),
            row.get("odds_history"),
        )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
    else:
        for row in rows:
            sys.stdout.write(json.dumps(row) + "\n")
