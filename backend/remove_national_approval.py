
import requests

BASE_URL = "http://192.168.80.28:8000/api/v1"

def cleanup():
    print("Fetching certifications...")
    certs = requests.get(f"{BASE_URL}/global/certifications").json()
    
    # Find National Approval
    target_cert = next((c for c in certs if c['name'] == "National Approval"), None)
    
    if not target_cert:
        print(" 'National Approval' certification not found. Nothing to do.")
        return

    cert_id = target_cert['id']
    print(f"Found 'National Approval' ID: {cert_id}")

    # Delete Rules
    print("Fetching regulatory matrix...")
    matrix = requests.get(f"{BASE_URL}/global/regulatory-matrix?limit=10000").json()
    
    deleted_rules = 0
    for r in matrix:
        if r['certification_id'] == cert_id:
            # print(f"Deleting Rule ID: {r['id']}")
            resp = requests.delete(f"{BASE_URL}/global/regulatory-matrix/{r['id']}")
            if resp.status_code in [200, 204]:
                deleted_rules += 1
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)

    print(f"\nDeleted {deleted_rules} rules associated with National Approval.")

    # Delete Certification
    # print(f"Deleting Certification ID: {cert_id}")
    # Note: If there are other constraints (like other tables), this might fail.
    # But usually just RegulatoryMatrix is the main link.
    resp = requests.delete(f"{BASE_URL}/global/certifications/{cert_id}")
    if resp.status_code in [200, 204]:
        print("Successfully deleted 'National Approval' certification.")
    else:
        print(f"Failed to delete certification: {resp.status_code} - {resp.text}")

cleanup()
