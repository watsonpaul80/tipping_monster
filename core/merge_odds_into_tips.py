#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

# === PATHS ===
today = datetime.utcnow().date().isoformat()
odds_files = sorted(Path("odds_snapshots").glob(f"{today}_*.json"))
if not odds_files:
    print(f"[!] No odds snapshot found for {today}")
    exit(1)

odds_file = odds_files[-1]
tips_file = Path(f"predictions/{today}/output.jsonl")
output_file = Path(f"predictions/{today}/tips_with_odds.jsonl")

print(f"[+] Using odds: {odds_file}")
print(f"[+] Reading tips: {tips_file}")

# === LOAD DATA ===
with open(odds_file) as f:
    odds = json.load(f)
with open(tips_file) as f:
    tips = [json.loads(line) for line in f]

# === NORMALIZATION ===


def standardize_course_only(race: str) -> str:
    """Return course name only, lowercased and stripped."""
    race = race.strip().lower().replace("(aw)", "").strip()
    match1 = re.match(r"^(\d{1,2}):(\d{2})\s+(.+)$", race)
    match2 = re.match(r"^(.+)\s+(\d{1,2}):(\d{2})$", race)
    if match1:
        return match1.group(3).strip()
    elif match2:
        return match2.group(1).strip()
    return race


print("\n[🧪] Sample standardization output for debugging:\n")

# Show 5 examples from each
for tip in tips[:5]:
    print(f"[TIP]   {tip['race']}  |  Horse: {tip['name']}")
for odd in odds[:5]:
    print(f"[ODDS]  {odd['race']}  |  Horse: {odd['horse']}")

# === MERGE LOGIC ===
merged = []
unmatched = []

for tip in tips:
    tip_course = standardize_course_only(tip["race"])
    tip_name = tip["name"].strip().lower()
    match = None

    for o in odds:
        o_course = standardize_course_only(o["race"])
        o_name = o["horse"].strip().lower()
        if o_course == tip_course and o_name == tip_name:
            match = o
            break

    if match:
        tip["bf_sp"] = match["bf_sp"]
        try:
            conf = float(tip.get("confidence", 0))
            bf_sp = float(tip["bf_sp"])
            if bf_sp > 0:
                tip["value_score"] = round((conf / bf_sp) * 100, 2)
        except Exception:
            pass
        merged.append(tip)
    else:
        unmatched.append(f"{tip['name']} in {tip['race']}")

# === SAVE OUTPUT ===
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w") as f:
    for row in merged:
        f.write(json.dumps(row) + "\n")

print(f"[✓] Merged {len(merged)} tips with odds → {output_file}")
if unmatched:
    print("[!] Unmatched tips:")
    for u in unmatched:
        print(f"   - {u}")
