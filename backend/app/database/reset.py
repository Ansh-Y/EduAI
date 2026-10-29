import os
import shutil
from app.core.config import settings
from app.database.session import engine, Base, SessionLocal
from app.database.init_db import init_and_seed_db

def reset_database():
    print("Resetting EduAI database...")
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed {db_file}")
        
    Base.metadata.drop_all(bind=engine)
    db = SessionLocal()
    try:
        init_and_seed_db(db)
        print("Database successfully restored to clean demonstration seed state!")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
