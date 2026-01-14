# TAMSys Backend - Multi-Tenant Certification Management System

**Enterprise SaaS platform for managing hardware certifications (FCC, CE, WPC) across global markets.**

## 🚀 Features

- ✅ **Global Data Management**: Technologies, Countries, Certifications, Regulatory Rules
- ✅ **Tenant Operations**: Multi-tenant architecture with data isolation
- ✅ **Device Management**: Register devices with technology specifications
- ✅ **Gap Analysis**: THE CORE FEATURE - Identify missing certifications for target markets
- ✅ **Compliance Tracking**: Track certification status (PENDING/ACTIVE/EXPIRING/EXPIRED)
- ✅ **Document Management**: Upload/download certificate PDFs (MinIO self-hosted storage)
- ✅ **Automated Alerts**: Daily cron job checks expiring certificates (email disabled for now)
- ✅ **Auto-Migrations**: Database migrations run automatically on startup
- ✅ **API Documentation**: Interactive Swagger UI and ReDoc

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- MinIO (for document storage)
- Docker & Docker Compose (recommended)

## 🛠️ Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start Infrastructure** (PostgreSQL + MinIO):
```bash
cd backend
docker-compose up -d
```

This starts:
- PostgreSQL on `localhost:5432`
- MinIO API on `localhost:9000`
- MinIO Console on `localhost:9001`

2. **Setup Python Environment**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure Environment**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (default values should work with Docker Compose)
```

4. **Run Backend**:
```bash
# Migrations run automatically on startup!
uvicorn app.main:app --reload
```

5. **Access API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- MinIO Console: http://localhost:9001 (user: minioadmin, pass: minioadmin123)

### Option 2: Local Setup (Without Docker)

1. **Install PostgreSQL 15+**
2. **Create Database**:
```sql
CREATE DATABASE tamsys_db;
CREATE USER tamsys_user WITH PASSWORD 'tamsys_secure_pass_2024';
GRANT ALL PRIVILEGES ON DATABASE tamsys_db TO tamsys_user;
```

3. **Install and Run MinIO**:
```bash
# Download MinIO
# Windows: https://dl.min.io/server/minio/release/windows-amd64/minio.exe
# Linux: wget https://dl.min.io/server/minio/release/linux-amd64/minio

# Run MinIO
minio server ./minio-data --console-address ":9001"
```

4. **Follow steps 2-5 from Option 1**

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/               # Configuration, database, MinIO setup
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic validation schemas
│   ├── services/           # Business logic layer
│   ├── api/                # API endpoints
│   │   └── v1/
│   │       └── endpoints/
│   ├── schedulers/         # Cron jobs (expiry checker)
│   └── main.py             # FastAPI application
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Infrastructure setup
└── README.md               # This file
```

## 🔧 API Endpoints

### Global Data APIs (Admin-managed)
- `GET /api/v1/global/technologies` - List all technologies
- `POST /api/v1/global/technologies` - Create technology
- `GET /api/v1/global/countries` - List all countries
- `POST /api/v1/global/countries` - Create country
- `GET /api/v1/global/certifications` - List all certifications
- `POST /api/v1/global/certifications` - Create certification
- `GET /api/v1/global/regulatory-matrix` - List regulatory rules
- `POST /api/v1/global/regulatory-matrix` - Create rule

### Tenant APIs
- `GET /api/v1/tenants` - List all tenants
- `POST /api/v1/tenants` - Create tenant
- `GET /api/v1/tenants/{id}/notification-rules` - Get tenant notification rules
- `POST /api/v1/tenants/{id}/notification-rules` - Create notification rule

### Device APIs
- `GET /api/v1/devices` - List devices for tenant
- `POST /api/v1/devices` - Create device with technologies
- `GET /api/v1/devices/{id}/technologies` - Get device technologies

### Compliance APIs (includes Gap Analysis)
- `POST /api/v1/compliance/gap-analysis` - **THE CORE FEATURE** - Analyze compliance gaps
- `GET /api/v1/compliance/records` - List compliance records
- `POST /api/v1/compliance/records` - Create compliance record
- `PUT /api/v1/compliance/records/{id}` - Update record (change status, add expiry)
- `POST /api/v1/compliance/records/{id}/document` - Upload certificate PDF
- `GET /api/v1/compliance/records/{id}/document` - Get download URL

## 🎯 Core Workflow

### 1. Setup Global Data (Admin)
```bash
# Create technologies
POST /api/v1/global/technologies
{
  "name": "Wi-Fi 6E",
  "description": "Wi-Fi operating in 6 GHz band"
}

# Create countries
POST /api/v1/global/countries
{
  "name": "India",
  "iso_code": "IND"
}

# Create certifications
POST /api/v1/global/certifications
{
  "name": "WPC",
  "authority_name": "Ministry of Communications",
  "description": "Wireless Planning and Coordination"
}

# Create regulatory rules (THE LOGIC ENGINE)
POST /api/v1/global/regulatory-matrix
{
  "technology_id": 1,      # Wi-Fi 6E
  "country_id": 2,         # India
  "certification_id": 5,   # WPC
  "is_mandatory": true,
  "notes": "6 GHz band requires WPC approval"
}
```

