# 📊 Tipping Monster – ROI Tracking Overview

This document outlines how ROI is tracked, logged, and reported across the Tipping Monster system.

## ✅ Scope
ROI is tracked across the following dimensions:
- Sent Tips (publicly dispatched)
- All Tips (selected by model, even if not sent)
- Tag-based breakdown (e.g. 🔥 Trainer %, ❗ Confidence 90%)
- Confidence band buckets (e.g. 0.80–0.89, 0.90+)
- Daily, weekly, and monthly time slices

## 🛠️ Main Components

| Script | Description |
|--------|-------------|
| `extract_best_realistic_odds.py` | Applies realistic odds to tips from snapshot |
| `generate_tip_results_csv_with_mode_FINAL.py` | Creates ROI-per-tip logs with profit calculations |
| `tag_roi_tracker.py` | Builds tag ROI summaries for both sent and all tips |
| `calibrate_confidence_daily.py` | Tracks ROI per confidence band daily |
| `weekly_roi_summary.py` | Sends weekly Telegram summary |
| `send_daily_roi_summary.py` | Sends daily Telegram summary (sent tips only) |
| | `unified_roi_sheet.csv` | Merges tip logs with tip, stake, odds, ROI, tag, confidence, and date metadata |

## 🧾 Output Files

- `tips_results_YYYY-MM-DD_advised_all.csv`
- `tips_results_YYYY-MM-DD_advised_sent.csv`
- `tag_roi_summary_all.csv`
- `tag_roi_summary_sent.csv`
- `monster_confidence_per_day_with_roi.csv`
- `weekly_summary.csv`

These are ready for pivoting, filtering, and dashboard integration.

## 📺 Dashboards
- *Streamlit dashboards planned*, including:
  - Paul's View: deep ROI filtering by tag, confidence, date
  - Member-facing view: simplified sent tip ROI
