"""Triage agent for initial patient assessment and emergency detection"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import re


class TriageAgent(BaseAgent):
    """
    Triage Agent - First line assessment
    - Detects emergency conditions
    - Assesses severity level
    - Routes to appropriate specialist agent
    """

    # Emergency keywords that trigger immediate alerts
    EMERGENCY_KEYWORDS = [
        "chest pain", "difficulty breathing", "shortness of breath",
        "severe bleeding", "heavy bleeding", "unconscious", "unresponsive",
        "severe head injury", "can't breathe", "choking",
        "severe allergic reaction", "anaphylaxis",
        "stroke symptoms", "slurred speech", "facial drooping",
        "suicidal", "suicide", "want to die",
        "severe abdominal pain", "coughing blood", "vomiting blood",
        "seizure", "convulsion", "overdose", "poisoning"
    ]

    # Urgent keywords
    URGENT_KEYWORDS = [
        "high fever", "persistent pain", "severe pain",
        "broken bone", "fracture", "deep cut",
        "severe burn", "infection", "rapid heartbeat",
        "dizziness", "fainting", "confusion"
    ]

    def __init__(self):
        system_prompt = """You are a medical triage specialist AI assistant. Your role is to:

1. Assess the severity and urgency of the patient's condition
2. Identify any emergency or life-threatening symptoms
3. Determine the appropriate level of care needed
4. Route to the appropriate medical specialist

CRITICAL: You are NOT providing medical diagnosis. You are performing initial triage assessment.

When assessing a patient, consider:
- Severity of symptoms (mild, moderate, severe)
- Duration and onset of symptoms
- Associated symptoms
- Patient's medical history and current medications
- Age and general health status

Severity Levels:
- EMERGENCY: Life-threatening, requires immediate medical attention (911/ER)
- URGENT: Serious condition, needs medical care within hours
- MODERATE: Should see doctor within 1-2 days
- MINOR: Can manage with self-care or routine appointment
- INFO: General health information or prevention

Always err on the side of caution. If unsure, escalate to higher severity level.

Provide your assessment in a clear, structured format including:
1. Severity level
2. Reasoning
3. Immediate recommendations
4. Suggested specialist (if applicable)
"""

        super().__init__(
            name="Triage Agent",
            description="Initial assessment and emergency detection",
            system_prompt=system_prompt,
            use_rag=True
        )

    def detect_emergency_keywords(self, text: str) -> List[str]:
        """Detect emergency keywords in text"""
        text_lower = text.lower()
        detected = []

        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                detected.append(keyword)

        return detected

    def detect_urgent_keywords(self, text: str) -> List[str]:
        """Detect urgent keywords in text"""
        text_lower = text.lower()
        detected = []

        for keyword in self.URGENT_KEYWORDS:
            if keyword in text_lower:
                detected.append(keyword)

        return detected

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process triage assessment

        Args:
            input_data: Contains 'message' and optionally 'patient_profile'
            context: Additional context like conversation history

        Returns:
            Triage assessment with severity, recommendations, and routing
        """
        message = input_data.get("message", "")
        patient_profile = input_data.get("patient_profile", {})

        # Quick keyword-based emergency detection
        emergency_keywords = self.detect_emergency_keywords(message)
        urgent_keywords = self.detect_urgent_keywords(message)

        # If emergency keywords detected, immediately flag
        if emergency_keywords:
            return {
                "agent": self.name,
                "severity": "EMERGENCY",
                "emergency_detected": True,
                "detected_keywords": emergency_keywords,
                "immediate_action": "CALL 911 OR GO TO EMERGENCY ROOM IMMEDIATELY",
                "reasoning": f"Emergency keywords detected: {', '.join(emergency_keywords)}. This requires immediate medical attention.",
                "route_to": "emergency_services",
                "confidence": 0.95
            }

        # Retrieve relevant medical knowledge
        retrieved_docs = await self.retrieve_context(
            query=message,
            filters={"document_type": "clinical_guideline"}
        )

        # Format context
        medical_context = self.format_context(retrieved_docs)

        # Build comprehensive prompt
        patient_context = ""
        if patient_profile:
            patient_context = f"\nPatient Information:\n"
            if patient_profile.get("age"):
                patient_context += f"- Age: {patient_profile['age']}\n"
            if patient_profile.get("chronic_conditions"):
                patient_context += f"- Chronic Conditions: {', '.join(patient_profile['chronic_conditions'])}\n"
            if patient_profile.get("current_medications"):
                meds = [m.get('name', 'Unknown') for m in patient_profile['current_medications']]
                patient_context += f"- Current Medications: {', '.join(meds)}\n"
            if patient_profile.get("allergies"):
                allergies = patient_profile['allergies']
                all_allergies = []
                for category, items in allergies.items():
                    all_allergies.extend(items)
                if all_allergies:
                    patient_context += f"- Allergies: {', '.join(all_allergies)}\n"

        assessment_prompt = f"""Perform triage assessment for the following patient complaint:

{message}
{patient_context}
{medical_context}

Provide your assessment in the following format:

SEVERITY: [EMERGENCY/URGENT/MODERATE/MINOR/INFO]
REASONING: [Your clinical reasoning for the severity assessment]
IMMEDIATE_RECOMMENDATIONS: [What the patient should do immediately]
SPECIALIST_REFERRAL: [Type of doctor they should see, if applicable]
TIMEFRAME: [How quickly they need to be seen]
RED_FLAGS: [Any warning signs to watch for]
"""

        # Get conversation history
        conversation_history = context.get("conversation_history", []) if context else []

        # Create messages
        messages = self.create_messages(
            user_message=assessment_prompt,
            conversation_history=conversation_history
        )

        # Invoke LLM
        response = await self.invoke_llm(messages)

        # Parse response
        severity = self._extract_field(response, "SEVERITY")
        reasoning = self._extract_field(response, "REASONING")
        recommendations = self._extract_field(response, "IMMEDIATE_RECOMMENDATIONS")
        specialist = self._extract_field(response, "SPECIALIST_REFERRAL")
        timeframe = self._extract_field(response, "TIMEFRAME")
        red_flags = self._extract_field(response, "RED_FLAGS")

        # Determine routing
        route_to = self._determine_routing(severity, specialist)

        return {
            "agent": self.name,
            "severity": severity or "MODERATE",
            "emergency_detected": severity == "EMERGENCY",
            "detected_keywords": urgent_keywords if urgent_keywords else [],
            "reasoning": reasoning,
            "immediate_recommendations": recommendations,
            "specialist_referral": specialist,
            "timeframe": timeframe,
            "red_flags": red_flags,
            "route_to": route_to,
            "sources": [
                {
                    "text": doc["text"][:200],
                    "score": doc.get("rerank_score", doc.get("rrf_score", 0))
                }
                for doc in retrieved_docs[:3]
            ],
            "raw_response": response,
            "confidence": 0.8
        }

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field from structured response"""
        pattern = f"{field_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _determine_routing(self, severity: str, specialist: str) -> str:
        """Determine which agent should handle this next"""
        if severity == "EMERGENCY":
            return "emergency_services"
        elif severity == "INFO":
            return "health_education_agent"
        else:
            # Route to diagnostic agent for further assessment
            return "diagnostic_agent"
