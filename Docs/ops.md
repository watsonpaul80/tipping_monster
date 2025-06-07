# Operations Guide (ops.md)

This document provides an overview of the operational aspects of the Tipping Monster system, including scheduled tasks and data flows.

## Scheduled Tasks (Cron Jobs)

The system relies on a series of cron jobs to perform regular tasks. Below is a breakdown of these jobs, their schedules, and their purposes.

**Key:**
- **Frequency:** When the job runs.
- **Purpose:** What the job does.
- **Command:** The actual command executed.
- **Log Output:** Where the primary output or errors of the cron command itself are logged (if specified). Internal script logging is now more organized within `logs/` subdirectories.

> **Environment Note:** Telegram alerts depend on `TELEGRAM_BOT_TOKEN` and
> `TELEGRAM_CHAT_ID` being set. Export these variables wherever cron runs (e.g.,
> in your crontab or shell profile).

---

### Core Pipeline & Odds Fetching

1.  **Run Main Pipeline (`run_pipeline_with_venv.sh`)**
    *   **Frequency:** Daily at 05:00
    *   **Purpose:** Executes the main data processing and tipping pipeline. This likely involves fetching racecards, running predictions, selecting tips, and preparing them for dispatch.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh pipeline /bin/bash /home/ec2-user/tipping-monster/run_pipeline_with_venv.sh`
    *   **Internal Logs:** Check `logs/inference/`, `logs/dispatch/` for detailed logs from this pipeline.

2.  **Fetch Betfair Odds (Hourly)**
    *   **Frequency:** Hourly between 07:05 and 20:05
    *   **Purpose:** Fetches updated odds from Betfair. This is crucial for monitoring market changes and potentially for features like "sniper" alerts or odds comparison.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh odds_hourly /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/fetch_betfair_odds.py`

---

### Results, Calibration & ROI

_All ROI-related scripts now live in the project root. The previous `ROI/` directory was removed during consolidation._

3.  **Upload Daily Results (`daily_upload_results.sh`)**
    *   **Frequency:** Daily at 22:30
    *   **Purpose:** Uploads race results from the day. These results are essential for calculating ROI and model performance.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh upload_results /bin/bash /home/ec2-user/tipping-monster/daily_upload_results.sh`

4.  **Calibrate Confidence Daily (`calibrate_confidence_daily.py`)**
    *   **Frequency:** Daily at 22:45
    *   **Purpose:** Runs the daily confidence calibration process, likely adjusting model confidence scores based on recent performance.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh calibrate_conf /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/calibrate_confidence_daily.py`
    *   **Internal Logs:** Check `logs/inference/` for calibration logs.

5.  **Run ROI Pipeline (`run_roi_pipeline.sh`)**
    *   **Frequency:** Daily at 22:50
    *   **Purpose:** Executes the ROI (Return on Investment) calculation pipeline. This likely processes sent tips and their results to generate ROI statistics.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh roi_pipeline /bin/bash /home/ec2-user/tipping-monster/run_roi_pipeline.sh`
    *   **Internal Logs:** Check `logs/roi/` for detailed ROI logs.

6.  **Generate Master Subscriber Log & Upload (`generate_subscriber_log.py`)**
    *   **Frequency:** Daily at 22:30
    *   **Purpose:** Generates the `master_subscriber_log.csv` file (now in `logs/roi/`) which tracks all tips, results, and running profit, then uploads it to S3.
    *   **Command:** `/home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/generate_subscriber_log.py --date $(date +\%F) && aws s3 cp /home/ec2-user/tipping-monster/logs/roi/master_subscriber_log.csv s3://tipping-monster-data/master_subscriber_log.csv`
    *   **Note:** Ensure this crontab line is updated as per `Docs/instructions.md`.

7.  **Generate Weekly Summary CSV (`generate_weekly_summary.py`)**
    *   **Frequency:** Weekly, Sunday at 22:59
    *   **Purpose:** Generates a CSV summary of the week's tipping performance.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh weekly_summary /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/generate_weekly_summary.py`
    *   **Internal Logs:** Likely writes to `logs/roi/`.

8.  **Send Weekly ROI to Telegram (`weekly_roi_summary.py`)**
    *   **Frequency:** Weekly, Sunday at 23:58
    *   **Purpose:** Sends a summary of the week's ROI to a Telegram channel.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh weekly_telegram /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/weekly_roi_summary.py --week $(date +\%G-W\%V) --telegram`

---

### System Maintenance

9.  **Backup to S3 (`backup_to_s3.sh`)**
    *   **Frequency:** Daily at 02:10
    *   **Purpose:** Backs up the entire application directory (presumably excluding certain files/dirs) to an S3 bucket.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh backup /bin/bash /home/ec2-user/tipping-monster/backup_to_s3.sh`

10. **Upload Logs to S3 (`upload_logs_to_s3.sh`)**
    *   **Frequency:** Daily at 04:00
    *   **Purpose:** Uploads the `logs/` directory (and its new subdirectories) to S3.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh upload_logs /bin/bash /home/ec2-user/tipping-monster/upload_logs_to_s3.sh`

11. **Delete Old Log Files**
    *   **Frequency:** Daily at 03:00
    *   **Purpose:** Deletes `.log` files older than 14 days from `logs/` and its subdirectories.
    *   **Command:** `find /home/ec2-user/tipping-monster/logs/ -type f -name "*.log" -mtime +14 -delete`
    *   **Note:** Ensure this crontab line is updated as per `Docs/instructions.md`.

