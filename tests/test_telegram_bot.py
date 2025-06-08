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
