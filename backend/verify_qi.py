
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
    
    print("\n--- Rules for Qi / USA ---")
    found = 0
    for r in matrix:
        t_name = tech_map.get(r['technology_id'])
        c_iso = country_map.get(r['country_id'])
        cert_name = cert_map.get(r['certification_id'])
        
        if c_iso == "USA" and ("Qi" in t_name or "Charging" in t_name):
            print(f"Rule ID: {r['id']} | Tech: {t_name} | Cert: {cert_name}")
            found += 1
            
    print(f"Total found: {found}")

verify()
