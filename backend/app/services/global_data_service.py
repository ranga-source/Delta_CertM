"""
Global Data Service Module
==========================
Business logic for managing global master data (admin operations).

Services in this module:
- Technology CRUD operations
- Country CRUD operations
- Certification CRUD operations
- Regulatory Matrix CRUD operations

All operations in this module should be restricted to admin users.
(Note: Auth will be added with Keycloak integration)
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.global_data import Technology, Country, Certification, RegulatoryMatrix
from app.schemas.global_data import (
    TechnologyCreate, TechnologyUpdate,
    CountryCreate, CountryUpdate,
    CertificationCreate, CertificationUpdate,
    RegulatoryMatrixCreate, RegulatoryMatrixUpdate
)


# ============================================
# Technology Service
# ============================================

class TechnologyService:
    """Service class for Technology operations."""
    
    @staticmethod
    def create_technology(db: Session, tech_data: TechnologyCreate) -> Technology:
        """
        Create a new technology in the global catalog.
        
        Args:
            db: Database session
            tech_data: Technology creation data
        
        Returns:
            Technology: Created technology object
        
        Raises:
            HTTPException: If technology name already exists (409 Conflict)
        """
        try:
            # Create new technology instance
            technology = Technology(**tech_data.model_dump())
            
            # Add to database
            db.add(technology)
            db.commit()
            db.refresh(technology)
            
            return technology
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Technology with name '{tech_data.name}' already exists"
            )
    
    @staticmethod
    def get_all_technologies(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Technology]:
        """
        Retrieve all technologies with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
        
        Returns:
            List[Technology]: List of technology objects
        """
        return db.query(Technology).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_technology_by_id(db: Session, tech_id: int) -> Technology:
        """
        Retrieve a specific technology by ID.
        
        Args:
            db: Database session
            tech_id: Technology ID
        
        Returns:
            Technology: Technology object
        
        Raises:
            HTTPException: If technology not found (404)
        """
        technology = db.query(Technology).filter(Technology.id == tech_id).first()
        
        if not technology:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Technology with ID {tech_id} not found"
            )
        
        return technology
    
    @staticmethod
    def update_technology(
        db: Session,
        tech_id: int,
        tech_data: TechnologyUpdate
    ) -> Technology:
        """
        Update an existing technology.
        
        Args:
            db: Database session
            tech_id: Technology ID to update
            tech_data: Updated technology data
        
        Returns:
            Technology: Updated technology object
        
        Raises:
            HTTPException: If technology not found (404) or name conflict (409)
        """
        # Get existing technology
        technology = TechnologyService.get_technology_by_id(db, tech_id)
        
        try:
            # Update fields (only if provided)
            update_data = tech_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(technology, field, value)
            
            db.commit()
            db.refresh(technology)
            
            return technology
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Technology with name '{tech_data.name}' already exists"
            )
    
    @staticmethod
    def delete_technology(db: Session, tech_id: int) -> dict:
        """
        Delete a technology from the catalog.
        
        Args:
            db: Database session
            tech_id: Technology ID to delete
        
        Returns:
            dict: Success message
        
        Raises:
            HTTPException: If technology not found (404)
        
        Note:
            Cascade delete will remove related regulatory_matrix entries
            and device_tech_map entries. Use with caution!
        """
        technology = TechnologyService.get_technology_by_id(db, tech_id)
        
        db.delete(technology)
        db.commit()
        
        return {"message": f"Technology '{technology.name}' deleted successfully"}


# ============================================
# Country Service
# ============================================

class CountryService:
    """Service class for Country operations."""
    
    @staticmethod
    def create_country(db: Session, country_data: CountryCreate) -> Country:
        """Create a new country in the global catalog."""
        try:
            country = Country(**country_data.model_dump())
            db.add(country)
            db.commit()
            db.refresh(country)
            return country
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Country with ISO code '{country_data.iso_code}' already exists"
            )
    
    @staticmethod
    def get_all_countries(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Country]:
        """Retrieve all countries with pagination."""
        return db.query(Country).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_country_by_id(db: Session, country_id: int) -> Country:
        """Retrieve a specific country by ID."""
        country = db.query(Country).filter(Country.id == country_id).first()
        
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with ID {country_id} not found"
            )
        
        return country
    
    @staticmethod
    def update_country(
        db: Session,
        country_id: int,
        country_data: CountryUpdate
    ) -> Country:
        """Update an existing country."""
        country = CountryService.get_country_by_id(db, country_id)
        
        try:
            update_data = country_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(country, field, value)
            
            db.commit()
            db.refresh(country)
            return country
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Country with this ISO code already exists"
            )
    
    @staticmethod
    def delete_country(db: Session, country_id: int) -> dict:
        """Delete a country from the catalog."""
        country = CountryService.get_country_by_id(db, country_id)
        db.delete(country)
        db.commit()
        return {"message": f"Country '{country.name}' deleted successfully"}


# ============================================
# Certification Service
# ============================================

class CertificationService:
    """Service class for Certification operations."""
    
    @staticmethod
    def create_certification(db: Session, cert_data: CertificationCreate) -> Certification:
        """Create a new certification in the global catalog."""
        try:
            certification = Certification(**cert_data.model_dump())
            db.add(certification)
            db.commit()
            db.refresh(certification)
            return certification
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Certification with name '{cert_data.name}' already exists"
            )
    
    @staticmethod
    def get_all_certifications(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Certification]:
        """Retrieve all certifications with pagination."""
        return db.query(Certification).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_certification_by_id(db: Session, cert_id: int) -> Certification:
        """Retrieve a specific certification by ID."""
        certification = db.query(Certification).filter(Certification.id == cert_id).first()
        
        if not certification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certification with ID {cert_id} not found"
            )
        
        return certification
    
    @staticmethod
    def update_certification(
        db: Session,
        cert_id: int,
        cert_data: CertificationUpdate
    ) -> Certification:
        """Update an existing certification."""
        certification = CertificationService.get_certification_by_id(db, cert_id)
        
        try:
            update_data = cert_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(certification, field, value)
            
            db.commit()
            db.refresh(certification)
            return certification
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Certification with this name already exists"
            )
    
    @staticmethod
    def delete_certification(db: Session, cert_id: int) -> dict:
        """Delete a certification from the catalog."""
        certification = CertificationService.get_certification_by_id(db, cert_id)
        db.delete(certification)
        db.commit()
        return {"message": f"Certification '{certification.name}' deleted successfully"}


# ============================================
# Regulatory Matrix Service
# ============================================

class RegulatoryMatrixService:
    """
    Service class for Regulatory Matrix operations.
    This is the CORE LOGIC ENGINE for compliance requirements.
    """
    
    @staticmethod
    def create_rule(db: Session, rule_data: RegulatoryMatrixCreate) -> RegulatoryMatrix:
        """
        Create a new regulatory rule.
        
        Example:
            "Wi-Fi 6E in India requires WPC certification"
            technology_id=1, country_id=2, certification_id=5
        """
        try:
            # Verify related entities exist
            TechnologyService.get_technology_by_id(db, rule_data.technology_id)
            CountryService.get_country_by_id(db, rule_data.country_id)
            CertificationService.get_certification_by_id(db, rule_data.certification_id)
            
            # Create rule
            rule = RegulatoryMatrix(**rule_data.model_dump())
            db.add(rule)
            db.commit()
            db.refresh(rule)
            return rule
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This regulatory rule already exists"
            )
    
    @staticmethod
    def get_all_rules(
        db: Session,
        technology_id: Optional[int] = None,
        country_id: Optional[int] = None,
        certification_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RegulatoryMatrix]:
        """
        Retrieve regulatory rules with optional filtering.
        
        Filters:
            - technology_id: Get rules for specific technology
            - country_id: Get rules for specific country
            - certification_id: Get rules for specific certification
        """
        query = db.query(RegulatoryMatrix)
        
        # Apply filters if provided
        if technology_id:
            query = query.filter(RegulatoryMatrix.technology_id == technology_id)
        if country_id:
            query = query.filter(RegulatoryMatrix.country_id == country_id)
        if certification_id:
            query = query.filter(RegulatoryMatrix.certification_id == certification_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_rule_by_id(db: Session, rule_id: int) -> RegulatoryMatrix:
        """Retrieve a specific regulatory rule by ID."""
        rule = db.query(RegulatoryMatrix).filter(RegulatoryMatrix.id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regulatory rule with ID {rule_id} not found"
            )
        
        return rule
    
    @staticmethod
    def update_rule(
        db: Session,
        rule_id: int,
        rule_data: RegulatoryMatrixUpdate
    ) -> RegulatoryMatrix:
        """Update an existing regulatory rule."""
        rule = RegulatoryMatrixService.get_rule_by_id(db, rule_id)
        
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(db: Session, rule_id: int) -> dict:
        """Delete a regulatory rule."""
        rule = RegulatoryMatrixService.get_rule_by_id(db, rule_id)
        db.delete(rule)
        db.commit()
        return {"message": "Regulatory rule deleted successfully"}


