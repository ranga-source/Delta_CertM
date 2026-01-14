
import requests
import sys

# Set output encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/v1"

def check_device_details():
    print("--- Checking Device Details API ---")
    
    # 1. Get Tenant
    tenants = requests.get(f"{BASE_URL}/tenants").json()
    if not tenants:
        print("No tenants found.")
        return
    tenant_id = tenants[0]['id']
    
    # 2. List Devices to find one
    devices = requests.get(f"{BASE_URL}/devices/?tenant_id={tenant_id}").json()
    if not devices:
        print("No devices found.")
        return
    
    target_device = next((d for d in devices if "Specific" in d['model_name']), devices[-1])
    did = target_device['id']
    print(f"Checking Device: {target_device['model_name']} ({did})")
    
    # 3. Get Details
    resp = requests.get(f"{BASE_URL}/devices/{did}?tenant_id={tenant_id}")
    if resp.status_code == 200:
        details = resp.json()
        tc = details.get('target_countries')
        print(f"Target Countries Raw: {tc}")
        print(f"Type: {type(tc)}")
    else:
        print(f"Failed to get details: {resp.status_code}")

if __name__ == "__main__":
    check_device_details()
