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
    initial_inquiry: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: int
    session_id: str
    title: Optional[str] = None
    urgency_level: Optional[str] = None
    recommended_legal_area: Optional[str] = None
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
    urgency_level: Optional[str] = None
    urgent_matter_detected: bool = False

    # Explainability
    sources: Optional[List[Dict[str, Any]]] = None
    reasoning: Optional[List[str]] = None

    # Recommendations
    legal_issues_identified: Optional[List[Dict[str, Any]]] = None
    recommended_actions: Optional[List[str]] = None
    legal_area_referral: Optional[str] = None

    # Legal disclaimer
    disclaimer: str = Field(
        default="This is an AI assistant and not a substitute for professional legal advice. "
        "Always consult with a qualified attorney for legal decisions and representation."
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoiceRequest(BaseModel):
    """Voice input request"""
    audio_base64: str
    session_id: Optional[str] = None


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request"""
    document_base64: str
    document_type: str = Field(..., regex="^(contract|legal_notice|court_document|agreement)$")
    session_id: Optional[str] = None
    additional_context: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response"""
    analysis: str
    detected_issues: Optional[List[str]] = None
    confidence_scores: Optional[Dict[str, float]] = None
    recommendations: Optional[List[str]] = None
    requires_urgent_attention: bool = False
    disclaimer: str = Field(
        default="AI document analysis is preliminary. Always get a professional legal review from a qualified attorney."
    )
