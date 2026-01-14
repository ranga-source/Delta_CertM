"""
Database Configuration Module
=============================
This module sets up SQLAlchemy database engine and session management.

Key Components:
- Database engine creation with connection pooling
- Session factory for database operations
- Dependency injection for FastAPI routes
- Database initialization and migration runner

Architecture:
- Uses SQLAlchemy 2.0 with declarative base
- Session-per-request pattern for API endpoints
- Alembic integration for automatic migrations
"""

from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings
import logging

# Setup logging for database operations
logger = logging.getLogger(__name__)


# ============================================
# Database Engine Configuration
# ============================================
"""
Create SQLAlchemy engine with connection pooling.

Connection Pool Settings:
- pool_pre_ping: Verify connections before using (prevents stale connections)
- pool_size: Number of connections to maintain
- max_overflow: Additional connections when pool is exhausted
- echo: Log all SQL statements (useful for debugging)
"""
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using
    pool_size=5,  # Maintain 5 connections in pool
    max_overflow=10,  # Allow 10 additional connections
    echo=settings.DEBUG,  # Log SQL in debug mode
)


# ============================================
# Session Factory
# ============================================
"""
Session factory for creating database sessions.

Configuration:
- autocommit=False: Explicit commit required (prevents accidental commits)
- autoflush=False: Manual flush control for better performance
- bind=engine: Associate sessions with our database engine
"""
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================
# Declarative Base for Models
# ============================================
"""
Base class for all SQLAlchemy models.
All database models will inherit from this base.

Usage:
    class MyModel(Base):
        __tablename__ = "my_table"
        id = Column(Integer, primary_key=True)
"""
Base = declarative_base()


# ============================================
# Dependency Injection for FastAPI
# ============================================
def get_db() -> Session:
    """
    Database session dependency for FastAPI routes.
    
    This function provides a database session to API endpoints and
    ensures proper cleanup after the request is complete.
    
    Usage in FastAPI endpoint:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        The session is automatically closed after the request,
        even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# Database Initialization Functions
# ============================================
def init_db():
    """
    Initialize database by creating all tables.
    
    This function creates all tables defined in SQLAlchemy models.
    In production, use Alembic migrations instead of this function.
    
    Note:
        This is primarily for development/testing. Production should
        use Alembic migrations for better version control.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def run_migrations():
    """
    Run Alembic migrations automatically on startup.
    
    This function executes pending Alembic migrations when the
    application starts, ensuring the database schema is up-to-date.
    
    Process:
        1. Check for pending migrations
        2. Apply migrations in order
        3. Log results
    
    Note:
        This satisfies the requirement: "Database migrations run
        automatically on backend startup - NO manual scripts"
    """
    try:
        from alembic.config import Config
        from alembic import command
        
        logger.info("Running database migrations...")
        
        # Load Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations to the latest version
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        # If Alembic fails (e.g., no migration scripts yet), fall back to
        # creating tables directly from SQLAlchemy models. This keeps the
        # application usable in development environments even when
        # migrations are not configured.
        logger.info("Falling back to direct table creation via SQLAlchemy Base.metadata.create_all()")
        init_db()

    # Even if migrations ran without raising an exception, it's possible that
    # no migration scripts exist yet (fresh project). In that case Alembic
    # will be a no-op and the core tables would still be missing. To guard
    # against this, verify that a known core table exists and, if not,
    # create all tables from the SQLAlchemy models.
    try:
        inspector = inspect(engine)
        # Check for one of the core global tables as a proxy that the schema
        # has been created. If it's missing, create all tables.
        if not inspector.has_table("global_technologies"):
            logger.info("Detected missing core tables. Creating all tables via Base.metadata.create_all()")
            init_db()
    except Exception as e:
        # Log but do not fail startup if inspection fails; other parts of the
        # system will surface errors if the schema is not usable.
        logger.error(f"Database schema verification failed: {str(e)}")


def check_db_connection():
    """
    Verify database connectivity on startup.
    
    This function tests the database connection and logs the result.
    Useful for catching configuration errors early.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Attempt a simple query to verify connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        logger.info(f"Database connection successful: {settings.DATABASE_HOST}")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


