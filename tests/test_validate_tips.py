import json

from utils.validate_tips import validate_tips


def test_validate_tips_ok(tmp_path):
    date = "2025-06-06"
    pred = tmp_path / "predictions" / date
    pred.mkdir(parents=True)
    tip = {"name": "Runner", "race": "12:00 Test", "confidence": 0.9}
    (pred / "tips_with_odds.jsonl").write_text(json.dumps(tip) + "\n")
    assert validate_tips(date, tmp_path / "predictions")


def test_validate_tips_missing(tmp_path):
    date = "2025-06-06"
    pred = tmp_path / "predictions" / date
    pred.mkdir(parents=True)
    tip = {"name": "Runner"}
    (pred / "tips_with_odds.jsonl").write_text(json.dumps(tip) + "\n")
    assert not validate_tips(date, tmp_path / "predictions")
