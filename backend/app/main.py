"""
TAMSys Backend - Main Application
=================================
FastAPI application entry point for the Multi-Tenant Certification Management System.

Features:
- RESTful API with automatic OpenAPI/Swagger documentation
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations (auto-run on startup)
- MinIO document storage
- Daily cron job for expiry checking
- CORS enabled for frontend access

Architecture:
- Models: SQLAlchemy ORM models (database layer)
- Schemas: Pydantic models (API validation layer)
- Services: Business logic layer
- API Endpoints: Route handlers (presentation layer)

To run:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import check_db_connection, run_migrations
from app.schedulers.expiry_checker import start_scheduler, shutdown_scheduler

# Import API routers
from app.api.v1.endpoints import (
    global_data,
    tenants,
    devices,
    compliance
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# Lifespan Context Manager (Startup/Shutdown)
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Startup:
        1. Check database connectivity
        2. Run Alembic migrations
        3. Start cron job scheduler
    
    Shutdown:
        1. Stop scheduler gracefully
    """
    # ========== STARTUP ==========
    logger.info("Starting TAMSys Backend...")
    
    # Check database connection
    logger.info("Checking database connectivity...")
    if not check_db_connection():
        logger.error("Failed to connect to database! Please check configuration.")
        raise Exception("Database connection failed")
    
    # Run migrations automatically
    logger.info("Running database migrations...")
    try:
        run_migrations()
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        # Continue anyway - migrations might already be up to date
    
    # Start scheduler
    logger.info("Starting cron job scheduler...")
    start_scheduler()
    
    logger.info("TAMSys Backend started successfully! ✓")
    logger.info(f"API Documentation: http://localhost:8000/docs")
    logger.info(f"ReDoc Documentation: http://localhost:8000/redoc")
    
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("Shutting down TAMSys Backend...")
    shutdown_scheduler()
    logger.info("TAMSys Backend shut down successfully!")


# ============================================
# FastAPI Application Instance
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **Multi-Tenant Certification Management System**
    
    Enterprise SaaS platform for managing hardware certifications (FCC, CE, WPC) 
    across global markets.
    
    ## Key Features
    
    * **Global Data Management**: Manage technologies, countries, certifications, and regulatory rules
    * **Tenant Operations**: Multi-tenant architecture with data isolation
    * **Device Management**: Register devices with technology specifications
    * **Gap Analysis**: Identify missing certifications for target markets
    * **Compliance Tracking**: Track certification status and expiry dates
    * **Document Management**: Upload and manage certificate PDFs (MinIO)
    * **Automated Alerts**: Daily cron job checks expiring certificates
    
    ## API Organization
    
    * `/api/v1/global/*` - Global master data (admin-managed)
    * `/api/v1/tenants/*` - Tenant management and notification rules
    * `/api/v1/devices/*` - Device registration and technology mapping
    * `/api/v1/compliance/*` - Compliance tracking and gap analysis
    
    ## Authentication
    
    Currently disabled. Future: Keycloak integration with JWT tokens.
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema
    lifespan=lifespan  # Startup/shutdown handler
)


# ============================================
# CORS Middleware
# ============================================

# CORS: allow localhost/127.0.0.1 for dev (covers port variations + redirects)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Explicit whitelist
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(:\d+)?",  # Fallback for local dev
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================
# API Routers
# ============================================

# Global Data APIs (Admin-managed)
app.include_router(
    global_data.router,
    prefix=f"{settings.API_V1_PREFIX}/global",
    tags=["Global Data"]
)

# Tenant APIs
app.include_router(
    tenants.router,
    prefix=f"{settings.API_V1_PREFIX}/tenants",
    tags=["Tenants"]
)

# Device APIs
app.include_router(
    devices.router,
    prefix=f"{settings.API_V1_PREFIX}/devices",
    tags=["Devices"]
)

# Compliance APIs (includes Gap Analysis)
app.include_router(
    compliance.router,
    prefix=f"{settings.API_V1_PREFIX}/compliance",
    tags=["Compliance & Gap Analysis"]
)


# ============================================
# Health Check Endpoint
# ============================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and database is accessible"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status message and version info
    """
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if check_db_connection() else "disconnected"
    }


@app.get(
    "/",
    tags=["Root"],
    summary="Root Endpoint",
    description="Welcome message with API documentation links"
)
async def root():
    """
    Root endpoint - provides links to documentation.
    
    Returns:
        dict: Welcome message and documentation URLs
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "endpoints": {
            "global_data": f"{settings.API_V1_PREFIX}/global",
            "tenants": f"{settings.API_V1_PREFIX}/tenants",
            "devices": f"{settings.API_V1_PREFIX}/devices",
            "compliance": f"{settings.API_V1_PREFIX}/compliance"
        }
    }


# ============================================
# Run Application (Development)
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST_IP,
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )


