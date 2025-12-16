from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator, EmailStr
from sqlalchemy.orm import Session
from backend.database.db_setup import SessionLocal, get_db
from backend.models.user_model import User
from backend.utils.security import hash_password, verify_password
from backend.schemas.user_schemas import UpdateLocationSchema
from backend.utils.auth_utils import get_current_user
import re
from typing import Optional

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    username: str  # This will be the full name from frontend
    email: EmailStr
    password: str
    role: str = "civilian"
    age: Optional[int] = None
    gender: Optional[str] = None
    district: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        # Allow full names with spaces, uppercase, special characters
        pattern = r'^[A-Za-zÀ-ÿ\s\-.\']+$'
        if not re.match(pattern, v):
            raise ValueError('Name can only contain letters, spaces, hyphens, apostrophes, and periods')
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 50:
            raise ValueError('Name must be at most 50 characters long')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Signup route
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username (full name) already exists - optional, since names can be the same
    # You might want to skip this or handle it differently
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        # If username exists, you could append a number or ask user to choose different
        # For now, we'll allow duplicate names since they're common
        pass
    
    # Create new user - using username as both username and full_name
    new_user = User(
        username=user.username,  # This is the full name
        email=user.email,
        full_name=user.username,  # Store the same in full_name field
        password=hash_password(user.password),
        role=user.role,
        age=user.age,
        gender=user.gender,
        district=user.district
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully", 
        "user_id": new_user.id,
        "username": new_user.username,  # This is the full name
        "email": new_user.email,
        "role": new_user.role
    }

# Login route
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "message": f"Welcome {db_user.username}",  # Using username (which is full name)
        "user_id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role
    }

# Update location route
@router.put("/update-location")
def update_location(
    location: UpdateLocationSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.latitude = location.latitude
    user.longitude = location.longitude
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Location updated successfully",
        "latitude": user.latitude,
        "longitude": user.longitude
    }

# Get user profile route
@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,  # This is the full name
        "email": user.email,
        "role": user.role,
        "age": user.age,
        "gender": user.gender,
        "district": user.district,
        "latitude": user.latitude,
        "longitude": user.longitude
    }

# Token refresh route
@router.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise credentials_exception

        # Create new access token
        access_token_data = {
            "user_id": user.id,
            "role": user.role,
            "username": user.username
        }
        new_access_token = create_access_token(access_token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise credentials_exception

# Update user profile route
@router.put("/profile")
def update_profile(
    username: Optional[str] = None,  # This is the full name
    age: Optional[int] = None,
    gender: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if username is not None:
        # Validate username (full name)
        pattern = r'^[A-Za-zÀ-ÿ\s\-.\']+$'
        if not re.match(pattern, username):
            raise HTTPException(status_code=400, detail="Name can only contain letters, spaces, hyphens, apostrophes, and periods")
        if len(username) < 2 or len(username) > 50:
            raise HTTPException(status_code=400, detail="Name must be between 2 and 50 characters")
        user.username = username
        user.full_name = username  # Update both fields
    
    if age is not None:
        if age < 18 or age > 120:
            raise HTTPException(status_code=400, detail="Age must be between 18 and 120")
        user.age = age
    
    if gender is not None:
        user.gender = gender
    
    if district is not None:
        user.district = district
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Profile updated successfully",
        "username": user.username,  # This is the full name
        "age": user.age,
        "gender": user.gender,
        "district": user.district
    }