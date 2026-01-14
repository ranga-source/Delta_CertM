
import os
import requests
import logging
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Dict, Any, Optional

# Setup database context
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import GlossaryTerm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

URLS = [
    "https://ib-lenhardt.com/kb/glossary/47-cfr-part-15",
    "https://ib-lenhardt.com/kb/glossary/accreditation",
    "https://ib-lenhardt.com/kb/glossary/afc",
    "https://ib-lenhardt.com/kb/glossary/ampere",
    "https://ib-lenhardt.com/kb/glossary/amplitude-modulation",
    "https://ib-lenhardt.com/kb/glossary/antenna-directivity",
    "https://ib-lenhardt.com/kb/glossary/antenna-gain",
    "https://ib-lenhardt.com/kb/glossary/antenna-polarization",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t48",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t66",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t71",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t75",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t91",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t104",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t107",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t108",
    "https://ib-lenhardt.com/kb/glossary/arib-std-t111",
    "https://ib-lenhardt.com/kb/glossary/awgn",
    "https://ib-lenhardt.com/kb/glossary/bandwidth",
    "https://ib-lenhardt.com/kb/glossary/beam-width",
    "https://ib-lenhardt.com/kb/glossary/bit-error-rate",
    "https://ib-lenhardt.com/kb/glossary/bluetooth-classic-br-edr",
    "https://ib-lenhardt.com/kb/glossary/bluetooth-le-audio",
    "https://ib-lenhardt.com/kb/glossary/bluetooth-le",
    "https://ib-lenhardt.com/kb/glossary/bluetooth-mesh",
    "https://ib-lenhardt.com/kb/glossary/bss",
    "https://ib-lenhardt.com/kb/glossary/carrier-to-noise-ratio",
    "https://ib-lenhardt.com/kb/glossary/ce-mark",
    "https://ib-lenhardt.com/kb/glossary/certification",
    "https://ib-lenhardt.com/kb/glossary/channel-bandwidth",
    "https://ib-lenhardt.com/kb/glossary/channel-number",
    "https://ib-lenhardt.com/kb/glossary/conducted-emissions",
    "https://ib-lenhardt.com/kb/glossary/conducted-measurements",
    "https://ib-lenhardt.com/kb/glossary/conformity-assessment",
    "https://ib-lenhardt.com/kb/glossary/coulomb",
    "https://ib-lenhardt.com/kb/glossary/decibel",
    "https://ib-lenhardt.com/kb/glossary/dbd",
    "https://ib-lenhardt.com/kb/glossary/dbi",
    "https://ib-lenhardt.com/kb/glossary/dbm",
    "https://ib-lenhardt.com/kb/glossary/dfs",
    "https://ib-lenhardt.com/kb/glossary/dut",
    "https://ib-lenhardt.com/kb/glossary/dsss",
    "https://ib-lenhardt.com/kb/glossary/ece-r-10",
    "https://ib-lenhardt.com/kb/glossary/ece-type-approval",
    "https://ib-lenhardt.com/kb/glossary/eirp",
    "https://ib-lenhardt.com/kb/glossary/erp",
    "https://ib-lenhardt.com/kb/glossary/electric-field-strength",
    "https://ib-lenhardt.com/kb/glossary/emc",
    "https://ib-lenhardt.com/kb/glossary/emc-pre-compliance",
    "https://ib-lenhardt.com/kb/glossary/emi",
    "https://ib-lenhardt.com/kb/glossary/ems",
    "https://ib-lenhardt.com/kb/glossary/en-55032-cispr-32",
    "https://ib-lenhardt.com/kb/glossary/en-55035-cispr-35",
    "https://ib-lenhardt.com/kb/glossary/en-61000-6-2",
    "https://ib-lenhardt.com/kb/glossary/en-61000-6-3",
    "https://ib-lenhardt.com/kb/glossary/etsi-en-300-220",
    "https://ib-lenhardt.com/kb/glossary/en-300-328",
    "https://ib-lenhardt.com/kb/glossary/en-301-893",
    "https://ib-lenhardt.com/kb/glossary/en-301-489-1",
    "https://ib-lenhardt.com/kb/glossary/etsi-en-303-687",
    "https://ib-lenhardt.com/kb/glossary/doc",
    "https://ib-lenhardt.com/kb/glossary/fcc-15-247",
    "https://ib-lenhardt.com/kb/glossary/fcc-15-407",
    "https://ib-lenhardt.com/kb/glossary/fspl",
    "https://ib-lenhardt.com/kb/glossary/frequency",
    "https://ib-lenhardt.com/kb/glossary/fhss",
    "https://ib-lenhardt.com/kb/glossary/frequency-modulation",
    "https://ib-lenhardt.com/kb/glossary/gain-method",
    "https://ib-lenhardt.com/kb/glossary/gauss",
    "https://ib-lenhardt.com/kb/glossary/harmonized-standard",
    "https://ib-lenhardt.com/kb/glossary/hertz",
    "https://ib-lenhardt.com/kb/glossary/ices-003",
    "https://ib-lenhardt.com/kb/glossary/impedance",
    "https://ib-lenhardt.com/kb/glossary/importer-authorized-representative",
    "https://ib-lenhardt.com/kb/glossary/ised-rss-210",
    "https://ib-lenhardt.com/kb/glossary/ised-rss-247",
    "https://ib-lenhardt.com/kb/glossary/ised-rss-310",
    "https://ib-lenhardt.com/kb/glossary/rss-gen",
    "https://ib-lenhardt.com/kb/glossary/iso-17025",
    "https://ib-lenhardt.com/kb/glossary/itu",
    "https://ib-lenhardt.com/kb/glossary/itu-r",
    "https://ib-lenhardt.com/kb/glossary/joule",
    "https://ib-lenhardt.com/kb/glossary/kelvin",
    "https://ib-lenhardt.com/kb/glossary/loss",
    "https://ib-lenhardt.com/kb/glossary/lpi",
    "https://ib-lenhardt.com/kb/glossary/magnetic-field-strength",
    "https://ib-lenhardt.com/kb/glossary/market-access",
    "https://ib-lenhardt.com/kb/glossary/market-surveillance",
    "https://ib-lenhardt.com/kb/glossary/milliwatt",
    "https://ib-lenhardt.com/kb/glossary/mu-mimo",
    "https://ib-lenhardt.com/kb/glossary/mra",
    "https://ib-lenhardt.com/kb/glossary/notified-body",
    "https://ib-lenhardt.com/kb/glossary/noise-figure",
    "https://ib-lenhardt.com/kb/glossary/occupied-bandwidth",
    "https://ib-lenhardt.com/kb/glossary/ofdm",
    "https://ib-lenhardt.com/kb/glossary/ofdma",
    "https://ib-lenhardt.com/kb/glossary/ohm-s-law",
    "https://ib-lenhardt.com/kb/glossary/phase-modulation",
    "https://ib-lenhardt.com/kb/glossary/psk",
    "https://ib-lenhardt.com/kb/glossary/placing-on-the-market",
    "https://ib-lenhardt.com/kb/glossary/power-density",
    "https://ib-lenhardt.com/kb/glossary/qam",
    "https://ib-lenhardt.com/kb/glossary/arib-std-31",
    "https://ib-lenhardt.com/kb/glossary/radar-classes",
    "https://ib-lenhardt.com/kb/glossary/radar-sensor-calibration",
    "https://ib-lenhardt.com/kb/glossary/radiated-emissions",
    "https://ib-lenhardt.com/kb/glossary/radiated-measurements",
    "https://ib-lenhardt.com/kb/glossary/resistance",
    "https://ib-lenhardt.com/kb/glossary/responsible-person-eu",
    "https://ib-lenhardt.com/kb/glossary/return-loss",
    "https://ib-lenhardt.com/kb/glossary/rf-connector-finder",
    "https://ib-lenhardt.com/kb/glossary/rf-standards",
    "https://ib-lenhardt.com/kb/glossary/risk-assessment",
    "https://ib-lenhardt.com/kb/glossary/sar",
    "https://ib-lenhardt.com/kb/glossary/sdoc",
    "https://ib-lenhardt.com/kb/glossary/signal-modulation",
    "https://ib-lenhardt.com/kb/glossary/snr",
    "https://ib-lenhardt.com/kb/glossary/si-unit",
    "https://ib-lenhardt.com/kb/glossary/spurious-emission",
    "https://ib-lenhardt.com/kb/glossary/technical-documentation",
    "https://ib-lenhardt.com/kb/glossary/tcb",
    "https://ib-lenhardt.com/kb/glossary/tesla",
    "https://ib-lenhardt.com/kb/glossary/thermal-load",
    "https://ib-lenhardt.com/kb/glossary/tpc",
    "https://ib-lenhardt.com/kb/glossary/type-examination",
    "https://ib-lenhardt.com/kb/glossary/unii-bands",
    "https://ib-lenhardt.com/kb/glossary/vcci-mark",
    "https://ib-lenhardt.com/kb/glossary/vlp",
    "https://ib-lenhardt.com/kb/glossary/voltage",
    "https://ib-lenhardt.com/kb/glossary/vswr",
    "https://ib-lenhardt.com/kb/glossary/watt",
    "https://ib-lenhardt.com/kb/glossary/wavelength",
    "https://ib-lenhardt.com/kb/glossary/channel-allocation",
    "https://ib-lenhardt.com/kb/glossary/wireless-power-profiles",
    "https://ib-lenhardt.com/kb/glossary/wrc",
    "https://ib-lenhardt.com/kb/glossary/y-factor-method"
]

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def determine_category_and_region(title: str, text_content: str) -> tuple[str, str]:
    title_lower = title.lower()
    text_lower = text_content.lower()
    
    # Defaults
    category = "General"
    region = None

    # Region Logic
    if "fcc" in title_lower or "47 cfr" in title_lower or "usa" in text_lower:
        region = "USA"
        category = "Regulatory"
    elif "etsi" in title_lower or "en 300" in title_lower or "europe" in text_lower or "eu " in title_lower:
        region = "EU"
        category = "Regulatory"
    elif "arib" in title_lower or "japan" in text_lower or "mic" in text_lower:
        region = "Japan"
        category = "Regulatory"
    elif "anatel" in title_lower or "brazil" in text_lower:
        region = "Brazil"
        category = "Regulatory"
    elif "ised" in title_lower or "canada" in text_lower or "rss" in title_lower:
        region = "Canada"
        category = "Regulatory"
    
    # Category Logic (Override if specific)
    if "emc" in title_lower or "emission" in title_lower or "immunity" in title_lower:
        category = "EMC"
    elif "radio" in title_lower or "wireless" in title_lower or "bluetooth" in title_lower or "wi-fi" in title_lower:
        category = "Radio"
    elif "safety" in title_lower or "sar" in title_lower:
        category = "Safety"
        
    return category, region

