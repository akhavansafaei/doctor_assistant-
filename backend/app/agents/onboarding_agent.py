"""Onboarding agent for collecting patient health information through conversation"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
import json
import re


class OnboardingAgent(BaseAgent):
    """
    Onboarding Agent - Collects patient health information conversationally
    - Asks about basic info, medical history, medications, allergies
    - Extracts structured data from natural language responses
    - Fills health profile automatically
    - Friendly, non-intrusive approach
    """

    def __init__(self):
        system_prompt = """You are a friendly medical assistant helping to collect a patient's health information for their profile.

Your role is to:
1. Ask questions ONE AT A TIME in a conversational, friendly manner
2. Extract and structure the information from their responses
3. Move through the health profile questions naturally
4. Be understanding if they don't know or skip questions
5. Make the process feel like a natural conversation, not an interrogation

Health Information to Collect (in order):
1. Basic Info: Age, Gender, Height, Weight, Blood Type (if known)
2. Chronic Conditions: Do they have any ongoing health conditions? (diabetes, hypertension, asthma, etc.)
3. Allergies: Drug allergies, food allergies, environmental allergies
4. Current Medications: What medications are they currently taking?
5. Past Surgeries: Any previous surgeries or major medical procedures?
6. Lifestyle: Smoking status, alcohol consumption, exercise frequency
7. Emergency Contact: Name, phone, relationship (optional but recommended)

IMPORTANT GUIDELINES:
- Ask ONE question at a time
- Be warm and conversational
- Accept "none", "no", "I don't know" as valid answers
- Don't make them feel uncomfortable
- Explain WHY you're asking (helps provide better medical advice)
- Allow them to skip questions they're not comfortable answering
- Summarize what you've collected before finishing

Example conversation flow:
"Hi! To provide you with the most accurate health advice, I'd like to learn a bit about you. This will only take a minute and helps me give you personalized care. Is that okay?"

"Great! Let's start simple - how old are you?"

"Thanks! And what's your biological gender? This helps with gender-specific health considerations."

"Perfect! Do you happen to know your height and weight? This helps assess various health metrics."

After collecting info, respond with a JSON object containing the extracted data.
"""

        super().__init__(
            name="Onboarding Agent",
            description="Conversational health profile collection",
            system_prompt=system_prompt,
            use_rag=False  # Don't need RAG for onboarding
        )

        # Questions to ask in order
        self.questions = [
            {
                "field": "basic_info",
                "question": "To provide you with personalized health advice, I'd like to know a bit about you. First, how old are you?",
                "extract": ["age"]
            },
            {
                "field": "basic_info",
                "question": "Thanks! And what's your biological gender? This helps with gender-specific health considerations.",
                "extract": ["gender"]
            },
            {
                "field": "basic_info",
                "question": "Do you know your height and current weight? This helps assess various health metrics.",
                "extract": ["height_cm", "weight_kg"]
            },
            {
                "field": "chronic_conditions",
                "question": "Do you have any ongoing health conditions or chronic illnesses? For example, diabetes, high blood pressure, asthma, etc. If none, just say 'none'.",
                "extract": ["chronic_conditions"]
            },
            {
                "field": "allergies",
                "question": "Great! Now, do you have any allergies? This could be to medications, foods, or environmental things like pollen. Please list them or say 'none'.",
                "extract": ["allergies"]
            },
            {
                "field": "medications",
                "question": "Are you currently taking any medications regularly? Please include prescription and over-the-counter medications, or say 'none'.",
                "extract": ["current_medications"]
            },
            {
                "field": "surgeries",
                "question": "Have you had any surgeries or major medical procedures in the past? If yes, please briefly mention them.",
                "extract": ["past_surgeries"]
            },
            {
                "field": "lifestyle",
                "question": "A few lifestyle questions: Do you smoke? How often do you drink alcohol? And how frequently do you exercise?",
                "extract": ["smoking_status", "alcohol_consumption", "exercise_frequency"]
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
                "next_question": "Hi! 👋 To provide you with the most accurate health advice, I'd like to learn a bit about you. This will only take a minute and helps me give you personalized care. Shall we begin?",
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
                "completion_message": "Perfect! Thank you for sharing that information. I now have a good understanding of your health profile, which will help me provide more personalized and accurate advice. How can I help you today? 😊"
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
        extraction_prompt = f"""Extract the following health information from the user's response.
