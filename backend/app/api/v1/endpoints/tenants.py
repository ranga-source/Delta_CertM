"""
Tenant API Endpoints
===================
CRUD operations for tenant management and notification rules.

Endpoints:
- Tenants: GET, POST, PUT, DELETE /tenants
- Notification Rules: GET, POST, PUT, DELETE /tenants/{id}/notification-rules

Data Isolation:
- Future: tenant_id extracted from JWT token
- Currently: tenant_id provided in path/body
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse,
    NotificationRuleCreate, NotificationRuleUpdate, NotificationRuleResponse
)
from app.services.tenant_service import TenantService, NotificationRuleService

router = APIRouter()


# ============================================
# Tenant Endpoints
# ============================================

@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Tenant",
    description="Register a new tenant organization"
)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tenant.
    
    Example:
        {
            "name": "John Deere",
            "contact_email": "compliance@johndeere.com"
        }
    """
    return TenantService.create_tenant(db, tenant)


@router.get(
    "/",
    response_model=List[TenantResponse],
    summary="List Tenants",
    description="Retrieve all tenants with pagination"
)
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all tenants.
    
    Query Parameters:
        - active_only: If true, return only active tenants
    """
    return TenantService.get_all_tenants(db, skip, limit, active_only)


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Get Tenant",
    description="Retrieve a specific tenant by ID"
)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get tenant by ID."""
    return TenantService.get_tenant_by_id(db, tenant_id)


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Update Tenant",
    description="Update an existing tenant"
)
def update_tenant(
    tenant_id: UUID,
    tenant: TenantUpdate,
    db: Session = Depends(get_db)
):
    """
    Update tenant information.
    
    Example:
        {
            "contact_email": "new-email@johndeere.com",
            "is_active": true
        }
    """
    return TenantService.update_tenant(db, tenant_id, tenant)


@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Tenant",
    description="Delete a tenant and ALL related data (use with caution)"
)
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete tenant.
    
    Warning: This CASCADE DELETES all related data:
        - All devices
        - All compliance records
        - All notification rules
    """
    return TenantService.delete_tenant(db, tenant_id)


@router.post(
    "/{tenant_id}/deactivate",
    response_model=TenantResponse,
    summary="Deactivate Tenant",
    description="Soft delete - deactivate tenant account (data preserved)"
)
def deactivate_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate tenant (soft delete)."""
    return TenantService.deactivate_tenant(db, tenant_id)


# ============================================
# Notification Rule Endpoints
# ============================================

@router.post(
    "/{tenant_id}/notification-rules",
    response_model=NotificationRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Notification Rule",
    description="Add a notification rule for a tenant"
)
def create_notification_rule(
    tenant_id: UUID,
    rule: NotificationRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a notification rule.
    
    Example:
        {
            "days_before_expiry": 90,
            "severity_level": "HIGH"
        }
    
    This will trigger alerts 90 days before certificate expiry.
    """
    return NotificationRuleService.create_rule(db, tenant_id, rule)


@router.get(
    "/{tenant_id}/notification-rules",
    response_model=List[NotificationRuleResponse],
    summary="List Notification Rules",
    description="Get all notification rules for a tenant"
)
def list_notification_rules(
    tenant_id: UUID,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get tenant's notification rules.
    
    Query Parameters:
        - active_only: If true, return only active rules
    """
    return NotificationRuleService.get_tenant_rules(db, tenant_id, active_only)


@router.get(
    "/{tenant_id}/notification-rules/{rule_id}",
    response_model=NotificationRuleResponse,
    summary="Get Notification Rule",
    description="Retrieve a specific notification rule"
)
def get_notification_rule(
    tenant_id: UUID,
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get notification rule by ID."""
    return NotificationRuleService.get_rule_by_id(db, rule_id, tenant_id)


@router.put(
    "/{tenant_id}/notification-rules/{rule_id}",
    response_model=NotificationRuleResponse,
    summary="Update Notification Rule",
    description="Update an existing notification rule"
)
def update_notification_rule(
    tenant_id: UUID,
    rule_id: int,
    rule: NotificationRuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update notification rule.
    
    Example:
        {
            "days_before_expiry": 60,
            "is_active": false
        }
    """
    return NotificationRuleService.update_rule(db, rule_id, rule, tenant_id)


@router.delete(
    "/{tenant_id}/notification-rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Notification Rule",
    description="Delete a notification rule"
)
def delete_notification_rule(
    tenant_id: UUID,
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete notification rule."""
    return NotificationRuleService.delete_rule(db, rule_id, tenant_id)


