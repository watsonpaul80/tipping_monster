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
