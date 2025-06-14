import argparse
import json
from typing import List, Tuple

import pandas as pd


def load_dataset(path: str) -> pd.DataFrame:
    """Load CSV or JSONL file into a DataFrame."""
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    elif path.lower().endswith(".jsonl") or path.lower().endswith(".json"):
        return pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported file type: {path}")


def validate_dataset_features(
    features: List[str], df: pd.DataFrame
) -> Tuple[List[str], List[str]]:
    """Return missing and extra feature columns compared to the DataFrame."""
    feature_set = set(features)
    data_set = set(df.columns)
    missing = sorted(feature_set - data_set)
    extra = sorted(data_set - feature_set)
    return missing, extra


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate dataset columns against features.json"
    )
    parser.add_argument("dataset", help="CSV or JSONL dataset file")
    parser.add_argument(
        "--features", default="features.json", help="Path to features.json"
    )
    args = parser.parse_args(argv)

    with open(args.features) as f:
        features = json.load(f)

    df = load_dataset(args.dataset)
    missing, extra = validate_dataset_features(features, df)

    if missing:
        print(f"Missing feature columns: {missing}")
    if extra:
        print(f"Extra columns not listed in features.json: {extra}")
    if not missing and not extra:
        print("All feature columns match the dataset.")

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
