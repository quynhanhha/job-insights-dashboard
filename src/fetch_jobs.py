# src/fetch_jobs.py
import csv
from datetime import datetime
from .fetchers.seek import fetch_seek
from .fetchers.prosple import fetch_prosple
from .fetchers.jora import fetch_jora
from .fetchers.indeed import fetch_indeed
from .fetchers.careerone import fetch_careerone
from .fetchers.workforce_au import fetch_workforce_au
from .utils.normalize import normalize_rows
from .utils.dedupe import dedupe

QUERIES = [
    # (source, keyword, location, kwargs)
    
    # ========== PROSPLE - Australia (WORKING ✓) ==========
    # Software & Engineering
    ("prosple", "software", "australia", {"pages": 10}),
    ("prosple", "software engineer", "australia", {"pages": 8}),
    ("prosple", "software developer", "australia", {"pages": 8}),
    ("prosple", "software engineering", "australia", {"pages": 8}),
    ("prosple", "developer", "australia", {"pages": 10}),
    ("prosple", "programming", "australia", {"pages": 6}),
    ("prosple", "web developer", "australia", {"pages": 6}),
    ("prosple", "frontend", "australia", {"pages": 5}),
    ("prosple", "backend", "australia", {"pages": 5}),
    ("prosple", "full stack", "australia", {"pages": 6}),
    ("prosple", "mobile developer", "australia", {"pages": 5}),
    ("prosple", "application developer", "australia", {"pages": 5}),
    
    # Data & Analytics
    ("prosple", "data", "australia", {"pages": 10}),
    ("prosple", "data science", "australia", {"pages": 8}),
    ("prosple", "data scientist", "australia", {"pages": 8}),
    ("prosple", "data analyst", "australia", {"pages": 10}),
    ("prosple", "data engineer", "australia", {"pages": 8}),
    ("prosple", "business analyst", "australia", {"pages": 10}),
    ("prosple", "business intelligence", "australia", {"pages": 6}),
    ("prosple", "analytics", "australia", {"pages": 8}),
    ("prosple", "machine learning", "australia", {"pages": 6}),
    ("prosple", "artificial intelligence", "australia", {"pages": 6}),
    
    # Technology & IT
    ("prosple", "technology", "australia", {"pages": 10}),
    ("prosple", "information technology", "australia", {"pages": 10}),
    ("prosple", "IT", "australia", {"pages": 10}),
    ("prosple", "tech", "australia", {"pages": 8}),
    ("prosple", "digital", "australia", {"pages": 8}),
    ("prosple", "technology consulting", "australia", {"pages": 6}),
    
    # IT Support & Infrastructure
    ("prosple", "IT support", "australia", {"pages": 6}),
    ("prosple", "technical support", "australia", {"pages": 5}),
    ("prosple", "help desk", "australia", {"pages": 5}),
    ("prosple", "system administrator", "australia", {"pages": 5}),
    ("prosple", "network", "australia", {"pages": 6}),
    ("prosple", "infrastructure", "australia", {"pages": 6}),
    ("prosple", "devops", "australia", {"pages": 5}),
    ("prosple", "cloud", "australia", {"pages": 6}),
    ("prosple", "cybersecurity", "australia", {"pages": 6}),
    ("prosple", "security", "australia", {"pages": 6}),
    
    # Specialized Roles
    ("prosple", "database", "australia", {"pages": 5}),
    ("prosple", "QA", "australia", {"pages": 5}),
    ("prosple", "testing", "australia", {"pages": 5}),
    ("prosple", "product manager", "australia", {"pages": 5}),
    ("prosple", "project manager", "australia", {"pages": 6}),
    ("prosple", "systems analyst", "australia", {"pages": 5}),
    ("prosple", "UX", "australia", {"pages": 4}),
    ("prosple", "UI", "australia", {"pages": 4}),
    
    # Specific Technologies
    ("prosple", "python", "australia", {"pages": 4}),
    ("prosple", "java", "australia", {"pages": 4}),
    ("prosple", "javascript", "australia", {"pages": 4}),
    ("prosple", "AWS", "australia", {"pages": 5}),
    ("prosple", "Azure", "australia", {"pages": 4}),
    
    # ========== WORKFORCE AU - Australia (WORKING ✓) ==========
    # Software & Engineering
    ("workforce_au", "software", "australia", {"max_pages": 10}),
    ("workforce_au", "software engineer", "australia", {"max_pages": 10}),
    ("workforce_au", "software developer", "australia", {"max_pages": 10}),
    ("workforce_au", "developer", "australia", {"max_pages": 10}),
    ("workforce_au", "web developer", "australia", {"max_pages": 8}),
    ("workforce_au", "frontend developer", "australia", {"max_pages": 6}),
    ("workforce_au", "backend developer", "australia", {"max_pages": 6}),
    ("workforce_au", "full stack developer", "australia", {"max_pages": 6}),
    ("workforce_au", "mobile developer", "australia", {"max_pages": 5}),
    ("workforce_au", "application developer", "australia", {"max_pages": 5}),
    
    # Data & Analytics
    ("workforce_au", "data", "australia", {"max_pages": 10}),
    ("workforce_au", "data analyst", "australia", {"max_pages": 10}),
    ("workforce_au", "data scientist", "australia", {"max_pages": 8}),
    ("workforce_au", "data engineer", "australia", {"max_pages": 8}),
    ("workforce_au", "business analyst", "australia", {"max_pages": 10}),
    ("workforce_au", "business intelligence", "australia", {"max_pages": 6}),
    ("workforce_au", "analytics", "australia", {"max_pages": 6}),
    
    # Technology & IT
    ("workforce_au", "technology", "australia", {"max_pages": 10}),
    ("workforce_au", "information technology", "australia", {"max_pages": 10}),
    ("workforce_au", "IT", "australia", {"max_pages": 10}),
    ("workforce_au", "digital", "australia", {"max_pages": 8}),
    
    # IT Support & Infrastructure
    ("workforce_au", "IT support", "australia", {"max_pages": 10}),
    ("workforce_au", "technical support", "australia", {"max_pages": 8}),
    ("workforce_au", "help desk", "australia", {"max_pages": 8}),
    ("workforce_au", "system administrator", "australia", {"max_pages": 8}),
    ("workforce_au", "network engineer", "australia", {"max_pages": 6}),
    ("workforce_au", "devops", "australia", {"max_pages": 6}),
    ("workforce_au", "cloud", "australia", {"max_pages": 6}),
    ("workforce_au", "cybersecurity", "australia", {"max_pages": 6}),
    
    # Specialized Roles
    ("workforce_au", "database administrator", "australia", {"max_pages": 5}),
    ("workforce_au", "QA engineer", "australia", {"max_pages": 5}),
    ("workforce_au", "test engineer", "australia", {"max_pages": 5}),
    ("workforce_au", "product manager", "australia", {"max_pages": 5}),
    ("workforce_au", "project manager", "australia", {"max_pages": 6}),
    
    # ========== WORKFORCE AU - Remote ==========
    ("workforce_au", "software", "remote", {"max_pages": 6}),
    ("workforce_au", "software engineer", "remote", {"max_pages": 6}),
    ("workforce_au", "software developer", "remote", {"max_pages": 6}),
    ("workforce_au", "data analyst", "remote", {"max_pages": 6}),
    ("workforce_au", "business analyst", "remote", {"max_pages": 6}),
    ("workforce_au", "IT support", "remote", {"max_pages": 4}),
    ("workforce_au", "developer", "remote", {"max_pages": 6}),
    
    # ========== BLOCKED SOURCES (Representative Queries Only) ==========
    # These sources have anti-scraping protection and will return 0 results
    # Keeping minimal queries for documentation purposes
    
    # SEEK - Australia (BLOCKED ✗)
    ("seek", "software-engineer", "australia", {"max_pages": 1}),
    ("seek", "data-analyst", "australia", {"max_pages": 1}),
    
    # INDEED - Australia (BLOCKED ✗)
    ("indeed", "software", "australia", {"max_pages": 1}),
    ("indeed", "data-analyst", "australia", {"max_pages": 1}),
    
    # JORA - Australia (BLOCKED ✗)
    ("jora", "software-engineer", "australia", {"max_pages": 1}),
    ("jora", "data-analyst", "australia", {"max_pages": 1}),
    
    # CAREERONE - Australia (BLOCKED ✗)
    ("careerone", "software", "australia", {"max_pages": 1}),
    ("careerone", "data-analyst", "australia", {"max_pages": 1}),
]

