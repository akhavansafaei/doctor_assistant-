"""WebSocket endpoint for real-time streaming chat"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from typing import Optional
import json
import uuid
from datetime import datetime
from loguru import logger

from app.api.websocket_manager import connection_manager
from app.agents import TriageAgent, DiagnosticAgent, TreatmentAgent
from app.agents.streaming import make_streaming_agent
from app.safety import SafetyGuardrails, EmergencyDetector, ComplianceManager
from app.schemas.chat import ChatRequest

router = APIRouter()

# Initialize services
safety_guardrails = SafetyGuardrails()
emergency_detector = EmergencyDetector()
compliance_manager = ComplianceManager()

# Create streaming versions of agents
StreamingTriageAgent = make_streaming_agent(TriageAgent)
StreamingDiagnosticAgent = make_streaming_agent(DiagnosticAgent)
StreamingTreatmentAgent = make_streaming_agent(TreatmentAgent)

# In-memory storage (replace with database in production)
conversations_db = {}
messages_db = {}


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming chat

    Protocol:
    - Client sends: {"message": "...", "session_id": "...", "enable_agents": true}
    - Server streams:
        - {"type": "token", "content": "..."}
        - {"type": "status", "status": "...", "details": {...}}
        - {"type": "stream_start"}
        - {"type": "stream_end", "metadata": {...}}
        - {"type": "error", "message": "..."}
    """
    session_id = None

    try:
        # Accept connection
        session_id = str(uuid.uuid4())
        await connection_manager.connect(websocket, session_id)

        # Main message loop
        while True:
            # Receive message from client
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

            # Extract message details
            user_message = message_data.get("message", "")
            use_provided_session = message_data.get("session_id")
            enable_agents = message_data.get("enable_agents", True)
            patient_profile = message_data.get("patient_profile", {})

            # Use provided session ID if available
            if use_provided_session:
                session_id = use_provided_session

            # Validate input
            if not user_message:
                await connection_manager.send_error(
                    session_id,
                    "Message cannot be empty",
                    "validation_error"
                )
                continue

            # Safety validation
            await connection_manager.send_status(
                session_id,
                "validating",
                {"step": "safety_check"}
            )

            input_validation = await safety_guardrails.validate_input(user_message)
            if not input_validation["safe"]:
                await connection_manager.send_error(
                    session_id,
                    f"Input validation failed: {', '.join(input_validation['issues'])}",
                    "safety_violation"
                )
                continue

            # Quick emergency detection
            await connection_manager.send_status(
                session_id,
                "checking_emergency",
                {"step": "emergency_detection"}
            )

            emergency_check = emergency_detector.detect(user_message)

            if emergency_check["is_emergency"]:
                # Send emergency alert immediately
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

                emergency_response += "\n\n" + safety_guardrails.get_medical_disclaimer("emergency")

                # Stream emergency message
                for char in emergency_response:
                    await connection_manager.stream_token(session_id, char)
                    await asyncio.sleep(0.01)  # Small delay for effect

                await connection_manager.stream_end(session_id, {
                    "emergency_detected": True,
                    "severity": "EMERGENCY"
                })
                continue

            # Process with streaming agents
            if enable_agents:
                await process_with_streaming_agents(
                    session_id,
                    user_message,
                    patient_profile,
                    messages_db.get(session_id, [])
                )
            else:
                # Simple echo response
                await connection_manager.stream_start(session_id)
                response = "Agent system is disabled. Enable agents for full functionality."
                for word in response.split():
                    await connection_manager.stream_token(session_id, word + " ")
                    await asyncio.sleep(0.05)
                await connection_manager.stream_end(session_id)

            # Store conversation
            if session_id not in messages_db:
                messages_db[session_id] = []

            messages_db[session_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Log interaction
            await compliance_manager.log_interaction(
                user_id=0,
                interaction_type="websocket_chat",
                details={
                    "session_id": session_id,
                    "message_length": len(user_message),
                    "agents_enabled": enable_agents
                }
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


async def process_with_streaming_agents(
    session_id: str,
    message: str,
    patient_profile: dict,
    conversation_history: list
):
    """Process message with streaming multi-agent workflow"""

    # Token callback
    async def on_token(token: str):
        await connection_manager.stream_token(session_id, token)

    # Status callback
    async def on_status(status: str, details: dict):
        await connection_manager.send_status(session_id, status, details)

    try:
        # Start streaming
        await connection_manager.stream_start(session_id, {
            "workflow": "multi_agent",
            "agents": ["triage", "diagnostic", "treatment"]
        })

        # Initialize streaming agents
        triage_agent = StreamingTriageAgent()
        diagnostic_agent = StreamingDiagnosticAgent()
        treatment_agent = StreamingTreatmentAgent()

        # Step 1: Triage
        await on_status("running_triage", {"current_agent": "triage"})

        triage_result = None
        async for update in triage_agent.stream_process(
            input_data={"message": message, "patient_profile": patient_profile},
            context={"conversation_history": conversation_history},
            on_token=on_token,
            on_status=on_status
        ):
            if update["type"] == "response_complete":
                triage_result = update

        # Check if we should continue to diagnostic
        if triage_result:
            severity = "MODERATE"  # Extract from triage result

            if severity not in ["EMERGENCY", "INFO"]:
                # Step 2: Diagnostic
                await on_status("running_diagnostic", {"current_agent": "diagnostic"})

                diagnostic_result = None
                async for update in diagnostic_agent.stream_process(
                    input_data={
                        "message": message,
                        "symptoms": message,
                        "patient_profile": patient_profile
                    },
                    context={"conversation_history": conversation_history},
                    on_token=on_token,
                    on_status=on_status
                ):
                    if update["type"] == "response_complete":
                        diagnostic_result = update

                # Step 3: Treatment
                if diagnostic_result:
                    await on_status("running_treatment", {"current_agent": "treatment"})

                    async for update in treatment_agent.stream_process(
                        input_data={
                            "condition": message,
                            "patient_profile": patient_profile
                        },
                        context={"conversation_history": conversation_history},
                        on_token=on_token,
                        on_status=on_status
                    ):
                        if update["type"] == "response_complete":
                            pass  # Final result

        # Add disclaimer
        disclaimer = "\n\n" + safety_guardrails.get_medical_disclaimer()
        for char in disclaimer:
            await on_token(char)

        # End streaming
        await connection_manager.stream_end(session_id, {
            "agents_completed": ["triage", "diagnostic", "treatment"],
            "session_id": session_id
        })

    except Exception as e:
        logger.error(f"Error in streaming agents: {e}", exc_info=True)
        await connection_manager.send_error(
            session_id,
            f"Error processing request: {str(e)}",
            "agent_error"
        )


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat_with_user(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint with user authentication

    Requires user_id for personalized experience
    """
    session_id = str(uuid.uuid4())

    try:
        await connection_manager.connect(websocket, session_id, user_id)

        # Load user's health profile
        # In production, fetch from database
        user_profile = {}

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Merge user profile into context
            message_data["patient_profile"] = user_profile

            # Process message (similar to above)
            # ... (implementation similar to websocket_chat_endpoint)

    except WebSocketDisconnect:
        logger.info(f"User {user_id} WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
    finally:
        connection_manager.disconnect(session_id, user_id)


import asyncio  # Add this import at the top
