import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from tippingmonster.utils import (
    clear_conf_override,
    load_override_or_default,
    repo_path,
    set_conf_override,
)


def test_override_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("TM_ROOT", str(tmp_path))
    clear_conf_override()
    default = 0.8
    assert load_override_or_default(default) == default
    set_conf_override(0.3, hours_valid=1)
    assert load_override_or_default(default) == 0.3
    clear_conf_override()
    assert load_override_or_default(default) == default


def test_override_expiry(tmp_path, monkeypatch):
    monkeypatch.setenv("TM_ROOT", str(tmp_path))
    path = repo_path("config", "conf_override.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "min_conf_override": 0.25,
        "expires": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    }
    path.write_text(json.dumps(data))
    assert load_override_or_default(0.8) == 0.8
