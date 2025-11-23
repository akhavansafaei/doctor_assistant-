"""Database models using SQLAlchemy"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer,
    String, Text, JSON, Table, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles"""
    CLIENT = "client"
    LAWYER = "lawyer"
    ADMIN = "admin"


class UrgencyLevel(str, enum.Enum):
    """Legal matter urgency levels"""
    CRITICAL_URGENT = "critical_urgent"  # Court deadlines, emergency injunctions
    URGENT = "urgent"  # Time-sensitive legal matters
    MODERATE = "moderate"  # Standard legal matters
    ROUTINE = "routine"  # General inquiries
    INFO = "info"  # Information only


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(50))
    role = Column(SQLEnum(UserRole), default=UserRole.CLIENT)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")
    case_history = relationship("CaseHistory", back_populates="user")


class ClientProfile(Base):
    """Client legal profile (uses health_profiles table for compatibility)"""
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Personal information
    occupation = Column(String(255))
    employer = Column(String(255))
    citizenship = Column(String(100))
    marital_status = Column(String(50))

    # Legal information
    legal_areas_of_interest = Column(JSON)  # List of legal practice areas (family, criminal, corporate, etc.)
    active_legal_matters = Column(JSON)  # List of ongoing legal matters
    previous_legal_issues = Column(JSON)  # List of past legal issues
    legal_restrictions = Column(JSON)  # Court orders, probation, restraining orders, etc.

    # Business/Financial context
    business_entities = Column(JSON)  # Owned businesses, corporations, partnerships
    financial_concerns = Column(JSON)  # Bankruptcy, debt, tax issues

    # Contact preferences
    preferred_communication = Column(String(50))  # email, phone, in-person
    availability = Column(JSON)  # Preferred times for consultation

    # Emergency contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    emergency_contact_relationship = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="client_profile")


class CaseHistory(Base):
    """Legal case history records (uses medical_history table for compatibility)"""
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    record_type = Column(String(50))  # case, consultation, document_review, court_appearance
    record_date = Column(DateTime, nullable=False)

    case_number = Column(String(100))  # Court case number
    case_type = Column(String(100))  # Civil, criminal, family, corporate, etc.
    jurisdiction = Column(String(255))  # Court or jurisdiction

    legal_issue = Column(String(500))  # Brief description of legal issue
    case_status = Column(String(50))  # active, closed, settled, dismissed

    handled_by = Column(String(255))  # Attorney/lawyer name
    law_firm = Column(String(255))

    outcome = Column(Text)  # Result or current status
    notes = Column(Text)

    documents = Column(JSON)  # Links to uploaded legal documents

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="case_history")


class Conversation(Base):
    """Conversation sessions"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    session_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255))

    initial_inquiry = Column(Text)
    severity_level = Column(SQLEnum(UrgencyLevel))  # Reusing severity_level column for urgency
    recommended_specialty = Column(String(100))  # Reusing specialty column for legal area

    status = Column(String(50), default="active")  # active, completed, archived

    # Agent outputs (reusing original column names)
    diagnosis = Column(JSON)  # Reusing for legal_issues_identified
    treatment_plan = Column(JSON)  # Reusing for legal_advice_provided
    severity_flags = Column(JSON)  # Reusing for urgency_flags

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Individual messages in a conversation"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)

    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Metadata
    agent_type = Column(String(50))  # Which agent generated this
    confidence_score = Column(Float)
    rag_sources = Column(JSON)  # References to knowledge base sources
    reasoning_chain = Column(JSON)  # For explainability

    # Media
    attachments = Column(JSON)  # Links to images, documents

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class AuditLog(Base):
    """Audit log for compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(Integer)

    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(255))

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class KnowledgeDocument(Base):
    """Documents in the knowledge base"""
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(500), nullable=False)
    source = Column(String(255))  # cornell_law, justia, findlaw, legal_databases
    document_type = Column(String(50))  # statute, case_law, regulation, legal_guide

    content = Column(Text)
    metadata = Column(JSON)

    vector_id = Column(String(100))  # ID in vector database
    embedding_model = Column(String(100))

    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UrgentLegalAlert(Base):
    """Urgent legal matter alert records (uses emergency_alerts table for compatibility)"""
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    alert_type = Column(String(50), nullable=False)  # deadline, court_date, statute_limitation
    severity = Column(SQLEnum(UrgencyLevel), nullable=False)  # Reusing severity column for urgency

    conditions = Column(JSON)  # Reusing conditions column for legal_issues
    detected_condition = Column(String(255))  # Reusing for detected_matter
    deadline_date = Column(DateTime)  # Critical deadline if applicable

    recommendation = Column(Text)

    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50))  # email, sms, push

    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
