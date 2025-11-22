"""Enhanced WebSocket endpoint with profile onboarding"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import json
import uuid
from datetime import datetime
from loguru import logger

from app.api.websocket_manager import connection_manager
from app.agents import TriageAgent, DiagnosticAgent, TreatmentAgent
from app.agents.onboarding_agent import OnboardingAgent, ProfileCompletionChecker
from app.agents.streaming import make_streaming_agent
from app.safety import SafetyGuardrails, EmergencyDetector, ComplianceManager
from app.utils.profile_context import format_profile_for_prompt, get_critical_warnings
from app.memory import MemoryManager
from app.services import api  # Assuming we can access API service

router = APIRouter()

# Initialize services
safety_guardrails = SafetyGuardrails()
emergency_detector = EmergencyDetector()
compliance_manager = ComplianceManager()
onboarding_agent = OnboardingAgent()

# Create streaming versions of agents
StreamingTriageAgent = make_streaming_agent(TriageAgent)
StreamingDiagnosticAgent = make_streaming_agent(DiagnosticAgent)
StreamingTreatmentAgent = make_streaming_agent(TreatmentAgent)

# Session storage
sessions_db = {}
messages_db = {}


@router.websocket("/ws/chat/enhanced")
async def websocket_chat_with_onboarding(websocket: WebSocket):
    """
    Enhanced WebSocket endpoint with intelligent profile onboarding

    Features:
    - Checks if user has complete health profile
    - If not, triggers conversational onboarding
    - Extracts profile data from natural language
    - Auto-fills profile
    - Injects profile context into all medical chats
    """
    session_id = None
    user_id = None  # In production, extract from auth token

    try:
        session_id = str(uuid.uuid4())
        await connection_manager.connect(websocket, session_id)

        # Initialize session state
        sessions_db[session_id] = {
            "onboarding_active": False,
            "onboarding_state": {},
            "health_profile": None,
            "profile_complete": False
        }

        while True:
            # Receive message
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await connection_manager.send_error(
                    session_id,
                    "Invalid JSON format",
                    "parse_error"
                )
                continue

            user_message = message_data.get("message", "")
            use_provided_session = message_data.get("session_id")
            enable_agents = message_data.get("enable_agents", True)

            if use_provided_session:
                session_id = use_provided_session

            if not user_message:
                await connection_manager.send_error(
                    session_id,
                    "Message cannot be empty",
                    "validation_error"
                )
                continue

            # Get session state
            session_state = sessions_db.get(session_id, {})

            # Load or check health profile
            if session_state.get("health_profile") is None:
                # In production, load from database using user_id
                # For now, simulate loading
                health_profile = await load_user_health_profile(user_id)
                session_state["health_profile"] = health_profile
                session_state["profile_complete"] = ProfileCompletionChecker.is_profile_complete(health_profile)

            # Check if we need onboarding
            if not session_state["profile_complete"] and not session_state["onboarding_active"]:
                # Start onboarding
                session_state["onboarding_active"] = True
                session_state["onboarding_state"] = {
                    "current_question": 0,
                    "collected_data": {}
                }

                await connection_manager.send_status(
                    session_id,
                    "onboarding_started",
                    {"message": "Starting health profile collection"}
                )

            # Handle onboarding flow
            if session_state["onboarding_active"]:
                await handle_onboarding(
                    session_id,
                    user_message,
                    session_state
                )
                continue

            # Normal chat flow with profile context
            await handle_chat_with_profile(
                session_id,
                user_message,
                session_state.get("health_profile"),
                enable_agents
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if session_id:
            try:
                await connection_manager.send_error(
                    session_id,
                    f"Internal error: {str(e)}",
                    "server_error"
                )
            except:
                pass
    finally:
        if session_id:
            connection_manager.disconnect(session_id)
            # Clean up session
            if session_id in sessions_db:
                del sessions_db[session_id]


async def handle_onboarding(
    session_id: str,
    message: str,
    session_state: dict
):
    """Handle onboarding conversation flow"""

    await connection_manager.stream_start(session_id, {
        "onboarding": True,
        "current_question": session_state["onboarding_state"]["current_question"]
    })

    # Process with onboarding agent
    result = await onboarding_agent.process(
        input_data={
            "message": message,
            "onboarding_state": session_state["onboarding_state"]
        },
        context={}
    )

    # Update onboarding state
    session_state["onboarding_state"]["current_question"] = result.get("current_question", 0)
    session_state["onboarding_state"]["collected_data"] = result.get("collected_data", {})

    # Get the message to send
    if result.get("onboarding_complete"):
        # Onboarding finished!
        response_message = result.get("completion_message", "")

        # Save profile to database
        collected_data = result.get("collected_data", {})
        await save_health_profile(session_id, collected_data)

        # Update session state
        session_state["health_profile"] = collected_data
        session_state["profile_complete"] = True
        session_state["onboarding_active"] = False

        # Add summary
        summary = result.get("summary", "")
        if summary:
            response_message += f"\n\n📋 **Profile Summary**: {summary}"

    else:
        response_message = result.get("next_question", "")

    # Stream the response
    for word in response_message.split():
        await connection_manager.stream_token(session_id, word + " ")
        await asyncio.sleep(0.05)

    await connection_manager.stream_end(session_id, {
        "onboarding_complete": result.get("onboarding_complete", False),
        "profile_completion": ProfileCompletionChecker.get_completion_percentage(
            session_state.get("health_profile")
        )
    })


async def handle_chat_with_profile(
    session_id: str,
    message: str,
    health_profile: Optional[dict],
    enable_agents: bool
):
    """Handle normal chat with profile context injected"""

    # Safety checks
    await connection_manager.send_status(
        session_id,
        "validating",
        {"step": "safety_check"}
    )

    input_validation = await safety_guardrails.validate_input(message)
    if not input_validation["safe"]:
        await connection_manager.send_error(
            session_id,
            f"Input validation failed: {', '.join(input_validation['issues'])}",
            "safety_violation"
        )
        return

    # Emergency detection
    emergency_check = emergency_detector.detect(message)
    if emergency_check["is_emergency"]:
        await send_emergency_response(session_id, emergency_check)
        return

    # Format profile context for LLM
    profile_context = format_profile_for_prompt(health_profile)
    critical_warnings = get_critical_warnings(health_profile)

    # Get long-term memory (past conversations)
    # NOTE: In production, initialize MemoryManager with actual db session and user_id
    # For now, we'll use a placeholder
    long_term_memory = ""
    memory_summary = {}

    # TODO: Replace with actual implementation when database session is available:
    # from app.database import get_db
    # db = next(get_db())
    # user_id = get_user_id_from_session(session_id)  # Extract from JWT token
    # memory_manager = MemoryManager(db=db, user_id=user_id)
    # long_term_memory = await memory_manager.format_memory_for_prompt(
    #     current_session_id=session_id,
    #     include_short_term=False  # Short-term is in conversation_history
    # )
    # memory_summary = await memory_manager.get_memory_summary(session_id)

    # Add profile context and memory to agent inputs
    enhanced_context = {
        "conversation_history": messages_db.get(session_id, []),
        "patient_profile_context": profile_context,
        "critical_warnings": critical_warnings,
        "long_term_memory": long_term_memory,  # NEW: Long-term memory from past chats
        "memory_summary": memory_summary  # NEW: Memory statistics
    }

    if enable_agents:
        await process_with_agents_and_profile(
            session_id,
            message,
            health_profile,
            enhanced_context
        )
    else:
        await send_simple_response(session_id, message)


async def process_with_agents_and_profile(
    session_id: str,
    message: str,
    health_profile: Optional[dict],
    context: dict
):
    """Process with agents including profile context"""

    async def on_token(token: str):
        await connection_manager.stream_token(session_id, token)

    async def on_status(status: str, details: dict):
        await connection_manager.send_status(session_id, status, details)

    await connection_manager.stream_start(session_id, {
        "workflow": "multi_agent_with_profile",
        "profile_available": health_profile is not None
    })

    # Show critical warnings if any
    critical_warnings = context.get("critical_warnings", [])
    if critical_warnings:
        for warning in critical_warnings:
            await on_token(f"\n{warning}\n\n")

    # Run agents with profile context
    # (Similar to original websocket.py but with enhanced context)
    triage_agent = StreamingTriageAgent()

    await on_status("running_triage", {"current_agent": "triage"})

    # Inject profile context into agent inputs
    agent_input = {
        "message": message,
        "patient_profile": health_profile or {}
    }

    triage_result = None
    async for update in triage_agent.stream_process(
        input_data=agent_input,
        context=context,
        on_token=on_token,
        on_status=on_status
    ):
        if update["type"] == "response_complete":
            triage_result = update

    # Continue with diagnostic and treatment agents...
    # (Implementation similar to original)

    # Add medical disclaimer
    disclaimer = "\n\n" + safety_guardrails.get_medical_disclaimer()
    for char in disclaimer:
        await on_token(char)

    await connection_manager.stream_end(session_id, {
        "agents_completed": ["triage"],
        "profile_used": True
    })


async def send_emergency_response(session_id: str, emergency_check: dict):
    """Send emergency response"""
    await connection_manager.stream_start(session_id, {
        "emergency": True,
        "severity": emergency_check["severity"]
    })

    emergency_response = f"""🚨 **EMERGENCY DETECTED** 🚨

