"""
Compliance Service Module
=========================
Business logic for compliance tracking and gap analysis.

Services in this module:
- Compliance Record CRUD operations
- Gap Analysis (THE CORE FEATURE)
- Document management (MinIO integration)

This is the MOST CRITICAL module - it implements the core business value:
"Tell me what certifications I'm missing for my device in a target country"
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional, Dict
from uuid import UUID
from datetime import date, datetime

from app.models.compliance import ComplianceRecord, ComplianceTask, ComplianceTaskNote
from app.models.device import TenantDevice, DeviceTechMap
from app.models.global_data import Technology, Country, Certification, RegulatoryMatrix
from app.schemas.compliance import (
    ComplianceRecordCreate,
    ComplianceRecordUpdate,
    ComplianceStatus,
    GapAnalysisRequest,
    GapAnalysisResponse,
    GapAnalysisResultItem,
    ComplianceTaskCreate,
    ComplianceTaskUpdate,
    ComplianceTaskNoteCreate,
    TaskStatus
)
from app.services.device_service import DeviceService
from app.services.global_data_service import CountryService, CertificationService
from app.core.minio_client import minio_client


# ============================================
# Compliance Record Service
# ============================================

class ComplianceRecordService:
    """Service class for Compliance Record operations."""
    
    @staticmethod
    def _task_progress(db: Session, record_id: UUID) -> Dict[str, int]:
        """Compute task counts and percent for a record."""
        total = db.query(ComplianceTask).filter(ComplianceTask.record_id == record_id).count()
        done = db.query(ComplianceTask).filter(
            ComplianceTask.record_id == record_id,
            ComplianceTask.status == TaskStatus.DONE.value
        ).count()
        in_progress = db.query(ComplianceTask).filter(
            ComplianceTask.record_id == record_id,
            ComplianceTask.status == TaskStatus.IN_PROGRESS.value
        ).count()
        pending = total - done - in_progress
        percent = int((done / total) * 100) if total > 0 else 0
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "pending": pending,
            "percent": percent
        }
    
    @staticmethod
    def bulk_init_compliance(
        db: Session,
        tenant_id: UUID,
        device_id: UUID,
        target_countries: List[str]
    ) -> dict:
        """
        Automatically initialize compliance records for a device's target countries.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            device_id: Device UUID
            target_countries: List of country ISO codes (or ['ALL'])
            
        Returns:
            dict: Summary of initialized records
        """
        # 1. Get all countries if 'ALL' is specified, else filter by ISO codes
        if 'ALL' in target_countries:
            countries = db.query(Country).all()
        else:
            countries = db.query(Country).filter(Country.iso_code.in_(target_countries)).all()
            
        total_created = 0
        skipped = 0
        
        for country in countries:
            # 2. Run Gap Analysis for each country
            analysis = GapAnalysisService.analyze(
                db, 
                tenant_id, 
                GapAnalysisRequest(device_id=device_id, country_id=country.id)
            )
            
            # 3. Create records for gaps
            for result in analysis.results:
                if result.has_gap:
                    try:
                        record_create = ComplianceRecordCreate(
                            device_id=device_id,
                            country_id=country.id,
                            certification_id=result.certification_id,
                            status=ComplianceStatus.PENDING
                        )
                        ComplianceRecordService.create_record(db, tenant_id, record_create)
                        total_created += 1
                    except HTTPException as e:
                        if e.status_code == status.HTTP_409_CONFLICT:
                            skipped += 1
                        else:
                            raise e
        
        return {
            "device_id": str(device_id),
            "total_countries_processed": len(countries),
            "records_created": total_created,
            "records_skipped_existing": skipped
        }
    
    @staticmethod
    def create_record(
        db: Session,
        tenant_id: UUID,
        record_data: ComplianceRecordCreate
    ) -> ComplianceRecord:
        """
        Create a new compliance record.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID (from JWT token)
            record_data: Compliance record creation data
        
        Returns:
            ComplianceRecord: Created compliance record
        
        Business Logic:
            Typically created when Gap Analysis identifies a missing
            certification. Initial status is PENDING.
        
        Raises:
            HTTPException: If record already exists (409 Conflict)
        """
        try:
            # Verify related entities exist
            DeviceService.get_device_by_id(db, record_data.device_id, tenant_id)
            CountryService.get_country_by_id(db, record_data.country_id)
            CertificationService.get_certification_by_id(db, record_data.certification_id)
            
            # Create record
            record = ComplianceRecord(
                tenant_id=tenant_id,
                **record_data.model_dump()
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Compliance record for this device+country+certification already exists"
            )
    
    @staticmethod
    def get_tenant_records(
        db: Session,
        tenant_id: UUID,
        device_id: Optional[UUID] = None,
        country_id: Optional[int] = None,
        status_filter: Optional[ComplianceStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceRecord]:
        """
        Get compliance records for a tenant with optional filtering.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            device_id: Optional device filter
            country_id: Optional country filter
            status_filter: Optional status filter (PENDING/ACTIVE/EXPIRING/EXPIRED)
            skip: Pagination offset
            limit: Maximum records to return
        
        Returns:
            List[ComplianceRecord]: List of compliance records
        """
        query = db.query(ComplianceRecord)\
            .options(
                joinedload(ComplianceRecord.device),
                joinedload(ComplianceRecord.country),
                joinedload(ComplianceRecord.certification),
            )\
            .filter(
                ComplianceRecord.tenant_id == tenant_id
            )
        
        # Apply optional filters
        if device_id:
            query = query.filter(ComplianceRecord.device_id == device_id)
        if country_id:
            query = query.filter(ComplianceRecord.country_id == country_id)
        if status_filter:
            query = query.filter(ComplianceRecord.status == status_filter.value)
        
        records = query.offset(skip).limit(limit).all()

        # Populate human-friendly names for UI
        for record in records:
            record.device_name = record.device.model_name if record.device else None
            record.country_name = record.country.name if record.country else None
            record.certification_name = record.certification.name if record.certification else None
            progress = ComplianceRecordService._task_progress(db, record.id)
            record.task_progress_percent = progress.get("percent", 0)
            record.task_counts = {
                "total": progress.get("total", 0),
                "done": progress.get("done", 0),
                "in_progress": progress.get("in_progress", 0),
                "pending": progress.get("pending", 0),
            }
        return records
    
    @staticmethod
    def get_record_by_id(
        db: Session,
        record_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceRecord:
        """
        Get a specific compliance record by ID.
        
        Args:
            db: Database session
            record_id: Compliance record UUID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            ComplianceRecord: Compliance record object
        
        Raises:
            HTTPException: If record not found (404)
        """
        query = db.query(ComplianceRecord)\
            .options(
                joinedload(ComplianceRecord.device),
                joinedload(ComplianceRecord.country),
                joinedload(ComplianceRecord.certification),
            )\
            .filter(ComplianceRecord.id == record_id)
        
        # Optional: Verify tenant owns this record
        if tenant_id:
            query = query.filter(ComplianceRecord.tenant_id == tenant_id)
        
        record = query.first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compliance record with ID {record_id} not found"
            )
        
        # Populate human-friendly names for UI
        record.device_name = record.device.model_name if record.device else None
        record.country_name = record.country.name if record.country else None
        record.certification_name = record.certification.name if record.certification else None
        progress = ComplianceRecordService._task_progress(db, record.id)
        record.task_progress_percent = progress.get("percent", 0)
        record.task_counts = {
            "total": progress.get("total", 0),
            "done": progress.get("done", 0),
            "in_progress": progress.get("in_progress", 0),
            "pending": progress.get("pending", 0),
        }
        return record
    
    @staticmethod
    def update_record(
        db: Session,
        record_id: UUID,
        record_data: ComplianceRecordUpdate,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceRecord:
        """
        Update an existing compliance record.
        
        Args:
            db: Database session
            record_id: Compliance record UUID
            record_data: Updated record data
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            ComplianceRecord: Updated compliance record
        
        Business Logic:
            When status changes from PENDING to ACTIVE,
            expiry_date must be provided.
        """
        record = ComplianceRecordService.get_record_by_id(db, record_id, tenant_id)
        
        update_data = record_data.model_dump(exclude_unset=True)
        
        # Track labeling status change
        if "labeling_status" in update_data and update_data["labeling_status"] != record.labeling_status:
            record.labeling_updated_at = datetime.now()
            
        for field, value in update_data.items():
            setattr(record, field, value)
        
        # Validation: ACTIVE status requires expiry_date
        if record.status == ComplianceStatus.ACTIVE.value and not record.expiry_date:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="expiry_date is required when status is ACTIVE"
            )
        
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete_record(
        db: Session,
        record_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> dict:
        """
        Delete a compliance record.
        
        Args:
            db: Database session
            record_id: Compliance record UUID
            tenant_id: Optional tenant ID for isolation check
        
        Returns:
            dict: Success message
        
        Note:
            Also deletes associated document from MinIO if exists.
        """
        record = ComplianceRecordService.get_record_by_id(db, record_id, tenant_id)
        
        # Delete document from MinIO if exists
        if record.document_path:
            minio_client.delete_file(record.document_path)
        
        db.delete(record)
        db.commit()
        return {"message": "Compliance record deleted successfully"}


# ============================================
# Gap Analysis Service (CORE FEATURE)
# ============================================

class GapAnalysisService:
    """
    Service class for Gap Analysis operations.
    
    This is THE MOST IMPORTANT service - implements the core business value.
    
    Purpose:
        Answer the question: "What certifications does my device need
        for a specific target country?"
    
    Algorithm:
        1. Get device technologies from device_tech_map
        2. Query regulatory_matrix for (technologies, country) → required certifications
        3. Check existing compliance_records for this device + country
        4. Compare: Required vs. Existing = GAP
        5. Return detailed analysis with status of each certification
    """
    
    @staticmethod
    def analyze(
        db: Session,
        tenant_id: UUID,
        analysis_request: GapAnalysisRequest
    ) -> GapAnalysisResponse:
        """
        Perform Gap Analysis for a device targeting a specific country.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID (from JWT token)
            analysis_request: Device ID + Country ID
        
        Returns:
            GapAnalysisResponse: Detailed analysis with gaps and status
        
        Business Logic:
            This is the "Tool" that users interact with:
            - Step 1: User registers device with technologies
            - Step 2: User runs Gap Analysis for target country (THIS)
            - Step 3: System shows missing certifications
            - Step 4: User uploads certificates
        
        Example:
            Input: device_id="abc", country_id=2 (India)
            Device has: Wi-Fi 6E, Bluetooth
            
            Output:
            {
                "total_required": 2,
                "gaps_found": 1,
                "results": [
                    {
                        "certification_name": "WPC",
                        "technology": "Wi-Fi 6E",
                        "has_gap": true  # MISSING!
                    },
                    {
                        "certification_name": "BIS",
                        "technology": "Bluetooth",
                        "has_gap": false,  # Already have it
                        "status": "ACTIVE"
                    }
                ]
            }
        """
        device_id = analysis_request.device_id
        country_id = analysis_request.country_id
        
        # Step 1: Verify device exists and belongs to tenant
        device = DeviceService.get_device_by_id(db, device_id, tenant_id)
        
        # Step 2: Verify country exists
        CountryService.get_country_by_id(db, country_id)
        
        # Step 3: Get all technologies for this device
        device_tech_ids = db.query(DeviceTechMap.technology_id)\
            .filter(DeviceTechMap.device_id == device_id)\
            .all()
        tech_ids = [t[0] for t in device_tech_ids]
        
        if not tech_ids:
            # Device has no technologies - no certifications required
            return GapAnalysisResponse(
                device_id=device_id,
                country_id=country_id,
                total_required=0,
                gaps_found=0,
                results=[]
            )
        
        # Step 4: Query regulatory_matrix for required certifications
        # Find all rules where:
        # - technology_id IN (device_technologies)
        # - country_id = target_country
        # - is_mandatory = True
        required_rules = db.query(RegulatoryMatrix)\
            .join(Technology, Technology.id == RegulatoryMatrix.technology_id)\
            .join(Certification, Certification.id == RegulatoryMatrix.certification_id)\
            .filter(
                RegulatoryMatrix.technology_id.in_(tech_ids),
                RegulatoryMatrix.country_id == country_id,
                RegulatoryMatrix.is_mandatory == True
            )\
            .all()
        
        # Step 5: Get existing compliance records for this device + country
        existing_records = db.query(ComplianceRecord)\
            .filter(
                ComplianceRecord.device_id == device_id,
                ComplianceRecord.country_id == country_id,
                ComplianceRecord.tenant_id == tenant_id
            )\
            .all()
        
        # Create a lookup map: certification_id → compliance_record
        existing_certs = {
            record.certification_id: record
            for record in existing_records
        }
        
        # Step 6: Build analysis results
        results = []
        
        # Track unique certs for counting
        required_cert_ids = set()
        missing_cert_ids = set()
        
        for rule in required_rules:
            cert_id = rule.certification_id
            required_cert_ids.add(cert_id)
            
            if cert_id in existing_certs:
                # Certification exists - no gap
                record = existing_certs[cert_id]
                
                # Count open tasks (TODO or IN_PROGRESS)
                open_tasks = db.query(ComplianceTask).filter(
                    ComplianceTask.record_id == record.id,
                    ComplianceTask.status.in_([TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]),
                    ComplianceTask.title == "Compliance Testing"
                ).count()
                
                results.append(GapAnalysisResultItem(
                    certification_id=cert_id,
                    certification_name=rule.certification.name,
                    technology=rule.technology.name,
                    has_gap=False,
                    status=record.status,
                    expiry_date=record.expiry_date,
                    compliance_record_id=record.id,
                    branding_image_url=rule.certification.branding_image_url,
                    labeling_requirements=rule.certification.labeling_requirements,
                    open_tasks_count=open_tasks
                ))
            else:
                # Certification missing - GAP FOUND!
                missing_cert_ids.add(cert_id)
                results.append(GapAnalysisResultItem(
                    certification_id=cert_id,
                    certification_name=rule.certification.name,
                    technology=rule.technology.name,
                    has_gap=True,
                    status="MISSING",
                    expiry_date=None,
                    compliance_record_id=None,
                    branding_image_url=rule.certification.branding_image_url,
                    labeling_requirements=rule.certification.labeling_requirements,
                    open_tasks_count=0
                ))
        
        # Step 7: Return complete analysis
        # COUNTing Logic: Use unique certifications (Papers), not rules (Line Items)
        return GapAnalysisResponse(
            device_id=device_id,
            country_id=country_id,
            total_required=len(required_cert_ids),
            gaps_found=len(missing_cert_ids),
            results=results
        )


# ============================================
# Document Management Service
# ============================================

class DocumentService:
    """Service class for certificate document operations (MinIO)."""
    
    @staticmethod
    async def upload_document(
        db: Session,
        compliance_record_id: UUID,
        file: UploadFile,
        doc_type: str = "certificate",  # "certificate" or "test_report"
        tenant_id: Optional[UUID] = None
    ) -> dict:
        """
        Upload a document (certificate or test report) to MinIO.
        """
        # Step 1: Verify record exists and belongs to tenant
        record = ComplianceRecordService.get_record_by_id(
            db,
            compliance_record_id,
            tenant_id
        )
        
        # Step 2: Read file content
        file_content = await file.read()
        
        # Step 3: Generate object path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        folder = "certificates"
        if doc_type == "test_report":
            folder = "test_reports"
        elif doc_type == "label_picture":
            folder = "label_pictures"
            
        object_name = f"{folder}/{record.tenant_id}/{record.device_id}/{timestamp}_{file.filename}"
        
        # Step 4: Upload to MinIO
        minio_client.upload_file(
            file_data=file_content,
            object_name=object_name,
            content_type=file.content_type or "application/pdf"
        )
        
        # Step 5: Update compliance record
        if doc_type == "certificate":
            record.document_path = object_name
            record.document_filename = file.filename
            record.document_mime_type = file.content_type
        elif doc_type == "test_report":
            record.test_report_path = object_name
            record.test_report_filename = file.filename
            record.test_report_mime_type = file.content_type
        elif doc_type == "label_picture":
            record.labeling_picture_path = object_name
            record.labeling_picture_filename = file.filename
            record.labeling_picture_mime_type = file.content_type
            
        db.commit()
        
        # Step 6: Generate presigned URL for download
        download_url = minio_client.get_presigned_url(object_name, expires_seconds=3600)
        
        return {
            "compliance_record_id": compliance_record_id,
            "document_path": object_name,
            "document_filename": file.filename,
            "document_url": download_url,
            "doc_type": doc_type,
            "message": f"{doc_type.replace('_', ' ').title()} uploaded successfully"
        }
    
    @staticmethod
    def get_download_url(
        db: Session,
        compliance_record_id: UUID,
        doc_type: str = "certificate",
        tenant_id: Optional[UUID] = None,
        expires_seconds: int = 3600
    ) -> dict:
        """
        Get a presigned download URL for a document.
        """
        # Verify record exists
        record = ComplianceRecordService.get_record_by_id(
            db,
            compliance_record_id,
            tenant_id
        )
        
        path = None
        if doc_type == "certificate":
            path = record.document_path
        elif doc_type == "test_report":
            path = record.test_report_path
        elif doc_type == "label_picture":
            path = record.labeling_picture_path
            
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {doc_type.replace('_', ' ')} uploaded for this record"
            )
        
        # Generate presigned URL
        download_url = minio_client.get_presigned_url(
            path,
            expires_seconds=expires_seconds
        )
        
        return {
            "document_url": download_url,
            "expires_in": expires_seconds,
            "doc_type": doc_type
        }


# ============================================
# Task Workflow Service
# ============================================


class ComplianceTaskService:
    """Service layer for compliance tasks and notes."""

    @staticmethod
    def _ensure_record_tenant(db: Session, record_id: UUID, tenant_id: Optional[UUID]):
        # Reuse record fetch to enforce tenant check
        return ComplianceRecordService.get_record_by_id(db, record_id, tenant_id)

    @staticmethod
    def list_tasks(db: Session, record_id: UUID, tenant_id: Optional[UUID] = None) -> List[ComplianceTask]:
        ComplianceTaskService._ensure_record_tenant(db, record_id, tenant_id)
        return db.query(ComplianceTask).filter(ComplianceTask.record_id == record_id).order_by(ComplianceTask.created_at.asc()).all()

    @staticmethod
    def create_task(
        db: Session,
        record_id: UUID,
        task_data: ComplianceTaskCreate,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceTask:
        ComplianceTaskService._ensure_record_tenant(db, record_id, tenant_id)
        task = ComplianceTask(
            record_id=record_id,
            **task_data.model_dump()
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(
        db: Session,
        task_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceTask:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        ComplianceTaskService._ensure_record_tenant(db, task.record_id, tenant_id)
        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: UUID,
        task_data: ComplianceTaskUpdate,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceTask:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        ComplianceTaskService._ensure_record_tenant(db, task.record_id, tenant_id)

        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def add_note(
        db: Session,
        task_id: UUID,
        note_data: ComplianceTaskNoteCreate,
        tenant_id: Optional[UUID] = None
    ) -> ComplianceTaskNote:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        ComplianceTaskService._ensure_record_tenant(db, task.record_id, tenant_id)

        note = ComplianceTaskNote(
            task_id=task_id,
            **note_data.model_dump()
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def list_notes(
        db: Session,
        task_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> List[ComplianceTaskNote]:
        task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        ComplianceTaskService._ensure_record_tenant(db, task.record_id, tenant_id)
        return db.query(ComplianceTaskNote).filter(ComplianceTaskNote.task_id == task_id).order_by(ComplianceTaskNote.created_at.desc()).all()


