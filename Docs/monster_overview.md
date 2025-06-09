# 🧠 TIPPING MONSTER – MASTER SYSTEM OVERVIEW

This document outlines the Tipping Monster project including core automation, tip generation logic, product layers, and roadmap planning. It reflects the current v6 system along with v7 enhancements and the newly defined v8+ strategic expansion.

---

## 🎯 CORE FEATURES (v6 COMPLETE)

These core functionalities are currently **deployed and operating seamlessly** within the v6 system.

* ✅ Automated pipeline (racecard → tips → results → ROI)
* ✅ Confidence-based XGBoost ML model for tip generation
* ✅ Odds integration (Betfair snapshot)
* ✅ Tagging (e.g. Class Drop, In Form)
* (Optional) LLM commentary generation – script not included
* ✅ Tag-based commentary generation (ML-driven)
* ✅ LLM commentary generation (optional)
* ✅ Realistic odds injection
* ✅ Odds delta tracking for each tip
* ✅ Telegram dispatch logic with rich formatting and efficient batching
* ✅ ROI tracking (level + advised)
* ✅ Confidence calibration logger & detailed confidence band ROI logging
* ✅ Weekly and daily ROI summaries
* ✅ Sent vs unsent tip separation
* ✅ Full logging + S3 backup
* ✅ Organized log folders (`roi/`, `dispatch/`, `inference/`)
* ✅ Automatic log archiving of files older than 14 days
* ✅ Extensive Data Coverage: Full GB/IRE Flat & Jumps training data
* ✅ Automated Data Ingestion: Daily race results ingested from `rpscrape/data/dates/all/*.csv`.
* ✅ Continuous Learning: Self-training with past tip outcomes (`was_tipped`, `tip_profit`, `confidence_band`)
* ✅ Smart Class Tracking: Real-time class-drop tracking via `last_class`
* ✅ Model Management: Latest model detection, S3 upload, and prediction output streamlined. Trained models are stored in the `tipping-monster` S3 bucket and downloaded on demand.
* ✅ Data Preparation: Flattened JSONL format for optimized inference input
* ✅ Dynamic Staking: A sophisticated confidence-based staking model
* ✅ Market Dynamics: Advanced market mover & odds drift detection capabilities
* ✅ Value Score: `(confidence / bf_sp) * 100` highlights 💰 Value Picks
* ✅ Each-Way Profit Logic: Accurate Each-Way profit calculation based on fluctuating odds
* ✅ Financial Tracking: Comprehensive bankroll tracker with detailed CSV logs
* ✅ Drawdown Metrics: Daily and weekly ROI logs show bankroll and worst drawdown
* ✅ Tip Summaries: Automated creation of `tips_summary.txt` files
* ✅ Matching Accuracy: Enhanced fuzzy horse name matching and time alignment for precise result linking

---

## 🧩 TIP CATEGORIES (DEFINED IN `TIPPING_MONSTER_PRODUCTS.md`)

The system defines 8 core product layers:

1.  🧠 Monster Tips (Main)
2.  📋 Monster Tips (All Races)
3.  💸 Value Bets
4.  📉 Steamers
5.  🥈 Each-Way Specials
6.  🔗 Doubles & Trebles
7.  ⚠️ Danger Favs
8.  ❌ Monster Lay

---

## 🔁 AUTOMATION PIPELINE (Daily Workflow 5 AM to Midnight)

