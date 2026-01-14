
import requests
import wikipedia
import re
import sys
import time

# Configuration
BASE_URL = "http://192.168.80.28:8000/api/v1"
TARGET_WORD_COUNT = 450 # Aim slightly higher than user request to be safe

# Certifications List (Copied from seed_global_data.py to ensure full coverage)
CERTIFICATIONS = [
    {"name": "FCC", "authority_name": "Federal Communications Commission (USA)"},
    {"name": "FCC Part 15", "authority_name": "Federal Communications Commission (USA)"},
    {"name": "FCC Part 18", "authority_name": "Federal Communications Commission (USA)"},
    {"name": "ISED", "authority_name": "Innovation, Science and Economic Development (Canada)"},
    {"name": "NOM/IFETEL", "authority_name": "IFETEL (Mexico)"},
    {"name": "ANATEL", "authority_name": "Agência Nacional de Telecomunicações (Brazil)"},
    {"name": "ENACOM", "authority_name": "ENACOM (Argentina)"},
    {"name": "SUBTEL", "authority_name": "SUBTEL (Chile)"},
    {"name": "CE", "authority_name": "European Commission (EU)"},
    {"name": "UKCA", "authority_name": "UK Conformity Assessed"},
    {"name": "EAC", "authority_name": "Eurasian Economic Union (Russia)"},
    {"name": "SRRC", "authority_name": "Ministry of Industry and Information Technology (China)"},
    {"name": "CCC", "authority_name": "China Compulsory Certificate (China)"},
    {"name": "NAL", "authority_name": "Ministry of Industry and Information Technology (China)"},
    {"name": "TELEC", "authority_name": "MIC (Japan)"},
    {"name": "VCCI", "authority_name": "VCCI Council (Japan)"},
    {"name": "KC", "authority_name": "RRA (South Korea)"},
    {"name": "WPC", "authority_name": "Ministry of Communications (India)"},
    {"name": "BIS", "authority_name": "Bureau of Indian Standards (India)"},
    {"name": "TEC", "authority_name": "Telecommunication Engineering Centre (India)"},
    {"name": "RCM", "authority_name": "ACMA (Australia/NZ)"},
    {"name": "IMDA", "authority_name": "Info-communications Media Development Authority (Singapore)"},
    {"name": "NCC", "authority_name": "National Communications Commission (Taiwan)"},
    {"name": "BSMI", "authority_name": "Bureau of Standards, Metrology and Inspection (Taiwan)"},
    {"name": "SDPPI", "authority_name": "Kominfo (Indonesia)"},
    {"name": "MIC-VN", "authority_name": "Ministry of Information and Communications (Vietnam)"},
    {"name": "NBTC", "authority_name": "NBTC (Thailand)"},
    {"name": "MCMC", "authority_name": "MCMC (Malaysia)"},
    {"name": "ICASA", "authority_name": "Independent Communications Authority (South Africa)"},
    {"name": "TDRA", "authority_name": "TDRA (UAE)"},
    {"name": "CITC", "authority_name": "CITC (Saudi Arabia)"},
]

# Wiki Mapping
WIKI_MAP = {
    "FCC": "Federal Communications Commission",
    "FCC Part 15": "Title 47 CFR Part 15",
    "FCC Part 18": "Title 47 CFR Part 18",
    "ISED": "Innovation, Science and Economic Development Canada",
    "NOM/IFETEL": "Federal Telecommunications Institute", # IFETEL
    "ANATEL": "Agência Nacional de Telecomunicações",
    "ENACOM": "Ente Nacional de Comunicaciones",
    "SUBTEL": "Telecommunications in Chile", # Fallback
    "CE": "CE marking",
    "UKCA": "UKCA marking",
    "EAC": "Eurasian Conformity mark",
    "SRRC": "State Radio Regulation of China", # Might fallback
    "CCC": "China Compulsory Certificate",
    "NAL": "Telecommunications industry in China", # Fallback
    "TELEC": "Technical Conformity Mark",
    "VCCI": "VCCI Council",
    "KC": "KC mark",
    "WPC": "Wireless Planning and Coordination Wing",
    "BIS": "Bureau of Indian Standards",
    "TEC": "Telecommunication Engineering Centre (India)", # Check availability
    "RCM": "Regulatory Compliance Mark",
    "IMDA": "Info-communications Media Development Authority",
    "NCC": "National Communications Commission",
    "BSMI": "Bureau of Standards, Metrology and Inspection",
    "SDPPI": "Ministry of Communication and Informatics (Indonesia)",
    "MIC-VN": "Ministry of Information and Communications (Vietnam)",
    "NBTC": "National Broadcasting and Telecommunications Commission",
    "MCMC": "Malaysian Communications and Multimedia Commission",
    "ICASA": "Independent Communications Authority of South Africa",
    "TDRA": "Telecommunications and Digital Government Regulatory Authority",
    "CITC": "Communications and Information Technology Commission (Saudi Arabia)",
}

def slugify(text):
    return text.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "")

def count_words(text):
    if not text: return 0
    return len(text.split())

def get_wiki_content(query):
    try:
        print(f"  Searching Wikipedia for: {query}...", end="", flush=True)
        search_res = wikipedia.search(query)
        if not search_res:
            print(" No results.")
            return None, None, []
        
        # Try exact match or first result
        page = wikipedia.page(search_res[0], auto_suggest=False)
        print(f" Found: {page.title}")
        
        summary = page.summary
        content = page.content
        images = [img for img in page.images if img.lower().endswith(('.jpg', '.png'))][:2]
        
        return summary, content, images
    except Exception as e:
        print(f" Error: {e}")
        return None, None, []

def clean_text(text):
    # Basic cleaning
    paras = [p.strip() for p in text.split('\n') if len(p.strip()) > 20 and not p.startswith('=')]
    return paras

