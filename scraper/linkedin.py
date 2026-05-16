from apify_client import ApifyClient

PROFILES = [
    "https://www.linkedin.com/in/leopold-aschenbrenner/",
]

KEYWORDS = [
    "Leopold Aschenbrenner",
    "Situational Awareness LP",
    "AGI",
]

def fetch_linkedin(api_key: str) -> list[dict]:
    client = ApifyClient(api_key)
    results = []

    # Search LinkedIn for keyword mentions
    for keyword in KEYWORDS:
        run = client.actor("curious_coder/linkedin-post-search-scraper").call(run_input={
            "keywords": keyword,
            "maxResults": 10,
        })
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append({
                "source": "linkedin",
                "author": item.get("authorName", ""),
                "text": item.get("text", "")[:500],
                "url": item.get("postUrl", ""),
                "date": item.get("postedAt", ""),
                "likes": item.get("numLikes", 0),
                "keyword": keyword,
            })

    return results
