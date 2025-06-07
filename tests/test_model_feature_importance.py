import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb

sys.path.append(str(Path(__file__).resolve().parents[1]))

from model_feature_importance import generate_chart


def test_generate_chart_closes_fig(tmp_path):
    X = pd.DataFrame({'a': [0, 1, 2], 'b': [1, 2, 3]})
    y = [0, 1, 0]
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X, y)

    model_path = tmp_path / 'model.bst'
    model.save_model(model_path)
    features_path = tmp_path / 'features.json'
    json.dump(list(X.columns), open(features_path, 'w'))
    data_path = tmp_path / 'data.jsonl'
    X.to_json(data_path, orient='records', lines=True)

    out = generate_chart(str(model_path), str(data_path), tmp_path / 'fi.png')
    assert out.exists()
    assert not plt.get_fignums()