| Time  | Script                        | Purpose                                                    |
|-------|-------------------------------|------------------------------------------------------------|
| 05:00 | `core/daily_upload_racecards.sh`  | Pulls today’s racecards using `rpscrape`                 |
| 05:06 | `core/daily_flatten.sh`           | Flattens racecards to JSONL format for ML input       |
| 08:00 | `core/fetch_betfair_odds.py`      | Grabs Betfair odds snapshot                            |
| 08:05 | `python -m core.run_inference_and_select_top1` | Runs XGBoost model + selects best per race             |
| 08:08 | `core/merge_odds_into_tips.py`    | Adds odds to predicted tips                            |
| 08:09 | `generate_lay_candidates.py`      | Flags favourites with low Monster confidence |
| 08:10 | `dispatch_danger_favs.py`         | Sends Danger Fav alerts to Telegram |
| 08:10 | `export_lay_candidates_csv.py`    | Saves Danger Fav CSV summary |
| 08:11 | *(disabled)* `generate_commentary_bedrock.py` | Optional commentary step – script not included |
| 08:12 | `core/dispatch_tips.py`           | Sends formatted tips to Telegram                       |
| 08:13 | `generate_combos.py`              | Suggests doubles & trebles from top tips               |
| 23:30 | `rpscrape` (results cron)    | Gets results for today’s races                         |
| 23:55 | `roi/roi_tracker_advised.py`     | Links tips to results and calculates profit            |
| 23:56 | `generate_lay_candidates.py --results` | Logs Danger Fav outcomes to CSV |
| 23:59 | `roi/send_daily_roi_summary.py`  | Telegram message with daily win %, ROI, and profit |
Scripts are grouped under `core/` and `roi/` directories for clarity.

---

## ⚙️ SCRIPT EXPLANATIONS

* `core/train_model_v6.py`: Trains an XGBoost classifier using features like rating, class, form, trainer, jockey, etc.
* `train_place_model.py`: Predicts whether a runner finishes in the top 3 using the same feature set.
* `python -m core.run_inference_and_select_top1`: Uses the model to predict a winner per race with confidence scores. Run it from the repo root (or add the repo root to `PYTHONPATH`) so it can locate the `core` package.
* `core/merge_odds_into_tips.py`: Adds price info to each runner in the tip file.
* `core/dispatch_tips.py`: Outputs NAPs, best bets, and high confidence runners into a formatted Telegram message.
* `core/dispatch_all_tips.py`: Sends every generated tip for a day. Use `--telegram` to post to Telegram and `--batch-size` to control how many tips per message (ensure `TG_USER_ID` is set).
* `generate_combos.py`: Suggests doubles and trebles from 90%+ confidence tips.
* `roi/roi_tracker_advised.py`: Matches tips with results and calculates each-way profit. Also acts as the main daily tracker – filters, calculates profit, generates tip results CSV. Uses the `requests` library to send ROI summaries to Telegram.
* `roi/calibrate_confidence_daily.py`: Logs ROI by confidence bin (e.g. 0.80–0.90, 0.90–1.00).
* `roi/weekly_roi_summary.py`: Aggregates weekly tips and profits. Rolls up recent tips into ISO week summaries for weekly ROI.
* `roi/generate_weekly_summary.py`: Outputs weekly performance in human-readable format.
* `roi/generate_weekly_roi.py`: Creates `weekly_summary_YYYY-WW.csv` with ROI and strike rate for the week.
* `roi/generate_tip_results_csv_with_mode_FINAL.py`: (Called by ROI tracker) Calculates wins, places, profit, ROI per tip.
* `roi/send_daily_roi_summary.py`: Posts a daily summary to Telegram with ROI and profit.
* `core/trainer_stable_profile.py`: Computes 30-day win rate and ROI per trainer.
* `trainer_intent_profiler.py`: Adds stable-form tags to tips based on recent performance.

---

## 📈 PERFORMANCE TRACKING & ROI – HOW IT WORKS

Tipping Monster tracks daily and weekly performance using a **point-based ROI system**.

### 💡 Overview

* Every day, tip outcomes are compared with **Betfair SP odds**. (Note: Also uses best realistic odds from snapshots)
* ROI is calculated in both:
    * **Level mode** (1pt win/each-way per tip)
    * **Advised mode** (confidence-weighted staking from the model)
* The system tracks: Tips count, Winners, Places (for each-way logic), Profit in points, ROI %
* Only tips with odds ≥ 5.0 are eligible for **each-way profit** to avoid false positives on short-odds places.
* Supports each-way place terms.
* Confidence bands logged for ROI per bin.
* Weekly summaries in ISO format.
* `monster_confidence_per_day_with_roi.csv` logs band stats.

