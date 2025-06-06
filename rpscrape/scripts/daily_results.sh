#!/usr/bin/env bash
set -euo pipefail
# daily_results.sh: Scrape race results and ingest into Postgres
# Usage: daily_results.sh [today|yesterday|YYYY-MM-DD]

# Determine script and project directories
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(dirname "$(dirname "$SCRIPT_DIR")")

echo "=== $(date +'%Y-%m-%d %H:%M:%S') Starting daily_results.sh ==="
# 1) Go to project root & activate virtualenv
cd "$PROJECT_ROOT"
source .venv/bin/activate

# Export DB connection env vars
export DB_HOST="tippingmonster123-db.cemmmoj0dk2b.eu-west-2.rds.amazonaws.com"
export DB_USER="tippingmonster"
export DB_PASSWORD="TippingMonster123"

# 2) Determine DATE_ARG (default today)
if [ "$#" -eq 0 ]; then
  DATE_ARG="today"
else
  DATE_ARG="$1"
fi

# 3) Compute SCRAPE_DATE for rpscrape CLI (YYYY/MM/DD) and file date for lookup (YYYY_MM_DD)
if [ "$DATE_ARG" = "today" ]; then
  SCRAPE_DATE=$(date +%Y/%m/%d)
  FILE_DATE=$(date +%Y_%m_%d)
elif [ "$DATE_ARG" = "yesterday" ]; then
  SCRAPE_DATE=$(date -d 'yesterday' +%Y/%m/%d)
  FILE_DATE=$(date -d 'yesterday' +%Y_%m_%d)
else
  SCRAPE_DATE=$(echo "$DATE_ARG" | tr '-' '/')
  FILE_DATE=$(echo "$DATE_ARG" | tr '-' '_')
fi

echo "Scrape date set to $SCRAPE_DATE (file date $FILE_DATE)"

# 4) Prepare output path
OUT_DIR="$PROJECT_ROOT/raw/results"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/${DATE_ARG}-results.csv"
# Clear or create the file
: > "$OUT_FILE"

echo "=== $(date +'%Y-%m-%d %H:%M:%S') Scraping results for $DATE_ARG ==="
# 5) Run scraper to generate per-region, per-type CSVs in rpscrape/data/dates/... directory
pushd "$PROJECT_ROOT/rpscrape/scripts" > /dev/null
python3 rpscrape.py -d "$SCRAPE_DATE" -r gb -t flat
python3 rpscrape.py -d "$SCRAPE_DATE" -r gb -t jumps
python3 rpscrape.py -d "$SCRAPE_DATE" -r ire -t flat
python3 rpscrape.py -d "$SCRAPE_DATE" -r ire -t jumps
popd > /dev/null

# 6) Merge generated CSVs into single output file, preserving header only once
for REGION in gb ire; do
  for TYPE in flat jumps; do
    SRC="$PROJECT_ROOT/rpscrape/data/dates/${REGION}/${TYPE}/${FILE_DATE}.csv"
    if [ -f "$SRC" ]; then
      if [ ! -s "$OUT_FILE" ]; then
        # first file: include header
        cat "$SRC" >> "$OUT_FILE"
      else
        # subsequent: skip header
        tail -n +2 "$SRC" >> "$OUT_FILE"
      fi
    else
      echo "Warning: results file not found: $SRC" >&2
    fi
  done
done

echo "Merged results written to $OUT_FILE"

# 7) Ingest merged CSV into DB
echo "=== $(date +'%Y-%m-%d %H:%M:%S') Ingesting results from $OUT_FILE ==="
python ingest_results.py --file "$OUT_FILE"

echo "=== $(date +'%Y-%m-%d %H:%M:%S') Results ingestion complete for $DATE_ARG ==="

