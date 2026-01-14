"""
Global Data API Endpoints
=========================
CRUD operations for global master data (admin-managed).

Endpoints:
- Technologies: GET, POST, PUT, DELETE /technologies
- Countries: GET, POST, PUT, DELETE /countries
- Certifications: GET, POST, PUT, DELETE /certifications
- Regulatory Matrix: GET, POST, PUT, DELETE /regulatory-matrix

Access Control:
- Currently open (no auth)
- Future: Restricted to admin users only via Keycloak
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.models import global_data as models
from app.schemas.global_data import (
    TechnologyCreate, TechnologyUpdate, TechnologyResponse,
    CountryCreate, CountryUpdate, CountryResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse,
    RegulatoryMatrixCreate, RegulatoryMatrixUpdate, RegulatoryMatrixResponse,
    GlossaryTermResponse, GlossaryTermCreate, GlossaryTermUpdate
)
from app.services.global_data_service import (
    TechnologyService,
    CountryService,
    CertificationService,
    RegulatoryMatrixService
)

router = APIRouter()


# ============================================
# Technology Endpoints
# ============================================

@router.post(
    "/technologies",
    response_model=TechnologyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Technology",
    description="Create a new technology in the global catalog (admin only)"
)
def create_technology(
    technology: TechnologyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new technology.
    
    Example:
        {
            "name": "Wi-Fi 6E",
            "description": "Wi-Fi operating in 6 GHz band"
        }
    """
    return TechnologyService.create_technology(db, technology)


@router.get(
    "/technologies",
    response_model=List[TechnologyResponse],
    summary="List Technologies",
    description="Retrieve all technologies with pagination"
)
def list_technologies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all technologies."""
    return TechnologyService.get_all_technologies(db, skip, limit)


@router.get(
    "/technologies/{technology_id}",
    response_model=TechnologyResponse,
    summary="Get Technology",
    description="Retrieve a specific technology by ID"
)
def get_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Get technology by ID."""
    return TechnologyService.get_technology_by_id(db, technology_id)


@router.put(
    "/technologies/{technology_id}",
    response_model=TechnologyResponse,
    summary="Update Technology",
    description="Update an existing technology (admin only)"
)
def update_technology(
    technology_id: int,
    technology: TechnologyUpdate,
    db: Session = Depends(get_db)
):
    """Update technology."""
    return TechnologyService.update_technology(db, technology_id, technology)


@router.delete(
    "/technologies/{technology_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Technology",
    description="Delete a technology from the catalog (admin only, use with caution)"
)
def delete_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Delete technology."""
    return TechnologyService.delete_technology(db, technology_id)


# ============================================
# Country Endpoints
# ============================================

@router.post(
    "/countries",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Country",
    description="Add a new country to the global catalog (admin only)"
)
def create_country(
    country: CountryCreate,
    db: Session = Depends(get_db)
):
    """Create a new country."""
    return CountryService.create_country(db, country)


@router.get(
    "/countries",
    response_model=List[CountryResponse],
    summary="List Countries",
    description="Retrieve all countries with pagination"
)
def list_countries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all countries."""
    return CountryService.get_all_countries(db, skip, limit)


@router.get(
    "/countries/{country_id}",
    response_model=CountryResponse,
    summary="Get Country",
    description="Retrieve a specific country by ID"
)
def get_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Get country by ID."""
    return CountryService.get_country_by_id(db, country_id)


@router.put(
    "/countries/{country_id}",
    response_model=CountryResponse,
    summary="Update Country",
    description="Update an existing country (admin only)"
)
def update_country(
    country_id: int,
    country: CountryUpdate,
    db: Session = Depends(get_db)
):
    """Update country."""
    return CountryService.update_country(db, country_id, country)


@router.delete(
    "/countries/{country_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Country",
    description="Delete a country from the catalog (admin only)"
)
def delete_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Delete country."""
    return CountryService.delete_country(db, country_id)


# ============================================
# Certification Endpoints
# ============================================

