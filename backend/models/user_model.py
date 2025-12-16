from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from backend.database.db_setup import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)  # Changed to nullable=True for police users who might use phone
    phone = Column(String, unique=True, index=True, nullable=True)  # Added phone field
    badge_id = Column(String, unique=True, index=True, nullable=True)  # Added badge ID field
    full_name = Column(String, nullable=True)  # Added full_name field
    password = Column(String, nullable=False)
    role = Column(String, default="civilian")  # "civilian", "police", or "admin"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo = Column(Text, nullable=True)  # Added photo field for base64 string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "badge_id": self.badge_id,
            "full_name": self.full_name,
            "role": self.role,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "photo": self.photo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }