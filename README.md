# Tipping Monster

Tipping Monster is a fully automated machine-learning tip engine for UK and Irish horse racing. It scrapes racecards, runs an XGBoost model to generate tips, merges realistic Betfair odds, dispatches formatted messages to Telegram, and tracks ROI.

A simple static landing page with a live tip feed is available under [site/index.html](site/index.html).
For dashboards or other tools, a lightweight FastAPI server (`stats_api.py`) exposes
`/roi`, `/tips` and `/tags` endpoints serving the latest ROI summaries and predictions.

See the [Docs/README.md](Docs/README.md) file for complete documentation, including environment variables and subsystem details. An audit of unused scripts lives in [Docs/script_audit.txt](Docs/script_audit.txt). A security review is available in [Docs/SECURITY_REVIEW.md](Docs/SECURITY_REVIEW.md). For a quick list of common developer commands, check [Docs/dev_command_reference.md](Docs/dev_command_reference.md).

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
# use `python3` if `python` is not available
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# GitHub Actions installs dependencies this way and caches them for
# faster test runs
```

2. Copy `.env.example` to `.env` and fill in your credentials:

```
BF_USERNAME, BF_PASSWORD, BF_APP_KEY, BF_CERT_PATH, BF_KEY_PATH, BF_CERT_DIR,
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_DEV_CHAT_ID, TM_DEV, TM_DEV_MODE,
TWITTER_API_KEY, TWITTER_API_SECRET,
TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ...
```


Set `TM_DEV=1` to route Telegram messages to `TELEGRAM_DEV_CHAT_ID`.
Set `TM_DEV_MODE=1` to suppress Telegram sends **and S3 uploads** and write logs to `logs/dev/` instead. Any script executed with the `--dev` flag automatically sets this variable.
The `.env` file should be placed in the repository root. The `utils/dev-check.sh` script looks for it in this location and can be executed from anywhere inside the repo.


For local development you can copy `.env.example` to `.env` and fill in your credentials.

3. Verify your development environment:

```bash
./utils/dev-check.sh
```

Private SSL keys are not included in the repository. Generate your own Betfair certificate and key files and store them securely outside version control (e.g., in a `certs/` folder).

Optionally, set `TIPPING_MONSTER_HOME` to the repository root:

```bash
source utils/set_tm_home.sh
```

4. Run tests to confirm everything is working:

```bash
pytest
```

5. Run the linter:

```bash
pre-commit run --files $(git ls-files '*.py')
```

6. Install the cron schedule:

```bash
crontab cron/dev.crontab   # dev mode
# or
crontab cron/prod.crontab  # production
```

---

## Usage

Launch the full daily pipeline with:

```bash
# Launch the full pipeline from the core directory
bash core/run_pipeline_with_venv.sh
# Use --dev to disable S3 uploads and Telegram posts
# (sets `TM_DEV_MODE=1`)
bash core/run_pipeline_with_venv.sh --dev
```

While testing the pipeline, always run it with `--dev` (or set
`TM_DEV_MODE=1`) so no real Telegram messages are posted and no files are
uploaded to S3.

Most Python scripts accept a `--debug` flag for verbose logging.

**Important:** run inference scripts from the repository root. For example:

```bash
python core/run_inference_and_select_top1.py --dev
```
Use `--dev` to disable the final S3 upload.
Executing this command inside the `core/` directory fails unless the repository root is on `PYTHONPATH` or you run it as a module:
`python -m core.run_inference_and_select_top1`.

This script uploads racecards, fetches odds, runs model inference, dispatches tips to Telegram, and uploads logs to S3. You can also run scripts individually for more control.

---

## Command Line Interface (tmcli)

Common workflows via CLI (run these commands from the repository root):

```bash
python cli/tmcli.py healthcheck --date YYYY-MM-DD
python cli/tmcli.py ensure-sent-tips YYYY-MM-DD
python cli/tmcli.py dispatch-tips YYYY-MM-DD --telegram
python cli/tmcli.py send-roi --date YYYY-MM-DD
python cli/tmcli.py model-feature-importance MODEL.bst --data DATA.csv --out chart.png
python cli/tmcli.py dispatch --date YYYY-MM-DD --telegram
python cli/tmcli.py roi-summary --date YYYY-MM-DD --telegram
python cli/tmcli.py chart-fi path/to/model_dir
python cli/tmcli.py send-photo path/to/image.jpg
python telegram_bot.py --dev  # start Telegram bot with /roi, /nap and /tip commands
```

## Tip Dispatch

Run `core/dispatch_tips.py` to send the day's tips to Telegram. Use `--telegram` to
actually post messages and `--explain` to append a short "Why we tipped this" summary generated from SHAP values.
If you run this file from inside `core/`, set `PYTHONPATH=..` or call it as
`python -m core.dispatch_tips` so it can locate the `core` package.

Use `--course "Royal Ascot"` (or any track name) to dispatch tips for a single
meeting only.

Tips under **0.80** confidence are automatically skipped unless their confidence
band showed a positive ROI in the last 30 days (tracked in
`monster_confidence_per_day_with_roi.csv`).

If the optional *meta place model* is present, each tip also includes a
`final_place_confidence` value summarised in the Telegram message as
"Place Chance".

The Streamlit P&L dashboard includes a *Positive ROI Bands Only* checkbox that
uses this same file to filter tips.

These commands wrap existing scripts for convenience and default locations.

The `tippingmonster` package also exposes handy helpers like
`send_telegram_message()`, `send_telegram_photo()` and `upload_to_s3()` for
posting messages, photos and uploading files while respecting dev mode.
A lightweight `trainer_intent_score()` function is also
provided for estimating how likely a trainer is trying to win based on recent
runs, strike rates and market moves.




## Health Check

To confirm all expected logs were created for a given day:

```bash
python utils/healthcheck_logs.py --date YYYY-MM-DD
```

This writes a status summary to `logs/healthcheck.log`.

---

## Make Targets

For convenience:

```bash
make train       # Train the model
make pipeline    # Run full daily pipeline
make roi         # Run ROI pipeline
make test        # Run unit tests
```

---

## Model Comparison

To compare two model versions:

```bash
make train    # train the model
make pipeline # run the full daily pipeline
make roi      # run ROI pipeline (use ROI scripts with `--tag` to filter by tag)
make test     # run unit tests
```

### Self-Training

Run `self_training_loop.py --retrain` to retrain the model with recent ROI logs.
This invokes `train_model_v6.py --self-train` and appends tip outcomes to the
training dataset. Schedule this weekly for continuous learning.
The repository also includes `train_place_model.py` to build a separate model
predicting whether a runner finishes in the top three.

`self_train_from_history.py` can be used to build a compact dataset from the
logged tips. It aggregates columns like *Confidence*, *Tags*, *Race Type*,
*Result*, *Odds* and *odds_delta* for direct model fine‑tuning with XGBoost.

### Model Comparison

Run `compare_model_v6_v7.py` to train both model versions on the same historical dataset. The script logs the confidence difference and ROI summary to `logs/compare_model_v6_v7.csv`.

## Model Files

Trained models are uploaded to S3 rather than stored in the repository. See
[Docs/model_storage.md](Docs/model_storage.md) for details on downloading the
latest model tarball from the `tipping-monster` bucket. The inference scripts
automatically choose the newest `tipping-monster-xgb-model-*.tar.gz` in the
repository root. If no model is found, they exit with `FileNotFoundError` and
instruct you to download one from S3 or train locally. When a path is provided
via `--model`, that file is downloaded if missing locally.

### v8 Stacked Ensemble (Experimental)

The latest research pipeline trains an ensemble of CatBoost, XGBoost and a small
Keras MLP. `train_monster_model_v8.py` saves the resulting stack as
`models/monster_v8_stack.tar.gz` and uploads it to the `tipping-monster` S3
bucket. Use `python -m core.run_inference_monster_v8 --input <racecards.jsonl>`
to produce tips under `predictions/<DATE>/output_v8.jsonl`.

## Model Transparency and Self‑Training

The pipeline uses **SHAP** to compute feature importance for each prediction. These explanations
reveal why the model tipped a runner, surfacing the top factors driving confidence. We log global
feature importance during training and publish per‑tip explanations in the weekly summary.

Past tips are merged back into the training data via a self‑training loop. Results are appended to
the dataset (`was_tipped`, `tip_profit`, `confidence_band`) so the model evolves with real world
performance. This continuous learning drives the weekly insights sent on Telegram and keeps the
model transparent and accountable.
