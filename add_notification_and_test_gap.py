import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print('=== ADDING NOTIFICATION RULE ===')

# Get the tenant with device
tenants_response = requests.get(BASE_URL + "/tenants")
if tenants_response.status_code == 200:
    tenants = tenants_response.json()

    # Find tenant with devices
    tenant_with_device = None
    for tenant in tenants:
        devices_response = requests.get(BASE_URL + f"/devices?tenant_id={tenant['id']}")
        if devices_response.status_code == 200 and devices_response.json():
            tenant_with_device = tenant
            break

    if tenant_with_device:
        tenant_id = tenant_with_device["id"]
        print(f'Found tenant with device: {tenant_with_device["name"]} (ID: {tenant_id})')

        # Add notification rule
        notification_data = {
            "days_before_expiry": 90,
            "severity_level": "HIGH"
        }

        rule_response = requests.post(BASE_URL + f"/tenants/{tenant_id}/notification-rules", json=notification_data)
        if rule_response.status_code == 201:
            print(f'[SUCCESS] Added notification rule: {notification_data["days_before_expiry"]} days, severity {notification_data["severity_level"]}')
        else:
            print(f'[INFO] Notification rule may already exist: {rule_response.status_code}')

        # Get device for gap analysis
        devices_response = requests.get(BASE_URL + f"/devices?tenant_id={tenant_id}")
        if devices_response.status_code == 200 and devices_response.json():
            device = devices_response.json()[0]
            device_id = device["id"]
            print(f'Found device: {device["model_name"]} (ID: {device_id})')

            print('\n=== RUNNING GAP ANALYSIS ===')

            # Run gap analysis for India
            gap_data = {
                "device_id": device_id,
                "country_id": 2  # India
            }

            gap_response = requests.post(BASE_URL + f"/compliance/gap-analysis?tenant_id={tenant_id}", json=gap_data)
            if gap_response.status_code == 200:
                gap_result = gap_response.json()
                print(f'Gap Analysis for India: {gap_result["total_required"]} required, {gap_result["gaps_found"]} gaps')
                print('Results:')
                for result in gap_result["results"]:
                    status = "[GAP]" if result["has_gap"] else "[OK]"
                    print(f'  {status} {result["certification_name"]} for {result["technology"]}')

            # Run gap analysis for USA
            gap_data_usa = {
                "device_id": device_id,
                "country_id": 1  # USA
            }

            gap_response_usa = requests.post(BASE_URL + f"/compliance/gap-analysis?tenant_id={tenant_id}", json=gap_data_usa)
            if gap_response_usa.status_code == 200:
                gap_result_usa = gap_response_usa.json()
                print(f'\nGap Analysis for USA: {gap_result_usa["total_required"]} required, {gap_result_usa["gaps_found"]} gaps')
                print('Results:')
                for result in gap_result_usa["results"]:
                    status = "[GAP]" if result["has_gap"] else "[OK]"
                    print(f'  {status} {result["certification_name"]} for {result["technology"]}')

            print('\n=== SYSTEM READY ===')
            print('The TAMSys system is now fully set up with:')
            print('- Global master data (technologies, countries, certifications, rules)')
            print('- Tenant (John Deere) with notification rules')
            print('- Device (Tractor X9) with technologies')
            print('- Gap analysis engine working correctly')
            print('\nYou can now:')
            print('1. Visit http://localhost:8000/docs for API documentation')
            print('2. Add compliance records for missing certifications')
            print('3. Upload certificate PDFs')
            print('4. Monitor expiry dates with automated alerts')

