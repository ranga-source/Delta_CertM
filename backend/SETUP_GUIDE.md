# TAMSys Backend - Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Infrastructure (2 minutes)
```bash
cd backend
docker-compose up -d
```

Wait for services to start. Check with:
```bash
docker ps
```

You should see:
- `tamsys_postgres` - Running
- `tamsys_minio` - Running

### Step 2: Setup Python Environment (2 minutes)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start Backend (1 minute)
```bash
# Migrations run automatically!
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Starting TAMSys Backend...
INFO:     Checking database connectivity...
INFO:     Database connection successful: localhost
INFO:     Running database migrations...
INFO:     Database migrations completed successfully!
INFO:     Starting cron job scheduler...
INFO:     Scheduler started successfully!
INFO:     TAMSys Backend started successfully! ✓
INFO:     API Documentation: http://localhost:8000/docs
```

### Step 4: Test the API ✨
Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin123)

---

## 📋 Detailed Setup

### Prerequisites
- Python 3.11+
- Docker Desktop (for Windows/Mac) or Docker + Docker Compose (for Linux)

### Environment Variables
The `.env` file is already configured with defaults that work with Docker Compose.

If you need to change anything:
```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=tamsys_db
DATABASE_USER=tamsys_user
DATABASE_PASSWORD=tamsys_secure_pass_2024

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

---

## 🧪 Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "application": "TAMSys Certification Management",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Create a Technology (Global Data)
```bash
curl -X POST http://localhost:8000/api/v1/global/technologies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wi-Fi 6E",
    "description": "Wi-Fi operating in 6 GHz band"
  }'
```

### 3. Create a Country
```bash
curl -X POST http://localhost:8000/api/v1/global/countries \
  -H "Content-Type: application/json" \
  -d '{
    "name": "India",
    "iso_code": "IND"
  }'
```

### 4. Create a Certification
```bash
curl -X POST http://localhost:8000/api/v1/global/certifications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WPC",
    "authority_name": "Ministry of Communications"
  }'
```

### 5. Create a Regulatory Rule
```bash
curl -X POST http://localhost:8000/api/v1/global/regulatory-matrix \
  -H "Content-Type: application/json" \
  -d '{
    "technology_id": 1,
    "country_id": 1,
    "certification_id": 1,
    "is_mandatory": true,
    "notes": "6 GHz band requires approval"
  }'
```

### 6. Create a Tenant
```bash
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Deere",
    "contact_email": "compliance@johndeere.com"
  }'
```

Response includes `"id": "123e4567-..."` - Save this tenant_id!

### 7. Create a Device
```bash
curl -X POST "http://localhost:8000/api/v1/devices?tenant_id=YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "Tractor X9",
    "sku": "TRX9-2024",
    "technology_ids": [1]
  }'
```

Response includes `"id": "789abc..."` - Save this device_id!

### 8. Run Gap Analysis (THE CORE FEATURE!)
```bash
curl -X POST "http://localhost:8000/api/v1/compliance/gap-analysis?tenant_id=YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "YOUR_DEVICE_ID",
    "country_id": 1
  }'
```

Expected response:
```json
{
  "device_id": "789abc...",
  "country_id": 1,
  "total_required": 1,
  "gaps_found": 1,
  "results": [
    {
      "certification_id": 1,
      "certification_name": "WPC",
      "technology": "Wi-Fi 6E",
      "has_gap": true,
      "status": "MISSING"
    }
  ]
}
```

**This shows the device is missing WPC certification for India!**

---

## 🐛 Troubleshooting

### "Database connection failed"
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# If not running, start it
docker-compose up -d postgres

# Check logs
docker logs tamsys_postgres
```

### "Migration failed"
```bash
# Try manual migration
alembic upgrade head
```

### "MinIO connection failed"
```bash
# Check MinIO is running
docker ps | grep minio

# If not running, start it
docker-compose up -d minio

# Check logs
docker logs tamsys_minio
```

### Port already in use
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Kill the process or change the port
uvicorn app.main:app --reload --port 8001
```

---

## 🛑 Stopping Services

```bash
# Stop backend
# Press Ctrl+C in the terminal running uvicorn

# Stop Docker services
docker-compose down

# Stop and remove all data (WARNING: This deletes the database!)
docker-compose down -v
```

---

## 📚 Next Steps

1. ✅ Explore the Swagger UI: http://localhost:8000/docs
2. ✅ Seed global data (technologies, countries, certifications, rules)
3. ✅ Create tenants and devices
4. ✅ Test gap analysis with different scenarios
5. ✅ Upload certificate documents
6. ✅ Check MinIO Console: http://localhost:9001

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Change all passwords in `.env`
- [ ] Set `DEBUG=False`
- [ ] Enable HTTPS for MinIO (`MINIO_SECURE=True`)
- [ ] Setup Keycloak for authentication
- [ ] Configure email service (SendGrid/SMTP)
- [ ] Use managed database (AWS RDS, Azure Database)
- [ ] Setup monitoring and logging
- [ ] Configure backup strategy
- [ ] Setup CI/CD pipeline
- [ ] Load test the API
- [ ] Security audit

---

**Happy coding! 🚀**


