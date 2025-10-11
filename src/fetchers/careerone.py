# src/fetchers/careerone.py
import time
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE = "https://www.careerone.com.au/jobs"

# Unified schema: ["source","title","company","location","posted_at","description","url"]

def _build_url(keyword: str, location: str, page: int) -> str:
    params = {
        "q": keyword,
        "l": location,   # e.g., "melbourne-vic" or just "melbourne"
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

    # Try common card containers first
    cards = (
        soup.select("article") or
        soup.select("div[data-automation='result']") or
        soup.select("div.job") or
        []
    )

    # If we didn't catch any containers, fall back to anchors that look like job detail pages
    if not cards:
        anchors = soup.select("a[href*='/job/']")
        rows = []
        for a in anchors:
            title = _text(a)
            href = a.get("href")
            if not title or not href:
                continue
            url = href if href.startswith("http") else "https://www.careerone.com.au" + href
            rows.append(["careerone", title, None, None, None, None, url])
        return rows

    rows: List[list] = []
    for c in cards:
        a = c.select_one("a[href*='/job/'], a[data-automation='job-title'], h2 a, h3 a") or c.find("a")
        title = _text(a)
        href = a.get("href") if a else None
        url = None
        if href:
            url = href if href.startswith("http") else "https://www.careerone.com.au" + href

        company = _text(
            c.select_one("[data-automation='company-name'], .company, .job-company")
        )
        location = _text(
            c.select_one("[data-automation='job-location'], .location, .job-location")
        )
        posted = _text(
            c.select_one(".posted, .time, [data-automation='job-age']")
        )

        if title and url:
            rows.append(["careerone", title, company, location, posted, None, url])

    return rows

def fetch_careerone(keyword: str, location: str, max_pages: int = 6, delay: float = 1.1, timeout: int = 25) -> List[list]:
    """
    Fetch CareerOne listings using Playwright to bypass anti-scraping measures.
    """
    all_rows: List[list] = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
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
                print(f"[careerone] Error on page {page_num}: {e}")
                break
        
        context.close()
        browser.close()
    
    return all_rows
