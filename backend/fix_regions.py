
import os
import sys
import logging
import re

# Setup database context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def determine_correct_region(term: GlossaryTerm) -> str | None:
    title_lower = term.term.lower()
    
    # Strict Dictionary for known Regulatory bodies
    if "fcc" in title_lower or "47 cfr" in title_lower:
        return "USA"
    if "etsi" in title_lower or "en 300" in title_lower or "red 2014" in title_lower:
        return "EU"
    if "arib" in title_lower or "telec" in title_lower:
        return "Japan"
    if "anatel" in title_lower:
        return "Brazil"
    if "ised" in title_lower or "rss-" in title_lower:
        return "Canada"
    if "vcci" in title_lower:
        return "Japan"
    if "acma" in title_lower:
        return "Australia"
    if "kc" in title_lower and "mark" in title_lower:
         return "South Korea"
         
    # If category is Regulatory, maybe keep existing IF it's not "Japan" derived from "mic"
    # Actually, simplistic rule: If it's a general concept (Ampere, Volt, Decibel, etc.), it MUST be None.
    
    technical_concepts = [
        "ampere", "volt", "watt", "hertz", "decibel", "ohm", "farad", "henry", "joule", "kelvin", "tesla",
        "bandwidth", "beam width", "noise", "gain", "loss", "impedance", "modulation", "emc", "emi", "ems",
        "sar", "mimo", "ofdm", "dsss", "fhss", "bluetooth", "wi-fi", "wlan", "radar", "radio"
    ]
    
    for concept in technical_concepts:
        if concept in title_lower:
            # Check if title is JUST the concept or "Concept (Symbol)"
            # vs "Japan Radio Law"
            # If title has no country name, it's global
            country_names = ["japan", "usa", "canada", "brazil", "china", "europe", "eu", "korea"]
            if not any(c in title_lower for c in country_names):
                return None

    # If we are here, and current region is Japan, check if we really mean it
    if term.region == "Japan":
        # The previous bug matched "mic" in content.
        # Verify if "MIC" or "ARIB" or "TELEC" or "Japan" is in title
        if any(x in title_lower for x in ["mic", "arib", "telec", "japan", "vcci"]):
            return "Japan"
        return None # Reset if it was likely a false positive

    # Preserve other existing correct ones (e.g. USA matched correctly)
    return term.region

def fix_regions():
    db = SessionLocal()
    try:
        terms = db.query(GlossaryTerm).all()
        logger.info(f"Scanning {len(terms)} terms for incorrect regions...")
        
        updated_count = 0
        
        for term in terms:
            old_region = term.region
            new_region = determine_correct_region(term)
            
            if old_region != new_region:
                logger.info(f"FIX: '{term.term}' | {old_region} -> {new_region}")
                term.region = new_region
                updated_count += 1
                
        if updated_count > 0:
            db.commit()
            logger.info(f"Successfully updated {updated_count} terms.")
        else:
            logger.info("No terms needed fixing.")
            
    finally:
        db.close()

if __name__ == "__main__":
    fix_regions()
