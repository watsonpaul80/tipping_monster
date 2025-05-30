---

# 🐎 TIPPING MONSTER MASTER BLUEPRINT (v6+)

## A Comprehensive System Overview

This document provides a detailed look into the Tipping Monster system, outlining its live production features, robust infrastructure, completed functionalities, and core logic, including the innovative Steam Sniper mode.

---

# 🧠 TIPPING MONSTER — CORE SYSTEM OVERVIEW (SPRUCED)

This document explains the logic, flow, scripts, and automation of the **core ML tipping engine** behind Tipping Monster. It handles: racecards, inference, Telegram tips, ROI tracking, and summary stats.

---

## 🏇 WHAT THE SYSTEM DOES

Tipping Monster is a fully automated machine learning system that:
- Pulls GB/IRE racecards via rpscrape
- Predicts the most likely winner in each race
- Formats and delivers tips to Telegram
- Tracks win/place results and calculates daily ROI
- Logs confidence bands and weekly summaries

---

## 🔄 DAILY WORKFLOW (5 AM to Midnight)

| Time  | Script                        | What it does |
|-------|-------------------------------|--------------|
| 05:00 | `daily_upload_racecards.sh`  | Pulls today’s racecards using `rpscrape` |
| 05:06 | `daily_flatten.sh`           | Flattens racecards to JSONL format for ML input |
| 08:00 | `fetch_betfair_odds.py`      | Grabs Betfair odds snapshot |
| 08:05 | `run_inference_and_select_top1.py` | Runs XGBoost model + selects best per race |
| 08:08 | `merge_odds_into_tips.py`    | Adds odds to predicted tips |
| 08:10 | `generate_commentary_bedrock.py` (optional) | Creates LLM-generated commentary |
| 08:12 | `dispatch_tips.py`           | Sends formatted tips to Telegram |
| 23:30 | `rpscrape` (results cron)    | Gets results for today’s races |
| 23:55 | `roi_tracker_advised_FIXED_v3.py` | Links tips to results and calculates profit |
| 23:59 | `send_daily_roi_summary.py` | Telegram message with daily win %, ROI, and profit |

---

## ⚙️ SCRIPT EXPLANATIONS

- `train_model_v6.py`: Trains an XGBoost classifier using features like rating, class, form, trainer, jockey, etc.
- `run_inference_and_select_top1.py`: Uses the model to predict a winner per race with confidence scores.
- `merge_odds_into_tips.py`: Adds price info to each runner in the tip file.
- `dispatch_tips.py`: Outputs NAPs, best bets, and high confidence runners into a formatted Telegram message.
- `roi_tracker_advised_FIXED_v3.py`: Matches tips with results and calculates each-way profit.
- `calibrate_confidence_daily.py`: Logs ROI by confidence bin (e.g. 0.80–0.90, 0.90–1.00).
- `weekly_roi_summary.py`: Aggregates weekly tips and profits.
- `generate_weekly_summary.py`: Outputs weekly performance in human-readable format.

---

## 💸 ROI TRACKING LOGIC

- ROI is tracked per confidence level and overall
- Stakes:
  - Singles: 1pt Win (or 0.5pt EW for longshots)
- Place terms:
  - <5 runners: Win Only
  - 5–7: 2 places @ 1/4 odds
  - 8+: 3 places @ 1/5 odds (or 3 places @ 1/4 for 12–15 runner handicaps, 4 @ 1/4 for 16+)

---

## 📡 TELEGRAM OUTPUT

- Channel: `-1002580022335`
- Tips sent in morning (by 08:15)
- ROI sent at 23:59
- Weekly summary sent Saturday night

---

## 🔐 FILE STRUCTURE

- `predictions/YYYY-MM-DD/` → holds `tips_with_odds.jsonl` and summaries
- `logs/monster_confidence_per_day_with_roi.csv` → stores per-band stats
- `logs/tips_results_YYYY-MM-DD.csv` → daily ROI output

---

## ✅ Live Features in Production (v6)

These core functionalities are currently **deployed and operating seamlessly** within your v6 system, delivering daily value.

* **Extensive Data Coverage:** Full GB/IRE Flat & Jumps training data for comprehensive insights.
* **Automated Data Ingestion:** Daily race results ingested from `rpscrape/data/dates/all/*.csv`.
* **Continuous Learning:** Self-training with past tip outcomes (`was_tipped`, `tip_profit`, `confidence_band`) ensures adaptive performance.
* **Smart Class Tracking:** Real-time class-drop tracking via `last_class` for identifying value.
* **Dual ROI Tracking:** Daily ROI tracking for both level and advised stakes provides a holistic view.
* **Confidence Analysis:** Detailed confidence band ROI logging and analysis for strategy refinement.
* **AI-Powered Commentary:** Automated commentary and tagging using advanced model features.
* **Full Automation:** Auto-cron for daily training and inference cycles.
* **Model Management:** Latest model detection, S3 upload, and prediction output streamlined.

