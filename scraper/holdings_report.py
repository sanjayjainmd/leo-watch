import requests, json, re, xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HEADERS = {"User-Agent": "leo-watch research@example.com"}
CIK_NUM = "2045724"
CIK_PADDED = "0002045724"

FILINGS = [
    ("Q4 2025", "2026-02-11", "0002045724-26-000002"),
    ("Q3 2025", "2025-11-14", "0002045724-25-000008"),
    ("Q2 2025", "2025-08-14", "0002045724-25-000006"),
    ("Q1 2025", "2025-05-14", "0002045724-25-000002"),
    ("Q4 2024", "2025-02-12", "0000935836-25-000120"),
]

QUARTERS_ORDER = ["Q4 2024", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]


def get_xml_filename(acc_clean):
    url = f"https://www.sec.gov/Archives/edgar/data/{CIK_NUM}/{acc_clean}/"
    r = requests.get(url, headers=HEADERS, timeout=15)
    files = re.findall(r'/Archives/edgar/data/[^"]+\.xml', r.text)
    data_files = [f for f in files if "primary_doc" not in f]
    return data_files[0] if data_files else None


def parse_holdings(xml_url):
    r = requests.get(xml_url, headers=HEADERS, timeout=15)
    root = ET.fromstring(r.content)
    holdings = []
    for node in root.iter():
        if node.tag.endswith("infoTable"):
            h = {child.tag.split("}")[-1]: child.text for child in node}
            holdings.append({
                "name": h.get("nameOfIssuer", ""),
                "cusip": h.get("cusip", ""),
                "value": int(h.get("value", 0) or 0),
                "shares": int(h.get("sshPrnamt", 0) or 0),
                "put_call": h.get("putCall", ""),
                "type": h.get("sshPrnamtType", ""),
            })
    return holdings


def fetch_all_quarters():
    all_quarters = {}
    for label, date, accession in FILINGS:
        acc_clean = accession.replace("-", "")
        xml_path = get_xml_filename(acc_clean)
        if not xml_path:
            continue
        holdings = parse_holdings(f"https://www.sec.gov{xml_path}")
        all_quarters[label] = {
            "date": date,
            "accession": accession,
            "holdings": sorted(holdings, key=lambda x: -x["value"]),
        }
    return all_quarters


def build_report(all_quarters: dict) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("SITUATIONAL AWARENESS LP — COMPLETE HOLDINGS HISTORY SINCE INCEPTION")
    lines.append("CIK: 0002045724  |  Leopold Aschenbrenner, CIO")
    lines.append(f"Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 72)

    quarter_maps = {}

    # Per-quarter detail
    for q in QUARTERS_ORDER:
        if q not in all_quarters:
            continue
        d = all_quarters[q]
        holdings = d["holdings"]
        total = sum(h["value"] for h in holdings)
        quarter_maps[q] = {h["cusip"]: h for h in holdings}

        lines.append(f"\n{'─'*72}")
        lines.append(f"  {q}  |  Filed: {d['date']}  |  Total: ${total/1e6:.1f}M")
        lines.append(f"{'─'*72}")
        lines.append(f"  {'POSITION':<42} {'VALUE':>10}  {'TYPE'}")
        lines.append(f"  {'─'*42} {'─'*10}  {'─'*8}")
        for h in holdings:
            pc = f" [{h['put_call']}]" if h["put_call"] else ""
            lines.append(f"  {h['name']+pc:<42} ${h['value']/1e6:>8.1f}M  {h['type']}")

    # Transaction history
    lines.append(f"\n{'='*72}")
    lines.append("TRANSACTION HISTORY — BUYS, SELLS & SIZE CHANGES")
    lines.append("=" * 72)

    prev_q = None
    for q in QUARTERS_ORDER:
        if q not in all_quarters:
            continue
        if prev_q is None:
            lines.append(f"\n  {q} — INCEPTION (first 13F filing)")
            for h in all_quarters[q]["holdings"]:
                pc = f" [{h['put_call']}]" if h["put_call"] else ""
                lines.append(f"    NEW ▶  {h['name']+pc:<42}  ${h['value']/1e6:.1f}M")
            prev_q = q
            continue

        prev = quarter_maps[prev_q]
        curr = quarter_maps[q]

        new_pos = [h for cusip, h in curr.items() if cusip not in prev]
        closed  = [h for cusip, h in prev.items() if cusip not in curr]
        changed = []
        for cusip, h in curr.items():
            if cusip in prev:
                old_val = prev[cusip]["value"]
                new_val = h["value"]
                pct = ((new_val - old_val) / old_val * 100) if old_val else 0
                if abs(pct) > 5:
                    changed.append((h, old_val, new_val, pct))

        lines.append(f"\n  {prev_q} → {q}  (filed {all_quarters[q]['date']})")

        if new_pos:
            lines.append("  NEW BUYS:")
            for h in sorted(new_pos, key=lambda x: -x["value"]):
                pc = f" [{h['put_call']}]" if h["put_call"] else ""
                lines.append(f"    ▶ BUY   {h['name']+pc:<42}  ${h['value']/1e6:.1f}M")

        if closed:
            lines.append("  CLOSED / SOLD:")
            for h in sorted(closed, key=lambda x: -x["value"]):
                pc = f" [{h['put_call']}]" if h["put_call"] else ""
                lines.append(f"    ◀ SELL  {h['name']+pc:<42}  ${h['value']/1e6:.1f}M")

        if changed:
            lines.append("  POSITION CHANGES (>5%):")
            for h, old, new, pct in sorted(changed, key=lambda x: -abs(x[3])):
                pc = f" [{h['put_call']}]" if h["put_call"] else ""
                arrow = "▲ ADDED" if pct > 0 else "▼ TRIM "
                lines.append(
                    f"    {arrow}  {h['name']+pc:<42}  "
                    f"${old/1e6:.1f}M → ${new/1e6:.1f}M  ({pct:+.0f}%)"
                )

        prev_q = q

    lines.append(f"\n{'='*72}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Fetching all 13F filings from SEC EDGAR...")
    quarters = fetch_all_quarters()

    report = build_report(quarters)
    print(report)

    # Save JSON data
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "sa_holdings.json", "w") as f:
        json.dump(quarters, f, indent=2, default=str)

    # Save text report
    report_path = out_dir / "sa_holdings_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nSaved → data/sa_holdings.json")
    print(f"Saved → data/sa_holdings_report.txt")
