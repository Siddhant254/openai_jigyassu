from db.database import engine  # Your SQLAlchemy engine
from models.models import Base      # Your Base metadata

def reset_db():
    Base.metadata.drop_all(bind=engine)   # Drop all existing tables
    Base.metadata.create_all(bind=engine) # Create tables as per models

if __name__ == "__main__":
    reset_db()
    print("Database reset complete.")
