"""Pydantic schemas for chat API"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=10000)


class MessageCreate(MessageBase):
    """Message creation schema"""
    conversation_id: Optional[str] = None
    attachments: Optional[List[str]] = None


class MessageResponse(BaseModel):
    """Message response schema"""
    id: int
    role: str
    content: str
    agent_type: Optional[str] = None
    confidence_score: Optional[float] = None
    rag_sources: Optional[List[Dict[str, Any]]] = None
    reasoning_chain: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Conversation creation schema"""
    initial_complaint: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: int
    session_id: str
    title: Optional[str] = None
    severity_level: Optional[str] = None
    recommended_specialty: Optional[str] = None
    status: str
    started_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    include_sources: bool = True
    enable_agents: bool = True


class ChatResponse(BaseModel):
    """Chat response schema"""
    session_id: str
    message: str
    agent_type: Optional[str] = None
    confidence_score: Optional[float] = None
    severity_level: Optional[str] = None
    emergency_detected: bool = False

    # Explainability
    sources: Optional[List[Dict[str, Any]]] = None
    reasoning: Optional[List[str]] = None

    # Recommendations
    differential_diagnoses: Optional[List[Dict[str, Any]]] = None
    recommended_actions: Optional[List[str]] = None
    specialist_referral: Optional[str] = None

    # Medical disclaimer
    disclaimer: str = Field(
        default="This is an AI assistant and not a substitute for professional medical advice. "
        "Always consult with a qualified healthcare provider for medical decisions."
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoiceRequest(BaseModel):
    """Voice input request"""
    audio_base64: str
    session_id: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    """Image analysis request"""
    image_base64: str
    image_type: str = Field(..., regex="^(skin|xray|lab_report|prescription)$")
    session_id: Optional[str] = None
    additional_context: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    """Image analysis response"""
    analysis: str
    detected_conditions: Optional[List[str]] = None
    confidence_scores: Optional[Dict[str, float]] = None
    recommendations: Optional[List[str]] = None
    requires_urgent_care: bool = False
    disclaimer: str = Field(
        default="AI image analysis is preliminary. Always get a professional medical evaluation."
    )
