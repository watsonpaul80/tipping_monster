# Tipping Monster

Tipping Monster is a fully automated machine-learning tip engine for UK and Irish horse racing. It scrapes racecards, runs an XGBoost model to generate tips, merges realistic Betfair odds, dispatches formatted messages to Telegram, and tracks ROI.

See the [Docs/README.md](Docs/README.md) file for complete documentation, including environment variables and subsystem details. An audit of unused scripts lives in [docs/script_audit.txt](docs/script_audit.txt).

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials:
`BF_USERNAME`, `BF_PASSWORD`, `BF_APP_KEY`, `BF_CERT_PATH`, `BF_KEY_PATH`, `BF_CERT_DIR`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and others as needed.


Create a `.env` file in the repository root with these variables. The `dev-check` script looks for `.env` in this location.

For local development you can copy `.env.example` to `.env` and fill in your credentials.
=======
3. Verify your development environment:

```bash
./dev-check.sh
```


Private SSL keys are not included in the repository. Generate your own Betfair certificate and key files and place them somewhere outside version control (for example in a local `certs/` folder).

Optionally set `TIPPING_MONSTER_HOME` to the repository root (run `source set_tm_home.sh` to configure automatically).

4. Run the tests to confirm everything works:

```bash
pytest
```

5. Run the linter:

```bash
pre-commit run --files $(git ls-files '*.py')
```

## Usage

Launch the full daily pipeline with:

```bash
bash run_pipeline_with_venv.sh
# Use --dev to disable S3 uploads and Telegram posts
bash run_pipeline_with_venv.sh --dev
```

This script uploads racecards, fetches odds, runs model inference, dispatches tips to Telegram and uploads logs to S3. Individual scripts can be executed separately for custom workflows.

## Command Line Interface

Common tasks can be run via the `tmcli` helper. Example usage:

```bash
python tmcli.py healthcheck --date YYYY-MM-DD
python tmcli.py ensure-sent-tips YYYY-MM-DD
```

These commands wrap existing scripts for convenience and default locations.

## Health Check

To confirm all expected logs were created for a given day, run:

```bash
python healthcheck_logs.py --date YYYY-MM-DD
```

This appends a status line to `logs/healthcheck.log` and lists any missing log files.

### Make Targets

For convenience you can use the provided `Makefile`:

```bash
make train    # train the model
make pipeline # run the full daily pipeline
make roi      # run ROI pipeline
make test     # run unit tests
```

### Self-Training

Run `self_training_loop.py --retrain` to retrain the model with recent ROI logs.
This invokes `train_model_v6.py --self-train` and appends tip outcomes to the
training dataset. Schedule this weekly for continuous learning.

### Model Comparison

Run `compare_model_v6_v7.py` to train both model versions on the same historical dataset. The script logs the confidence difference and ROI summary to `logs/compare_model_v6_v7.csv`.
