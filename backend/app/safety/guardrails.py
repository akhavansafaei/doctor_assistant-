"""AI Safety Guardrails for medical chatbot"""
from typing import Dict, Any, List, Optional
import re


class SafetyGuardrails:
    """
    Implements safety guardrails for medical AI
    - Validates LLM outputs for medical accuracy
    - Prevents hallucinations
    - Enforces medical disclaimers
    - Blocks inappropriate responses
    """

    # Prohibited actions/claims
    PROHIBITED_PATTERNS = [
        r"i\s+(?:can|will)\s+diagnose",
        r"you\s+(?:definitely|certainly)\s+have",
        r"this\s+is\s+(?:definitely|certainly)",
        r"i\s+(?:can|will)\s+prescribe",
        r"take\s+\d+\s+(?:mg|pills|tablets)",  # Specific dosing
        r"(?:guaranteed|guarantee)\s+(?:cure|treatment)",
        r"no\s+need\s+to\s+see\s+(?:a\s+)?doctor",
        r"don't\s+(?:see|consult)\s+(?:a\s+)?doctor",
    ]

    # Required disclaimers
    REQUIRED_DISCLAIMERS = {
        "general": "This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.",
        "emergency": "If you are experiencing a medical emergency, call 911 or go to the nearest emergency room immediately.",
        "not_diagnosis": "This is not a medical diagnosis. Only a qualified healthcare professional can diagnose your condition.",
        "not_prescription": "This AI cannot prescribe medications. Consult with your doctor or pharmacist for prescription information."
    }

    def __init__(self):
        self.violation_count = {}

    async def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input for safety concerns

        Returns:
            Dict with 'safe' boolean and 'issues' list
        """
        issues = []

        # Check for extremely long input (potential injection attack)
        if len(user_input) > 10000:
            issues.append("Input too long")

        # Check for code injection attempts
        if self._detect_injection_attempt(user_input):
            issues.append("Potential injection attack detected")

        # Check for jailbreak attempts
        if self._detect_jailbreak_attempt(user_input):
            issues.append("Jailbreak attempt detected")

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "sanitized_input": user_input[:10000]  # Truncate if needed
        }

    async def validate_output(
        self,
        llm_output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate LLM output before sending to user

        Returns:
            Dict with 'safe' boolean, 'violations' list, and 'modified_output'
        """
        violations = []

        # Check for prohibited patterns
        for pattern in self.PROHIBITED_PATTERNS:
            if re.search(pattern, llm_output, re.IGNORECASE):
                violations.append(f"Prohibited pattern detected: {pattern}")

        # Check if appropriate disclaimers are present
        has_disclaimer = any(
            disclaimer.lower()[:50] in llm_output.lower()
            for disclaimer in self.REQUIRED_DISCLAIMERS.values()
        )

        # Add disclaimer if missing and response contains medical advice
        modified_output = llm_output
        if self._contains_medical_advice(llm_output) and not has_disclaimer:
            modified_output = self._add_disclaimer(llm_output, context)

        # Check for hallucination indicators
        hallucination_score = self._detect_hallucination(llm_output)
        if hallucination_score > 0.7:
            violations.append("High hallucination risk detected")

        # Check for inappropriate certainty
        if self._has_inappropriate_certainty(llm_output):
            violations.append("Inappropriate medical certainty detected")

        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "modified_output": modified_output,
            "hallucination_score": hallucination_score,
            "requires_human_review": len(violations) > 0
        }

    def _detect_injection_attempt(self, text: str) -> bool:
        """Detect potential prompt injection"""
        injection_patterns = [
            r"ignore\s+(?:previous|all)\s+(?:instructions|prompts)",
            r"you\s+are\s+now",
            r"new\s+instructions",
            r"system\s*:\s*",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _detect_jailbreak_attempt(self, text: str) -> bool:
        """Detect jailbreak attempts"""
        jailbreak_patterns = [
            r"pretend\s+you're",
            r"act\s+as\s+(?:if|though)",
            r"roleplay",
            r"hypothetically",
            r"in\s+a\s+fictional\s+world",
        ]

        for pattern in jailbreak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _contains_medical_advice(self, text: str) -> bool:
        """Check if text contains medical advice"""
        medical_keywords = [
            "treatment", "medication", "diagnosis", "symptoms",
            "condition", "disease", "therapy", "prescription",
            "doctor", "hospital", "medical"
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for keyword in medical_keywords if keyword in text_lower)

        return keyword_count >= 2

    def _add_disclaimer(
        self,
        output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add appropriate disclaimer to output"""
        disclaimers = ["\n\n---\n\n**Medical Disclaimer:**\n"]

        # Add general disclaimer
        disclaimers.append(self.REQUIRED_DISCLAIMERS["general"])

        # Add emergency disclaimer if severity is high
        if context and context.get("severity") in ["EMERGENCY", "URGENT"]:
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["emergency"])

        # Add not-diagnosis disclaimer
        if "diagnos" in output.lower():
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["not_diagnosis"])

        # Add not-prescription disclaimer
        if any(word in output.lower() for word in ["medication", "drug", "prescription"]):
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["not_prescription"])

        return output + "".join(disclaimers)

    def _detect_hallucination(self, text: str) -> float:
        """
        Detect potential hallucination in medical output
        Returns score 0-1 where 1 is highest risk
        """
        hallucination_indicators = 0
        total_checks = 0

        # Check for overly specific medical claims without sources
        total_checks += 1
        if re.search(r"\d+%\s+of\s+(?:patients|people)", text) and "study" not in text.lower():
            hallucination_indicators += 1

        # Check for specific drug dosages without qualification
        total_checks += 1
        if re.search(r"\d+\s*mg", text) and "typically" not in text.lower():
            hallucination_indicators += 1

        # Check for absolute statements
        total_checks += 1
        absolute_words = ["always", "never", "guaranteed", "certainly", "definitely"]
        if any(word in text.lower() for word in absolute_words):
            hallucination_indicators += 1

        # Check for citations that don't exist
        total_checks += 1
        if re.search(r"\[\d+\]", text) or re.search(r"\(.*\s+et\s+al\..*\d{4}.*\)", text):
            hallucination_indicators += 1

        # Check for overly complex medical jargon without explanation
        total_checks += 1
        complex_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", text)
        if len(complex_terms) > 5:
            hallucination_indicators += 0.5

        return min(hallucination_indicators / total_checks, 1.0)

    def _has_inappropriate_certainty(self, text: str) -> bool:
        """Check for inappropriate medical certainty"""
        certainty_patterns = [
            r"you\s+(?:definitely|certainly)\s+(?:have|need|should)",
            r"this\s+is\s+(?:definitely|certainly|absolutely)",
            r"(?:guaranteed|100%)\s+(?:cure|effective)",
            r"(?:will|must)\s+(?:cure|fix|heal)",
        ]

        for pattern in certainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    async def log_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None
    ):
        """Log safety violations for monitoring"""
        # In production, send to monitoring system
        print(f"SAFETY VIOLATION: {violation_type}")
        print(f"Details: {details}")
        print(f"User ID: {user_id}")

        # Track violations per user
        if user_id:
            if user_id not in self.violation_count:
                self.violation_count[user_id] = 0
            self.violation_count[user_id] += 1

    def get_medical_disclaimer(self, context: Optional[str] = None) -> str:
        """Get appropriate medical disclaimer"""
        base_disclaimer = self.REQUIRED_DISCLAIMERS["general"]

        if context and "emergency" in context.lower():
            return f"{base_disclaimer}\n\n{self.REQUIRED_DISCLAIMERS['emergency']}"

        return base_disclaimer
