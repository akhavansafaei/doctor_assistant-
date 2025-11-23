"""Onboarding agent for collecting client legal information through conversation"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
import json
import re


class OnboardingAgent(BaseAgent):
    """
    Onboarding Agent - Collects client legal information conversationally
    - Asks about legal areas of interest, active matters, restrictions
    - Extracts structured data from natural language responses
    - Fills client profile automatically
    - Professional, non-intrusive approach
    """

    def __init__(self):
        system_prompt = """You are a professional legal intake assistant helping to collect a client's legal information for their profile.

Your role is to:
1. Ask questions ONE AT A TIME in a conversational, professional manner
2. Extract and structure the information from their responses
3. Move through the client profile questions naturally
4. Be understanding if they prefer not to answer certain questions
5. Make the process feel like a natural conversation, not an interrogation

Client Information to Collect (in order):
1. Basic Info: Occupation, Employer (if applicable), Citizenship/Jurisdiction
2. Legal Areas of Interest: What areas of law are they interested in or seeking guidance on?
3. Active Legal Matters: Do they have any ongoing legal cases or matters?
4. Previous Legal Issues: Any past legal matters or cases?
5. Legal Restrictions: Any court orders, probation, restraining orders, or legal restrictions?
6. Business Entities: Do they own or have interest in any businesses?
7. Financial Concerns: Any financial legal issues (bankruptcy, liens, debt collection, etc.)?
8. Preferred Communication: How do they prefer to be contacted?

IMPORTANT GUIDELINES:
- Ask ONE question at a time
- Be professional and respectful
- Accept "none", "no", "I prefer not to say" as valid answers
- Maintain confidentiality and trust
- Explain WHY you're asking (helps provide better legal guidance)
- Allow them to skip sensitive questions
- Summarize what you've collected before finishing
- Remind them this is for informational purposes and not legal advice

Example conversation flow:
"Hello! To provide you with the most relevant legal information and resources, I'd like to learn a bit about your situation. This will only take a few minutes and helps me guide you to the right legal resources. Shall we begin?"

"Great! Let's start with some basic information. What is your current occupation?"

"Thank you! And what legal areas are you most interested in or seeking guidance on? For example: family law, contract law, employment law, real estate, criminal law, etc."

