"""AI Safety Guardrails for legal chatbot"""
from typing import Dict, Any, List, Optional
import re


class SafetyGuardrails:
    """
    Implements safety guardrails for legal AI
    - Validates LLM outputs for legal accuracy
    - Prevents hallucinations
    - Enforces legal disclaimers
    - Blocks inappropriate responses
    """

    # Prohibited actions/claims
    PROHIBITED_PATTERNS = [
        r"i\s+(?:can|will)\s+represent\s+you",
        r"you\s+(?:definitely|certainly)\s+will\s+win",
        r"this\s+is\s+(?:definitely|certainly)\s+legal\s+advice",
        r"i\s+(?:can|will)\s+file\s+(?:your|a)\s+lawsuit",
        r"(?:guaranteed|guarantee)\s+(?:outcome|victory|win)",
        r"no\s+need\s+to\s+(?:hire|consult)\s+(?:a|an)\s+(?:attorney|lawyer)",
        r"don't\s+(?:hire|consult)\s+(?:a|an)\s+(?:attorney|lawyer)",
        r"you\s+don't\s+need\s+(?:a|an)\s+(?:attorney|lawyer)",
    ]

    # Required disclaimers
    REQUIRED_DISCLAIMERS = {
        "general": "This information is for informational and educational purposes only and does not constitute legal advice. The use of this AI assistant does not create an attorney-client relationship. For legal advice specific to your situation, please consult with a licensed attorney in your jurisdiction.",
        "urgent": "If you are facing a time-sensitive legal matter with imminent deadlines, contact a licensed attorney immediately. Missing legal deadlines can result in loss of rights.",
        "not_legal_advice": "This is informational guidance only and not legal advice. Only a licensed attorney can provide legal advice tailored to your specific situation.",
        "no_attorney_client": "Use of this AI assistant does not create an attorney-client relationship. Confidential or privileged communications should only be shared with your attorney."
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

        # Add disclaimer if missing and response contains legal guidance
        modified_output = llm_output
        if self._contains_legal_guidance(llm_output) and not has_disclaimer:
            modified_output = self._add_disclaimer(llm_output, context)

        # Check for hallucination indicators
        hallucination_score = self._detect_hallucination(llm_output)
        if hallucination_score > 0.7:
            violations.append("High hallucination risk detected")

        # Check for inappropriate certainty
        if self._has_inappropriate_certainty(llm_output):
            violations.append("Inappropriate legal certainty detected")

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

    def _contains_legal_guidance(self, text: str) -> bool:
        """Check if text contains legal guidance"""
        legal_keywords = [
            "legal", "law", "attorney", "lawyer", "court", "case",
            "statute", "regulation", "contract", "rights", "liability",
            "jurisdiction", "lawsuit", "litigation"
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for keyword in legal_keywords if keyword in text_lower)

        return keyword_count >= 2

    def _add_disclaimer(
        self,
        output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add appropriate disclaimer to output"""
        disclaimers = ["\n\n---\n\n**Legal Disclaimer:**\n"]

        # Add general disclaimer
        disclaimers.append(self.REQUIRED_DISCLAIMERS["general"])

        # Add urgent disclaimer if urgency is high
        if context and context.get("urgency") in ["CRITICAL_URGENT", "URGENT"]:
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["urgent"])

        # Add not-legal-advice disclaimer
        if any(word in output.lower() for word in ["advice", "recommend", "should"]):
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["not_legal_advice"])

        # Add no-attorney-client disclaimer if representation language detected
        if any(word in output.lower() for word in ["represent", "client", "attorney-client"]):
            disclaimers.append("\n\n" + self.REQUIRED_DISCLAIMERS["no_attorney_client"])

        return output + "".join(disclaimers)

    def _detect_hallucination(self, text: str) -> float:
        """
        Detect potential hallucination in legal output
        Returns score 0-1 where 1 is highest risk
        """
        hallucination_indicators = 0
        total_checks = 0

        # Check for overly specific legal claims without sources
        total_checks += 1
        if re.search(r"\d+%\s+of\s+(?:cases|courts)", text) and "study" not in text.lower():
            hallucination_indicators += 1

        # Check for specific case citations without qualification
        total_checks += 1
        if re.search(r"v\.\s+[A-Z][a-z]+", text) and "typically" not in text.lower():
            hallucination_indicators += 0.5

        # Check for absolute statements
        total_checks += 1
        absolute_words = ["always", "never", "guaranteed", "certainly", "definitely", "will win"]
        if any(word in text.lower() for word in absolute_words):
            hallucination_indicators += 1

        # Check for fake citations
        total_checks += 1
        if re.search(r"\[\d+\]", text) or re.search(r"\d+\s+[A-Z][a-z\.]+\s+\d+", text):
            hallucination_indicators += 1

        # Check for overly complex legal jargon without explanation
        total_checks += 1
        complex_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", text)
        if len(complex_terms) > 5:
            hallucination_indicators += 0.5

        return min(hallucination_indicators / total_checks, 1.0)

    def _has_inappropriate_certainty(self, text: str) -> bool:
        """Check for inappropriate legal certainty"""
        certainty_patterns = [
            r"you\s+(?:definitely|certainly)\s+(?:will|should|must)\s+win",
            r"this\s+is\s+(?:definitely|certainly|absolutely)\s+legal",
            r"(?:guaranteed|100%)\s+(?:win|victory|success)",
            r"(?:will|must)\s+(?:win|succeed|prevail)",
            r"judge\s+will\s+(?:definitely|certainly|always)",
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

    def get_legal_disclaimer(self, context: Optional[str] = None) -> str:
        """Get appropriate legal disclaimer"""
        base_disclaimer = self.REQUIRED_DISCLAIMERS["general"]

        if context and "urgent" in context.lower():
            return f"{base_disclaimer}\n\n{self.REQUIRED_DISCLAIMERS['urgent']}"

        return base_disclaimer
