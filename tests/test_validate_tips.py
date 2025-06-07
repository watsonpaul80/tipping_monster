import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from validate_tips import load_tips, validate_tips


def write_tips(tmp_path, tips):
    file = tmp_path / "tips.jsonl"
    with open(file, "w") as f:
        for t in tips:
            f.write(json.dumps(t) + "\n")
    return file


def test_valid_file(tmp_path):
    tips = [
        {
            "race": "1:00 A",
            "name": "Horse A",
            "confidence": 0.9,
            "bf_sp": 4.0,
            "tags": ["\U0001f9e0 Monster NAP", "\u2757 Confidence 90%+"],
        },
        {
            "race": "1:30 A",
            "name": "Horse B",
            "confidence": 0.8,
            "bf_sp": 6.0,
            "tags": [],
        },
    ]
    path = write_tips(tmp_path, tips)
    loaded = load_tips(path)
    assert validate_tips(loaded) == []


def test_missing_field(tmp_path):
    tips = [{"race": "1", "confidence": 0.5, "bf_sp": 5.0, "tags": []}]
    path = write_tips(tmp_path, tips)
    loaded = load_tips(path)
    errs = validate_tips(loaded)
    assert any("missing 'name'" in e for e in errs)


def test_duplicate_runner(tmp_path):
    tips = [
        {"race": "1", "name": "A", "confidence": 0.5, "bf_sp": 5.0, "tags": []},
        {"race": "1", "name": "A", "confidence": 0.6, "bf_sp": 4.0, "tags": []},
    ]
    path = write_tips(tmp_path, tips)
    errs = validate_tips(load_tips(path))
    assert any("duplicate runner" in e for e in errs)


def test_invalid_confidence_or_odds(tmp_path):
    tips = [{"race": "1", "name": "A", "confidence": 1.2, "bf_sp": -3, "tags": []}]
    path = write_tips(tmp_path, tips)
    errs = validate_tips(load_tips(path))
    assert any("invalid confidence" in e for e in errs)
    assert any("invalid odds" in e for e in errs)


def test_inconsistent_tags(tmp_path):
    tips = [
        {
            "race": "1",
            "name": "A",
            "confidence": 0.85,
            "bf_sp": 4.0,
            "tags": ["\U0001f9e0 Monster NAP", "\u2757 Confidence 90%+"],
        },
        {"race": "2", "name": "B", "confidence": 0.9, "bf_sp": 3.0, "tags": []},
    ]
    path = write_tips(tmp_path, tips)
    errs = validate_tips(load_tips(path))
    assert any("marked NAP" in e for e in errs)
    assert any("Confidence 90%+" in e for e in errs)
