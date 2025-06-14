#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from subprocess import PIPE, run

import psycopg2
from psycopg2.extras import execute_values

# --- CLI ---
parser = argparse.ArgumentParser(description="Scrape and ingest racecards JSON files")
parser.add_argument(
    "--folder",
    required=True,
    help="Folder containing racecards JSON files, relative to project root",
)
parser.add_argument(
    "--skip-scrape",
    action="store_true",
    help="Skip scraping; ingest existing JSON in folder",
)
parser.add_argument("--db-host", default=os.getenv("DB_HOST"), help="Database host")
parser.add_argument(
    "--db-port", default=os.getenv("DB_PORT", "5432"), help="Database port"
)
parser.add_argument(
    "--db-name", default=os.getenv("DB_NAME", "racecards"), help="Database name"
)
parser.add_argument("--db-user", default=os.getenv("DB_USER"), help="Database user")
parser.add_argument(
    "--db-password", default=os.getenv("DB_PASSWORD"), help="Database password"
)
args = parser.parse_args()

# Setup logging
target = logging.INFO if not os.getenv("DEBUG") else logging.DEBUG
logging.basicConfig(level=target)
logger = logging.getLogger(__name__)

# Determine today's date and paths
today = datetime.utcnow().strftime("%Y-%m-%d")
PROJECT_ROOT = os.getcwd()
folder_path = os.path.join(PROJECT_ROOT, args.folder)
json_file = os.path.join(folder_path, f"{today}.json")

# Scrape if not skipped
if not args.skip_scrape:
    if os.path.exists(json_file):
        logger.info(f"Removing stale JSON: {json_file}")
        os.remove(json_file)
    logger.info("Scraping racecards for today")
    scraper = os.path.join(PROJECT_ROOT, "rpscrape/scripts/racecards.py")
    result = run(
        [sys.executable, scraper, "today"],
        stdout=open(json_file, "w", encoding="utf-8"),
        stderr=PIPE,
    )
    if result.returncode != 0:
        logger.error(f"Scraper failed: {result.stderr.decode().strip()}")
        sys.exit(1)
else:
    logger.info("Skipping scrape; using existing JSON")

# Verify JSON exists
if not os.path.isfile(json_file):
    logger.error(f"JSON file not found: {json_file}")
    sys.exit(1)

# Load JSON data
with open(json_file) as f:
    data = json.load(f)

# Extract meetings: each region key holds meeting dicts
meetings = []
for region_val in data.values():
    if isinstance(region_val, dict):
        for meeting in region_val.values():
            if isinstance(meeting, dict) and "races" in meeting:
                meetings.append(meeting)

if not meetings:
    logger.error(
        f"No meetings found in {json_file}. Top-level keys: {list(data.keys())}"
    )
    sys.exit(1)

# Connect to database
conn = psycopg2.connect(
    host=args.db_host,
    port=args.db_port,
    dbname=args.db_name,
    user=args.db_user,
    password=args.db_password,
)
cur = conn.cursor()

# Flatten runner rows
rows = []
for meeting in meetings:
    mid = meeting.get("meeting_id") or meeting.get("id")
    for race in meeting.get("races", []):
        rid = race.get("race_id") or race.get("id")
        for runner in race.get("runners", []):
            runner_id = runner.get("runner_id") or runner.get("id")
            name = runner.get("name")
            trainer_info = runner.get("trainer") or runner.get("stats", {}).get(
                "trainer", {}
            )
            trainer_pct = (
                trainer_info.get("ovr_wins_pct")
                if isinstance(trainer_info, dict)
                else None
            )
            rows.append((mid, rid, runner_id, name, trainer_pct))

if not rows:
    logger.warning("No runner rows to ingest")
else:
    sql = (
        "INSERT INTO racecards"
        " (meeting_id, race_id, runner_id, runner_name, trainer_win_pct)"
        " VALUES %s ON CONFLICT (meeting_id, race_id, runner_id) DO NOTHING"
    )
    execute_values(cur, sql, rows)
    conn.commit()
    logger.info(f"Ingested {len(rows)} runners from {json_file}")

cur.close()
conn.close()
