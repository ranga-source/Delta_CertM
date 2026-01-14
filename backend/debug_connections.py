import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from minio import Minio
from minio.error import S3Error
import urllib3

# Load env
load_dotenv()

def check_postgres():
    print("-" * 20)
    print("Checking PostgreSQL...")
    db_url = f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    print(f"URL: {db_url.replace(os.getenv('DATABASE_PASSWORD'), '***')}")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL Connection Successful!")
    except Exception as e:
        print(f"❌ PostgreSQL Failed: {e}")

def check_minio():
    print("-" * 20)
    print("Checking MinIO...")
    endpoint = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = "certificates"
    
    print(f"Endpoint: {endpoint}")
    try:
        # Check raw HTTP first
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', f'http://{endpoint}/minio/health/live')
            print(f"MinIO Health Check: {r.status} (Raw HTTP)")
        except Exception as e:
            print(f"⚠️ Raw HTTP Check Failed: {e}")

        # Check MinIO Client
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        if not client.bucket_exists(bucket):
            print(f"Bucket '{bucket}' does not exist. Attempting creation...")
            client.make_bucket(bucket)
            print(f"✅ Bucket '{bucket}' created.")
        else:
            print(f"✅ Bucket '{bucket}' exists.")
        print("✅ MinIO Client Connection Successful!")
        
    except Exception as e:
        print(f"❌ MinIO Failed: {e}")

if __name__ == "__main__":
    check_postgres()
    check_minio()
