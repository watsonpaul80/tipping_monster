#!/usr/bin/env python3
# check_betfair_market_times.py
import datetime
import pytz
from betfairlightweight import APIClient, filters
from tippingmonster.env_loader import load_env

load_env()

from secrets1 import BF_USERNAME, BF_PASSWORD, BF_APP_KEY, BF_CERT_DIR


def main():
    print("🔎 Checking Betfair market start times (UTC vs BST)...")

    trading = APIClient(
        BF_USERNAME,
        BF_PASSWORD,
        app_key=BF_APP_KEY,
        certs=BF_CERT_DIR
    )

    trading.login()

    today = datetime.datetime.utcnow().date()

    market_filter = filters.market_filter(
        event_type_ids=['7'],  # Horse racing
        market_type_codes=['WIN'],
        market_countries=['GB', 'IE'],
        market_start_time={
            'from': f"{today}T00:00:00Z",
            'to': f"{today}T23:59:00Z"
        }
    )

    markets = trading.betting.list_market_catalogue(
        filter=market_filter,
        max_results=5,  # Keep it light
        market_projection=['EVENT', 'MARKET_START_TIME']
    )

    utc = pytz.utc
    bst = pytz.timezone("Europe/London")

    for mkt in markets:
        raw = mkt.market_start_time
        utc_time = raw.replace(tzinfo=utc)
        local_time = utc_time.astimezone(bst)

        print("📍", mkt.event.venue, "-", mkt.event.name)
        print("   🕐 Betfair UTC :", utc_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("   🕐 Local BST   :", local_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("---")

    trading.logout()


if __name__ == "__main__":
    main()
