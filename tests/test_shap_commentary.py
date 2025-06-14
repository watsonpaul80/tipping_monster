import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.shap_commentary import generate_tip_explanation


def test_generate_tip_explanation():
    top_features = [
        {"feature": "form_score", "value": 26, "shap": 3.2},
        {"feature": "draw_bias_rank", "value": 0.15, "shap": 2.8},
        {"feature": "trainer_rtf", "value": 31, "shap": 2.1},
        {"feature": "last_class_vs_current", "value": 1, "shap": -1.5},
        {"feature": "days_since_run", "value": 12, "shap": 1.3},
    ]
    tech, punter = generate_tip_explanation(
        "Knight Arrow",
        "3:15 Ascot",
        top_features,
        course="Ascot",
        going="Good to Firm",
        draw=2,
        runners=14,
    )
    assert "Form Score" in tech
    assert "Class Jump" in tech
    assert "drawn".lower() in punter.lower()
