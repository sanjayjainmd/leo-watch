import requests
from datetime import datetime, timedelta

# Situational Awareness LP
PRIMARY_CIK = "0002045724"

# Similar funds to monitor
WATCH_LIST = {
    "0002045724": "Situational Awareness LP",
    "0001336528": "Coatue Management",
    "0001510950": "ARK Investment Management",
}

HEADERS = {"User-Agent": "leo-watch research@example.com"}

def fetch_recent_filings(since_days: int = 1) -> list[dict]:
    results = []
    cutoff = datetime.utcnow() - timedelta(days=since_days)

    for cik, name in WATCH_LIST.items():
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            continue

        data = resp.json()
        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        descriptions = filings.get("primaryDocument", [])

        for form, date_str, accession, doc in zip(forms, dates, accessions, descriptions):
            try:
                filed = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            if filed < cutoff:
                continue

            accession_clean = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_clean}/{doc}"

            results.append({
                "source": "sec_edgar",
                "fund": name,
                "form": form,
                "date": date_str,
                "accession": accession,
                "url": filing_url,
                "index_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}",
            })

    return results

def fetch_latest_holdings(cik: str = PRIMARY_CIK) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return {}

    data = resp.json()
    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])

    for i, form in enumerate(forms):
        if form == "13F-HR":
            return {
                "form": form,
                "date": filings["filingDate"][i],
                "accession": filings["accessionNumber"][i],
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F-HR",
            }
    return {}