---

## ⚙️ Infrastructure & Core Automation

The foundational elements and automated processes that power Tipping Monster are **robustly in place and fully operational**.

* **Python Environment:** Running on **Python 3.11.8** within a dedicated virtual environment for stability.
* **Daily Cron Pipeline:** A precisely timed automation schedule that orchestrates every critical stage of the system:
    * **`05:00`**: Racecard scrape
    * **`05:06`**: Flatten racecards
    * **`08:00`**: Fetch Betfair odds
    * **`08:05`**: Run ML inference
    * **`08:08`**: Merge tips with odds
    * **`08:10`**: Add LLM commentary (optional)
    * **`08:12`**: Dispatch tips to Telegram
    * **`23:30`**: Upload race results
    * **`23:55`**: Run ROI tracker
    * **`23:59`**: Send ROI summary to Telegram
    * **`23:56`**: Track bankroll and cumulative profit
* **Centralized Logging:** All system logs are meticulously saved under the `/logs/*.log` directory for easy monitoring and debugging.
* **Automated S3 Backups:** Daily zipped backup to S3 at `02:10 AM` using `backup_to_s3_zipped.sh`.
    * **Retention Policy:** Lifecycle rule ensures auto-deletion of backups older than **30 days**.
    * **Security:** AES-256 Server-side encryption is enabled for all backups.
    * **Location:** Backups stored in the `tipping-monster-backups` S3 bucket.
    * **Reliability:** Backups are periodically tested to ensure data integrity.

---

## ✨ Completed Tasks & Features

These features represent significant milestones, having been **fully implemented, tested, and marked as complete**.

* **ML Tip Generation:** Powered by XGBoost, generating intelligent tips from racecard data.
* **Data Preparation:** Flattened JSONL format for optimized inference input.
* **Odds Integration:** Seamless integration of Betfair odds snapshots.
* **Dynamic Staking:** A sophisticated confidence-based staking model for optimized betting.
* **Market Dynamics:** Advanced market mover & odds drift detection capabilities.
* **Telegram Dispatch:** Robust Telegram tip dispatch with rich formatting and efficient batching.
* **ROI Data Persistence:** ROI logging to `monster_confidence_per_day_with_roi.csv` for historical analysis.
* **Each-Way Profit Logic:** Accurate Each-Way profit calculation based on fluctuating odds.
* **Financial Tracking:** Comprehensive bankroll tracker with detailed CSV logs.
* **Telegram Channel Migration:** Successful migration to the new Telegram channel (ID: `-1002580022335`).
* **Full Automation:** All critical processes fully automated via cron jobs.
* **Tip Summaries:** Automated creation of `tips_summary.txt` files for quick overview.
* **Telegram ROI Summaries:** Automated daily ROI summaries sent via `send_roi_summary.py`.
* **Matching Accuracy:** Enhanced fuzzy horse name matching and time alignment for precise result linking.
* **Development Log:** All tracked tasks and changes logged in `TIPPING_MONSTER_TASKS.md`.

## 📣 Auto-Tweeting Tips to Twitter (monstertweeter module)

The `monstertweeter/auto_tweet_tips.py` script publishes all **daily Tipping Monster selections** to Twitter (X) as a thread. It runs automatically each morning (08:15 via cron) **after tips have been dispatched** to Telegram.

This system increases transparency and reach by making the Monster's free tips publicly visible on social media — without revealing paid content such as Sniper alerts.

### ✅ What It Does
- Posts a Twitter thread of all selections from `tips_with_odds.jsonl`
- Highlights the **NAP** (highest-confidence selection)
- Includes **yesterday’s ROI** from `logs/tips_results_YYYY-MM-DD_advised.csv`
- Excludes Sniper-only tips and anything under the public tipping threshold (e.g. confidence < 0.80)
- Branded with hashtags like `#TippingMonster` for growth and visibility

---

## 🧠 Auto-Tweet Fallback Logic (Planned)

### Problem
If **no tips meet the 0.80 confidence threshold**, the dispatch script doesn’t create `tips_with_odds.jsonl`, and no tweet is sent — even though tips may have been delivered or manually posted.

### ✅ What We Have Now
- Clean daily Twitter posts when tips exist
- ROI included from previous day
- Silent skip if `tips_with_odds.jsonl` is missing
- Logging and threading work reliably

