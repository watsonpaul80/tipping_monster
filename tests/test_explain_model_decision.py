import json
import sys
from pathlib import Path

import pandas as pd
import xgboost as xgb

sys.path.append(str(Path(__file__).resolve().parents[1]))

from explain_model_decision import generate_explanations


def build_dummy_model(path: Path) -> None:
    features = [
        "draw",
        "or",
        "rpr",
        "lbs",
        "age",
        "dist_f",
        "class",
        "going",
        "prize",
        "stale_penalty",
    ]
    X = pd.DataFrame([[0] * len(features), [1] * len(features)], columns=features)
    y = [0, 1]
    model = xgb.XGBClassifier(
        use_label_encoder=False, eval_metric="logloss", n_estimators=1
    )
    model.fit(X, y)
    model.get_booster().save_model(path)


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
        "stale_penalty": 0,
    }
    p = tmp_path / "tips.jsonl"
    with open(p, "w") as f:
        f.write(json.dumps(tip) + "\n")

    root = Path(__file__).resolve().parents[1]
    model = tmp_path / "model.bst"
    build_dummy_model(model)
    features = root / "features.json"
    expl = generate_explanations(
        str(p), model_path=str(model), features_path=str(features)
    )
    key = f"{tip['race']}|{tip['name']}"
    assert key in expl
    assert isinstance(expl[key], str)
    assert expl[key]
