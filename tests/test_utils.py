import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tippingmonster import send_telegram_message, calculate_profit, repo_root, repo_path, logs_path


def test_send_telegram_message(monkeypatch):
    calls = {}

    def fake_post(url, data=None, timeout=None):
        calls['url'] = url
        calls['data'] = data
        calls['timeout'] = timeout
        class Resp:
            status_code = 200
        return Resp()

    import requests
    monkeypatch.setattr(requests, 'post', fake_post)

    send_telegram_message('hi', token='TOK', chat_id='CID')
    assert calls['url'] == 'https://api.telegram.org/botTOK/sendMessage'
    assert calls['data']['chat_id'] == 'CID'
    assert calls['data']['text'] == 'hi'


def test_calculate_profit_win_and_place():
    row = {
        'Odds': 10.0,
        'Position': '1',
        'Stake': 1.0,
        'Runners': 10,
        'Race Name': 'Some Hcp'
    }
    assert calculate_profit(row) == 5.0


def test_calculate_profit_place_only():
    row = {
        'Odds': 10.0,
        'Position': '2',
        'Stake': 1.0,
        'Runners': 10,
        'Race Name': 'Some Hcp'
    }
    assert calculate_profit(row) == 0.5


def test_calculate_profit_simple_win():
    row = {'Odds': 3.0, 'Position': '1', 'Stake': 1.0}
    assert calculate_profit(row) == 2.0


def test_repo_and_logs_path_helpers():
    root = repo_root()
    assert root.is_dir()
    logs = logs_path('roi')
    assert logs == repo_path('logs', 'roi')
    assert str(logs).endswith('logs/roi')
