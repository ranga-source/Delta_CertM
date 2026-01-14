"""
Device Service Module
====================
Business logic for device registration and technology mapping.

Services in this module:
- Device CRUD operations
- Device-Technology mapping operations

Data Isolation:
- Devices are filtered by tenant_id
- Future enhancement: Extract tenant_id from JWT token
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.device import TenantDevice, DeviceTechMap
from app.models.global_data import Technology
from app.schemas.device import TenantDeviceCreate, TenantDeviceUpdate
from app.services.tenant_service import TenantService


# ============================================
# Device Service
# ============================================

class DeviceService:
    """Service class for Tenant Device operations."""
    
    @staticmethod
    def create_device(
        db: Session,
        tenant_id: UUID,
        device_data: TenantDeviceCreate
    ) -> TenantDevice:
        """
        Create a new device for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID (from JWT token in production)
            device_data: Device creation data including technology_ids
        
        Returns:
            TenantDevice: Created device object with technologies
        
        Business Logic:
            1. Verify tenant exists
            2. Create device record
            3. Create device-technology mappings
            4. Return device with relationships loaded
        
        Example:
            device_data = {
                "model_name": "Tractor X9",
                "sku": "TRX9-2024",
                "technology_ids": [1, 2, 3]  # Wi-Fi, Bluetooth, GPS
            }
        """
        # Verify tenant exists
        TenantService.get_tenant_by_id(db, tenant_id)
        
        # Extract technology_ids before creating device
        tech_ids = device_data.technology_ids
        device_dict = device_data.model_dump(exclude={'technology_ids'})
        
        # Create device
        device = TenantDevice(
            tenant_id=tenant_id,
            **device_dict
        )
        db.add(device)
        db.flush()  # Flush to get device ID without committing
        
        # Create device-technology mappings
        for tech_id in tech_ids:
            # Verify technology exists
            technology = db.query(Technology).filter(Technology.id == tech_id).first()
            if not technology:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Technology with ID {tech_id} not found"
                )
            
            # Create mapping
            mapping = DeviceTechMap(
                device_id=device.id,
                technology_id=tech_id
            )
            db.add(mapping)
        
        db.commit()
        # Reload with technologies for response serialization
        return DeviceService.get_device_by_id(
            db=db,
            device_id=device.id,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def get_tenant_devices(
        db: Session,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[TenantDevice]:
        """
        Get all devices for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            skip: Pagination offset
            limit: Maximum records to return
        
        Returns:
            List[TenantDevice]: List of devices for the tenant
        """
        return db.query(TenantDevice)\
            .options(
                selectinload(TenantDevice.technologies)
            )\
            .filter(TenantDevice.tenant_id == tenant_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_device_by_id(
        db: Session,
        device_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> TenantDevice:
        """
        Get a specific device by ID.
        
        Args:
            db: Database session
            device_id: Device UUID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            TenantDevice: Device object
        
        Raises:
            HTTPException: If device not found (404)
        """
        query = db.query(TenantDevice)\
            .options(
                selectinload(TenantDevice.technologies)
            )\
            .filter(TenantDevice.id == device_id)
        
        # Optional: Verify tenant owns this device
        if tenant_id:
            query = query.filter(TenantDevice.tenant_id == tenant_id)
        
        device = query.first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found"
            )
        
        return device
    
    @staticmethod
    def update_device(
        db: Session,
        device_id: UUID,
        device_data: TenantDeviceUpdate,
        tenant_id: Optional[UUID] = None
    ) -> TenantDevice:
        """
        Update an existing device.
        
        Args:
            db: Database session
            device_id: Device UUID
            device_data: Updated device data
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            TenantDevice: Updated device object
        
        Business Logic:
            If technology_ids is provided, it REPLACES the existing
            technology mappings (not an addition).
        """
        device = DeviceService.get_device_by_id(db, device_id, tenant_id)
        
        # Extract technology_ids if provided
        update_data = device_data.model_dump(exclude_unset=True, exclude={'technology_ids'})
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(device, field, value)
        
        # Update technologies if provided
        if device_data.technology_ids is not None:
            # Delete existing mappings
            db.query(DeviceTechMap)\
                .filter(DeviceTechMap.device_id == device_id)\
                .delete()
            
            # Create new mappings
            for tech_id in device_data.technology_ids:
                # Verify technology exists
                technology = db.query(Technology).filter(Technology.id == tech_id).first()
                if not technology:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Technology with ID {tech_id} not found"
                    )
                
                mapping = DeviceTechMap(
                    device_id=device.id,
                    technology_id=tech_id
                )
                db.add(mapping)
        
        db.commit()
        # Reload with technologies for response serialization
        return DeviceService.get_device_by_id(
            db=db,
            device_id=device.id,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def delete_device(
        db: Session,
        device_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> dict:
        """
        Delete a device.
        
        Args:
            db: Database session
            device_id: Device UUID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            dict: Success message
        
        Warning:
            This will CASCADE DELETE:
            - All device-technology mappings
            - All compliance records for this device
            Use with caution!
        """
        device = DeviceService.get_device_by_id(db, device_id, tenant_id)
        db.delete(device)
        db.commit()
        return {"message": f"Device '{device.model_name}' and all related data deleted successfully"}
    
    @staticmethod
    def get_device_technologies(db: Session, device_id: UUID) -> List[Technology]:
        """
        Get all technologies for a device.
        
        Args:
            db: Database session
            device_id: Device UUID
        
        Returns:
            List[Technology]: List of technologies used in the device
        
        Business Logic:
            Joins device_tech_map with global_technologies
            to return full technology objects.
        """
        # Verify device exists
        DeviceService.get_device_by_id(db, device_id)
        
        # Query technologies through mapping table
        technologies = db.query(Technology)\
            .join(DeviceTechMap, Technology.id == DeviceTechMap.technology_id)\
            .filter(DeviceTechMap.device_id == device_id)\
            .all()
        
        return technologies


