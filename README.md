# Tipping Monster

Tipping Monster is a fully automated machine-learning tip engine for UK and Irish horse racing. It scrapes racecards, runs an XGBoost model to generate tips, merges realistic Betfair odds, dispatches formatted messages to Telegram, and tracks ROI.

See the [Docs/README.md](Docs/README.md) file for complete documentation, including environment variables and subsystem details. An audit of unused scripts lives in [docs/script_audit.txt](docs/script_audit.txt). A security review is available in [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md).

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials:

```
BF_USERNAME, BF_PASSWORD, BF_APP_KEY, BF_CERT_PATH, BF_KEY_PATH, BF_CERT_DIR,
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TWITTER_API_KEY, TWITTER_API_SECRET,
TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ...
```

The `.env` file should be placed in the repository root. The `dev-check.sh` script looks for it in this location.

3. Verify your development environment:

```bash
./dev-check.sh
```

Private SSL keys are not included in the repository. Generate your own Betfair certificate and key files and store them securely outside version control (e.g., in a `certs/` folder).

Optionally, set `TIPPING_MONSTER_HOME` to the repository root:

```bash
source set_tm_home.sh
```

4. Run tests to confirm everything is working:

```bash
pytest
```

5. Run the linter:

```bash
pre-commit run --files $(git ls-files '*.py')
```

---

## Usage

Launch the full daily pipeline with:

```bash
# Launch the full pipeline from the core directory
bash core/run_pipeline_with_venv.sh
# Use --dev to disable S3 uploads and Telegram posts
bash core/run_pipeline_with_venv.sh --dev
```

This script uploads racecards, fetches odds, runs model inference, dispatches tips to Telegram, and uploads logs to S3. You can also run scripts individually for more control.

---

## Command Line Interface (tmcli)

Common workflows via CLI:

```bash
python tmcli.py pipeline --dev            # run full pipeline in dev mode
python tmcli.py roi --date YYYY-MM-DD     # generate ROI stats
python tmcli.py sniper --dev              # (placeholder) sniper tasks
python tmcli.py healthcheck --date YYYY-MM-DD
python tmcli.py ensure-sent-tips YYYY-MM-DD
```

These wrap core scripts for ease of use.

---

## Tip Dispatch

Run `dispatch_tips.py` to send the day's tips to Telegram. Use `--telegram` to
actually post messages and `--explain` to append a short "Why we tipped this"
summary generated from SHAP values.

## Tip Dispatch

Run `dispatch_tips.py` to send the day's tips to Telegram. Use `--telegram` to
actually post messages and `--explain` to append a short "Why we tipped this"
summary generated from SHAP values.

## Tip Dispatch

Run `dispatch_tips.py` to send the day's tips to Telegram. Use `--telegram` to
actually post messages and `--explain` to append a short "Why we tipped this"
summary generated from SHAP values.

## Tip Dispatch

Run `dispatch_tips.py` to send the day's tips to Telegram. Use `--telegram` to
actually post messages and `--explain` to append a short "Why we tipped this"
summary generated from SHAP values.

## Health Check

To confirm all expected logs were created for a given day:

```bash
python healthcheck_logs.py --date YYYY-MM-DD
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

### Model Comparison

Run `compare_model_v6_v7.py` to train both model versions on the same historical dataset. The script logs the confidence difference and ROI summary to `logs/compare_model_v6_v7.csv`.


### Self-Training Evaluation

`evaluate_self_training.py` trains models with and without past tip features and writes the ROI comparison to `logs/evaluate_self_training.csv`.

## Model Transparency and Self‑Training

The pipeline uses **SHAP** to compute feature importance for each prediction. These explanations
reveal why the model tipped a runner, surfacing the top factors driving confidence. We log global
feature importance during training and publish per‑tip explanations in the weekly summary.

Past tips are merged back into the training data via a self‑training loop. Results are appended to
the dataset (`was_tipped`, `tip_profit`, `confidence_band`) so the model evolves with real world
performance. This continuous learning drives the weekly insights sent on Telegram and keeps the
model transparent and accountable.
