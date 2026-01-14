
import requests
import sys

# API Configuration
BASE_URL = "http://192.168.80.28:8000/api/v1"
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def log_success(msg): print(f"{GREEN}✓ {msg}{RESET}")
def log_error(msg): print(f"{RED}✗ {msg}{RESET}")

LABELS = [
    {
        "name": "Giteki Mark (MIC)",
        "authority": "MIC (Japan)",
        "description": "Technical Conformity Mark for radio equipment in Japan. Shows compliance with Radio Law.",
        "requirements": {
            "min_height": "3mm (diameter)",
            "content": "Must appear with the R symbol (Radio) and T symbol (Telecom) + Certification Number.",
            "placement": "Visible on product. If embedded module, host must say 'Contains MIC ID: ...'.",
            "proportions": "Strict geometry for the 'broken circle' icon."
        },
        "image_url": "https://tse2.mm.bing.net/th/id/OIP.bJrmTt_fw_hdJvxuzn3DDQHaHg?pid=Api&P=0&h=220",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Giteki_mark.svg",
        "country_name": "Japan"
    },
    {
        "name": "KC Mark",
        "authority": "KATS (South Korea)",
        "description": "Korea Certification mark. Unified certification mark for electrical/electronic products in South Korea.",
        "requirements": {
            "min_height": "5mm",
            "content": "Must include Certification Number (e.g. R-R-Abc-ModelName) below/near the mark.",
            "color": "Indigo (Pantone 286C) / Gold / Silver / Black on White.",
            "language": "Korean labeling often required for safety info."
        },
        "image_url": "https://sffanfactory.com/wp-content/uploads/2025/09/6d64748119b325b7cf28b5174cdbfbff.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/KC_Logo.svg",
        "country_name": "South Korea"
    },
    {
        "name": "CCC Mark",
        "authority": "CNCA (China)",
        "description": "China Compulsory Certification mark. Mandatory for products in 132 categories (including IT/AV/Telecom).",
        "requirements": {
            "min_height": "Variable (proportional)",
            "placement": "Must be applied by the manufacturer on the product.",
            "format": "Standard oval logo with 'CCC' inside plus category suffix (e.g. S, EMC, F) if applicable.",
            "permission": "Printing/molding permission required from CNCA."
        },
        "image_url": "https://www.pngkey.com/png/detail/188-1889021_the-china-compulsory-certificate-mark-commonly-known-ccc.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/d/d4/China_Compulsory_Certificate_mark.svg",
        "country_name": "China"
    },
    {
        "name": "UKCA Mark",
        "authority": "UK Government",
        "description": "The UK Conformity Assessed (UKCA) marking is a new UK product marking that is used for goods being placed on the market in Great Britain (England, Wales and Scotland).",
        "requirements": {
            "min_height": "5mm",
            "proportions": "Letters must be in proportion to the official version.",
            "placement": "On product, or packaging/manuals (transitional measure until 2027).",
            "visibility": "Must be permanently attached."
        },
        "image_url": "https://assets.publishing.service.gov.uk/media/5fedad56e90e0776a9208404/ukca-black-fill.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/2/22/UKCA_mark.svg",
        "country_name": "United Kingdom"
    },
    {
        "name": "RCM (Regulatory Compliance Mark)",
        "authority": "ACMA (Australia) / RSM (New Zealand)",
        "description": "Indicates a device's compliance with applicable ACMA regulatory arrangements (EMC, Radio, EME, Telecom). Replaces C-Tick and A-Tick.",
        "requirements": {
            "min_height": "3mm",
            "placement": "Surface of product (labeling/printing).",
            "content": "Does not require supplier ID (unlike C-Tick).",
            "color": "Contrast required."
        },
        "image_url": "https://www.appluslaboratories.com/laboratories/en/dam/jcr:d7e79370-a023-43b3-8067-0d518d238cd9/rcm%20australia%20mark.2020-06-09-17-44-49.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/2/23/RCM_Logo.svg",
        "country_name": "Australia"
    },
    {
        "name": "CE Mark",
        "authority": "European Union",
        "description": "Administrative marking that indicates conformity with health, safe, and environmental protection standards for products sold within the European Economic Area (EEA).",
        "requirements": {
            "min_height": "5mm",
            "proportions": "Must maintain specific grid proportions (two circles touching)",
            "placement": "Visible, legible, validation indelible on product or data plate.",
            "color": "Any color, provided visibility is maintained.",
            "region": "EU"
        },
        "image_url": "https://single-market-economy.ec.europa.eu/sites/default/files/styles/oe_theme_small_no_crop/public/2021-10/ce-mark_0.png?itok=WbyH8iLK",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/e/e5/CE_Logo.svg"
    },
    {
        "name": "FCC Label",
        "authority": "Federal Communications Commission (USA)",
        "description": "Certification mark for electronic products manufactured or sold in the United States. Indicates that the electromagnetic interference from the device is under limits approved by the FCC.",
        "requirements": {
            "min_height": "Variable (must be legible)",
            "clear_space": "None specified, but must be distinct",
            "content": "FCC ID must be visible on the product exterior. If product is too small (<8x10cm), ID can be in manual/packaging, but logo/statement rules apply.",
            "color": "Contrast required (e.g. black on white)",
            "e_label": "Permitted for devices with integral screen."
        },
        "image_url": "https://logodix.com/logo/846412.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/b/bc/FCC_New_Logo.svg",
        "country_name": "United States"
    },
    {
        "name": "WEEE Symbol",
        "authority": "European Union / Global",
        "description": "Waste Electrical and Electronic Equipment directive symbol. Indicates product should not be discarded in normal trash.",
        "requirements": {
            "min_height": "7mm (crossed out bin)",
            "feature": "Must include the 'black bar' or date code indicating post-2005 mfg.",
            "placement": "Visible, legible, indelible.",
            "region": "EU"
        },
        "image_url": "https://www.compliancegate.com/wp-content/uploads/2019/12/WEEE-mark.jpg",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/d/d1/WEEE_symbol_vectors.svg"
    },
    {
        "name": "ANATEL Mark",
        "authority": "ANATEL (Brazil)",
        "description": "Homologation seal for telecommunications products in Brazil.",
        "requirements": {
            "min_height": "4mm",
            "content": "Must include Anatel Logo + Homologation Number (HHHHH-YY-FFF).",
            "placement": "On product, manual, and packaging.",
            "text": "Statement 'This equipment is netitled to protection... secondary service' required for restricted radiation."
        },
        "image_url": "https://c-prav.com/wp-content/uploads/2024/10/website-images-august-2024-1.png",
        "vector_url": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Anatel_logo.svg",
        "country_name": "Brazil"
    },
    {
        "name": "BIS Mark",
        "authority": "Bureau of Indian Standards (India)",
        "description": "ISI mark or Standard Mark for product certification in India (CRS). Mandatory for electronics/IT goods.",
        "requirements": {
            "min_height": "6mm (variable)",
            "content": "Must include 'IS <Standard Number>' (Top) and 'R-<Registration Number>' (Bottom).",
            "placement": "Screen printing or molding on the product body.",
            "visibility": "Visible without disassembling."
        },
        "image_url": "https://e7.pngegg.com/pngimages/819/588/png-clipart-bureau-of-indian-standards-ministry-of-electronics-and-information-technology-technical-standard-brand-liaison-bis-registration-wpc-license-isi-mark-certification-consultants-india.png",
        "country_name": "India"
    }
]

