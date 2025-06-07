from dispatch_tips import calculate_monster_stake
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_calculate_monster_stake_above_threshold():
    stake = calculate_monster_stake(0.85, 4.0, min_conf=0.80)
    assert stake == 1.0


def test_calculate_monster_stake_below_threshold():
    stake = calculate_monster_stake(0.75, 4.0, min_conf=0.80)
    assert stake == 0.0


def test_select_nap_tip_blocks_high_odds(tmp_path):
    tips = [
        {"name": "Longshot", "race": "1:00", "confidence": 0.99, "odds": 30.0},
        {"name": "Safe", "race": "1:30", "confidence": 0.95, "odds": 5.0},
    ]
    log_file = tmp_path / "nap.log"
    nap, conf = select_nap_tip(tips, odds_cap=21.0, log_path=str(log_file))
    assert nap["name"] == "Safe"
    assert log_file.exists()
    assert "Longshot" in log_file.read_text()


def test_select_nap_tip_override(tmp_path):
    tips = [
        {
            "name": "Longshot",
            "race": "1:00",
            "confidence": 0.99,
            "odds": 30.0,
            "override_nap": True,
        },
        {"name": "Safe", "race": "1:30", "confidence": 0.95, "odds": 5.0},
    ]
    log_file = tmp_path / "nap.log"
    nap, conf = select_nap_tip(tips, odds_cap=21.0, log_path=str(log_file))
    assert nap["name"] == "Longshot"
    assert not log_file.exists() or log_file.read_text() == ""


def test_select_nap_tip_normal(tmp_path):
    tips = [
        {"name": "A", "race": "1", "confidence": 0.9, "odds": 10.0},
        {"name": "B", "race": "2", "confidence": 0.8, "odds": 12.0},
    ]
    log_file = tmp_path / "nap.log"
    nap, conf = select_nap_tip(tips, odds_cap=21.0, log_path=str(log_file))
    assert nap["name"] == "A"
    assert not log_file.exists() or log_file.read_text() == ""


def test_select_nap_tip_all_blocked(tmp_path):
    tips = [
        {"name": "Longshot", "race": "1", "confidence": 0.9, "odds": 30.0},
        {"name": "Second", "race": "2", "confidence": 0.85, "odds": 25.0},
    ]
    log_file = tmp_path / "nap.log"
    nap, conf = select_nap_tip(tips, odds_cap=21.0, log_path=str(log_file))
    assert nap is None
    assert log_file.exists()
    assert "no replacement" in log_file.read_text().lower()


def test_generate_tags_with_delta():
    tip = {
        'race': '12:00 Test',
        'name': 'Runner',
        'confidence': 0.9,
        'bf_sp': 6.0,
        'realistic_odds': 4.0
    }
    tags = generate_tags(tip, get_tip_composite_id(tip), 0.9)
    assert '🔥 Market Mover' in tags
