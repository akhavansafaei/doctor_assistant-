"""Health profile API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.user import (
    HealthProfileCreate,
    HealthProfileResponse,
    HealthProfileUpdate,
    MedicalHistoryCreate,
    MedicalHistoryResponse
)
from app.api.auth import oauth2_scheme
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with database)
health_profiles_db = {}
medical_history_db = {}


@router.post("/health-profile", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_health_profile(
    profile: HealthProfileCreate,
    token: str = Depends(oauth2_scheme)
):
    """Create or update health profile"""
    # In production, get user_id from token
    user_id = 1  # Placeholder

    profile_id = len(health_profiles_db) + 1

    profile_data = {
        "id": profile_id,
        "user_id": user_id,
        **profile.model_dump(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    health_profiles_db[profile_id] = profile_data

    return HealthProfileResponse(**profile_data)


@router.get("/health-profile", response_model=HealthProfileResponse)
async def get_health_profile(token: str = Depends(oauth2_scheme)):
    """Get user's health profile"""
    # In production, get user_id from token
    user_id = 1

    # Find profile for user
    profile = next(
        (p for p in health_profiles_db.values() if p["user_id"] == user_id),
        None
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )

    return HealthProfileResponse(**profile)


@router.put("/health-profile", response_model=HealthProfileResponse)
async def update_health_profile(
    update_data: HealthProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update health profile"""
    user_id = 1  # Placeholder

    # Find existing profile
    profile = next(
        (p for p in health_profiles_db.values() if p["user_id"] == user_id),
        None
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            profile[key] = value

    profile["updated_at"] = datetime.utcnow()

    return HealthProfileResponse(**profile)


@router.post("/medical-history", response_model=MedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_medical_history(
    record: MedicalHistoryCreate,
    token: str = Depends(oauth2_scheme)
):
    """Add medical history record"""
    user_id = 1  # Placeholder

    record_id = len(medical_history_db) + 1

    record_data = {
        "id": record_id,
        "user_id": user_id,
        **record.model_dump(),
        "created_at": datetime.utcnow()
    }

    medical_history_db[record_id] = record_data

    return MedicalHistoryResponse(**record_data)


@router.get("/medical-history", response_model=List[MedicalHistoryResponse])
async def get_medical_history(token: str = Depends(oauth2_scheme)):
    """Get user's medical history"""
    user_id = 1  # Placeholder

    records = [
        MedicalHistoryResponse(**record)
        for record in medical_history_db.values()
        if record["user_id"] == user_id
    ]

    return records


@router.get("/timeline")
async def get_health_timeline(token: str = Depends(oauth2_scheme)):
    """Get health timeline visualization data"""
    user_id = 1  # Placeholder

    # Get all medical records sorted by date
    records = sorted(
        [r for r in medical_history_db.values() if r["user_id"] == user_id],
        key=lambda x: x["record_date"],
        reverse=True
    )

    timeline = []
    for record in records:
        timeline.append({
            "date": record["record_date"].isoformat(),
            "type": record["record_type"],
            "title": record.get("diagnosis_name", "Medical Event"),
            "description": record.get("notes", ""),
            "details": {
                "diagnosis_code": record.get("diagnosis_code"),
                "prescribed_by": record.get("prescribed_by")
            }
        })

    return {
        "user_id": user_id,
        "timeline": timeline,
        "total_records": len(timeline)
    }
