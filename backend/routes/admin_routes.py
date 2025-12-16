from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.db_setup import get_db
from backend.models.user_model import User
from backend.utils.auth_utils import get_current_user, get_current_admin_user

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    district: Optional[str] = None
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True

@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users in the system - only available to admin users
    """
    try:
        users = db.query(User).order_by(User.id.desc()).all()

        # Format the users to include datetime strings
        formatted_users = []
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "latitude": user.latitude,
                "longitude": user.longitude,
                "age": user.age,
                "gender": user.gender,
                "district": user.district,
            }

            # Add created_at and updated_at if they exist
            if hasattr(user, 'created_at') and user.created_at:
                user_dict["created_at"] = user.created_at.isoformat()
            if hasattr(user, 'updated_at') and user.updated_at:
                user_dict["updated_at"] = user.updated_at.isoformat()

            formatted_users.append(UserResponse(**user_dict))

        return formatted_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


@router.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID - only available to admin users
    """
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "latitude": user.latitude,
            "longitude": user.longitude,
            "age": user.age,
            "gender": user.gender,
            "district": user.district,
        }
        
        if hasattr(user, 'created_at') and user.created_at:
            user_dict["created_at"] = user.created_at.isoformat()
        if hasattr(user, 'updated_at') and user.updated_at:
            user_dict["updated_at"] = user.updated_at.isoformat()
        
        return UserResponse(**user_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's role - only available to admin users
    """
    
    # Verify the new role is valid
    valid_roles = ["civilian", "police", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = new_role
        db.commit()
        
        return {"message": f"User role updated to {new_role}", "user_id": user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user - only available to admin users
    """
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully", "user_id": user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")