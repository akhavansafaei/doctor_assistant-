"""Diagnostic reasoning agent for differential diagnosis"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json


class DiagnosticAgent(BaseAgent):
    """
    Diagnostic Reasoning Agent
    - Generates differential diagnoses
    - Asks clarifying questions
    - Maps to ICD-10 codes
    - Provides evidence-based reasoning
    """

    def __init__(self):
        system_prompt = """You are an expert fitness and body composition assessment AI assistant trained in exercise science and nutritional analysis.

Your role is to:
1. Analyze user's fitness level, body composition, and physical condition
2. Assess current performance capabilities and limitations
3. Evaluate nutritional status and caloric needs
4. Identify training imbalances, weaknesses, or areas for improvement
5. Suggest assessments or measurements to better understand fitness status
6. Provide evidence-based analysis using sports science principles

CRITICAL GUIDELINES:
- Provide comprehensive assessment considering multiple factors
- Analyze body composition based on photos, measurements, or descriptions
- Calculate caloric needs based on activity level, goals, and body composition
- Consider user's experience level, current training, and goals
- Use evidence-based exercise science and nutrition research
- Be transparent about limitations of remote assessment
- Recommend professional assessment (DEXA scan, VO2 max testing) when appropriate
- Account for individual variation and genetic factors

Assessment Framework:
1. Body Composition Analysis: Estimate body fat percentage, muscle mass distribution
2. Fitness Level Assessment: Cardiovascular fitness, strength level, flexibility
3. Nutritional Analysis: Caloric needs (TDEE), macronutrient ratios, Persian diet integration
4. Training Status: Recovery, overtraining signs, training age
5. Goal Alignment: How current state aligns with stated goals

