from __future__ import annotations

import os
from typing import Iterable, List, Optional

TAG_MAP = {
    "Fresh": "Fresh off a break",
    "Layoff": "Returning after a layoff",
    "Class Drop": "Class drop",
    "Light Weight": "Light weight",
    "In Form": "Strong recent form",
    "Monster NAP": "Monster NAP",
    "Monster Mode": "Monster Mode",
    "Market Mover": "Market mover",
    "Drifter": "Market drifter",
    "Solid pick": "Solid pick",
}

EXPRESSIVE_MAP = {
    "Fresh off a break": "Fresh and ready to bounce back",
    "Returning after a layoff": "Back from a break",
    "Class drop": "Dropping in class",
    "Light weight": "Nicely weighted",
    "Strong recent form": "Yard's flying",
    "Monster NAP": "Monster NAP",
    "Monster Mode": "Monster Mode triggered",
    "Market mover": "Money coming",
    "Market drifter": "Market cold",
    "Solid pick": "Reliable sort",
}


def _parse_trainer_tag(tag: str) -> str:
    digits = "".join(ch for ch in tag if ch.isdigit())
    return f"Trainer in form (RTF {digits}%)" if digits else "Trainer in form"


def _parse_confidence_tag(tag: str, confidence: float) -> str:
    digits = "".join(ch for ch in tag if ch.isdigit())
    if digits:
        return f"Confidence {digits}%"
    return f"Confidence {round(confidence * 100)}%"


def _build_commentary_basic(phrases: List[str]) -> str:
    return "✍️ " + " | ".join(phrases)


def _build_commentary_expressive(phrases: List[str]) -> str:
    styled = [EXPRESSIVE_MAP.get(p, p) for p in phrases]
    first, *rest = styled
    if rest:
        return f"🗣️ 🔥 {first}! {' '.join(rest)}."
    return f"🗣️ 🔥 {first}!"


def generate_commentary(
    tags: Iterable[str],
    confidence: float,
    trainer_form: Optional[float] = None,
    layoff_days: Optional[int] = None,
    last_win_days: Optional[int] = None,
    style: Optional[str] = None,
) -> str:
    """Return a short commentary string derived from ``tags`` and ``confidence``."""
    style = style or os.getenv("TM_COMMENT_STYLE", "basic").lower()
    phrases: List[str] = []
    for tag in tags:
        if "Trainer" in tag:
            phrases.append(_parse_trainer_tag(tag))
        elif "Confidence" in tag:
            phrases.append(_parse_confidence_tag(tag, confidence))
        else:
            for key, phrase in TAG_MAP.items():
                if key in tag:
                    phrases.append(phrase)
                    break
    if not phrases:
        prefix = "✍️" if style == "basic" else "🗣️"
        return f"{prefix} No standout signals — check form manually."
    if style == "expressive":
        return _build_commentary_expressive(phrases)
    return _build_commentary_basic(phrases)


__all__ = ["generate_commentary"]
