import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print('=== FINAL SYSTEM STATE ===')

# Check tenants
tenants_response = requests.get(BASE_URL + "/tenants")
if tenants_response.status_code == 200:
    tenants = tenants_response.json()
    print(f'Tenants: {len(tenants)}')
    for tenant in tenants:
        tenant_id = tenant["id"]
        print(f'  - {tenant["name"]} (ID: {tenant_id})')
        print(f'    Email: {tenant["contact_email"]}')

        # Check notification rules
        rules_response = requests.get(BASE_URL + f"/tenants/{tenant_id}/notification-rules")
        if rules_response.status_code == 200:
            rules = rules_response.json()
            print(f'    Notification Rules: {len(rules)}')
            for rule in rules:
                print(f'      - {rule["days_before_expiry"]} days, severity: {rule["severity_level"]}')

        # Check devices
        devices_response = requests.get(BASE_URL + f"/devices?tenant_id={tenant_id}")
        if devices_response.status_code == 200:
            devices = devices_response.json()
            print(f'    Devices: {len(devices)}')
            for device in devices:
                device_id = device["id"]
                print(f'      - {device["model_name"]} ({device["sku"]}) - ID: {device_id}')

                # Check device technologies
                tech_response = requests.get(BASE_URL + f"/devices/{device_id}/technologies?tenant_id={tenant_id}")
                if tech_response.status_code == 200:
                    technologies = tech_response.json()
                    tech_names = [tech["name"] for tech in technologies]
                    print(f'        Technologies: {tech_names}')

print('\n=== GLOBAL DATA SUMMARY ===')
tech_response = requests.get(BASE_URL + "/global/technologies")
countries_response = requests.get(BASE_URL + "/global/countries")
cert_response = requests.get(BASE_URL + "/global/certifications")
rules_response = requests.get(BASE_URL + "/global/regulatory-matrix")

print(f'Technologies: {len(tech_response.json())}')
print(f'Countries: {len(countries_response.json())}')
print(f'Certifications: {len(cert_response.json())}')
print(f'Regulatory Rules: {len(rules_response.json())}')

print('\n=== READY FOR GAP ANALYSIS ===')
print('You can now run gap analysis on the device for different countries!')
print('Example: POST to /api/v1/compliance/gap-analysis with device_id and country_id')
