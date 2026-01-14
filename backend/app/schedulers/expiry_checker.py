"""
Expiry Checker Scheduler
========================
Daily cron job to check expiring certificates and update status.

Schedule: Runs daily at 00:00 UTC

Responsibilities:
1. Check certificates approaching expiry (match against notification_rules)
2. Update status: ACTIVE → EXPIRING (when within threshold)
3. Update status: EXPIRING/ACTIVE → EXPIRED (when past expiry date)
4. Send email notifications (future feature, disabled for now)
5. Update last_notified_at to prevent spam

Business Logic:
- Each tenant has notification_rules (e.g., alert at 90, 60, 30 days)
- Daily job checks compliance_records.expiry_date
- Calculates days_until_expiry = expiry_date - today
- If days_until_expiry matches any rule threshold, trigger alert
- Prevent spam: Only alert if last_notified_at > 7 days ago
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import logging

from app.core.database import SessionLocal
from app.models.compliance import ComplianceRecord
from app.models.tenant import NotificationRule
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


# ============================================
# Scheduler Instance
# ============================================

scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)


# ============================================
# Expiry Check Job
# ============================================

async def check_expiring_certificates():
    """
    Daily job to check expiring certificates and update status.
    
    Process:
        1. Query all active notification rules
        2. For each rule, find compliance records expiring at threshold
        3. Update status if needed (ACTIVE → EXPIRING)
        4. Log alert (email disabled for now)
        5. Update last_notified_at timestamp
        6. Mark expired certificates (EXPIRING → EXPIRED)
    
    Example:
        Today: 2024-01-01
        Notification Rule: days_before_expiry = 90
        Threshold Date: 2024-04-01 (90 days from today)
        
        Find all compliance records with expiry_date = 2024-04-01
        These certificates are expiring in exactly 90 days → Alert!
    """
    logger.info("Starting daily expiry check job...")
    
    db: Session = SessionLocal()
    
    try:
        today = date.today()
        logger.info(f"Checking certificates for date: {today}")
        
        # ========================================
        # Part 1: Check certificates approaching expiry
        # ========================================
        
        # Get all active notification rules
        notification_rules = db.query(NotificationRule)\
            .filter(NotificationRule.is_active == True)\
            .all()
        
        logger.info(f"Found {len(notification_rules)} active notification rules")
        
        for rule in notification_rules:
            # Calculate threshold date
            # If rule says "alert 90 days before", threshold = today + 90 days
            threshold_date = today + timedelta(days=rule.days_before_expiry)
            
            logger.info(
                f"Processing rule: Tenant={rule.tenant_id}, "
                f"Days={rule.days_before_expiry}, "
                f"Threshold Date={threshold_date}"
            )
            
            # Find compliance records expiring at this threshold
            records = db.query(ComplianceRecord)\
                .filter(
                    ComplianceRecord.tenant_id == rule.tenant_id,
                    ComplianceRecord.expiry_date == threshold_date,
                    ComplianceRecord.status.in_(['ACTIVE', 'EXPIRING'])
                )\
                .all()
            
            logger.info(f"Found {len(records)} records expiring on {threshold_date}")
            
            for record in records:
                # Check if we recently notified (prevent spam)
                should_notify = True
                
                if record.last_notified_at:
                    days_since_last_notification = (datetime.now() - record.last_notified_at).days
                    
                    # Don't notify if alerted within last 7 days
                    if days_since_last_notification < 7:
                        logger.info(
                            f"Skipping notification for record {record.id} "
                            f"(notified {days_since_last_notification} days ago)"
                        )
                        should_notify = False
                
                if should_notify:
                    # ========================================
                    # SEND NOTIFICATION (Email disabled for now)
                    # ========================================
                    
                    # Future: Send email via SendGrid/SMTP
                    # await send_expiry_alert_email(record, rule)
                    
                    # For now, just log
                    logger.warning(
                        f"ALERT: Certificate expiring in {rule.days_before_expiry} days! "
                        f"Record ID: {record.id}, "
                        f"Device: {record.device_id}, "
                        f"Country: {record.country_id}, "
                        f"Certification: {record.certification_id}, "
                        f"Expiry Date: {record.expiry_date}"
                    )
                    
                    # Update notification timestamp
                    record.last_notified_at = datetime.now()
                    
                    # Update status to EXPIRING if currently ACTIVE
                    if record.status == 'ACTIVE':
                        record.status = 'EXPIRING'
                        logger.info(f"Updated record {record.id} status: ACTIVE → EXPIRING")
        
        # ========================================
        # Part 2: Mark expired certificates
        # ========================================
        
        # Find all records past expiry date
        expired_records = db.query(ComplianceRecord)\
            .filter(
                ComplianceRecord.expiry_date < today,
                ComplianceRecord.status != 'EXPIRED'
            )\
            .all()
        
        logger.info(f"Found {len(expired_records)} expired certificates")
        
        for record in expired_records:
            old_status = record.status
            record.status = 'EXPIRED'
            
            logger.error(
                f"CRITICAL: Certificate EXPIRED! "
                f"Record ID: {record.id}, "
                f"Device: {record.device_id}, "
                f"Expiry Date: {record.expiry_date}, "
                f"Status: {old_status} → EXPIRED"
            )
        
        # Commit all changes
        db.commit()
        
        logger.info("Expiry check job completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in expiry check job: {str(e)}", exc_info=True)
        db.rollback()
        
    finally:
        db.close()


# ============================================
# Email Notification Function (Future Feature)
# ============================================

async def send_expiry_alert_email(record: ComplianceRecord, rule: NotificationRule):
    """
    Send email notification for expiring certificate.
    
    Args:
        record: Compliance record approaching expiry
        rule: Notification rule that triggered this alert
    
    Note:
        Currently disabled. Will be implemented with SendGrid/SMTP.
    
    Email Template Example:
        Subject: Certificate Expiring in {days} Days - Action Required
        
        Dear {tenant_name},
        
        Your certificate is expiring soon and requires immediate attention:
        
        Device: {device_model}
        Certification: {certification_name}
        Country: {country_name}
        Expiry Date: {expiry_date}
        Days Remaining: {days_remaining}
        
        Please renew this certification before expiry to avoid shipment delays.
        
        Login to TAMSys: https://tamsys.com/dashboard
        
        Best regards,
        TAMSys Compliance Team
    """
    # Future implementation with SendGrid
    pass


# ============================================
# Scheduler Configuration
# ============================================

def start_scheduler():
    """
    Start the scheduler and add jobs.
    
    Schedule:
        - Expiry check: Daily at 00:00 UTC (midnight)
    
    Note:
        Scheduler is started in main.py on application startup.
    """
    if not settings.ENABLE_SCHEDULER:
        logger.info("Scheduler is disabled in settings")
        return
    
    logger.info("Configuring scheduler...")
    
    # Add expiry check job (daily at midnight UTC)
    scheduler.add_job(
        check_expiring_certificates,
        trigger=CronTrigger(hour=0, minute=0, timezone=settings.SCHEDULER_TIMEZONE),
        id='check_expiring_certificates',
        name='Check Expiring Certificates (Daily)',
        replace_existing=True
    )
    
    # Optional: Add job to run immediately on startup (for testing)
    # scheduler.add_job(
    #     check_expiring_certificates,
    #     'date',  # Run once
    #     id='check_expiring_certificates_startup',
    #     name='Check Expiring Certificates (Startup)',
    # )
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started successfully!")
    logger.info(f"Next expiry check scheduled for: {scheduler.get_job('check_expiring_certificates').next_run_time}")


def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully.
    
    Note:
        Called in main.py on application shutdown.
    """
    if scheduler.running:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down successfully!")