12. **Healthcheck Logs (`tmcli.py healthcheck`)**
    *   **Frequency:** Daily at 00:05
    *   **Purpose:** Verifies key log files exist and writes a status line to `logs/healthcheck.log`.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh healthcheck /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/tmcli.py healthcheck --date $(date +\%F)`

---

### Sniper & Morning Preparation (Currently Commented Out or Specific Logging)

The following jobs are related to "sniper" functionality (market movement detection) and morning preparation tasks. Some sniper-related jobs appear to be commented out in the provided crontab.

13. **Build Sniper Intel (`steam_sniper_intel/build_sniper_schedule.py`)** (Commented Out)
    *   **Frequency:** Was Daily at 09:30
    *   **Purpose:** Likely prepares data or schedules for the sniper functionality.
    *   **Command:** `#bash /home/ec2-user/tipping-monster/safecron.sh build_sniper_intel /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/steam_sniper_intel/build_sniper_schedule.py`
    *   **Internal Logs:** Check `logs/sniper/` if re-enabled.

14. **Load Sniper Intel & Schedule Jobs (`steam_sniper_intel/generate_and_schedule_snipers.sh`)**
    *   **Frequency:** Daily at 09:35
    *   **Purpose:** Loads sniper data and schedules the actual sniper monitoring jobs.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh load_sniper_intel /bin/bash /home/ec2-user/tipping-monster/steam_sniper_intel/generate_and_schedule_snipers.sh`
    *   **Internal Logs:** Check `logs/sniper/`.

15. **Fetch Betfair Odds (08:00 Snapshot)**
    *   **Frequency:** Daily at 08:00
    *   **Purpose:** Fetches a snapshot of Betfair odds specifically at 08:00.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh odds_0800 /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/fetch_betfair_odds.py --label 0800 >> /home/ec2-user/tipping-monster/logs/odds_0800_$(date +\%F).log 2>&1`
    *   **Log Output:** `logs/odds_0800_YYYY-MM-DD.log` (remains in root `logs/`)

16. **Morning Digest Script (`scripts/morning_digest.py`)**
    *   **Frequency:** Daily at 09:10
    *   **Purpose:** Runs a morning digest script, possibly summarizing tips or other information.
    *   **Command:** `/home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/scripts/morning_digest.py >> /home/ec2-user/tipping-monster/logs/morning_digest.log 2>&1`
    *   **Log Output:** `logs/morning_digest.log` (remains in root `logs/`)

17. **Auto Tweet Tips (`monstertweeter/auto_tweet_tips.py`)**
    *   **Frequency:** Daily at 08:15
    *   **Purpose:** Automatically tweets selected tips.
    *   **Command:** `/home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/monstertweeter/auto_tweet_tips.py >> /home/ec2-user/tipping-monster/logs/twitter_post.log 2>&1`
    *   **Log Output:** `logs/twitter_post.log` (remains in root `logs/`)

---

### Optional Model Training & S3 Upload

18. **Daily Model Training (`daily_train.sh`)**
    *   **Frequency:** Daily at 03:00
    *   **Purpose:** Performs daily model retraining.
    *   **Command:** `bash /home/ec2-user/tipping-monster/safecron.sh train /bin/bash /home/ec2-user/tipping-monster/daily_train.sh`
    *   **Log Output:** The script itself logs to `logs/train.log` and `logs/train_YYYY-MM-DD.log` (remains in root `logs/`).

19. **S3 Upload of `master_subscriber_log.csv` (Redundant?)**
    *   **Frequency:** Daily at 23:59
    *   **Purpose:** Uploads `master_subscriber_log.csv` (now from `logs/roi/`) to S3. This appears similar to job #6.
    *   **Command:** `/usr/local/bin/aws s3 cp /home/ec2-user/tipping-monster/logs/roi/master_subscriber_log.csv s3://tipping-monster-data/ --region eu-west-2 >> /home/ec2-user/tipping-monster/logs/s3_upload.log 2>&1`
    *   **Log Output:** `logs/s3_upload.log` (remains in root `logs/`)
    *   **Note:** Ensure this crontab line is updated as per `Docs/instructions.md`. Consider if this job is redundant given job #6.

## Data Flow Overview (High Level)

1.  **Race Data:** Racecards are fetched (likely by `run_pipeline_with_venv.sh`).
2.  **Predictions:** Models run, generating predictions and tips (logged in `logs/inference/` and `logs/dispatch/`).
3.  **Odds:** Odds are fetched regularly (`fetch_betfair_odds.py`).
4.  **Dispatch:** Tips are potentially dispatched via various channels (e.g., Telegram by `dispatch_tips.py`, Twitter by `auto_tweet_tips.py`). Sent tips logged in `logs/dispatch/`.
5.  **Results:** Daily race results are uploaded (`daily_upload_results.sh`).
6.  **ROI Calculation:** Results are compared against sent tips to calculate ROI. `generate_subscriber_log.py` creates a master log in `logs/roi/`, and `run_roi_pipeline.sh` processes these for summaries (logged in `logs/roi/`).
7.  **Summaries:** Daily and weekly summaries are generated and sent (e.g., to Telegram).
8.  **Maintenance:** Logs are cleaned, and backups are made to S3.

This is a preliminary guide. Further details can be added as the system evolves.
