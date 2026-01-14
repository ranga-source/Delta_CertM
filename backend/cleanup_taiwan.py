
import requests

BASE_URL = "http://192.168.80.28:8000/api/v1"

def cleanup():
    print("Fetching global lists...")
    # Get IDs
    countries = requests.get(f"{BASE_URL}/global/countries").json()
    twn_id = next((c['id'] for c in countries if c['iso_code'] == "TWN"), None)
    
    if not twn_id:
        print("Taiwan not found!")
        return

    print("Fetching matrix...")
    matrix = requests.get(f"{BASE_URL}/global/regulatory-matrix?limit=10000").json()
    
    # Helper Maps
    techs = requests.get(f"{BASE_URL}/global/technologies").json()
    tech_map = {t['id']: t['name'] for t in techs}
    
    certs = requests.get(f"{BASE_URL}/global/certifications").json()
    cert_map = {c['id']: c['name'] for c in certs}

    print("\n--- Deleting incorrect Taiwan Rules ---")
    deleted = 0
    for r in matrix:
        if r['country_id'] == twn_id:
            t_name = tech_map.get(r['technology_id'])
            cert_name = cert_map.get(r['certification_id'])
            
            if "Receiver" in t_name and cert_name != "NCC":
                print(f"Deleting: TWN | {t_name} | {cert_name} (ID: {r['id']})")
                requests.delete(f"{BASE_URL}/global/regulatory-matrix/{r['id']}")
                deleted += 1
                
    print(f"Total deleted: {deleted}")

cleanup()
