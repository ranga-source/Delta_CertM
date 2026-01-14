import requests
import sys
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

DEVICES = [
    {
        "model_name": "Tractor X9",
        "description": "Autonomous Heavy Duty Tractor",
        "technologies": ["GPS", "Cellular 5G", "Wi-Fi 6"]
    },
    {
        "model_name": "Drone Mk1",
        "description": "Surveillance Drone",
        "technologies": ["GPS", "Bluetooth 5.0", "Wi-Fi 6"]
    },
    {
        "model_name": "Sensor Gateway",
        "description": "IoT Hub for field sensors",
        "technologies": ["LoRaWAN", "Cellular 4G", "Bluetooth 5.0"]
    },
    {
        "model_name": "Smart Watch Pro",
        "description": "Health monitoring wearable",
        "technologies": ["Bluetooth 5.0", "NFC", "GPS"]
    },
    {
        "model_name": "Industrial Controller",
        "description": "PLC with wireless connectivity",
        "technologies": ["Wi-Fi 6", "Bluetooth 5.0"]
    }
]

def get_technologies():
    try:
        response = requests.get(f"{BASE_URL}/global/technologies")
        if response.status_code == 200:
            return {t['name']: t['id'] for t in response.json()}
        else:
            print(f"❌ Failed to fetch technologies: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Error fetching technologies: {str(e)}")
        return {}

def get_tenants():
    try:
        response = requests.get(f"{BASE_URL}/tenants")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch tenants: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error fetching tenants: {str(e)}")
        return []

def seed_devices():
    print("="*50)
    print("Seeding Devices")
    print("="*50)

    tech_map = get_technologies()
    if not tech_map:
        print("❌ No technologies found. Please run seed_data.py first.")
        sys.exit(1)

    tenants = get_tenants()
    if not tenants:
        print("❌ No tenants found. Please run seed_tenants.py first.")
        sys.exit(1)

    success_count = 0

    for tenant in tenants:
        print(f"\nProcessing Tenant: {tenant['name']}")
        
        # Pick 2-3 random devices for this tenant
        tenant_devices = random.sample(DEVICES, random.randint(2, 3))
        
        for device_info in tenant_devices:
            # Map tech names to IDs
            tech_ids = [tech_map[t] for t in device_info['technologies'] if t in tech_map]
            
            payload = {
                "model_name": device_info['model_name'],
                "description": device_info['description'],
                "technology_ids": tech_ids
            }

            try:
                # tenant_id must be in query string, not body
                response = requests.post(
                    f"{BASE_URL}/devices", 
                    params={"tenant_id": tenant['id']}, 
                    json=payload
                )
                if response.status_code == 201:
                    print(f"  ✓ Created: {device_info['model_name']}")
                    success_count += 1
                else:
                    print(f"  ✗ Failed: {device_info['model_name']} - {response.text}")
            except Exception as e:
                print(f"  ✗ Exception: {str(e)}")

    print("-" * 50)
    print(f"Seed Complete. Total Devices Created: {success_count}")

if __name__ == "__main__":
    seed_devices()
