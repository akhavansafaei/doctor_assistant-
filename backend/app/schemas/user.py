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
    """Fitness profile creation"""
    # Fitness-specific fields
    fitness_level: Optional[str] = None  # beginner, intermediate, advanced
    training_experience: Optional[str] = None  # e.g., "2 years", "6 months"
    fitness_goals: Optional[List[str]] = []  # muscle gain, fat loss, strength, athletic performance

    available_equipment: Optional[List[str]] = []  # full gym, dumbbells, bodyweight, etc.
    training_days_per_week: Optional[int] = None
    training_duration_minutes: Optional[int] = None

    # Health and injury tracking
    current_injuries: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []

    # Nutrition preferences
    diet_preference: Optional[str] = None  # Persian cuisine, flexible, etc.
    dietary_restrictions: Optional[List[str]] = []  # vegetarian, vegan, etc.
    food_allergies: Optional[List[str]] = []

    # Lifestyle
    exercise_frequency: Optional[str] = None

    # Body composition tracking
    body_fat_percentage: Optional[float] = None
    body_measurements: Optional[Dict[str, float]] = {}  # chest, waist, hips, arms, etc.

    # Legacy medical fields (optional, kept for health conditions)
    chronic_conditions: Optional[List[str]] = []  # deprecated, use health_conditions
    current_medications: Optional[List[Dict[str, Any]]] = []

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class HealthProfileUpdate(HealthProfileBase):
    """Fitness profile update (partial)"""
    fitness_level: Optional[str] = None
    training_experience: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    available_equipment: Optional[List[str]] = None
    training_days_per_week: Optional[int] = None
    training_duration_minutes: Optional[int] = None
    current_injuries: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    diet_preference: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    food_allergies: Optional[List[str]] = None
    body_fat_percentage: Optional[float] = None
    body_measurements: Optional[Dict[str, float]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None


class HealthProfileResponse(HealthProfileBase):
    """Fitness profile response"""
    id: int
    user_id: int

    # Fitness fields
    fitness_level: Optional[str] = None
    training_experience: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    available_equipment: Optional[List[str]] = None
    training_days_per_week: Optional[int] = None
    training_duration_minutes: Optional[int] = None
    current_injuries: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    diet_preference: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    food_allergies: Optional[List[str]] = None
    exercise_frequency: Optional[str] = None
    body_fat_percentage: Optional[float] = None
    body_measurements: Optional[Dict[str, float]] = None

    # Legacy medical fields
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[List[Dict[str, Any]]] = None

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
