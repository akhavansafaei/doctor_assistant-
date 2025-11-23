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
        system_prompt = """You are a friendly fitness assistant helping to collect a user's fitness profile information.

Your role is to:
1. Ask questions ONE AT A TIME in a conversational, friendly manner
2. Extract and structure the information from their responses
3. Move through the fitness profile questions naturally
4. Be understanding if they don't know or skip questions
5. Make the process feel like a natural conversation, not an interrogation

Fitness Information to Collect (in order):
1. Basic Info: Age, Gender, Height, Weight
2. Fitness Goals: What do they want to achieve? (muscle gain, fat loss, strength, athletic performance, general fitness)
3. Current Fitness Level: Beginner, Intermediate, Advanced
4. Training Experience: How long have they been training?
5. Available Equipment: Full gym, home gym with equipment, dumbbells only, bodyweight only?
6. Training Schedule: How many days per week can they train? How much time per session?
7. Current Injuries or Health Conditions: Any injuries or health issues to consider?
8. Diet Preference: Do they prefer Persian cuisine? Any dietary restrictions or food allergies?
9. Current Activity Level: How active are they currently?

IMPORTANT GUIDELINES:
- Ask ONE question at a time
- Be warm and conversational
- Accept "none", "no", "I don't know" as valid answers
- Don't make them feel uncomfortable
- Explain WHY you're asking (helps provide better fitness and nutrition guidance)
- Allow them to skip questions they're not comfortable answering
- Summarize what you've collected before finishing

Example conversation flow:
"Hi! To create the perfect fitness and nutrition plan for you, I'd like to learn about your goals and current situation. This will only take a minute and helps me give you personalized guidance. Sound good?"

"Awesome! Let's start simple - how old are you?"

"Thanks! And what's your gender? This helps with things like calorie calculations and training recommendations."

"Perfect! Do you know your height and weight? This helps me calculate your caloric needs and track progress."

After collecting info, respond with a JSON object containing the extracted data.
"""

        super().__init__(
            name="Onboarding Agent",
            description="Conversational fitness profile collection",
            system_prompt=system_prompt,
            use_rag=False  # Don't need RAG for onboarding
        )

        # Questions to ask in order
        self.questions = [
            {
                "field": "basic_info",
                "question": "To create the perfect fitness and nutrition plan for you, I'd like to know a bit about you. First, how old are you?",
                "extract": ["age"]
            },
            {
                "field": "basic_info",
                "question": "Thanks! And what's your gender? This helps with calorie calculations and training recommendations.",
                "extract": ["gender"]
            },
            {
                "field": "basic_info",
                "question": "Perfect! Do you know your height and current weight? This helps me calculate your caloric needs and track progress.",
                "extract": ["height_cm", "weight_kg"]
            },
            {
                "field": "fitness_goals",
                "question": "Great! Now, what are your main fitness goals? For example: muscle gain, fat loss, strength building, athletic performance, or general fitness. You can have multiple goals!",
                "extract": ["fitness_goals"]
            },
            {
                "field": "fitness_level",
                "question": "How would you describe your current fitness level? Beginner, Intermediate, or Advanced?",
                "extract": ["fitness_level"]
            },
            {
                "field": "training_experience",
                "question": "How long have you been training or working out? This helps me design an appropriate program for your experience level.",
                "extract": ["training_experience"]
            },
            {
                "field": "equipment",
                "question": "What equipment do you have access to? Full gym, home gym with equipment, dumbbells only, or just bodyweight?",
                "extract": ["available_equipment"]
            },
            {
                "field": "schedule",
                "question": "How many days per week can you train, and how much time do you have per session?",
                "extract": ["training_days_per_week", "training_duration_minutes"]
            },
            {
                "field": "health_and_injuries",
                "question": "Do you have any current injuries or health conditions I should know about? This helps me keep your program safe and effective.",
                "extract": ["current_injuries", "health_conditions"]
            },
            {
                "field": "diet",
                "question": "Do you prefer Persian cuisine for your meal plans? Also, do you have any dietary restrictions or food allergies?",
                "extract": ["diet_preference", "dietary_restrictions", "food_allergies"]
            },
            {
                "field": "current_activity",
                "question": "Finally, how active are you currently? This helps me understand your starting point.",
                "extract": ["exercise_frequency"]
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
                "next_question": "Hi! 💪 To create the perfect fitness and nutrition plan for you, I'd like to learn about your goals and current situation. This will only take a minute and helps me give you personalized guidance. Ready to get started?",
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
                "completion_message": "Awesome! Thank you for sharing that information. I now have a complete understanding of your fitness profile and goals. I'm ready to help you with personalized workout plans, Persian diet recommendations, and fitness guidance. What would you like to work on first? 💪"
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
        extraction_prompt = f"""Extract the following fitness information from the user's response.
If information is not mentioned or user says "none"/"no", return null for that field.

Response: "{response}"

Extract these fields: {', '.join(fields)}

Return ONLY a JSON object with these exact field names. Examples:

For age: {{"age": 28}}
For gender: {{"gender": "male"}} or {{"gender": "female"}}
For height/weight: {{"height_cm": 180, "weight_kg": 75}}
For fitness goals: {{"fitness_goals": ["muscle gain", "strength building"]}} or {{"fitness_goals": ["fat loss"]}}
For fitness level: {{"fitness_level": "intermediate"}} or {{"fitness_level": "beginner"}}
For training experience: {{"training_experience": "2 years"}} or {{"training_experience": "6 months"}}
For equipment: {{"available_equipment": ["full gym"]}} or {{"available_equipment": ["dumbbells", "resistance bands"]}}
For schedule: {{"training_days_per_week": 4, "training_duration_minutes": 60}}
For injuries/health: {{"current_injuries": ["knee pain"], "health_conditions": ["high blood pressure"]}} or {{"current_injuries": [], "health_conditions": []}}
For diet: {{"diet_preference": "Persian cuisine", "dietary_restrictions": ["vegetarian"], "food_allergies": ["peanuts"]}}
For activity: {{"exercise_frequency": "3-4 times per week"}}

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

        if collected_data.get("fitness_level"):
            summary_parts.append(f"Level: {collected_data['fitness_level']}")

        if collected_data.get("fitness_goals"):
            goals = collected_data["fitness_goals"]
            if isinstance(goals, list) and goals:
                summary_parts.append(f"Goals: {', '.join(goals)}")

        if collected_data.get("training_days_per_week"):
            summary_parts.append(f"Training: {collected_data['training_days_per_week']}x/week")

        if collected_data.get("diet_preference"):
            summary_parts.append(f"Diet: {collected_data['diet_preference']}")

        if collected_data.get("available_equipment"):
            equipment = collected_data["available_equipment"]
            if isinstance(equipment, list) and equipment:
                summary_parts.append(f"Equipment: {', '.join(equipment)}")

        return " | ".join(summary_parts) if summary_parts else "Basic fitness profile created"


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
