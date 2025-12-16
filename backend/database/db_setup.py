from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database (file-based)
SQLALCHEMY_DATABASE_URL = "sqlite:///./police_security.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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