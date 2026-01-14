
import requests

BASE_URL = "http://192.168.80.28:8000/api/v1"

def verify():
    print("Fetching matrix...")
    matrix = requests.get(f"{BASE_URL}/global/regulatory-matrix?limit=10000").json()
    
    # helper maps
    techs = requests.get(f"{BASE_URL}/global/technologies").json()
    tech_map = {t['id']: t['name'] for t in techs}
    
    countries = requests.get(f"{BASE_URL}/global/countries").json()
    country_map = {c['id']: c['iso_code'] for c in countries}
    
    certs = requests.get(f"{BASE_URL}/global/certifications").json()
    cert_map = {c['id']: c['name'] for c in certs}
    
    print("\n--- Checking for National Approval ---")
    found = 0
    # No specific target countries, check global
    for r in matrix:
        cert_name = cert_map.get(r['certification_id'])
        
        if cert_name == "National Approval":
            print(f"!!! FAIL: Found National Approval: {r['id']}")
            found += 1
            
    if found == 0:
        print("PASS: No National Approval records found.")
    else:
        print(f"FAIL: Found {found} records.")

verify()
