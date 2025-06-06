# Scrape racecards for today
date_str=$(date +'%F')
OUTPUT_FILE="today_racecards.json" # Change this line
echo "[INFO] Running racecards.py for today (${date_str})"
if python racecards.py today > "$OUTPUT_FILE"; then
  echo "[INFO] Racecards JSON saved to $OUTPUT_FILE"
else
  echo "[ERROR] racecards.py did not output JSON; aborting" >&2
  rm -f "$OUTPUT_FILE"
  exit 1
fi

# Check if file is non-empty
if [ ! -s "$OUTPUT_FILE" ]; then
  echo "[WARN] $OUTPUT_FILE is empty; no races to ingest" >&2
  exit 0
fi

# Ingest this JSON file into the database
cd /home/ec2-user/tipping-monster || { echo "Cannot cd to project root" >&2; exit 1; } #This cd is not needed
echo "[INFO] Ingesting racecards JSON into DB"
# change the file path here
if python ingest_racecards.py --file /home/ec2-user/tipping-monster/rpscrape/scripts/"$OUTPUT_FILE"; then
  echo "[INFO] Finished ingesting racecards at $(date +'%Y-%m-%d %H:%M:%S')"
else
  echo "[ERROR] Ingestion failed for $OUTPUT_FILE" >&2
  exit 1
fi
