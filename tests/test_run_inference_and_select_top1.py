import json
import runpy
import sys
import tarfile
import types
from datetime import date
from pathlib import Path

import numpy as np
import orjson
import pandas as pd


class DummyPlaceModel:
    def predict_proba(self, X):
        scores = X["score"].astype(float).values
        return np.vstack([1 - scores, scores]).T


def test_run_inference_selects_top_tip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # create dummy combined results for get_last_class
    (tmp_path / "rpscrape" / "data" / "regions" / "gb" / "foo").mkdir(parents=True)
    results_csv = (
        tmp_path / "rpscrape" / "data" / "regions" / "gb" / "foo" / "2015-2025.csv"
    )
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "course": ["A", "B"],
            "off": ["12:00", "13:00"],
            "class": [5, 2],
            "horse": ["HorseB", "HorseC"],
        }
    ).to_csv(results_csv, index=False)

    # create features.json and dummy model tarball
    features_json = tmp_path / "features.json"
    json.dump(["score"], open(features_json, "w"))
    meta_features = tmp_path / "meta_place_features.json"
    json.dump(["score"], open(meta_features, "w"))

    model_file = tmp_path / "tipping-monster-xgb-model.bst"
    model_file.write_text("")

    meta_model_file = tmp_path / "meta_place_model.pkl"
    import pickle

    with open(meta_model_file, "wb") as f:
        pickle.dump(DummyPlaceModel(), f)

    tar_path = tmp_path / "tipping-monster-xgb-model-test.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(features_json, arcname="features.json")
        tar.add(model_file, arcname="tipping-monster-xgb-model.bst")
        tar.add(meta_features, arcname="meta_place_features.json")
        tar.add(meta_model_file, arcname="meta_place_model.pkl")

    # create input jsonl
    input_file = tmp_path / "inputs.jsonl"
    with open(input_file, "w") as f:
        f.write(
            orjson.dumps(
                {
                    "race": "10:00 A",
                    "name": "HorseA",
                    "score": 0.3,
                    "trainer_rtf": 10,
                    "days_since_run": 8,
                    "class": 3,
                    "lbs": 140,
                    "form_score": 10,
                }
            ).decode()
            + "\n"
        )
        f.write(
            orjson.dumps(
                {
                    "race": "10:00 A",
                    "name": "HorseB",
                    "score": 0.8,
                    "trainer_rtf": 20,
                    "days_since_run": 8,
                    "class": 4,
                    "lbs": 130,
                    "form_score": 25,
                }
            ).decode()
            + "\n"
        )
        f.write(
            orjson.dumps(
                {
                    "race": "11:00 B",
                    "name": "HorseC",
                    "score": 0.7,
                    "trainer_rtf": 5,
                    "days_since_run": 200,
                    "class": 2,
                    "lbs": 140,
                    "form_score": 5,
                }
            ).decode()
            + "\n"
        )

    class FakeModel:
        def load_model(self, path):
            pass

        def predict_proba(self, X):
            scores = X["score"].astype(float).values
            return np.vstack([1 - scores, scores]).T

    fake_xgb = types.SimpleNamespace(XGBClassifier=lambda *a, **k: FakeModel())
    monkeypatch.setitem(sys.modules, "xgboost", fake_xgb)

    class FakeClient:
        def upload_file(self, *a, **k):
            pass

    fake_boto3 = types.SimpleNamespace(client=lambda *a, **k: FakeClient())
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run",
            "--model",
            str(tar_path),
            "--input",
            str(input_file),
        ],
    )

    script_path = (
        Path(__file__).resolve().parents[1]
        / "core"
        / "run_inference_and_select_top1.py"
    )
    runpy.run_path(str(script_path), run_name="__main__")

    output_file = tmp_path / "predictions" / date.today().isoformat() / "output.jsonl"
    rows = [orjson.loads(line) for line in output_file.read_text().splitlines()]
    assert len(rows) == 2

    race_a = next(r for r in rows if r["race"] == "10:00 A")
    assert race_a["name"] == "HorseB"
    assert abs(race_a["confidence"] - 0.8) < 1e-6
    assert abs(race_a["final_place_confidence"] - 0.8) < 1e-6
    assert "\U0001f9e0 Monster NAP" in race_a["tags"]
    assert "\U0001f7e2 Class Drop" in race_a["tags"]

    for row in rows:
        assert abs(row["global_max_confidence"] - 0.8) < 1e-6
