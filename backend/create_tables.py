
from app.core.database import engine, Base
# Import all models to ensure they are registered with Base
from app.models import global_data 

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
