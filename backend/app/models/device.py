"""
Device Models
============
These models represent tenant devices (products) and their technology specifications.

Tables in this module:
1. TenantDevice - Products manufactured by tenants
2. DeviceTechMap - Many-to-many mapping of devices to technologies

Data Isolation:
- Each device belongs to exactly ONE tenant
- Devices are isolated by tenant_id
- Technologies are global but usage is tenant-specific
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, PrimaryKeyConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class TenantDevice(Base):
    """
    Tenant Device Model - Products that require certification
    
    Examples:
        - John Deere Tractor Model X9 (with GPS, Cellular, Wi-Fi)
        - Samsung Galaxy Watch 5 (with Bluetooth, NFC, Wireless Charging)
        - Tesla Model 3 (with 5G, GPS, Bluetooth, Wi-Fi)
        - Fitbit Sense 2 (with Bluetooth, NFC)
    
    Business Logic:
        - Each device is associated with multiple technologies
        - Technologies determine which certifications are needed
        - Gap Analysis uses device technologies + target country to find requirements
        - Devices can be variants/SKUs of the same product family
    
    User Journey:
        1. Tenant creates a device (e.g., "Tractor V1")
        2. Tenant tags technologies (GPS, Cellular, Wi-Fi)
        3. Tenant runs Gap Analysis for target country (e.g., India)
        4. System returns required certifications based on tech+country rules
        5. Tenant uploads certificates and tracks expiry
    
    Relationships:
        - tenant: Organization that owns this device
        - technologies: Hardware capabilities (via DeviceTechMap)
        - compliance_records: Certification tracking for this device
    """
    __tablename__ = "tenant_devices"
    
    # Primary Key - UUID for security
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the device"
    )
    
    # Foreign Key - Owning tenant
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant who owns this device"
    )
    
    # Device model name
    model_name = Column(
        String(100),
        nullable=False,
        comment="Device model name (e.g., 'Tractor X9', 'Galaxy Watch 5')"
    )
    
    # SKU or product code
    sku = Column(
        String(50),
        nullable=True,
        comment="Stock Keeping Unit or internal product code"
    )
    
    # Detailed description
    description = Column(
        Text,
        nullable=True,
        comment="Detailed device description, specifications, or notes"
    )

    # Target Markets (JSON list of country ISO codes or "ALL")
    # stored as JSON: ["ALL"] or ["USA", "DEU", "KOR"]
    target_countries = Column(JSON, default=["ALL"])
    
    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Device registration timestamp"
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
    
    # Owning tenant
    tenant = relationship(
        "Tenant",
        back_populates="devices",
        doc="Tenant who owns this device"
    )
    
    # Device technologies (many-to-many via DeviceTechMap)
    technology_mappings = relationship(
        "DeviceTechMap",
        back_populates="device",
        cascade="all, delete-orphan",
        doc="Technologies incorporated in this device"
    )
    
    # Direct technology relationship for easy serialization
    technologies = relationship(
        "Technology",
        secondary="device_tech_map",
        viewonly=True,
        doc="Technologies used by this device (resolved via mapping table)"
    )
    
    # Compliance tracking
    compliance_records = relationship(
        "ComplianceRecord",
        back_populates="device",
        cascade="all, delete-orphan",
        doc="Certification compliance records for this device"
    )
    
    def __repr__(self):
        return f"<TenantDevice(id={self.id}, model='{self.model_name}', tenant={self.tenant_id})>"


class DeviceTechMap(Base):
    """
    Device-Technology Mapping Model - Many-to-Many relationship
    
    Purpose:
        Links devices to the technologies they incorporate. A device can have
        multiple technologies, and a technology can be used in multiple devices.
    
    Example Mappings:
        - (Tractor X9, GPS) - Tractor uses GPS
        - (Tractor X9, Cellular 5G) - Tractor uses 5G
        - (Tractor X9, Wi-Fi 6) - Tractor uses Wi-Fi
        - (Galaxy Watch 5, Bluetooth) - Watch uses Bluetooth
        - (Galaxy Watch 5, NFC) - Watch uses NFC
    
    Business Logic:
        - Used by Gap Analysis to determine device capabilities
        - Query: "Get all technology_ids for device_id X"
        - Then use those IDs in regulatory_matrix query
        - This is the bridge between tenant devices and global tech catalog
    
    Relationships:
        - device: The product being analyzed
        - technology: The hardware capability
    """
    __tablename__ = "device_tech_map"
    
    # Composite Primary Key
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenant_devices.id", ondelete="CASCADE"),
        nullable=False,
        comment="Device that uses this technology"
    )
    
    technology_id = Column(
        Integer,
        ForeignKey("global_technologies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Technology used in the device"
    )
    
    # Define composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('device_id', 'technology_id'),
        {
            'comment': 'Many-to-many mapping between devices and technologies'
        }
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    device = relationship(
        "TenantDevice",
        back_populates="technology_mappings",
        doc="Device that incorporates this technology"
    )
    
    technology = relationship(
        "Technology",
        back_populates="device_mappings",
        doc="Technology used in the device"
    )
    
    def __repr__(self):
        return f"<DeviceTechMap(device={self.device_id}, tech={self.technology_id})>"