### ❌ What’s Missing
- No fallback when tips are filtered out
- `logs/sent_tips_YYYY-MM-DD.jsonl` is not used by the Twitter module
- Creates gaps in public posting when the Telegram side was still active

### 🔧 What We Need to Solve
- Update `auto_tweet_tips.py` to fallback to `logs/sent_tips_*.jsonl` if `tips_with_odds.jsonl` is absent
- Tweet a message like: “📭 No tips today — Monster’s confidence was below threshold” if both are empty
- Ensure clear logging of fallback usage for transparency
- Preserve the discipline of the Monster while maintaining a daily public presence

---

### 🚀 Steam Sniper Mode (Fully Implemented)

An innovative feature designed to detect significant market movements and dispatch lucrative alerts for horses **not already tipped** by the main model.

* **🎯 Smart Mover Detection:** Identifies big Betfair price movers.
* **⏱️ Scheduled Monitoring:** Automated cron jobs at `12:00` or `13:00` for continuous market surveillance, managed by automated schedule + `at` jobs.
* **⚡️ Instant Alerts:** Sends tagged alerts (e.g., *"🥷 Steam Sniper: Al Ameen – 12/1 → 4/1"*) directly to Telegram.
* **📊 Odds Snapshots:** `Workspace_betfair_odds.py` supports `--label` for capturing specific odds snapshots.
* **⚖️ Odds Comparison:** `compare_odds_to_0800.py` is built and ready for comparing current odds to the 08:00 baseline.
* **📤 Sniper Dispatch:** `dispatch_snipers.py` is built and triggers Telegram alerts.
* **🔄 Job Management:** `load_sniper_jobs.sh` loads each snapshot into the `at` queue for scheduled execution.
* **📈 Performance Tracking:** `evaluate_steamers.py` logs results and calculates ROI for sniper picks.
* **🗓️ Weekly Summaries:** `steam_sniper_weekly_summary.py` provides a comprehensive weekly sniper ROI summary to Telegram.

---

## 📈 ROI Tracking – How It Works

Tipping Monster tracks daily and weekly performance using a **point-based ROI system**.

### 💡 Overview

- Every day, tip outcomes are compared with **Betfair SP odds**.
- ROI is calculated in both:
  - **Level mode** (1pt win/each-way per tip)
  - **Advised mode** (confidence-weighted staking from the model)
- The system tracks:
  - Tips count
  - Winners
  - Places (for each-way logic)
  - Profit in points
  - ROI %

Only tips with odds ≥ 5.0 are eligible for **each-way profit** to avoid false positives on short-odds places.

---

### 🛠️ Scripts Involved

| Script | Purpose |
|--------|---------|
| `roi_tracker_advised_FIXED_v3.py` | Main daily tracker – filters, calculates profit, generates tip results CSV |
| `weekly_roi_summary.py` | Rolls up recent tips into ISO week summaries for weekly ROI |
| `send_daily_roi_summary.py` | Posts a daily summary to Telegram with ROI and profit |
| `generate_tip_results_csv_with_mode_FINAL.py` | (Called by ROI tracker) Calculates wins, places, profit, ROI per tip |
| `logs/tips_results_YYYY-MM-DD_[level|advised].csv` | Stores per-day ROI breakdown |
| `logs/weekly_roi_summary.txt` | Used for Telegram weekly summary posts |
| `logs/monster_confidence_per_day_with_roi.csv` | (Optional) Aggregated confidence bin ROI, used for filtering insight |

---

### 📦 Key Data Files

| File | Description |
|------|-------------|
| `predictions/YYYY-MM-DD/tips_with_odds.jsonl` | Full output with model confidence and odds |
| `predictions/YYYY-MM-DD/tips_summary.txt` | Cleaned summary version used for subscribers |
| `logs/tips_results_*.csv` | Daily ROI performance logs |
| `logs/weekly_roi_summary.txt` | Aggregated weekly performance for Telegram |
| `logs/monster_confidence_per_day_with_roi.csv` | Confidence band win/place/profit ratios |

---

### ✅ Extra Features

- Confidence filtering (`--min_conf 0.80`) can be applied to hide low-quality tips
- ROI is calculated in **pts**, making it bankroll-agnostic (e.g. 1pt = £10 or £20)
- Place logic obeys racing rules:
  - 1/5 or 1/4 odds based on race type + runners
  - Win-only if fewer than 5 runners
---

## ⏰ Daily Automation Schedule (Detailed Overview)

