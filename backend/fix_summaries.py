
import os
import sys
import logging

# Setup database context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def fix_summaries():
    db = SessionLocal()
    try:
        terms = db.query(GlossaryTerm).all()
        logger.info(f"Scanning {len(terms)} terms for missing summaries...")
        
        updated_count = 0
        
        for term in terms:
            current_summary = term.summary.strip() if term.summary else ""
            
            # Check if summary is missing or placeholder
            if not current_summary or current_summary == "No summary available.":
                # Look for a useful paragraph in sections
                new_summary = None
                
                # Priority 1: Check "General Context (from Wikipedia)"
                if term.sections:
                    for section in term.sections:
                        if "from Wikipedia" in section.get("title", "") and section.get("content"):
                            # Take the first paragraph
                            first_para = section["content"][0]
                            if len(first_para) > 50: # Ensure it's substantial
                                new_summary = first_para
                                break
                                
                    # Priority 2: Check "Overview" or first section if Priority 1 failed
                    if not new_summary and term.sections:
                         first_section = term.sections[0]
                         if first_section.get("content"):
                             first_para = first_section["content"][0]
                             if len(first_para) > 50:
                                 new_summary = first_para
                
                if new_summary:
                    logger.info(f"FIX: '{term.term}' | Summary updated from section content.")
                    # Truncate if too long? No, rich summary is fine.
                    term.summary = new_summary
                    updated_count += 1
                else:
                    logger.warning(f"SKIP: '{term.term}' | No suitable content found for summary.")
            
        if updated_count > 0:
            db.commit()
            logger.info(f"Successfully updated {updated_count} summaries.")
        else:
            logger.info("No summaries required fixing.")
            
    finally:
        db.close()

if __name__ == "__main__":
    fix_summaries()
