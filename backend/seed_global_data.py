"""
Global Seeding Script (Comprehensive)
=====================================
Populates the database with 25+ Major Countries, Granular Technologies, Certifications, and Regulatory Rules.

Usage:
    python seed_global_data.py
"""

import requests
import sys

# API Configuration
BASE_URL = "http://192.168.80.28:8000/api/v1"
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Helpers
def log_success(msg): print(f"{GREEN}✓ {msg}{RESET}")
def log_error(msg): print(f"{RED}✗ {msg}{RESET}")
def log_info(msg): print(f"{BLUE}ℹ {msg}{RESET}")

# ============================================
# 1. Technologies (Granular Versions)
# ============================================
TECHNOLOGIES = [
    # Wi-Fi
    {"name": "Wi-Fi 4 (802.11n)", "description": "2.4/5GHz High Throughput"},
    {"name": "Wi-Fi 5 (802.11ac)", "description": "5GHz Very High Throughput"},
    {"name": "Wi-Fi 6 (802.11ax)", "description": "2.4/5GHz High Efficiency"},
    {"name": "Wi-Fi 6E (802.11ax 6GHz)", "description": "6GHz Spectrum Extension"},
    {"name": "Wi-Fi 7 (802.11be)", "description": "Extremely High Throughput (320MHz channels)"},
    
    # Bluetooth
    {"name": "Bluetooth 4.0", "description": "Classic + LE (Smart)"},
    {"name": "Bluetooth 4.2", "description": "IoT enhancements"},
    {"name": "Bluetooth 5.0", "description": "2x Speed, 4x Range"},
    {"name": "Bluetooth 5.1", "description": "Direction Finding (AoA/AoD)"},
    {"name": "Bluetooth 5.2", "description": "LE Audio (Isochronous Channels)"},
    {"name": "Bluetooth 5.3", "description": "Connection Subrating"},

    # Cellular
    {"name": "2G/3G GSM", "description": "Legacy Voice/Data"},
    {"name": "4G LTE", "description": "Long Term Evolution"},
    {"name": "5G Cellular", "description": "5G mobile network technology"},
    {"name": "5G NR Sub-6GHz", "description": "FR1 Bands"},
    {"name": "5G NR mmWave", "description": "FR2 Bands (>24GHz)"},
    {"name": "NB-IoT", "description": "Narrowband IoT (LTE Cat-NB1/NB2)"},

    # LPWAN / Other
    {"name": "LoRaWAN", "description": "Long Range Wide Area Network"},
    {"name": "Sigfox", "description": "Ultra Narrowband"},
    {"name": "NFC", "description": "13.56 MHz Near Field Communication"},
    {"name": "GPS/GNSS", "description": "L1/L5 Band Satellite Navigation"},
    {"name": "Wireless Charging (Qi)", "description": "WPC Qi Standard"},
    
    # Broadcast Receivers
    {"name": "AM Receiver", "description": "Amplitude Modulation Radio Receiver"},
    {"name": "FM Receiver", "description": "Frequency Modulation Radio Receiver"},
    
    # Legacy generic names (kept for backward compatibility if needed, or we can treat them as aliases)
    # For now, we rely on the specific ones above for new mappings.
]

# ============================================
# 2. Countries (28 Major Markets)
# ============================================
COUNTRIES = [
    # North America
    {"name": "United States", "iso_code": "USA"},
    {"name": "Canada", "iso_code": "CAN"},
    {"name": "Mexico", "iso_code": "MEX"},
    # South America
    {"name": "Brazil", "iso_code": "BRA"},
    {"name": "Argentina", "iso_code": "ARG"},
    {"name": "Chile", "iso_code": "CHL"},
    # Europe
    {"name": "United Kingdom", "iso_code": "GBR"},
    {"name": "Germany", "iso_code": "DEU"},
    {"name": "France", "iso_code": "FRA"},
    {"name": "Italy", "iso_code": "ITA"},
    {"name": "Spain", "iso_code": "ESP"},
    {"name": "Netherlands", "iso_code": "NLD"},
    {"name": "Sweden", "iso_code": "SWE"},
    {"name": "Switzerland", "iso_code": "CHE"},
    {"name": "Russia", "iso_code": "RUS"},
    {"name": "Turkey", "iso_code": "TUR"},
    # APAC
    {"name": "China", "iso_code": "CHN"},
    {"name": "Japan", "iso_code": "JPN"},
    {"name": "South Korea", "iso_code": "KOR"},
    {"name": "India", "iso_code": "IND"},
    {"name": "Australia", "iso_code": "AUS"},
    {"name": "Singapore", "iso_code": "SGP"},
    {"name": "Taiwan", "iso_code": "TWN"},
    {"name": "Indonesia", "iso_code": "IDN"},
    {"name": "Vietnam", "iso_code": "VNM"},
    {"name": "Thailand", "iso_code": "THA"},
    {"name": "Malaysia", "iso_code": "MYS"},
    # MEA
    {"name": "South Africa", "iso_code": "ZAF"},
    {"name": "United Arab Emirates", "iso_code": "ARE"},
    {"name": "Saudi Arabia", "iso_code": "SAU"},
]

