"""Intake agent for initial client assessment and urgent matter detection"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import re


class IntakeAgent(BaseAgent):
    """
    Intake Agent - First line client assessment
    - Detects urgent legal matters (deadlines, court dates)
    - Assesses urgency level
    - Routes to appropriate legal specialist agent
    """

    # Critical urgency keywords that trigger immediate alerts (English & Persian)
    CRITICAL_URGENT_KEYWORDS = [
        # English
        "court date tomorrow", "deadline today", "deadline tomorrow",
        "statute of limitations", "eviction notice", "foreclosure",
        "restraining order", "arrest warrant", "deportation",
        "child custody emergency", "emergency injunction",
        "termination notice", "lawsuit filed", "court summons",
        "garnishment", "asset seizure", "bankruptcy filing",
        "criminal charges", "indictment", "subpoena",
        # Persian/Farsi
        "جلسه دادگاه فردا", "ضرب‌الاجل امروز", "ضرب‌الاجل فردا",
        "مهلت قانونی", "اخطار تخلیه", "توقیف اموال",
        "دستور بازداشت", "اخراج از کشور",
        "اورژانس حضانت فرزند", "دستور موقت دادگاه",
        "اخطار اخراج", "طرح دعوی", "احضاریه دادگاه",
        "توقیف دستمزد", "ورشکستگی", "اتهامات کیفری"
    ]

    # Urgent keywords (English & Persian)
    URGENT_KEYWORDS = [
        # English
        "legal deadline", "contract dispute", "employment termination",
        "divorce filing", "child support", "property dispute",
        "debt collection", "tax audit", "visa issue",
        "intellectual property", "trademark infringement",
        "breach of contract", "landlord dispute", "tenant rights",
        # Persian/Farsi
        "ضرب‌الاجل قانونی", "اختلاف قراردادی", "اخراج از کار",
        "طلاق", "نفقه فرزند", "اختلاف املاک",
        "وصول طلب", "ممیزی مالیاتی", "مشکل ویزا",
        "مالکیت فکری", "نقض علامت تجاری",
        "نقض قرارداد", "اختلاف مالک", "حقوق مستاجر"
    ]

    def __init__(self):
        system_prompt = """You are a legal intake specialist AI assistant. Your role is to:

1. Assess the urgency and time-sensitivity of the client's legal matter
2. Identify any critical deadlines or urgent legal issues
3. Determine the appropriate level of legal attention needed
4. Route to the appropriate legal specialist area

CRITICAL: You are NOT providing legal advice. You are performing initial intake assessment.

When assessing a client's matter, consider:
- Time sensitivity (deadlines, court dates, statutes of limitation)
- Severity of potential legal consequences
- Complexity of the legal issue
- Client's legal history and current legal matters
- Jurisdiction and applicable laws

Urgency Levels:
- CRITICAL_URGENT: Time-critical matters requiring immediate legal attention (imminent court dates, expiring deadlines, emergency injunctions)
- URGENT: Serious legal matters that need attorney consultation within days
- MODERATE: Legal matters that should be addressed within weeks
- ROUTINE: Can be handled through standard legal consultation process
- INFO: General legal information or educational questions

Always err on the side of caution. If unsure about deadlines or urgency, escalate to higher urgency level.

