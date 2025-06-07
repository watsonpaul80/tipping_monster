# Codex Checkpoint — 2025-06-07

This milestone summarises all notable features and fixes committed to the repository so far.

## Added
- **Command Line Wrapper** `cli/tmcli.py` for running the pipeline, ROI tasks and (now removed) sniper jobs with `--dev` mode support【F:cli/tmcli.py†L1-L60】.
- **Dispatch All Tips** `dispatch_all_tips.py` to send full card tips in batches with Telegram integration【F:dispatch_all_tips.py†L1-L114】.
- **Codex Action Logger** `codex_logger.py` to record agent actions to `logs/codex.log`【F:codex_logger.py†L1-L27】.
- **Safe Cron Utility** `safecron.sh` validating `TG_BOT_TOKEN` and `TG_USER_ID` env vars before execution, alerting on failures【F:safecron.sh†L1-L40】.
- **Environment Variable Support** via `set_tm_home.sh` and consistent `TIPPING_MONSTER_HOME` usage across scripts【F:set_tm_home.sh†L1-L4】.
- **Python Package** `tippingmonster` containing utility functions such as Telegram messaging and profit calculation【F:tippingmonster/utils.py†L1-L66】【F:tippingmonster/utils.py†L67-L109】.
- **Feature Validation** script `validate_features.py` ensuring datasets match `features.json` columns【F:validate_features.py†L1-L50】.
- **Sent Tips Helper** `ensure_sent_tips.py` to recreate `sent_tips_DATE.jsonl` if missing【F:ensure_sent_tips.py†L8-L26】.
- **Dispatch Alerts** `alert_if_no_sent_tips.py` (removed later) and `alert_if_bad_snapshot.py` warned when no tips were sent or odds snapshots were incomplete.
- **Log Healthcheck** `healthcheck_logs.py` verifies expected logs exist each day【F:healthcheck_logs.py†L14-L28】.
<<<<<<< HEAD
- **Archive Old Logs** `archive_old_logs.py` (removed later) compressed logs older than N days for cleanup.
=======
- **Archive Old Logs** `archive_old_logs.py` compresses logs older than N days for cleanup【F:archive_old_logs.py†L8-L26】.
- **Model Drift Report** `model_drift_report.py` detects SHAP feature drift and writes a markdown summary.
>>>>>>> 5c9414507daf288de8ea26cce9bf4c7d8a24a540
- **Unit Tests** covering CLI behaviour, odds extraction, ROI calculations and more under `tests/`【F:tests/test_tmcli.py†L1-L34】.
- **GitHub Actions** workflow to run Python tests on pushes.
- **Quickstart & Docs** providing an overview of the system and instructions.

## Changed
- Reworked multiple scripts to use the `TIPPING_MONSTER_HOME` variable for repo‑relative paths.
- Secrets (Telegram tokens, etc.) moved to environment variables for security.
- Added dev mode flag to dispatch and pipeline scripts to avoid sending production messages.
- Consolidated ROI scripts under the project root and simplified cron jobs.
- Added log directory creation logic so scripts don’t fail when paths are missing.
- Standardised PEP8 formatting and removed stray cache files (`__pycache__`).

## Removed
- All Steam Sniper scripts, schedules and data files to focus on core tipping pipeline.
- SSL key files previously committed by mistake.
- Duplicate ROI scripts from older directory structure.

## Documentation
- `Docs/CHANGELOG.md` records detailed updates, including pipeline improvements on 2025‑05‑31, ROI fixes on 2025‑06‑01, script consolidation on 2025‑06‑06 and Sniper removal on 2025‑06‑07【F:Docs/CHANGELOG.md†L1-L105】.
- `Docs/monster_overview.md` lists full system features and automation schedule【F:Docs/monster_overview.md†L1-L38】【F:Docs/monster_overview.md†L40-L94】.

---
This checkpoint captures the repository state after removing the Sniper workflow and finalising environment variable support. Future commits will build upon this stable foundation.
