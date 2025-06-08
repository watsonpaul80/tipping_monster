import json
from pathlib import Path

import pandas as pd
import xgboost as xgb

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

    X = pd.DataFrame(
        {
            "draw": [2, 3],
            "or": [70, 71],
            "rpr": [120, 121],
            "lbs": [126, 127],
            "age": [5, 6],
            "dist_f": [8, 9],
            "class": [4, 4],
            "going": ["Good", "Good"],
            "prize": [5000, 6000],
        }
    )
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, [0, 1])
    model_path = tmp_path / "model.bst"
    model.save_model(model_path)
    features_path = tmp_path / "features.json"
    features_path.write_text(json.dumps(list(X.columns)))

    expl = generate_explanations(
        str(p), model_path=str(model_path), features_path=str(features_path)
    )
    key = f"{tip['race']}|{tip['name']}"
    assert key in expl
    assert isinstance(expl[key], str)
    assert expl[key]
