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

    # Emergency keywords that trigger immediate alerts (English & Persian)
    EMERGENCY_KEYWORDS = [
        # English - Serious injuries and dangerous conditions
        "chest pain during exercise", "severe chest pain", "heart attack symptoms",
        "can't breathe", "difficulty breathing", "severe shortness of breath",
        "unconscious", "passed out", "blacked out",
        "severe head injury", "neck injury", "spinal injury",
        "compound fracture", "bone through skin", "severe bleeding",
        "severe allergic reaction", "anaphylaxis",
        "heat stroke", "severe dehydration", "hypothermia",
        "rhabdomyolysis", "dark urine after workout", "muscle breakdown",
        # Persian/Farsi
        "درد قفسه سینه هنگام ورزش", "درد شدید قلب", "علائم حمله قلبی",
        "نفس کشیدن سخت", "تنگی نفس شدید", "نمی‌توانم نفس بکشم",
        "بیهوش", "بی‌هوش", "غش کردن",
        "آسیب شدید سر", "آسیب گردن", "آسیب ستون فقرات",
        "شکستگی باز", "استخوان از پوست زده", "خونریزی شدید",
        "واکنش آلرژیک شدید", "آنافیلاکسی",
        "گرمازدگی", "کم‌آبی شدید", "سرمازدگی",
        "رابدومیولیز", "ادرار تیره بعد از ورزش", "تجزیه عضلانی"
    ]

    # Urgent keywords (English & Persian)
    URGENT_KEYWORDS = [
        # English - Injuries and concerning symptoms
        "severe joint pain", "joint swelling", "can't move joint",
        "fracture", "broken bone", "severe sprain",
        "sharp pain", "stabbing pain", "extreme pain",
        "severe muscle strain", "torn muscle", "pulled muscle",
        "rapid heartbeat during rest", "irregular heartbeat", "palpitations",
        "dizziness", "severe nausea", "vomiting",
        "severe cramps", "persistent pain", "chronic pain worsening",
        # Persian/Farsi
        "درد شدید مفصل", "ورم مفصل", "عدم حرکت مفصل",
        "شکستگی", "شکستگی استخوان", "پیچ خوردگی شدید",
        "درد تیز", "درد چاقو زدن", "درد شدید",
        "کشیدگی شدید عضله", "پارگی عضله", "کشیدگی عضلانی",
        "ضربان سریع قلب در حالت استراحت", "ضربان نامنظم قلب", "تپش قلب",
        "سرگیجه", "حالت تهوع شدید", "استفراغ",
        "گرفتگی شدید عضلات", "درد مداوم", "بدتر شدن درد مزمن"
    ]

    def __init__(self):
        system_prompt = """You are a fitness and wellness triage specialist AI assistant. Your role is to:

1. Assess the severity and urgency of fitness-related concerns or injuries
2. Identify any serious injuries or dangerous conditions requiring immediate medical attention
3. Determine the appropriate level of guidance needed
4. Route to appropriate fitness specialist or medical professional

CRITICAL: You are NOT diagnosing injuries. You are performing initial assessment of fitness concerns.

When assessing a user's concern, consider:
- Severity of pain or injury (mild discomfort, moderate pain, severe injury)
- Duration and onset (acute injury, chronic issue, gradual development)
- Impact on daily activities and training ability
- User's fitness level, training history, and goals
- Age and physical condition

Severity Levels:
- EMERGENCY: Serious injury or dangerous condition, requires immediate medical attention (ER/Doctor)
- URGENT: Significant injury or concern, needs professional evaluation within 24-48 hours
- MODERATE: Should rest and monitor, may need physiotherapist or sports medicine consult
- MINOR: Can manage with rest, ice, modifications to training
- INFO: General fitness/nutrition information or guidance

Always err on the side of caution. If unsure about an injury, recommend professional evaluation.

Provide your assessment in a clear, structured format including:
1. Severity level
2. Reasoning
3. Immediate recommendations
4. Suggested specialist (sports medicine, physiotherapist, nutritionist, etc.)
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
                "immediate_action": "SEEK IMMEDIATE MEDICAL ATTENTION - CALL 911 OR GO TO EMERGENCY ROOM",
                "reasoning": f"Serious injury or dangerous condition detected: {', '.join(emergency_keywords)}. This requires immediate medical evaluation, not fitness guidance.",
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

        # Get long-term memory context
        long_term_memory = context.get("long_term_memory", "") if context else ""
        memory_context = self.format_memory_context(long_term_memory)

        # Detect language and get instruction
        language_code, language_instruction = self.detect_and_format_language(message, context)

        # Build comprehensive prompt
        user_context = ""
        if patient_profile:
            user_context = f"\nUser Profile:\n"
            if patient_profile.get("age"):
                user_context += f"- Age: {patient_profile['age']}\n"
            if patient_profile.get("fitness_level"):
                user_context += f"- Fitness Level: {patient_profile['fitness_level']}\n"
            if patient_profile.get("fitness_goals"):
                user_context += f"- Fitness Goals: {', '.join(patient_profile['fitness_goals'])}\n"
            if patient_profile.get("training_experience"):
                user_context += f"- Training Experience: {patient_profile['training_experience']}\n"
            if patient_profile.get("current_injuries"):
                user_context += f"- Current Injuries: {', '.join(patient_profile['current_injuries'])}\n"
            if patient_profile.get("health_conditions"):
                user_context += f"- Health Conditions: {', '.join(patient_profile['health_conditions'])}\n"

        assessment_prompt = f"""Perform triage assessment for the following fitness/wellness concern:

{message}
{user_context}
{memory_context}
{medical_context}

Provide your assessment in the following format:

SEVERITY: [EMERGENCY/URGENT/MODERATE/MINOR/INFO]
REASONING: [Your reasoning for the severity assessment]
IMMEDIATE_RECOMMENDATIONS: [What the user should do immediately]
SPECIALIST_REFERRAL: [Type of specialist they should see - sports medicine doctor, physiotherapist, nutritionist, etc.]
TIMEFRAME: [How quickly they need professional evaluation]
RED_FLAGS: [Any warning signs to watch for that require immediate medical attention]
{language_instruction}"""

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
            return "fitness_education_agent"
        else:
            # Route to fitness assessment agent for further evaluation
            return "diagnostic_agent"
