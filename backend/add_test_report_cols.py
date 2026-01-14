import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path so we can import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def migrate_db():
    print(f"Connecting to database at {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as connection:
        # Check if columns exist
        print("Checking for existing columns...")
        result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='compliance_records'"))
        existing_columns = [row[0] for row in result]
        
        columns_to_add = [
            ("test_report_path", "TEXT"),
            ("test_report_filename", "VARCHAR(255)"),
            ("test_report_mime_type", "VARCHAR(100)")
        ]

        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column {col_name}...")
                try:
                    connection.execute(text(f"ALTER TABLE compliance_records ADD COLUMN {col_name} {col_type}"))
                    print(f"Successfully added {col_name}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists.")
        
        connection.commit()
        print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_db()