Always structure your output clearly with:
- Body composition assessment
- Fitness level evaluation
- Caloric and nutritional needs
- Strengths and weaknesses
- Specific recommendations for improvement
- Clarifying questions or suggested assessments
"""

        super().__init__(
            name="Fitness Assessment Agent",
            description="Fitness level and body composition assessment",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate fitness and body composition assessment

        Args:
            input_data: Contains user query, fitness profile, and any measurements/photos
            context: Conversation history and triage assessment

        Returns:
            Comprehensive fitness assessment with recommendations
        """
        user_query = input_data.get("symptoms", input_data.get("message", ""))
        patient_profile = input_data.get("patient_profile", {})
        measurements = input_data.get("test_results", {})

        # Build comprehensive fitness query
        fitness_query = self._build_clinical_query(
            user_query, patient_profile, measurements
        )

        # Retrieve relevant fitness and nutrition knowledge
        retrieved_docs = await self.retrieve_context(
            query=fitness_query,
            filters={"document_type": ["fitness_science", "nutrition_guideline"]}
        )

        knowledge_context = self.format_context(retrieved_docs)

        # Build assessment prompt
        diagnostic_prompt = f"""Perform comprehensive fitness assessment for the following:

USER QUERY/GOAL:
{user_query}

USER FITNESS PROFILE:
{self._format_patient_info(patient_profile)}

{knowledge_context}

Provide comprehensive fitness assessment in the following structured format:

BODY_COMPOSITION_ASSESSMENT:
- Estimated Body Fat Percentage: [Estimate based on available info]
- Muscle Mass Distribution: [Analysis of muscle development]
- Body Type Classification: [Ectomorph/Mesomorph/Endomorph tendencies]
- Visual Assessment Notes: [If photo provided, detailed analysis]

FITNESS_LEVEL_EVALUATION:
- Cardiovascular Fitness: [Estimated level]
- Strength Level: [Beginner/Intermediate/Advanced/Elite]
- Flexibility & Mobility: [Assessment if mentioned]
- Training Age: [Estimated based on experience]

CALORIC_AND_NUTRITIONAL_NEEDS:
- Estimated TDEE (Total Daily Energy Expenditure): [Calculation]
- Caloric Goal for User's Objective: [Surplus/Deficit/Maintenance with amount]
- Recommended Macronutrient Ratios: [Protein/Carbs/Fats in grams and percentages]
- Persian Diet Integration: [How to meet needs with Persian cuisine]

STRENGTHS_AND_WEAKNESSES:
- Current Strengths: [What user is doing well]
- Areas for Improvement: [Specific weaknesses or imbalances]
- Training Gaps: [What's missing from current routine]

RECOMMENDATIONS:
1. [Specific recommendation for improvement]
2. [Another recommendation]
   ...

CLARIFYING_QUESTIONS:
1. [Important question to better assess user]
2. [Another question]
   ...

SUGGESTED_ASSESSMENTS:
[Measurements or tests that would provide better data - body measurements, photos, performance tests]

ASSESSMENT_REASONING:
[Your step-by-step analysis process]
"""

        # Get conversation history
        conversation_history = context.get("conversation_history", []) if context else []

        # Create messages
        messages = self.create_messages(
            user_message=diagnostic_prompt,
            conversation_history=conversation_history[-6:]  # Last 3 exchanges
        )

        # Invoke LLM with slightly higher temperature for creativity
        response = await self.invoke_llm(messages, temperature=0.2)

        # Parse structured output
        parsed = self._parse_diagnostic_output(response)

        # Add sources
        parsed["sources"] = [
            {
                "title": doc.get("metadata", {}).get("title", "Medical Source"),
                "text": doc["text"][:300],
                "source": doc.get("metadata", {}).get("source", "Unknown"),
                "relevance_score": doc.get("rerank_score", doc.get("rrf_score", 0))
            }
            for doc in retrieved_docs[:5]
        ]

        parsed["agent"] = self.name
        parsed["raw_response"] = response

        return parsed

    def _build_clinical_query(
        self,
        symptoms: str,
        patient_profile: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> str:
        """Build comprehensive query for knowledge retrieval"""
        query_parts = [symptoms]

        # Add relevant patient factors
        if patient_profile.get("age"):
            query_parts.append(f"age {patient_profile['age']}")

        if patient_profile.get("chronic_conditions"):
            query_parts.append(
                f"history of {', '.join(patient_profile['chronic_conditions'])}"
            )

        # Add test results if available
        if test_results:
            query_parts.append(f"with findings: {str(test_results)}")

        return " ".join(query_parts)

    def _format_patient_info(self, patient_profile: Dict[str, Any]) -> str:
        """Format user fitness profile for prompt"""
        info_parts = []

        if patient_profile.get("age"):
            info_parts.append(f"- Age: {patient_profile['age']}")

        if patient_profile.get("gender"):
            info_parts.append(f"- Gender: {patient_profile['gender']}")

        if patient_profile.get("height_cm") and patient_profile.get("weight_kg"):
            height = patient_profile['height_cm']
            weight = patient_profile['weight_kg']
            bmi = weight / ((height / 100) ** 2)
            info_parts.append(f"- Height: {height} cm, Weight: {weight} kg (BMI: {bmi:.1f})")

        if patient_profile.get("fitness_level"):
            info_parts.append(f"- Current Fitness Level: {patient_profile['fitness_level']}")

        if patient_profile.get("training_experience"):
            info_parts.append(f"- Training Experience: {patient_profile['training_experience']}")

        if patient_profile.get("fitness_goals"):
            info_parts.append(f"- Fitness Goals: {', '.join(patient_profile['fitness_goals'])}")

        if patient_profile.get("available_equipment"):
            info_parts.append(f"- Available Equipment: {', '.join(patient_profile['available_equipment'])}")

        if patient_profile.get("training_days_per_week"):
            info_parts.append(f"- Training Days Per Week: {patient_profile['training_days_per_week']}")

        if patient_profile.get("training_duration_minutes"):
            info_parts.append(f"- Training Duration: {patient_profile['training_duration_minutes']} minutes per session")

        if patient_profile.get("diet_preference"):
            info_parts.append(f"- Diet Preference: {patient_profile['diet_preference']}")

        if patient_profile.get("health_conditions"):
            info_parts.append(f"- Health Conditions to Consider: {', '.join(patient_profile['health_conditions'])}")

        if patient_profile.get("current_injuries"):
            info_parts.append(f"- Current Injuries: {', '.join(patient_profile['current_injuries'])}")

        if patient_profile.get("exercise_frequency"):
            info_parts.append(f"- Current Exercise Frequency: {patient_profile['exercise_frequency']}")

        return "\n".join(info_parts) if info_parts else "No fitness profile information available"

    def _parse_diagnostic_output(self, response: str) -> Dict[str, Any]:
        """Parse the fitness assessment output into structured format"""
        import re

        result = {
            "body_composition_assessment": "",
            "fitness_level_evaluation": "",
            "caloric_and_nutritional_needs": "",
            "strengths_and_weaknesses": "",
            "recommendations": [],
            "clarifying_questions": [],
            "suggested_assessments": "",
            "assessment_reasoning": ""
        }

        # Extract assessment sections
        result["body_composition_assessment"] = self._extract_section(
            response, "BODY_COMPOSITION_ASSESSMENT"
        )
        result["fitness_level_evaluation"] = self._extract_section(
            response, "FITNESS_LEVEL_EVALUATION"
        )
        result["caloric_and_nutritional_needs"] = self._extract_section(
            response, "CALORIC_AND_NUTRITIONAL_NEEDS"
        )
        result["strengths_and_weaknesses"] = self._extract_section(
            response, "STRENGTHS_AND_WEAKNESSES"
        )
        result["suggested_assessments"] = self._extract_section(
            response, "SUGGESTED_ASSESSMENTS"
        )
        result["assessment_reasoning"] = self._extract_section(
            response, "ASSESSMENT_REASONING"
        )

        # Extract recommendations list
        recommendations_section = self._extract_section(response, "RECOMMENDATIONS")
        if recommendations_section:
            recommendations = re.findall(r'^\d+\.\s*(.+)$', recommendations_section, re.MULTILINE)
            result["recommendations"] = recommendations

        # Extract clarifying questions
        questions_section = self._extract_section(response, "CLARIFYING_QUESTIONS")
        if questions_section:
            questions = re.findall(r'^\d+\.\s*(.+)$', questions_section, re.MULTILINE)
            result["clarifying_questions"] = questions

        return result

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from the response"""
        pattern = f"{section_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_diagnoses(self, dd_text: str) -> List[Dict[str, Any]]:
        """Parse differential diagnoses from text"""
        diagnoses = []
        current_diagnosis = None

        lines = dd_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a new diagnosis (starts with number)
            if re.match(r'^\d+\.', line):
                if current_diagnosis:
                    diagnoses.append(current_diagnosis)

                # Extract condition name and ICD code
                condition_match = re.match(
                    r'^\d+\.\s*(.+?)(?:\s*\(ICD-10:\s*([A-Z0-9.]+)\))?',
                    line
                )
                if condition_match:
                    current_diagnosis = {
                        "condition": condition_match.group(1).strip(),
                        "icd10_code": condition_match.group(2),
                        "likelihood": "",
                        "supporting_evidence": "",
                        "against": "",
                        "typical_presentation": ""
                    }
            elif current_diagnosis:
                # Parse sub-fields
                if "Likelihood:" in line:
                    current_diagnosis["likelihood"] = line.split(":", 1)[1].strip()
                elif "Supporting Evidence:" in line:
                    current_diagnosis["supporting_evidence"] = line.split(":", 1)[1].strip()
                elif "Against:" in line:
                    current_diagnosis["against"] = line.split(":", 1)[1].strip()
                elif "Typical Presentation:" in line:
                    current_diagnosis["typical_presentation"] = line.split(":", 1)[1].strip()

        # Add last diagnosis
        if current_diagnosis:
            diagnoses.append(current_diagnosis)

        return diagnoses
