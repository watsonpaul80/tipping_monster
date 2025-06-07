import sys
from pathlib import Path

import pandas as pd
import xgboost as xgb

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tippingmonster.helpers import generate_chart


def test_generate_chart(tmp_path):
    df = pd.DataFrame({"a": [1, 2, 3], "b": [2, 3, 4]})
    dtrain = xgb.DMatrix(df, label=[0, 1, 0])
    model = xgb.train({}, dtrain, num_boost_round=1)
    model_path = tmp_path / "model.bst"
    model.save_model(model_path)
    data_path = tmp_path / "data.csv"
    df.to_csv(data_path, index=False)
    out_path = tmp_path / "chart.png"
    generate_chart(str(model_path), str(data_path), out_path, telegram=False)
    assert out_path.exists()

