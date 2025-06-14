# Quickstart Guide for Tipping Monster

This quickstart aims to help new contributors understand the overall structure of the **Tipping Monster** project and where to dive in.

## Repository Overview

*Tipping Monster* is an automated horse‑racing tipping system. The codebase includes scraping racecards, running a machine learning model to generate tips, fetching odds, sending formatted Telegram messages and tracking ROI.

A static landing page with a live tip feed is available at [site/index.html](../site/index.html).
Most detailed documentation lives in the `Docs/` directory. The main files are:

- `monster_overview.md` – full system overview with pipeline schedule and feature list.
- `ops.md` – operations guide describing cron jobs and data flows.
- `monster_todo.md` – detailed backlog for the tipping engine.
- `monster_todo_v2.md` – high-level roadmap for upcoming features.

## Project Structure

Key folders and scripts include:

- `rpscrape/` – scraper for racecards and results.
- ROI tracking scripts (e.g., `roi/roi_tracker_advised.py`, `roi/send_daily_roi_summary.py`) and `roi/run_roi_pipeline.sh` send performance updates via Telegram.
- `logs/` – organized logs for inference, ROI and dispatch processes.
- `predictions/` – daily output tips and summaries.
- Core scripts such as `core/run_pipeline_with_venv.sh`, `core/fetch_betfair_odds.py`, and `core/dispatch_tips.py` drive the daily pipeline.
 - `tmcli.py` – command-line helper with `pipeline`, `roi`, `sniper` and `healthcheck` commands. Run all `tmcli` commands from the repository root, e.g. `python tmcli.py pipeline --dev`.

Before running any scripts, set the environment variables listed in `Docs/README.md` (especially `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`). These allow the system to communicate with Telegram during live runs. Set `TM_DEV_MODE=1` to log Telegram and Twitter messages to `logs/dev/` instead of sending them.

A typical daily pipeline runs the following steps:

```
05:00  core/daily_upload_racecards.sh  # Pull racecards via rpscrape
05:06  core/daily_flatten.sh           # Flatten racecards for model input
08:00  core/fetch_betfair_odds.py      # Capture odds snapshot
08:05  python -m core.run_inference_and_select_top1  # Predict and select tips
08:08  core/merge_odds_into_tips.py    # Attach odds to tips
08:12  core/dispatch_tips.py           # Send tips to Telegram
08:13  generate_combos.py              # Suggest Monster doubles/trebles
23:30  rpscrape (results cron)         # Get results for today
23:55  roi/roi_tracker_advised.py      # Link tips to results and calc profit
23:59  roi/send_daily_roi_summary.py  # Telegram summary of ROI
```
These times are detailed in `Docs/monster_overview.md`.
*Note:* An optional commentary step exists, but the script is **proprietary and not included**.

## Key Scripts

- **Training:** `core/train_model_v6.py` and `core/train_modelv7.py` load historical data and produce an XGBoost model.
- **Model Comparison:** `core/compare_model_v6_v7.py` trains both versions side by side and logs confidence deltas.
- **Output Comparison:** `compare_model_outputs.py` runs two models on the same racecards and saves the differences in tip selection, confidence and feature impact.

- **Inference:** `core/run_inference_and_select_top1.py` chooses the most recent
  `tipping-monster-xgb-model-*.tar.gz` in the repository root and downloads it
  from S3 if a path is provided. If no model is available, the script exits with
  `FileNotFoundError`.
- **v8 Ensemble Training:** `core/train_monster_model_v8.py` builds the stacked
  model and saves `models/monster_v8_stack.tar.gz`.
- **v8 Ensemble Inference:** `core/run_inference_monster_v8.py` loads
  `models/monster_v8_stack.tar.gz` (downloaded on demand) and writes
  predictions to `predictions/<DATE>/output_v8.jsonl`.
- **Important:** run this script from the **repository root**:

```bash
python core/run_inference_and_select_top1.py
```
Running it while inside `core/` triggers a `ModuleNotFoundError` unless the repository root is on your `PYTHONPATH` or you run `python -m core.run_inference_and_select_top1`.
- **Odds Integration:** `core/fetch_betfair_odds.py` grabs odds snapshots; `core/merge_odds_into_tips.py` merges them with tips; `core/extract_best_realistic_odds.py` updates tips with the best available odds for ROI.
- **Dispatch & ROI:** `core/dispatch_tips.py` formats tips for Telegram. `roi/roi_tracker_advised.py` and `roi/send_daily_roi_summary.py` track daily performance and report ROI.
- **Explainability:** `model_feature_importance.py` plots SHAP values and can upload the chart to S3.
- **Steam Sniper:** Scripts like `build_sniper_schedule.py` detect market steamers from Betfair odds.

## Next Steps for Newcomers

1. **Read through `Docs/monster_overview.md`** to understand the full pipeline and feature set.
2. **Consult `Docs/ops.md`** for cron schedules and log locations. Ready-to-use
   templates live in `cron/prod.crontab` and `cron/dev.crontab`.
3. Explore the training scripts (`core/train_model_v6.py` and the experimental `train_monster_model_v8.py`) and their matching inference commands (`python -m core.run_inference_and_select_top1` or `python -m core.run_inference_monster_v8`). If you run these by path, ensure the repo root is on `PYTHONPATH` or use the module form above.
4. Review the ROI scripts (e.g., `roi/roi_tracker_advised.py`) and `roi/run_roi_pipeline.sh` to understand profit tracking.
5. Check the TODO lists in `Docs/monster_todo.md` and `Docs/TIPPING_MONSTER_ROI_TODO.md` for future work items.
6. Run `./utils/dev-check.sh` followed by `make test` to verify your setup.

With these files as a guide, you can get up to speed quickly and start contributing to the system.

*Note:* Older "sniper" scripts were removed in June 2025 to streamline the project.
