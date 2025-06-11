import os
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.archive_old_logs import archive_old_logs


def create_file(path: Path, days_old: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("log")
    ts = (datetime.now() - timedelta(days=days_old)).timestamp()
    os.utime(path, (ts, ts))


def test_archive_old_logs(tmp_path):
    logs = tmp_path / "logs"
    old_file = logs / "old.log"
    new_file = logs / "new.log"
    create_file(old_file, days_old=15)
    create_file(new_file, days_old=1)
    os.chdir(tmp_path)
    archive = archive_old_logs()
    assert archive is not None
    assert archive.exists()
    assert not old_file.exists()
    assert new_file.exists()
    with zipfile.ZipFile(archive) as zf:
        assert "old.log" in zf.namelist()


def test_archive_old_logs_none(tmp_path):
    logs = tmp_path / "logs"
    fresh = logs / "fresh.log"
    create_file(fresh, days_old=1)
    os.chdir(tmp_path)
    result = archive_old_logs()
    assert result is None
    assert fresh.exists()
