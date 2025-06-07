import pandas as pd
from core.validate_features import validate_dataset_features


def test_validate_dataset_features_extra_and_missing():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    missing, extra = validate_dataset_features(["a", "b", "d"], df)
    assert missing == ["d"]
    assert extra == ["c"]


def test_validate_dataset_features_perfect_match():
    df = pd.DataFrame({"x": [1], "y": [2]})
    missing, extra = validate_dataset_features(["x", "y"], df)
    assert missing == []
    assert extra == []