# ============================================
# 3. Certifications (Global Map)
# ============================================
CERTIFICATIONS = [
    # Americas
    {"name": "FCC", "authority_name": "Federal Communications Commission (USA)"},
    {
        "name": "FCC Part 15", 
        "authority_name": "Federal Communications Commission (USA)", 
        "description": "Radio Frequency Devices (Intentional & Unintentional Radiators)",
        "branding_image_url": "https://www.fcc.gov/sites/default/files/fcc-logo-black-2020.svg",
        "labeling_requirements": "**FCC Part 15 Labeling:**\n1. **Placement**: FCC ID visible on exterior.\n2. **Statement**: 'This device complies with Part 15...'.\n3. **Intentional**: Subpart C (WiFi/BT). **Unintentional**: Subpart B."
    },
    {
        "name": "FCC Part 18", 
        "authority_name": "Federal Communications Commission (USA)", 
        "description": "Industrial, Scientific, and Medical equipment",
        "branding_image_url": "https://www.fcc.gov/sites/default/files/fcc-logo-black-2020.svg",
        "labeling_requirements": "**FCC Labeling Requirements:**\n1. **Placement**: The FCC ID must be visible on the exterior of the product.\n2. **Text**: Must include \"This device complies with Part 15 of the FCC Rules...\"\n3. **E-Labeling**: Permitted for devices with integral screens."
    },
    {"name": "ISED", "authority_name": "Innovation, Science and Economic Development (Canada)"},
    {"name": "NOM/IFETEL", "authority_name": "IFETEL (Mexico)"},
    {"name": "ANATEL", "authority_name": "Agência Nacional de Telecomunicações (Brazil)"},
    {"name": "ENACOM", "authority_name": "ENACOM (Argentina)"},
    {"name": "SUBTEL", "authority_name": "SUBTEL (Chile)"},
    # Europe
    {
        "name": "CE", 
        "authority_name": "European Commission (EU)",
        "description": "Conformité Européenne marking",
        "branding_image_url": "http://images.seeklogo.com/logo-png/0/1/ce-marking-logo-png_seeklogo-99.png",
        "labeling_requirements": "**CE Marking Requirements:**\n1. **Size**: The CE mark must be at least 5mm vertically.\n2. **Visibility**: Must be visible, legible, and indelible.\n3. **Packaging**: If impossible on product, must be on packaging and documents."
    },
    {"name": "UKCA", "authority_name": "UK Conformity Assessed"},
    {"name": "EAC", "authority_name": "Eurasian Economic Union (Russia)"},
    # APAC
    {"name": "SRRC", "authority_name": "Ministry of Industry and Information Technology (China)"},
    {"name": "CCC", "authority_name": "CNCA (China)"},
    {"name": "NAL", "authority_name": "Ministry of Industry and Information Technology (China)"},
    {"name": "TELEC", "authority_name": "MIC (Japan)"},
    {"name": "VCCI", "authority_name": "VCCI Council (Japan)"},
    {"name": "KC", "authority_name": "RRA (South Korea)"},
    {
        "name": "WPC", 
        "authority_name": "Ministry of Communications (India)",
        "description": "Wireless Planning and Coordination",
        "branding_image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6s8v4_Qj0h8w3_q_5a7_0_1_2_3_4_5",
        "labeling_requirements": "**WPC ETA Labeling:**\n1. **ETA Number**: Must display \"ETA-SD-YYYY/MMXX\" issued by WPC.\n2. **Placement**: On product label or manual."
    },
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
    # MEA
    {"name": "ICASA", "authority_name": "Independent Communications Authority (South Africa)"},
    {"name": "TDRA", "authority_name": "TDRA (UAE)"},
    {"name": "CITC", "authority_name": "CITC (Saudi Arabia)"},
]

