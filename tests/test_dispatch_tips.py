import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from dispatch_tips import calculate_monster_stake
from dispatch_tips import generate_tags, get_tip_composite_id


def test_calculate_monster_stake_above_threshold():
    stake = calculate_monster_stake(0.85, 4.0, min_conf=0.80)
    assert stake == 1.0


def test_calculate_monster_stake_below_threshold():
    stake = calculate_monster_stake(0.75, 4.0, min_conf=0.80)
    assert stake == 0.0


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
