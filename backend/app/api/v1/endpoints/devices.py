"""
Device API Endpoints
===================
CRUD operations for device registration and technology mapping.

Endpoints:
- Devices: GET, POST, PUT, DELETE /devices
- Device Technologies: GET /devices/{id}/technologies

Data Isolation:
- Future: tenant_id extracted from JWT token
- Currently: tenant_id provided as query parameter
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.device import (
    TenantDeviceCreate,
    TenantDeviceUpdate,
    TenantDeviceResponse
)
from app.schemas.global_data import TechnologyResponse
from app.services.device_service import DeviceService
from app.services.compliance_service import ComplianceRecordService

router = APIRouter()


# ============================================
# Device Endpoints
# ============================================

@router.post(
    "/",
    response_model=TenantDeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Device",
    description="Register a new device with technologies"
)
def create_device(
    device: TenantDeviceCreate,
    tenant_id: UUID = Query(..., description="Tenant UUID (future: from JWT token)"),
    db: Session = Depends(get_db)
):
    """
    Create a new device.
    
    Example:
        {
            "model_name": "Tractor X9",
            "sku": "TRX9-2024",
            "description": "Agricultural tractor with GPS and cellular",
            "technology_ids": [1, 2, 3]  # Wi-Fi, Bluetooth, GPS
        }
    
    Note:
        tenant_id currently comes from query parameter.
        In production, it will be extracted from JWT token.
    """
    created_device = DeviceService.create_device(db, tenant_id, device)
    
    # Automatically initialize compliance records based on target countries
    if created_device.target_countries:
        try:
            ComplianceRecordService.bulk_init_compliance(
                db, 
                tenant_id, 
                created_device.id, 
                created_device.target_countries
            )
        except Exception as e:
            # We don't want to fail device creation if compliance init fails
            # but we should log it or handle it. For now, just continue.
            print(f"Error initializing compliance records: {e}")
            
    return created_device


@router.get(
    "/",
    response_model=List[TenantDeviceResponse],
    summary="List Devices",
    description="Retrieve all devices for a tenant"
)
def list_devices(
    tenant_id: UUID = Query(..., description="Tenant UUID (future: from JWT token)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all devices for a tenant.
    
    Query Parameters:
        - tenant_id: Tenant UUID (data isolation)
        - skip: Pagination offset
        - limit: Maximum records to return
    """
    return DeviceService.get_tenant_devices(db, tenant_id, skip, limit)


@router.get(
    "/{device_id}",
    response_model=TenantDeviceResponse,
    summary="Get Device",
    description="Retrieve a specific device by ID"
)
def get_device(
    device_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Get device by ID.
    
    Query Parameters:
        - tenant_id: Optional - verifies device belongs to tenant
    """
    return DeviceService.get_device_by_id(db, device_id, tenant_id)


@router.put(
    "/{device_id}",
    response_model=TenantDeviceResponse,
    summary="Update Device",
    description="Update an existing device"
)
def update_device(
    device_id: UUID,
    device: TenantDeviceUpdate,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Update device information.
    
    Example:
        {
            "model_name": "Tractor X9 Pro",
            "technology_ids": [1, 2, 3, 4]  # Add NFC
        }
    
    Note:
        If technology_ids is provided, it REPLACES existing technologies.
    """
    updated_device = DeviceService.update_device(db, device_id, device, tenant_id)
    
    # Re-initialize compliance records if target_countries or technology_ids changed
    # (bulk_init_compliance handles existing records gracefully by skipping them)
    if updated_device.target_countries:
        try:
            ComplianceRecordService.bulk_init_compliance(
                db, 
                tenant_id, 
                updated_device.id, 
                updated_device.target_countries
            )
        except Exception as e:
            print(f"Error re-initializing compliance records: {e}")
            
    return updated_device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Device",
    description="Delete a device and ALL related data"
)
def delete_device(
    device_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Delete device.
    
    Warning: This CASCADE DELETES:
        - All device-technology mappings
        - All compliance records for this device
    """
    return DeviceService.delete_device(db, device_id, tenant_id)


# ============================================
# Device Technology Endpoints
# ============================================

@router.get(
    "/{device_id}/technologies",
    response_model=List[TechnologyResponse],
    summary="Get Device Technologies",
    description="Retrieve all technologies for a device"
)
def get_device_technologies(
    device_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all technologies used in a device.
    
    Returns:
        List of technology objects (id, name, description)
    
    Business Logic:
        Used by Gap Analysis to determine required certifications.
    """
    return DeviceService.get_device_technologies(db, device_id)