# ============================================
# 4. Country Details (Knowledge Base)
# ============================================
COUNTRY_DETAILS = {
    "USA": {
        "voltage": "120V",
        "frequency": "60Hz",
        "plug_types": ["A", "B"],
        "label_requirements": "FCC ID must be visible on the exterior. If too small, can be in manual."
    },
    "CAN": {
        "voltage": "120V",
        "frequency": "60Hz",
        "plug_types": ["A", "B"],
        "label_requirements": "ISED/IC ID required. Bilingual (English/French) statement recommended."
    },
    "GBR": {
        "voltage": "230V",
        "frequency": "50Hz",
        "plug_types": ["G"],
        "label_requirements": "UKCA Work required. CE mark accepted until end of transition period."
    },
    "DEU": {
        "voltage": "230V",
        "frequency": "50Hz",
        "plug_types": ["C", "F"],
        "label_requirements": "CE Mark required. EU Declaration of Conformity must be available."
    },
    "IND": {
        "voltage": "230V",
        "frequency": "50Hz",
        "plug_types": ["C", "D", "M"],
        "label_requirements": "WPC ETA Number or BIS Registration mark required."
    },
    "BRA": {
        "voltage": "127V/220V",
        "frequency": "60Hz",
        "plug_types": ["N"],
        "label_requirements": "ANATEL Logo + Homologation Number."
    },
    "CHN": {
        "voltage": "220V",
        "frequency": "50Hz",
        "plug_types": ["A", "C", "I"],
        "label_requirements": "CMIIT ID (SRRC) must be displayed."
    },
    "JPN": {
        "voltage": "100V",
        "frequency": "50Hz/60Hz",
        "plug_types": ["A", "B"],
        "label_requirements": "Giteki Mark (Technical Conformity Mark) + Certification Number."
    },
    "FRA": {
        "voltage": "230V",
        "frequency": "50Hz",
        "plug_types": ["E", "C"],
        "regulatory_guide": "red",
        "label_requirements": "CE Mark required. Triman logo for recycling."
    },
    "ITA": {
        "voltage": "230V",
        "frequency": "50Hz",
        "plug_types": ["L", "C", "F"],
        "regulatory_guide": "red",
        "label_requirements": "CE Mark required."
    }
}

# ============================================
# 5. Regulatory Matrix Rules Generator
# ============================================

EU_COUNTRIES = ["DEU", "FRA", "ITA", "ESP", "NLD", "SWE"]

