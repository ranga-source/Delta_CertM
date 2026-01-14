"""
Seed Data Script
================
This script populates the database with sample global data for testing.

Run this script after the first startup to create sample:
- Technologies
- Countries
- Certifications
- Regulatory Matrix rules

Usage:
    python seed_data.py
"""

import requests
import json
from typing import Dict, List

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message: str):
    """Print success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    """Print info message in blue."""
    print(f"{BLUE}ℹ {message}{RESET}")


# ============================================
# Sample Data
# ============================================

TECHNOLOGIES = [
    {"name": "Wi-Fi 6E", "description": "Wi-Fi operating in 6 GHz band"},
    {"name": "Bluetooth 5.3", "description": "Bluetooth Low Energy wireless technology"},
    {"name": "GPS/GNSS", "description": "Global Positioning System / Global Navigation Satellite System"},
    {"name": "5G Cellular", "description": "5G mobile network technology"},
    {"name": "NFC", "description": "Near Field Communication"},
    {"name": "Wireless Charging (Qi)", "description": "WPC Qi wireless charging standard"},
]

COUNTRIES = [
    {"name": "United States", "iso_code": "USA"},
    {"name": "India", "iso_code": "IND"},
    {"name": "Germany", "iso_code": "DEU"},
    {"name": "Japan", "iso_code": "JPN"},
    {"name": "China", "iso_code": "CHN"},
]

CERTIFICATIONS = [
    {"name": "FCC Part 15", "authority_name": "Federal Communications Commission", 
     "description": "Unintentional radiators"},
    {"name": "FCC Part 18", "authority_name": "Federal Communications Commission",
     "description": "Industrial, Scientific, and Medical equipment"},
    {"name": "WPC", "authority_name": "Ministry of Communications (India)",
     "description": "Wireless Planning and Coordination"},
    {"name": "BIS", "authority_name": "Bureau of Indian Standards",
     "description": "Indian Standards certification"},
    {"name": "CE", "authority_name": "European Commission",
     "description": "Conformité Européenne marking"},
    {"name": "TELEC", "authority_name": "Ministry of Internal Affairs and Communications (Japan)",
     "description": "Radio equipment certification"},
    {"name": "SRRC", "authority_name": "State Radio Regulation Committee (China)",
     "description": "Radio equipment approval"},
]

REGULATORY_RULES = [
    # USA Rules
    {"tech_name": "Wi-Fi 6E", "country_code": "USA", "cert_name": "FCC Part 15",
     "notes": "Required for Wi-Fi devices"},
    {"tech_name": "Bluetooth 5.3", "country_code": "USA", "cert_name": "FCC Part 15",
     "notes": "Required for Bluetooth devices"},
    {"tech_name": "5G Cellular", "country_code": "USA", "cert_name": "FCC Part 15",
     "notes": "Required for cellular devices"},
    
    # India Rules
    {"tech_name": "Wi-Fi 6E", "country_code": "IND", "cert_name": "WPC",
     "notes": "6 GHz band requires WPC approval"},
    {"tech_name": "Bluetooth 5.3", "country_code": "IND", "cert_name": "BIS",
     "notes": "Required for Bluetooth devices"},
    {"tech_name": "5G Cellular", "country_code": "IND", "cert_name": "WPC",
     "notes": "Required for cellular devices"},
    
    # Germany/EU Rules
    {"tech_name": "Wi-Fi 6E", "country_code": "DEU", "cert_name": "CE",
     "notes": "CE marking required for EU market"},
    {"tech_name": "Bluetooth 5.3", "country_code": "DEU", "cert_name": "CE",
     "notes": "CE marking required"},
    {"tech_name": "Wireless Charging (Qi)", "country_code": "DEU", "cert_name": "CE",
     "notes": "CE marking required for wireless charging"},
    
    # Japan Rules
    {"tech_name": "Wi-Fi 6E", "country_code": "JPN", "cert_name": "TELEC",
     "notes": "TELEC certification required"},
    {"tech_name": "Bluetooth 5.3", "country_code": "JPN", "cert_name": "TELEC",
     "notes": "TELEC certification required"},
    
    # China Rules
    {"tech_name": "Wi-Fi 6E", "country_code": "CHN", "cert_name": "SRRC",
     "notes": "SRRC approval required"},
    {"tech_name": "5G Cellular", "country_code": "CHN", "cert_name": "SRRC",
     "notes": "SRRC approval required"},
]


# ============================================
# Seed Functions
# ============================================

def seed_technologies() -> Dict[str, int]:
    """Seed technologies and return name-to-id mapping."""
    print_info("Seeding technologies...")
    tech_map = {}
    
    for tech in TECHNOLOGIES:
        try:
            response = requests.post(f"{BASE_URL}/global/technologies", json=tech)
            if response.status_code == 201:
                data = response.json()
                tech_map[tech["name"]] = data["id"]
                print_success(f"Created technology: {tech['name']} (ID: {data['id']})")
            elif response.status_code == 409:
                # Already exists, get ID
                response = requests.get(f"{BASE_URL}/global/technologies")
                for item in response.json():
                    if item["name"] == tech["name"]:
                        tech_map[tech["name"]] = item["id"]
                        print_info(f"Technology already exists: {tech['name']} (ID: {item['id']})")
                        break
            else:
                print_error(f"Failed to create {tech['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error creating {tech['name']}: {str(e)}")
    
    return tech_map


def seed_countries() -> Dict[str, int]:
    """Seed countries and return iso_code-to-id mapping."""
    print_info("Seeding countries...")
    country_map = {}
    
    for country in COUNTRIES:
        try:
            response = requests.post(f"{BASE_URL}/global/countries", json=country)
            if response.status_code == 201:
                data = response.json()
                country_map[country["iso_code"]] = data["id"]
                print_success(f"Created country: {country['name']} (ID: {data['id']})")
            elif response.status_code == 409:
                # Already exists, get ID
                response = requests.get(f"{BASE_URL}/global/countries")
                for item in response.json():
                    if item["iso_code"] == country["iso_code"]:
                        country_map[country["iso_code"]] = item["id"]
                        print_info(f"Country already exists: {country['name']} (ID: {item['id']})")
                        break
            else:
                print_error(f"Failed to create {country['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error creating {country['name']}: {str(e)}")
    
    return country_map


def seed_certifications() -> Dict[str, int]:
    """Seed certifications and return name-to-id mapping."""
    print_info("Seeding certifications...")
    cert_map = {}
    
    for cert in CERTIFICATIONS:
        try:
            response = requests.post(f"{BASE_URL}/global/certifications", json=cert)
            if response.status_code == 201:
                data = response.json()
                cert_map[cert["name"]] = data["id"]
                print_success(f"Created certification: {cert['name']} (ID: {data['id']})")
            elif response.status_code == 409:
                # Already exists, get ID
                response = requests.get(f"{BASE_URL}/global/certifications")
                for item in response.json():
                    if item["name"] == cert["name"]:
                        cert_map[cert["name"]] = item["id"]
                        print_info(f"Certification already exists: {cert['name']} (ID: {item['id']})")
                        break
            else:
                print_error(f"Failed to create {cert['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error creating {cert['name']}: {str(e)}")
    
    return cert_map


def seed_regulatory_rules(tech_map: Dict, country_map: Dict, cert_map: Dict):
    """Seed regulatory matrix rules."""
    print_info("Seeding regulatory rules...")
    
    for rule in REGULATORY_RULES:
        try:
            # Get IDs from mappings
            tech_id = tech_map.get(rule["tech_name"])
            country_id = country_map.get(rule["country_code"])
            cert_id = cert_map.get(rule["cert_name"])
            
            if not all([tech_id, country_id, cert_id]):
                print_error(f"Missing IDs for rule: {rule}")
                continue
            
            rule_data = {
                "technology_id": tech_id,
                "country_id": country_id,
                "certification_id": cert_id,
                "is_mandatory": True,
                "notes": rule["notes"]
            }
            
            response = requests.post(f"{BASE_URL}/global/regulatory-matrix", json=rule_data)
            if response.status_code == 201:
                print_success(f"Created rule: {rule['tech_name']} + {rule['country_code']} → {rule['cert_name']}")
            elif response.status_code == 409:
                print_info(f"Rule already exists: {rule['tech_name']} + {rule['country_code']} → {rule['cert_name']}")
            else:
                print_error(f"Failed to create rule: {response.text}")
        except Exception as e:
            print_error(f"Error creating rule: {str(e)}")


# ============================================
# Main
# ============================================

def main():
    """Main seed function."""
    print("\n" + "="*60)
    print("TAMSys Database Seeding")
    print("="*60 + "\n")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print_error("API is not responding. Please start the backend first.")
            return
    except Exception as e:
        print_error(f"Cannot connect to API: {str(e)}")
        print_info("Please make sure the backend is running: uvicorn app.main:app --reload")
        return
    
    # Seed data
    tech_map = seed_technologies()
    print()
    
    country_map = seed_countries()
    print()
    
    cert_map = seed_certifications()
    print()
    
    seed_regulatory_rules(tech_map, country_map, cert_map)
    print()
    
    print("="*60)
    print_success("Database seeding completed!")
    print("="*60)
    print(f"\nCreated:")
    print(f"  - {len(tech_map)} Technologies")
    print(f"  - {len(country_map)} Countries")
    print(f"  - {len(cert_map)} Certifications")
    print(f"  - {len(REGULATORY_RULES)} Regulatory Rules")
    print(f"\nNext steps:")
    print(f"  1. Visit Swagger UI: http://localhost:8000/docs")
    print(f"  2. Create a tenant: POST /api/v1/tenants")
    print(f"  3. Create a device: POST /api/v1/devices")
    print(f"  4. Run gap analysis: POST /api/v1/compliance/gap-analysis")
    print()


if __name__ == "__main__":
    main()


