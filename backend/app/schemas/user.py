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


class ClientProfileBase(BaseModel):
    """Base client profile schema"""
    occupation: Optional[str] = None
    employer: Optional[str] = None
    citizenship: Optional[str] = None
    marital_status: Optional[str] = None


class ClientProfileCreate(ClientProfileBase):
    """Client profile creation"""
    legal_areas_of_interest: Optional[List[str]] = []
    active_legal_matters: Optional[List[Dict[str, Any]]] = []
    previous_legal_issues: Optional[List[Dict[str, Any]]] = []
    legal_restrictions: Optional[List[Dict[str, Any]]] = []

    business_entities: Optional[List[Dict[str, Any]]] = []
    financial_concerns: Optional[List[str]] = []

    preferred_communication: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class ClientProfileUpdate(ClientProfileBase):
    """Client profile update (partial)"""
    legal_areas_of_interest: Optional[List[str]] = None
    active_legal_matters: Optional[List[Dict[str, Any]]] = None
    previous_legal_issues: Optional[List[Dict[str, Any]]] = None
    legal_restrictions: Optional[List[Dict[str, Any]]] = None
    business_entities: Optional[List[Dict[str, Any]]] = None
    financial_concerns: Optional[List[str]] = None


class ClientProfileResponse(ClientProfileBase):
    """Client profile response"""
    id: int
    user_id: int
    legal_areas_of_interest: Optional[List[str]] = None
    active_legal_matters: Optional[List[Dict[str, Any]]] = None
    previous_legal_issues: Optional[List[Dict[str, Any]]] = None
    legal_restrictions: Optional[List[Dict[str, Any]]] = None
    business_entities: Optional[List[Dict[str, Any]]] = None
    financial_concerns: Optional[List[str]] = None

    preferred_communication: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseHistoryCreate(BaseModel):
    """Legal case history record creation"""
    record_type: str = Field(..., regex="^(case|consultation|document_review|court_appearance)$")
    record_date: datetime
    case_number: Optional[str] = None
    case_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    legal_issue: Optional[str] = None
    case_status: Optional[str] = None
    handled_by: Optional[str] = None
    law_firm: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    documents: Optional[List[str]] = None


class CaseHistoryResponse(BaseModel):
    """Legal case history response"""
    id: int
    record_type: str
    record_date: datetime
    case_number: Optional[str] = None
    case_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    legal_issue: Optional[str] = None
    case_status: Optional[str] = None
    handled_by: Optional[str] = None
    law_firm: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
