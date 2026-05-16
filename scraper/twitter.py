import os
from apify_client import ApifyClient
from datetime import datetime, timedelta

HANDLES = [
    "leopoldasch",
    "karpathy",
    "sama",
    "ESYudkowsky",
    "DarioAmodei",
    "demishassabis",
    "pmarca",
    "nathanbenaich",
    "DavidCahn6",
    "GaryMarcus",
    "robbensinger",
    "scottaaronson",
    "TheZvi",
]

def fetch_tweets(api_key: str, since_hours: int = 24) -> list[dict]:
    client = ApifyClient(api_key)
    since = (datetime.utcnow() - timedelta(hours=since_hours)).strftime("%Y-%m-%d_%H:%M:%S_UTC")
    results = []

    run = client.actor("apidojo/tweet-scraper").call(run_input={
        "handles": HANDLES,
        "maxTweets": 50,
        "since": since,
        "addUserInfo": True,
    })

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append({
            "source": "twitter",
            "author": item.get("author", {}).get("userName", ""),
            "text": item.get("text", ""),
            "url": item.get("url", ""),
            "date": item.get("createdAt", ""),
            "likes": item.get("likeCount", 0),
            "retweets": item.get("retweetCount", 0),
        })

    return results
