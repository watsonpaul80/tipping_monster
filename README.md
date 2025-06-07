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

`BF_USERNAME`, `BF_PASSWORD`, `BF_APP_KEY`, `BF_CERT_PATH`, `BF_KEY_PATH`, `BF_CERT_DIR`, `TG_BOT_TOKEN`, `TG_USER_ID`.

For local development you can copy `.env.example` to `.env` and fill in your credentials.

Private SSL keys are not included in the repository. Generate your own Betfair certificate and key files and place them somewhere outside version control (for example in a local `certs/` folder).

`BF_USERNAME`, `BF_PASSWORD`, `BF_APP_KEY`, `BF_CERT_PATH`, `BF_KEY_PATH`, `BF_CERT_DIR`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
Optionally set `TIPPING_MONSTER_HOME` to the repository root (run `source set_tm_home.sh` to configure automatically).


3. Run the tests to confirm everything works:

```bash
pytest
```

4. Run the linter:

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