def get_cert_for_country(iso_code, tech_name):
    """Determine the certification based on country and technology."""
    
    # United States
    if iso_code == "USA":
        if "Wireless Charging" in tech_name or "Qi" in tech_name:
             return ["FCC Part 15", "FCC Part 18"]
        if "Wi-Fi" in tech_name or "Bluetooth" in tech_name or "Zigbee" in tech_name or "NFC" in tech_name:
            return "FCC Part 15"
        if "Receiver" in tech_name or "AM" in tech_name or "FM" in tech_name:
            # AM/FM Receivers are Unintentional Radiators
            return "FCC Part 15"
        if "Cellular" in tech_name or "LTE" in tech_name or "5G" in tech_name:
            return "FCC"
        if "Wireless Charging" in tech_name: return "FCC Part 18"
        return "FCC" # Default fallback
    
    # Canada
    if iso_code == "CAN":
        if "Receiver" in tech_name: return "ISED" # ICES-003 for unintentional
        return "ISED"
    
    # Mexico
    if iso_code == "MEX":
        return "NOM/IFETEL"

    # Chile
    if iso_code == "CHL":
        return "SUBTEL"

    # Argentina
    if iso_code == "ARG":
        return "ENACOM"

    # Brazil
    if iso_code == "BRA":
        return "ANATEL"

    # EU + Generic CE
    # EU + Generic CE
    if iso_code in EU_COUNTRIES:
        return "CE"
    if iso_code == "CHE": return "CE" # Technically compliant with harmonized, often accepted
    if iso_code == "TUR": return "CE" # Often follows RED
    if "Receiver" in tech_name and iso_code in ["CHE", "TUR", "NLD"]: return "CE" # Explicit for AM/FM

    # UK
    if iso_code == "GBR":
        return "UKCA"

    # Russia
    if iso_code == "RUS":
        return "EAC"

    # China
    if iso_code == "CHN":
        if "Cellular" in tech_name or "LTE" in tech_name or "5G" in tech_name: 
            return "NAL" # Network Access License for cellular
        if "Wi-Fi" in tech_name or "Bluetooth" in tech_name or "Zigbee" in tech_name:
            return "SRRC" # State Radio Regulation of China
        if "CCC" in tech_name: return "CCC" 
        if "Receiver" in tech_name: return "CCC" # Receivers need CCC (EMC/Safety) but usually exempt from SRRC
        return "SRRC" # Default for radio

    # Japan
    if iso_code == "JPN":
        if "Cellular" in tech_name:
            return "JATE" # Telecommunications Business Law (Network)
        # Note: Ideally devices need BOTH JATE & TELEC, but for matrix simplicity we pick primary radio
        if "Wi-Fi" in tech_name or "Bluetooth" in tech_name:
            return "TELEC" # Radio Law
        if "Receiver" in tech_name: return "TELEC" # Giteki (MIC) covers receivers
        return "TELEC" 

    # Korea
    if iso_code == "KOR":
        if "Receiver" in tech_name: return "KC"
        return "KC"

    # India
    if iso_code == "IND":
        if "Cellular" in tech_name: return "TEC" # Mandatory Testing (MTCTE)
        if "Bluetooth" in tech_name or "Wi-Fi" in tech_name: return "WPC"
        if "Receiver" in tech_name: return "WPC" # WPC ETA
        return "WPC"

    # Australia
    if iso_code == "AUS":
        return "RCM"

    # Rest of World / Fallback
    # South Africa
    if iso_code == "ZAF": return "ICASA"
    
    # Southeast Asia
    if iso_code == "SGP": return "IMDA"
    if iso_code == "MYS": return "MCMC"
    if iso_code == "THA": return "NBTC"
    if iso_code == "IDN": return "SDPPI"
    if iso_code == "VNM": return "MIC-VN"
    
    # Middle East
    if iso_code == "ARE": return "TDRA"
    if iso_code == "SAU": return "CITC"



    # Taiwan
    if iso_code == "TWN":
        if "Wi-Fi" in tech_name or "Bluetooth" in tech_name or "Cellular" in tech_name:
            return "NCC"
        if "Receiver" in tech_name: return "NCC"
        return "BSMI"

    # Australia / NZ
    if iso_code == "AUS" or iso_code == "NZL":
        return "RCM"
        
    # Argentina
    if iso_code == "ARG":
        return "ENACOM"

    # Chile
    if iso_code == "CHL":
        return "SUBTEL"

    # Southeast Asia
    if iso_code == "SGP": return "IMDA"
    if iso_code == "MYS": return "MCMC"
    if iso_code == "THA": return "NBTC"
    if iso_code == "VNM": return "MIC-VN"
    if iso_code == "IDN": return "SDPPI"
    
    # Middle East / Africa
    if iso_code == "ZAF": return "ICASA"
    if iso_code == "ARE": return "TDRA"
    if iso_code == "SAU": return "CITC"

    # Fallback for any other valid country in our list not explicitly handled above
    # We map them to "CE" or "FCC" based on region or just return None if we really don't know
    # But user wants "every technology should have a record".
    # Remaining from COUNTRIES list: None specific known missing, but let's be safe.
    
    # Fallback for others (receivers)
    if "Receiver" in tech_name: 
        # User requested to remove National Approval records. 
        # So if no specific mapping exists, we return None (skip).
        return None

    return None

# ============================================
# Main Logic
# ============================================

def get_or_create(endpoint, data, lookup_key):
    try:
        resp = requests.post(f"{BASE_URL}/{endpoint}", json=data)
        if resp.status_code == 201:
            log_success(f"Created {data.get(lookup_key)}")
            return resp.json()['id']
        elif resp.status_code == 409:
            # Slow but safe: fetch all and find ID
            all_items = requests.get(f"{BASE_URL}/{endpoint}").json()
            for item in all_items:
                if item[lookup_key] == data[lookup_key]:
                    return item['id']
    except Exception as e:
        log_error(f"Failed {data.get(lookup_key)}: {e}")
    return None

