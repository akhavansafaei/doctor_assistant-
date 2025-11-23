"""Chat API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from app.schemas.chat import (
    ChatRequest, ChatResponse, MessageResponse,
    ConversationResponse, VoiceRequest, ImageAnalysisRequest
)
from app.agents import AgentOrchestrator
from app.safety import SafetyGuardrails, UrgencyDetector, ComplianceManager
from app.core.config import settings

router = APIRouter()

# Initialize services
agent_orchestrator = AgentOrchestrator()
safety_guardrails = SafetyGuardrails()
urgency_detector = UrgencyDetector()
compliance_manager = ComplianceManager()

# In-memory storage for demo (replace with database in production)
conversations_db = {}
messages_db = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the AI law assistant chatbot

    This endpoint orchestrates the full multi-agent workflow:
    1. Safety validation
    2. Urgency detection
    3. Agent orchestration (Intake → Legal Analysis → Legal Advice)
    4. Response compilation with sources
    """
    try:
        # Validate input with safety guardrails
        input_validation = await safety_guardrails.validate_input(request.message)

        if not input_validation["safe"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input validation failed: {', '.join(input_validation['issues'])}"
            )

        # Quick urgency detection
        urgency_check = urgency_detector.detect(request.message)

        # If critical urgent matter, return immediate response
        if urgency_check["is_urgent"]:
            urgent_response = f"""
⚠️ **TIME-SENSITIVE LEGAL MATTER DETECTED** ⚠️

{urgency_check["immediate_action"]}

**Urgent Legal Resources:**
"""
            for name, contact in urgency_check.get("urgent_contacts", {}).items():
                urgent_response += f"\n• {name}: {contact}"

            urgent_response += "\n\n" + safety_guardrails.get_legal_disclaimer("urgent")

            return ChatResponse(
                session_id=request.session_id or str(uuid.uuid4()),
                message=urgent_response,
                agent_type="urgency_detector",
                urgency_level="CRITICAL_URGENT",
                urgent_matter_detected=True,
                timestamp=datetime.utcnow()
            )

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        # Get conversation history
        conversation_history = messages_db.get(session_id, [])

        # Run multi-agent orchestration
        if request.enable_agents:
            # Get client profile (in production, fetch from database)
            client_profile = request.context.get("client_profile", {}) if request.context else {}

            # Run agent orchestrator
            agent_result = await agent_orchestrator.run(
                message=request.message,
                client_profile=client_profile,
                conversation_history=conversation_history
            )

            response_text = agent_result["response"]
            urgency = agent_result["urgency"]
            sources = agent_result["sources"] if request.include_sources else []

        else:
            # Simple mode without agents (fallback)
            response_text = "Agent system is disabled. Please enable agents for full functionality."
            urgency = "INFO"
            sources = []

        # Validate output with safety guardrails
        output_validation = await safety_guardrails.validate_output(
            response_text,
            context={"urgency": urgency}
        )

        if not output_validation["safe"]:
            # Log violations
            await safety_guardrails.log_violation(
                violation_type="output_validation_failed",
                details={"violations": output_validation["violations"]},
                user_id=None  # Would be actual user ID in production
            )

        # Use modified output with disclaimers
        final_response = output_validation["modified_output"]

        # Store conversation (in production, use database)
        conversation_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation_history.append({
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        messages_db[session_id] = conversation_history

        # Log interaction for compliance
        await compliance_manager.log_interaction(
            user_id=0,  # Would be actual user ID
            interaction_type="chat_message",
            details={
                "session_id": session_id,
                "message_length": len(request.message),
                "urgency": urgency,
                "agents_used": request.enable_agents
            }
        )

        return ChatResponse(
            session_id=session_id,
            message=final_response,
            agent_type="multi_agent" if request.enable_agents else "simple",
            urgency_level=urgency,
            urgent_matter_detected=False,
            sources=sources if request.include_sources else None,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=List[MessageResponse])
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    history = messages_db.get(session_id, [])

    return [
        MessageResponse(
            id=i,
            role=msg["role"],
            content=msg["content"],
            timestamp=datetime.fromisoformat(msg["timestamp"])
        )
        for i, msg in enumerate(history)
    ]


@router.delete("/history/{session_id}")
async def delete_conversation(session_id: str):
    """Delete a conversation (GDPR right to erasure)"""
    if session_id in messages_db:
        del messages_db[session_id]

    if session_id in conversations_db:
        del conversations_db[session_id]

    return {"message": "Conversation deleted successfully", "session_id": session_id}


@router.post("/voice")
async def process_voice_input(request: VoiceRequest):
    """
    Process voice input using STT (Speech-to-Text)

    In production, integrate with Whisper or similar STT service
    """
    # Placeholder for voice processing
    return {
        "message": "Voice processing not yet implemented",
        "session_id": request.session_id
    }


@router.post("/image")
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze legal documents (contracts, forms, evidence, etc.)

    In production, integrate with GPT-4V or document analysis AI
    """
    # Placeholder for image analysis
    return {
        "message": "Document analysis not yet implemented",
        "session_id": request.session_id,
        "image_type": request.image_type
    }


@router.get("/urgency-check")
async def check_urgency(message: str):
    """Quick urgency level check for legal matters"""
    result = urgency_detector.detect(message)

    return {
        "is_urgent": result["is_urgent"],
        "urgency": result["urgency"],
        "immediate_action": result.get("immediate_action"),
        "urgent_contacts": result.get("urgent_contacts", {})
    }
