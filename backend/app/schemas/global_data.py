"""
Global Data Pydantic Schemas
============================
Request/Response schemas for global master data (admin-managed).

Schema Patterns:
- *Base: Shared fields for create/update
- *Create: For POST requests (no ID)
- *Update: For PUT/PATCH requests (optional fields)
- *Response: For API responses (includes ID, timestamps, relationships)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================
# Technology Schemas
# ============================================

class TechnologyBase(BaseModel):
    """
    Base schema for Technology with shared fields.
    Used as foundation for Create/Update schemas.
    """
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Technology name (e.g., 'Wi-Fi 6E', 'Bluetooth 5.3')",
        examples=["Wi-Fi 6E", "Bluetooth 5.3", "GPS/GNSS"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the technology",
        examples=["Wi-Fi operating in 6 GHz band, requires WPC approval in India"]
    )


class TechnologyCreate(TechnologyBase):
    """
    Schema for creating a new Technology.
    Used in POST /api/v1/global/technologies
    """
    pass


class TechnologyUpdate(BaseModel):
    """
    Schema for updating an existing Technology.
    Used in PUT/PATCH /api/v1/global/technologies/{id}
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class TechnologyResponse(TechnologyBase):
    """
    Schema for Technology API responses.
    Includes ID and timestamps.
    """
    id: int = Field(..., description="Unique technology ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Country Schemas
# ============================================

class CountryBase(BaseModel):
    """Base schema for Country with shared fields."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full country name",
        examples=["United States", "India", "Germany"]
    )
    iso_code: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 3166-1 alpha-3 country code",
        examples=["USA", "IND", "DEU"]
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed country profile (voltage, plugs, label info)",
        examples=[{"voltage": "120V", "frequency": "60Hz", "plug_types": ["A", "B"]}]
    )


class CountryCreate(CountryBase):
    """
    Schema for creating a new Country.
    Used in POST /api/v1/global/countries
    """
    pass


class CountryUpdate(BaseModel):
    """
    Schema for updating an existing Country.
    All fields optional for partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    iso_code: Optional[str] = Field(None, min_length=3, max_length=3)
    details: Optional[Dict[str, Any]] = None


class CountryResponse(CountryBase):
    """Schema for Country API responses."""
    id: int = Field(..., description="Unique country ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Certification Schemas
# ============================================

class CertificationBase(BaseModel):
    """Base schema for Certification with shared fields."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Certification name/code",
        examples=["FCC Part 15", "WPC", "CE", "TELEC"]
    )
    authority_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Regulatory body that issues this certification",
        examples=["Federal Communications Commission", "Ministry of Communications"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of certification requirements and coverage"
    )
    branding_image_url: Optional[str] = Field(
        None,
        description="URL to the official certification logo/mark"
    )
    labeling_requirements: Optional[str] = Field(
        None,
        description="Specific placement requirements for the label"
    )


class CertificationCreate(CertificationBase):
    """
    Schema for creating a new Certification.
    Used in POST /api/v1/global/certifications
    """
    pass


class CertificationUpdate(BaseModel):
    """Schema for updating an existing Certification."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    authority_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    branding_image_url: Optional[str] = None
    labeling_requirements: Optional[str] = None


class CertificationResponse(CertificationBase):
    """Schema for Certification API responses."""
    id: int = Field(..., description="Unique certification ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Regulatory Matrix Schemas
# ============================================

class RegulatoryMatrixBase(BaseModel):
    """
    Base schema for Regulatory Matrix rules.
    This is the core logic: Tech + Country = Required Cert
    """
    technology_id: int = Field(
        ...,
        description="Technology being regulated",
        examples=[1, 2, 3]
    )
    country_id: int = Field(
        ...,
        description="Country where certification is required",
        examples=[1, 2, 3]
    )
    certification_id: int = Field(
        ...,
        description="Required certification",
        examples=[1, 2, 3]
    )
    is_mandatory: bool = Field(
        True,
        description="True = Mandatory for market access, False = Optional/Recommended"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional regulatory notes or special conditions"
    )


class RegulatoryMatrixCreate(RegulatoryMatrixBase):
    """
    Schema for creating a new Regulatory Matrix rule.
    Used in POST /api/v1/global/regulatory-matrix
    
    Example:
        {
            "technology_id": 1,  # Wi-Fi 6E
            "country_id": 2,      # India
            "certification_id": 5, # WPC
            "is_mandatory": true,
            "notes": "6 GHz band requires special approval"
        }
    """
    pass


class RegulatoryMatrixUpdate(BaseModel):
    """Schema for updating an existing Regulatory Matrix rule."""
    is_mandatory: Optional[bool] = None
    notes: Optional[str] = None


class RegulatoryMatrixResponse(RegulatoryMatrixBase):
    """
    Schema for Regulatory Matrix API responses.
    Includes expanded information about related entities.
    """
    id: int = Field(..., description="Unique rule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Optional: Include related entity names (useful for UI)
    technology_name: Optional[str] = Field(None, description="Technology name")
    country_name: Optional[str] = Field(None, description="Country name")
    certification_name: Optional[str] = Field(None, description="Certification name")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Glossary Schemas
# ============================================

class GlossaryTermBase(BaseModel):
    """Base schema for Glossary Term."""
    term: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., max_length=50)
    region: Optional[str] = Field(None, max_length=50)
    summary: str
    sections: List[Dict[str, Any]]  # Rich content structure

class GlossaryTermCreate(GlossaryTermBase):
    """Schema for creating a new Glossary Term (slug ID is manual)."""
    id: str = Field(..., min_length=1, max_length=50, pattern="^[a-z0-9-]+$")

class GlossaryTermUpdate(BaseModel):
    """Schema for updating a Glossary Term."""
    term: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    summary: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None

class GlossaryTermResponse(GlossaryTermBase):
    """Schema for Glossary Term response."""
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Certification Label Schemas
# ============================================

class CertificationLabelBase(BaseModel):
    name: str = Field(..., max_length=100)
    authority: str = Field(..., max_length=100)
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    vector_url: Optional[str] = None
    country_id: Optional[int] = None

class CertificationLabelCreate(CertificationLabelBase):
    pass

class CertificationLabelUpdate(BaseModel):
    name: Optional[str] = None
    authority: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    vector_url: Optional[str] = None
    country_id: Optional[int] = None

class CertificationLabelResponse(CertificationLabelBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



