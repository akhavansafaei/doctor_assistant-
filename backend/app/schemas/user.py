"""Pydantic schemas for user management"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=8, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class HealthProfileBase(BaseModel):
    """Base health profile schema"""
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    blood_type: Optional[str] = None


class HealthProfileCreate(HealthProfileBase):
    """Health profile creation"""
    chronic_conditions: Optional[List[str]] = []
    allergies: Optional[Dict[str, List[str]]] = {
        "drug": [],
        "food": [],
        "environmental": []
    }
    current_medications: Optional[List[Dict[str, Any]]] = []
    past_surgeries: Optional[List[Dict[str, Any]]] = []
    family_history: Optional[Dict[str, List[str]]] = {}

    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    diet_type: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class HealthProfileUpdate(HealthProfileBase):
    """Health profile update (partial)"""
    chronic_conditions: Optional[List[str]] = None
    allergies: Optional[Dict[str, List[str]]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None
    past_surgeries: Optional[List[Dict[str, Any]]] = None
    family_history: Optional[Dict[str, List[str]]] = None


class HealthProfileResponse(HealthProfileBase):
    """Health profile response"""
    id: int
    user_id: int
    chronic_conditions: Optional[List[str]] = None
    allergies: Optional[Dict[str, List[str]]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None
    past_surgeries: Optional[List[Dict[str, Any]]] = None
    family_history: Optional[Dict[str, List[str]]] = None

    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    diet_type: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalHistoryCreate(BaseModel):
    """Medical history record creation"""
    record_type: str = Field(..., regex="^(diagnosis|treatment|lab_result|prescription)$")
    record_date: datetime
    diagnosis_code: Optional[str] = None
    diagnosis_name: Optional[str] = None
    prescribed_by: Optional[str] = None
    prescription_details: Optional[Dict[str, Any]] = None
    lab_results: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    documents: Optional[List[str]] = None


class MedicalHistoryResponse(BaseModel):
    """Medical history response"""
    id: int
    record_type: str
    record_date: datetime
    diagnosis_code: Optional[str] = None
    diagnosis_name: Optional[str] = None
    prescribed_by: Optional[str] = None
    prescription_details: Optional[Dict[str, Any]] = None
    lab_results: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
