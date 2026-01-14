"""
Device Pydantic Schemas
=======================
Request/Response schemas for device registration and technology mapping.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.schemas.global_data import TechnologyResponse


# ============================================
# Device Schemas
# ============================================

class TenantDeviceBase(BaseModel):
    """Base schema for Tenant Device with shared fields."""
    model_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Device model name",
        examples=["Tractor X9", "Galaxy Watch 5", "Model 3"]
    )
    sku: Optional[str] = Field(
        None,
        max_length=50,
        description="Stock Keeping Unit or product code",
        examples=["TRX9-2024", "SM-R900"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed device description"
    )
    target_countries: List[str] = ["ALL"]


class TenantDeviceCreate(TenantDeviceBase):
    """
    Schema for creating a new Device.
    Used in POST /api/v1/devices
    
    Note: tenant_id is extracted from JWT token (not in request body)
    """
    technology_ids: List[int] = Field(
        ...,
        description="List of technology IDs this device incorporates",
        examples=[[1, 2, 3], [5, 7]]
    )


class TenantDeviceUpdate(BaseModel):
    """Schema for updating an existing Device."""
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    technology_ids: Optional[List[int]] = Field(
        None,
        description="Update device technologies (replaces existing list)"
    )
    target_countries: Optional[List[str]] = Field(
        None,
        description="Update target countries (replaces existing list). Pass ['ALL'] for Global."
    )


class TenantDeviceResponse(TenantDeviceBase):
    """
    Schema for Device API responses.
    Includes related technologies.
    """
    id: UUID = Field(..., description="Unique device identifier (UUID)")
    tenant_id: UUID = Field(..., description="Owning tenant ID")
    created_at: datetime = Field(..., description="Device registration timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    
    # Include technology information
    technologies: Optional[List[TechnologyResponse]] = Field(
        None,
        description="List of technologies in this device"
    )
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Device-Technology Mapping (for direct operations if needed)
# ============================================

class DeviceTechMapCreate(BaseModel):
    """
    Schema for directly creating a Device-Technology mapping.
    
    Note: Usually this is handled automatically when creating/updating devices,
    but this schema is available for direct manipulation if needed.
    """
    device_id: UUID = Field(..., description="Device UUID")
    technology_id: int = Field(..., description="Technology ID")


class DeviceTechMapResponse(BaseModel):
    """Schema for Device-Technology mapping responses."""
    device_id: UUID
    technology_id: int
    technology_name: Optional[str] = Field(None, description="Technology name")
    
    model_config = ConfigDict(from_attributes=True)


