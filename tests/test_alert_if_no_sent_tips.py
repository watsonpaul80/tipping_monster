import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from alert_if_no_sent_tips import alert_if_no_sent_tips


def test_alert_when_missing(tmp_path):
    date = "2025-06-07"
    os.chdir(tmp_path)
    triggered = alert_if_no_sent_tips(date, sent_dir=Path('logs/dispatch'), alert_log=Path('alert.log'))
    assert triggered
    assert (tmp_path / 'alert.log').exists()


def test_no_alert_when_present(tmp_path):
    date = "2025-06-07"
    sent_dir = tmp_path / 'logs/dispatch'
    sent_dir.mkdir(parents=True)
    (sent_dir / f'sent_tips_{date}.jsonl').write_text('data')
    log_path = tmp_path / 'alert.log'
    triggered = alert_if_no_sent_tips(date, sent_dir=sent_dir, alert_log=log_path)
    assert not triggered
    assert not log_path.exists()
