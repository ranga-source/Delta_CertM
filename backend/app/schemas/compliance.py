"""
Compliance Pydantic Schemas
===========================
Request/Response schemas for compliance tracking and gap analysis.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import date, datetime
from uuid import UUID
from enum import Enum


# ============================================
# Compliance Status Enum
# ============================================

class ComplianceStatus(str, Enum):
    """
    Enumeration of compliance status values.
    Ensures type safety and validation.
    """
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"


class TaskStatus(str, Enum):
    """Task workflow status."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class LabelingStatus(str, Enum):
    """Labeling status."""
    PENDING = "PENDING"
    DONE = "DONE"


# ============================================
# Compliance Record Schemas
# ============================================

class ComplianceRecordBase(BaseModel):
    """Base schema for Compliance Record with shared fields."""
    device_id: UUID = Field(..., description="Device requiring certification")
    country_id: int = Field(..., description="Target market country")
    certification_id: int = Field(..., description="Required certification")


class ComplianceRecordCreate(ComplianceRecordBase):
    """
    Schema for creating a new Compliance Record.
    Used in POST /api/v1/compliance
    
    Typically created when Gap Analysis identifies a missing certification.
    Initial status is always PENDING.
    
    Note: tenant_id is extracted from JWT token
    """
    status: ComplianceStatus = Field(
        ComplianceStatus.PENDING,
        description="Initial status (usually PENDING)"
    )
    labeling_status: Optional[LabelingStatus] = Field(
        LabelingStatus.PENDING,
        description="Labeling status"
    )
    certificate_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Official certificate number (if already obtained)"
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Certificate expiry date (required if status is ACTIVE)"
    )


class ComplianceRecordUpdate(BaseModel):
    """
    Schema for updating a Compliance Record.
    Used when uploading certificates or updating status.
    """
    status: Optional[ComplianceStatus] = None
    labeling_status: Optional[LabelingStatus] = None
    certificate_number: Optional[str] = Field(None, max_length=100)
    expiry_date: Optional[date] = Field(
        None,
        description="Certificate expiry date"
    )
    # Note: document fields are handled separately via file upload endpoint


class ComplianceRecordResponse(ComplianceRecordBase):
    """
    Schema for Compliance Record API responses.
    Includes full details with document info.
    """
    id: UUID = Field(..., description="Unique compliance record identifier")
    tenant_id: UUID = Field(..., description="Tenant tracking this compliance")
    status: ComplianceStatus = Field(..., description="Current compliance status")
    labeling_status: Optional[LabelingStatus] = Field(None, description="Labeling status")
    labeling_updated_at: Optional[datetime] = Field(None, description="Timestamp when labeling_status was last changed")
    expiry_date: Optional[date] = Field(None, description="Certificate expiry date")
    certificate_number: Optional[str] = Field(None, description="Official certificate number")
    
    # Document information
    document_path: Optional[str] = Field(None, description="MinIO object path")
    document_filename: Optional[str] = Field(None, description="Original filename")
    document_mime_type: Optional[str] = Field(None, description="File MIME type")
    
    # Notification tracking
    last_notified_at: Optional[datetime] = Field(None, description="Last alert timestamp")

    # Test Report information
    test_report_path: Optional[str] = Field(None, description="MinIO object path for test report")
    test_report_filename: Optional[str] = Field(None, description="Original filename of test report")
    test_report_mime_type: Optional[str] = Field(None, description="File MIME type of test report")
    
    # Labeling Picture information
    labeling_picture_path: Optional[str] = Field(None, description="MinIO object path for labeling picture")
    labeling_picture_filename: Optional[str] = Field(None, description="Original filename of labeling picture")
    labeling_picture_mime_type: Optional[str] = Field(None, description="File MIME type of labeling picture")
    
    # Timestamps
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    
    # Optional: Include related entity names (useful for UI)
    device_name: Optional[str] = Field(None, description="Device model name")
    country_name: Optional[str] = Field(None, description="Country name")
    certification_name: Optional[str] = Field(None, description="Certification name")
    
    # Task progress info
    task_progress_percent: Optional[int] = Field(None, description="Task completion percent 0-100")
    task_counts: Optional[Dict[str, int]] = Field(None, description="Counts per task status")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Gap Analysis Schemas
# ============================================

