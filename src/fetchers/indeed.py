# src/fetchers/indeed.py
import time
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE = "https://au.indeed.com/jobs"

# Unified schema: ["source","title","company","location","posted_at","description","url"]


def _build_url(keyword: str, location: str, start: int) -> str:
    params = {
        "q": keyword,
        "l": location,
        "start": str(start),  # pagination offset: 0,10,20...
        "radius": "50",
    }
    return f"{BASE}?{urllib.parse.urlencode(params)}"


def _text(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    return t or None


def _parse_cards(html: str) -> List[list]:
    soup = BeautifulSoup(html, "html.parser")

    # Indeed loves changing class names; target stable attributes first
    cards = soup.select("div[class*='jobsearch-SerpJobCard'], a[data-jk], div[data-jk]")
    if not cards:
        # fallback to generic result items
        cards = soup.select("div[id^='job_'], div.result, a.tapItem")

    rows: List[list] = []
    for c in cards:
        # Title + link
        a = c.select_one("a[aria-label], a.jcs-JobTitle, a.tapItem")
        if not a:
            # sometimes the anchor is nested differently
            a = c.find("a")
        title = _text(a)
        href = a.get("href") if a else None
        if href and href.startswith("/"):
            url = "https://au.indeed.com" + href
        else:
            url = href

        # Company, location, posted_at
        company = _text(
            c.select_one(".companyName, span.company, span[data-testid='company-name']")
        )
        location = _text(
            c.select_one(".companyLocation, div.location, span[data-testid='text-location']")
        )
        posted = _text(
            c.select_one("span.date, span[data-testid='myJobsStateDate']")
        )

        if title and url:
            rows.append(["indeed", title, company, location, posted, None, url])

    return rows


def fetch_indeed(keyword: str, location: str, max_pages: int = 6, delay: float = 1.2, timeout: int = 25) -> List[list]:
    """
    Paginate Indeed search using Playwright to bypass anti-scraping measures.
    """
    all_rows: List[list] = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
            locale="en-AU"
        )
        page = context.new_page()
        page.set_default_timeout(timeout * 1000)

        for page_num in range(max_pages):
            start = page_num * 10
            url = _build_url(keyword, location, start)
            
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                
                html = page.content()
                rows = _parse_cards(html)
                
                if not rows:
                    break
                
                all_rows.extend(rows)
                time.sleep(max(0.5, delay))
            except Exception as e:
                print(f"[indeed] Error on page {page_num}: {e}")
                break

        context.close()
        browser.close()

    return all_rows
