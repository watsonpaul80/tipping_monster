
# EC2 Setup Guide

This guide describes how to deploy and run Tipping Monster on an Amazon EC2 instance.

## Basic Installation
1. Install system dependencies (`git`, `python3`, `virtualenv`).
2. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/watsonpaul80/tipping-monster.git
   cd tipping-monster
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Running Tests
**Important:** Always set `TM_DEV_MODE=1` before running tests or experiments. This disables Telegram/Twitter posts and logs output locally.

```bash
export TM_DEV_MODE=1
pytest
```

Using the `--dev` flag on many scripts also sets this variable automatically. Leaving `TM_DEV_MODE` unset may send real Telegram messages.

# EC2 Dev-to-Prod Setup Guide

This guide explains how to deploy Tipping Monster on a fresh Ubuntu EC2 instance for development and then transition the same machine to production.

## Development Environment

1. **Launch** an Ubuntu 22.04 EC2 instance with at least 2 vCPUs and 4 GB RAM.
2. **Install system packages:**
   ```bash
   sudo apt update && sudo apt install -y git python3-venv python3-pip
   ```
3. **Clone the repository:**
   ```bash
   git clone <YOUR FORK URL> tipping-monster
   cd tipping-monster
   ```
4. **Create a virtual environment and install requirements:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pre-commit
   ```
5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # edit .env with your Betfair, Telegram and AWS credentials
   ```
6. **Verify your setup:**
   ```bash
   ./utils/dev-check.sh
   pre-commit run --files $(git ls-files '*.py')
   pytest
   ```
7. **Run the pipeline in dev mode:**
   ```bash
   make pipeline -- --dev
   ```
   Using `--dev` (or setting `TM_DEV_MODE=1`) logs Telegram messages locally and skips S3 uploads.

## Moving to Production

1. **Disable dev mode** by setting `TM_DEV_MODE=0` and `TM_DEV=0` in `.env`.
2. **Install cron jobs** using the schedules in `Docs/ops.md`. Each cron line should wrap the command with `utils/safecron.sh` so dev mode is respected when enabled.
3. **Key scripts for production:**
   - `core/run_pipeline_with_venv.sh` – orchestrates the daily pipeline.
   - `core/run_inference_and_select_top1.py` – generates predictions.
   - `core/dispatch_tips.py` – sends tips to Telegram.
   - `roi/run_roi_pipeline.sh` – calculates ROI.
   - `utils/upload_logs_to_s3.sh` – uploads logs to S3.
4. **Testing commands before enabling cron:**
   ```bash
   python core/run_inference_and_select_top1.py --dev
   python core/dispatch_tips.py $(date +%F) --telegram --dev
   python cli/tmcli.py healthcheck --date $(date +%F)
   ```
5. Once everything works in dev mode, remove the `--dev` flags and update your crontab accordingly.

With these steps you can bootstrap a new EC2 instance for development, run the full pipeline safely, and then switch to production by disabling dev mode and enabling the cron schedule.

