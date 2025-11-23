"""Treatment planning agent"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class TreatmentAgent(BaseAgent):
    """
    Treatment Planning Agent
    - Suggests evidence-based treatment options
    - Checks drug interactions
    - Provides lifestyle recommendations
    - Offers patient education
    """

    def __init__(self):
        system_prompt = """You are an expert fitness and nutrition planning AI assistant specializing in gym programs, bodybuilding, and Persian diet integration.

Your role is to:
1. Create personalized workout plans based on user's goals, equipment, and schedule
2. Design progressive training programs for muscle building, fat loss, or athletic performance
3. Provide detailed Persian diet plans (daily meals and general nutrition strategies)
4. Calculate and track caloric intake and macronutrient distribution
5. Adapt programs based on body composition, experience level, and available time
6. Integrate evidence-based training principles with practical nutrition guidance

CRITICAL GUIDELINES:
- Base all programs on exercise science and nutrition research
- Consider user's fitness level, training experience, and injury history
- Adapt exercises to available equipment (full gym, home gym, bodyweight, etc.)
- Match training volume and intensity to user's recovery capacity
- Provide Persian diet options that meet caloric and macro needs
- Include both daily meal plans and general dietary guidelines
- Account for training days per week and time per session
- Emphasize progressive overload and proper form
- NEVER recommend dangerous exercises or extreme diets

Training Program Framework:
1. Training Split: Based on days available and experience level
2. Exercise Selection: Matched to goals and equipment
3. Sets/Reps/Intensity: Progressive schemes for strength or hypertrophy
4. Progression Plan: How to increase difficulty over time
5. Recovery Considerations: Rest days, deloads, injury prevention

Nutrition Program Framework:
1. Caloric Target: Calculated from TDEE and goals
2. Macronutrient Split: Protein/carbs/fats optimized for goals
3. Persian Daily Meal Plan: Specific meals with portion sizes
4. General Persian Diet Guidelines: Food choices and timing
5. Meal Timing: Pre/post-workout nutrition strategies

