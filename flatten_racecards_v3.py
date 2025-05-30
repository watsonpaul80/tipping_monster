import json
import sys

def form_score(form):
    if not isinstance(form, str):
        return -1
    digits = [int(ch) for ch in form if ch.isdigit()]
    if not digits:
        return -1
    win_ratio = digits.count(1) / len(digits)
    trend = (digits[-1] - digits[0]) if len(digits) > 1 else 0
    return win_ratio * 100 - trend

def encode_headgear(h):
    h = (h or "").lower()
    if "b" in h: return 1
    if "v" in h: return 2
    if "c" in h: return 3
    if "h" in h: return 4
    return 0

def flatten_racecard(input_json):
    with open(input_json) as f:
        data = json.load(f)

    output = []

    for country_data in data.values():
        for meeting_data in country_data.values():
            for race_time, race in meeting_data.items():
                field_size = len(race["runners"])
                for runner in race["runners"]:
                    # Days since run
                    try:
                        days_since = float(str(runner.get("last_run", "-1")).split()[0])
                    except:
                        days_since = -1

                    # Prize
                    try:
                        prize_val = float(
                            str(race.get("prize", "0"))
                            .replace("£", "")
                            .replace("€", "")
                            .replace(",", "")
                            .strip() or 0
                        )
                    except:
                        prize_val = 0.0

                    # Draw bias rank
                    try:
                        draw_val = float(runner.get("draw", 0))
                    except:
                        draw_val = 0

                    flat = {
                        "race": f"{race_time} {race['course']}",
                        "name": runner.get("name", ""),
                        "draw": runner.get("draw", -1),
                        "or": runner.get("or", -1),
                        "rpr": runner.get("rpr", -1),
                        "lbs": runner.get("lbs", -1),
                        "age": runner.get("age", -1),
                        "dist_f": race.get("distance_f", -1),
                        "class": race.get("race_class", -1),
                        "going": race.get("going", -1),
                        "prize": prize_val,
                        "trainer": runner.get("trainer", ""),
                        "jockey": runner.get("jockey", ""),
                        "trainer_rtf": runner.get("trainer_rtf", -1),
                        "jockey_rtf": runner.get("jockey_rtf", -1),
                        "form_score": form_score(runner.get("form", "")),
                        "days_since_run": days_since,
                        "headgear_type": encode_headgear(runner.get("headgear", "")),
                        "draw_bias_rank": draw_val / max(field_size, 1)
                    }
                    output.append(flat)
    return output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python flatten_racecards_v3.py <input.json> <output.jsonl>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    rows = flatten_racecard(input_path)

    with open(output_path, "w") as out:
        for row in rows:
            out.write(json.dumps(row) + "\n")

    print(f"✅ Flattened {len(rows)} runners to {output_path}")

