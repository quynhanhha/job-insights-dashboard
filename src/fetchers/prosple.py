# src/fetchers/prosple.py
import json
import re
import time
from typing import List, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0 Safari/537.36"
    )
}

SEARCH_BASE = "https://au.prosple.com/search-jobs"

# Unified schema: ["source","title","company","location","posted_at","description","url"]


def _build_url(keyword: str, location: str, page: int) -> str:
    params = {"keywords": keyword, "locations": location, "page": page}
    return f"{SEARCH_BASE}?{urlencode(params)}"


def _extract_next_data_html(html: str) -> Optional[dict]:
    """Try to pull Next.js data from <script id="__NEXT_DATA__">…</script>."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None


def _rows_from_next_data(next_data: dict) -> List[list]:
    """

    Extract job listings from Prosple's Next.js data structure.
    Data lives in props.pageProps.initialResult.opportunities[]
    """
    rows: List[list] = []
    
    try:
        opportunities = (
            next_data.get("props", {})
            .get("pageProps", {})
            .get("initialResult", {})
            .get("opportunities", [])
        )
        
        for opp in opportunities:
            if not isinstance(opp, dict):
                continue
                
            title = opp.get("title")
            if not title:
                continue
            
            # Company from parentEmployer
            company = None
            parent_employer = opp.get("parentEmployer", {})
            if isinstance(parent_employer, dict):
                company = parent_employer.get("title") or parent_employer.get("advertiserName")
            
            # Location from locationDescription or physicalLocations
            location = opp.get("locationDescription")
            if not location:
                physical_locs = opp.get("physicalLocations", [])
                if physical_locs and isinstance(physical_locs, list):
                    location = ", ".join([
                        loc.get("label", "") 
                        for loc in physical_locs 
                        if isinstance(loc, dict) and loc.get("label")
                    ])
            
            # URL from detailPageURL
            url = opp.get("detailPageURL")
            if url and url.startswith("/"):
                url = "https://au.prosple.com" + url
            
            if title and url:
                rows.append(["prosple", title, company, location, None, None, url])
    
    except Exception:
        # If structure changes, fail gracefully
        pass
    
    return rows


def _fetch_static(keyword: str, location: str, page: int, timeout: int) -> Optional[List[list]]:
    """Try SSR/embedded JSON path. Returns rows or None if not found."""
    url = _build_url(keyword, location, page)
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        return None
    nd = _extract_next_data_html(resp.text)
    if not nd:
        return None
    rows = _rows_from_next_data(nd)
    return rows or None


def _fetch_with_playwright(keyword: str, location: str, page: int, timeout: int, wait: float) -> List[list]:
    """
    Render with Playwright only if static path fails.
    Requires: pip install playwright && python -m playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        # Playwright not installed; return empty list so caller can decide.
        return []

    url = _build_url(keyword, location, page)
    rows: List[list] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"])
        page_obj = context.new_page()
        page_obj.set_default_timeout(timeout * 1000)
        page_obj.goto(url, wait_until="domcontentloaded")
        # give React a beat to hydrate
        page_obj.wait_for_timeout(int(wait * 1000))

        html = page_obj.content()
        soup = BeautifulSoup(html, "html.parser")

        # Try anchors that look like job detail pages
        anchors = soup.select("a[href*='/graduate-jobs/'], a[href*='/internships/'], a[href*='/cadetships/']")
        for a in anchors:
            title = a.get_text(" ", strip=True)
            href = a.get("href")
            if not title or not href:
                continue
            url2 = "https://au.prosple.com" + href if href.startswith("/") else href

            card = a.find_parent(["article", "li", "div"]) or soup
            company = None
            location_txt = None

            # common label fallbacks
            c_el = card.select_one("[data-testid='organisation-name'], .organisation-name, .job-card__company, .company")
            l_el = card.select_one("[data-testid='location'], .job-card__location, .location, .MuiChip-label")
            if c_el:
                company = c_el.get_text(" ", strip=True)
            if l_el:
                location_txt = l_el.get_text(" ", strip=True)

            rows.append(["prosple", title, company, location_txt, None, None, url2])

        context.close()
        browser.close()

    return rows


def fetch_prosple(
    keyword: str = "software",
    location: str = "melbourne",
    pages: int = 3,
    delay: float = 1.0,
    timeout: int = 25,
    use_playwright_fallback: bool = True,
    verbose: bool = False,
) -> List[list]:
    all_rows: List[list] = []

    for p in range(1, max(1, pages) + 1):
        rows = _fetch_static(keyword, location, p, timeout)
        if not rows and use_playwright_fallback:
            if verbose:
                print(f"[prosple] static parse empty on page {p}; trying Playwright…")
            rows = _fetch_with_playwright(keyword, location, p, timeout, wait=1.0)

        if verbose:
            print(f"[prosple] page {p}: {len(rows or [])} rows")

        if rows:
            all_rows.extend(rows)
        else:
            # if page > 1 and we got nothing, assume we’re at the end
            if p > 1:
                break

        time.sleep(max(0.4, delay))

    return all_rows
