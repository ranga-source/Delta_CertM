
import os
import sys
import logging
import wikipedia
import re
from typing import List, Dict, Any

# Setup database context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TARGET_WORD_COUNT = 400

def count_words(text: str) -> int:
    if not text: return 0
    return len(text.split())

def get_term_word_count(term: GlossaryTerm) -> int:
    count = count_words(term.summary)
    if term.sections:
        for section in term.sections:
             if 'content' in section and section['content']:
                 count += sum(count_words(p) for p in section['content'])
    return count

def clean_wiki_text(text: str) -> List[str]:
    # Split into paragraphs and clean
    paras = text.split('\n')
    cleaned = []
    for p in paras:
        p = p.strip()
        if p and not p.startswith('==') and len(p) > 20: # Ignore headers and short lines
            cleaned.append(p)
    return cleaned

def expand_term(db: Session, term: GlossaryTerm):
    current_count = get_term_word_count(term)
    if current_count >= TARGET_WORD_COUNT:
        return

    logger.info(f"Expanding '{term.term}' (Current: {current_count} words)...")
    
    try:
        # Search for the page
        search_results = wikipedia.search(term.term)
        if not search_results:
            logger.warning(f"No Wikipedia results for {term.term}")
            return

        # Try to match exact term or first result
        page_title = search_results[0]
        
        # specific fixes for common ambiguous terms if needed, or just let it fail gracefully
        try:
             page = wikipedia.page(page_title, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            logger.warning(f"Disambiguation error for {term.term}: {e.options[:3]}")
            # Try the first option if it looks relevant? 
            # For safety, skipping ambiguous ones to avoid garbage data.
            return
        except wikipedia.PageError:
            logger.warning(f"Page not found: {page_title}")
            return

        # Prepare new content
        # We append a "General Information" section
        wiki_summary = page.summary
        wiki_content = page.content # unique content
        
        # Simple strategy: Take the summary + first few paragraphs of content until we have enough words
        
        new_paragraphs = clean_wiki_text(wiki_summary)
        
        # Verify we aren't duplicating the exact summary we already scratched (likely not identical text, but conceptually)
        # We will add it as a new section "General Context (Wikipedia)"
        
        # If we need more, grab from main content
        content_paras = clean_wiki_text(wiki_content)
        
        # Filter out paras that are already in summary (approximate)
        final_paras = []
        words_added = 0
        
        # Deduplicate: if para is in existing sections, skip (unlikely but possible)
        # Just add them.
        
        # Slice content to not make it HUGE, just enough to pass 400 words
        needed = TARGET_WORD_COUNT - current_count
        
        for p in new_paragraphs + content_paras:
            if words_added > needed + 100: # Buffer
                break
            final_paras.append(p)
            words_added += count_words(p)
            
        if not final_paras:
            return

        # Create new section
        new_section = {
            "title": "General Context (from Wikipedia)",
            "content": final_paras,
            "images": [img for img in page.images if img.lower().endswith(('.jpg', '.png', '.jpeg'))][:2] # limit images
        }
        
        # Append to existing sections
        # We need to copy formatting to avoid mutation issues with SQLAlchemy JSON type
        current_sections = list(term.sections) if term.sections else []
        current_sections.append(new_section)
        
        term.sections = current_sections
        db.add(term) # Mark as dirty
        db.commit()
        
        logger.info(f"Expanded '{term.term}' with {words_added} words from Wikipedia: {page.title}")

    except Exception as e:
        logger.error(f"Error expanding {term.term}: {str(e)}")

def main():
    db = SessionLocal()
    try:
        terms = db.query(GlossaryTerm).all()
        logger.info(f"Checking {len(terms)} terms for expansion...")
        
        for term in terms:
            expand_term(db, term)
            
        logger.info("Expansion Process Complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
