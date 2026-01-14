"""
Tenant Service Module
====================
Business logic for tenant management and notification rules.

Services in this module:
- Tenant CRUD operations
- Notification Rule CRUD operations

Data Isolation:
- Future enhancement will filter by tenant_id from JWT token
- For now, tenants can access all data (auth disabled)
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.tenant import Tenant, NotificationRule
from app.schemas.tenant import (
    TenantCreate, TenantUpdate,
    NotificationRuleCreate, NotificationRuleUpdate
)


# ============================================
# Tenant Service
# ============================================

class TenantService:
    """Service class for Tenant operations."""
    
    @staticmethod
    def create_tenant(db: Session, tenant_data: TenantCreate) -> Tenant:
        """
        Create a new tenant organization.
        
        Args:
            db: Database session
            tenant_data: Tenant creation data
        
        Returns:
            Tenant: Created tenant object with auto-generated UUID
        
        Business Logic:
            - UUID is auto-generated for security
            - is_active defaults to True
            - Timestamps are auto-set
        """
        tenant = Tenant(**tenant_data.model_dump())
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    @staticmethod
    def get_all_tenants(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Tenant]:
        """
        Retrieve all tenants with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            active_only: If True, return only active tenants
        
        Returns:
            List[Tenant]: List of tenant objects
        """
        query = db.query(Tenant)
        
        if active_only:
            query = query.filter(Tenant.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: UUID) -> Tenant:
        """
        Retrieve a specific tenant by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
        
        Returns:
            Tenant: Tenant object
        
        Raises:
            HTTPException: If tenant not found (404)
        """
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} not found"
            )
        
        return tenant
    
    @staticmethod
    def update_tenant(
        db: Session,
        tenant_id: UUID,
        tenant_data: TenantUpdate
    ) -> Tenant:
        """
        Update an existing tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            tenant_data: Updated tenant data
        
        Returns:
            Tenant: Updated tenant object
        """
        tenant = TenantService.get_tenant_by_id(db, tenant_id)
        
        update_data = tenant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)
        
        db.commit()
        db.refresh(tenant)
        return tenant
    
    @staticmethod
    def delete_tenant(db: Session, tenant_id: UUID) -> dict:
        """
        Delete a tenant organization.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
        
        Returns:
            dict: Success message
        
        Warning:
            This will CASCADE DELETE all related data:
            - All devices
            - All compliance records
            - All notification rules
            Use with extreme caution!
        """
        tenant = TenantService.get_tenant_by_id(db, tenant_id)
        db.delete(tenant)
        db.commit()
        return {"message": f"Tenant '{tenant.name}' and all related data deleted successfully"}
    
    @staticmethod
    def deactivate_tenant(db: Session, tenant_id: UUID) -> Tenant:
        """
        Deactivate a tenant (soft delete).
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
        
        Returns:
            Tenant: Updated tenant with is_active=False
        
        Note:
            Preferred over hard delete. Tenant data is preserved
            but account is suspended.
        """
        tenant = TenantService.get_tenant_by_id(db, tenant_id)
        tenant.is_active = False
        db.commit()
        db.refresh(tenant)
        return tenant


# ============================================
# Notification Rule Service
# ============================================

class NotificationRuleService:
    """Service class for Notification Rule operations."""
    
    @staticmethod
    def create_rule(
        db: Session,
        tenant_id: UUID,
        rule_data: NotificationRuleCreate
    ) -> NotificationRule:
        """
        Create a new notification rule for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID (from path or JWT)
            rule_data: Notification rule creation data
        
        Returns:
            NotificationRule: Created rule object
        
        Example:
            Create alert for 90 days before expiry:
            tenant_id = "123e4567..."
            rule_data = {
                "days_before_expiry": 90,
                "severity_level": "HIGH"
            }
        """
        # Verify tenant exists
        TenantService.get_tenant_by_id(db, tenant_id)
        
        # Create rule
        rule = NotificationRule(
            tenant_id=tenant_id,
            **rule_data.model_dump()
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def get_tenant_rules(
        db: Session,
        tenant_id: UUID,
        active_only: bool = False
    ) -> List[NotificationRule]:
        """
        Get all notification rules for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            active_only: If True, return only active rules
        
        Returns:
            List[NotificationRule]: List of notification rules
        """
        query = db.query(NotificationRule).filter(
            NotificationRule.tenant_id == tenant_id
        )
        
        if active_only:
            query = query.filter(NotificationRule.is_active == True)
        
        return query.all()
    
    @staticmethod
    def get_rule_by_id(
        db: Session,
        rule_id: int,
        tenant_id: Optional[UUID] = None
    ) -> NotificationRule:
        """
        Get a specific notification rule by ID.
        
        Args:
            db: Database session
            rule_id: Notification rule ID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            NotificationRule: Notification rule object
        
        Raises:
            HTTPException: If rule not found (404)
        """
        query = db.query(NotificationRule).filter(NotificationRule.id == rule_id)
        
        # Optional: Verify tenant owns this rule
        if tenant_id:
            query = query.filter(NotificationRule.tenant_id == tenant_id)
        
        rule = query.first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification rule with ID {rule_id} not found"
            )
        
        return rule
    
    @staticmethod
    def update_rule(
        db: Session,
        rule_id: int,
        rule_data: NotificationRuleUpdate,
        tenant_id: Optional[UUID] = None
    ) -> NotificationRule:
        """
        Update an existing notification rule.
        
        Args:
            db: Database session
            rule_id: Notification rule ID
            rule_data: Updated rule data
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            NotificationRule: Updated rule object
        """
        rule = NotificationRuleService.get_rule_by_id(db, rule_id, tenant_id)
        
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(
        db: Session,
        rule_id: int,
        tenant_id: Optional[UUID] = None
    ) -> dict:
        """
        Delete a notification rule.
        
        Args:
            db: Database session
            rule_id: Notification rule ID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            dict: Success message
        """
        rule = NotificationRuleService.get_rule_by_id(db, rule_id, tenant_id)
        db.delete(rule)
        db.commit()
        return {"message": f"Notification rule (alert at {rule.days_before_expiry} days) deleted successfully"}

