# src/fetchers/workforce_au.py
import time
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Workforce Australia search tends to live under /individuals/jobs/search
BASE = "https://www.workforceaustralia.gov.au/individuals/jobs/search"

# Unified schema: ["source","title","company","location","posted_at","description","url"]

def _build_url(keyword: str, location: str, page: int) -> str:
    # Page param may be "page" or "start" depending on their template; start with "page"
    params = {
        "keyword": keyword,
        "location": location,
        "page": str(page)
    }
    return f"{BASE}?{urllib.parse.urlencode(params)}"

def _text(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    return t or None

def _parse_cards(html: str) -> List[list]:
    soup = BeautifulSoup(html, "html.parser")

    # Try common card shells
    cards = (
        soup.select("article.job-card, li.job-card, div.job-card") or
        soup.select("li[data-testid*='job-card']") or
        []
    )

    # Fallback: anchors that look like job details
    if not cards:
        anchors = soup.select("a[href*='/individuals/jobs/details']")
        rows = []
        for a in anchors:
            title = _text(a)
            href = a.get("href")
            if not title or not href:
                continue
            url = href if href.startswith("http") else "https://www.workforceaustralia.gov.au" + href
            rows.append(["workforce_au", title, None, None, None, None, url])
        return rows

    rows: List[list] = []
    for c in cards:
        a = c.select_one("a[href*='/individuals/jobs/details'], h3 a, h2 a") or c.find("a")
        title = _text(a)
        href = a.get("href") if a else None
        url = None
        if href:
            url = href if href.startswith("http") else "https://www.workforceaustralia.gov.au" + href

        company = _text(
            c.select_one("[data-testid='company-name'], .company, .job-company")
        )
        location = _text(
            c.select_one("[data-testid='job-location'], .location, .job-location")
        )
        posted = _text(
            c.select_one("[data-testid='posted-date'], .posted, .time")
        )

        if title and url:
            rows.append(["workforce_au", title, company, location, posted, None, url])

    return rows

def fetch_workforce_au(keyword: str, location: str, max_pages: int = 6, delay: float = 1.1, timeout: int = 25) -> List[list]:
    """
    Fetch Workforce Australia listings using Playwright to bypass anti-scraping measures.
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
        
        for page_num in range(1, max_pages + 1):
            url = _build_url(keyword, location, page_num)
            
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                
                html = page.content()
                rows = _parse_cards(html)
                
                if not rows and page_num > 1:
                    break
                    
                all_rows.extend(rows)
                time.sleep(max(0.4, delay))
            except Exception as e:
                print(f"[workforce_au] Error on page {page_num}: {e}")
                break
        
        context.close()
        browser.close()
    
    return all_rows