{emergency_check["immediate_action"]}

**Emergency Contacts:**
"""
    for name, number in emergency_check.get("emergency_contacts", {}).items():
        emergency_response += f"\n• {name}: {number}"

    for char in emergency_response:
        await connection_manager.stream_token(session_id, char)
        await asyncio.sleep(0.01)

    await connection_manager.stream_end(session_id, {
        "emergency_detected": True
    })


async def send_simple_response(session_id: str, message: str):
    """Send simple response without agents"""
    await connection_manager.stream_start(session_id)
    response = "Agent system is disabled. Enable agents for full functionality."
    for word in response.split():
        await connection_manager.stream_token(session_id, word + " ")
        await asyncio.sleep(0.05)
    await connection_manager.stream_end(session_id)


async def load_user_health_profile(user_id: Optional[int]) -> Optional[dict]:
    """Load user health profile from database"""
    # In production, fetch from database
    # For now, return None to trigger onboarding
    return None


async def save_health_profile(session_id: str, profile_data: dict):
    """Save collected health profile to database"""
    # In production, save to database using user_id
    logger.info(f"Saving health profile for session {session_id}: {profile_data}")

    # Transform collected data to health profile format
    health_profile = {
        "age": profile_data.get("age"),
        "gender": profile_data.get("gender"),
        "height_cm": profile_data.get("height_cm"),
        "weight_kg": profile_data.get("weight_kg"),
        "blood_type": profile_data.get("blood_type"),
        "chronic_conditions": profile_data.get("chronic_conditions", []),
        "allergies": profile_data.get("allergies", {}),
        "current_medications": profile_data.get("current_medications", []),
        "past_surgeries": profile_data.get("past_surgeries", []),
        "smoking_status": profile_data.get("smoking_status"),
        "alcohol_consumption": profile_data.get("alcohol_consumption"),
        "exercise_frequency": profile_data.get("exercise_frequency"),
    }

    # Call API to save (in production)
    # await api.createHealthProfile(health_profile)

    return health_profile


import asyncio
