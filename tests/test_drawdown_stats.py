import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_drawdown_updates(tmp_path, monkeypatch):
    monkeypatch.setenv("TM_ROOT", str(tmp_path))
    import importlib

    import tippingmonster.utils as utils

    importlib.reload(utils)
    from roi import roi_tracker_advised as rta

    importlib.reload(rta)

    row1 = rta.update_drawdown_stats("2025-06-01", -1.0, -1.0)
    assert row1["CurrentLosingRun"] == 1
    assert row1["LongestLosingRun"] == 1
    assert row1["MaxDrawdown"] == 1.0

    row2 = rta.update_drawdown_stats("2025-06-02", -2.0, -3.0)
    assert row2["CurrentLosingRun"] == 2
    assert row2["LongestLosingRun"] == 2
    assert row2["MaxDrawdown"] == 3.0

    row3 = rta.update_drawdown_stats("2025-06-03", 1.0, -2.0)
    assert row3["CurrentLosingRun"] == 0
    assert row3["LongestLosingRun"] == 2
    assert row3["MaxDrawdown"] == 3.0

    df = rta.load_drawdown_stats()
    assert len(df) == 3
