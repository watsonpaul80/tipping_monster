import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.codex_logger import log_action


def test_log_action_creates_file(tmp_path):
    log_path = tmp_path / 'logs' / 'codex.log'
    result = log_action('hello world', log_path=log_path)
    assert result == log_path
    assert log_path.exists()
    text = log_path.read_text().strip()
    assert 'hello world' in text


def test_log_action_appends(tmp_path):
    log_path = tmp_path / 'logs' / 'codex.log'
    log_action('first', log_path=log_path)
    log_action('second', log_path=log_path)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2
    assert lines[0].endswith('first')
    assert lines[1].endswith('second')
