from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db_setup import SessionLocal
from backend.models.user_model import User
from backend.utils.auth_utils import get_current_police_user  # Use police-only dependency

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/civilians")
def get_civilian_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_police_user)  # Automatically checks for police role
):
    try:
        # Only police can access this (already enforced by get_current_police_user)
        civilians = db.query(User).filter(User.role == "civilian").all()

        return [
            {
                "id": c.id, 
                "username": c.username, 
                "latitude": c.latitude, 
                "longitude": c.longitude,
                "email": c.email
            }
            for c in civilians if c.latitude is not None and c.longitude is not None
        ]
        
    except Exception as e:
        print("Error fetching civilians:", e)
        raise HTTPException(status_code=500, detail="Error fetching civilian data")