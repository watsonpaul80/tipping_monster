import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from check_tip_sanity import check_tip_sanity


def test_warn_low_conf_missing_fields(tmp_path):
    tips = [
        {"race": "3:45 Ascot", "name": "A", "confidence": 0.4, "tags": []},
    ]
    assert any("Low confidence" in w for w in check_tip_sanity(tips))
    assert any("missing odds" in w for w in check_tip_sanity(tips))
    assert any("missing stake" in w for w in check_tip_sanity(tips))


def test_warn_nap_confidence(tmp_path):
    tips = [
        {
            "race": "1:00 A",
            "name": "B",
            "confidence": 0.9,
            "bf_sp": 4.0,
            "stake": 1.0,
            "tags": [],
        },
        {
            "race": "1:30 A",
            "name": "C",
            "confidence": 0.7,
            "bf_sp": 5.0,
            "stake": 1.0,
            "tags": ["Monster NAP"],
        },
    ]
    warns = check_tip_sanity(tips)
    assert any("NAP confidence" in w for w in warns)
