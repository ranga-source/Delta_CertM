"""
Tenant Pydantic Schemas
=======================
Request/Response schemas for tenant operations and notification rules.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


# ============================================
# Tenant Schemas
# ============================================

class TenantBase(BaseModel):
    """Base schema for Tenant with shared fields."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Organization name",
        examples=["John Deere", "Samsung Electronics", "Tesla Inc."]
    )
    contact_email: EmailStr = Field(
        ...,
        description="Primary contact email for notifications",
        examples=["compliance@johndeere.com"]
    )


class TenantCreate(TenantBase):
    """
    Schema for creating a new Tenant.
    Used in POST /api/v1/tenants
    """
    pass


class TenantUpdate(BaseModel):
    """Schema for updating an existing Tenant."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = Field(
        None,
        description="Account active status (False = suspended)"
    )


class TenantResponse(TenantBase):
    """
    Schema for Tenant API responses.
    Includes UUID, active status, and timestamps.
    """
    id: UUID = Field(..., description="Unique tenant identifier (UUID)")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Tenant registration timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Notification Rule Schemas
# ============================================

class NotificationRuleBase(BaseModel):
    """
    Base schema for Notification Rules.
    
    Business Logic:
        Different tenants want alerts at different intervals.
        Common patterns: 90/60/30 days, 60/30 days, or just 30 days.
    """
    days_before_expiry: int = Field(
        ...,
        gt=0,
        le=365,
        description="Days before expiry to trigger alert",
        examples=[90, 60, 30, 15, 7]
    )
    severity_level: str = Field(
        "HIGH",
        description="Alert severity level (for future channel routing)",
        examples=["HIGH", "MEDIUM", "LOW"]
    )


class NotificationRuleCreate(NotificationRuleBase):
    """
    Schema for creating a Notification Rule.
    Used in POST /api/v1/tenants/{tenant_id}/notification-rules
    
    Note: tenant_id comes from path parameter, not request body
    """
    pass


class NotificationRuleUpdate(BaseModel):
    """Schema for updating a Notification Rule."""
    days_before_expiry: Optional[int] = Field(None, gt=0, le=365)
    severity_level: Optional[str] = None
    is_active: Optional[bool] = Field(
        None,
        description="False = Rule disabled (won't trigger alerts)"
    )


class NotificationRuleResponse(NotificationRuleBase):
    """Schema for Notification Rule API responses."""
    id: int = Field(..., description="Unique rule ID")
    tenant_id: UUID = Field(..., description="Tenant who owns this rule")
    is_active: bool = Field(..., description="Rule active status")
    created_at: datetime = Field(..., description="Rule creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


