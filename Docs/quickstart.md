# Quickstart Guide for Tipping Monster

This quickstart aims to help new contributors understand the overall structure of the **Tipping Monster** project and where to dive in.

## Repository Overview

*Tipping Monster* is an automated horse‑racing tipping system. The codebase includes scraping racecards, running a machine learning model to generate tips, fetching odds, sending formatted Telegram messages and tracking ROI.

Most detailed documentation lives in the `Docs/` directory. The main files are:

- `monster_overview.md` – full system overview with pipeline schedule and feature list.
- `ops.md` – operations guide describing cron jobs and data flows.
- `monster_todo.md` and `sniper_todo.md` – feature roadmaps for the tipping engine and the Steam Sniper subsystem.

## Project Structure

Key folders and scripts include:

- `rpscrape/` – scraper for racecards and results.
- ROI tracking scripts (e.g., `roi_tracker_advised.py`, `send_daily_roi_summary.py`) and `run_roi_pipeline.sh` send performance updates via Telegram.
- `logs/` – organized logs for inference, ROI, dispatch and sniper processes.
- `predictions/` – daily output tips and summaries.
- Root‑level scripts such as `run_pipeline_with_venv.sh`, `fetch_betfair_odds.py`, and `dispatch_tips.py` drive the daily pipeline.

A typical daily pipeline runs the following steps:

```
05:00  daily_upload_racecards.sh  # Pull racecards via rpscrape
05:06  daily_flatten.sh           # Flatten racecards for model input
08:00  fetch_betfair_odds.py      # Capture odds snapshot
08:05  run_inference_and_select_top1.py  # Predict and select tips
08:08  merge_odds_into_tips.py    # Attach odds to tips
08:10  generate_commentary_bedrock.py (optional)
08:12  dispatch_tips.py           # Send tips to Telegram
23:30  rpscrape (results cron)    # Get results for today
23:55  roi_tracker_advised.py     # Link tips to results and calc profit
23:59  send_daily_roi_summary.py  # Telegram summary of ROI
```
These times are detailed in `Docs/monster_overview.md`.

## Key Scripts

- **Training:** `train_model_v6.py` and `train_modelv7.py` load historical data and produce an XGBoost model.
- **Inference:** `run_inference_and_select_top1.py` downloads the latest model, predicts on flattened racecards and uploads predictions.
- **Odds Integration:** `fetch_betfair_odds.py` grabs odds snapshots; `merge_odds_into_tips.py` merges them with tips; `extract_best_realistic_odds.py` updates tips with the best available odds for ROI.
- **Dispatch & ROI:** `dispatch_tips.py` formats tips for Telegram. `roi_tracker_advised.py` and `send_daily_roi_summary.py` track daily performance and report ROI.
- **Steam Sniper:** Scripts like `build_sniper_schedule.py` and `dispatch_snipers.py` detect market steamers from Betfair odds.

## Next Steps for Newcomers

1. **Read through `Docs/monster_overview.md`** to understand the full pipeline and feature set.
2. **Consult `Docs/ops.md`** for cron schedules and log locations.
3. Explore the training (`train_model_v6.py`) and inference (`run_inference_and_select_top1.py`) scripts to see how predictions are generated.
4. Review the ROI scripts (e.g., `roi_tracker_advised.py`) and `run_roi_pipeline.sh` to understand profit tracking.
5. Check the TODO lists in `Docs/monster_todo.md` and `Docs/TIPPING_MONSTER_ROI_TODO.md` for future work items.

With these files as a guide, you can get up to speed quickly and start contributing to the system.
