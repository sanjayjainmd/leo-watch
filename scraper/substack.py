import feedparser
from datetime import datetime, timedelta, timezone

SUBSTACKS = [
    {"name": "Zvi Mowshowitz", "url": "https://thezvi.substack.com/feed"},
    {"name": "Nathan Benaich", "url": "https://nathanbenaich.substack.com/feed"},
    {"name": "Rohit Krishnan", "url": "https://www.strangeloopcanon.com/feed"},
    {"name": "Packy McCormick", "url": "https://www.notboring.co/feed"},
]

KEYWORDS = [
    "leopold", "aschenbrenner", "situational awareness",
    "agi", "compute", "superintelligence", "ai safety",
]

def fetch_substack(since_hours: int = 168) -> list[dict]:
    # Default 168h (weekly) since Substack posts are less frequent
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)

    for sub in SUBSTACKS:
        feed = feedparser.parse(sub["url"])
        for entry in feed.entries:
            published = entry.get("published_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            relevant = any(kw in title or kw in summary for kw in KEYWORDS)
            results.append({
                "source": "substack",
                "author": sub["name"],
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "date": entry.get("published", ""),
                "summary": entry.get("summary", "")[:500],
                "relevant": relevant,
            })

    return results
