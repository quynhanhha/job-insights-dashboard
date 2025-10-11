# src/utils/dedupe.py
import hashlib
from typing import List

def _key(title, company, location):
    base = f"{(title or '').lower()}|{(company or '').lower()}|{(location or '').lower()}"
    return hashlib.md5(base.encode()).hexdigest()

def dedupe(rows: List[list]) -> List[list]:
    seen, out = set(), []
    for r in rows:
        if not r or len(r) < 4:
            continue
        k = _key(r[1], r[2], r[3])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out
