import os
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import tmcli


def test_tmcli_healthcheck(tmp_path):
    date = "2025-06-06"
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / f"sent_tips_{date}.jsonl").write_text("ok")
    (logs / f"pipeline_{date}.log").write_text("ok")
    (logs / f"odds_0800_{date}.log").write_text("ok")
    (logs / f"odds_hourly_{date}.log").write_text("ok")

    os.chdir(tmp_path)
    tmcli.main(["healthcheck", "--date", date, "--out-log", "hc.log"])
    text = (tmp_path / "hc.log").read_text().strip()
    assert text.endswith("OK")


def test_tmcli_ensure_sent_tips(tmp_path):
    date = "2025-06-06"
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)
    (pred_dir / "tips_with_odds.jsonl").write_text("tip")

    os.chdir(tmp_path)
    tmcli.main(["ensure-sent-tips", date, "--predictions-dir", "predictions", "--dispatch-dir", "logs/dispatch"])
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date}.jsonl"
    assert sent.exists()
    assert sent.read_text() == "tip"


def test_tmcli_model_feature_importance(tmp_path):
    import pandas as pd
    import xgboost as xgb
    import json

    X = pd.DataFrame({"a": [0, 1, 2, 3], "b": [1, 2, 3, 4]})
    y = [0, 1, 0, 1]
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, y)

    model_path = tmp_path / "model.bst"
    model.save_model(model_path)
    features_path = tmp_path / "features.json"
    json.dump(list(X.columns), open(features_path, "w"))
    data_path = tmp_path / "data.jsonl"
    X.to_json(data_path, orient="records", lines=True)

    os.chdir(tmp_path)
    tmcli.main([
        "model-feature-importance",
        "--model",
        str(model_path),
        "--data",
        str(data_path),
        "--out-dir",
        "logs/model",
    ])
    out = tmp_path / "logs/model" / f"feature_importance_{date.today().isoformat()}.png"
    assert out.exists()