### Stakes and Place Terms from ROI Tracking Logic
* Stakes:
    * Singles: 1pt Win (or 0.5pt EW for longshots)
* Place terms:
    * <5 runners: Win Only
    * 5–7: 2 places @ 1/4 odds
    * 8+: 3 places @ 1/5 odds (or 3 places @ 1/4 for 12–15 runner handicaps, 4 @ 1/4 for 16+)

### 🛠️ Scripts Involved

| Script                                      | Purpose                                                                         |
|---------------------------------------------|---------------------------------------------------------------------------------|
| `roi/roi_tracker_advised.py`                    | Main daily tracker – filters, calculates profit, generates tip results CSV      |
| `roi/weekly_roi_summary.py`                     | Rolls up recent tips into ISO week summaries for weekly ROI                 |
| `roi/send_daily_roi_summary.py`                 | Posts a daily summary to Telegram with ROI and profit                       |
| `roi/generate_unified_roi_sheet.py` | Merges daily result CSVs into `unified_roi_sheet.csv` |
| `roi/nap_tracker.py` | Logs NAP ROI to `nap_history.csv` |
| `roi/generate_tip_results_csv_with_mode_FINAL.py` | (Called by ROI tracker) Calculates wins, places, profit, ROI per tip          |
| `logs/roi/tips_results_YYYY-MM-DD_[level\|advised].csv` | Stores per-day ROI breakdown                                          |
| `logs/roi/weekly_roi_summary.txt`               | Used for Telegram weekly summary posts                                    |
| `logs/roi/band_summary_<week>.csv`              | Weekly ROI per confidence band                                           |
| `logs/roi/daily_band_summary_<date>.csv`        | Daily ROI per confidence band                                            |
| `logs/roi/monster_confidence_per_day_with_roi.csv`  | (Optional) Aggregated confidence bin ROI, used for filtering insight        |

---

## 📈 ROI Pipeline – How It Works (Full Flow)

### 🧠 Purpose
Track daily and weekly ROI using **realistic odds** (from Betfair snapshots) and **true tip delivery logs**, ensuring accurate Telegram updates and subscriber trust.

---

### 🔄 Flow Summary

| Step | Time | Script | What It Does |
|------|------|--------|--------------|
| 1 | 22:50 | `extract_best_realistic_odds.py` | Injects best realistic odds into tip records from latest snapshot before race |
| 2 | 22:51 | `roi/roi_tracker_advised.py` (x2) | Generates `tips_results_DATE.csv` files for both `--mode advised` and `--mode level` |
| 3 | 22:52 | `roi/send_daily_roi_summary.py` | Sends formatted daily ROI summary to Telegram |
| 4 | Sunday 23:58 | `roi/weekly_roi_summary.py --telegram` | Sends full weekly ROI breakdown to Telegram |

---

### 🗂️ Files Used & Created

| File | Role |
|------|------|
| `logs/dispatch/sent_tips_DATE.jsonl` | Tips that were actually sent |
| `odds_snapshots/DATE_HHMM.json` | Source for realistic odds |
| `logs/dispatch/sent_tips_DATE_realistic.jsonl` | Tips with updated odds injected |
| `logs/roi/tips_results_DATE_[level\|advised].csv` | Main per-day ROI breakdown |
| `logs/roi/roi_telegram_DATE.log` | Output of Telegram ROI summary |
| `logs/roi/weekly_roi_summary.txt` | Human-friendly weekly Telegram output |
| `logs/roi/monster_confidence_per_day_with_roi.csv` | Confidence bin ROI stats for analysis |

---

### 🔧 Commands

Run manually:
```bash
# Daily ROI pipeline (default date = today)
bash roi/run_roi_pipeline.sh

# Weekly summary (current ISO week)
roi/weekly_roi_summary.py --week $(date +%G-W%V) --telegram
# or
python roi/weekly_roi_summary.py --week $(date +%G-W%V) --telegram
```

