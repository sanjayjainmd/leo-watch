import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from scraper.twitter import fetch_tweets
from scraper.reddit import fetch_reddit
from scraper.youtube import fetch_youtube
from scraper.linkedin import fetch_linkedin
from scraper.hackernews import fetch_hackernews
from scraper.news import fetch_news
from scraper.substack import fetch_substack
from scraper.sec_edgar import fetch_recent_filings
from scraper.arxiv import fetch_arxiv
from synthesize import build_daily_brief, build_weekly_report
from emailer.send import send_email

APIFY_KEY = os.environ["APIFY_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def save_data(data: list[dict], label: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = DATA_DIR / f"{ts}_{label}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved {len(data)} items → {path}")


def load_week_data() -> list[dict]:
    all_data = []
    for path in sorted(DATA_DIR.glob("*.json"))[-14:]:  # last ~7 days of files
        with open(path) as f:
            all_data.extend(json.load(f))
    return all_data


def scrape(label: str, fn, *args, **kwargs) -> list[dict]:
    """Run a scraper, catch errors so one failure doesn't kill the whole run."""
    try:
        print(f"  → {label}...")
        results = fn(*args, **kwargs)
        print(f"     {len(results)} items")
        return results
    except Exception as e:
        print(f"     WARNING: {label} failed — {e}")
        return []


def run_daily():
    print(f"[{datetime.utcnow()}] Running daily scrape...")
    all_data = []

    all_data += scrape("Twitter", fetch_tweets, APIFY_KEY, since_hours=24)
    all_data += scrape("Reddit", fetch_reddit, APIFY_KEY, since_hours=24)
    all_data += scrape("Hacker News", fetch_hackernews, since_hours=24)
    all_data += scrape("Google News", fetch_news, since_hours=24)
    all_data += scrape("SEC EDGAR", fetch_recent_filings, since_days=1)
    all_data += scrape("ArXiv", fetch_arxiv, since_days=1)
    all_data += scrape("YouTube", fetch_youtube, APIFY_KEY, since_days=1)
    all_data += scrape("LinkedIn", fetch_linkedin, APIFY_KEY)

    print(f"  Total items collected: {len(all_data)}")
    save_data(all_data, "daily")

    print("  → Synthesizing with Claude...")
    brief = build_daily_brief(all_data, ANTHROPIC_KEY)

    date_str = datetime.now(timezone.utc).strftime("%a %b %d")
    subject = f"The Leo Brief — {date_str}"
    send_email(subject, brief, RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_PASSWORD)
    print("  Done.")


def run_weekly():
    print(f"[{datetime.utcnow()}] Running weekly deep dive...")

    fresh = []
    fresh += scrape("Twitter (7d)", fetch_tweets, APIFY_KEY, since_hours=168)
    fresh += scrape("Reddit (7d)", fetch_reddit, APIFY_KEY, since_hours=168)
    fresh += scrape("Substack (7d)", fetch_substack, since_hours=168)
    fresh += scrape("YouTube (7d)", fetch_youtube, APIFY_KEY, since_days=7)
    fresh += scrape("SEC EDGAR (7d)", fetch_recent_filings, since_days=7)
    fresh += scrape("ArXiv (7d)", fetch_arxiv, since_days=7)
    fresh += scrape("Hacker News (7d)", fetch_hackernews, since_hours=168)
    fresh += scrape("Google News (7d)", fetch_news, since_hours=168)

    stored = load_week_data()
    all_data = fresh + stored
    save_data(fresh, "weekly_fresh")

    print(f"  → Synthesizing {len(all_data)} total items with Claude...")
    report = build_weekly_report(all_data, ANTHROPIC_KEY)

    week_str = datetime.now(timezone.utc).strftime("Week of %b %d, %Y")
    subject = f"The Leo Deep Dive — {week_str}"
    send_email(subject, report, RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_PASSWORD)
    print("  Done.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    if mode == "weekly":
        run_weekly()
    else:
        run_daily()