def seed_labels():
    print("--- Seeding Certification Labels ---")
    for label in LABELS:
        try:
            # Check exist
            # We don't have a direct 'get by name' easily exposed via generic API lists without filtering, 
            # but we can try POST and handle 409 or just create.
            # Actually, let's just attempt POST. If it fails due to unique constraint, we update.
            
            # Since my create returns 409... wait, my API implementation for create usually raises 500 on integrity error unless I handle it.
            # Let's verify API behavior. Usually FastAPI/SQLAlchemy returns 500 unless caught.
            # I will assume "create or skip" logic.
            
            # Better: Get all and check.
            pass 
        except:
            pass
            
    # GET all labels first
    try:
        existing = requests.get(f"{BASE_URL}/global/labels").json()
        existing_names = {l['name']: l['id'] for l in existing}
    except Exception as e:
        log_error(f"Failed to fetch labels: {e}")
        return

    # Fetch countries to map IDs
    country_map = {}
    try:
        countries_resp = requests.get(f"{BASE_URL}/global/countries?limit=1000")
        if countries_resp.status_code == 200:
            for c in countries_resp.json():
                country_map[c['name']] = c['id']
    except Exception as e:
        log_error(f"Failed to fetch countries: {e}")

    count = 0
    updated_count = 0
    for label in LABELS:
        # Map country_id if country_name is present
        if 'country_name' in label:
            c_name = label.pop('country_name') # Remove from payload
            if c_name in country_map:
                label['country_id'] = country_map[c_name]
        
        if label['name'] in existing_names:
            # Update
            lid = existing_names[label['name']]
            try:
                # Update image_url even if exists
                resp = requests.put(f"{BASE_URL}/global/labels/{lid}", json=label)
                if resp.status_code == 200:
                    print("u", end="", flush=True)
                    updated_count += 1
                else:
                    print(f"Failed to update {label['name']}: {resp.status_code}")
            except Exception as e:
                log_error(f"Error updating {label['name']}: {e}")
        else:
            # Create
            try:
                resp = requests.post(f"{BASE_URL}/global/labels", json=label)
                if resp.status_code == 201:
                    print(".", end="", flush=True)
                    count += 1
                else:
                    print("x", end="", flush=True)
                    # print(resp.text)
            except Exception as e:
                log_error(f"Error: {e}")
                
    print(f"\nSeeding complete. Added {count} new, Updated {updated_count} existing labels.")

if __name__ == "__main__":
    seed_labels()
