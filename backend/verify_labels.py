
import requests
import json

BASE_URL = "http://192.168.80.28:8000/api/v1"

try:
    response = requests.get(f"{BASE_URL}/global/labels")
    if response.status_code == 200:
        labels = response.json()
        print(f"Found {len(labels)} labels.")
        for l in labels:
            print(f"\nLabel: {l['name']}")
            print(f"Country ID: {l.get('country_id')}")
            print(f"Requirements: {json.dumps(l.get('requirements'), indent=2)}")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
