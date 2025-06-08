import pandas as pd

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
