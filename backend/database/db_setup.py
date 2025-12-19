from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use DATABASE_URL from environment variable if set (for Render/production), otherwise use local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./police_security.db")

# Check if it's a PostgreSQL URL (for Render) or SQLite
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    # SQLite database (file-based)
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with Base
from backend.models.user_model import User
from backend.models.emergency_model import EmergencyReport
from backend.models.chat_model import ChatSession, ChatMessage

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Call this function when your application starts
create_tables()