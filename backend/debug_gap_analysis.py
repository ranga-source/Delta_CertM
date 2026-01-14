import requests
import sys

# Set output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/v1"

def debug():
    try:
        print("--- Technologies ---")
        techs = requests.get(f"{BASE_URL}/global/technologies").json()
        for t in techs:
            print(f"ID: {t['id']}, Name: {t['name']}")

        print("\n--- Tenants ---")
        tenants = requests.get(f"{BASE_URL}/tenants").json()
        if not tenants:
            print("No tenants found! Create one first.")
            return
        
        tenant_id = tenants[0]['id']
        print(f"Using Tenant: {tenants[0]['name']} ({tenant_id})")

        print("\n--- Devices ---")
        devices = requests.get(f"{BASE_URL}/devices?tenant_id={tenant_id}").json()
        if not devices:
            print("No devices found.")
        
        for d in devices:
            print(f"DEBUG DEVICE ITEM: {d} (Type: {type(d)})")
            if isinstance(d, str):
                 # If it's just a string, maybe it's an ID?
                 did = d
                 d = {"id": did, "model_name": "Unknown"}
            else:
                 did = str(d['id'])
            # Avoid f-string complexity if causing issues
            print("Device: " + d['model_name'] + " (" + did + ")")
            
            # Get details
            details = requests.get(f"{BASE_URL}/devices/{did}").json()
            device_techs = [t['name'] for t in details.get('technologies', [])]
            print("  Techs: " + str(device_techs))
            
            if not device_techs:
                print("  [FIX] Device has no techs! Adding Wi-Fi 6E and 5G Cellular...")
                # Find tech IDs
                w_id = next((t['id'] for t in techs if t['name'] == 'Wi-Fi 6E'), None)
                g_id = next((t['id'] for t in techs if t['name'] == '5G Cellular'), None)
                
                if w_id and g_id:
                    update_payload = {
                        "model_name": d['model_name'],
                        "technology_ids": [w_id, g_id]
                    }
                    # Update device
                    up_resp = requests.put(
                        f"{BASE_URL}/devices/{did}?tenant_id={tenant_id}", 
                        json=update_payload
                    )
                    if up_resp.status_code == 200:
                         print("  [FIX] Success! Technologies added.")
                    else:
                         print("  [FIX] Failed: " + up_resp.text)

        print("\n--- Rules for South Korea ---")
        countries = requests.get(f"{BASE_URL}/global/countries").json()
        kor_id = None
        for c in countries:
            if c['iso_code'] in ['KOR', 'KR']:
                kor_id = c['id']
                break
        
        if kor_id:
            print("KOR ID: " + str(kor_id))
            if devices:
                d = devices[0]
                print("\n--- Gap Analysis Test ---")
                payload = {
                    "device_id": str(d['id']),
                    "country_id": kor_id
                }
                resp = requests.post(f"{BASE_URL}/compliance/gap-analysis", json=payload)
                print(resp.json())
        else:
            print("KOR Not found")

    except Exception as e:
        print("Error: " + str(e))

if __name__ == "__main__":
    debug()
