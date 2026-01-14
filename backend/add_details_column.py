import sys
import os
from sqlalchemy import create_engine, text

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.core.config import settings

def migrate():
    print(f"Connecting to database...")
    # SQL Alchemy URL
    url = settings.DATABASE_URL
    print(f"URL: {url}")
    
    engine = create_engine(url)
    
    try:
        with engine.connect() as conn:
            # Using JSONB is better for Postgres, but let's stick to what SQLAlchemy expects.
            # Actually, let's use JSONB if it's Postgres, as it allows indexing if we ever need it.
            # But for simple storage, JSON is fine.
            # Let's try adding it.
            
            sql = "ALTER TABLE global_countries ADD COLUMN IF NOT EXISTS details JSONB"
            
            print(f"Executing: {sql}")
            conn.execute(text(sql))
            conn.commit()
            print("Successfully added 'details' column.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        # Identify if it's because JSONB isn't supported (unlikely in modern PG) or table missing
        
if __name__ == "__main__":
    migrate()
