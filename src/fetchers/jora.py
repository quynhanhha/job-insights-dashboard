import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch_jora(keyword, location, max_pages=8, delay=1.2, timeout=25):
    """
    Fetch Jora listings using Playwright to bypass anti-scraping measures.
    """
    rows = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(timeout * 1000)
        
        for page_num in range(1, max_pages + 1):
            url = f"https://au.jora.com/j?keyword={keyword}&l={location}&p={page_num}"
            
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("article.job-card, div.job-card, a.job-title") or []
                
                if not cards:
                    break
                    
                for c in cards:
                    a = c.select_one("a.job-title") if c.name != "a" else c
                    title = a.get_text(strip=True) if a else None
                    href = a.get("href") if a else None
                    if href and href.startswith("/"):
                        href = "https://au.jora.com" + href
                    company = (c.select_one(".job-company") or {}).get_text(strip=True) if c.select_one(".job-company") else None
                    location_txt = (c.select_one(".job-location") or {}).get_text(strip=True) if c.select_one(".job-location") else None
                    if title:
                        rows.append(["jora", title, company, location_txt, None, None, href])
                        
                time.sleep(delay)
            except Exception as e:
                print(f"[jora] Error on page {page_num}: {e}")
                break
        
        context.close()
        browser.close()
    
    return rows
