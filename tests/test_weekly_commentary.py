import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("shap", type("_Dummy", (), {}))
sys.modules.setdefault("xgboost", type("_Dummy", (), {}))
from roi.weekly_roi_summary import generate_commentary_block


def test_generate_commentary_block():
    df = pd.DataFrame(
        {
            "Date": ["2025-06-01", "2025-06-02", "2025-06-03"],
            "Profit": [1.0, -2.0, 3.0],
            "Stake": [1.0, 1.0, 1.0],
            "ROI": [100.0, -200.0, 300.0],
        }
    )
    text = generate_commentary_block(df)
    assert "2025-06-03" in text
    assert "2025-06-02" in text
    assert "rising" in text
