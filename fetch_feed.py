import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

FEED_URL = "https://orderinthenorth.substack.com/feed"

def fetch_feed():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; OrderInTheNorth/1.0)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def strip_html(html):
    return re.sub(r"<[^>]+>", "", html).strip()

def format_date(pub_date_str):
    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"]:
        try:
            dt = datetime.strptime(pub_date_str.strip(), fmt)
            return dt.strftime("%B %-d, %Y")
        except:
            continue
    return ""

def get_category(categories):
    cats = [c.lower() for c in categories]
    if any("case" in c for c in cats):
        return "case-breakdown"
    if any("everyday" in c for c in cats):
        return "everyday-law"
    if any("law school" in c for c in cats):
        return "law-school"
    return "other"

def parse_items(xml_text):
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = strip_html(item.findtext("description", ""))[:200]
        categories = [c.text for c in item.findall("category") if c.text]
        items.append({
            "title": title,
            "link": link,
            "date": format_date(pub_date),
            "desc": description,
            "cat": get_category(categories)
        })
    return items

def main():
    print(f"Fetching {FEED_URL}...")
    try:
        xml_text = fetch_feed()
        items = parse_items(xml_text)
        print(f"Found {len(items)} posts")
    except Exception as e:
        print(f"Error fetching feed: {e}")
        items = []

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Written articles.json with {len(items)} entries")

if __name__ == "__main__":
    main()
