# Tipping Monster

Tipping Monster is a fully automated machine-learning tip engine for UK and Irish horse racing. It scrapes racecards, runs an XGBoost model to generate tips, merges realistic Betfair odds, dispatches formatted messages to Telegram, and tracks ROI.

See the [Docs/README.md](Docs/README.md) file for complete documentation, including environment variables and subsystem details.

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Export the required environment variables (see Docs/README.md for the full list):
`BF_USERNAME`, `BF_PASSWORD`, `BF_APP_KEY`, `BF_CERT_PATH`, `BF_KEY_PATH`, `BF_CERT_DIR`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

3. Run the tests to confirm everything works:

```bash
pytest
```

## Usage

Launch the full daily pipeline with:

```bash
bash run_pipeline_with_venv.sh
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
