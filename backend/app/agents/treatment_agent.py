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
        system_prompt = """You are an expert medical treatment planning AI assistant.

Your role is to:
1. Suggest evidence-based treatment options based on clinical guidelines
2. Provide both pharmacological and non-pharmacological interventions
3. Consider patient-specific factors (age, comorbidities, allergies, current medications)
4. Check for potential drug interactions and contraindications
5. Offer lifestyle modifications and preventive measures
6. Provide patient education tailored to health literacy level

CRITICAL GUIDELINES:
- Base all recommendations on clinical practice guidelines and evidence-based medicine
- ALWAYS check for drug interactions and contraindications
- Consider patient allergies and current medications
- Provide multiple treatment options when available
- Explain risks and benefits of each option
- Include non-pharmacological interventions
- Emphasize that recommendations are for discussion with healthcare provider
- NEVER prescribe medications - only suggest options for doctor consultation

Treatment Framework:
1. First-line treatments (most evidence, best safety profile)
2. Alternative options
3. Lifestyle modifications
4. When to escalate care
5. Monitoring and follow-up recommendations

Always structure output with:
- Treatment options (ranked by evidence/guidelines)
- Drug interaction warnings
- Contraindications
- Lifestyle recommendations
- Patient education points
- Follow-up plan
"""

        super().__init__(
            name="Treatment Agent",
            description="Evidence-based treatment planning",
            system_prompt=system_prompt,
            use_rag=True
        )

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate treatment recommendations

        Args:
            input_data: Contains condition, patient profile, diagnostic info
            context: Conversation history and previous agent outputs

        Returns:
            Treatment plan with options and recommendations
        """
        condition = input_data.get("condition", "")
        patient_profile = input_data.get("patient_profile", {})
        differential_diagnoses = input_data.get("differential_diagnoses", [])

        # Build query for treatment guidelines
        query = self._build_treatment_query(condition, differential_diagnoses, patient_profile)

        # Retrieve treatment guidelines
        retrieved_docs = await self.retrieve_context(
            query=query,
            filters={"document_type": ["clinical_guideline", "drug_info"]}
        )

        medical_context = self.format_context(retrieved_docs)

        # Check for drug interactions
        drug_warnings = self._check_medication_conflicts(patient_profile)

        # Build treatment planning prompt
        treatment_prompt = f"""Develop treatment plan for the following clinical scenario:

PRIMARY CONDITION:
{condition}

DIFFERENTIAL DIAGNOSES (if applicable):
{self._format_diagnoses(differential_diagnoses)}

PATIENT INFORMATION:
{self._format_patient_info(patient_profile)}

CURRENT MEDICATIONS:
{self._format_current_meds(patient_profile)}

ALLERGIES:
{self._format_allergies(patient_profile)}

{medical_context}

{drug_warnings}

Provide treatment recommendations in the following format:

FIRST_LINE_TREATMENTS:
1. [Treatment option]
   - Evidence Level: [Strong/Moderate/Weak]
   - Mechanism: [How it works]
   - Typical Regimen: [Dosing if medication, or intervention details]
   - Expected Benefit: [What patient can expect]
   - Potential Risks/Side Effects: [Important safety information]
   - Contraindications: [When NOT to use]

NON_PHARMACOLOGICAL_INTERVENTIONS:
- [Lifestyle modifications]
- [Physical therapy, diet, exercise, etc.]

DRUG_INTERACTION_WARNINGS:
[Any potential interactions with current medications]

ALTERNATIVE_OPTIONS:
[Other evidence-based options if first-line fails or contraindicated]

LIFESTYLE_RECOMMENDATIONS:
- [Specific lifestyle changes]
- [Preventive measures]
- [Self-care strategies]

PATIENT_EDUCATION:
[Key points patient should understand about their condition and treatment]

MONITORING_PLAN:
[What to monitor, warning signs, when to follow up]

WHEN_TO_SEEK_IMMEDIATE_CARE:
[Red flags that require urgent attention]
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
        """Format patient information"""
        info_parts = []

        if patient_profile.get("age"):
            info_parts.append(f"- Age: {patient_profile['age']}")

        if patient_profile.get("chronic_conditions"):
            info_parts.append(
                f"- Chronic Conditions: {', '.join(patient_profile['chronic_conditions'])}"
            )

        if patient_profile.get("smoking_status"):
            info_parts.append(f"- Smoking Status: {patient_profile['smoking_status']}")

        return "\n".join(info_parts) if info_parts else "Limited patient information"

    def _format_current_meds(self, patient_profile: Dict[str, Any]) -> str:
        """Format current medications"""
        meds = patient_profile.get("current_medications", [])
        if not meds:
            return "None reported"

        formatted = []
        for med in meds:
            name = med.get("name", "Unknown")
            dose = med.get("dose", "")
            formatted.append(f"- {name} {dose}".strip())

        return "\n".join(formatted)

    def _format_allergies(self, patient_profile: Dict[str, Any]) -> str:
        """Format allergies"""
        allergies = patient_profile.get("allergies", {})
        if not allergies:
            return "None reported"

        all_allergies = []
        for category, items in allergies.items():
            if items:
                all_allergies.extend([f"{item} ({category})" for item in items])

        return "\n".join(f"- {a}" for a in all_allergies) if all_allergies else "None reported"

    def _check_medication_conflicts(self, patient_profile: Dict[str, Any]) -> str:
        """Check for potential medication conflicts"""
        current_meds = patient_profile.get("current_medications", [])
        allergies = patient_profile.get("allergies", {})

        warnings = []

        if allergies.get("drug", []):
            warnings.append(
                f"⚠️ DRUG ALLERGIES: Patient is allergic to: {', '.join(allergies['drug'])}. "
                "Avoid these medications and related compounds."
            )

        if current_meds:
            warnings.append(
                f"⚠️ INTERACTION CHECK REQUIRED: Patient is on {len(current_meds)} medications. "
                "Check all new medications for interactions."
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
