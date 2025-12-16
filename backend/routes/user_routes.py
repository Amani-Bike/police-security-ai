from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.database.db_setup import SessionLocal
from backend.models.user_model import User
from backend.utils.security import hash_password, verify_password
from backend.utils.auth_utils import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_police_user,
    get_current_civilian_user,
    validate_email,
    validate_password,
    validate_username,
    validate_police_identifier,
    validate_full_name
)
from backend.schemas.user_schemas import UpdateLocationSchema

router = APIRouter()

# Pydantic models with validation
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str = None
    password: str
    role: str = "civilian"

class CivilianSignupRequest(BaseModel):
    username: str
    email: str
    full_name: str = None
    password: str
    role: str = "civilian"

class PoliceSignupRequest(BaseModel):
    username: str
    identifier: str  # Either email or phone number
    password: str
    full_name: str = None
    badge_id: str = None
    age: int = None
    district: str = None
    role: str = "police"

class UserLogin(BaseModel):
    email: str
    password: str

class PoliceLoginRequest(BaseModel):
    identifier: str  # Can be email or badge ID
    password: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enhanced signup route with validation for civilians
@router.post("/signup")
def signup(user: CivilianSignupRequest, db: Session = Depends(get_db)):
    try:
        # Validate inputs
        if not validate_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # For civilian signup, validate username as a full name if it contains spaces
        # otherwise use traditional username validation
        if ' ' in user.username:
            # Username contains spaces, treat as a full name
            full_name_validation = validate_full_name(user.username)
            if not full_name_validation["is_valid"]:
                raise HTTPException(status_code=400, detail="; ".join(full_name_validation["errors"]))
        else:
            # No spaces, use traditional username validation
            username_validation = validate_username(user.username)
            if not username_validation["is_valid"]:
                raise HTTPException(status_code=400, detail="; ".join(username_validation["errors"]))

        password_validation = validate_password(user.password)
        if not password_validation["is_valid"]:
            raise HTTPException(status_code=400, detail="; ".join(password_validation["errors"]))

        # Validate full_name if provided
        if user.full_name:
            full_name_validation = validate_full_name(user.full_name)
            if not full_name_validation["is_valid"]:
                raise HTTPException(status_code=400, detail="; ".join(full_name_validation["errors"]))

        if user.role not in ["civilian", "police"]:
            raise HTTPException(status_code=400, detail="Role must be either 'civilian' or 'police'")

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create new user
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            password=hash_password(user.password),
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "user_id": new_user.id,
            "role": new_user.role
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Signup error:", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during signup")

# Police signup route that accepts either email or phone number
@router.post("/signup/police")
def police_signup(police_user: PoliceSignupRequest, db: Session = Depends(get_db)):
    try:
        # Validate inputs
        validation_result, identifier_type = validate_police_identifier(police_user.identifier)
        if not validation_result:
            raise HTTPException(status_code=400, detail="Invalid email or phone number format")

        # For police signup, validate as full name (allowing spaces and more characters) rather than strict username
        full_name_validation = validate_full_name(police_user.username)
        if not full_name_validation["is_valid"]:
            raise HTTPException(status_code=400, detail="; ".join(full_name_validation["errors"]))

        password_validation = validate_password(police_user.password)
        if not password_validation["is_valid"]:
            raise HTTPException(status_code=400, detail="; ".join(password_validation["errors"]))

        # Check if user already exists by email or phone
        if identifier_type == "email":
            existing_user = db.query(User).filter(User.email == police_user.identifier).first()
        else:  # phone
            existing_user = db.query(User).filter(User.phone == police_user.identifier).first()

        if existing_user:
            raise HTTPException(status_code=400, detail=f"User with this {'email' if identifier_type == 'email' else 'phone number'} already registered")

        # Check if username already exists (derived from full name)
        system_username = f"officer_{police_user.username.replace(' ', '_').lower()}"
        existing_username = db.query(User).filter(User.username == system_username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Also check if badge ID already exists (if provided)
        if police_user.badge_id:
            existing_badge = db.query(User).filter(User.badge_id == police_user.badge_id).first()
            if existing_badge:
                raise HTTPException(status_code=400, detail="Badge ID already registered")

        # Create new police user
        new_user = User(
            username=system_username,
            email=police_user.identifier if identifier_type == "email" else None,
            phone=police_user.identifier if identifier_type == "phone" else None,
            badge_id=police_user.badge_id,
            full_name=police_user.username,  # Store the full name in the full_name field
            password=hash_password(police_user.password),
            role="police"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "Police officer registered successfully",
            "user_id": new_user.id,
            "role": new_user.role
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Police signup error:", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during police signup")

# Enhanced login route for civilians
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        # Basic validation
        if not user.email or not user.password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        if not validate_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Find user
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT token with role
        token_data = {
            "user_id": db_user.id,
            "role": db_user.role,
            "username": db_user.username
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": f"Welcome {db_user.username}",
            "role": db_user.role,
            "user_id": db_user.id
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Login error:", e)
        raise HTTPException(status_code=500, detail="Internal server error during login")

# Police login route that accepts email, phone number, or badge ID
@router.post("/login/police")
def police_login(login_request: PoliceLoginRequest, db: Session = Depends(get_db)):
    try:
        # Basic validation
        if not login_request.identifier or not login_request.password:
            raise HTTPException(status_code=400, detail="Email/badge ID and password are required")

        # Try to find by badge ID first
        db_user = db.query(User).filter(User.badge_id == login_request.identifier).first()

        # If not found by badge ID, try to find by email
        if not db_user:
            if validate_email(login_request.identifier):
                db_user = db.query(User).filter(User.email == login_request.identifier).first()
            else:
                # Check if it could be a phone number
                db_user = db.query(User).filter(User.phone == login_request.identifier).first()

        # Verify password
        if not db_user or not verify_password(login_request.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Ensure user is police
        if db_user.role != "police":
            raise HTTPException(status_code=401, detail="Access denied. Police role required.")

        # Create JWT token with role
        token_data = {
            "user_id": db_user.id,
            "role": db_user.role,
            "username": db_user.username
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": f"Welcome {db_user.username}",
            "role": db_user.role,
            "user_id": db_user.id
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Police login error:", e)
        raise HTTPException(status_code=500, detail="Internal server error during police login")

# Protected routes with role-specific dependencies
@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "latitude": current_user.latitude,
        "longitude": current_user.longitude
    }

@router.put("/update-location")
def update_location(
    location: UpdateLocationSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_civilian_user)  # Only civilians can update location
):
    try:
        # Validate location coordinates (Malawi bounds)
        if not (-17.5 <= location.latitude <= -9.0) or not (32.5 <= location.longitude <= 36.0):
            raise HTTPException(
                status_code=400, 
                detail="Location must be within Malawi boundaries"
            )

        # Re-fetch user in the current session
        user_in_db = db.query(User).filter(User.id == current_user.id).first()
        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")

        user_in_db.latitude = location.latitude
        user_in_db.longitude = location.longitude

        db.commit()
        db.refresh(user_in_db)

        return {
            "message": "Location updated successfully",
            "user_id": user_in_db.id,
            "latitude": user_in_db.latitude,
            "longitude": user_in_db.longitude
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Update location error:", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Server error updating location")