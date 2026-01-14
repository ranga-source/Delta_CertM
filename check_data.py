import requests
import json

print('=== CHECKING SEEDED GLOBAL DATA ===')

# Technologies
tech_response = requests.get('http://localhost:8000/api/v1/global/technologies')
tech_count = len(tech_response.json()) if tech_response.status_code == 200 else 0
print(f'Technologies: {tech_count} found')
if tech_response.status_code == 200:
    for tech in tech_response.json():
        print(f'  - {tech["name"]} (ID: {tech["id"]})')

# Countries
countries_response = requests.get('http://localhost:8000/api/v1/global/countries')
country_count = len(countries_response.json()) if countries_response.status_code == 200 else 0
print(f'Countries: {country_count} found')
if countries_response.status_code == 200:
    for country in countries_response.json():
        print(f'  - {country["name"]} ({country["iso_code"]}) (ID: {country["id"]})')

# Certifications
cert_response = requests.get('http://localhost:8000/api/v1/global/certifications')
cert_count = len(cert_response.json()) if cert_response.status_code == 200 else 0
print(f'Certifications: {cert_count} found')
if cert_response.status_code == 200:
    for cert in cert_response.json():
        print(f'  - {cert["name"]} (ID: {cert["id"]})')

# Regulatory Rules
rules_response = requests.get('http://localhost:8000/api/v1/global/regulatory-matrix')
rules_count = len(rules_response.json()) if rules_response.status_code == 200 else 0
print(f'Regulatory Rules: {rules_count} found')

print('\n=== CHECKING TENANTS ===')
# Tenants
tenants_response = requests.get('http://localhost:8000/api/v1/tenants')
tenant_count = len(tenants_response.json()) if tenants_response.status_code == 200 else 0
print(f'Tenants: {tenant_count} found')
if tenants_response.status_code == 200 and tenant_count > 0:
    for tenant in tenants_response.json():
        print(f'  - {tenant["name"]} (ID: {tenant["id"]})')

print('\n=== CHECKING DEVICES ===')
# Devices (if tenant exists)
if tenants_response.status_code == 200 and tenant_count > 0:
    tenant_id = tenants_response.json()[0]["id"]
    devices_response = requests.get(f'http://localhost:8000/api/v1/devices?tenant_id={tenant_id}')
    device_count = len(devices_response.json()) if devices_response.status_code == 200 else 0
    print(f'Devices for tenant {tenant_id}: {device_count} found')
    if devices_response.status_code == 200:
        for device in devices_response.json():
            print(f'  - {device["model_name"]} (SKU: {device["sku"]}) (ID: {device["id"]})')
else:
    print('No tenants found, so no devices to check')

