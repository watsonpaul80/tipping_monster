import json
from pathlib import Path

from explain_model_decision import generate_explanations


def test_generate_explanations(tmp_path):
    tip = {
        "race": "1:00 Test",
        "name": "Runner",
        "draw": 2,
        "or": 70,
        "rpr": 120,
        "lbs": 126,
        "age": 5,
        "dist_f": 8,
        "class": 4,
        "going": "Good",
        "prize": 5000,
    }
    p = tmp_path / "tips.jsonl"
    with open(p, "w") as f:
        f.write(json.dumps(tip) + "\n")

    root = Path(__file__).resolve().parents[1]
    model = root / "tipping-monster-xgb-model.bst"
    features = root / "features.json"
    expl = generate_explanations(str(p), model_path=str(model), features_path=str(features))
    key = f"{tip['race']}|{tip['name']}"
    assert key in expl
    assert isinstance(expl[key], str)
    assert expl[key]
