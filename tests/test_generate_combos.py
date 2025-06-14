import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from generate_combos import generate_combo_messages


def test_generate_combo_messages_basic():
    tips = [
        {"race": "12:00 A", "name": "HorseA", "bf_sp": 5.0, "confidence": 0.97},
        {"race": "12:30 B", "name": "HorseB", "bf_sp": 3.0, "confidence": 0.92},
        {"race": "13:00 C", "name": "HorseC", "bf_sp": 4.0, "confidence": 0.91},
        {"race": "12:00 A", "name": "HorseD", "bf_sp": 2.0, "confidence": 0.95},
    ]

    msgs = generate_combo_messages(tips)
    assert len(msgs) == 2
    assert msgs[0].startswith("\U0001f9e0 Monster Double")
    assert "12:00 A" in msgs[0]
    assert "HorseB" in msgs[0]
    assert "@ 5.0" in msgs[0] or "@ 2.0" in msgs[0]
    assert msgs[1].startswith("\U0001f9e0 Monster Treble")
