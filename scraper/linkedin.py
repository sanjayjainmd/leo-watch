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
    for keyword in KEYWORDS:
        try:
            run = client.actor("curious_coder/linkedin-posts-scraper").call(run_input={
                "keywords": [keyword],
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
        except Exception as e:
            print(f"LinkedIn scraper failed for '{keyword}': {e}")
            continue
    return results
