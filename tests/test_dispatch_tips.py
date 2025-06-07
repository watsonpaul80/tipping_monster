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
