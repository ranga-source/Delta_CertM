"""
Pydantic Schemas Package
========================
This package contains all Pydantic models for request/response validation.

Pydantic vs SQLAlchemy:
- SQLAlchemy models: Database ORM (what's IN the database)
- Pydantic schemas: API validation (what goes OVER the wire)

Schema Categories:
1. Global Data Schemas: For technologies, countries, certifications, rules
2. Tenant Schemas: For tenant management and notification rules
3. Device Schemas: For device registration and technology mapping
4. Compliance Schemas: For compliance tracking and gap analysis
"""

from app.schemas.global_data import *
from app.schemas.tenant import *
from app.schemas.device import *
from app.schemas.compliance import *


