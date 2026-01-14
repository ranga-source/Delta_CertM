import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add target_countries column to tenant_devices table."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Check if column exists (PostgreSQL specific check, but works generic enough for add column with catch)
            # Actually easier to just try adding it.
            logger.info("Adding target_countries column to tenant_devices...")
            conn.execute(text("ALTER TABLE tenant_devices ADD COLUMN target_countries JSON DEFAULT '[\"ALL\"]'"))
            conn.commit()
            logger.info("Migration successful!")
    except Exception as e:
        logger.error(f"Migration failed (Column might already exist?): {e}")

if __name__ == "__main__":
    migrate()
