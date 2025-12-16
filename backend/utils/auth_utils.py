from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import re

from backend.utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.database.db_setup import SessionLocal
from backend.models.user_model import User
from backend.database.db_setup import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Create refresh token
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Refresh tokens should last longer, e.g., 7 days
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Enhanced dependency to get current user with role validation
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")

        if user_id is None or role is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise credentials_exception

        return user

    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Police-only access dependency
def get_current_police_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "police":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Police role required."
        )
    return current_user

# Civilian-only access dependency
def get_current_civilian_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "civilian":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Civilian role required."
        )
    return current_user

# Admin-only access dependency
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

# Input validation utilities
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    # Remove spaces, dashes, and parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's a valid phone number format (international format starting with + or 10-15 digits)
    pattern = r'^(\+\d{1,3})?\d{10,15}$'
    if re.match(pattern, cleaned_phone) and len(cleaned_phone) <= 15:
        return True
    return False

def validate_police_identifier(identifier: str) -> tuple[bool, str]:  # Returns (is_valid, type)
    """
    Validates if the input is either a valid email or phone number for police signup
    """
    if validate_email(identifier):
        return True, "email"
    elif validate_phone(identifier):
        return True, "phone"
    return False, ""

def validate_password(password: str) -> dict:
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_username(username: str) -> dict:
    errors = []

    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    if len(username) > 20:
        errors.append("Username must be less than 20 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append("Username can only contain letters, numbers, and underscores")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_full_name(full_name: str) -> dict:
    errors = []

    if len(full_name) < 2:
        errors.append("Full name must be at least 2 characters long")
    if len(full_name) > 50:
        errors.append("Full name must be less than 50 characters")
    # Allow letters, spaces, hyphens, apostrophes, and periods for names
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', full_name):
        errors.append("Full name can only contain letters, spaces, hyphens, apostrophes, and periods")
    if '  ' in full_name:  # Check for multiple consecutive spaces
        errors.append("Full name cannot contain multiple consecutive spaces")
    if full_name != full_name.strip():  # Check if it starts/ends with whitespace
        errors.append("Full name cannot start or end with whitespace")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }