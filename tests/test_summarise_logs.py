import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from summarise_logs import summarise_day


def test_summarise_day_complete(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    date = "2025-07-11"
    (logs / f"sent_tips_{date}.jsonl").write_text("{}\n")
    csv = logs / f"tips_results_{date}_advised.csv"
    csv.write_text("Position\n1\n2\n")
    (logs / f"roi_{date}.log").write_text("ok")

    line = summarise_day(date, logs)
    assert "✅" in line
    assert "2 tips" in line
    assert "1W 1P" in line
    assert line.endswith("ROI log ✅")


def test_summarise_day_missing_tips(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    date = "2025-07-11"
    line = summarise_day(date, logs)
    assert "Missing tips file" in line
