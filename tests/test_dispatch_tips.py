import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# isort: off
from core.dispatch_tips import (
    calculate_monster_stake,
    build_confidence_line,
    generate_tags,
    get_tip_composite_id,
    load_recent_roi_stats,
    select_nap_tip,
    should_skip_by_roi,
)

# isort: on


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
        "race": "12:00 Test",
        "name": "Runner",
        "confidence": 0.9,
        "bf_sp": 6.0,
        "realistic_odds": 4.0,
    }
    tags = generate_tags(tip, get_tip_composite_id(tip), 0.9)
    assert "🔥 Market Mover" in tags


def test_generate_tags_value_pick():
    tip = {
        "race": "12:00 Test",
        "name": "Runner",
        "confidence": 0.8,
        "bf_sp": 10.0,
        "value_score": 8.0,
    }
    tags = generate_tags(tip, get_tip_composite_id(tip), 0.8)
    assert "💰 Value Pick" in tags


def test_generate_tags_draw_advantage():
    tip = {
        "race": "12:00 Test",
        "name": "Runner",
        "confidence": 0.85,
        "draw_bias_rank": 0.8,
    }
    tags = generate_tags(tip, get_tip_composite_id(tip), 0.9)
    assert "📊 Draw Advantage" in tags


def test_generate_tags_stable_intent():
    tip = {
        "race": "12:30 Test",
        "name": "Horse",
        "confidence": 0.8,
        "stable_form": 25.0,
        "multi_runner": True,
        "class_drop_layoff": True,
    }
    tags = generate_tags(tip, get_tip_composite_id(tip), 0.9)
    assert "🔍 Stable Intent" in tags
    assert "🏠 Multiple Runners" in tags
    assert "⬇️ Class Drop Layoff" in tags


def _roi_csv(path, pnl):
    header = (
        "Date,Confidence Bin,Tips,Wins,Win %,Places,Place %,Win PnL,EW PnL (5.0+),"
        "Win ROI %,EW ROI %,Win Profit £,EW Profit £\n"
    )
    row = f"2025-06-01,0.70\u20130.80,10,1,10.0,1,10.0,{pnl},0.0,0.0,0.0,{pnl*10},0.0\n"
    path.write_text(header + row)


def test_should_skip_by_roi_negative(tmp_path):
    f = tmp_path / "roi.csv"
    _roi_csv(f, -5.0)
    stats = load_recent_roi_stats(f, "2025-06-30", 30)
    assert should_skip_by_roi(0.75, stats, 0.80)


def test_should_skip_by_roi_positive(tmp_path):
    f = tmp_path / "roi.csv"
    _roi_csv(f, 5.0)
    stats = load_recent_roi_stats(f, "2025-06-30", 30)
    assert not should_skip_by_roi(0.75, stats, 0.80)


def test_build_confidence_line_basic():
    tip = {
        "race": "1:00 Test",
        "name": "Runner",
        "confidence": 0.92,
        "bf_sp": 5.0,
        "tags": ["🔽 Class Drop", "⚡ Fresh"],
    }
    line = build_confidence_line(tip)
    assert line.startswith("\ud83e\udde0 Model Confidence: High (92%)")
    assert "class drop" in line and "fresh" in line