Always structure output with:
- Complete workout program (exercises, sets, reps, rest)
- Progression scheme
- Persian diet plan (daily meals and general guidelines)
- Supplement suggestions (if applicable)
- Form cues and safety tips
- Tracking and adjustment strategies
"""

        super().__init__(
            name="Fitness Program Agent",
            description="Personalized workout and nutrition planning",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized fitness and nutrition program

        Args:
            input_data: Contains user goals, fitness profile, assessment results
            context: Conversation history and previous agent outputs

        Returns:
            Complete workout and nutrition program
        """
        user_goal = input_data.get("condition", "")
        patient_profile = input_data.get("patient_profile", {})
        fitness_assessment = input_data.get("differential_diagnoses", [])

        # Build query for fitness and nutrition guidelines
        query = self._build_treatment_query(user_goal, fitness_assessment, patient_profile)

        # Retrieve fitness and nutrition knowledge
        retrieved_docs = await self.retrieve_context(
            query=query,
            filters={"document_type": ["fitness_program", "nutrition_guide"]}
        )

        knowledge_context = self.format_context(retrieved_docs)

        # Check for injury or health considerations
        safety_notes = self._check_medication_conflicts(patient_profile)

        # Build program planning prompt
        treatment_prompt = f"""Create a comprehensive fitness and nutrition program for the following user:

USER GOAL:
{user_goal}

FITNESS ASSESSMENT (if available):
{self._format_diagnoses(fitness_assessment)}

USER FITNESS PROFILE:
{self._format_patient_info(patient_profile)}

AVAILABLE EQUIPMENT:
{self._format_current_meds(patient_profile)}

DIETARY PREFERENCES & RESTRICTIONS:
{self._format_allergies(patient_profile)}

{knowledge_context}

{safety_notes}

Provide a complete fitness and nutrition program in the following format:

TRAINING_PROGRAM_OVERVIEW:
- Training Split: [e.g., 4-day Upper/Lower, 5-day PPL, 3-day Full Body]
- Program Duration: [e.g., 8-12 weeks before reassessment]
- Primary Focus: [Strength/Hypertrophy/Fat Loss/Athletic Performance]

DETAILED_WORKOUT_PLAN:
Day 1 [Name]:
1. [Exercise Name]
   - Sets x Reps: [e.g., 3 x 8-10]
   - Rest: [e.g., 90 seconds]
   - Load: [e.g., RPE 8, or weight progression]
   - Form Cues: [Key points for proper execution]

2. [Next exercise...]
   ...

Day 2 [Name]:
[Continue for all training days...]

PROGRESSION_SCHEME:
- Week 1-4: [Volume/intensity/exercise variations]
- Week 5-8: [How to progress]
- Week 9-12: [Advanced progression]
- Deload Strategy: [When and how to reduce volume]

PERSIAN_DAILY_MEAL_PLAN:
Target: [Total calories] calories per day
Macros: [Protein]g P / [Carbs]g C / [Fat]g F

Breakfast (Time):
- [Persian dish with portions, e.g., "2 eggs + نان بربری (1 piece) + پنیر (50g)"]
- Calories: [amount] | P: [g] | C: [g] | F: [g]

Mid-Morning Snack:
- [Persian snack option]

Lunch (Time):
- [Persian main meal, e.g., "قورمه سبزی with rice (150g cooked)"]
- Calories: [amount] | P: [g] | C: [g] | F: [g]

Pre-Workout (if training):
- [Quick energy option]

Post-Workout (if training):
- [Protein-rich recovery meal]

Dinner (Time):
- [Persian dinner option]
- Calories: [amount] | P: [g] | C: [g] | F: [g]

Evening Snack (optional):
- [Light option if calories allow]

GENERAL_PERSIAN_DIET_GUIDELINES:
- Best Protein Sources: [Persian options like chicken, lamb, fish, eggs, lentils]
- Complex Carbs: [Rice varieties, bread types, legumes]
- Healthy Fats: [Olive oil, nuts, kashk]
- Meal Timing: [When to eat relative to training]
- Hydration: [Water intake recommendations]
- Persian Foods to Emphasize: [List]
- Persian Foods to Moderate: [List]

SUPPLEMENT_RECOMMENDATIONS (optional):
- [Evidence-based supplements if beneficial]
- [Dosing and timing]

FORM_AND_SAFETY_TIPS:
- [Exercise-specific cues]
- [Injury prevention strategies]
- [When to reduce load or modify exercises]

TRACKING_AND_ADJUSTMENTS:
- Track: [Bodyweight, measurements, performance metrics]
- Progress Indicators: [What shows program is working]
- When to Adjust: [Plateaus, excessive fatigue, etc.]
- Modification Strategies: [How to adapt program]
"""

        # Get conversation history
        conversation_history = context.get("conversation_history", []) if context else []

        # Create messages
        messages = self.create_messages(
            user_message=treatment_prompt,
            conversation_history=conversation_history[-4:]
        )

        # Invoke LLM
        response = await self.invoke_llm(messages, temperature=0.1)

        # Parse response
        parsed = self._parse_treatment_output(response)

        # Add sources
        parsed["sources"] = [
            {
                "title": doc.get("metadata", {}).get("title", "Clinical Guideline"),
                "text": doc["text"][:300],
                "source": doc.get("metadata", {}).get("source", "Unknown"),
                "relevance_score": doc.get("rerank_score", doc.get("rrf_score", 0))
            }
            for doc in retrieved_docs[:5]
        ]

        parsed["agent"] = self.name
        parsed["raw_response"] = response

        return parsed

    def _build_treatment_query(
        self,
        condition: str,
        differential_diagnoses: List[Dict[str, Any]],
        patient_profile: Dict[str, Any]
    ) -> str:
        """Build query for treatment guideline retrieval"""
        query_parts = [f"treatment for {condition}"]

        if differential_diagnoses:
            top_diagnosis = differential_diagnoses[0].get("condition", "")
            if top_diagnosis:
                query_parts.append(f"management of {top_diagnosis}")

        # Add patient-specific factors
        if patient_profile.get("chronic_conditions"):
            query_parts.append(f"in patient with {patient_profile['chronic_conditions'][0]}")

        return " ".join(query_parts)

    def _format_diagnoses(self, diagnoses: List[Dict[str, Any]]) -> str:
        """Format differential diagnoses"""
        if not diagnoses:
            return "None provided"

        formatted = []
        for i, dx in enumerate(diagnoses[:3], 1):
            condition = dx.get("condition", "Unknown")
            likelihood = dx.get("likelihood", "")
            formatted.append(f"{i}. {condition} ({likelihood})")

        return "\n".join(formatted)

    def _format_patient_info(self, patient_profile: Dict[str, Any]) -> str:
        """Format user fitness profile"""
        info_parts = []

        if patient_profile.get("age"):
            info_parts.append(f"- Age: {patient_profile['age']}")

        if patient_profile.get("gender"):
            info_parts.append(f"- Gender: {patient_profile['gender']}")

        if patient_profile.get("height_cm") and patient_profile.get("weight_kg"):
            info_parts.append(f"- Height: {patient_profile['height_cm']}cm, Weight: {patient_profile['weight_kg']}kg")

        if patient_profile.get("fitness_level"):
            info_parts.append(f"- Fitness Level: {patient_profile['fitness_level']}")

        if patient_profile.get("training_experience"):
            info_parts.append(f"- Training Experience: {patient_profile['training_experience']}")

        if patient_profile.get("fitness_goals"):
            info_parts.append(f"- Goals: {', '.join(patient_profile['fitness_goals'])}")

        if patient_profile.get("training_days_per_week"):
            info_parts.append(f"- Training Days Per Week: {patient_profile['training_days_per_week']}")

        if patient_profile.get("training_duration_minutes"):
            info_parts.append(f"- Training Duration: {patient_profile['training_duration_minutes']} min/session")

        if patient_profile.get("exercise_frequency"):
            info_parts.append(f"- Current Activity Level: {patient_profile['exercise_frequency']}")

        return "\n".join(info_parts) if info_parts else "Limited fitness profile information"

    def _format_current_meds(self, patient_profile: Dict[str, Any]) -> str:
        """Format available equipment"""
        equipment = patient_profile.get("available_equipment", [])
        if not equipment:
            return "Not specified (assume bodyweight only or inquire)"

        return "\n".join(f"- {item}" for item in equipment)

    def _format_allergies(self, patient_profile: Dict[str, Any]) -> str:
        """Format dietary preferences and restrictions"""
        info_parts = []

        if patient_profile.get("diet_preference"):
            info_parts.append(f"- Diet Preference: {patient_profile['diet_preference']}")

        if patient_profile.get("food_allergies"):
            info_parts.append(f"- Food Allergies: {', '.join(patient_profile['food_allergies'])}")

        if patient_profile.get("dietary_restrictions"):
            info_parts.append(f"- Dietary Restrictions: {', '.join(patient_profile['dietary_restrictions'])}")

        return "\n".join(info_parts) if info_parts else "None reported - flexible with Persian diet"

    def _check_medication_conflicts(self, patient_profile: Dict[str, Any]) -> str:
        """Check for injuries and health considerations"""
        current_injuries = patient_profile.get("current_injuries", [])
        health_conditions = patient_profile.get("health_conditions", [])

        warnings = []

        if current_injuries:
            warnings.append(
                f"⚠️ INJURY CONSIDERATIONS: User has current injuries: {', '.join(current_injuries)}. "
                "Modify exercises to avoid aggravating these injuries."
            )

        if health_conditions:
            warnings.append(
                f"⚠️ HEALTH CONDITIONS: User has: {', '.join(health_conditions)}. "
                "Ensure program is safe and appropriate for these conditions."
            )

        return "\n".join(warnings) if warnings else ""

    def _parse_treatment_output(self, response: str) -> Dict[str, Any]:
        """Parse treatment plan from response"""
        import re

        result = {
            "first_line_treatments": [],
            "non_pharmacological": [],
            "drug_warnings": [],
            "alternative_options": [],
            "lifestyle_recommendations": [],
            "patient_education": "",
            "monitoring_plan": "",
            "red_flags": ""
        }

        # Extract sections
        result["patient_education"] = self._extract_section(response, "PATIENT_EDUCATION")
        result["monitoring_plan"] = self._extract_section(response, "MONITORING_PLAN")
        result["red_flags"] = self._extract_section(response, "WHEN_TO_SEEK_IMMEDIATE_CARE")

        # Extract lists
        non_pharm = self._extract_section(response, "NON_PHARMACOLOGICAL_INTERVENTIONS")
        if non_pharm:
            result["non_pharmacological"] = [
                line.strip('- ').strip()
                for line in non_pharm.split('\n')
                if line.strip().startswith('-')
            ]

        lifestyle = self._extract_section(response, "LIFESTYLE_RECOMMENDATIONS")
        if lifestyle:
            result["lifestyle_recommendations"] = [
                line.strip('- ').strip()
                for line in lifestyle.split('\n')
                if line.strip().startswith('-')
            ]

        warnings = self._extract_section(response, "DRUG_INTERACTION_WARNINGS")
        if warnings:
            result["drug_warnings"] = [w.strip() for w in warnings.split('\n') if w.strip()]

        return result

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract section from response"""
        import re
        pattern = f"{section_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
