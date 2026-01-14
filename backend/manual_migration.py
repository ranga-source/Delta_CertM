
from sqlalchemy import text
from app.core.database import SessionLocal

def run_manual_migration():
    db = SessionLocal()
    try:
        print("Attempting to manually add columns to global_certifications table...")
        
        # Check if columns exist first (idempotency)
        # We can just try to add them and catch the error if they exist
        
        try:
            db.execute(text("ALTER TABLE global_certifications ADD COLUMN branding_image_url VARCHAR(255)"))
            print("Added branding_image_url column.")
        except Exception as e:
            print(f"branding_image_url might already exist: {e}")
            db.rollback()

        try:
            db.execute(text("ALTER TABLE global_certifications ADD COLUMN labeling_requirements TEXT"))
            print("Added labeling_requirements column.")
        except Exception as e:
            print(f"labeling_requirements might already exist: {e}")
            db.rollback()

        db.commit()
        print("Manual migration completed.")
        
    except Exception as e:
        print(f"Critical Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_manual_migration()