class GapAnalysisRequest(BaseModel):
    """
    Schema for Gap Analysis request.
    Used in POST /api/v1/compliance/gap-analysis
    
    This is THE CORE FEATURE - analyzes device against target country.
    """
    device_id: UUID = Field(
        ...,
        description="Device to analyze",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    country_id: int = Field(
        ...,
        description="Target market country",
        examples=[1, 2, 3]
    )


class GapAnalysisResultItem(BaseModel):
    """
    Individual result item in Gap Analysis response.
    Represents one certification requirement.
    """
    certification_id: int = Field(..., description="Required certification ID")
    certification_name: str = Field(..., description="Certification name")
    technology: str = Field(..., description="Technology requiring this certification")
    has_gap: bool = Field(
        ...,
        description="True = Missing certification (GAP), False = Already have it"
    )
    status: Optional[str] = Field(
        None,
        description="Current status if certification exists (PENDING/ACTIVE/EXPIRING/EXPIRED)"
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Expiry date if certification exists"
    )
    compliance_record_id: Optional[UUID] = Field(
        None,
        description="Compliance record ID if exists"
    )
    branding_image_url: Optional[str] = Field(
        None,
        description="URL to certification logo for labeling"
    )
    labeling_requirements: Optional[str] = Field(
        None,
        description="Placement rules for the label"
    )
    open_tasks_count: int = Field(
        0,
        description="Number of open tasks associated with this certification"
    )


class GapAnalysisResponse(BaseModel):
    """
    Complete Gap Analysis response.
    
    Business Logic:
        - Lists ALL required certifications for device + country
        - Flags which ones are missing (has_gap=True)
        - Shows status of existing certifications
    
    Example Response:
        {
            "device_id": "123...",
            "country_id": 2,
            "total_required": 3,
            "gaps_found": 1,
            "results": [
                {
                    "certification_name": "WPC",
                    "technology": "Wi-Fi 6E",
                    "has_gap": true,  # MISSING!
                    "status": "MISSING"
                },
                {
                    "certification_name": "BIS",
                    "technology": "Bluetooth",
                    "has_gap": false,  # Already have it
                    "status": "ACTIVE",
                    "expiry_date": "2025-12-31"
                }
            ]
        }
    """
    device_id: UUID = Field(..., description="Analyzed device ID")
    country_id: int = Field(..., description="Target country ID")
    total_required: int = Field(..., description="Total certifications required")
    gaps_found: int = Field(..., description="Number of missing certifications")
    results: List[GapAnalysisResultItem] = Field(
        ...,
        description="Detailed analysis results"
    )


# ============================================
# Document Upload Schemas
# ============================================

class DocumentUploadResponse(BaseModel):
    """
    Schema for document upload response.
    Used when uploading certificate PDFs.
    """
    compliance_record_id: UUID = Field(..., description="Compliance record updated")
    document_path: str = Field(..., description="MinIO object path")
    document_filename: str = Field(..., description="Uploaded filename")
    document_url: str = Field(..., description="Presigned download URL")
    message: str = Field(
        ...,
        description="Success message",
        examples=["Certificate uploaded successfully"]
    )


# ============================================
# Task Workflow Schemas
# ============================================


class ComplianceTaskBase(BaseModel):
    """Base task fields."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, description="Task details")
    assignee: Optional[str] = Field(None, max_length=100, description="Assigned user")


class ComplianceTaskCreate(ComplianceTaskBase):
    """Create task for a compliance record."""
    status: TaskStatus = Field(TaskStatus.TODO, description="Initial task status")


class ComplianceTaskUpdate(BaseModel):
    """Update task fields."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee: Optional[str] = Field(None, max_length=100)
    updated_by: Optional[str] = Field(None, max_length=100)


class ComplianceTaskResponse(ComplianceTaskBase):
    """Task response model."""
    id: UUID
    record_id: UUID
    status: TaskStatus
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskNoteCreate(BaseModel):
    """Create a worknote for a task."""
    note: str = Field(..., description="Worknote content")
    author: Optional[str] = Field(None, max_length=100)


class ComplianceTaskNoteResponse(BaseModel):
    """Task worknote response."""
    id: UUID
    task_id: UUID
    note: str
    author: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentDownloadResponse(BaseModel):
    """
    Schema for document download URL response.
    Returns presigned URL for secure download.
    """
    document_url: str = Field(
        ...,
        description="Presigned URL (expires in 1 hour)",
        examples=["http://192.168.80.36:9000/certificates/...?X-Amz-Expires=3600"]
    )
    expires_in: int = Field(
        ...,
        description="URL validity in seconds",
        examples=[3600]
    )


