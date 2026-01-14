import requests
import sys
import random
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

STATUSES = ['ACTIVE', 'EXPIRING', 'EXPIRED', 'PENDING']

def get_tenants():
    try:
        response = requests.get(f"{BASE_URL}/tenants")
        return response.json()
    except Exception: return []

def get_tenant_devices(tenant_id):
    try:
        response = requests.get(f"{BASE_URL}/devices", params={"tenant_id": tenant_id})
        return response.json()
    except Exception: return []

def get_global_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}/global/{endpoint}")
        return response.json()
    except Exception: return []

def seed_compliance():
    print("="*50)
    print("Seeding Compliance Records")
    print("="*50)

    tenants = get_tenants()
    countries = get_global_data("countries")
    certifications = get_global_data("certifications")

    if not tenants or not countries or not certifications:
        print("❌ Missing dependency data. Run seed_data.py and seed_tenants.py first.")
        sys.exit(1)

    success_count = 0

    for tenant in tenants:
        print(f"\nProcessing Tenant: {tenant['name']}")
        devices = get_tenant_devices(tenant['id'])
        
        if not devices:
            print("  No devices found.")
            continue

        for device in devices:
            # Create 2-4 records per device
            num_records = random.randint(2, 4)
            selected_countries = random.sample(countries, min(len(countries), num_records))
            
            for country in selected_countries:
                cert = random.choice(certifications)
                status = random.choice(STATUSES)
                
                # Calculate dates based on status
                expiry_date = None
                if status == 'ACTIVE':
                    expiry_date = (datetime.now() + timedelta(days=random.randint(100, 700))).strftime('%Y-%m-%d')
                elif status == 'EXPIRING':
                    # Expires in 10-25 days
                    expiry_date = (datetime.now() + timedelta(days=random.randint(5, 25))).strftime('%Y-%m-%d')
                elif status == 'EXPIRED':
                    # Expired 10-100 days ago
                    expiry_date = (datetime.now() - timedelta(days=random.randint(10, 100))).strftime('%Y-%m-%d')
                # PENDING usually has no expiry date yet, or a target date. We'll leave it null or future.

                payload = {
                    "tenant_id": tenant['id'],
                    "device_id": device['id'],
                    "country_id": country['id'],
                    "certification_id": cert['id'],
                    "status": status,
                    "expiry_date": expiry_date
                }

                try:
                    # tenant_id must be in query string
                    response = requests.post(
                        f"{BASE_URL}/compliance/records", 
                        params={"tenant_id": tenant['id']},
                        json=payload
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"  ✓ {status}: {device['model_name']} - {country['name']} ({cert['name']})")
                        success_count += 1
                    else:
                        # Fallback: Maybe endpoint is different?
                        print(f"  ✗ Failed: {response.text}")
                except Exception as e:
                    print(f"  ✗ Exception: {str(e)}")

    print("-" * 50)
    print(f"Seed Complete. Total Records: {success_count}")

if __name__ == "__main__":
    seed_compliance()
