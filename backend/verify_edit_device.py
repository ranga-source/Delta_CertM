
import requests
import sys
import json

# Set output encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/v1"

def verify_update():
    print("--- Verifying Device Update Feature ---")
    
    # 1. Get Tenant
    tenants = requests.get(f"{BASE_URL}/tenants").json()
    if not tenants:
        print("No tenants found.")
        return
    tenant_id = tenants[0]['id']
    
    # 2. Find a device to edit
    devices = requests.get(f"{BASE_URL}/devices/?tenant_id={tenant_id}").json()
    if not devices:
        print("No devices found.")
        return
    
    target_device = devices[0]
    did = target_device['id']
    print(f"Testing Update on: {target_device['model_name']} ({did})")
    
    # 3. Update to Specific Countries
    new_countries = ["JPN", "KOR"]
    print(f"\n[TEST] Updating to: {new_countries}")
    payload = {
        "target_countries": new_countries
    }
    resp = requests.put(f"{BASE_URL}/devices/{did}?tenant_id={tenant_id}", json=payload)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Response Target Countries: {data.get('target_countries')}")
        
        # Verify persistence
        print("Verifying persistence via GET...")
        get_resp = requests.get(f"{BASE_URL}/devices/{did}?tenant_id={tenant_id}")
        saved_data = get_resp.json()
        saved_countries = saved_data.get('target_countries')
        print(f"Saved Target Countries: {saved_countries}")
        
        if set(saved_countries) == set(new_countries):
             print("PASS: Update persisted correctly.")
        else:
             print("FAIL: Persistence mismatch.")
    else:
        print(f"FAIL: {resp.status_code} - {resp.text}")

    # 4. Revert to ALL
    print(f"\n[TEST] Reverting to: ['ALL']")
    payload_revert = {
        "target_countries": ["ALL"]
    }
    resp_revert = requests.put(f"{BASE_URL}/devices/{did}?tenant_id={tenant_id}", json=payload_revert)
    if resp_revert.status_code == 200:
         print("PASS: Reverted to ALL.")
    else:
         print(f"FAIL: Revert failed {resp_revert.status_code}")

if __name__ == "__main__":
    verify_update()
