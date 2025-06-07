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
Optionally set `TIPPING_MONSTER_HOME` to the repository root (run `source set_tm_home.sh` to configure automatically).

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

