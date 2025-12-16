from backend.database.db_setup import Base, engine

# Import all models to ensure they are registered with Base before creating tables
from backend.models.user_model import User
from backend.models.emergency_model import EmergencyReport
from backend.models.chat_model import ChatSession, ChatMessage

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")