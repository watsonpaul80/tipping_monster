import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from healthcheck_logs import check_logs


def test_check_logs_with_all_files(tmp_path):
    date = "2025-06-06"
    # create expected files
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True)
    (logs / "inference").mkdir(parents=True)
    (logs / "dispatch" / f"sent_tips_{date}.jsonl").write_text("ok")
    (logs / "inference" / f"pipeline_{date}.log").write_text("ok")
    (logs / "inference" / f"odds_0800_{date}.log").write_text("ok")
    (logs / "inference" / f"odds_hourly_{date}.log").write_text("ok")

    out_log = tmp_path / "healthcheck.log"
    os.chdir(tmp_path)
    missing = check_logs(out_log, date=date)
    assert missing == []
    assert out_log.read_text().strip().endswith("OK")


def test_check_logs_missing_file(tmp_path):
    date = "2025-06-06"
    # create some but not all
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True)
    (logs / "inference").mkdir(parents=True)
    (logs / "dispatch" / f"sent_tips_{date}.jsonl").write_text("ok")
    (logs / "inference" / f"pipeline_{date}.log").write_text("ok")
    # no odds files

    out_log = tmp_path / "healthcheck.log"
    os.chdir(tmp_path)
    missing = check_logs(out_log, date=date)
    assert len(missing) == 2
    text = out_log.read_text()
    assert "MISSING" in text