| Time           | Component                        | What It Does                                      |
| :------------- | :------------------------------- | :------------------------------------------------ |
| `05:01`        | `build_sniper_schedule.py`       | Generates the daily sniper schedule.              |
| `05:02`        | `load_sniper_jobs.sh`            | Loads all sniper odds-check jobs into the `at` queue. |
| `08:00`        | `Workspace_betfair_odds.py`          | Captures the **baseline odds snapshot** (labeled `0800`). |
| `12:00+`       | `evaluate_steamers.py`           | Compares current odds to the 08:00 baseline to detect market movers. |
| `Rolling`      | `at` triggers sniper jobs        | Fetches and compares odds in real-time, then dispatches alerts to Telegram. |
| `23:40`        | `evaluate_steamers.py`           | Calculates ROI for sniper picks if race results are available. |
| `Sunday 23:50` | `steam_sniper_weekly_summary.py` | Sends a comprehensive 7-day ROI Telegram report for Steam Sniper. |

---

## 🧠 Steam Sniper — Core Logic

The Steam Sniper module is engineered to detect significant market movers that were **not already tipped** by the main model. It operates autonomously throughout the day, delivering sharp, "sniper-style" alerts to Telegram upon detection of strong price movements.

* **Baseline Creation:** At `08:00`, a crucial snapshot of Betfair odds is saved as `odds_snapshots/YYYY-MM-DD_0800.json`.
* **Live Snapshots:** As the day progresses, the system captures additional odds snapshots at strategic race-relative times (e.g., T–60, T–30, T–10 minutes before race start).
* **Dynamic Comparison:** Each new snapshot is rigorously compared against the 08:00 baseline using `compare_odds_to_0800.py`.
* **Intelligent Filtering:** Horses already tipped by the main model are automatically filtered out to avoid redundancy.
* **Trigger Mechanism:** If a horse's odds demonstrate a significant drop (e.g., from 10/1 to 5/1), it is immediately flagged as a **steamer**.
* **Instant Delivery:** Flagged steamers are swiftly dispatched via `dispatch_snipers.py` to Telegram, accompanied by a distinctive ⚡️ alert message.

---

## 🧾 Summary Reports

The Steam Sniper module generates detailed reports to keep you informed of its performance.

* **Daily Summary:** `generate_daily_steamer_summary.py` compiles a plain-text report, saved to:
    ```
    logs/steam_sniper_summary_YYYY-MM-DD.txt
    ```
    This report includes:
    * Number of steamers flagged.
    * Number of winners.
    * Flat-stake ROI for sniper picks.

* **Weekly Summary:** `steam_sniper_weekly_summary.py` aggregates all daily summaries to produce a comprehensive 7-day recap, which is then sent directly to Telegram.

---

## 🛠️ Useful Manual Commands (For Debugging/Specific Checks)

While the entire sniper stack is fully automated, these commands can be invaluable for manual checks or debugging:

```bash
# List today's sniper files:
ls steamers_$(date +%F)_*.json

# Check the number of steamers in a specific file (e.g., for 14:00 snapshot):
cat steamers_$(date +%F)_1400.json | jq length

# Manually fetch an odds snapshot (e.g., labeled 1400):
python fetch_betfair_odds.py --label 1400

# Manually detect steamers by comparing a specific snapshot to the 08:00 baseline:
python compare_odds_to_0800.py --snapshot odds_snapshots/<span class="math-inline">\(date \+%F\)\_1400\.json
\# Manually send steamer alerts from a specific source file\:
python dispatch\_snipers\.py \-\-source steamers\_</span>(date +%F)_1400.json

# Manually re-run ROI evaluation for a specific snapshot and date with debug info:
python evaluate_steamers.py --label 1400 --date $(date +%F) --debug

📌 Welcome to Tipping Monster 🧠🐎
Your data-driven tipster powered by machine learning and confidence tracking.

🔍 What You Get:
✅ Daily horse racing tips with confidence-based staking

📈 Live ROI tracking — no cherry-picking, just results

🧾 Weekly summaries posted every Sunday

💰 Last Week’s Results (2025-W21)
Level Stakes: +48.51 pts (ROI: +34.4%)

Advised Stakes: +48.51 pts (ROI: +34.4%)

🎯 Coming Soon: Monster Premium
🔐 Exclusive Nap tips

🧠 Market Movers mode

📊 Extra confidence analytics

You can now offer:

Tier	What’s Included	Price
Free	1–2 tips/day	£0
Starter	Monster picks only	£30–40/mo
Pro	Monster + Sniper	£59–79/mo
VIP	Pro + breakdowns + visual dashboards	£99/mo or £249/qtr