Automated by cron:
```cron
# 📊 ROI Pipeline (Realistic Odds → ROI → Telegram)
50 22 * * * bash utils/safecron.sh roi_pipeline /bin/bash roi/run_roi_pipeline.sh

# 📤 Weekly ROI Summary to Telegram
58 23 * * 0 bash utils/safecron.sh weekly_telegram /home/ec2-user/tipping-monster/.venv/bin/python roi/weekly_roi_summary.py --week $(date +\%G-W\%V) --telegram
# 📊 Weekly SHAP Feature Chart
55 23 * * 0 bash utils/safecron.sh model_features /home/ec2-user/tipping-monster/.venv/bin/python model_feature_importance.py --telegram
```

---

✅ **Status**  
All components live and working as intended:

✔️ Realistic odds now injected and used for ROI  
✔️ Daily tips filtered by sent tips file  
✔️ Advised + Level tracked separately  
✔️ Telegram summary sent nightly

---

## 📡 TELEGRAM OUTPUT

* Channel: `-1002580022335` (Successfully migrated)
* Tips sent in morning (by 08:15)
* ROI sent at 23:59
* Weekly summary sent Saturday night

---

## ⚙️ INFRASTRUCTURE & CORE AUTOMATION

The foundational elements and automated processes that power Tipping Monster are **robustly in place and fully operational**.

* **Python Environment:** Running on **Python 3.11.8** within a dedicated virtual environment for stability.
* **Daily Cron Pipeline:** A precisely timed automation schedule that orchestrates every critical stage of the system:
    * **`05:00`**: Racecard scrape
    * **`05:06`**: Flatten racecards
    * **`08:00`**: Fetch Betfair odds
    * **`08:05`**: Run ML inference
    * **`08:08`**: Merge tips with odds
    * **`08:10`**: *(disabled)* Add LLM commentary – script not included
    * **`08:12`**: Dispatch tips to Telegram
    * **`23:30`**: Upload race results
    * **`23:55`**: Run ROI tracker
    * **`23:59`**: Send ROI summary to Telegram
    * **`23:56`**: Track bankroll and cumulative profit
* **Centralized Logging:** All system logs are meticulously saved under the `/logs/*.log` directory for easy monitoring and debugging.
* **Automated S3 Backups:** Daily backup to S3 at `02:10 AM` using `utils/backup_to_s3.sh`.
    * **Retention Policy:** Lifecycle rule ensures auto-deletion of backups older than **30 days**.
    * **Security:** AES-256 Server-side encryption is enabled for all backups.
    * **Location:** Backups stored in the `tipping-monster-backups` S3 bucket.
* **Reliability:** Backups are periodically tested to ensure data integrity.

---

## 🔎 MODEL TRANSPARENCY & SELF‑TRAINING

Tipping Monster computes **SHAP** values for every prediction to highlight the
top features pushing a horse toward or away from being tipped. Global feature
importance is recorded during training, while per‑tip explanations feed into the
weekly ROI reports so subscribers see *why* each runner was selected.

Past tips are merged back into the dataset (`was_tipped`, `tip_profit`,
`confidence_band`) allowing the model to retrain on its own results. This
feedback loop continually refines accuracy and keeps the weekly insights fresh.

---

## 🚧 PLANNED ENHANCEMENTS

### 🔜 v7 Features
* SHAP-based tip explanations implemented via `dispatch_tips.py --explain`
* Confidence band filtering (Activate suppression logic based on band ROI performance)
* Premium tip tagging logic (Tag top 3 per day as Premium Tips)
* Dashboard enhancements (Visual dashboards - Streamlit / HTML)
* Tag-based ROI (ROI breakdown by confidence band, tip type, and tag)
* ✅ Logic-based commentary blocks (e.g., "📉 Class Drop, 📈 In Form, Conf: 92%")
* Parallel model comparison (v6 vs v7)
* Drawdown tracking in ROI logs

