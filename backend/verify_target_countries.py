
import requests
import sys

# Set output encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/v1"

def verify():
    print("--- Verifying Target Countries Feature ---")
    
    # 1. Get Tenant
    tenants = requests.get(f"{BASE_URL}/tenants").json()
    if not tenants:
        print("No tenants found.")
        return
    tenant_id = tenants[0]['id']
    print(f"Tenant: {tenants[0]['name']}")
    
    # 2. Get Techs (need valid IDs)
    techs = requests.get(f"{BASE_URL}/global/technologies").json()
    if not techs:
        print("No technologies found.")
        return
    wifi_id = next((t['id'] for t in techs if "Wi-Fi" in t['name']), techs[0]['id'])

    # 3. Create Device with Specific Countries
    print("\n[TEST] Creating Device with Specific Countries (USA, DEU)...")
    payload_specific = {
        "model_name": "Test Device Specific",
        "technology_ids": [wifi_id],
        "target_countries": ["USA", "DEU"]
    }
    resp1 = requests.post(f"{BASE_URL}/devices/?tenant_id={tenant_id}", json=payload_specific)
    if resp1.status_code == 201:
        data = resp1.json()
        print(f"Success! ID: {data['id']}")
        print(f"Target Countries: {data.get('target_countries')}")
        if "USA" in data.get('target_countries', []) and "DEU" in data['target_countries']:
            print("PASS: Specific countries saved correctly.")
        else:
            print("FAIL: Countries mismatch.")
    else:
        print(f"FAIL: {resp1.status_code} - {resp1.text}")

    # 4. Create Device with Global (Default)
    print("\n[TEST] Creating Device with Global (ALL)...")
    payload_global = {
        "model_name": "Test Device Global",
        "technology_ids": [wifi_id],
        # target_countries defaults to ["ALL"] in schema, so we can omit or send explicitly
        "target_countries": ["ALL"]
    }
    resp2 = requests.post(f"{BASE_URL}/devices/?tenant_id={tenant_id}", json=payload_global)
    if resp2.status_code == 201:
        data = resp2.json()
        print(f"Success! ID: {data['id']}")
        print(f"Target Countries: {data.get('target_countries')}")
        if data.get('target_countries') == ["ALL"]:
            print("PASS: Global default saved correctly.")
        else:
            print("FAIL: Global mismatch.")
    else:
        print(f"FAIL: {resp2.status_code} - {resp2.text}")

if __name__ == "__main__":
    verify()
