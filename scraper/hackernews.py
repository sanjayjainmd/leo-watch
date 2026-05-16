import requests
from datetime import datetime, timedelta

KEYWORDS = [
    "Leopold Aschenbrenner",
    "Situational Awareness",
    "leopoldasch",
    "AGI timeline",
]

def fetch_hackernews(since_hours: int = 24) -> list[dict]:
    results = []
    since_ts = int((datetime.utcnow() - timedelta(hours=since_hours)).timestamp())

    for keyword in KEYWORDS:
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "query": keyword,
            "tags": "(story,comment)",
            "numericFilters": f"created_at_i>{since_ts}",
            "hitsPerPage": 20,
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            continue

        for hit in resp.json().get("hits", []):
            results.append({
                "source": "hackernews",
                "title": hit.get("title") or hit.get("comment_text", "")[:100],
                "text": hit.get("story_text") or hit.get("comment_text", "")[:500],
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "date": hit.get("created_at", ""),
                "points": hit.get("points", 0),
                "keyword": keyword,
            })

    return results
