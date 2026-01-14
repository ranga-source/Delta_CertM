"""
Global Data Models
=================
These models represent the MASTER DATA that is managed by administrators
and visible to all tenants. This is the "Rules Engine" foundation.

Tables in this module:
1. Technology - Building blocks (Wi-Fi, Bluetooth, GPS, etc.)
2. Country - Target markets (USA, India, EU countries, etc.)
3. Certification - Regulatory licenses (FCC, WPC, CE, etc.)
4. RegulatoryMatrix - The logic engine (Tech + Country = Required Cert)

Data Visibility:
- These tables are GLOBAL (no tenant_id)
- All tenants can READ this data
- Only ADMINS can CREATE/UPDATE/DELETE
- This ensures consistent regulatory logic across all tenants
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Technology(Base):
    """
    Technology Model - Hardware capabilities that require certification
    
    Examples:
        - Wi-Fi 6E (6 GHz band)
        - Bluetooth 5.3
        - GPS/GNSS
        - 5G Cellular
        - NFC
        - Wireless Charging (WPC Qi)
    
    Business Logic:
        Each technology may require different certifications in different countries.
        For example, Wi-Fi 6E requires special approval in India (WPC) because
        it uses the 6 GHz band.
    
    Relationships:
        - regulatory_matrix: Links to required certifications per country
        - devices: Links to devices that use this technology
    """
    __tablename__ = "global_technologies"
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier for the technology"
    )
    
    # Technology name - must be unique
    name = Column(
        String(100), 
        nullable=False, 
        unique=True,
        comment="Technology name (e.g., 'Wi-Fi 6E', 'Bluetooth 5.3')"
    )
    
    # Detailed description
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the technology and its regulatory considerations"
    )
    
    # Audit timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    # Link to regulatory requirements
    regulatory_rules = relationship(
        "RegulatoryMatrix",
        back_populates="technology",
        cascade="all, delete-orphan",
        doc="Regulatory requirements for this technology across countries"
    )
    
    # Link to devices using this technology
    device_mappings = relationship(
        "DeviceTechMap",
        back_populates="technology",
        cascade="all, delete-orphan",
        doc="Devices that incorporate this technology"
    )
    
    def __repr__(self):
        return f"<Technology(id={self.id}, name='{self.name}')>"


class Country(Base):
    """
    Country Model - Target markets with specific regulatory requirements
    
    Examples:
        - United States (USA) - FCC regulations
        - India (IND) - WPC, BIS, TEC regulations
        - European Union countries - CE marking
        - Japan (JPN) - TELEC/JATE
        - China (CHN) - SRRC, CCC
    
    Business Logic:
        Each country has unique regulatory bodies and certification requirements.
        Some certifications apply to groups of countries (e.g., CE for EU).
    
    Relationships:
        - regulatory_matrix: Links to required certifications for technologies
        - compliance_records: Links to actual compliance tracking per tenant
    """
    __tablename__ = "global_countries"
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier for the country"
    )
    
    # Country name
    name = Column(
        String(100), 
        nullable=False,
        comment="Full country name (e.g., 'United States', 'India')"
    )
    
    # ISO 3166-1 alpha-3 code
    iso_code = Column(
        String(3), 
        nullable=False, 
        unique=True,
        comment="ISO 3166-1 alpha-3 country code (e.g., 'USA', 'IND', 'GBR')"
    )

    # Detailed country profile (Voltage, Plugs, Label Requirements, etc.)
    details = Column(
        JSON,
        nullable=True,
        comment="Flexible country details (voltage, plugs, label requirements)"
    )
    
    # Audit timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    # Link to regulatory requirements
    regulatory_rules = relationship(
        "RegulatoryMatrix",
        back_populates="country",
        cascade="all, delete-orphan",
        doc="Regulatory requirements for this country"
    )
    
    # Link to compliance records
    compliance_records = relationship(
        "ComplianceRecord",
        back_populates="country",
        doc="Compliance tracking for devices targeting this country"
    )
    
    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', iso_code='{self.iso_code}')>"


class Certification(Base):
    """
    Certification Model - Regulatory licenses/approvals required for market access
    
    Examples:
        - FCC Part 15 (USA) - Unintentional radiators
        - FCC Part 18 (USA) - Industrial, Scientific, and Medical equipment
        - WPC (India) - Wireless Planning and Coordination
        - CE (EU) - Conformité Européenne marking
        - TELEC (Japan) - Radio equipment certification
        - SRRC (China) - State Radio Regulation Committee
    
    Business Logic:
        Each certification is issued by a regulatory authority and has specific
        requirements, testing procedures, and renewal cycles.
    
    Relationships:
        - regulatory_matrix: Links to technologies and countries where required
        - compliance_records: Links to actual certification status per device
    """
    __tablename__ = "global_certifications"
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier for the certification"
    )
    
    # Certification name - must be unique
    name = Column(
        String(100), 
        nullable=False, 
        unique=True,
        comment="Certification name/code (e.g., 'FCC Part 15', 'WPC', 'CE')"
    )
    
    # Issuing authority
    authority_name = Column(
        String(100),
        nullable=True,
        comment="Regulatory body that issues this certification (e.g., 'Federal Communications Commission')"
    )
    
    # Detailed description
    description = Column(
        Text,
        nullable=True,
        comment="Description of what this certification covers, requirements, and validity period"
    )

    # Branding/Labeling Info
    branding_image_url = Column(
        String(255),
        nullable=True,
        comment="URL to the official certification logo/mark"
    )

    labeling_requirements = Column(
        Text,
        nullable=True,
        comment="Specific requirements for placing the label on the product (min size, location, etc.)"
    )
    
    # Audit timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    # Link to regulatory requirements
    regulatory_rules = relationship(
        "RegulatoryMatrix",
        back_populates="certification",
        cascade="all, delete-orphan",
        doc="Regulatory rules where this certification is required"
    )
    
    # Link to compliance records
    compliance_records = relationship(
        "ComplianceRecord",
        back_populates="certification",
        doc="Compliance tracking for this certification across tenants"
    )
    
    def __repr__(self):
        return f"<Certification(id={self.id}, name='{self.name}')>"


class RegulatoryMatrix(Base):
    """
    Regulatory Matrix Model - The CORE LOGIC ENGINE
    
    This is the most critical table in the system. It defines the rules:
    "If a device has Technology X and targets Country Y, it MUST have Certification Z"
    
    Example Rules:
        - (Wi-Fi 6E, India, WPC) - MANDATORY
        - (Bluetooth, USA, FCC Part 15) - MANDATORY
        - (GPS, EU, CE) - MANDATORY
        - (Wireless Charging, USA, FCC Part 18) - MANDATORY
    
    Business Logic:
        The Gap Analysis Engine queries this table to determine what certifications
        a device needs based on its technologies and target market.
    
    Gap Analysis Query Logic:
        1. Get all technologies in the device (from device_tech_map)
        2. Filter regulatory_matrix WHERE technology_id IN (device_techs) AND country_id = target_country
        3. Return list of required certifications
        4. Compare against existing compliance_records to find gaps
    
    Relationships:
        - technology: The hardware capability being regulated
        - country: The market with specific requirements
        - certification: The required regulatory approval
    """
    __tablename__ = "regulatory_matrix"
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier for the regulatory rule"
    )
    
    # Foreign Keys - The "Rule Triple"
    technology_id = Column(
        Integer, 
        ForeignKey("global_technologies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Indexed for fast Gap Analysis queries
        comment="Technology being regulated"
    )
    
    country_id = Column(
        Integer, 
        ForeignKey("global_countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Indexed for fast Gap Analysis queries
        comment="Country where certification is required"
    )
    
    certification_id = Column(
        Integer, 
        ForeignKey("global_certifications.id", ondelete="CASCADE"),
        nullable=False,
        comment="Required certification"
    )
    
    # Mandatory flag
    is_mandatory = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="True = Mandatory for market access, False = Optional/Recommended"
    )
    
    # Additional notes
    notes = Column(
        Text,
        nullable=True,
        comment="Additional regulatory notes, exemptions, or special conditions"
    )
    
    # Audit timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    # ============================================
    # Constraints
    # ============================================
    # Ensure no duplicate rules: Same Tech + Country + Cert combination should appear only once
    __table_args__ = (
        UniqueConstraint(
            'technology_id', 
            'country_id', 
            'certification_id',
            name='uq_regulatory_rule'
        ),
        {
            'comment': 'Regulatory Matrix - Core logic engine for compliance requirements'
        }
    )
    
    # ============================================
    # Relationships
    # ============================================
    technology = relationship(
        "Technology",
        back_populates="regulatory_rules",
        doc="Technology being regulated"
    )
    
    country = relationship(
        "Country",
        back_populates="regulatory_rules",
        doc="Country with this requirement"
    )
    
    certification = relationship(
        "Certification",
        back_populates="regulatory_rules",
        doc="Required certification"
    )
    
    def __repr__(self):
        return (
            f"<RegulatoryMatrix("
            f"tech={self.technology_id}, "
            f"country={self.country_id}, "
            f"cert={self.certification_id}, "
            f"mandatory={self.is_mandatory}"
            f")>"
        )



class GlossaryTerm(Base):
    """
    Glossary Term Model - Knowledge Base Articles
    
    Stores rich content for glossary terms, including structured sections,
    tables, and metadata.
    """
    __tablename__ = "global_glossary"
    
    id = Column(
        String(50), 
        primary_key=True, 
        index=True,
        comment="Slug ID (e.g., 'fcc-15-247')"
    )
    
    term = Column(
        String(200),
        nullable=False,
        index=True,
        comment="The term being defined (e.g., 'FCC Part 15.247')"
    )
    
    category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Category (Regulatory, Japan, EMC, etc.)"
    )

    region = Column(
        String(50),
        nullable=True,
        comment="Region (e.g., 'USA', 'EU', 'Japan', 'Brazil')"
    )
    
    summary = Column(
        Text,
        nullable=False,
        comment="Brief summary for list view"
    )
    
    # Rich content: sections, paragraphs, tables
    sections = Column(
        JSON,
        nullable=False,
        comment="List of section objects with content, lists, and tables"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
class CertificationLabel(Base):
    """
    Certification Label Model - Visual Marking Requirements
    
    Stores high-res images and precise usage rules for certification marks
    (FCC ID, CE, RCM, etc).
    """
    __tablename__ = "global_certification_labels"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique identifier"
    )
    
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Label name (e.g., 'FCC Label', 'CE Mark')"
    )
    
    authority = Column(
        String(100),
        nullable=False,
        comment="Issuing authority (e.g., 'FCC', 'European Commission')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="General description of the label"
    )
    
    # Store requirements as JSON for flexibility
    # Example: {"min_height": "5mm", "clear_space": "2mm", "color": "Black on White"}
    requirements = Column(
        JSON,
        nullable=True,
        comment="Structured requirements (min_size, clear_space, etc)"
    )
    
    image_url = Column(
        String(255),
        nullable=True,
        comment="URL to high-quality raster image (PNG/JPG)"
    )
    
    vector_url = Column(
        String(255),
        nullable=True,
        comment="URL to vector file (SVG/EPS) if available"
    )
    
    # Optional link to country if specific to one
    country_id = Column(
        Integer, 
        ForeignKey("global_countries.id", ondelete="SET NULL"),
        nullable=True
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

