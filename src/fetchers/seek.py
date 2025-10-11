# src/fetchers/seek.py
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def _parse_seek_list(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("[data-automation='job-card']") or []
    rows = []
    for c in cards:
        title_el = c.select_one("a[data-automation='jobTitle']")
        company_el = c.select_one("[data-automation='jobCompany']")
        loc_el = c.select_one("[data-automation='jobLocation']")
        url = None
        if title_el and title_el.has_attr("href"):
            href = title_el["href"]
            url = "https://www.seek.com.au" + href if href.startswith("/") else href

        title = title_el.get_text(strip=True) if title_el else None
        company = company_el.get_text(strip=True) if company_el else None
        location = loc_el.get_text(strip=True) if loc_el else None

        if title:
            # Unified schema: source,title,company,location,posted_at,description,url
            rows.append(["seek", title, company, location, None, None, url])
    return rows

def fetch_seek(keyword: str, location: str, max_pages: int = 8, delay: float = 1.2, timeout: int = 25):
    """
    Crawl Seek list pages using Playwright to bypass anti-scraping measures.
    """
    all_rows = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(timeout * 1000)

        for page_num in range(1, max_pages + 1):
            url = f"https://www.seek.com.au/{keyword}-jobs/in-{location}?page={page_num}"
            try:
                page.goto(url, wait_until="domcontentloaded")
                # Give time for JS to load
                page.wait_for_timeout(2000)
                
                html = page.content()
                rows = _parse_seek_list(html)
                
                if not rows:
                    break
                    
                all_rows.extend(rows)
                time.sleep(delay)
            except Exception as e:
                print(f"[seek] Error on page {page_num}: {e}")
                break

        context.close()
        browser.close()
    
    return all_rows

