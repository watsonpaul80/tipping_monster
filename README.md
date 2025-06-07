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
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ...
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
bash run_pipeline_with_venv.sh
# Dev mode: disables S3 uploads and Telegram posts
bash run_pipeline_with_venv.sh --dev
```

This script uploads racecards, fetches odds, runs model inference, dispatches tips to Telegram, and uploads logs to S3. You can also run scripts individually for more control.

---

## Command Line Interface (tmcli)

Common workflows via CLI:

```bash
python tmcli.py healthcheck --date YYYY-MM-DD
python tmcli.py ensure-sent-tips YYYY-MM-DD
python tmcli.py dispatch-tips --date YYYY-MM-DD --telegram
python tmcli.py send-roi --date YYYY-MM-DD
python tmcli.py model-feature-importance --telegram
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
python compare_model_v6_v7.py
```

This logs confidence and ROI differences to `logs/compare_model_v6_v7.csv`.
