import requests
import sys

BASE_URL = "http://192.168.80.32:8000/api/v1"

# --- Helpers ---
def get_map(endpoint, key_field):
    """Fetch all items from endpoint and return a dict of key->id."""
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}?limit=1000")
        if resp.status_code == 200:
            return {item[key_field]: item["id"] for item in resp.json()}
    except Exception as e:
        print(f"[WARN] Could not fetch {endpoint}: {e}")
    return {}

def create_tenant(name, email):
    print(f"\n--- Processing Tenant: {name} ---")
    data = {"name": name, "contact_email": email}
    resp = requests.post(f"{BASE_URL}/tenants", json=data)
    if resp.status_code == 201:
        tid = resp.json()["id"]
        print(f"[CREATED] Tenant '{name}' (ID: {tid})")
        return tid
    elif resp.status_code == 409:
        # Fetch existing
        all_tenants = requests.get(f"{BASE_URL}/tenants").json()
        for t in all_tenants:
            if t["name"] == name:
                print(f"[EXISTS] Tenant '{name}' found (ID: {t['id']})")
                return t["id"]
    print(f"[ERROR] Could not get/create tenant {name}")
    return None

def create_device(tenant_id, model, sku, tech_names, tech_map, country_codes=None, country_map=None):
    if not tenant_id: return
    
    print(f"  ... Processing Device: {model}")
    
    # Resolve Tech IDs
    tech_ids = []
    for tname in tech_names:
        if tname in tech_map:
            tech_ids.append(tech_map[tname])
        else:
            print(f"    [WARN] Technology '{tname}' not found in DB")
            
    # Resolve Country IDs
    target_country_ids = []
    if country_codes and country_map:
        for code in country_codes:
            if code in country_map:
                target_country_ids.append(country_map[code])
            else:
                 print(f"    [WARN] Country '{code}' not found in DB")

    data = {
        "model_name": model,
        "sku": sku,
        "technology_ids": tech_ids,
        "target_country_ids": target_country_ids
    }
    
    resp = requests.post(f"{BASE_URL}/devices?tenant_id={tenant_id}", json=data)
    if resp.status_code == 201:
        did = resp.json()["id"]
        print(f"    [CREATED] Device '{model}' (ID: {did})")
    elif resp.status_code == 409:
        print(f"    [EXISTS] Device '{model}' already exists")
    else:
        print(f"    [ERROR] Failed to create device: {resp.text}")

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Build Lookups
    print("Fetching metadata...")
    tech_map = get_map("global/technologies", "name")
    country_map = get_map("global/countries", "iso_code")
    
    if not tech_map:
        print("[FATAL] No technologies found. Is the backend running and seeded?")
        sys.exit(1)

    # 2. John Deere (Tractor)
    jd_id = create_tenant("John Deere", "compliance@johndeere.com")
    create_device(
        tenant_id=jd_id,
        model="Tractor X9",
        sku="TRX9-2025",
        tech_names=["Wi-Fi 6E (802.11ax 6GHz)", "Bluetooth 5.3", "GPS/GNSS", "4G LTE"],
        tech_map=tech_map,
        country_codes=["USA", "DEU", "BRA"],
        country_map=country_map
    )

    # 3. Tesla (Infotainment)
    tesla_id = create_tenant("Tesla", "homologation@tesla.com")
    create_device(
        tenant_id=tesla_id,
        model="Model Y Infotainment System",
        sku="MY-INFO-V4",
        tech_names=["Wi-Fi 6 (802.11ax)", "Bluetooth 5.2", "5G Cellular", "UWB" if "UWB" in tech_map else "NFC"], # Fallback if UWB missing
        tech_map=tech_map,
        country_codes=["USA", "CHN", "DEU", "GBR"],
        country_map=country_map
    )

    # 4. Apple (Phone) - Example of diverse techs
    apple_id = create_tenant("Apple", "reg-ops@apple.com")
    create_device(
        tenant_id=apple_id,
        model="iPhone 16 Pro",
        sku="A3000",
        tech_names=["Wi-Fi 7 (802.11be)", "Bluetooth 5.3", "5G NR mmWave", "NFC", "Wireless Charging (Qi)"],
        tech_map=tech_map,
        country_codes=["USA", "JPN", "IND", "FRA"],
        country_map=country_map
    )

