
import os
import sys
# Setup database context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

def audit_summaries():
    db = SessionLocal()
    try:
        terms = db.query(GlossaryTerm).all()
        print(f"Total Terms: {len(terms)}")
        
        missing_summary_count = 0
        placeholder_count = 0
        
        for term in terms:
            s = term.summary.strip() if term.summary else ""
            if not s:
                missing_summary_count += 1
                print(f"MISSING: {term.term}")
            elif s == "No summary available.":
                placeholder_count += 1
                print(f"PLACEHOLDER: {term.term}")
                
        print(f"\nTotal Missing: {missing_summary_count}")
        print(f"Total Placeholder ('No summary available.'): {placeholder_count}")

    finally:
        db.close()

if __name__ == "__main__":
    audit_summaries()
