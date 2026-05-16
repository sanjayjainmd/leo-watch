from apify_client import ApifyClient
from datetime import datetime, timedelta

SUBREDDITS = [
    "singularity",
    "MachineLearning",
    "artificial",
    "LessWrong",
    "AIInvesting",
    "stocks",
]

KEYWORDS = [
    "Leopold Aschenbrenner",
    "Situational Awareness",
    "leopoldasch",
    "situational awareness LP",
    "AGI timeline",
    "compute bottleneck",
]

def fetch_reddit(api_key: str, since_hours: int = 24) -> list[dict]:
    client = ApifyClient(api_key)
    results = []
    since_ts = int((datetime.utcnow() - timedelta(hours=since_hours)).timestamp())

    # Search each subreddit for keyword mentions
    for keyword in KEYWORDS:
        run = client.actor("trudax/reddit-scraper-lite").call(run_input={
            "searches": [keyword],
            "maxItems": 20,
            "searchType": "posts",
        })
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            created = item.get("createdAt", 0)
            if isinstance(created, str):
                try:
                    created = int(datetime.fromisoformat(created.replace("Z", "")).timestamp())
                except Exception:
                    created = 0
            if created >= since_ts:
                results.append({
                    "source": "reddit",
                    "subreddit": item.get("subreddit", ""),
                    "title": item.get("title", ""),
                    "text": item.get("selftext", "")[:500],
                    "url": item.get("url", ""),
                    "date": item.get("createdAt", ""),
                    "score": item.get("score", 0),
                    "keyword": keyword,
                })

    return results
