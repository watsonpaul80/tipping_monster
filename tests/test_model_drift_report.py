import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta # Import timedelta explicitly for the test

from model_drift_report import generate_report


def test_model_drift(tmp_path):
    local_dir = tmp_path / "shap"
    local_dir.mkdir()
    dates = ["2025-06-04", "2025-06-05", "2025-06-06"]

    pd.DataFrame(
        {
            "feature": ["A", "B", "C", "D"],
            "importance": [0.4, 0.3, 0.2, 0.1],
        }
    ).to_csv(local_dir / f"{dates[0]}_shap.csv", index=False)

    pd.DataFrame(
        {
            "feature": ["A", "B", "C", "D"],
            "importance": [0.41, 0.31, 0.2, 0.08],
        }
    ).to_csv(local_dir / f"{dates[1]}_shap.csv", index=False)

    pd.DataFrame(
        {
            "feature": ["C", "E", "B", "A"],
            "importance": [0.5, 0.4, 0.3, 0.2],
        }
    ).to_csv(local_dir / f"{dates[2]}_shap.csv", index=False)

    out_md = tmp_path / "report.md"
    
    with patch("model_drift_report.datetime") as dt:
        dt.utcnow.return_value = datetime(2025, 6, 6)
        dt.timedelta = timedelta
        dt.date = datetime.date
        dt.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)


    # Verify all SHAP files exist before running the report
    for date in dates:
        shap_file = local_dir / f"{date}_shap.csv"
        assert shap_file.exists(), f"Missing SHAP file: {shap_file}"

    # Freeze today's date so test is deterministic without mocking datetime methods
    class Fixed(datetime):
        @classmethod
        def utcnow(cls):  # type: ignore[override]
            return datetime(2025, 6, 6)

        @classmethod
        def today(cls):
            return cls.utcnow().date() # Ensure .today() also returns the fixed date

        # We also need to mock strptime if it's used directly on the datetime object
        # but in model_drift_report, pd.to_datetime is used which handles patching internally
        # However, it's good practice to ensure timedelta is available if datetime is mocked.
        # Although in the current model_drift_report, timedelta is imported directly.
        # For robustness, we'll ensure it behaves as expected if datetime is a parent.

    import model_drift_report as mdr

    orig_dt = mdr.datetime
    # Assign the Fixed class to the datetime object within the module being tested
    mdr.datetime = Fixed
    try:
        generate_report(days=3, local_dir=str(local_dir), out_md=str(out_md))
    finally:
        # Restore the original datetime object to avoid side effects on other tests
        mdr.datetime = orig_dt

    text = out_md.read_text()
    assert "Spearman" in text
    assert "❗" in text