def run():
    all_rows = []
    total_queries = len(QUERIES)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting job fetch: {total_queries} queries")
    print("=" * 70)
    
    for idx, (source, kw, loc, kwargs) in enumerate(QUERIES, 1):
        try:
            print(f"[{idx}/{total_queries}] {source.upper()}: '{kw}' in {loc}...", end=" ", flush=True)
            
            if source == "seek":
                rows = fetch_seek(kw, loc, **kwargs)
            elif source == "prosple":
                rows = fetch_prosple(kw, loc, **kwargs)
            elif source == "jora":
                rows = fetch_jora(kw, loc, **kwargs)
            elif source == "indeed":
                rows = fetch_indeed(kw, loc, **kwargs)
            elif source == "careerone":
                rows = fetch_careerone(kw, loc, **kwargs)
            elif source == "workforce_au":
                rows = fetch_workforce_au(kw, loc, **kwargs)
            else:
                rows = []
            
            normalized = normalize_rows(source, rows)
            all_rows += normalized
            print(f"✓ {len(normalized)} jobs")
            
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            continue
    
    print("=" * 70)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Raw total: {len(all_rows)} jobs")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Deduplicating...")
    
    merged = dedupe(all_rows)

    out_path = "data/jobs_merged.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source","title","company","location","posted_at","description","url"])
        w.writerows(merged)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Saved {len(merged)} unique jobs → {out_path}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Removed {len(all_rows) - len(merged)} duplicates")

if __name__ == "__main__":
    run()
