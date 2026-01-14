"""
Compliance API Endpoints
=======================
Compliance tracking, gap analysis, and document management.

Endpoints:
- Compliance Records: GET, POST, PUT, DELETE /records
- Gap Analysis: POST /gap-analysis (THE CORE FEATURE)
- Documents: POST, GET /records/{id}/document

This module implements the MOST CRITICAL business feature:
"Tell me what certifications I'm missing for my device in a target country"
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.compliance import (
    ComplianceRecordCreate,
    ComplianceRecordUpdate,
    ComplianceRecordResponse,
    ComplianceStatus,
    GapAnalysisRequest,
    GapAnalysisResponse,
    DocumentUploadResponse,
    DocumentDownloadResponse,
    ComplianceTaskCreate,
    ComplianceTaskUpdate,
    ComplianceTaskResponse,
    ComplianceTaskNoteCreate,
    ComplianceTaskNoteResponse
)
from app.services.compliance_service import (
    ComplianceRecordService,
    GapAnalysisService,
    DocumentService,
    ComplianceTaskService
)

router = APIRouter()


# ============================================
# Gap Analysis Endpoint (THE CORE FEATURE)
# ============================================

@router.post(
    "/gap-analysis",
    response_model=GapAnalysisResponse,
    summary="Perform Gap Analysis",
    description="THE CORE FEATURE: Identify missing certifications for a device in a target country"
)
def perform_gap_analysis(
    analysis_request: GapAnalysisRequest,
    tenant_id: UUID = Query(..., description="Tenant UUID (future: from JWT token)"),
    db: Session = Depends(get_db)
):
    """
    Perform Gap Analysis - THE MOST IMPORTANT ENDPOINT.
    
    Purpose:
        Answer: "What certifications does my device need for [country]?"
    
    User Journey:
        1. User creates device with technologies
        2. User calls this endpoint with device_id + target country_id
        3. System returns:
            - List of ALL required certifications
            - Which ones are MISSING (gaps)
            - Status of existing certifications
    
    Request Body:
        {
            "device_id": "123e4567-e89b-12d3-a456-426614174000",
            "country_id": 2  # India
        }
    
    Response Example:
        {
            "device_id": "123e4567...",
            "country_id": 2,
            "total_required": 3,
            "gaps_found": 1,
            "results": [
                {
                    "certification_name": "WPC",
                    "technology": "Wi-Fi 6E",
                    "has_gap": true,  # MISSING - needs action!
                    "status": "MISSING"
                },
                {
                    "certification_name": "BIS",
                    "technology": "Bluetooth",
                    "has_gap": false,  # Already have it
                    "status": "ACTIVE",
                    "expiry_date": "2025-12-31"
                },
                {
                    "certification_name": "TEC",
                    "technology": "5G Cellular",
                    "has_gap": false,
                    "status": "EXPIRING",  # Warning: approaching expiry!
                    "expiry_date": "2024-03-15"
                }
            ]
        }
    
    Business Logic:
        1. Get device technologies (Wi-Fi, Bluetooth, GPS, etc.)
        2. Query regulatory_matrix: (technologies + country) → required certs
        3. Check existing compliance_records
        4. Compare: Required vs. Existing = GAPS
        5. Return detailed analysis
    """
    return GapAnalysisService.analyze(db, tenant_id, analysis_request)


# ============================================
# Compliance Record Endpoints
# ============================================

@router.post(
    "/records",
    response_model=ComplianceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Compliance Record",
    description="Create a new compliance record (usually from Gap Analysis results)"
)
def create_compliance_record(
    record: ComplianceRecordCreate,
    tenant_id: UUID = Query(..., description="Tenant UUID (future: from JWT token)"),
    db: Session = Depends(get_db)
):
    """
    Create a compliance record.
    
    Typically created when Gap Analysis identifies a missing certification.
    Initial status is usually PENDING.
    
    Example:
        {
            "device_id": "123e4567...",
            "country_id": 2,
            "certification_id": 5,
            "status": "PENDING"
        }
    """
    return ComplianceRecordService.create_record(db, tenant_id, record)


@router.get(
    "/records",
    response_model=List[ComplianceRecordResponse],
    summary="List Compliance Records",
    description="Retrieve compliance records with optional filtering"
)
def list_compliance_records(
    tenant_id: UUID = Query(..., description="Tenant UUID (future: from JWT token)"),
    device_id: Optional[UUID] = None,
    country_id: Optional[int] = None,
    status_filter: Optional[ComplianceStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get compliance records with optional filters.
    
    Query Parameters:
        - tenant_id: Tenant UUID (data isolation)
        - device_id: Filter by specific device
        - country_id: Filter by target country
        - status_filter: Filter by status (PENDING/ACTIVE/EXPIRING/EXPIRED)
        - skip: Pagination offset
        - limit: Maximum records to return
    
    Use Cases:
        - Get all EXPIRED certificates: status_filter=EXPIRED
        - Get all records for a device: device_id=xxx
        - Get all certifications for India: country_id=2
    """
    return ComplianceRecordService.get_tenant_records(
        db, tenant_id, device_id, country_id, status_filter, skip, limit
    )


