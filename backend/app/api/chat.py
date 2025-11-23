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
from app.safety import SafetyGuardrails, EmergencyDetector, ComplianceManager
from app.core.config import settings

router = APIRouter()

# Initialize services
agent_orchestrator = AgentOrchestrator()
safety_guardrails = SafetyGuardrails()
emergency_detector = EmergencyDetector()
compliance_manager = ComplianceManager()

# In-memory storage for demo (replace with database in production)
conversations_db = {}
messages_db = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the AI doctor chatbot

    This endpoint orchestrates the full multi-agent workflow:
    1. Safety validation
    2. Emergency detection
    3. Agent orchestration (Triage → Diagnostic → Treatment)
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

        # Quick emergency detection
        emergency_check = emergency_detector.detect(request.message)

        # If emergency, return immediate response
        if emergency_check["is_emergency"]:
            emergency_response = f"""
🚨 **EMERGENCY DETECTED** 🚨

{emergency_check["immediate_action"]}

**Emergency Contacts:**
"""
            for name, number in emergency_check.get("emergency_contacts", {}).items():
                emergency_response += f"\n• {name}: {number}"

            emergency_response += "\n\n" + safety_guardrails.get_medical_disclaimer("emergency")

            return ChatResponse(
                session_id=request.session_id or str(uuid.uuid4()),
                message=emergency_response,
                agent_type="emergency_detector",
                severity_level="EMERGENCY",
                emergency_detected=True,
                timestamp=datetime.utcnow()
            )

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        # Get conversation history
        conversation_history = messages_db.get(session_id, [])

        # Run multi-agent orchestration
        if request.enable_agents:
            # Get patient profile (in production, fetch from database)
            patient_profile = request.context.get("patient_profile", {}) if request.context else {}

            # Run agent orchestrator
            agent_result = await agent_orchestrator.run(
                message=request.message,
                patient_profile=patient_profile,
                conversation_history=conversation_history
            )

            response_text = agent_result["response"]
            severity = agent_result["severity"]
            sources = agent_result["sources"] if request.include_sources else []

        else:
            # Simple mode without agents (fallback)
            response_text = "Agent system is disabled. Please enable agents for full functionality."
            severity = "INFO"
            sources = []

        # Validate output with safety guardrails
        output_validation = await safety_guardrails.validate_output(
            response_text,
            context={"severity": severity}
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
                "severity": severity,
                "agents_used": request.enable_agents
            }
        )

        return ChatResponse(
            session_id=session_id,
            message=final_response,
            agent_type="multi_agent" if request.enable_agents else "simple",
            severity_level=severity,
            emergency_detected=False,
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
    Analyze medical images (skin conditions, lab reports, etc.)

    In production, integrate with GPT-4V or medical imaging AI
    """
    # Placeholder for image analysis
    return {
        "message": "Image analysis not yet implemented",
        "session_id": request.session_id,
        "image_type": request.image_type
    }


@router.get("/emergency-check")
async def check_emergency(message: str):
    """Quick emergency condition check"""
    result = emergency_detector.detect(message)

    return {
        "is_emergency": result["is_emergency"],
        "severity": result["severity"],
        "immediate_action": result.get("immediate_action"),
        "emergency_contacts": result.get("emergency_contacts", {})
    }
