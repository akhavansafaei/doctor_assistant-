"""Client profile API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.user import (
    ClientProfileCreate,
    ClientProfileResponse,
    ClientProfileUpdate,
    CaseHistoryCreate,
    CaseHistoryResponse
)
from app.api.auth import oauth2_scheme
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with database)
client_profiles_db = {}
case_history_db = {}


@router.post("/client-profile", response_model=ClientProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_client_profile(
    profile: ClientProfileCreate,
    token: str = Depends(oauth2_scheme)
):
    """Create or update client profile"""
    # In production, get user_id from token
    user_id = 1  # Placeholder

    profile_id = len(client_profiles_db) + 1

    profile_data = {
        "id": profile_id,
        "user_id": user_id,
        **profile.model_dump(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    client_profiles_db[profile_id] = profile_data

    return ClientProfileResponse(**profile_data)


@router.get("/client-profile", response_model=ClientProfileResponse)
async def get_client_profile(token: str = Depends(oauth2_scheme)):
    """Get user's client profile"""
    # In production, get user_id from token
    user_id = 1

    # Find profile for user
    profile = next(
        (p for p in client_profiles_db.values() if p["user_id"] == user_id),
        None
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )

    return ClientProfileResponse(**profile)


@router.put("/client-profile", response_model=ClientProfileResponse)
async def update_client_profile(
    update_data: ClientProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update client profile"""
    user_id = 1  # Placeholder

    # Find existing profile
    profile = next(
        (p for p in client_profiles_db.values() if p["user_id"] == user_id),
        None
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            profile[key] = value

    profile["updated_at"] = datetime.utcnow()

    return ClientProfileResponse(**profile)


@router.post("/case-history", response_model=CaseHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_case_history(
    record: CaseHistoryCreate,
    token: str = Depends(oauth2_scheme)
):
    """Add case history record"""
    user_id = 1  # Placeholder

    record_id = len(case_history_db) + 1

    record_data = {
        "id": record_id,
        "user_id": user_id,
        **record.model_dump(),
        "created_at": datetime.utcnow()
    }

    case_history_db[record_id] = record_data

    return CaseHistoryResponse(**record_data)


@router.get("/case-history", response_model=List[CaseHistoryResponse])
async def get_case_history(token: str = Depends(oauth2_scheme)):
    """Get user's case history"""
    user_id = 1  # Placeholder

    records = [
        CaseHistoryResponse(**record)
        for record in case_history_db.values()
        if record["user_id"] == user_id
    ]

    return records


@router.get("/timeline")
async def get_case_timeline(token: str = Depends(oauth2_scheme)):
    """Get case timeline visualization data"""
    user_id = 1  # Placeholder

    # Get all case records sorted by date
    records = sorted(
        [r for r in case_history_db.values() if r["user_id"] == user_id],
        key=lambda x: x["record_date"],
        reverse=True
    )

    timeline = []
    for record in records:
        timeline.append({
            "date": record["record_date"].isoformat(),
            "type": record["record_type"],
            "title": record.get("case_number", "Legal Event"),
            "description": record.get("notes", ""),
            "details": {
                "case_type": record.get("case_type"),
                "jurisdiction": record.get("jurisdiction"),
                "handled_by": record.get("handled_by")
            }
        })

    return {
        "user_id": user_id,
        "timeline": timeline,
        "total_records": len(timeline)
    }
