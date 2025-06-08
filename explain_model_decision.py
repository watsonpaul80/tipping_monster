import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import shap

from tippingmonster.utils import load_xgb_model


def load_model(model_path: str):
    """Load an XGBoost model from ``model_path`` (supports .bst or .bst.gz)."""
    return load_xgb_model(model_path)


def load_features(path: str) -> list[str]:
    """Return the list of model features from ``path``."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_explanations(
    predictions_path: str,
    model_path: str = "tipping-monster-xgb-model.bst.gz",
    features_path: str = "features.json",
    top_n: int = 3,
) -> Dict[str, str]:
    """Return a mapping of ``tip_id`` to a short SHAP-based explanation."""
    with open(predictions_path, "r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    if not rows:
        return {}

    df = pd.DataFrame(rows)
    features = load_features(features_path)
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)

    model = load_model(model_path)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    explanations: Dict[str, str] = {}
    for idx, row in df.iterrows():
        values = shap_values[idx]
        abs_vals = np.abs(values)
        top_idx = abs_vals.argsort()[-top_n:][::-1]
        parts = [f"{features[i]}{'↑' if values[i] > 0 else '↓'}" for i in top_idx]
        tip_id = f"{row.get('race','')}|{row.get('name','')}"
        explanations[tip_id] = ", ".join(parts)
    return explanations


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SHAP explanations")
    parser.add_argument("--predictions", required=True, help="Path to tips JSONL")
    parser.add_argument("--model", default="tipping-monster-xgb-model.bst.gz")
    parser.add_argument("--features", default="features.json")
    parser.add_argument("--out", help="Output JSON file")
    args = parser.parse_args()

    exps = generate_explanations(
        args.predictions, model_path=args.model, features_path=args.features
    )
    if args.out:
        Path(args.out).write_text(json.dumps(exps, indent=2))
    else:
        print(json.dumps(exps, indent=2))
