#!/usr/bin/env python3
"""Add top SHAP features to each tip record."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import shap

from tippingmonster.utils import load_xgb_model


def load_model(model_path: str):
    """Return an XGBoost model from ``model_path`` supporting .gz/.b64."""
    data = Path(model_path).read_bytes()
    cleaned = model_path
    if cleaned.endswith(".b64"):
        data = base64.b64decode(data)
        cleaned = cleaned[:-4]
    if cleaned.endswith(".gz"):
        data = gzip.decompress(data)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bst")
    tmp.write(data)
    tmp.flush()
    tmp.close()
    model = load_xgb_model(tmp.name)
    os.unlink(tmp.name)
    return model


def load_tips(path: Path) -> List[Dict]:
    tips: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                tips.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return tips


def add_shap_info(tips: List[Dict], model_path: str, features_path: str) -> None:
    features = json.loads(Path(features_path).read_text())
    df = pd.DataFrame(tips)
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(-1)

    model = load_model(model_path)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    for idx, tip in enumerate(tips):
        values = shap_values[idx]
        top_idx = list(np.argsort(np.abs(values))[-5:][::-1])
        tip["shap_top"] = [
            {"feature": features[i], "value": float(values[i])} for i in top_idx
        ]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate per-tip SHAP features")
    parser.add_argument("tips", help="Path to tips JSONL")
    parser.add_argument(
        "--model",
        default="tipping-monster-xgb-model.bst.gz.b64",
        help="XGBoost model path",
    )
    parser.add_argument(
        "--features", default="features.json", help="Path to features list"
    )
    parser.add_argument(
        "--out",
        default="tips_with_shap.jsonl",
        help="Output JSONL with SHAP features",
    )
    args = parser.parse_args(argv)

    tips_path = Path(args.tips)
    out_path = Path(args.out)

    tips = load_tips(tips_path)
    if not tips:
        print(f"No tips found in {tips_path}")
        return 1

    add_shap_info(tips, args.model, args.features)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for tip in tips:
            json.dump(tip, f)
            f.write("\n")
    print(f"✅ SHAP explanations written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
