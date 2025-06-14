from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

FEATURE_MAP = {
    "form_score": "Form Score",
    "draw_bias_rank": "Draw Bias Rank",
    "trainer_rtf": "Trainer RTF",
    "last_class_vs_current": "Class Jump",
    "days_since_run": "Fresh",
}


def _friendly_name(feature: str) -> str:
    return FEATURE_MAP.get(feature, feature.replace("_", " ").title())


def build_technical_summary(top_features: Iterable[Dict[str, Any]]) -> str:
    """Return a formatted technical summary from SHAP features."""
    lines = []
    for feat in top_features:
        shap_val = float(feat.get("shap", 0))
        arrow = "📊" if shap_val >= 0 else "📉"
        sign = "+" if shap_val >= 0 else "-"
        name = _friendly_name(str(feat.get("feature", "")))
        value = feat.get("value")
        lines.append(f"{arrow} {sign}{abs(shap_val):.1f} pts: {name} ({value})")
    return "\n".join(lines)


def build_punter_commentary(
    top_features: Iterable[Dict[str, Any]],
    course: str,
    going: str,
    draw: int,
    runners: int,
) -> str:
    """Return a short punter-friendly explanation."""
    phrases = []
    for feat in top_features:
        name = feat.get("feature")
        val = feat.get("value")
        shap_val = float(feat.get("shap", 0))
        if name == "form_score":
            if shap_val > 0:
                phrases.append("solid recent form")
            else:
                phrases.append("poor recent form")
        elif name == "draw_bias_rank":
            if shap_val > 0:
                phrases.append("good draw position")
            else:
                phrases.append("tough draw")
        elif name == "trainer_rtf":
            if shap_val > 0:
                phrases.append(f"trainer hitting {val}% strike rate")
            else:
                phrases.append(f"trainer only {val}% strike rate")
        elif name == "last_class_vs_current":
            if shap_val > 0:
                phrases.append("dropping in class")
            else:
                phrases.append("stepping up in class")
        elif name == "days_since_run":
            if shap_val > 0:
                phrases.append(f"fresh off a {val}-day break")
            else:
                phrases.append(f"may need the run after {val} days")
    draw_line = f"Drawn {draw} of {runners} at {course}"
    if going:
        draw_line += f" on {going} ground"
    comment = "✍️ " + ", ".join(phrases + [draw_line]) + "."
    return comment


def generate_tip_explanation(
    horse: str,
    race: str,
    top_features: Iterable[Dict[str, Any]],
    course: str,
    going: str,
    draw: int,
    runners: int,
) -> Tuple[str, str]:
    """Return (technical_summary, punter_commentary) for a tip."""
    tech = build_technical_summary(top_features)
    punter = build_punter_commentary(top_features, course, going, draw, runners)
    return tech, punter


__all__ = [
    "build_technical_summary",
    "build_punter_commentary",
    "generate_tip_explanation",
]
