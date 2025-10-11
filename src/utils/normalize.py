# src/utils/normalize.py
from typing import List

SCHEMA = ["source", "title", "company", "location", "posted_at", "description", "url"]

def normalize_rows(source: str, rows: List[list]) -> List[list]:
    """
    Ensure each row matches the unified schema length and has correct source.
    """
    out = []
    for r in rows:
        if not r:
            continue
        # If already shaped correctly, pass through
        if len(r) == len(SCHEMA) and r[0] == source:
            out.append(r)
            continue
        # Otherwise patch
        padded = [None] * len(SCHEMA)
        padded[0] = source
        for i in range(1, min(len(SCHEMA), len(r) + 1)):
            padded[i] = r[i - 1] if i - 1 < len(r) else None
        out.append(padded)
    return out