If information is not mentioned or user says "none"/"no", return null for that field.

Response: "{response}"

Extract these fields: {', '.join(fields)}

Return ONLY a JSON object with these exact field names. Examples:

For age: {{"age": 35}}
For gender: {{"gender": "male"}} or {{"gender": "female"}}
For height/weight: {{"height_cm": 175, "weight_kg": 70}}
For chronic conditions: {{"chronic_conditions": ["diabetes", "hypertension"]}} or {{"chronic_conditions": []}}
For allergies: {{"allergies": {{"drug": ["penicillin"], "food": ["peanuts"], "environmental": []}}}}
For medications: {{"current_medications": [{{"name": "Metformin", "dose": "500mg twice daily"}}]}}
For surgeries: {{"past_surgeries": [{{"name": "Appendectomy", "date": "2015"}}]}}
For lifestyle: {{"smoking_status": "never", "alcohol_consumption": "occasionally", "exercise_frequency": "3 times per week"}}

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
        """Create a friendly summary of collected information"""
        summary_parts = []

        if collected_data.get("age"):
            summary_parts.append(f"Age: {collected_data['age']}")

        if collected_data.get("chronic_conditions"):
            conditions = collected_data["chronic_conditions"]
            if conditions:
                summary_parts.append(f"Chronic conditions: {', '.join(conditions)}")

        if collected_data.get("current_medications"):
            meds = [m.get("name", "") for m in collected_data.get("current_medications", [])]
            if meds:
                summary_parts.append(f"Medications: {', '.join(meds)}")

        if collected_data.get("allergies"):
            allergies = collected_data["allergies"]
            all_allergies = []
            for category, items in allergies.items():
                if items:
                    all_allergies.extend(items)
            if all_allergies:
                summary_parts.append(f"Allergies: {', '.join(all_allergies)}")

        return " | ".join(summary_parts) if summary_parts else "Basic profile created"


class ProfileCompletionChecker:
    """Check if health profile is complete enough to skip onboarding"""

    REQUIRED_FIELDS = [
        "age",
        "chronic_conditions",  # Can be empty list
        "allergies",  # Can be empty dict
    ]

    OPTIONAL_FIELDS = [
        "height_cm",
        "weight_kg",
        "current_medications",
        "smoking_status",
    ]

    @staticmethod
    def is_profile_complete(health_profile: Optional[Dict[str, Any]]) -> bool:
        """
        Check if profile has minimum required information

        Args:
            health_profile: Health profile data

        Returns:
            True if profile is complete enough
        """
        if not health_profile:
            return False

        # Check required fields exist (can be None/empty for some)
        for field in ProfileCompletionChecker.REQUIRED_FIELDS:
            if field not in health_profile:
                return False

        # If we have age and at least checked allergies/conditions, it's complete
        if health_profile.get("age") is not None:
            return True

        return False

    @staticmethod
    def get_completion_percentage(health_profile: Optional[Dict[str, Any]]) -> int:
        """Get profile completion percentage"""
        if not health_profile:
            return 0

        all_fields = ProfileCompletionChecker.REQUIRED_FIELDS + ProfileCompletionChecker.OPTIONAL_FIELDS
        filled_fields = sum(1 for field in all_fields if health_profile.get(field) is not None)

        return int((filled_fields / len(all_fields)) * 100)

    @staticmethod
    def get_missing_fields(health_profile: Optional[Dict[str, Any]]) -> List[str]:
        """Get list of missing important fields"""
        if not health_profile:
            return ProfileCompletionChecker.REQUIRED_FIELDS + ProfileCompletionChecker.OPTIONAL_FIELDS

        missing = []
        for field in ProfileCompletionChecker.REQUIRED_FIELDS:
            if field not in health_profile or health_profile.get(field) is None:
                missing.append(field)

        return missing