@router.get(
    "/records/{record_id}",
    response_model=ComplianceRecordResponse,
    summary="Get Compliance Record",
    description="Retrieve a specific compliance record by ID"
)
def get_compliance_record(
    record_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """Get compliance record by ID."""
    return ComplianceRecordService.get_record_by_id(db, record_id, tenant_id)


@router.put(
    "/records/{record_id}",
    response_model=ComplianceRecordResponse,
    summary="Update Compliance Record",
    description="Update compliance record (e.g., change status, add expiry date)"
)
def update_compliance_record(
    record_id: UUID,
    record: ComplianceRecordUpdate,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Update compliance record.
    
    Common use cases:
        - Certificate obtained: status = PENDING → ACTIVE, add expiry_date
        - Certificate renewed: update expiry_date
        - Add certificate number: certificate_number = "FCC123456"
    
    Example:
        {
            "status": "ACTIVE",
            "expiry_date": "2025-12-31",
            "certificate_number": "WPC/2024/12345"
        }
    """
    return ComplianceRecordService.update_record(db, record_id, record, tenant_id)


@router.delete(
    "/records/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Compliance Record",
    description="Delete a compliance record and associated document"
)
def delete_compliance_record(
    record_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Delete compliance record.
    
    Note: Also deletes associated certificate document from MinIO if exists.
    """
    return ComplianceRecordService.delete_record(db, record_id, tenant_id)


# ============================================
# Document Management Endpoints (MinIO)
# ============================================

@router.post(
    "/records/{record_id}/document",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="Upload a certificate or test report to MinIO storage"
)
async def upload_document(
    record_id: UUID,
    file: UploadFile = File(..., description="PDF or Image file"),
    doc_type: str = Query("certificate", enum=["certificate", "test_report", "label_picture"], description="Document type"),
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    """
    Upload compliance document.
    """
    return await DocumentService.upload_document(db, record_id, file, doc_type, tenant_id)


@router.get(
    "/records/{record_id}/document",
    response_model=DocumentDownloadResponse,
    summary="Get Document Download URL",
    description="Generate presigned URL for document download"
)
def get_document_download_url(
    record_id: UUID,
    doc_type: str = Query("certificate", enum=["certificate", "test_report", "label_picture"], description="Document type"),
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    expires_in: int = Query(3600, description="URL validity in seconds (default: 1 hour)"),
    db: Session = Depends(get_db)
):
    """
    Get presigned download URL for document.
    """
    return DocumentService.get_download_url(db, record_id, doc_type, tenant_id, expires_in)


# ============================================
# Task Workflow Endpoints
# ============================================


@router.get(
    "/records/{record_id}/tasks",
    response_model=List[ComplianceTaskResponse],
    summary="List tasks for a compliance record"
)
def list_tasks(
    record_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.list_tasks(db, record_id, tenant_id)


@router.post(
    "/records/{record_id}/tasks",
    response_model=ComplianceTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task for a compliance record"
)
def create_task(
    record_id: UUID,
    task: ComplianceTaskCreate,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.create_task(db, record_id, task, tenant_id)


@router.get(
    "/tasks/{task_id}",
    response_model=ComplianceTaskResponse,
    summary="Get a compliance task"
)
def get_task(
    task_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.get_task(db, task_id, tenant_id)


@router.put(
    "/tasks/{task_id}",
    response_model=ComplianceTaskResponse,
    summary="Update a compliance task"
)
def update_task(
    task_id: UUID,
    task: ComplianceTaskUpdate,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.update_task(db, task_id, task, tenant_id)


@router.get(
    "/tasks/{task_id}/notes",
    response_model=List[ComplianceTaskNoteResponse],
    summary="List notes for a task"
)
def list_task_notes(
    task_id: UUID,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.list_notes(db, task_id, tenant_id)


@router.post(
    "/tasks/{task_id}/notes",
    response_model=ComplianceTaskNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a worknote to a task"
)
def add_task_note(
    task_id: UUID,
    note: ComplianceTaskNoteCreate,
    tenant_id: UUID = Query(None, description="Optional tenant ID for isolation check"),
    db: Session = Depends(get_db)
):
    return ComplianceTaskService.add_note(db, task_id, note, tenant_id)


