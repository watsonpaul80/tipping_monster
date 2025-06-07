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

   *If you need Betfair certificate authentication, generate your own client key
   and certificate locally using `openssl` (or the Betfair docs) and keep them
   out of version control. Place them in a directory such as `certs/` and set
   `BF_CERT_PATH` and `BF_KEY_PATH` accordingly.*

3. Run the tests to confirm everything works:

```bash
pytest
```

4. Python cache artifacts (`*.pyc` files and `__pycache__/` directories) are ignored via `.gitignore`.

## Usage

Launch the full daily pipeline with:

```bash
bash run_pipeline_with_venv.sh
```

This script uploads racecards, fetches odds, runs model inference, dispatches tips to Telegram and uploads logs to S3. Individual scripts can be executed separately for custom workflows.

### tmcli Wrapper

Common workflows are consolidated under a simple CLI:

```bash
# Run the full pipeline
python tmcli.py pipeline --date 2025-06-07

# Run the full pipeline in dev mode
python tmcli.py pipeline --date 2025-06-07 --dev

# Run the ROI pipeline for a specific day
python tmcli.py roi --date 2025-06-07
# Dev mode also supported
python tmcli.py roi --date 2025-06-07 --dev

# Build and schedule Steam Sniper jobs
python tmcli.py sniper
# Dev mode
python tmcli.py sniper --dev
```

