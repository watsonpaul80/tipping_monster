import json
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
import telegram_bot


def test_get_roi_summary(tmp_path):
    base = tmp_path
    (base / "logs" / "roi").mkdir(parents=True)
    csv = base / "logs" / "roi" / "tips_results_2025-06-01_advised.csv"
    df = pd.DataFrame(
        {"Position": [1, 2, 5], "Stake": [1.0, 1.0, 1.0], "Profit": [2.0, 0.5, -1.0]}
    )
    df.to_csv(csv, index=False)
    summary = telegram_bot.get_roi_summary("2025-06-01", base)
    assert summary == "ROI 2025-06-01: +1.50 pts (50.00%) from 3 tips"


def test_get_weekly_roi_summary(tmp_path):
    base = tmp_path
    (base / "logs" / "roi").mkdir(parents=True)

    df1 = pd.DataFrame(
        {"Position": [1, 2, 5], "Stake": [1.0, 1.0, 1.0], "Profit": [2.0, 0.5, -1.0]}
    )
    df2 = pd.DataFrame({"Position": [1, 5], "Stake": [1.0, 1.0], "Profit": [2.0, -1.0]})
    (base / "logs" / "roi" / "tips_results_2025-06-02_advised.csv").write_text(
        df1.to_csv(index=False)
    )
    (base / "logs" / "roi" / "tips_results_2025-06-03_advised.csv").write_text(
        df2.to_csv(index=False)
    )

    summary = telegram_bot.get_weekly_roi_summary("2025-06-03", base)
    assert "Week 2025-W23" in summary
    assert "(+2.50 pts" in summary or "+2.50 pts" in summary


def test_get_recent_naps(tmp_path):
    base = tmp_path
    for i in range(3):
        date = f"2025-06-0{i+1}"
        pred_dir = base / "predictions" / date
        pred_dir.mkdir(parents=True)
        nap = {
            "race": "1:00 Test",
            "name": f"Horse{i}",
            "tags": ["🧠 Monster NAP"],
            "confidence": 0.9,
            "bf_sp": 2.0,
        }
        with open(pred_dir / "tips_with_odds.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps(nap) + "\n")

        (base / "logs").mkdir(exist_ok=True)
        df = pd.DataFrame(
            {
                "Date": [date],
                "Race Time": ["1:00"],
                "Course": ["Test"],
                "Horse": [f"Horse{i}"],
                "Odds": [2.0],
                "Confidence": [0.9],
                "Position": [1 if i == 0 else 2],
                "Mode": ["advised"],
                "Stake": [1.0],
                "Profit": [1.0 if i == 0 else -1.0],
            }
        )
        df.to_csv(base / "logs" / f"tips_results_{date}_advised.csv", index=False)

    summary = telegram_bot.get_recent_naps(2, base)
    assert "Horse2" in summary
    assert "Horse1" in summary
    assert "ROI" in summary


def test_get_tip_info(tmp_path):
    base = tmp_path
    (base / "logs").mkdir()
    tip = {
        "race": "2:00 Test",
        "name": "Knebworth",
        "confidence": 0.85,
        "tags": ["🚀"],
        "commentary": "Nice chance",
        "bf_sp": 5.0,
    }
    with open(base / "logs" / "sent_tips_2025-06-07.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(tip) + "\n")

    summary = telegram_bot.get_tip_info("Knebworth", base)
    assert "2:00 Test" in summary
    assert "85.0%" in summary
    assert "🚀" in summary
    assert "Nice chance" in summary
    assert "5.0" in summary
