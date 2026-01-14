"""
Database Models Package
======================
This package contains all SQLAlchemy ORM models for the TAMSys application.

Model Categories:
1. Global Data Models: Technologies, Countries, Certifications, RegulatoryMatrix
2. Tenant Models: Tenants, NotificationRules
3. Device Models: TenantDevices, DeviceTechMap
4. Compliance Models: ComplianceRecords

Import all models here for easy access and Alembic auto-detection.
"""

from app.models.global_data import (
    Technology,
    Country,
    Certification,
    RegulatoryMatrix
)

from app.models.tenant import (
    Tenant,
    NotificationRule
)

from app.models.device import (
    TenantDevice,
    DeviceTechMap
)

from app.models.compliance import (
    ComplianceRecord
)

# Export all models for easy import
__all__ = [
    # Global Data Models
    "Technology",
    "Country",
    "Certification",
    "RegulatoryMatrix",
    
    # Tenant Models
    "Tenant",
    "NotificationRule",
    
    # Device Models
    "TenantDevice",
    "DeviceTechMap",
    
    # Compliance Models
    "ComplianceRecord",
]


