from pathlib import Path
import os
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))

from extract_best_realistic_odds import extract_race_key


def test_extract_race_key_normal_case():
    minutes, course = extract_race_key("15:30 Chelmsford")
    assert minutes == 15 * 60 + 30
    assert course == "chelmsford"


def test_extract_race_key_with_extra_spaces():
    minutes, course = extract_race_key(" 15:30   Chelmsford ")
    assert minutes is None and course is None


def test_extract_race_key_missing_space_returns_none():
    minutes, course = extract_race_key("15:30Chelmsford")
    assert minutes is None and course is None


def test_extract_race_key_bad_time_returns_none():
    minutes, course = extract_race_key("15-30 Chelmsford")
    assert minutes is None and course is None


def test_extract_race_key_empty_course_returns_none():
    minutes, course = extract_race_key("15:30   ")
    assert minutes is None and course is None

