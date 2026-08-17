from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Update this to use PostgreSQL. 
# You will replace the credentials with your actual database details later.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/exam_db"

# PostgreSQL doesn't need "check_same_thread": False
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()