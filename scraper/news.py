import feedparser
from datetime import datetime, timedelta, timezone

FEEDS = [
    "https://news.google.com/rss/search?q=Leopold+Aschenbrenner&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Situational+Awareness+LP+fund&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=AGI+hedge+fund+2025&hl=en-US&gl=US&ceid=US:en",
]

def fetch_news(since_hours: int = 24) -> list[dict]:
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published = entry.get("published_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue
            results.append({
                "source": "google_news",
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "date": entry.get("published", ""),
                "summary": entry.get("summary", "")[:400],
            })

    return results
