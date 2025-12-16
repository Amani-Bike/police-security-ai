from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db_setup import get_db
from backend.models.user_model import User
from backend.models.emergency_model import EmergencyReport
from backend.utils.auth_utils import get_current_user, get_current_police_user

router = APIRouter()

class EmergencyReportCreate(BaseModel):
    emergency_type: str
    description: str
    latitude: float
    longitude: float

class EmergencyStatusUpdate(BaseModel):
    status: str  # active, in_progress, resolved

@router.post("/report-emergency")
def report_emergency(
    emergency: EmergencyReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Validate emergency type
        valid_types = ['medical', 'crime', 'fire', 'accident', 'other']
        if emergency.emergency_type not in valid_types:
            raise HTTPException(status_code=400, detail="Invalid emergency type")
        
        # Validate Malawi coordinates
        if not (-17.5 <= emergency.latitude <= -9.0) or not (32.5 <= emergency.longitude <= 36.0):
            raise HTTPException(status_code=400, detail="Location must be within Malawi")
        
        # Create emergency report
        new_emergency = EmergencyReport(
            user_id=current_user.id,
            username=current_user.username,
            emergency_type=emergency.emergency_type,
            description=emergency.description,
            latitude=emergency.latitude,
            longitude=emergency.longitude,
            status="active"
        )
        
        db.add(new_emergency)
        db.commit()
        db.refresh(new_emergency)
        
        return {
            "message": "Emergency reported successfully! Help is on the way.",
            "emergency_id": new_emergency.id,
            "timestamp": new_emergency.created_at.isoformat() if new_emergency.created_at else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error reporting emergency: {str(e)}")

@router.get("/emergencies")
def get_emergencies(
    status: str = "active",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_police_user)
):
    try:
        # Get emergencies filtered by status
        if status == "all":
            emergencies = db.query(EmergencyReport).order_by(EmergencyReport.created_at.desc()).all()
        else:
            emergencies = db.query(EmergencyReport).filter(
                EmergencyReport.status == status
            ).order_by(EmergencyReport.created_at.desc()).all()
        
        return [emergency.to_dict() for emergency in emergencies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emergencies: {str(e)}")

@router.put("/emergencies/{emergency_id}/status")
def update_emergency_status(
    emergency_id: int,
    status_update: EmergencyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_police_user)
):
    try:
        emergency = db.query(EmergencyReport).filter(EmergencyReport.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency report not found")
        
        valid_statuses = ['active', 'in_progress', 'resolved']
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        emergency.status = status_update.status
        if status_update.status == "resolved":
            emergency.resolved_by = current_user.id
        
        db.commit()
        
        return {
            "message": f"Emergency status updated to {status_update.status}",
            "emergency_id": emergency_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating emergency: {str(e)}")

@router.get("/my-emergencies")
def get_my_emergencies(
    status: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get emergencies reported by the current user"""
    try:
        if status == "all":
            emergencies = db.query(EmergencyReport).filter(
                EmergencyReport.user_id == current_user.id
            ).order_by(EmergencyReport.created_at.desc()).all()
        else:
            emergencies = db.query(EmergencyReport).filter(
                EmergencyReport.user_id == current_user.id,
                EmergencyReport.status == status
            ).order_by(EmergencyReport.created_at.desc()).all()

        return [{
            "id": emergency.id,
            "user_id": emergency.user_id,
            "username": emergency.username,
            "emergency_type": emergency.emergency_type,
            "description": emergency.description,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude,
            "status": emergency.status,
            "created_at": emergency.created_at.isoformat() if emergency.created_at else None,
            "updated_at": emergency.updated_at.isoformat() if emergency.updated_at else None
        } for emergency in emergencies]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user emergencies: {str(e)}")


@router.get("/active-emergencies")
def get_active_emergencies_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_police_user)
):
    """Get only active emergencies for map display"""
    try:
        active_emergencies = db.query(EmergencyReport).filter(
            EmergencyReport.status == "active"
        ).all()

        return [{
            "id": emergency.id,
            "user_id": emergency.user_id,
            "username": emergency.username,
            "emergency_type": emergency.emergency_type,
            "description": emergency.description,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude,
            "created_at": emergency.created_at.isoformat() if emergency.created_at else None
        } for emergency in active_emergencies]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active emergencies: {str(e)}")