"""
Compliance Models
================
These models track the actual compliance status of devices against regulatory requirements.

Tables in this module:
1. ComplianceRecord - The master tracker for certification status

This is where the "business happens":
- Gaps identified by Gap Analysis become PENDING records
- Uploaded certificates become ACTIVE records
- Expiry tracking triggers EXPIRING/EXPIRED status changes
- Notification engine queries this table daily
"""

from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class ComplianceRecord(Base):
    """
    Compliance Record Model - The certification lifecycle tracker
    
    This is the CORE OPERATIONAL TABLE where certification compliance is tracked.
    
    Status Lifecycle:
        PENDING → User knows certification is needed but hasn't obtained it yet
        ACTIVE → Certificate uploaded and currently valid
        EXPIRING → Within notification threshold (approaching expiry)
        EXPIRED → Past expiry date (CRITICAL - shipments blocked!)
    
    Example Records:
        1. (Tractor X9, India, WPC, PENDING) - Identified gap, no cert yet
        2. (Tractor X9, India, WPC, ACTIVE, expiry=2025-12-31) - Certificate uploaded
        3. (Galaxy Watch, USA, FCC, EXPIRING, expiry=2024-02-15) - 30 days to expiry
        4. (Old Device, EU, CE, EXPIRED, expiry=2023-01-01) - Must renew immediately!
    
    Business Logic:
        - Created when Gap Analysis identifies a requirement
        - Updated when certificate is uploaded (PENDING → ACTIVE)
        - Monitored by daily cron job for expiry (ACTIVE → EXPIRING → EXPIRED)
        - Triggers email notifications based on tenant notification_rules
        - Links to MinIO for certificate document storage
    
    Notification Flow:
        1. Cron job runs daily at 00:00 UTC
        2. Queries: expiry_date - current_date = days_until_expiry
        3. Checks if days_until_expiry matches any tenant notification_rules
        4. Sends email if threshold hit and last_notified_at > 7 days ago
        5. Updates status: ACTIVE → EXPIRING (when within threshold)
        6. Updates status: EXPIRING → EXPIRED (when past expiry)
    
    Relationships:
        - tenant: Organization tracking this compliance
        - device: Product requiring certification
        - country: Target market
        - certification: Required regulatory approval
    """
    __tablename__ = "compliance_records"
    
    # Primary Key - UUID for security
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the compliance record"
    )
    
    # ============================================
    # Foreign Keys - The "Compliance Context"
    # ============================================
    
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Critical for tenant data isolation queries
        comment="Tenant tracking this compliance"
    )
    
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenant_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Device requiring certification"
    )
    
    country_id = Column(
        Integer,
        ForeignKey("global_countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target market country"
    )
    
    certification_id = Column(
        Integer,
        ForeignKey("global_certifications.id", ondelete="CASCADE"),
        nullable=False,
        comment="Required certification type"
    )
    
    # ============================================
    # Status Tracking
    # ============================================
    
    status = Column(
        String(20),
        nullable=False,
        index=True,  # Indexed for fast filtering by status
        comment="Certification status: PENDING, ACTIVE, EXPIRING, EXPIRED"
    )
    
    expiry_date = Column(
        Date,
        nullable=True,
        index=True,  # Indexed for fast cron job queries
        comment="Certificate expiry date (NULL for PENDING status)"
    )
    
    certificate_number = Column(
        String(100),
        nullable=True,
        comment="Official certification number/ID issued by regulatory body"
    )

    labeling_status = Column(
        String(20),
        nullable=True,
        default="PENDING",
        comment="Labeling status: PENDING, DONE"
    )

    labeling_updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when labeling_status was last changed"
    )
    
    # ============================================
    # Document Storage (MinIO)
    # ============================================
    
    document_path = Column(
        Text,
        nullable=True,
        comment="MinIO object path: certificates/{tenant_id}/{device_id}/{filename}"
    )
    
    document_filename = Column(
        String(255),
        nullable=True,
        comment="Original filename of uploaded certificate (e.g., 'FCC_Certificate.pdf')"
    )
    
    document_mime_type = Column(
        String(100),
        nullable=True,
        comment="MIME type of the document (e.g., 'application/pdf')"
    )

    # ============================================
    # Test Report Storage (MinIO)
    # ============================================

    test_report_path = Column(
        Text,
        nullable=True,
        comment="MinIO object path for test report"
    )

    test_report_filename = Column(
        String(255),
        nullable=True,
        comment="Original filename of uploaded test report"
    )

    test_report_mime_type = Column(
        String(100),
        nullable=True,
        comment="MIME type of the test report"
    )

    # ============================================
    # Labeling Picture Storage (MinIO)
    # ============================================

    labeling_picture_path = Column(
        Text,
        nullable=True,
        comment="MinIO object path for label picture"
    )

    labeling_picture_filename = Column(
        String(255),
        nullable=True,
        comment="Original filename of uploaded label picture"
    )

    labeling_picture_mime_type = Column(
        String(100),
        nullable=True,
        comment="MIME type of the label picture"
    )
    
    # ============================================
    # Notification Tracking
    # ============================================
    
    last_notified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last email notification sent (prevents spam)"
    )
    
    # ============================================
    # Audit Timestamps
    # ============================================
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp (when gap was identified)"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp"
    )
    
    # ============================================
    # Constraints
    # ============================================
    
    # Status must be one of the defined values
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'ACTIVE', 'EXPIRING', 'EXPIRED')",
            name='check_valid_status'
        ),
        # Prevent duplicate tracking: Same device + country + cert should have only one active record
        UniqueConstraint(
            'tenant_id',
            'device_id',
            'country_id',
            'certification_id',
            name='uq_compliance_tracking'
        ),
        {
            'comment': 'Compliance tracking records for certification lifecycle management'
        }
    )
    
    # ============================================
    # Relationships
    # ============================================
    
    tenant = relationship(
        "Tenant",
        back_populates="compliance_records",
        doc="Tenant tracking this compliance"
    )
    
    device = relationship(
        "TenantDevice",
        back_populates="compliance_records",
        doc="Device requiring certification"
    )
    
    country = relationship(
        "Country",
        back_populates="compliance_records",
        doc="Target market country"
    )
    
    certification = relationship(
        "Certification",
        back_populates="compliance_records",
        doc="Required certification"
    )
    
    # Tasks workflow
    tasks = relationship(
        "ComplianceTask",
        back_populates="record",
        cascade="all, delete-orphan",
        doc="Tasks associated with this compliance record"
    )
    
    def __repr__(self):
        return (
            f"<ComplianceRecord("
            f"id={self.id}, "
            f"device={self.device_id}, "
            f"country={self.country_id}, "
            f"cert={self.certification_id}, "
            f"status='{self.status}', "
            f"expiry={self.expiry_date}"
            f")>"
        )


class ComplianceTask(Base):
    """
    Tasks related to compliance records (e.g., "Upload document", "Renew certification")
    """
    __tablename__ = "compliance_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("compliance_records.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="TODO")  # TODO/IN_PROGRESS/DONE
    assignee = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    record = relationship("ComplianceRecord", back_populates="tasks")
    notes = relationship(
        "ComplianceTaskNote",
        back_populates="task",
        cascade="all, delete-orphan",
        doc="Worknotes for this task"
    )

    def __repr__(self):
        return f"<ComplianceTask(id={self.id}, record={self.record_id}, status={self.status})>"


class ComplianceTaskNote(Base):
    """
    Worknote for a compliance task.
    """
    __tablename__ = "compliance_task_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("compliance_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    note = Column(Text, nullable=False)
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task = relationship("ComplianceTask", back_populates="notes")

    def __repr__(self):
        return f"<ComplianceTaskNote(id={self.id}, task={self.task_id})>"


