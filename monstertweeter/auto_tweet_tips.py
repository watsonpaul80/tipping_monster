import os
import json
import tweepy
import pandas as pd
from datetime import date, timedelta
from dotenv import load_dotenv

# === Load credentials from .env or hardcoded fallback ===
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY", "YOUR_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET", "YOUR_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "YOUR_ACCESS_SECRET")

# === Twitter Auth ===
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# === Load today's tips ===
TODAY = date.today().isoformat()
tips_path = f"logs/dispatch/sent_tips_{TODAY}.jsonl"

if not os.path.exists(tips_path):
    print(f"[!] No tips file found: {tips_path}")
    exit(1)

with open(tips_path, "r") as f:
    tips = [json.loads(line.strip()) for line in f]

# === Filter top 5 tips ===
top_tips = sorted([t for t in tips if not t.get("is_sniper")], key=lambda x: x["confidence"], reverse=True)[:5]

if not top_tips:
    print("[!] No valid tips to tweet.")
    exit(0)

# === Load ROI from yesterday ===
yesterday = (date.today() - timedelta(days=1)).isoformat()
roi_path = f"logs/roi/tips_results_{yesterday}_advised.csv"

roi_summary = ""
try:
    if os.path.exists(roi_path):
        df = pd.read_csv(roi_path)
        total_staked = df['Staked'].sum()
        profit = df['Profit'].sum()
        roi = (profit / total_staked) * 100 if total_staked > 0 else 0
        roi_summary = f"📈 Yday ROI: {roi:.1f}% ({profit:+.2f} pts)"
    else:
        roi_summary = "📈 Yday ROI: No data"
except Exception as e:
    roi_summary = "📈 Yday ROI: Error"
    print(f"[!] ROI read error: {e}")

# === Build tweets ===
header = (
    f"🧠 TIPPING MONSTER — Today's AI Tips ({TODAY})\n\n"
    f"Let’s smash the bookies.\n{roi_summary}\n"
)
tweets = [header]

for tip in top_tips:
    race_time, course = tip["race"].split(" ", 1)
    selection = tip["name"]
    conf = round(tip["confidence"] * 100)
    odds = tip.get("bf_sp", "?")
    nap_flag = "🔥 NAP: " if tip.get("is_nap") else ""
    tweets.append(f"🏇 {race_time} {course} — {nap_flag}{selection}\nConf: {conf}% | Odds: {odds}")

footer = (
    f"📊 Total: {len(top_tips)} Tips | Conf ≥ 80%\n"
    f"🧠 ROI tracked\n"
    f"Join the Telegram stable 🧠🐎👇\n"
    f"https://t.me/tippingmonsterai\n"
    f"#TippingMonster #HorseRacing #BettingTips #AIpunter"
)
tweets.append(footer)

# === Post as thread ===
tweet_chain = []
first = api.update_status(status=tweets[0])
tweet_chain.append(first)
in_reply_to = first.id

for t in tweets[1:]:
    next_tweet = api.update_status(status=t, in_reply_to_status_id=in_reply_to, auto_populate_reply_metadata=True)
    tweet_chain.append(next_tweet)
    in_reply_to = next_tweet.id

print(f"[+] Posted {len(tweet_chain)} tweets as thread.")

