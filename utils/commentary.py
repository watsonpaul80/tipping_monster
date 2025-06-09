from __future__ import annotations

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


def _parse_trainer_tag(tag: str) -> str:
    digits = "".join(ch for ch in tag if ch.isdigit())
    return f"Trainer in form (RTF {digits}%)" if digits else "Trainer in form"


def _parse_confidence_tag(tag: str, confidence: float) -> str:
    digits = "".join(ch for ch in tag if ch.isdigit())
    if digits:
        return f"Confidence {digits}%"
    return f"Confidence {round(confidence * 100)}%"


def generate_commentary(
    tags: Iterable[str],
    confidence: float,
    trainer_form: Optional[float] = None,
    layoff_days: Optional[int] = None,
    last_win_days: Optional[int] = None,
) -> str:
    """Return a short commentary string derived from ``tags`` and ``confidence``."""
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
        return "✍️ No standout signals — check form manually."
    return "✍️ " + " | ".join(phrases)


__all__ = ["generate_commentary"]
