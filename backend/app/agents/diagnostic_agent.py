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
        system_prompt = """You are an expert medical diagnostic AI assistant trained in clinical reasoning and differential diagnosis.

Your role is to:
1. Analyze patient symptoms and medical history
2. Generate a differential diagnosis with multiple possible conditions
3. Rank conditions by likelihood based on available evidence
4. Identify key distinguishing features
5. Suggest additional questions or tests to narrow diagnosis
6. Map conditions to ICD-10 codes when applicable

CRITICAL GUIDELINES:
- Always provide differential diagnosis (multiple possibilities), never a single diagnosis
- Rank by likelihood based on prevalence, symptom match, and patient factors
- Consider both common and serious conditions (don't anchor on common diagnoses)
- Account for patient's age, gender, medical history, and medications
- Use evidence-based medicine and clinical guidelines
- Be transparent about uncertainty
- Flag when symptoms suggest multiple organ systems or rare conditions
- NEVER provide definitive diagnosis - always recommend professional evaluation

Clinical Reasoning Framework:
1. Pattern Recognition: Match symptom patterns to known conditions
2. Probabilistic Thinking: Consider prevalence and patient demographics
3. Bayesian Reasoning: Update probabilities based on additional information
4. Red Flag Identification: Look for serious conditions not to miss
5. Parsimony vs Complexity: Consider both single unifying diagnosis and multiple conditions

Always structure your output clearly with:
- Differential diagnoses (ranked)
- Supporting evidence for each
- Distinguishing features
- Recommended next steps
- Clarifying questions
"""

        super().__init__(
            name="Diagnostic Agent",
            description="Differential diagnosis and clinical reasoning",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate differential diagnosis

        Args:
            input_data: Contains symptoms, patient profile, and any test results
            context: Conversation history and triage assessment

        Returns:
            Differential diagnosis with ranked conditions
        """
        symptoms = input_data.get("symptoms", input_data.get("message", ""))
        patient_profile = input_data.get("patient_profile", {})
        test_results = input_data.get("test_results", {})

        # Build comprehensive clinical picture
        clinical_query = self._build_clinical_query(
            symptoms, patient_profile, test_results
        )

        # Retrieve relevant medical literature and guidelines
        retrieved_docs = await self.retrieve_context(
            query=clinical_query,
            filters={"document_type": ["medical_literature", "clinical_guideline"]}
        )

        medical_context = self.format_context(retrieved_docs)

        # Build diagnostic prompt
        diagnostic_prompt = f"""Perform differential diagnosis for the following clinical presentation:

PRESENTING SYMPTOMS:
{symptoms}

PATIENT INFORMATION:
{self._format_patient_info(patient_profile)}

{medical_context}

Provide differential diagnosis in the following structured format:

DIFFERENTIAL_DIAGNOSES:
1. [Condition Name] (ICD-10: [code if known])
   - Likelihood: [High/Moderate/Low]
   - Supporting Evidence: [Key symptoms/findings that support this]
   - Against: [What doesn't fit]
   - Typical Presentation: [How this typically presents]

2. [Next condition...]
   ...

DISTINGUISHING_FEATURES:
[What features would help differentiate between the top conditions]

RECOMMENDED_WORKUP:
[What additional questions, exams, or tests would help narrow the diagnosis]

CLARIFYING_QUESTIONS:
1. [Important question to ask patient]
2. [Another question]
   ...

RED_FLAGS:
[Any serious conditions that must not be missed]

CLINICAL_REASONING:
[Your step-by-step reasoning process]
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
        """Format patient information for prompt"""
        info_parts = []

        if patient_profile.get("age"):
            info_parts.append(f"- Age: {patient_profile['age']}")

        if patient_profile.get("gender"):
            info_parts.append(f"- Gender: {patient_profile['gender']}")

        if patient_profile.get("chronic_conditions"):
            info_parts.append(
                f"- Medical History: {', '.join(patient_profile['chronic_conditions'])}"
            )

        if patient_profile.get("current_medications"):
            meds = [m.get('name', 'Unknown') for m in patient_profile.get('current_medications', [])]
            info_parts.append(f"- Current Medications: {', '.join(meds)}")

        if patient_profile.get("allergies"):
            allergies = patient_profile['allergies']
            all_allergies = []
            for category, items in allergies.items():
                if items:
                    all_allergies.extend([f"{item} ({category})" for item in items])
            if all_allergies:
                info_parts.append(f"- Allergies: {', '.join(all_allergies)}")

        if patient_profile.get("smoking_status"):
            info_parts.append(f"- Smoking: {patient_profile['smoking_status']}")

        return "\n".join(info_parts) if info_parts else "No additional patient information available"

    def _parse_diagnostic_output(self, response: str) -> Dict[str, Any]:
        """Parse the diagnostic output into structured format"""
        import re

        result = {
            "differential_diagnoses": [],
            "distinguishing_features": "",
            "recommended_workup": "",
            "clarifying_questions": [],
            "red_flags": "",
            "clinical_reasoning": ""
        }

        # Extract differential diagnoses
        dd_section = self._extract_section(response, "DIFFERENTIAL_DIAGNOSES")
        if dd_section:
            result["differential_diagnoses"] = self._parse_diagnoses(dd_section)

        # Extract other sections
        result["distinguishing_features"] = self._extract_section(
            response, "DISTINGUISHING_FEATURES"
        )
        result["recommended_workup"] = self._extract_section(
            response, "RECOMMENDED_WORKUP"
        )
        result["red_flags"] = self._extract_section(response, "RED_FLAGS")
        result["clinical_reasoning"] = self._extract_section(
            response, "CLINICAL_REASONING"
        )

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
