import uvicorn
import os
import sys

# Add the current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting TAMSys Backend on {settings.HOST_IP}:8000")
    print(f"MinIO Endpoint: {settings.EFFECTIVE_MINIO_ENDPOINT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST_IP,
        port=8000,
        reload=True
    )
