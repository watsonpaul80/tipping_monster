import runpy
from datetime import date, timedelta

import pytest
import tweepy

from tippingmonster import repo_path


def test_auto_tweet_dev_mode(tmp_path, monkeypatch):
    monkeypatch.chdir(repo_path())
    monkeypatch.setenv("TM_DEV_MODE", "1")
    monkeypatch.setenv("TM_LOG_DIR", str(tmp_path / "logs" / "dev"))

    today = date.today().isoformat()
    tips_file = repo_path("logs", "dispatch", f"sent_tips_{today}.jsonl")
    tips_file.parent.mkdir(parents=True, exist_ok=True)
    tips_file.write_text('{"race":"10:00 A","name":"Horse","confidence":0.9}\n')

    yday = (date.today() - timedelta(days=1)).isoformat()
    roi_file = repo_path("logs", "roi", f"tips_results_{yday}_advised.csv")
    roi_file.parent.mkdir(parents=True, exist_ok=True)
    roi_file.write_text("Stake,Profit\n1,1\n")

    calls = []

    class FakeAPI:
        def __init__(self, *args, **kwargs):
            pass

        def update_status(self, *args, **kwargs):
            calls.append(True)
            return type("Resp", (), {"id": 1})()

    monkeypatch.setattr(tweepy, "API", lambda auth: FakeAPI())

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(
            str(repo_path("monstertweeter", "auto_tweet_tips.py")),
            run_name="__main__",
        )
    assert exc.value.code == 0

    assert not calls
    log_file = repo_path("logs", "dev", "twitter.log")
    assert log_file.exists()
    assert "TIPPING MONSTER" in log_file.read_text()
