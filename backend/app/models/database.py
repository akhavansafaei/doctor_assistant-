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
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class SeverityLevel(str, enum.Enum):
    """Medical severity levels"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    MODERATE = "moderate"
    MINOR = "minor"
    INFO = "info"


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
    role = Column(SQLEnum(UserRole), default=UserRole.PATIENT)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")
    medical_history = relationship("MedicalHistory", back_populates="user")


class HealthProfile(Base):
    """User fitness profile"""
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Physical attributes
    height_cm = Column(Float)
    weight_kg = Column(Float)
    blood_type = Column(String(5))

    # Fitness-specific fields
    fitness_level = Column(String(50))  # beginner, intermediate, advanced
    training_experience = Column(String(100))  # e.g., "2 years", "6 months"
    fitness_goals = Column(JSON)  # List: muscle gain, fat loss, strength, etc.

    available_equipment = Column(JSON)  # List: full gym, dumbbells, bodyweight, etc.
    training_days_per_week = Column(Integer)
    training_duration_minutes = Column(Integer)

    # Health and injury tracking
    current_injuries = Column(JSON)  # List of current injuries
    health_conditions = Column(JSON)  # List of health conditions to consider

    # Nutrition preferences
    diet_preference = Column(String(100))  # Persian cuisine, flexible, etc.
    dietary_restrictions = Column(JSON)  # List: vegetarian, vegan, etc.
    food_allergies = Column(JSON)  # List of food allergies

    # Lifestyle
    exercise_frequency = Column(String(50))

    # Body composition tracking
    body_fat_percentage = Column(Float)
    body_measurements = Column(JSON)  # Dict: chest, waist, hips, arms, etc.

    # Legacy medical fields (kept for backward compatibility)
    chronic_conditions = Column(JSON)  # Deprecated, use health_conditions
    allergies = Column(JSON)  # Legacy field
    current_medications = Column(JSON)  # List of current medications
    past_surgeries = Column(JSON)  # Legacy field
    family_history = Column(JSON)  # Legacy field
    smoking_status = Column(String(50))  # Legacy field
    alcohol_consumption = Column(String(50))  # Legacy field
    diet_type = Column(String(50))  # Legacy field

    # Emergency contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    emergency_contact_relationship = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_profile")


class MedicalHistory(Base):
    """Medical history records"""
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    record_type = Column(String(50))  # diagnosis, treatment, lab_result, prescription
    record_date = Column(DateTime, nullable=False)

    diagnosis_code = Column(String(20))  # ICD-10 code
    diagnosis_name = Column(String(255))

    prescribed_by = Column(String(255))  # Doctor name
    prescription_details = Column(JSON)

    lab_results = Column(JSON)
    notes = Column(Text)

    documents = Column(JSON)  # Links to uploaded documents

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="medical_history")


class Conversation(Base):
    """Conversation sessions"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    session_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255))

    initial_complaint = Column(Text)
    severity_level = Column(SQLEnum(SeverityLevel))
    recommended_specialty = Column(String(100))

    status = Column(String(50), default="active")  # active, completed, archived

    # Agent outputs
    differential_diagnoses = Column(JSON)
    treatment_suggestions = Column(JSON)
    emergency_flags = Column(JSON)

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
    source = Column(String(255))  # pubmed, cdc, who, fda
    document_type = Column(String(50))  # guideline, research, drug_info

    content = Column(Text)
    doc_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy reserved keyword

    vector_id = Column(String(100))  # ID in vector database
    embedding_model = Column(String(100))

    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmergencyAlert(Base):
    """Emergency alert records"""
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    alert_type = Column(String(50), nullable=False)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)

    symptoms = Column(JSON)
    detected_condition = Column(String(255))

    recommendation = Column(Text)

    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50))  # email, sms, push

    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