### 2. Register Tenant
```bash
POST /api/v1/tenants
{
  "name": "John Deere",
  "contact_email": "compliance@johndeere.com"
}

# Create notification rules
POST /api/v1/tenants/{tenant_id}/notification-rules
{
  "days_before_expiry": 90,
  "severity_level": "HIGH"
}
```

### 3. Register Device
```bash
POST /api/v1/devices?tenant_id={tenant_id}
{
  "model_name": "Tractor X9",
  "sku": "TRX9-2024",
  "technology_ids": [1, 2, 3]  # Wi-Fi 6E, Bluetooth, GPS
}
```

### 4. Run Gap Analysis (THE CORE FEATURE!)
```bash
POST /api/v1/compliance/gap-analysis?tenant_id={tenant_id}
{
  "device_id": "123e4567-e89b-12d3-a456-426614174000",
  "country_id": 2  # India
}

# Response shows missing certifications
{
  "total_required": 3,
  "gaps_found": 1,
  "results": [
    {
      "certification_name": "WPC",
      "technology": "Wi-Fi 6E",
      "has_gap": true,      # MISSING!
      "status": "MISSING"
    },
    {
      "certification_name": "BIS",
      "technology": "Bluetooth",
      "has_gap": false,     # Already have it
      "status": "ACTIVE"
    }
  ]
}
```

### 5. Upload Certificate
```bash
# Create compliance record for missing certification
POST /api/v1/compliance/records?tenant_id={tenant_id}
{
  "device_id": "123e4567...",
  "country_id": 2,
  "certification_id": 5,
  "status": "PENDING"
}

# Upload certificate PDF
POST /api/v1/compliance/records/{record_id}/document
[multipart/form-data with PDF file]

# Update status to ACTIVE
PUT /api/v1/compliance/records/{record_id}
{
  "status": "ACTIVE",
  "expiry_date": "2025-12-31",
  "certificate_number": "WPC/2024/12345"
}
```

## 🤖 Cron Jobs

### Expiry Checker (Daily at 00:00 UTC)
- Checks compliance records against notification rules
- Updates status: ACTIVE → EXPIRING → EXPIRED
- Logs alerts (email disabled for now)
- Prevents spam: Only alerts once per 7 days

## 🗄️ Database Schema

### Global Data Tables
- `global_technologies` - Wi-Fi, Bluetooth, GPS, etc.
- `global_countries` - USA, India, EU, etc.
- `global_certifications` - FCC, WPC, CE, etc.
- `regulatory_matrix` - Tech + Country → Required Cert (THE RULES ENGINE)

### Tenant Data Tables
- `tenants` - Organizations (John Deere, Samsung, etc.)
- `notification_rules` - Alert thresholds per tenant
- `tenant_devices` - Products requiring certification
- `device_tech_map` - Device → Technologies mapping
- `compliance_records` - Certification tracking (PENDING/ACTIVE/EXPIRING/EXPIRED)

## 🔒 Security Notes

- **Authentication**: Currently disabled. Future: Keycloak integration with JWT tokens
- **Data Isolation**: tenant_id filtering in all queries (future: from JWT)
- **CORS**: Configured for frontend origins
- **MinIO**: Uses presigned URLs for secure document access

## 📝 Development Notes

### Database Migrations
Migrations run **automatically on startup**. No manual migration commands needed!

To create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

### Testing the API
Use Swagger UI at http://localhost:8000/docs for interactive testing.

### Checking Logs
```bash
# Backend logs show:
# - Database connections
# - Migration status
# - Scheduler status
# - API requests
# - Cron job execution
```

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U tamsys_user -d tamsys_db
```

### MinIO Connection Failed
```bash
# Check MinIO is running
docker ps | grep minio

# Access MinIO Console: http://localhost:9001
# Credentials: minioadmin / minioadmin123
```

### Migrations Failed
```bash
# Migrations run automatically but you can manually run:
alembic upgrade head
```

## 🚀 Production Deployment

1. Update `.env` with production values
2. Set `DEBUG=False`
3. Enable HTTPS for MinIO (`MINIO_SECURE=True`)
4. Use strong passwords
5. Setup Keycloak for authentication
6. Configure email service (SendGrid/SMTP)
7. Use managed PostgreSQL (AWS RDS, Azure Database)
8. Use production ASGI server (Gunicorn + Uvicorn workers)

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🙏 Support

For issues or questions, please create an issue in the repository.

---

**Built with FastAPI, PostgreSQL, SQLAlchemy, and MinIO** 🚀