After collecting info, respond with a JSON object containing the extracted data.
"""

        super().__init__(
            name="Onboarding Agent",
            description="Conversational client profile collection",
            system_prompt=system_prompt,
            use_rag=False  # Don't need RAG for onboarding
        )

        # Questions to ask in order
        self.questions = [
            {
                "field": "basic_info",
                "question": "To provide you with relevant legal information, I'd like to know a bit about you. First, what is your current occupation?",
                "extract": ["occupation"]
            },
            {
                "field": "basic_info",
                "question": "Thanks! And if you're employed, who is your employer? You can skip this if you prefer.",
                "extract": ["employer"]
            },
            {
                "field": "basic_info",
                "question": "What is your citizenship or primary jurisdiction? This helps ensure we provide legally relevant information for your location.",
                "extract": ["citizenship"]
            },
            {
                "field": "legal_areas",
                "question": "What areas of law are you most interested in or seeking guidance on? For example: family law, employment law, contract law, real estate, criminal law, immigration, etc. Please list any that apply.",
                "extract": ["legal_areas_of_interest"]
            },
            {
                "field": "active_matters",
                "question": "Do you currently have any active legal matters or ongoing cases? If yes, please briefly describe them. If none, just say 'none'.",
                "extract": ["active_legal_matters"]
            },
            {
                "field": "previous_issues",
                "question": "Have you had any previous legal issues or cases in the past? If yes, please briefly mention the type and approximate timeframe.",
                "extract": ["previous_legal_issues"]
            },
            {
                "field": "restrictions",
                "question": "Do you have any current legal restrictions, such as court orders, probation, restraining orders, or similar? This is confidential and helps ensure accurate guidance.",
                "extract": ["legal_restrictions"]
            },
            {
                "field": "business",
                "question": "Do you own or have ownership interest in any business entities? If yes, please mention the business name and type (LLC, corporation, partnership, etc.).",
                "extract": ["business_entities"]
            },
            {
                "field": "financial",
                "question": "Do you have any financial legal concerns, such as bankruptcy, tax liens, foreclosure, or debt collection issues? Please list any that apply or say 'none'.",
                "extract": ["financial_concerns"]
            },
            {
                "field": "communication",
                "question": "Finally, how would you prefer to receive legal information and updates? For example: email, phone, text message, or in-person consultation.",
                "extract": ["preferred_communication"]
            },
        ]

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process onboarding conversation

        Args:
            input_data: Contains 'message' and 'onboarding_state'
            context: Conversation history and current profile data

        Returns:
            Next question or completed profile data
        """
        message = input_data.get("message", "")
        onboarding_state = input_data.get("onboarding_state", {})
        conversation_history = context.get("conversation_history", []) if context else []

        # Get current question index
        current_index = onboarding_state.get("current_question", 0)
        collected_data = onboarding_state.get("collected_data", {})

        # If user just started, welcome them
        if current_index == 0 and not conversation_history:
            return {
                "agent": self.name,
                "next_question": "Hello! 👋 To provide you with the most relevant legal information and resources, I'd like to learn a bit about your situation. This will only take a few minutes and helps me guide you to the right legal resources. All information is confidential. Shall we begin?",
                "onboarding_complete": False,
                "current_question": 0,
                "collected_data": collected_data
            }

        # Extract data from user's response
        if message and current_index > 0:  # Skip extraction for initial welcome
            extracted = await self._extract_data_from_response(
                message,
                self.questions[current_index - 1]["extract"]
            )
            collected_data.update(extracted)

        # Check if onboarding is complete
        if current_index >= len(self.questions):
            return {
                "agent": self.name,
                "onboarding_complete": True,
                "collected_data": collected_data,
                "summary": self._create_summary(collected_data),
                "completion_message": "Perfect! Thank you for sharing that information. I now have a good understanding of your legal situation, which will help me provide more relevant legal information and resources. Remember, this is for informational purposes only and does not constitute legal advice. How can I assist you today? 😊"
            }

        # Ask next question
        next_question_data = self.questions[current_index]

        return {
            "agent": self.name,
            "next_question": next_question_data["question"],
            "onboarding_complete": False,
            "current_question": current_index + 1,
            "collected_data": collected_data,
            "field": next_question_data["field"]
        }

    async def _extract_data_from_response(
        self,
        response: str,
        fields: List[str]
    ) -> Dict[str, Any]:
        """
        Use LLM to extract structured data from natural language response

        Args:
            response: User's natural language response
            fields: Fields to extract

        Returns:
            Structured data dictionary
        """
        extraction_prompt = f"""Extract the following client information from the user's response.
If information is not mentioned or user says "none"/"no"/"prefer not to say", return null for that field.

Response: "{response}"

Extract these fields: {', '.join(fields)}

Return ONLY a JSON object with these exact field names. Examples:

For occupation: {{"occupation": "Software Engineer"}}
For employer: {{"employer": "Tech Corp"}} or {{"employer": null}}
For citizenship: {{"citizenship": "United States"}}
For legal areas: {{"legal_areas_of_interest": ["family law", "employment law"]}}
For active matters: {{"active_legal_matters": [{{"description": "custody dispute", "status": "ongoing"}}]}} or {{"active_legal_matters": []}}
For previous issues: {{"previous_legal_issues": [{{"type": "contract dispute", "year": "2020"}}]}}
For restrictions: {{"legal_restrictions": [{{"type": "probation", "details": "expires 2025"}}]}} or {{"legal_restrictions": []}}
For business entities: {{"business_entities": [{{"name": "ABC LLC", "type": "LLC", "ownership_percentage": 50}}]}}
For financial concerns: {{"financial_concerns": ["bankruptcy consideration", "tax lien"]}} or {{"financial_concerns": []}}
For communication: {{"preferred_communication": "email"}}

Return ONLY the JSON, no explanation."""

        messages = self.create_messages(extraction_prompt)
        llm_response = await self.invoke_llm(messages, temperature=0.1)

        # Parse JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error parsing extraction: {e}")
            return {}

    def _create_summary(self, collected_data: Dict[str, Any]) -> str:
        """Create a professional summary of collected information"""
        summary_parts = []

        if collected_data.get("occupation"):
            summary_parts.append(f"Occupation: {collected_data['occupation']}")

        if collected_data.get("legal_areas_of_interest"):
            areas = collected_data["legal_areas_of_interest"]
            if areas:
                summary_parts.append(f"Legal interests: {', '.join(areas)}")

        if collected_data.get("active_legal_matters"):
            matters = [m.get("description", "") for m in collected_data.get("active_legal_matters", [])]
            if matters:
                summary_parts.append(f"Active matters: {', '.join(matters)}")

        if collected_data.get("business_entities"):
            entities = [e.get("name", "") for e in collected_data.get("business_entities", [])]
            if entities:
                summary_parts.append(f"Business entities: {', '.join(entities)}")

        if collected_data.get("legal_restrictions"):
            restrictions = [r.get("type", "") for r in collected_data.get("legal_restrictions", [])]
            if restrictions:
                summary_parts.append(f"Restrictions: {', '.join(restrictions)}")

        return " | ".join(summary_parts) if summary_parts else "Basic profile created"


class ProfileCompletionChecker:
    """Check if client profile is complete enough to skip onboarding"""

    REQUIRED_FIELDS = [
        "legal_areas_of_interest",  # Can be empty list
        "active_legal_matters",  # Can be empty list
    ]

    OPTIONAL_FIELDS = [
        "occupation",
        "citizenship",
        "previous_legal_issues",
        "legal_restrictions",
        "business_entities",
        "financial_concerns",
    ]

    @staticmethod
    def is_profile_complete(client_profile: Optional[Dict[str, Any]]) -> bool:
        """
        Check if profile has minimum required information

        Args:
            client_profile: Client profile data

        Returns:
            True if profile is complete enough
        """
        if not client_profile:
            return False

        # Check required fields exist (can be None/empty for some)
        for field in ProfileCompletionChecker.REQUIRED_FIELDS:
            if field not in client_profile:
                return False

        # If we have legal areas of interest, profile is minimally complete
        if client_profile.get("legal_areas_of_interest") is not None:
            return True

        return False

    @staticmethod
    def get_completion_percentage(client_profile: Optional[Dict[str, Any]]) -> int:
        """Get profile completion percentage"""
        if not client_profile:
            return 0

        all_fields = ProfileCompletionChecker.REQUIRED_FIELDS + ProfileCompletionChecker.OPTIONAL_FIELDS
        filled_fields = sum(1 for field in all_fields if client_profile.get(field) is not None)

        return int((filled_fields / len(all_fields)) * 100)

    @staticmethod
    def get_missing_fields(client_profile: Optional[Dict[str, Any]]) -> List[str]:
        """Get list of missing important fields"""
        if not client_profile:
            return ProfileCompletionChecker.REQUIRED_FIELDS + ProfileCompletionChecker.OPTIONAL_FIELDS

        missing = []
        for field in ProfileCompletionChecker.REQUIRED_FIELDS:
            if field not in client_profile or client_profile.get(field) is None:
                missing.append(field)

        return missing
