import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# isort: off
from tippingmonster import (
    calculate_profit,
    logs_path,
    repo_path,
    repo_root,
    send_telegram_message,
    send_telegram_photo,
)

# isort: on


def test_send_telegram_message(monkeypatch):
    calls = {}

    def fake_post(url, data=None, timeout=None):
        calls["url"] = url
        calls["data"] = data
        calls["timeout"] = timeout

        class Resp:
            status_code = 200

        return Resp()

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    send_telegram_message("hi", token="TOK", chat_id="CID")
    assert calls["url"] == "https://api.telegram.org/botTOK/sendMessage"
    assert calls["data"]["chat_id"] == "CID"
    assert calls["data"]["text"] == "hi"


def test_send_telegram_photo(monkeypatch, tmp_path):
    calls = {}

    def fake_post(url, data=None, files=None, timeout=None):
        calls["url"] = url
        calls["data"] = data
        calls["files"] = files
        calls["timeout"] = timeout

        class Resp:
            status_code = 200

        return Resp()

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    photo = tmp_path / "img.png"
    photo.write_bytes(b"\x89PNG")
    send_telegram_photo(photo, "cap", token="TOK", chat_id="CID")

    assert calls["url"] == "https://api.telegram.org/botTOK/sendPhoto"
    assert calls["data"]["chat_id"] == "CID"
    assert calls["data"]["caption"] == "cap"
    assert "photo" in calls["files"]


def test_send_telegram_message_dev_mode(monkeypatch, tmp_path):
    calls = {}

    def fake_post(url, data=None, timeout=None):
        calls["called"] = True

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setenv("TM_DEV_MODE", "1")
    monkeypatch.setenv("TM_LOG_DIR", str(tmp_path / "logs/dev"))

    send_telegram_message("hello", token="TOK", chat_id="CID")
    assert "called" not in calls
    log_file = repo_path("logs", "dev", "telegram.log")
    assert log_file.exists()
    assert "hello" in log_file.read_text()


def test_send_telegram_photo_dev_mode(monkeypatch, tmp_path):
    calls = {}

    def fake_post(url, data=None, files=None, timeout=None):
        calls["called"] = True

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setenv("TM_DEV_MODE", "1")
    monkeypatch.setenv("TM_LOG_DIR", str(tmp_path / "logs/dev"))

    photo = tmp_path / "img.png"
    photo.write_bytes(b"\x89PNG")
    send_telegram_photo(photo, "hey", token="TOK", chat_id="CID")

    assert "called" not in calls
    log_file = repo_path("logs", "dev", "telegram.log")
    assert log_file.exists()
    assert "hey" in log_file.read_text()
    saved = repo_path("logs", "dev", "img.png")
    assert saved.exists()


def test_calculate_profit_win_and_place():
    row = {
        "Odds": 10.0,
        "Position": "1",
        "Stake": 1.0,
        "Runners": 10,
        "Race Name": "Some Hcp",
    }
    assert calculate_profit(row) == 5.0


def test_calculate_profit_place_only():
    row = {
        "Odds": 10.0,
        "Position": "2",
        "Stake": 1.0,
        "Runners": 10,
        "Race Name": "Some Hcp",
    }
    assert calculate_profit(row) == 0.5


def test_calculate_profit_simple_win():
    row = {"Odds": 3.0, "Position": "1", "Stake": 1.0}
    assert calculate_profit(row) == 2.0


def test_repo_and_logs_path_helpers():
    root = repo_root()
    assert root.is_dir()
    logs = logs_path("roi")
    assert logs == repo_path("logs", "roi")
    assert str(logs).endswith("logs/roi")


def test_logs_path_dev(monkeypatch):
    monkeypatch.setenv("TM_DEV_MODE", "1")
    p = logs_path("dispatch")
    assert str(p).endswith("logs/dev/dispatch")