@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Certification",
    description="Add a new certification type to the global catalog (admin only)"
)
def create_certification(
    certification: CertificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new certification."""
    return CertificationService.create_certification(db, certification)


@router.get(
    "/certifications",
    response_model=List[CertificationResponse],
    summary="List Certifications",
    description="Retrieve all certifications with pagination"
)
def list_certifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all certifications."""
    return CertificationService.get_all_certifications(db, skip, limit)


@router.get(
    "/certifications/{certification_id}",
    response_model=CertificationResponse,
    summary="Get Certification",
    description="Retrieve a specific certification by ID"
)
def get_certification(
    certification_id: int,
    db: Session = Depends(get_db)
):
    """Get certification by ID."""
    return CertificationService.get_certification_by_id(db, certification_id)


@router.put(
    "/certifications/{certification_id}",
    response_model=CertificationResponse,
    summary="Update Certification",
    description="Update an existing certification (admin only)"
)
def update_certification(
    certification_id: int,
    certification: CertificationUpdate,
    db: Session = Depends(get_db)
):
    """Update certification."""
    return CertificationService.update_certification(db, certification_id, certification)


@router.delete(
    "/certifications/{certification_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Certification",
    description="Delete a certification from the catalog (admin only)"
)
def delete_certification(
    certification_id: int,
    db: Session = Depends(get_db)
):
    """Delete certification."""
    return CertificationService.delete_certification(db, certification_id)


# ============================================
# Regulatory Matrix Endpoints (THE RULES ENGINE)
# ============================================

@router.post(
    "/regulatory-matrix",
    response_model=RegulatoryMatrixResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Regulatory Rule",
    description="Add a new regulatory rule: Tech + Country → Required Cert (admin only)"
)
def create_regulatory_rule(
    rule: RegulatoryMatrixCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new regulatory rule.
    
    Example:
        {
            "technology_id": 1,    # Wi-Fi 6E
            "country_id": 2,       # India
            "certification_id": 5, # WPC
            "is_mandatory": true,
            "notes": "6 GHz band requires WPC approval"
        }
    """
    return RegulatoryMatrixService.create_rule(db, rule)


@router.get(
    "/regulatory-matrix",
    response_model=List[RegulatoryMatrixResponse],
    summary="List Regulatory Rules",
    description="Retrieve regulatory rules with optional filtering"
)
def list_regulatory_rules(
    technology_id: int = None,
    country_id: int = None,
    certification_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get regulatory rules with optional filters.
    
    Query Parameters:
        - technology_id: Filter by specific technology
        - country_id: Filter by specific country
        - certification_id: Filter by specific certification
    """
    return RegulatoryMatrixService.get_all_rules(
        db, technology_id, country_id, certification_id, skip, limit
    )


@router.get(
    "/regulatory-matrix/{rule_id}",
    response_model=RegulatoryMatrixResponse,
    summary="Get Regulatory Rule",
    description="Retrieve a specific regulatory rule by ID"
)
def get_regulatory_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get regulatory rule by ID."""
    return RegulatoryMatrixService.get_rule_by_id(db, rule_id)


@router.put(
    "/regulatory-matrix/{rule_id}",
    response_model=RegulatoryMatrixResponse,
    summary="Update Regulatory Rule",
    description="Update an existing regulatory rule (admin only)"
)
def update_regulatory_rule(
    rule_id: int,
    rule: RegulatoryMatrixUpdate,
    db: Session = Depends(get_db)
):
    """Update regulatory rule."""
    return RegulatoryMatrixService.update_rule(db, rule_id, rule)


@router.delete(
    "/regulatory-matrix/{rule_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Regulatory Rule",
    description="Delete a regulatory rule (admin only)"
)
def delete_regulatory_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete regulatory rule."""
    return RegulatoryMatrixService.delete_rule(db, rule_id)



# ============================================
# Glossary Endpoints
# ============================================

@router.get("/glossary", response_model=List[GlossaryTermResponse])
def get_glossary_terms(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """
    Get all glossary terms with optional search.
    """
    query = db.query(models.GlossaryTerm)
    
    if search:
        search_lower = search.lower()
        query = query.filter(
            (func.lower(models.GlossaryTerm.term).contains(search_lower)) |
            (func.lower(models.GlossaryTerm.summary).contains(search_lower))
        )
        
    return query.offset(skip).limit(limit).all()

@router.get("/glossary/{term_id}", response_model=GlossaryTermResponse)
def get_glossary_term(
    term_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific glossary term by ID.
    """
    term = db.query(models.GlossaryTerm).filter(models.GlossaryTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Glossary term not found")
    return term

@router.post("/glossary", response_model=GlossaryTermResponse, status_code=status.HTTP_201_CREATED)
def create_glossary_term(
    term: GlossaryTermCreate,
    db: Session = Depends(get_db)
):
    """Create a new glossary term."""
    db_term = models.GlossaryTerm(**term.model_dump())
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

@router.put("/glossary/{term_id}", response_model=GlossaryTermResponse)
def update_glossary_term(
    term_id: str,
    term_update: GlossaryTermUpdate,
    db: Session = Depends(get_db)
):
    """Update a glossary term."""
    db_term = db.query(models.GlossaryTerm).filter(models.GlossaryTerm.id == term_id).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Glossary term not found")
    
    update_data = term_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_term, key, value)
        
    db.commit()
    db.refresh(db_term)
    return db_term

@router.delete("/glossary/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_glossary_term(
    term_id: str,
    db: Session = Depends(get_db)
):
    """Delete a glossary term."""
    db_term = db.query(models.GlossaryTerm).filter(models.GlossaryTerm.id == term_id).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="Glossary term not found")
    
    db.delete(db_term)
    db.commit()


# ============================================
# Certification Label Endpoints
# ============================================
from app.schemas.global_data import (
    CertificationLabelCreate, CertificationLabelUpdate, CertificationLabelResponse
)

@router.get("/labels", response_model=List[CertificationLabelResponse])
def list_certification_labels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all certification labels."""
    return db.query(models.CertificationLabel).offset(skip).limit(limit).all()

@router.post("/labels", response_model=CertificationLabelResponse, status_code=status.HTTP_201_CREATED)
def create_certification_label(
    label: CertificationLabelCreate,
    db: Session = Depends(get_db)
):
    """Create a new certification label."""
    db_label = models.CertificationLabel(**label.model_dump())
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label

@router.get("/labels/{label_id}", response_model=CertificationLabelResponse)
def get_certification_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """Get label by ID."""
    label = db.query(models.CertificationLabel).filter(models.CertificationLabel.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    return label

@router.put("/labels/{label_id}", response_model=CertificationLabelResponse)
def update_certification_label(
    label_id: int,
    label_update: CertificationLabelUpdate,
    db: Session = Depends(get_db)
):
    """Update label."""
    db_label = db.query(models.CertificationLabel).filter(models.CertificationLabel.id == label_id).first()
    if not db_label:
        raise HTTPException(status_code=404, detail="Label not found")
    
    update_data = label_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_label, key, value)
        
    db.commit()
    db.refresh(db_label)
    return db_label

@router.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """Delete label."""
    db_label = db.query(models.CertificationLabel).filter(models.CertificationLabel.id == label_id).first()
    if not db_label:
        raise HTTPException(status_code=404, detail="Label not found")
    
    db.delete(db_label)
    db.commit()

