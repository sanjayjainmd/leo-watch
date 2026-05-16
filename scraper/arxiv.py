import requests
from datetime import datetime, timedelta, timezone

AUTHOR_KEYWORDS = ["aschenbrenner"]
TOPIC_KEYWORDS = [
    "AGI timeline",
    "transformative AI",
    "compute scaling",
    "AI safety alignment",
    "situational awareness",
]

def fetch_arxiv(since_days: int = 1) -> list[dict]:
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    base_url = "http://export.arxiv.org/api/query"

    queries = AUTHOR_KEYWORDS + TOPIC_KEYWORDS
    for q in queries:
        params = {
            "search_query": f"all:{q}",
            "start": 0,
            "max_results": 10,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        resp = requests.get(base_url, params=params, timeout=15)
        if resp.status_code != 200:
            continue

        import xml.etree.ElementTree as ET
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.text)

        for entry in root.findall("atom:entry", ns):
            published_str = entry.findtext("atom:published", "", ns)
            try:
                published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except ValueError:
                continue
            if published < cutoff:
                continue

            authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
            results.append({
                "source": "arxiv",
                "title": entry.findtext("atom:title", "", ns).strip(),
                "authors": ", ".join(authors),
                "url": entry.findtext("atom:id", "", ns),
                "date": published_str,
                "summary": entry.findtext("atom:summary", "", ns).strip()[:400],
                "query": q,
            })

    return results