### 🔭 v8+ Expansion (Strategic)
* Trainer intent tracker (`trainer_intent_score.py`)
* Drift watcher
* Telegram replay builder
* Wildcard tips
* Self-training feedback loop
* Hall of Fame
* Tip memory tracking
* ✅ /roi and /nap bot commands (Also /stats)
* ✅ /tip bot command for horse info
* Commentary fine-tuning via GPT
* Telegram poll buttons
* Stake simulation modes
* Place-focused model (predict 1st–3rd)
* Confidence regression model (predict prob, not binary)
* ROI-based calibration (not just accuracy)
* Penalise stale horses and poor form
* ✅ Weekly ROI line chart (matplotlib) to logs
* Monetisation hooks (Stripe, Patreon, etc.)

---

## 📁 FOLDER STRUCTURE

| Folder                      | Purpose            |
|-----------------------------|--------------------|
| `predictions/YYYY-MM-DD/`   | Tips + summaries |
| `logs/`                     | Main directory for categorized log subfolders (roi, dispatch, inference, etc.) |
| `odds_snapshots/`           | Betfair snapshots  |

---

## ✅ FILES TO REFERENCE

* `monster_todo.md` – full backlog + roadmap
* `monster_todo_v2.md` – high-level roadmap for upcoming features
* `TIPPING_MONSTER_PRODUCTS.md` – tip product layer logic
* `logs/roi/tips_results_*.csv` – ROI by day
* `logs/dispatch/sent_tips_*.jsonl` – actual sent Telegram tips
* `logs/roi/monster_confidence_per_day_with_roi.csv` – bin tracking
* `monster_changelog.md` – versioned updates if added
* `TIPPING_MONSTER_TASKS.md` - Development log for tracked tasks and changes (Note: `monster_todo.md` is the primary task list)


📊 ROI Tracking – Overview
The Tipping Monster system has a full-stack ROI pipeline that tracks performance at every level. It captures ROI for both public-facing sent tips and internal all tips to allow deep analysis, performance tuning, and monetisation reporting.

🧠 ROI Modes
Mode	Description
advised	ROI using variable stakes per tip
level	(Deprecated) Fixed-stake ROI per tip

We're now focused solely on advised mode for all ROI tracking.

🗂️ ROI Scripts
Script	Purpose	Scope
roi/tag_roi_tracker.py	Tracks ROI by tag	✅ Sent + All tips
roi/send_daily_roi_summary.py	Sends daily Telegram ROI	✅ Sent only
roi/roi_tracker_advised.py	CLI tracker for daily PnL	✅ Sent only
roi/weekly_roi_summary.py	Weekly Telegram summary	✅ Sent only
roi/generate_tip_results_csv_with_mode_FINAL.py	Saves core results CSVs	✅ Sent only
calibrate_confidence_daily.py	Tracks confidence band ROI	✅ All tips
roi_by_confidence_band.py       Aggregates ROI by confidence band ✅ Sent only
simulate_staking.py            Simulates staking strategies (level/conf/value) ✅ All tips
win_rate_by_tag.py             Overall win % and ROI per tag    ✅ All tips
unified_roi_sheet.csv	Unified log for all tips	✅ All tips

📄 ROI Output Files
File	Description
logs/roi/tips_results_YYYY-MM-DD_advised_sent.csv	ROI per tip (only sent tips)
logs/roi/tips_results_YYYY-MM-DD_advised_all.csv	ROI per tip (all tips)
logs/roi/tag_roi_summary_sent.csv	ROI by tag for sent tips
logs/roi/tag_roi_summary_all.csv	ROI by tag for all tips
logs/roi/monster_confidence_per_day_with_roi.csv	ROI by confidence bin
logs/roi/roi_by_confidence_band_sent.csv        ROI by confidence band
logs/roi/unified_roi_sheet.csv	Full tip log with Date/Week/Month
logs/roi/staking_simulation.png Profit curves for staking simulations

🔍 Analysis Levels
Daily ROI and summary

Weekly breakdown with per-day win/place/profit stats

By tag: ROI and profit for every tag (🔥 Trainer %, ❗ Confidence, etc.)

By confidence: ROI tracking across confidence bands

By send status: Can compare sent vs unsent performance

By time: Week/month fields embedded in final spready


---

📅 Updated: 2025-06-01.
