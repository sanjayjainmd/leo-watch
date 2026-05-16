from apify_client import ApifyClient

CHANNELS = [
    "https://www.youtube.com/@lexfridman",
    "https://www.youtube.com/@DwarkeshPatel",
    "https://www.youtube.com/@80000Hours",
    "https://www.youtube.com/@bg2pod",
]

KEYWORDS = [
    "Leopold Aschenbrenner",
    "Situational Awareness",
    "AGI",
    "artificial general intelligence",
    "AI safety",
    "compute",
]

def fetch_youtube(api_key: str, since_days: int = 1) -> list[dict]:
    client = ApifyClient(api_key)
    results = []

    run = client.actor("streamers/youtube-scraper").call(run_input={
        "startUrls": [{"url": c} for c in CHANNELS],
        "maxResults": 10,
        "maxResultsShorts": 0,
    })

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        title = item.get("title", "").lower()
        desc = item.get("description", "").lower()
        if any(kw.lower() in title or kw.lower() in desc for kw in KEYWORDS):
            results.append({
                "source": "youtube",
                "channel": item.get("channelName", ""),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "date": item.get("date", ""),
                "views": item.get("viewCount", 0),
                "description": item.get("description", "")[:300],
            })

    return results
