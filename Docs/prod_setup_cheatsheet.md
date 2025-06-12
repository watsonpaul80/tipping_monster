# Production Cheatsheet

This quick reference explains how to move from a dev install to a full
production deployment.

## 1. Local Testing

- Clone the repo and set up a virtual environment as in `Docs/ec2_setup_guide.md`.
- Copy `.env.example` to `.env` and fill in your credentials.
- **Always run in dev mode first** to avoid Telegram posts:
  ```bash
  export TM_DEV_MODE=1
  make pipeline -- --dev
  ```
  Telegram messages are written to `logs/dev/telegram.log` when `TM_DEV_MODE=1`.
- Use `pre-commit run --files <file>` and `pytest` before any commit.

## 2. Key Scripts

- `core/run_pipeline_with_venv.sh` – full daily pipeline.
- `core/dispatch_tips.py` – sends NAPs and top picks.
- `core/dispatch_all_tips.py` – posts every race using `--telegram` and
  `--batch-size`.
- `roi/run_roi_pipeline.sh` – links tips to results and updates ROI logs.
- Training:
  - `train_model_v6.py` – base model, optionally use `--self-train` to inject past tips.
  - `core/train_modelv7.py` – always includes tip history features (`was_tipped`,
    `tip_confidence`, `tip_profit`).
- `compare_model_v6_v7.py` – trains v6 and v7 side by side and writes
  `logs/compare_model_v6_v7.csv` with ROI for each.

## 3. Training Data

Historical results CSVs are downloaded from S3 automatically. Past tips are
merged when you enable self-training (v6 `--self-train` or v7 default).
The model learns from each horse's real outcome and whether it was previously
tipped.

## 4. Deploying to Production

1. Set `TM_DEV_MODE=0` in `.env`.
2. Install cron jobs using the template at `cron/prod.crontab` (`crontab cron/prod.crontab`).
3. Run `make pipeline` to produce daily predictions.
4. Enable `core/dispatch_tips.py --telegram` in cron to send tips.
5. Schedule `roi/run_roi_pipeline.sh` and `roi/send_daily_roi_summary.py` for ROI updates.

## 5. All Races Tips Mode

Use `core/dispatch_all_tips.py` to broadcast every tip:
```bash
python core/dispatch_all_tips.py --date YYYY-MM-DD --telegram --batch-size 40
```
This groups races into batches to avoid Telegram limits.

## 6. Comparing Two Models

Run:
```bash
python core/compare_model_v6_v7.py
```
The output CSV lists confidence scores from both models and prints ROI lines
similar to:
```
ROI v6: 0.05 | ROI v7: 0.08
```
Check `logs/compare_model_v6_v7.csv` for per-horse deltas.

## 7. Quick ROI Checks

After running the pipeline, execute:
```bash
roi/run_roi_pipeline.sh --date YYYY-MM-DD
```
The ROI scripts track daily and weekly performance and send summaries if
Telegram is enabled.