def seed():
    # 1. Technologies
    print("\n--- Technologies ---")
    tech_map = {}
    for t in TECHNOLOGIES:
        tid = get_or_create("global/technologies", t, "name")
        if tid: tech_map[t["name"]] = tid

    # 2. Countries
    print("\n--- Countries ---")
    country_map = {}
    for c in COUNTRIES:
        # Merge details if available
        if c["iso_code"] in COUNTRY_DETAILS:
            c["details"] = COUNTRY_DETAILS[c["iso_code"]]
            
        cid = get_or_create("global/countries", c, "iso_code")
        if cid: \
            country_map[c["iso_code"]] = cid
        
        # Force update details if we have them (even if country existed)
        if cid and "details" in c:
            try:
                requests.put(f"{BASE_URL}/global/countries/{cid}", json={"details": c["details"]})
                # print("u", end="", flush=True) # updated
            except:
                pass

    # 3. Certifications
    print("\n--- Certifications ---")
    cert_map = {}
    for cert in CERTIFICATIONS:
        cid = get_or_create("global/certifications", cert, "name")
        if cid: cert_map[cert["name"]] = cid

    # 4. Glossary
    print("\n--- Glossary ---")
    GLOSSARY_DATA = [
        {"id": "red", "term": "RED 2014/53/EU", "category": "Regulatory", "region": "EU", "summary": "Radio Equipment Directive regulating wireless devices in the EU.", "sections": [{"content": ["The Radio Equipment Directive (RED) establishes a regulatory framework for placing radio equipment on the European market."]}, {"title": "General Context (from Wikipedia)", "content": ["The Radio Equipment Directive (RED, EU directive 2014/53/EU) established a regulatory framework for placing radio equipment on the market in the EU...", "This directive was published on 16 April 2014..."], "images": []}]},
        {"id": "arib-std-t66", "term": "ARIB STD-T66", "category": "Regulatory", "region": "Japan", "summary": "The standard applies to low-power wireless systems using the 2.4 GHz band.", "sections": [{"title": "Scope and Application", "content": ["The standard applies to low-power wireless systems using the 2.4 GHz band..."], "listItems": ["Bluetooth and Bluetooth Low Energy...", "Wi-Fi (IEEE 802.11b/g/n)..."]}, {"title": "Frequency Range", "listItems": ["Operating Band: 2,400 – 2,483.5 MHz"]}, {"title": "Power Limits", "listItems": ["Maximum EIRP: 10 mW"]}]},
        {"id": "ce-mark", "term": "CE Mark", "category": "Regulatory", "region": "EU", "summary": "The presence of the CE marking on commercial products indicates that the manufacturer or importer affirms the goods' conformity with European health, safety, and environmental protection standards.", "sections": [{"title": "Definition and Purpose", "content": ["The CE mark serves as a manufacturer’s declaration..."], "listItems": ["Electrical and electronic devices", "Medical devices"]}, {"title": "Key Requirements", "listItems": ["Identify applicable EU legislation", "Perform a conformity assessment"]}]},
        {"id": "47-cfr-part-15", "term": "47 CFR Part 15", "category": "Regulatory", "region": "USA", "summary": "Code of Federal Regulations, Title 47, Part 15... regulates everything from spurious emissions to unlicensed low-power broadcasting.", "sections": [{"title": "Scope and Application", "listItems": ["Intentional radiators", "Unintentional radiators"]}, {"title": "Typical Compliance Process", "listItems": ["Testing", "Authorization", "Documentation"]}]},
        {"id": "accreditation", "term": "Accreditation", "category": "Regulatory", "region": None, "summary": "Accreditation is the independent, third-party evaluation of a conformity assessment body...", "sections": [{"title": "Scope and Application", "listItems": ["EMC testing", "Product safety evaluation"]}, {"title": "Key Technical Requirements", "listItems": ["ISO/IEC 17025", "ISO/IEC 17065"]}]},
        {"id": "afc", "term": "Automated Frequency Coordination (AFC)", "category": "Regulatory", "region": "USA", "summary": "AFC is a channel allocation scheme specified for wireless LANs...", "sections": [{"title": "Scope and Application", "listItems": ["Wi-Fi 6E and Wi-Fi 7 standard-power access points"]}, {"title": "How AFC Works", "listItems": ["Location-based query", "Frequency assignment"]}]},
        {"id": "ampere", "term": "Ampere (A)", "category": "General", "region": None, "summary": "The ampere is the unit of electric current in the International System of Units (SI).", "sections": [{"title": "Mathematical Definition", "content": ["I = V / R"], "listItems": ["I = Current", "V = Voltage"]}, {"title": "Measurement", "listItems": ["Smartphone charging 1-3 A", "Toaster 8 A"]}]},
        {"id": "amplitude-modulation", "term": "Amplitude Modulation (AM)", "category": "General", "region": None, "summary": "Amplitude modulation (AM) is a signal modulation technique used in electronic communication.", "sections": [{"title": "Mathematical Definition", "content": ["s(t) = A_c[1 + m(t)] cos(ω_c t)"], "listItems": ["A_c = Carrier amplitude", "m(t) = Modulating signal"]}, {"title": "Types", "listItems": ["Double Sideband (DSB)", "Single Sideband (SSB)"]}]},
        {"id": "arib-std-t71", "term": "ARIB STD-T71", "category": "Regulatory", "region": "Japan", "summary": "ARIB STD-T71 defines the technical requirements for wireless LAN devices operating in the 5 GHz band in Japan.", "sections": [{"content": ["ARIB STD-T71 defines the technical requirements..."]}, {"title": "Scope and Application", "listItems": ["5 GHz Radio Access Systems", "Low-Power Data Communication Systems"]}, {"title": "Frequency Bands", "table": {"headers": ["Frequency Band", "Range (MHz)", "Restrictions"], "rows": [["W52", "5,150-5,250", "Indoor Only"], ["W53", "5,250-5,350", "Indoor Only* DFS"], ["W56", "5,470-5,725", "Indoor/Outdoor DFS"]]}}]},
        {"id": "arib-std-t75", "term": "ARIB STD-T75", "category": "Regulatory", "region": "Japan", "summary": "The standard applies to short-range vehicle communication systems.", "sections": [{"title": "Scope and Application", "listItems": ["On-Board Units (OBU)", "Roadside Units (RSU)"]}, {"title": "Frequency Range", "listItems": ["5.76–5.92 GHz"]}]},
        {"id": "awgn", "term": "AWGN (Additive White Gaussian Noise)", "category": "General", "region": None, "summary": "Additive white Gaussian noise (AWGN) is a basic noise model used in information theory.", "sections": [{"title": "Definition", "listItems": ["Additive", "White", "Gaussian"]}, {"title": "Probability Distribution", "content": ["p(x) = (1/√(2πσ²)) × e^(-(x–μ)² / (2σ²))"]}]},
        {"id": "antenna-directivity", "term": "Antenna Directivity (D)", "category": "General", "region": None, "summary": "Directivity is a parameter of an antenna which measures the degree to which the radiation emitted is concentrated in a single direction.", "sections": [{"title": "Definition", "content": ["D = U(θ, φ) / U₀"]}, {"title": "Practical Applications", "listItems": ["Satellite links", "Radar"]}]},
        {"id": "antenna-gain", "term": "Antenna Gain", "category": "General", "region": None, "summary": "Antenna gain combines directivity and radiation efficiency.", "sections": [{"title": "Formula", "content": ["G(dBi) = –AF + 20 × log₁₀(f) – 29.8"]}, {"title": "Examples", "listItems": ["Wi-Fi Router: 2-3 dBi", "Satellite Dish: >30 dBi"]}]},
        {"id": "antenna-polarization", "term": "Antenna Polarization", "category": "General", "region": None, "summary": "Polarization describes the trajectory of the electric field vector.", "sections": [{"title": "Types", "listItems": ["Linear (Vertical/Horizontal)", "Circular (RHCP/LHCP)"]}, {"title": "Importance", "listItems": ["Mobile systems (Vertical)", "TV (Horizontal)"]}]},
        {"id": "arib-std-t48", "term": "ARIB STD-T48", "category": "Regulatory", "region": "Japan", "summary": "Covers short-range, low-power radar used for basic detection tasks.", "sections": [{"title": "Frequency Range", "listItems": ["60.5 GHz", "76.5 GHz"]}, {"title": "Power Limits", "listItems": ["EIRP ≤ 10 mW"]}]},
        {"id": "bandwidth", "term": "Bandwidth", "category": "Regulatory", "region": None, "summary": "Bandwidth is the difference between the upper and lower frequencies in a continuous band of frequencies.", "sections": [{"title": "Definition", "listItems": ["Absolute Bandwidth", "Effective Bandwidth (-3dB)"]}, {"title": "Shannon's Theorem", "content": ["C = B × log₂(1 + SNR)"]}]},
        {"id": "arib-std-t91", "term": "ARIB STD-T91", "category": "Regulatory", "region": "Japan", "summary": "UWB systems regulations in Japan.", "sections": [{"title": "Scope", "listItems": ["Indoor positioning", "High-res imaging"]}, {"title": "Bands", "listItems": ["Low Band: 3.4-4.8 GHz", "High Band: 7.25-10.25 GHz"]}]},
        {"id": "arib-std-t104", "term": "ARIB STD-T104", "category": "Regulatory", "region": "Japan", "summary": "LTE-Advanced equipment in Japan.", "sections": [{"title": "Scope", "content": ["Public mobile communication networks operating under Japan Radio Law."]}, {"title": "Bands", "listItems": ["700 MHz", "800 MHz", "1.5 GHz", "2 GHz"]}]},
        {"id": "fspl", "term": "Free Space Path Loss (FSPL)", "category": "Regulatory", "region": None, "summary": "FSPL is the loss in signal strength of a signal traveling between two antennas in free space.", "sections": [{"title": "Formula", "content": ["FSPL (dB) = 20 log₁₀(d) + 20 log₁₀(f) + 32.45"]}, {"title": "Applications", "listItems": ["Link budget planning", "Coverage estimation"]}]},
        {"id": "wireless-power-profiles", "term": "Qi Wireless Power Profiles", "category": "Radio", "region": None, "summary": "Qi is an open standard for inductive charging.", "sections": [{"title": "Overview", "content": ["Browse wireless power profiles including Magnetic Power Profile (MPP)."]}, {"title": "General Context", "content": ["Qi allows compatible devices to receive power..."]}]},
        {"id": "arib-std-t107", "term": "ARIB STD-T107", "category": "Regulatory", "region": "Japan", "summary": "920 MHz Band RFID equipment.", "sections": [{"title": "Scope", "listItems": ["Logistics", "Inventory"]}, {"title": "Frequency", "listItems": ["916.7 – 923.5 MHz"]}]},
        {"id": "arib-std-t108", "term": "ARIB STD-T108", "category": "Regulatory", "region": "Japan", "summary": "920 MHz Band Telemeter/Telecontrol/Data Transmission.", "sections": [{"title": "Scope", "listItems": ["Smart meters", "LPWAN (Sigfox, LoRa)"]}, {"title": "Power Limits", "listItems": ["20 mW EIRP"]}]},
        {"id": "arib-std-t111", "term": "ARIB STD-T111", "category": "Regulatory", "region": "Japan", "summary": "79 GHz Band Millimeter Wave Radar.", "sections": [{"title": "Scope", "listItems": ["Automotive radar", "ADAS"]}, {"title": "Frequency", "listItems": ["77 - 81 GHz"]}]},
        {"id": "bit-error-rate", "term": "Bit Error Rate (BER)", "category": "General", "region": None, "summary": "BER is the number of bit errors per unit time.", "sections": [{"title": "Definition", "content": ["BER = Errors / Total Bits"]}, {"title": "Typical Values", "listItems": ["Wi-Fi: 10^-5", "Optical: 10^-12"]}]},
        {"id": "bluetooth-classic-br-edr", "term": "Bluetooth Classic (BR/EDR)", "category": "Radio", "region": None, "summary": "Bluetooth Classic operates in the 2.4 GHz ISM band.", "sections": [{"title": "Modulation", "listItems": ["GFSK (BR)", "DQPSK/8DPSK (EDR)"]}, {"title": "Applications", "listItems": ["Audio streaming (A2DP)", "File transfer"]}]},
        {"id": "bluetooth-le-audio", "term": "Bluetooth LE Audio", "category": "Radio", "region": None, "summary": "Next-generation audio over Bluetooth Low Energy.", "sections": [{"title": "Features", "listItems": ["LC3 Codec", "Auracast", "Multi-stream"]}, {"title": "Difference from Classic", "listItems": ["Uses BLE radio", "Isochronous channels"]}]},
        {"id": "fcc-15-407", "term": "FCC §15.407", "category": "Regulatory", "region": "USA", "summary": "U-NII 5 GHz / 6 GHz Wi-Fi regulations.", "sections": [{"title": "Scope", "listItems": ["U-NII-1 to U-NII-8"]}, {"title": "Compliance", "listItems": ["DFS (Radar detection)", "Power limits"]}]},
        {"id": "wrc", "term": "World Radiocommunication Conference (WRC)", "category": "Radio", "region": None, "summary": "WRC organizes ITU Radio Regulations revisions every 3-4 years.", "sections": [{"title": "Purpose", "listItems": ["Allocate frequency bands", "Harmonize standards"]}, {"title": "Recent WRCs", "listItems": ["WRC-19 (5G mmWave)", "WRC-23"]}]},
        {"id": "y-factor", "term": "Y-Factor Method", "category": "Regulatory", "region": None, "summary": "Technique for measuring gain and noise temperature of amplifiers.", "sections": [{"title": "Formula", "content": ["Y = P_hot / P_cold", "NF = ENR - 10 log(Y-1)"]}]},
        {"id": "anatel", "term": "ANATEL Requirements", "category": "Regulatory", "region": "Brazil", "summary": "Certification requirements for telecom products in Brazil.", "sections": [{"title": "Categories", "listItems": ["Category I (Cell phones)", "Category II (Wi-Fi/BT)"]}]}
    ]

    for term in GLOSSARY_DATA:
        # Check if exists
        exists = False
        try:
            r = requests.get(f"{BASE_URL}/global/glossary/{term['id']}")
            if r.status_code == 200:
                exists = True
        except:
            pass
        
        if not exists:
            try:
                # API expects 'id' in the body for creation since we defined GlossaryTermCreate with 'id'
                resp = requests.post(f"{BASE_URL}/global/glossary", json=term)
                if resp.status_code == 201:
                    print(".", end="", flush=True)
                else:
                    print(f"Failed to seed {term['id']}: {resp.text}")
            except Exception as e:
                print(f"Error seeding {term['id']}: {e}")
        else:
            print("s", end="", flush=True) # skip if exists

    # 4. Regulatory Matrix
    print("\n--- Regulatory Matrix ---")
    count = 0
    updated_count = 0
    
    # 4a. Pre-fetch existing rules to handle deduplication
    print("Fetching existing matrix...", end="", flush=True)
    existing_rules_map = {} # (tid, cid) -> {id, cert_id}
    try:
        # Check if limit parameter is supported or fetch all pages if needed
        # Assuming simple get returns list 
        all_rules_resp = requests.get(f"{BASE_URL}/global/regulatory-matrix?limit=10000")
        if all_rules_resp.status_code == 200:
            for r in all_rules_resp.json():
                existing_rules_map[(r['technology_id'], r['country_id'], r['certification_id'])] = r
        print("Done.")
    except Exception as e:
        print(f"Error fetching existing rules: {e}")

    # Generate rules for ALL Techs x ALL Countries
    for tech in TECHNOLOGIES:
        tech_name = tech["name"]
        tid = tech_map.get(tech_name)
        
        for country in COUNTRIES:
            iso = country["iso_code"]
            cid = country_map.get(iso)
            
            # Smartly determine cert
            cert_names_or_name = get_cert_for_country(iso, tech_name)
            if not cert_names_or_name:
                continue # Skip if no known cert map
            
            # Normalize to list
            cert_names = cert_names_or_name if isinstance(cert_names_or_name, list) else [cert_names_or_name]

            for cert_name in cert_names:
                cert_id = cert_map.get(cert_name)
                
                if not all([tid, cid, cert_id]):
                    continue

                # Special Notes for 6GHz
                notes = f"Standard type approval for {tech_name}"
                if "6GHz" in tech_name or "Wi-Fi 6E" in tech_name or "Wi-Fi 7" in tech_name:
                    notes += ". Check for LPI (Low Power Indoor) restrictions."
                
                payload = {
                    "technology_id": tid,
                    "country_id": cid,
                    "certification_id": cert_id,
                    "is_mandatory": True,
                    "notes": notes
                }
                
                # Deduplication / Update Check
                existing = existing_rules_map.get((tid, cid, cert_id))
                
                if existing:
                     print("s", end="", flush=True) # Skip (Match)
                else:
                    # Create New
                    try:
                        resp = requests.post(f"{BASE_URL}/global/regulatory-matrix", json=payload)
                        if resp.status_code == 201:
                            count += 1
                            print(".", end="", flush=True)
                        elif resp.status_code == 409:
                            print("s", end="", flush=True)
                    except:
                        print("x", end="", flush=True)
                
    print(f"\n\nProcessed all rules. Added {count} new rules. Updated {updated_count} rules.")

if __name__ == "__main__":
    try:
        requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        seed()
    except Exception as e:
        log_error(f"Backend not running? {e}")
