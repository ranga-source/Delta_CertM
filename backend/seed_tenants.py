import requests
import sys

# Use 127.0.0.1 to avoid potential localhost resolution issues on Windows
BASE_URL = "http://127.0.0.1:8000/api/v1"

TENANTS = [
    {"name": "Acme Corp", "contact_email": "admin@acme.com"},
    {"name": "Globex Corporation", "contact_email": "contact@globex.com"},
    {"name": "Initech", "contact_email": "support@initech.com"},
    {"name": "Umbrella Corp", "contact_email": "security@umbrella.com"},
    {"name": "Stark Industries", "contact_email": "tony@stark.com"},
    {"name": "Cyberdyne Systems", "contact_email": "skynet@cyberdyne.com"},
    {"name": "Wayne Enterprises", "contact_email": "bruce@wayne.com"}
]

def seed_tenants():
    print("="*50)
    print("Seeding Tenants")
    print("="*50)
    
    # Check API health first
    try:
        # Simple health check (assuming /docs or /openapi.json exists, or just root)
        # Using a known endpoint get to check connectivity
        requests.get(f"http://127.0.0.1:8000/docs", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to backend at {BASE_URL}")
        print("Please ensure the backend is running: uvicorn app.main:app --reload")
        sys.exit(1)

    success_count = 0
    for tenant in TENANTS:
        try:
            response = requests.post(f"{BASE_URL}/tenants", json=tenant)
            if response.status_code == 201:
                data = response.json()
                print(f"✓ Created: {tenant['name']:<20} (ID: {data['id']})")
                success_count += 1
            elif response.status_code == 409:
                print(f"ℹ Exists : {tenant['name']}")
                # Count existence as success for the purpose of 'data is there'
                success_count += 1
            elif response.status_code == 422:
                print(f"✗ Validation Error for {tenant['name']}: {response.text}")
            else:
                print(f"✗ Failed ({response.status_code}): {tenant['name']} - {response.text}")
        except Exception as e:
            print(f"✗ Exception for {tenant['name']}: {str(e)}")
            
    print("-" * 50)
    print(f"Seed Complete. Total Tenants ready: {success_count}/{len(TENANTS)}")

if __name__ == "__main__":
    seed_tenants()
