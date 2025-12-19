from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use DATABASE_URL from environment variable if set (for Render/production), otherwise use local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./police_security.db")

# Check if it's a PostgreSQL URL (for Render) or SQLite
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
    print("Using PostgreSQL database for production")
else:
    # SQLite database (file-based) - for Render, it's better to use temp file due to ephemeral storage
    # But for basic deployment, we'll stick with file-based
    if "RENDER" in os.environ:
        # On Render, SQLite file will be lost after each deploy, warn user
        print("WARNING: Using SQLite on Render. Data will not persist between deploys.")
        print("Consider using PostgreSQL for production.")
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