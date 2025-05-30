#!/bin/bash
set -e  # stop on error

LABEL=$1  # pass time label like 1420

cd /home/ec2-user/tipping-monster/steam_sniper_intel
source ../.venv/bin/activate

echo "[+] Fetch sniper odds for $LABEL"
python fetch_betfair_sniper_odds.py --label $LABEL

echo "[+] Merge odds history"
python merge_sniper_history.py

echo "[+] Detect steamers for $LABEL"
python detect_and_save_steamers.py --label $LABEL

echo "[+] Dispatch steamers for $LABEL"
python dispatch_snipers.py --source sniper_data/steamers_$(date +%F)_${LABEL}.json

echo "[+] Done for $LABEL"

