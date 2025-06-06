import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
import pytz

import betfairlightweight
from betfairlightweight import filters
from secrets1 import (
    BF_USERNAME,
    BF_PASSWORD,
    BF_APP_KEY,
    BF_CERT_DIR
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", type=str, help="Override timestamp label (e.g. 1445)", default=None)
    args = parser.parse_args()

    local_tz = pytz.timezone("Europe/London")
    now = datetime.now(local_tz)
    today = now.date()
    label = args.label if args.label else now.strftime("%H%M")
    output_dir = Path("steam_sniper_intel/sniper_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{today}_{label}.json"

    trading = betfairlightweight.APIClient(
        BF_USERNAME,
        BF_PASSWORD,
        app_key=BF_APP_KEY,
        certs=BF_CERT_DIR
    )

    print("[+] Logging in...")
    trading.login()

    try:
        market_filter = filters.market_filter(
            event_type_ids=['7'],  # Horse racing
            market_type_codes=['WIN'],
            market_countries=['GB', 'IE'],
            market_start_time={
                'from': f"{today}T00:00:00Z",
                'to': f"{today}T23:59:00Z"
            }
        )

        print("[+] Fetching markets...")
        markets = trading.betting.list_market_catalogue(
            filter=market_filter,
            max_results=1000,
            market_projection=['EVENT', 'RUNNER_METADATA', 'MARKET_START_TIME', 'RUNNER_DESCRIPTION']
        )

        if not markets:
            print("[!] No markets found matching criteria")
            return

        market_ids = [m.market_id for m in markets]
        batch_size = 10
        all_price_data = []

        for i in range(0, len(market_ids), batch_size):
            batch = market_ids[i:i + batch_size]
            print(f"[+] Fetching batch {i//batch_size + 1}...")
            try:
                price_data = trading.betting.list_market_book(
                    market_ids=batch,
                    price_projection=filters.price_projection(price_data=['EX_BEST_OFFERS'])
                )
                all_price_data.extend(price_data)
                time.sleep(0.5)
            except Exception as e:
                print(f"[!] Error fetching batch {i//batch_size + 1}: {e}")
                continue

        all_data = []
        for mkt, book in zip(markets, all_price_data):
            try:
                race_time = mkt.market_start_time.strftime("%H:%M")
                course = mkt.event.venue if mkt.event and mkt.event.venue else "Unknown"
                race_id = f"{race_time} {course}"

                for runner, runner_book in zip(mkt.runners, book.runners):
                    prices = runner_book.ex.available_to_back
                    best_price = prices[0].price if prices else None

                    all_data.append({
                        "race": race_id,
                        "horse": runner.runner_name,
                        "price": round(best_price, 2) if best_price else None,
                        "selection_id": runner.selection_id,
                        "market_id": mkt.market_id,
                    })
            except Exception as e:
                print(f"[!] Error processing market {mkt.market_id}: {e}")
                continue

        print(f"[+] Saving {len(all_data)} runner odds to {output_path}")
        with open(output_path, "w") as f:
            json.dump(all_data, f, indent=2)

    finally:
        trading.logout()
        print("[+] Logged out")

if __name__ == "__main__":
    main()