Provide your assessment in a clear, structured format including:
1. Urgency level
2. Legal reasoning
3. Immediate recommendations
4. Suggested legal area/practice (if applicable)
5. Critical deadlines (if any)
"""

        super().__init__(
            name="Intake Agent",
            description="Initial client assessment and urgent matter detection",
            system_prompt=system_prompt,
            use_rag=True
        )

    def detect_critical_urgent_keywords(self, text: str) -> List[str]:
        """Detect critical urgent keywords in text"""
        text_lower = text.lower()
        detected = []

        for keyword in self.CRITICAL_URGENT_KEYWORDS:
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
        Process intake assessment

        Args:
            input_data: Contains 'message' and optionally 'client_profile'
            context: Additional context like conversation history

        Returns:
            Intake assessment with urgency, recommendations, and routing
        """
        message = input_data.get("message", "")
        client_profile = input_data.get("client_profile", {})

        # Quick keyword-based critical urgency detection
        critical_keywords = self.detect_critical_urgent_keywords(message)
        urgent_keywords = self.detect_urgent_keywords(message)

        # If critical urgent keywords detected, immediately flag
        if critical_keywords:
            return {
                "agent": self.name,
                "urgency": "CRITICAL_URGENT",
                "urgent_matter_detected": True,
                "detected_keywords": critical_keywords,
                "immediate_action": "CONSULT WITH AN ATTORNEY IMMEDIATELY - TIME-SENSITIVE LEGAL MATTER",
                "reasoning": f"Critical urgent keywords detected: {', '.join(critical_keywords)}. This requires immediate legal attention to protect your rights.",
                "route_to": "urgent_legal_services",
                "confidence": 0.95
            }

        # Retrieve relevant legal knowledge
        retrieved_docs = await self.retrieve_context(
            query=message,
            filters={"document_type": "statute"}
        )

        # Format context
        legal_context = self.format_context(retrieved_docs)

        # Get long-term memory context
        long_term_memory = context.get("long_term_memory", "") if context else ""
        memory_context = self.format_memory_context(long_term_memory)

        # Detect language and get instruction
        language_code, language_instruction = self.detect_and_format_language(message, context)

        # Build comprehensive prompt
        client_context = ""
        if client_profile:
            client_context = f"\nClient Information:\n"
            if client_profile.get("occupation"):
                client_context += f"- Occupation: {client_profile['occupation']}\n"
            if client_profile.get("active_legal_matters"):
                client_context += f"- Active Legal Matters: {len(client_profile['active_legal_matters'])}\n"
            if client_profile.get("legal_areas_of_interest"):
                client_context += f"- Legal Areas of Interest: {', '.join(client_profile['legal_areas_of_interest'])}\n"
            if client_profile.get("legal_restrictions"):
                if client_profile['legal_restrictions']:
                    client_context += f"- Legal Restrictions: Present (details in profile)\n"

        assessment_prompt = f"""Perform intake assessment for the following client inquiry:

{message}
{client_context}
{memory_context}
{legal_context}

Provide your assessment in the following format:

URGENCY: [CRITICAL_URGENT/URGENT/MODERATE/ROUTINE/INFO]
LEGAL_REASONING: [Your legal reasoning for the urgency assessment]
IMMEDIATE_RECOMMENDATIONS: [What the client should do immediately]
LEGAL_AREA_REFERRAL: [Practice area they should consult - family law, criminal defense, corporate, etc.]
TIMEFRAME: [How quickly they need legal consultation]
CRITICAL_DEADLINES: [Any time-sensitive deadlines to be aware of]
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
        urgency = self._extract_field(response, "URGENCY")
        reasoning = self._extract_field(response, "LEGAL_REASONING")
        recommendations = self._extract_field(response, "IMMEDIATE_RECOMMENDATIONS")
        legal_area = self._extract_field(response, "LEGAL_AREA_REFERRAL")
        timeframe = self._extract_field(response, "TIMEFRAME")
        deadlines = self._extract_field(response, "CRITICAL_DEADLINES")

        # Determine routing
        route_to = self._determine_routing(urgency, legal_area)

        return {
            "agent": self.name,
            "urgency": urgency or "MODERATE",
            "urgent_matter_detected": urgency == "CRITICAL_URGENT",
            "detected_keywords": urgent_keywords if urgent_keywords else [],
            "reasoning": reasoning,
            "immediate_recommendations": recommendations,
            "legal_area_referral": legal_area,
            "timeframe": timeframe,
            "critical_deadlines": deadlines,
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

    def _determine_routing(self, urgency: str, legal_area: str) -> str:
        """Determine which agent should handle this next"""
        if urgency == "CRITICAL_URGENT":
            return "urgent_legal_services"
        elif urgency == "INFO":
            return "legal_education_agent"
        else:
            # Route to legal analysis agent for further assessment
            return "legal_analysis_agent"
