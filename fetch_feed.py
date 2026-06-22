import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

FEED_URL = "https://rss.beehiiv.com/feeds/EAthtiKUGq.xml"

def fetch_feed():
    req = urllib.request.Request(
        FEED_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8")
        print(f"Feed fetched successfully, length: {len(content)} chars")
        return content

def strip_html(html):
    return re.sub(r"<[^>]+>", "", html).strip()

def format_date(pub_date_str):
    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"]:
        try:
            dt = datetime.strptime(pub_date_str.strip(), fmt)
            return dt.strftime("%B %-d, %Y")
        except:
            continue
    return pub_date_str

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
    all_items = root.findall(".//item")
    print(f"Found {len(all_items)} items in feed")
    for item in all_items:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = strip_html(item.findtext("description", ""))[:200]
        categories = [c.text for c in item.findall("category") if c.text]
        print(f"  - {title}")
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
        print(f"Parsed {len(items)} posts")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        items = []

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Written articles.json with {len(items)} entries")

if __name__ == "__main__":
    main()
