#!/usr/bin/env python3
# brief.py — CLI client
# Usage:  python brief.py "your topic here"
#
# Install: pip install requests python-dotenv
# Needs:   server.py running on localhost:3000

import sys
import os
import re
import requests
from datetime import date
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("BRIEF_SERVER_URL", "http://localhost:3000")
TOKEN  = os.getenv("MCP_HTTP_TOKEN",   "changeme")

if len(sys.argv) < 2:
    print('Usage: python brief.py "your topic"')
    sys.exit(1)

TOPIC = sys.argv[1]

HEADERS = {
    "Content-Type":  "application/json",
    "Authorization": f"Bearer {TOKEN}",
}

def call(endpoint: str, body: dict) -> dict | list:
    resp = requests.post(f"{SERVER}/tools/{endpoint}", json=body, headers=HEADERS, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"{endpoint} failed ({resp.status_code}): {resp.text}")
    return resp.json()

def main():
    print(f'\n🔍  Searching for: "{TOPIC}"\n')

    # 1. Search
    results = call("search_web", {"query": TOPIC, "k": 6})
    print(f"   Found {len(results)} results.")

    # 2. Fetch readable text from first 3 distinct domains
    seen, to_fetch = set(), []
    for r in results:
        host = urlparse(r["url"]).hostname or ""
        if host not in seen:
            seen.add(host)
            to_fetch.append(r)
        if len(to_fetch) == 3:
            break

    print(f"\n📄  Fetching content from {len(to_fetch)} domains…")
    docs = []
    for r in to_fetch:
        try:
            page = call("fetch_readable", {"url": r["url"]})
            docs.append({"title": page.get("title") or r["title"],
                         "url":   r["url"],
                         "text":  page.get("text", "")})
            print(f"   ✓ {urlparse(r['url']).hostname}")
        except RuntimeError as e:
            print(f"   ✗ {r['url']}: {e}")

    if not docs:
        print("No content fetched — try a different topic or increase k.")
        sys.exit(1)

    # 3. Summarize
    print("\n🧠  Summarizing with local LLM…")
    summary = call("summarize_with_citations", {"topic": TOPIC, "docs": docs})

    # 4. Build markdown
    today    = date.today().isoformat()
    filename = f"brief_{today}.md"

    bullets_md = "\n".join(f"- {b}" for b in summary["bullets"])
    sources_md = "\n".join(
        f"{s['i']}. [{s['title']}]({s['url']})" for s in summary["sources"]
    )

    markdown = f"""# Brief: {TOPIC}
_Generated: {today}_

## Summary

{bullets_md}

## Sources

{sources_md}
"""

    # 5. Save
    saved = call("save_markdown", {"filename": filename, "content": markdown})
    print(f"\n✅  Saved → {saved['path']}\n")
    print("── Preview ─────────────────────────────────────────────────")
    print(markdown)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\n❌  Error: {e}")
        sys.exit(1)
