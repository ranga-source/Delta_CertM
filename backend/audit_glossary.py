
import os
import sys
# Setup database context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

import logging
logging.basicConfig(level=logging.ERROR) # Suppress INFO logs

def count_words(text: str) -> int:
    if not text: return 0
    return len(text.split())

def audit():
    db = SessionLocal()
    try:
        terms = db.query(GlossaryTerm).all()
        print(f"Total Terms: {len(terms)}")
        
        region_map = {}
        for term in terms:
            r = term.region or "None"
            if r not in region_map:
                region_map[r] = []
            region_map[r].append(term.term)
            
        for region, items in region_map.items():
            print(f"\nRegion: {region} ({len(items)})")
            # Print sample to detect errors
            print(", ".join(items[:10]) + ("..." if len(items) > 10 else ""))

    finally:
        db.close()

if __name__ == "__main__":
    audit()