def process_cert(cert):
    name = cert["name"]
    slug = slugify(name)
    query = WIKI_MAP.get(name, name)
    
    print(f"\nProcessing {name} (ID: {slug})...")
    
    # Check existence
    exists = False
    current_word_count = 0
    existing_data = {}
    
    try:
        r = requests.get(f"{BASE_URL}/global/glossary/{slug}")
        if r.status_code == 200:
            exists = True
            existing_data = r.json()
            # Calculate word count logic here if needed, but for now we trust we want to expand/overwrite
            summary_wc = count_words(existing_data.get('summary', ''))
            sections_wc = sum(count_words(' '.join(s.get('content', []))) for s in existing_data.get('sections', []))
            current_word_count = summary_wc + sections_wc
            print(f"  Exists. Format: {current_word_count} words.")
    except:
        pass

    if exists and current_word_count > TARGET_WORD_COUNT:
        print("  Skipping (Already sufficient words).")
        return

    # Fetch Content
    wiki_summary, wiki_content, images = get_wiki_content(query)
    
    if not wiki_summary:
        print("  Wikipedia content not found. Using fallback.")
        wiki_summary = f"{name} is the regulatory certification for {cert['authority_name']}."
        wiki_content = "Details not currently available from automated sources."
        images = []

    # Build Content
    # Target length strategy
    final_summary = wiki_summary[:300] + "..." if len(wiki_summary) > 300 else wiki_summary
    
    # Sections construction
    cleaned_summary_paras = clean_text(wiki_summary)
    cleaned_content_paras = clean_text(wiki_content)
    
    target_paras = []
    current_wc = 0
    
    # Add summary paras first
    for p in cleaned_summary_paras:
        target_paras.append(p)
        current_wc += count_words(p)
        
    # Fill with content
    for p in cleaned_content_paras:
        if current_wc > TARGET_WORD_COUNT + 50:
            break
        if p not in target_paras: # Basic dedup
            target_paras.append(p)
            current_wc += count_words(p)
            
    sections = [
        {
            "title": "General Overview",
            "content": target_paras[:3], # First 3 paras
            "images": images[:1] if images else []
        },
        {
            "title": "Detailed Regulatory Context",
            "content": target_paras[3:], # Rest
            "images": images[1:2] if len(images) > 1 else []
        }
    ]
    
    # Payload
    payload = {
        "id": slug,
        "term": name,
        "category": "Regulatory",
        "region": None, # or derive from cert['authority_name'] if parsed, but 'None' is safer for now or we can map it
        "summary": final_summary,
        "sections": sections
    }
    
    # Determine Region string from authority_name roughly
    if "(USA)" in cert["authority_name"]: payload["region"] = "USA"
    elif "(Canada)" in cert["authority_name"]: payload["region"] = "Canada"
    elif "(EU)" in cert["authority_name"]: payload["region"] = "EU"
    elif "(China)" in cert["authority_name"]: payload["region"] = "China"
    elif "(Japan)" in cert["authority_name"]: payload["region"] = "Japan"
    elif "(India)" in cert["authority_name"]: payload["region"] = "India"
    elif "(Taiwan)" in cert["authority_name"]: payload["region"] = "Taiwan"
    elif "(Brazil)" in cert["authority_name"]: payload["region"] = "Brazil"
    elif "(Mexico)" in cert["authority_name"]: payload["region"] = "Mexico"
    elif "(Argentina)" in cert["authority_name"]: payload["region"] = "Argentina"
    elif "(Chile)" in cert["authority_name"]: payload["region"] = "Chile"
    elif "(South Korea)" in cert["authority_name"]: payload["region"] = "South Korea"
    elif "(Australia" in cert["authority_name"]: payload["region"] = "Australia"
    elif "(Singapore)" in cert["authority_name"]: payload["region"] = "Singapore"
    elif "(Indonesia)" in cert["authority_name"]: payload["region"] = "Indonesia"
    elif "(Vietnam)" in cert["authority_name"]: payload["region"] = "Vietnam"
    elif "(Thailand)" in cert["authority_name"]: payload["region"] = "Thailand"
    elif "(Malaysia)" in cert["authority_name"]: payload["region"] = "Malaysia"
    elif "(South Africa)" in cert["authority_name"]: payload["region"] = "South Africa"
    elif "(UAE)" in cert["authority_name"]: payload["region"] = "UAE"
    elif "(Saudi Arabia)" in cert["authority_name"]: payload["region"] = "Saudi Arabia"
    elif "(Russia)" in cert["authority_name"]: payload["region"] = "Russia"
    
    # Create or Update
    try:
        if exists:
            # Update (using PUT if available or just update logic)
            # Assuming PUT /global/glossary/{id} works or we just POST over it if the API supports upsert
            # checking code... seed_global_data uses POST and checks 409.
            # Let's try PUT if implemented, else delete and post?
            # Safest is usually update if supported.
            r_up = requests.put(f"{BASE_URL}/global/glossary/{slug}", json=payload)
            if r_up.status_code == 200:
                print("  Updated successfully.")
            else:
                print(f"  Update failed: {r_up.status_code}")
        else:
            r_cr = requests.post(f"{BASE_URL}/global/glossary", json=payload)
            if r_cr.status_code == 201:
                print("  Created successfully.")
            else:
                print(f"  Creation failed: {r_cr.status_code} {r_cr.text}")
    except Exception as e:
        print(f"  API Error: {e}")

def main():
    print("Starting Comprehensive Glossary Seeding...")
    for cert in CERTIFICATIONS:
        process_cert(cert)
        time.sleep(1) # Be nice to Wiki API
    print("\nDone.")

if __name__ == "__main__":
    main()
