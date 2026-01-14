"""
Alembic Environment Configuration
=================================
This module configures Alembic for automatic database migrations.

Key Features:
- Loads database URL from application settings (not hardcoded)
- Auto-imports all models for migration detection
- Supports both online and offline migration modes
- Integrates with SQLAlchemy Base metadata

Migration Process:
1. Alembic compares current database schema with SQLAlchemy models
2. Generates migration scripts with detected changes
3. Applies migrations in order on startup (via run_migrations() in database.py)
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic can detect schema changes
# This is CRITICAL - without these imports, Alembic won't see the models
from app.models.global_data import Technology, Country, Certification, RegulatoryMatrix, GlossaryTerm
from app.models.tenant import Tenant, NotificationRule
from app.models.device import TenantDevice, DeviceTechMap
from app.models.compliance import ComplianceRecord

# Alembic Config object
config = context.config

# Override sqlalchemy.url from settings (don't use hardcoded value from alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy MetaData object for autogenerate support
# This contains all table definitions from our models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    By skipping Engine creation, we don't need a live database connection.
    
    Use case:
        Generate SQL scripts for manual execution (for DBA review)
    
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    This creates an Engine and associates a connection with the context.
    This is the normal mode used when the application starts.
    
    Use case:
        Automatic migrations on application startup (our requirement)
    
    Process:
        1. Create database engine from config
        2. Connect to database
        3. Configure Alembic context
        4. Run pending migrations
        5. Close connection
    """
    # Create engine from config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections for migrations
    )

    # Connect and run migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Compare type helps detect column type changes
            compare_type=True,
            # Compare server default to detect default value changes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


