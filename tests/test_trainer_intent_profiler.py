import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from trainer_intent_profiler import tag_tips


def test_tag_tips_flags():
    tips = [
        {
            "race": "1:00 Test",
            "name": "A1",
            "trainer": "A",
            "class": "4",
            "last_class": "5",
            "days_since_run": 70,
        },
        {
            "race": "1:00 Test",
            "name": "A2",
            "trainer": "A",
            "class": "4",
            "last_class": "5",
            "days_since_run": 70,
        },
    ]
    trainer_form = {"A": 25.0}
    tagged = tag_tips(tips, trainer_form)
    for row in tagged:
        assert "🔍 Stable Intent" in row["tags"]
        assert "🏠 Multiple Runners" in row["tags"]
        assert "⬇️ Class Drop Layoff" in row["tags"]
        assert row["stable_form"] == 25.0
