
import requests
import json

BASE_URL = "http://192.168.80.28:8000/api/v1"

def check_labels():
    try:
        print("Fetching labels from /global/labels...")
        resp = requests.get(f"{BASE_URL}/global/labels")
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            labels = resp.json()
            print(f"Found {len(labels)} labels.")
            if len(labels) > 0:
                print("Sample Label:")
                print(json.dumps(labels[0], indent=2))
                
                # Check specifics
                names = [l['name'] for l in labels]
                print(f"Available names: {names}")
        else:
            print(f"Error: {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

check_labels()
