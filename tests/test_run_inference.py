import json
import pandas as pd
import pytest


def extract_race_sort_key(race: str) -> int:
    try:
        time_str, _course = race.split(maxsplit=1)
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except Exception:
        return 9999


def validate_features(df: pd.DataFrame, features_path) -> pd.DataFrame:
    with open(features_path) as f:
        model_features = json.load(f)
    missing = [f for f in model_features if f not in df.columns]
    if missing:
        print(f"\N{WARNING SIGN} Feature mismatch. Missing: {missing}")
        raise SystemExit(1)
    X = df[model_features]
    return X.apply(pd.to_numeric, errors="coerce").fillna(-1)


def test_feature_mismatch(tmp_path):
    features_path = tmp_path / "features.json"
    json.dump(["draw", "or"], open(features_path, "w"))
    df = pd.DataFrame([{"draw": 1, "race": "10:00 A"}])

    with pytest.raises(SystemExit):
        validate_features(df, features_path)


def test_races_sorted_by_time():
    df = pd.DataFrame([
        {"race": "12:30 Kempton", "confidence": 0.6},
        {"race": "11:00 Ascot", "confidence": 0.9},
        {"race": "NoTime", "confidence": 0.5},
    ])
    top = df.sort_values("confidence", ascending=False).groupby("race").head(1)
    top["sort_key"] = top["race"].apply(extract_race_sort_key)
    ordered = top.sort_values("sort_key")
    assert list(ordered["race"]) == ["11:00 Ascot", "12:30 Kempton", "NoTime"]

