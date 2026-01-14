"""
Core Configuration Module
=========================
This module handles all application configuration settings using Pydantic Settings.
Settings are loaded from environment variables and .env file.

Key Features:
- Type-safe configuration with validation
- Environment variable loading with defaults
- Database URL construction
- MinIO settings management
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application Settings Class
    
    All configuration values are loaded from environment variables.
    Default values are provided for development environment.
    
    Usage:
        from app.core.config import settings
        database_url = settings.DATABASE_URL
    """
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = "TAMSys Certification Management"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Central Host Configuration
    HOST_IP: str = "127.0.0.1"
    
    # ============================================
    # Database Configuration
    # ============================================
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 5433
    DATABASE_NAME: str = "tamsys_db"
    DATABASE_USER: str = "tamsys_user"
    DATABASE_PASSWORD: str = "tamsys_secure_pass_2024"
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct PostgreSQL connection URL from individual components
        
        Returns:
            str: Complete database URL in format:
                 postgresql://user:password@host:port/dbname
        """
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    # ============================================
    # MinIO Configuration (Self-hosted S3)
    # ============================================
    MINIO_ENDPOINT: str = "" # Set default to empty to enforce derivation if not present
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "certificates"
    MINIO_SECURE: bool = False  # Use HTTPS in production
    
    @property
    def EFFECTIVE_MINIO_ENDPOINT(self) -> str:
        """Derive MinIO endpoint from HOST_IP if not explicitly set."""
        if self.MINIO_ENDPOINT:
            return self.MINIO_ENDPOINT
        return f"{self.HOST_IP}:9000"

    # ============================================
    # CORS Settings (Frontend Access Control)
    # ============================================
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Derive allowed origins from HOST_IP."""
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        # Add dynamic host IP if distinct
        if self.HOST_IP not in ["localhost", "127.0.0.1"]:
            origins.extend([
                f"http://{self.HOST_IP}:3000",
                f"http://{self.HOST_IP}:5173"
            ])
        return origins
    
    # ============================================
    # Scheduler Settings (Cron Jobs)
    # ============================================
    ENABLE_SCHEDULER: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"  # Load from .env file if present
        case_sensitive = True


# ============================================
# Global Settings Instance
# ============================================
# Create a single instance to be imported throughout the application
settings = Settings()