def parse_page(url: str) -> Optional[Dict[str, Any]]:
    try:
        logger.info(f"Scraping: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Title
        title_elem = soup.find('h1')
        if not title_elem:
            logger.warning(f"No h1 found for {url}")
            return None
        title = clean_text(title_elem.get_text())
        
        # 2. Key Metadata (Slug ID)
        slug_id = url.split('/')[-1]
        
        # 3. Main Content Container
        # IB-Lenhardt structure usually has content in a specific div. 
        # Inspecting previous chunks suggests standards markdown structure under headers.
        # We will look for the main article body. Often 'article' or specific class.
        # A generic approach: find all headers (h2) and split content between them.
        
        # Fallback to finding the first h2 (usually "Definition" or similar) and going from there?
        # Or just getting all siblings after h1.
        
        content_container = soup.find('article') or soup.find('div', class_='entry-content') or title_elem.parent
        
        if not content_container:
             logger.warning(f"No content container found for {url}")
             return None

        # 4. Extract Summary (First paragraph after H1)
        summary = ""
        current_elem = title_elem.find_next_sibling()
        while current_elem:
            if current_elem.name == 'p':
                summary = clean_text(current_elem.get_text())
                if len(summary) > 20: # Valid paragraph
                    break
            current_elem = current_elem.find_next_sibling()
            
        if not summary:
            summary = "No summary available."
            
        # 5. Extract Sections
        sections = []
        
        # Find all H2s
        h2s = content_container.find_all('h2')
        
        if not h2s:
            # Maybe just one section?
            # Collect all paragraphs
            content_paras = []
            for p in content_container.find_all('p'):
                txt = clean_text(p.get_text())
                if txt and txt != summary:
                    content_paras.append(txt)
            
            if content_paras:
                sections.append({
                    "title": "Overview",
                    "content": content_paras
                })
        else:
            for h2 in h2s:
                section_title = clean_text(h2.get_text())
                section_content = []
                section_list_items = []
                section_images = []
                
                # Iterate siblings until next H2
                curr = h2.find_next_sibling()
                while curr and curr.name != 'h2':
                    if curr.name == 'p':
                        txt = clean_text(curr.get_text())
                        if txt:
                            section_content.append(txt)
                    elif curr.name == 'ul' or curr.name == 'ol':
                        for li in curr.find_all('li'):
                            txt = clean_text(li.get_text())
                            if txt:
                                section_list_items.append(txt)
                    elif curr.name == 'img':
                        src = curr.get('src')
                        if src:
                            if src.startswith('/'):
                                src = f"https://ib-lenhardt.com{src}"
                            section_images.append(src)
                    elif curr.name == 'figure':
                        img = curr.find('img')
                        if img:
                            src = img.get('src')
                            if src:
                                if src.startswith('/'):
                                    src = f"https://ib-lenhardt.com{src}"
                                section_images.append(src)
                                
                    curr = curr.find_next_sibling()
                
                sections.append({
                    "title": section_title,
                    "content": section_content,
                    "listItems": section_list_items if section_list_items else None,
                    "images": section_images if section_images else None
                })
                
        # 6. Determine Category/Region
        category, region = determine_category_and_region(title, str(sections) + summary)
        
        return {
            "id": slug_id,
            "term": title,
            "category": category,
            "region": region,
            "summary": summary,
            "sections": sections
        }

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None

def seed_db(terms: List[Dict[str, Any]]):
    db: Session = SessionLocal()
    try:
        count = 0
        for term_data in terms:
            # Check if exists
            existing = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_data["id"]).first()
            if existing:
                logger.info(f"Updating {term_data['term']}")
                existing.term = term_data["term"]
                existing.category = term_data["category"]
                existing.region = term_data["region"]
                existing.summary = term_data["summary"]
                existing.sections = term_data["sections"]
            else:
                logger.info(f"Creating {term_data['term']}")
                new_term = GlossaryTerm(**term_data)
                db.add(new_term)
            
            count += 1
            
        db.commit()
        logger.info(f"Successfully processed {count} terms.")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Bulk Import...")
    scraped_terms = []
    
    for url in URLS:
        data = parse_page(url)
        if data:
            scraped_terms.append(data)
            
    if scraped_terms:
        logger.info(f"Scraped {len(scraped_terms)} terms. Seeding DB...")
        seed_db(scraped_terms)
        logger.info("Import Complete!")
    else:
        logger.warning("No terms scraped.")
