"""
Tenant Models
============
These models represent tenant (customer) organizations and their configuration.

Tables in this module:
1. Tenant - Organizations using the system (John Deere, Samsung, etc.)
2. NotificationRule - Per-tenant alert configuration

Data Isolation:
- Each tenant sees ONLY their own data
- Tenant ID is used throughout the system for data isolation
- Global data (countries, technologies) is shared across all tenants
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Tenant(Base):
    """
    Tenant Model - Organizations using the TAMSys platform
    
    Examples:
        - John Deere - Agricultural equipment manufacturer
        - Samsung Electronics - Consumer electronics
        - Tesla - Automotive manufacturer
        - Fitbit - Wearable devices
    
    Business Logic:
        - Each tenant has isolated data (devices, compliance records)
        - Tenants share global regulatory data (countries, certifications)
        - Tenant ID is extracted from JWT token for all API requests
        - Multi-tenant architecture using shared database with tenant_id isolation
    
    Relationships:
        - devices: All devices registered by this tenant
        - compliance_records: All certification tracking for this tenant
        - notification_rules: Alert configuration for this tenant
    """
    __tablename__ = "tenants"
    
    # Primary Key - UUID for security (prevents enumeration attacks)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the tenant organization"
    )
    
    # Tenant organization name
    name = Column(
        String(100),
        nullable=False,
        comment="Organization name (e.g., 'John Deere', 'Samsung Electronics')"
    )
    
    # Primary contact email
    contact_email = Column(
        String(150),
        nullable=False,
        comment="Primary contact email for notifications and alerts"
    )
    
    # Active status flag
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="False = Tenant account is suspended/deactivated"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Tenant registration timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp"
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    # Tenant's devices
    devices = relationship(
        "TenantDevice",
        back_populates="tenant",
        cascade="all, delete-orphan",
        doc="All devices registered by this tenant"
    )
    
    # Tenant's compliance tracking
    compliance_records = relationship(
        "ComplianceRecord",
        back_populates="tenant",
        cascade="all, delete-orphan",
        doc="All certification compliance records for this tenant"
    )
    
    # Tenant's notification configuration
    notification_rules = relationship(
        "NotificationRule",
        back_populates="tenant",
        cascade="all, delete-orphan",
        doc="Alert configuration rules for this tenant"
    )
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', active={self.is_active})>"


class NotificationRule(Base):
    """
    Notification Rule Model - Per-tenant alert configuration
    
    Purpose:
        Different tenants have different alert preferences. Some want early
        warnings (90 days), others prefer shorter notice (30 days).
    
    Examples:
        - John Deere: Alert at 90, 60, and 30 days before expiry
        - Samsung: Alert at 60 and 30 days only
        - Startup Company: Alert at 30 days only (tight budget)
    
    Business Logic:
        - The daily cron job queries compliance_records.expiry_date
        - Compares against these notification rules per tenant
        - Sends email alerts when thresholds are hit
        - Prevents spam by tracking last_notified_at in compliance_records
    
    Future Enhancement:
        Could add notification channels (email, SMS, Slack, webhook)
        and severity-based routing.
    
    Relationships:
        - tenant: The organization this rule applies to
    """
    __tablename__ = "notification_rules"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique identifier for the notification rule"
    )
    
    # Foreign Key - Tenant who owns this rule
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant this notification rule applies to"
    )
    
    # Days before expiry to trigger alert
    days_before_expiry = Column(
        Integer,
        nullable=False,
        comment="Number of days before certificate expiry to send alert (e.g., 90, 60, 30)"
    )
    
    # Severity level (for future use with different notification channels)
    severity_level = Column(
        String(20),
        default="HIGH",
        nullable=False,
        comment="Alert severity: HIGH, MEDIUM, LOW (for future channel routing)"
    )
    
    # Active flag
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="False = Rule is disabled (won't trigger alerts)"
    )
    
    # Audit timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Rule creation timestamp"
    )
    
    # ============================================
    # Relationships
    # ============================================
    tenant = relationship(
        "Tenant",
        back_populates="notification_rules",
        doc="Tenant who owns this notification rule"
    )
    
    def __repr__(self):
        return (
            f"<NotificationRule("
            f"id={self.id}, "
            f"tenant={self.tenant_id}, "
            f"days={self.days_before_expiry}, "
            f"active={self.is_active}"
            f")>"
        )


