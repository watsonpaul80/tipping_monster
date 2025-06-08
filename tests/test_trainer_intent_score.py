import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from trainer_intent_score import trainer_intent_score


def test_trainer_intent_basic():
    score = trainer_intent_score(7, 50, 20, [6.0, 5.0, 4.5])
    assert round(score, 1) == 57.2


def test_trainer_intent_no_recency():
    score = trainer_intent_score(45, 20, 30, [4.0, 4.0, 5.0])
    assert round(score, 1) == 17.5
